from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import fw030_podman_adapter as adapter
from scripts.fw030_contract import validate_result


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/framework/schemas/fw030/fixtures/request.valid.synthetic.json"


class PodmanAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve() / "invocation"
        (self.root / "input").mkdir(parents=True)
        (self.root / "output").mkdir()
        (self.root / "input" / "fixture.txt").write_text("synthetic", encoding="utf-8")
        (self.root / "input" / "workload.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.env = {
            "GITHUB_ACTIONS": "true", "RUNNER_OS": "Linux", "ImageOS": "ubuntu24",
            "GITHUB_REPOSITORY": "example/framework", "GITHUB_SHA": "a" * 40,
            "GITHUB_RUN_ID": "12345", "GITHUB_RUN_ATTEMPT": "1",
            "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REF": "refs/heads/test",
            "FW030_PILOT_ROOT": str(self.root), "RUNNER_TEMP": str(self.root.parent.resolve()),
        }
        self.request = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.request["source"] = {"repository": self.env["GITHUB_REPOSITORY"], "revision": self.env["GITHUB_SHA"], "tree_sha256": "b" * 64}
        self.request["execution_context"] = {"kind": "hosted", "provider_context": {
            "provider": "GitHub Actions", "workflow": "FW-030 test", "job": "adapter", "run_id": "12345",
            "attempt": 1, "event": "workflow_dispatch", "ref": "refs/heads/test", "url": "https://github.com/example/framework/actions/runs/12345"}}
        self.request["profile"] = {"id": adapter.PROFILE_ID, "revision": adapter.PROFILE_REVISION}
        self.request["workload"] = {"image": adapter.PINNED_IMAGE, "argv": ["sh", "-eu", "/input/workload.sh"], "executable": "sh", "working_directory": "/input"}
        self.request["policy"]["mounts"] = [
            {"kind": "input", "source": str(self.root / "input"), "target": "/input", "mode": "read_only"},
            {"kind": "output", "source": str(self.root / "output"), "target": "/output", "mode": "write_only"},
        ]
        self.request["policy"]["limits"] = {"cpu_millis": 1000, "memory_mb": 128, "process_count": 32, "disk_mb": 16, "wall_seconds": 30}
        self.request["policy"]["uid"] = 1000
        self.request["policy"]["gid"] = 1000
        self.request["policy"]["evidence"]["case_ids"] = ["INPUT_READONLY", "HOST_PATH_DENIED", "NETWORK_DISABLED", "SECRETS_NOT_INJECTED", "OUTPUT_BOUNDED", "OUTPUT_TMPFS_EFFECTIVE", "CAPABILITIES_DROPPED"]
        self.cap_drop = sorted(adapter.PODMAN_DEFAULT_CAPABILITIES)
        policy = dict(self.request["policy"])
        policy.pop("sha256")
        self.request["policy"]["sha256"] = hashlib.sha256(json.dumps(policy, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.raw = json.dumps(self.request, sort_keys=True, separators=(",", ":")).encode()
        self.digest = hashlib.sha256(self.raw).hexdigest()
        self.auth = {"record_id": "SYNTHETIC-AUTH", "record_sha256": "c" * 64, "authorized_request_sha256": self.digest}

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_rejects_other_host_before_runtime_or_workload(self) -> None:
        calls: list[list[str]] = []
        def runner(argv, timeout):
            calls.append(list(argv))
            return subprocess.CompletedProcess(argv, 0, "", "")
        with patch.object(adapter, "_host_facts", side_effect=adapter.AdapterError("fw030.adapter.profile_unsupported", "unsupported", "unsupported")):
            result = adapter.run_request(self.raw, self.auth, self.env, runner)
        self.assertEqual(result["states"]["request_readiness"], "unsupported")
        self.assertEqual(result["states"]["execution"], "not_started")
        self.assertEqual(calls, [])
        self.assertTrue(validate_result(json.dumps(result))["valid"])

    def test_crun_runtime_version_is_normalized_and_raw_value_retained(self) -> None:
        raw_version = "crun version 1.14.1\ncommit: synthetic"
        info = {"host": {"security": {"rootless": True}, "ociRuntime": {"name": "crun", "version": raw_version}}}
        def runner(argv, timeout):
            if argv == ["podman", "--version"]:
                return subprocess.CompletedProcess(argv, 0, "podman version 4.9.3\n", "")
            if argv == ["podman", "info", "--format", "json"]:
                return subprocess.CompletedProcess(argv, 0, json.dumps(info), "")
            raise AssertionError("unexpected runtime observation command")
        observation = adapter._profile_observation(runner, 10)
        self.assertEqual(observation["oci_runtime_version"], "1.14.1")
        self.assertEqual(observation["oci_runtime_version_raw"], raw_version)

    def test_unsupported_oci_runtime_is_recorded_without_running_workload(self) -> None:
        observed_runtime = {"podman": adapter.PODMAN_VERSION, "oci_runtime": "crun", "oci_runtime_version": "9.9.9"}
        observations: list[dict[str, str]] = []
        with patch.object(adapter, "_host_facts", return_value={"os": "Ubuntu 24.04", "architecture": "x86_64", "image_header": "unknown", "image_env": "ubuntu24"}), patch.object(adapter, "_profile_observation", return_value=observed_runtime):
            result = adapter.run_request(self.raw, self.auth, self.env, observation_sink=observations.append)
        self.assertEqual(result["states"]["request_readiness"], "unsupported")
        self.assertEqual(result["states"]["execution"], "not_started")
        self.assertEqual(observations[0]["oci_runtime_version"], "9.9.9")
        self.assertTrue(observations[0]["image_pull"].startswith("not_attempted;"))
        self.assertIn("fw030.adapter.oci_runtime_mismatch", {d["code"] for d in result["diagnostics"]})
        self.assertTrue(validate_result(json.dumps(result))["valid"])

    def test_pull_exception_reports_attempted_unknown(self) -> None:
        runtime = {"podman": adapter.PODMAN_VERSION, "oci_runtime": "crun", "oci_runtime_version": "1.14.1"}
        observations: list[dict[str, str]] = []
        def runner(argv, timeout):
            if argv[:2] == ["podman", "pull"]:
                raise adapter.AdapterError("fw030.adapter.host_command_timeout", "synthetic timeout", "unsupported")
            raise AssertionError("workload commands must not run after a failed image pull")
        with patch.object(adapter, "_host_facts", return_value={"os": "Ubuntu 24.04", "architecture": "x86_64", "image_header": "unknown", "image_env": "ubuntu24"}), patch.object(adapter, "_profile_observation", return_value=runtime):
            result = adapter.run_request(self.raw, self.auth, self.env, runner, observation_sink=observations.append)
        self.assertEqual(result["states"]["execution"], "not_started")
        self.assertTrue(observations[-1]["image_pull"].startswith("attempted_outcome_unknown;"))
        self.assertIn("fw030.adapter.host_command_timeout", {d["code"] for d in result["diagnostics"]})
        self.assertTrue(validate_result(json.dumps(result))["valid"])

    def test_rejects_unbound_authorization_before_workload(self) -> None:
        runtime = {"podman": adapter.PODMAN_VERSION, "oci_runtime": "crun", "oci_runtime_version": "1.14.1"}
        calls = []
        def runner(argv, timeout):
            calls.append(list(argv))
            if argv[:2] == ["podman", "pull"]:
                return subprocess.CompletedProcess(argv, 0, "", "")
            raise AssertionError("unbound authorization must not start a workload")
        with patch.object(adapter, "_host_facts", return_value={"os": "Ubuntu 24.04", "architecture": "x86_64", "image_header": "unknown", "image_env": "ubuntu24"}), patch.object(adapter, "_profile_observation", return_value=runtime):
            result = adapter.run_request(self.raw, {**self.auth, "authorized_request_sha256": "d" * 64}, self.env, runner)
        self.assertEqual(result["states"]["execution"], "not_started")
        self.assertIsNone(result["authorization_reference"])
        self.assertFalse(any(call[:2] == ["podman", "run"] for call in calls))
        self.assertIn("fw030.adapter.authorization_invalid", {d["code"] for d in result["diagnostics"]})
        self.assertTrue(validate_result(json.dumps(result))["valid"])

    def test_success_requires_all_declared_cases_and_verified_cleanup(self) -> None:
        cases = [{"case_id": case_id, "outcome": "unknown" if case_id == "OUTPUT_TMPFS_EFFECTIVE" else "passed"} for case_id in self.request["policy"]["evidence"]["case_ids"]]
        inspect = [{"Config": {"User": "1000:1000", "Image": adapter.PINNED_IMAGE,
                                "Cmd": ["sh", "-eu", "/input/workload.sh"], "WorkingDir": "/input"}, "HostConfig": {
            "NetworkMode": "none", "ReadonlyRootfs": True, "Memory": 128 * 1024 * 1024,
            "NanoCpus": 1_000_000_000, "PidsLimit": 32, "CapDrop": self.cap_drop,
            "SecurityOpt": ["no-new-privileges"], "Tmpfs": {"/output": "rw,noexec,nosuid,nodev,size=16m,mode=1777,rprivate,nodev"},
            "Binds": [f"{self.root}/input:/input:ro"]}, "Mounts": [{"Type": "bind", "Source": str(self.root / "input"), "Destination": "/input", "RW": False}]}]
        existence_checks = iter([0, 1])
        def runner(argv, timeout):
            if argv[:2] == ["podman", "pull"]:
                return subprocess.CompletedProcess(argv, 0, "", "")
            if argv[:2] == ["podman", "run"]:
                return subprocess.CompletedProcess(argv, 0, "", "")
            if argv[:2] == ["podman", "inspect"]:
                return subprocess.CompletedProcess(argv, 0, json.dumps(inspect), "")
            if argv[:2] == ["podman", "cp"]:
                if argv[2].endswith("/output/cases.json"):
                    Path(argv[-1]).write_text(json.dumps(cases), encoding="utf-8")
                else:
                    Path(argv[-1]).write_text("/output|tmpfs|rw,nosuid,nodev,noexec,relatime|rw,size=16384k,mode=1777,inode64", encoding="ascii")
                return subprocess.CompletedProcess(argv, 0, "", "")
            if argv[:3] == ["podman", "container", "exists"]:
                return subprocess.CompletedProcess(argv, next(existence_checks), "", "")
            if argv[:3] == ["podman", "rm", "--force"]:
                return subprocess.CompletedProcess(argv, 0, "", "")
            raise AssertionError("unexpected runtime command")
        runtime = {"podman": adapter.PODMAN_VERSION, "oci_runtime": "crun", "oci_runtime_version": "1.14.1"}
        with patch.object(adapter, "_host_facts", return_value={"os": "Ubuntu 24.04", "architecture": "x86_64", "image_header": "unknown", "image_env": "ubuntu24"}), patch.object(adapter, "_profile_observation", return_value=runtime):
            result = adapter.run_request(self.raw, self.auth, self.env, runner)
        self.assertEqual(result["states"]["execution"], "succeeded")
        self.assertEqual(result["states"]["cleanup"], "complete")
        self.assertEqual(len(result["case_results"]), len(cases))
        self.assertTrue(validate_result(json.dumps(result))["valid"])

    def test_cleanup_query_error_is_unknown_and_does_not_claim_success(self) -> None:
        runtime = {"podman": adapter.PODMAN_VERSION, "oci_runtime": "crun", "oci_runtime_version": "1.14.1"}
        def runner(argv, timeout):
            if argv[:3] == ["podman", "container", "exists"]:
                return subprocess.CompletedProcess(argv, 125, "", "")
            return subprocess.CompletedProcess(argv, 0, "", "")
        with patch.object(adapter, "_host_facts", return_value={"os": "Ubuntu 24.04", "architecture": "x86_64", "image_header": "unknown", "image_env": "ubuntu24"}), patch.object(adapter, "_profile_observation", return_value=runtime), patch.object(adapter, "_safe_paths", return_value=(self.root, self.root / "input", self.root / "output")):
            result = adapter.run_request(self.raw, self.auth, self.env, runner)
        self.assertEqual(result["states"]["cleanup"], "unknown")
        self.assertIn("fw030.adapter.cleanup_unknown", {d["code"] for d in result["diagnostics"]})
        self.assertTrue(validate_result(json.dumps(result))["valid"])

    def test_mount_observation_summary_redacts_paths_and_bounds_options(self) -> None:
        source = str(self.root / "input")
        item = {"HostConfig": {"Binds": [f"{source}:/input:ro,rprivate"]},
                "Mounts": [{"Type": "bind", "Source": source, "Destination": "/input", "RW": False}]}
        summary = adapter._mount_observation_summary(item, source)
        rendered = json.dumps(summary)
        self.assertNotIn(str(self.root), rendered)
        self.assertEqual(summary["bind_count"], 1)
        self.assertEqual(summary["binds"][0]["options"], ["ro", "rprivate"])
        self.assertEqual(summary["effective_mounts"][0]["read_only"], True)

    def test_mount_observation_reports_bounded_option_keys_without_values(self) -> None:
        source = str(self.root / "input")
        item = {"HostConfig": {"Binds": [f"{source}:/input:ro,rprivate,uid=1000,password=synthetic-secret,/private/path"]},
                "Mounts": [{"Type": "bind", "Source": source, "Destination": "/input", "RW": False}]}
        summary = adapter._mount_observation_summary(item, source)
        rendered = json.dumps(summary)
        row = summary["binds"][0]
        self.assertNotIn(str(self.root), rendered)
        self.assertNotIn("1000", rendered)
        self.assertNotIn("synthetic-secret", rendered)
        self.assertNotIn("/private/path", rendered)
        self.assertEqual(row["option_count"], 5)
        self.assertEqual(row["other_option_count"], 3)
        self.assertEqual(row["other_option_keys"], ["<other>", "password", "uid"])
        self.assertTrue(row["option_details"][2]["has_value"])

    def test_mount_observation_truncates_option_details_and_keys(self) -> None:
        source = str(self.root / "input")
        tokens = [f"option{i:02d}=private-value" for i in range(40)]
        item = {"HostConfig": {"Binds": [f"{source}:/input:{','.join(tokens)}"]},
                "Mounts": [{"Type": "bind", "Source": source, "Destination": "/input", "RW": False}]}
        row = adapter._mount_observation_summary(item, source)["binds"][0]
        self.assertEqual(row["option_count"], 32)
        self.assertTrue(row["option_count_truncated"])
        self.assertEqual(len(row["option_details"]), 8)
        self.assertEqual(len(row["other_option_keys"]), 8)
        self.assertTrue(all(len(key) <= 24 for key in row["other_option_keys"]))
        rendered = json.dumps(row)
        self.assertNotIn("private-value", rendered)
        self.assertNotIn("option39", rendered)

    def test_recursive_bind_preflight_rejects_nested_mounts_and_fails_closed(self) -> None:
        input_dir = Path("/tmp/fw030 synthetic/input")
        encoded_input = str(input_dir).replace(" ", "\\040")
        root_mount = "36 25 0:32 / / rw,relatime - ext4 /dev/root rw"
        input_mount = f"37 25 0:32 / {encoded_input} rw,relatime - ext4 /dev/root rw"
        optional_mount = "39 25 0:32 / / rw,relatime shared:1 master:2 - ext4 /dev/root rw"
        nested_mount = f"38 25 0:33 / {encoded_input}/nested rw,relatime - ext4 /dev/loop0 rw"
        self.assertFalse(adapter._has_nested_mounts(input_dir, (root_mount + "\n" + input_mount + "\n" + optional_mount + "\n").encode()))
        self.assertTrue(adapter._has_nested_mounts(input_dir, (root_mount + "\n" + nested_mount + "\n").encode()))
        with self.assertRaises(adapter.AdapterError) as caught:
            adapter._has_nested_mounts(input_dir, b"malformed")
        self.assertEqual(caught.exception.code, "fw030.adapter.mount_preflight_unknown")
        for malformed in (b"", b"   \n", b"36 25 0:32 / / - rw,relatime ext4 /dev/root rw",
                          (root_mount + " trailing").encode()):
            with self.subTest(malformed=malformed):
                with self.assertRaises(adapter.AdapterError) as caught:
                    adapter._has_nested_mounts(input_dir, malformed)
                self.assertEqual(caught.exception.code, "fw030.adapter.mount_preflight_unknown")

    def test_mount_observation_allows_observed_default_rprivate(self) -> None:
        request = copy.deepcopy(self.request)
        source = str(self.root / "input")
        base = {"Config": {"User": "1000:1000", "Image": adapter.PINNED_IMAGE,
                            "Cmd": request["workload"]["argv"], "WorkingDir": "/input"},
                "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True,
                               "Memory": 128 * 1024 * 1024, "NanoCpus": 1_000_000_000,
                               "PidsLimit": 32, "CapDrop": self.cap_drop,
                               "SecurityOpt": ["no-new-privileges"],
                               "Tmpfs": {"/output": "rw,noexec,nosuid,nodev,size=16m,mode=1777"},
                               "Binds": [f"{source}:/input:ro,rprivate"]},
                "Mounts": [{"Type": "bind", "Source": source, "Destination": "/input", "RW": False}]}
        adapter._verify_container([base], request)
        for bind in (f"{source}:/input:rw,rprivate", f"{source}:/input:ro,rshared",
                     f"{source}:/input:ro,rprivate,unknown", f"{source}:/extra:ro"):
            item = copy.deepcopy(base)
            item["HostConfig"]["Binds"] = [bind]
            with self.subTest(bind_options=bind.rsplit(":", 1)[-1]):
                with self.assertRaises(adapter.AdapterError) as caught:
                    adapter._verify_container([item], request)
                self.assertEqual(caught.exception.code, "fw030.adapter.mount_observation_mismatch")

    def test_effective_mount_source_must_match_declared_input(self) -> None:
        request = copy.deepcopy(self.request)
        inspect = [{"Config": {"User": "1000:1000", "Image": adapter.PINNED_IMAGE,
                                "Cmd": request["workload"]["argv"], "WorkingDir": "/input"},
                    "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True,
                                   "Memory": 128 * 1024 * 1024, "NanoCpus": 1_000_000_000,
                                   "PidsLimit": 32, "CapDrop": self.cap_drop,
                                   "SecurityOpt": ["no-new-privileges"],
                                   "Tmpfs": {"/output": "rw,noexec,nosuid,nodev,size=16m,mode=1777"},
                                   "Binds": ["/unexpected/input:/input:ro"]}}]
        with self.assertRaises(adapter.AdapterError) as caught:
            adapter._verify_container(inspect, request)
        self.assertEqual(caught.exception.code, "fw030.adapter.mount_observation_mismatch")

    def test_tmpfs_config_rejects_conflicting_or_unexpected_options(self) -> None:
        base = "rw,noexec,nosuid,nodev,size=16m,mode=1777,rprivate,tmpcopyup,nodev"
        self.assertTrue(adapter._tmpfs_options_match(base, 16))
        for conflicting in ("exec", "suid", "dev", "ro", "size=32m", "mode=0700", "uid=1000"):
            with self.subTest(conflicting=conflicting):
                self.assertFalse(adapter._tmpfs_options_match(f"{base},{conflicting}", 16))
        self.assertFalse(adapter._tmpfs_options_match(None, 16))

    def test_effective_tmpfs_mount_observation_is_strict(self) -> None:
        valid = b"/output|tmpfs|rw,nosuid,nodev,noexec,relatime|rw,size=16384k,mode=1777,inode64"
        self.assertTrue(adapter._effective_tmpfs_mount_matches(valid, 16))
        for observed in (
            b"/output|ext4|rw,nosuid,nodev,noexec|rw,size=16384k,mode=1777",
            b"/other|tmpfs|rw,nosuid,nodev,noexec|rw,size=16384k,mode=1777",
            b"/output|tmpfs|rw,suid,nodev,noexec|rw,size=16384k,mode=1777",
            b"/output|tmpfs|rw,nosuid,nodev,exec|rw,size=16384k,mode=1777",
            b"/output|tmpfs|rw,nosuid,nodev,noexec|rw,size=32768k,mode=1777",
            b"/output|tmpfs|rw,nosuid,nodev,noexec|rw,size=16384k,mode=0700",
        ):
            with self.subTest(observed=observed):
                self.assertFalse(adapter._effective_tmpfs_mount_matches(observed, 16))

    def test_generated_workload_has_valid_shell_syntax_and_does_not_claim_tmpfs(self) -> None:
        script = adapter._pilot_workload_script(Path("/synthetic/host-sentinel.txt"))
        checked = subprocess.run(["sh", "-n"], input=script, text=True, capture_output=True, check=False)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertIn("/proc/self/mountinfo", script)
        self.assertIn('"OUTPUT_TMPFS_EFFECTIVE","outcome":"unknown"', script)
        self.assertIn("CapEff CapPrm CapInh CapBnd CapAmb", script)
        self.assertIn('"CAPABILITIES_DROPPED","outcome":"' + "'${capabilities_dropped}'" , script)

    def test_cap_drop_matches_observed_podman_expansion_exactly(self) -> None:
        observed = sorted(adapter.PODMAN_DEFAULT_CAPABILITIES)
        self.assertTrue(adapter._cap_drop_matches(observed))
        self.assertFalse(adapter._cap_drop_matches(["ALL"]))
        self.assertFalse(adapter._cap_drop_matches(observed[:-1]))
        self.assertFalse(adapter._cap_drop_matches(observed + ["CAP_SYS_ADMIN"]))
        self.assertFalse(adapter._cap_drop_matches(observed[:-1] + [observed[0]]))
        self.assertFalse(adapter._cap_drop_matches([{}]))

    def test_rejects_unreported_or_additional_effective_mounts(self) -> None:
        request = copy.deepcopy(self.request)
        inspect = [{"Config": {"User": "1000:1000", "Image": adapter.PINNED_IMAGE,
                                "Cmd": request["workload"]["argv"], "WorkingDir": "/input"},
                    "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True,
                                   "Memory": 128 * 1024 * 1024, "NanoCpus": 1_000_000_000,
            "PidsLimit": 32, "CapDrop": self.cap_drop,
                                   "SecurityOpt": ["no-new-privileges"],
                                   "Tmpfs": {"/output": "rw,noexec,nosuid,nodev,size=16m,mode=1777"},
                                   "Binds": [f"{self.root}/input:/input:ro"]},
                    "Mounts": [{"Type": "bind", "Source": str(self.root / "input"),
                                "Destination": "/input", "RW": False},
                               {"Type": "volume", "Source": "unexpected", "Destination": "/output", "RW": True}]}]
        with self.assertRaises(adapter.AdapterError) as caught:
            adapter._verify_container(inspect, request)
        self.assertEqual(caught.exception.code, "fw030.adapter.mount_observation_mismatch")

    def test_malformed_case_output_becomes_failed_result_and_still_cleans_up(self) -> None:
        inspect = [{"Config": {"User": "1000:1000", "Image": adapter.PINNED_IMAGE,
                                "Cmd": self.request["workload"]["argv"], "WorkingDir": "/input"},
                    "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True,
                                   "Memory": 128 * 1024 * 1024, "NanoCpus": 1_000_000_000,
                                   "PidsLimit": 32, "CapDrop": self.cap_drop,
                                   "SecurityOpt": ["no-new-privileges"],
                                   "Tmpfs": {"/output": "rw,noexec,nosuid,nodev,size=16m,mode=1777"},
                                   "Binds": [f"{self.root}/input:/input:ro"]}, "Mounts": [{"Type": "bind", "Source": str(self.root / "input"), "Destination": "/input", "RW": False}]}]
        existence_checks = iter([0, 1])
        def runner(argv, timeout):
            if argv[:2] == ["podman", "pull"] or argv[:2] == ["podman", "run"]:
                return subprocess.CompletedProcess(argv, 0, "", "")
            if argv[:2] == ["podman", "inspect"]:
                return subprocess.CompletedProcess(argv, 0, json.dumps(inspect), "")
            if argv[:2] == ["podman", "cp"]:
                if argv[2].endswith("/output/cases.json"):
                    Path(argv[-1]).write_text('[{"case_id": [], "outcome": "passed"}]', encoding="utf-8")
                else:
                    Path(argv[-1]).write_text("/output|tmpfs|rw,nosuid,nodev,noexec|rw,size=16384k,mode=1777", encoding="ascii")
                return subprocess.CompletedProcess(argv, 0, "", "")
            if argv[:3] == ["podman", "container", "exists"]:
                return subprocess.CompletedProcess(argv, next(existence_checks), "", "")
            if argv[:3] == ["podman", "rm", "--force"]:
                return subprocess.CompletedProcess(argv, 0, "", "")
            raise AssertionError("unexpected runtime command")
        runtime = {"podman": adapter.PODMAN_VERSION, "oci_runtime": "crun", "oci_runtime_version": "1.14.1"}
        with patch.object(adapter, "_host_facts", return_value={"os": "Ubuntu 24.04", "architecture": "x86_64", "image_header": "unknown", "image_env": "ubuntu24"}), patch.object(adapter, "_profile_observation", return_value=runtime):
            result = adapter.run_request(self.raw, self.auth, self.env, runner)
        self.assertEqual(result["states"]["execution"], "failed")
        self.assertEqual(result["states"]["cleanup"], "complete")
        self.assertIn("fw030.adapter.cases_invalid", {d["code"] for d in result["diagnostics"]})
        self.assertTrue(validate_result(json.dumps(result))["valid"])

    def test_podman_subprocess_environment_excludes_host_secrets_and_user_config(self) -> None:
        captured: dict[str, object] = {}
        def fake_run(argv, **kwargs):
            captured.update(kwargs)
            return subprocess.CompletedProcess(argv, 0, "", "")
        env = {**self.env, "FW030_SECRET_SENTINEL": "must-not-propagate", "HOME": "/host/home"}
        with patch.object(adapter.subprocess, "run", side_effect=fake_run):
            adapter._run(["podman", "--version"], 5, env)
        child_env = captured["env"]
        self.assertNotIn("FW030_SECRET_SENTINEL", child_env)
        self.assertNotIn("GITHUB_SHA", child_env)
        self.assertNotIn("GITHUB_RUN_ID", child_env)
        self.assertLessEqual(set(child_env), {"PATH", "HOME", "LANG", "LC_ALL", "XDG_RUNTIME_DIR", "TMPDIR"})
        self.assertEqual(child_env["HOME"], str(self.root / "podman-home"))
        self.assertFalse(captured["shell"])


    def test_runtime_error_hint_redacts_paths_and_credential_values(self) -> None:
        hint = adapter._safe_runtime_error_hint(
            "Error: permission denied at /home/runner/work/private/path token=synthetic-secret-value"
        )
        self.assertIn("<path>", hint)
        self.assertIn("token=<redacted>", hint)
        self.assertNotIn("/home/runner", hint)
        self.assertNotIn("synthetic-secret-value", hint)
        self.assertLessEqual(len(hint), 160)

    def test_cleanup_diagnostic_preserves_first_error_and_redacts_workspace_path(self) -> None:
        first = self.root / "input" / "fixture.txt"
        second = self.root / "input" / "workload.sh"
        failures: dict[str, object] = {}
        adapter._record_cleanup_error(
            failures, self.root, Path.unlink, str(first),
            PermissionError(13, "permission denied", str(first)),
        )
        adapter._record_cleanup_error(
            failures, self.root, Path.unlink, str(second),
            PermissionError(13, "permission denied", str(second)),
        )
        self.assertEqual(failures["entry"], "input/fixture.txt")
        self.assertEqual(failures["operation"], "unlink")
        self.assertEqual(failures["errno"], 13)
        self.assertNotIn(str(self.root), str(failures))
        self.assertIn(failures["owner"], {"runner", "other"})


if __name__ == "__main__":
    unittest.main()

