from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CI_CHECKS = ROOT / "scripts/ci_checks.py"


class RequiredCheckRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "scripts").mkdir()
        shutil.copy2(CI_CHECKS, self.root / "scripts/ci_checks.py")
        shutil.copy2(ROOT / "scripts/artifacts.py", self.root / "scripts/artifacts.py")
        (self.root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
        (self.root / ".sdd/schemas").mkdir(parents=True)
        shutil.copy2(ROOT / "docs/framework/schemas/required-checks-v1.schema.json", self.root / ".sdd/schemas/required-checks-v1.schema.json")
        self._git("init", "-q")
        self._git("config", "user.name", "Fixture")
        self._git("config", "user.email", "fixture@example.com")
        (self.root / "README.md").write_text("fixture\n", encoding="utf-8")
        self._git("add", "README.md")
        self._git("add", ".gitignore", "scripts/ci_checks.py", "scripts/artifacts.py")
        self._git("add", ".sdd/schemas/required-checks-v1.schema.json")
        self._git("commit", "-qm", "fixture")
        self.evidence_temp = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.evidence_temp.cleanup()
        self.temporary.cleanup()

    def _git(self, *args: str) -> str:
        result = subprocess.run(["git", *args], cwd=self.root, text=True, capture_output=True, check=True)
        return result.stdout.strip()

    def _manifest(self, command: str) -> None:
        (self.root / ".sdd/required-checks.json").write_text(
            json.dumps({
                "manifest_version": 1,
                "status": "active",
                "checks": [{
                    "check_id": "PYTEST-01",
                    "execution": "ci",
                    "required": True,
                    "task_ids": ["TASK-001"],
                    "acceptance_criteria": ["AC-001"],
                    "platforms": ["linux"],
                    "command_or_procedure": command,
                    "runtime_probe": "python3 --version",
                    "scope_paths": ["src", "tests"],
                    "pass_condition": "exit_code == 0",
                    "evidence_location": ".sdd/ci-evidence/"
                }]
            }, indent=2) + "\n",
            encoding="utf-8",
        )
        self._git("add", ".sdd/required-checks.json")
        self._git("commit", "-qm", "declare checks")

    def _run(self, *, expected_sha: str | None = None, failure: bool = False) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        evidence_dir = Path(self.evidence_temp.name)
        env = os.environ.copy()
        for key in list(env):
            if key.startswith(("GITHUB_", "RUNNER_")) or key in {"ImageOS", "ImageVersion"}:
                env.pop(key, None)
        env["SDD_CI_EVIDENCE_DIR"] = str(evidence_dir)
        if expected_sha is not None:
            env["GITHUB_ACTIONS"] = "true"
            env["GITHUB_REPOSITORY"] = "example/app"
            env["GITHUB_RUN_ID"] = "101"
            env["GITHUB_RUN_ATTEMPT"] = "2"
            env["GITHUB_WORKFLOW"] = "Verify"
            env["GITHUB_JOB"] = "checks"
            env["GITHUB_EVENT_NAME"] = "pull_request"
            env["GITHUB_REF"] = "refs/pull/7/merge"
            env["GITHUB_SHA"] = expected_sha
            event_path = Path(self.evidence_temp.name) / "event.json"
            event_path.write_text(json.dumps({"pull_request": {"head": {"sha": "b" * 40}, "base": {"sha": "c" * 40}}}), encoding="utf-8")
            env["GITHUB_EVENT_PATH"] = str(event_path)
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/ci_checks.py")],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        report = json.loads((evidence_dir / "required-check-results.json").read_text(encoding="utf-8"))
        return result, report

    def test_success_record_binds_runner_attempt_sha_event_and_output_digests(self) -> None:
        self._manifest("python3 -c 'print(\"ok\")'")
        sha = self._git("rev-parse", "HEAD")
        result, report = self._run(expected_sha=sha)
        self.assertEqual(result.returncode, 0, result.stderr)
        provider = report["provider_run"]
        self.assertEqual(provider["provider"], "github-actions")
        self.assertEqual(provider["tested_commit_sha"], sha)
        self.assertEqual(provider["run_attempt"], 2)
        self.assertEqual(provider["event_head_sha"], "b" * 40)
        self.assertEqual(provider["runner_os"], "local")
        self.assertIn("/attempts/2", provider["run_url"])
        check = report["checks"][0]
        output = self.root / check["stdout_path"]
        self.assertEqual(check["result"], "passed")
        self.assertEqual(check["stdout_sha256"], "sha256:" + hashlib.sha256(output.read_bytes()).hexdigest())

    def test_nonzero_check_fails_and_preserves_observed_exit_code(self) -> None:
        self._manifest("python3 -c 'raise SystemExit(4)'")
        result, report = self._run()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["overall_result"], "failed")
        self.assertEqual(report["checks"][0]["exit_code"], 4)

    def test_provider_sha_mismatch_fails_closed_but_writes_evidence(self) -> None:
        self._manifest("python3 -c 'print(\"ok\")'")
        result, report = self._run(expected_sha="0" * 40)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("does not match provider event SHA" in error for error in report["errors"]))
        self.assertEqual(report["checks"][0]["result"], "passed")

    def test_invalid_manifest_is_rejected_before_any_declared_command_runs(self) -> None:
        marker = self.root / "command-ran"
        self._manifest(f"python3 -c 'from pathlib import Path; Path(\"{marker}\").touch()'")
        manifest = json.loads((self.root / ".sdd/required-checks.json").read_text(encoding="utf-8"))
        manifest["checks"][0]["scope_paths"] = ["../outside"]
        (self.root / ".sdd/required-checks.json").write_text(json.dumps(manifest), encoding="utf-8")
        self._git("add", ".sdd/required-checks.json")
        self._git("commit", "-qm", "invalid manifest fixture")
        result, report = self._run()
        self.assertEqual(result.returncode, 1)
        self.assertFalse(marker.exists())
        self.assertEqual(report["checks"], [])
        self.assertTrue(any("must be repository-relative" in error for error in report["errors"]))

    def test_check_that_mutates_tracked_source_fails_and_stops_remaining_checks(self) -> None:
        marker = self.root / "second-check-ran"
        self._manifest("printf 'changed\\n' >> README.md")
        manifest_path = self.root / ".sdd/required-checks.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["checks"].append({**manifest["checks"][0], "check_id": "PYTEST-02",
            "command_or_procedure": f"python3 -c 'from pathlib import Path; Path({str(marker)!r}).touch()'"})
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self._git("add", ".sdd/required-checks.json")
        self._git("commit", "-qm", "add second check")
        result, report = self._run()
        self.assertEqual(result.returncode, 1)
        self.assertFalse(marker.exists())
        self.assertEqual(len(report["checks"]), 1)
        self.assertTrue(any("preserve a clean checkout" in error for error in report["errors"]))

    def test_timeout_terminates_background_process_group(self) -> None:
        spec = importlib.util.spec_from_file_location("ci_checks_fixture", CI_CHECKS)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.path.insert(0, str(ROOT / "scripts"))
        spec.loader.exec_module(module)
        module.MAX_COMMAND_SECONDS = 1
        marker = self.root.parent / f"{self.root.name}-child-survived"
        command = f"(sleep 2; touch {shlex.quote(str(marker))}) & wait"
        code, _stdout, _stderr, error = module.run_command(command, self.root, os.environ.copy())
        self.assertIsNotNone(code)
        self.assertIn("process group was terminated", error or "")
        import time
        time.sleep(1.2)
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
