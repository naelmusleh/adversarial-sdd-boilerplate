from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.artifacts import (
    CANONICAL_FRAMEWORK_URL,
    _lock_v4_gimpl_evidence_type_problem,
    _trusted_gimpl_attestation_problems,
    trusted_ci_policy,
)


ROOT = Path(__file__).resolve().parents[1]


class TrustedCiAttestationTests(unittest.TestCase):
    def test_lock_v4_policy_cannot_retarget_the_framework_signer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".sdd/schemas").mkdir(parents=True)
            policy = {
                "policy_version": 1,
                "status": "unconfigured",
                "provider": "github-actions",
                "repository": None,
                "protected_ref": None,
                "signer_workflow": "attacker/runner/.github/workflows/sdd-trusted-ci-attest.yml",
                "signer_digest": "a" * 40,
            }
            (root / ".sdd/trusted-ci.json").write_text(json.dumps(policy), encoding="utf-8")
            (root / ".sdd/schemas/trusted-ci-v1.schema.json").write_text(
                (ROOT / "docs/framework/schemas/trusted-ci-v1.schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (root / ".sdd/framework.lock.json").write_text(json.dumps({
                "lock_version": 4,
                "framework_repository": "https://github.com/attacker/runner",
                "framework_revision": "a" * 40,
            }), encoding="utf-8")
            _, problems = trusted_ci_policy(root)
            self.assertTrue(any(CANONICAL_FRAMEWORK_URL in problem for problem in problems), problems)
            self.assertTrue(any("canonical framework-owned reusable attester" in problem for problem in problems), problems)

    def test_local_and_typed_command_evidence_cannot_support_lock_v4_pass(self) -> None:
        for evidence_type in ("command-execution", "manual-observation"):
            with self.subTest(evidence_type=evidence_type):
                problem = _lock_v4_gimpl_evidence_type_problem({"type": evidence_type}, "fixture")
                self.assertIn("provider-attested ci-run is required", problem or "")
        self.assertIsNone(_lock_v4_gimpl_evidence_type_problem({"type": "ci-run"}, "fixture"))

    def test_valid_signed_report_is_bound_to_framework_signer_source_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".sdd").mkdir()
            manifest = {
                "manifest_version": 1,
                "status": "active",
                "checks": [{
                    "check_id": "TASK-TEST",
                    "task_ids": ["APP-TASK-001"],
                    "acceptance_criteria": ["AC-001"],
                    "platforms": ["python"],
                    "scope_paths": ["src", "tests"],
                    "required": True,
                    "execution": "ci",
                    "command_or_procedure": "python -m unittest",
                    "pass_condition": "exit code 0",
                }],
            }
            policy = {
                "policy_version": 1,
                "status": "active",
                "provider": "github-actions",
                "repository": "example/app",
                "protected_ref": "refs/heads/main",
                "signer_workflow": "naelmusleh/adversarial-sdd-boilerplate/.github/workflows/sdd-trusted-ci-attest.yml",
                "signer_digest": "a" * 40,
            }
            (root / ".sdd/required-checks.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / ".sdd/trusted-ci.json").write_text(json.dumps(policy), encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", ".sdd"], cwd=root, check=True)
            subprocess.run([
                "git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "commit", "-qm", "source",
            ], cwd=root, check=True)
            source_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, check=True, text=True, capture_output=True,
            ).stdout.strip()
            manifest_sha = "sha256:" + hashlib.sha256((root / ".sdd/required-checks.json").read_bytes()).hexdigest()
            observed_check = {
                **manifest["checks"][0],
                "result": "passed",
                "exit_code": 0,
                "scope": "src, tests",
            }
            report = {
                "manifest_status": "active",
                "manifest_sha256": manifest_sha,
                "overall_result": "passed",
                "errors": [],
                "provider_run": {
                    "provider": "github-actions",
                    "repository": "example/app",
                    "event_name": "push",
                    "ref": "refs/heads/main",
                    "ref_protected": True,
                    "workflow_ref": "example/app/.github/workflows/sdd-contract-validation.yml@refs/heads/main",
                    "workflow_sha": source_sha,
                    "tested_commit_sha": source_sha,
                    "run_url": "https://github.com/example/app/actions/runs/123/attempts/1",
                },
                "checks": [observed_check],
            }
            report_path = root / "docs/evidence/report.json"
            report_path.parent.mkdir(parents=True)
            report_path.write_text(json.dumps(report), encoding="utf-8")
            report_sha = "sha256:" + hashlib.sha256(report_path.read_bytes()).hexdigest()
            evidence = {
                "type": "ci-run",
                "record_sha256": report_sha,
                "details": {
                    "run_id_or_url": report["provider_run"]["run_url"],
                    "attestation": {
                        "report_path": "docs/evidence/report.json",
                        "report_sha256": report_sha,
                        "manifest_sha256": manifest_sha,
                    },
                },
            }
            record = {
                "repository": {"url_or_path": "https://github.com/example/app"},
                "gate_data": {"selected_task_id": "APP-TASK-001"},
            }
            verifier_output = json.dumps([{
                "verificationResult": {
                    "statement": {
                        "subject": [{"digest": {"sha256": report_sha.removeprefix("sha256:")}}]
                    }
                }
            }])
            real_run = subprocess.run
            seen_command: list[str] = []

            def fake_run(command, **kwargs):
                if command[0] == "/usr/bin/gh":
                    seen_command.extend(command)
                    return subprocess.CompletedProcess(command, 0, verifier_output, "")
                return real_run(command, **kwargs)

            with patch("scripts.artifacts.shutil.which", return_value="/usr/bin/gh"), patch(
                "scripts.artifacts.subprocess.run", side_effect=fake_run,
            ):
                problems = _trusted_gimpl_attestation_problems(
                    root, record, evidence, source_sha, policy, manifest["checks"], "fixture",
                )

            self.assertEqual(problems, [])
            self.assertIn("--signer-workflow", seen_command)
            self.assertIn(policy["signer_workflow"], seen_command)
            self.assertIn("--signer-digest", seen_command)
            self.assertIn(policy["signer_digest"], seen_command)
            self.assertIn("--source-digest", seen_command)
            self.assertIn(source_sha, seen_command)

            def authentication_failure(command, **kwargs):
                if command[0] == "/usr/bin/gh":
                    return subprocess.CompletedProcess(command, 1, "", "HTTP 401: Bad credentials")
                return real_run(command, **kwargs)

            with patch("scripts.artifacts.shutil.which", return_value="/usr/bin/gh"), patch(
                "scripts.artifacts.subprocess.run", side_effect=authentication_failure,
            ):
                auth_problems = _trusted_gimpl_attestation_problems(
                    root, record, evidence, source_sha, policy, manifest["checks"], "fixture",
                )

            self.assertTrue(
                any("GitHub attestation verification failed: HTTP 401: Bad credentials" in problem
                    for problem in auth_problems),
                auth_problems,
            )

    def test_missing_provider_verifier_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report_path = root / "report.json"
            report_path.write_text("{}", encoding="utf-8")
            report_sha = "sha256:" + hashlib.sha256(report_path.read_bytes()).hexdigest()
            problems = _trusted_gimpl_attestation_problems(
                root,
                {"repository": {}, "gate_data": {}},
                {"type": "ci-run", "record_sha256": report_sha, "details": {}},
                "1" * 40,
                {"repository": "example/app", "protected_ref": "refs/heads/main"},
                [{"check_id": "TASK-TEST", "execution": "ci"}],
                "fixture",
            )
            self.assertIn("lock-v4 G-IMPL PASS requires verified provider attestation metadata", problems[0])


if __name__ == "__main__":
    unittest.main()
