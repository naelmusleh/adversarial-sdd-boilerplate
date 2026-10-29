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
        self.root = Path(self.temp.name) / "invocation"
        (self.root / "input").mkdir(parents=True)
        (self.root / "output").mkdir()
        (self.root / "input" / "fixture.txt").write_text("synthetic", encoding="utf-8")
        (self.root / "input" / "workload.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.env = {
            "GITHUB_ACTIONS": "true", "RUNNER_OS": "Linux", "ImageOS": "ubuntu24",
            "GITHUB_REPOSITORY": "example/framework", "GITHUB_SHA": "a" * 40,
            "GITHUB_RUN_ID": "12345", "GITHUB_RUN_ATTEMPT": "1",
            "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REF": "refs/heads/test",
            "FW030_PILOT_ROOT": str(self.root), "RUNNER_TEMP": str(self.root.parent),
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

    def test_rejects_unbound_authorization_before_workload(self) -> None:
        runtime = {"podman": adapter.PODMAN_VERSION, "oci_runtime": "crun", "oci_runtime_version": "1.14.1"}
        with patch.object(adapter, "_host_facts", return_value={"os": "Ubuntu 24.04", "architecture": "x86_64", "image_header": "unknown", "image_env": "ubuntu24"}), patch.object(adapter, "_profile_observation", return_value=runtime):
            result = adapter.run_request(self.raw, {**self.auth, "authorized_request_sha256": "d" * 64}, self.env)
        self.assertEqual(result["states"]["execution"], "not_started")
        self.assertIsNone(result["authorization_reference"])
        self.assertIn("fw030.adapter.authorization_invalid", {d["code"] for d in result["diagnostics"]})
        self.assertTrue(validate_result(json.dumps(result))["valid"])

    def test_success_requires_all_declared_cases_and_verified_cleanup(self) -> None:
        cases = [{"case_id": case_id, "outcome": "passed"} for case_id in self.request["policy"]["evidence"]["case_ids"]]
        inspect = [{"Config": {"User": "1000:1000", "Image": adapter.PINNED_IMAGE,
                                "Cmd": ["sh", "-eu", "/input/workload.sh"], "WorkingDir": "/input"}, "HostConfig": {
            "NetworkMode": "none", "ReadonlyRootfs": True, "Memory": 128 * 1024 * 1024,
            "NanoCpus": 1_000_000_000, "PidsLimit": 32, "CapDrop": ["ALL"],
            "SecurityOpt": ["no-new-privileges"], "Tmpfs": {"/output": "rw,noexec,nosuid,size=16m,uid=1000,gid=1000,rprivate,nodev"},
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
                Path(argv[-1]).write_text(json.dumps(cases), encoding="utf-8")
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

    def test_effective_mount_source_must_match_declared_input(self) -> None:
        request = copy.deepcopy(self.request)
        inspect = [{"Config": {"User": "1000:1000", "Image": adapter.PINNED_IMAGE,
                                "Cmd": request["workload"]["argv"], "WorkingDir": "/input"},
                    "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True,
                                   "Memory": 128 * 1024 * 1024, "NanoCpus": 1_000_000_000,
                                   "PidsLimit": 32, "CapDrop": ["ALL"],
                                   "SecurityOpt": ["no-new-privileges"],
                                   "Tmpfs": {"/output": "rw,noexec,nosuid,size=16m,uid=1000,gid=1000"},
                                   "Binds": ["/unexpected/input:/input:ro"]}}]
        with self.assertRaises(adapter.AdapterError) as caught:
            adapter._verify_container(inspect, request)
        self.assertEqual(caught.exception.code, "fw030.adapter.mount_observation_mismatch")

    def test_malformed_case_output_becomes_failed_result_and_still_cleans_up(self) -> None:
        inspect = [{"Config": {"User": "1000:1000", "Image": adapter.PINNED_IMAGE,
                                "Cmd": self.request["workload"]["argv"], "WorkingDir": "/input"},
                    "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True,
                                   "Memory": 128 * 1024 * 1024, "NanoCpus": 1_000_000_000,
                                   "PidsLimit": 32, "CapDrop": ["ALL"],
                                   "SecurityOpt": ["no-new-privileges"],
                                   "Tmpfs": {"/output": "rw,noexec,nosuid,size=16m,uid=1000,gid=1000"},
                                   "Binds": [f"{self.root}/input:/input:ro"]}, "Mounts": [{"Type": "bind", "Source": str(self.root / "input"), "Destination": "/input", "RW": False}]}]
        existence_checks = iter([0, 1])
        def runner(argv, timeout):
            if argv[:2] == ["podman", "pull"] or argv[:2] == ["podman", "run"]:
                return subprocess.CompletedProcess(argv, 0, "", "")
            if argv[:2] == ["podman", "inspect"]:
                return subprocess.CompletedProcess(argv, 0, json.dumps(inspect), "")
            if argv[:2] == ["podman", "cp"]:
                Path(argv[-1]).write_text('[{"case_id": [], "outcome": "passed"}]', encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
