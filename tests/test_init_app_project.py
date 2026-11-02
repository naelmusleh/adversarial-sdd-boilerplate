from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from scripts.init_app_project import _write_outputs_transactionally


ROOT = Path(__file__).resolve().parents[1]
INITIALIZER = ROOT / "scripts" / "init_app_project.py"
CORE_ARTIFACTS = {
    "mission.md",
    "constitution.md",
    "specification.md",
    "design.md",
    "backlog.md",
}
SUPPORTING_ARTIFACTS = {
    "decisions/DECISION-LOG.md",
    "decisions/DECISION-001.md",
    "reviews/REVIEW-001.md",
    "reviews/GATE-REQ-001.md",
    "architecture/feasibility-register.md",
    "architecture/architecture.md",
    "architecture/ADR-001.md",
    "architecture/EXAMPLE-ARCH-HANDSHAKE-001.md",
    "delivery/verification-plan.md",
    "delivery/verification/VERIFY-001.md",
    "delivery/releases/RELEASE-001.md",
    "operations/RUNBOOK.md",
    ".sdd/assumption-experiments.json",
}
BASE_FILES = {
    "README.md",
    "AGENTS.md",
    ".gitignore",
    "scripts/artifacts.py",
    "scripts/ci_checks.py",
    ".sdd/framework.lock.json",
    ".sdd/G-REQ-HANDOFF.json.template",
    ".sdd/G-ARCH-CONTRACT.json.template",
    ".sdd/gate-run-v1.json.template",
    ".sdd/schemas/gate-run-v1.schema.json",
    ".sdd/gate-run-v1.2.json.template",
    ".sdd/schemas/gate-run-v1.2.schema.json",
    ".sdd/schemas/trusted-ci-v1.schema.json",
    ".sdd/schemas/assumption-experiment-v1.schema.json",
    ".sdd/trusted-ci.json.template",
    ".sdd/trusted-ci.json",
    ".sdd/schemas/required-checks-v1.schema.json",
    ".sdd/required-checks.json.template",
    ".sdd/required-checks.json",
    ".sdd/schemas/core-file-manifest-v1.schema.json",
    ".sdd/schemas/profile-manifest-v1.schema.json",
    ".sdd/schemas/profile-selection-manifest-v1.schema.json",
    ".sdd/schemas/profile-check-result-v1.schema.json",
    ".sdd/core-file-manifest-v1.json",
    ".sdd/profile-selection-v1.json",
    ".sdd/profile-check-result-v1.json",
    "docs/templates/app-project/gate-record.md.template",
    ".github/workflows/sdd-contract-validation.yml",
}


class InitAppProjectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source_temp = tempfile.TemporaryDirectory()
        self.template_root = Path(self.source_temp.name) / "template"
        (self.template_root / "scripts").mkdir(parents=True)
        shutil.copy2(INITIALIZER, self.template_root / "scripts" / INITIALIZER.name)
        shutil.copy2(ROOT / "scripts" / "artifacts.py", self.template_root / "scripts" / "artifacts.py")
        shutil.copy2(ROOT / "scripts" / "ci_checks.py", self.template_root / "scripts" / "ci_checks.py")
        shutil.copy2(ROOT / "scripts" / "profile_composer.py", self.template_root / "scripts" / "profile_composer.py")
        shutil.copytree(ROOT / ".sdd", self.template_root / ".sdd")
        (self.template_root / "docs" / "framework").mkdir(parents=True)
        shutil.copytree(ROOT / "docs" / "framework" / "schemas", self.template_root / "docs" / "framework" / "schemas")
        shutil.copytree(ROOT / "framework" / "profiles", self.template_root / "framework" / "profiles")
        (self.template_root / "docs" / "templates").mkdir(parents=True)
        shutil.copytree(
            ROOT / "docs" / "templates" / "app-project",
            self.template_root / "docs" / "templates" / "app-project",
        )
        subprocess.run(["git", "init", "-q"], cwd=self.template_root, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture Author"], cwd=self.template_root, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.com"], cwd=self.template_root, check=True)
        subprocess.run(["git", "add", "scripts", ".sdd", "docs/templates/app-project", "docs/framework/schemas", "framework/profiles"], cwd=self.template_root, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture baseline"], cwd=self.template_root, check=True)

    def tearDown(self) -> None:
        self.source_temp.cleanup()

    def invoke(self, target: Path, *extra: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(self.template_root / "scripts" / INITIALIZER.name),
                "--name",
                "Example App",
                "--prefix",
                "EXAMPLE",
                "--target",
                str(target),
                "--framework-url",
                "https://github.com/naelmusleh/adversarial-sdd-boilerplate",
                *extra,
            ],
            cwd=self.template_root,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

    def test_lock_v4_initializer_rejects_unenrolled_framework_fork(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            result = self.invoke(target, "--framework-url", "https://github.com/example/adversarial-sdd")
            self.assertEqual(result.returncode, 2)
            self.assertIn("separately reviewed trust-root enrollment", result.stderr)
            self.assertFalse(target.exists())

    def test_default_generates_only_core_project_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            result = self.invoke(target)
            self.assertEqual(result.returncode, 0, result.stderr)

            files = {str(path.relative_to(target)) for path in target.rglob("*") if path.is_file()}
            self.assertEqual(files, CORE_ARTIFACTS | BASE_FILES)
            self.assertEqual(len(files), 33)
            generated_readme = (target / "README.md").read_text(encoding="utf-8")
            self.assertIn("EXAMPLE-DECISION-001", generated_readme)
            self.assertIn("Give your AI agent the app idea", generated_readme)
            self.assertIn("The agent drafts [`mission.md`](mission.md)", generated_readme)
            lock = json.loads((target / ".sdd/framework.lock.json").read_text(encoding="utf-8"))
            self.assertEqual(lock["lock_version"], 5)
            self.assertEqual(lock["gate_contract_id"], "FRAMEWORK-GATE-CONTRACT-001")
            self.assertEqual(lock["gate_contract_version"], "1.2")
            self.assertIn(".sdd/schemas/gate-run-v1.schema.json", lock["locked_files"])
            self.assertIn("scripts/ci_checks.py", lock["locked_files"])
            self.assertIn(".sdd/schemas/required-checks-v1.schema.json", lock["locked_files"])
            self.assertIn(".sdd/schemas/gate-run-v1.2.schema.json", lock["locked_files"])
            self.assertIn(".sdd/schemas/trusted-ci-v1.schema.json", lock["locked_files"])
            self.assertIn(".sdd/schemas/profile-selection-manifest-v1.schema.json", lock["locked_files"])
            self.assertIn(".sdd/profile-selection-v1.json", lock["locked_files"])
            selection = json.loads((target / ".sdd/profile-selection-v1.json").read_text(encoding="utf-8"))
            result_record = json.loads((target / ".sdd/profile-check-result-v1.json").read_text(encoding="utf-8"))
            self.assertEqual(selection["selected_profiles"], {})
            self.assertEqual(selection["profile_checks"], {})
            self.assertEqual(result_record["check_results"], {})
            self.assertIn("governance-core-only", result.stdout)
            schema = target / ".sdd/schemas/assumption-experiment-v1.schema.json"
            self.assertTrue(schema.is_file())
            check_manifest = json.loads((target / ".sdd/required-checks.json").read_text(encoding="utf-8"))
            check_schema = json.loads((target / ".sdd/schemas/required-checks-v1.schema.json").read_text(encoding="utf-8"))
            from scripts.artifacts import validate_schema_value
            self.assertEqual(validate_schema_value(check_manifest, check_schema, check_schema), [])
            self.assertRegex(lock["framework_revision"], r"^[a-f0-9]{40}$")
            self.assertIn(f"/blob/{lock['framework_revision']}/", generated_readme)
            gate_template = json.loads((target / ".sdd/gate-run-v1.2.json.template").read_text(encoding="utf-8"))
            schema = json.loads((target / ".sdd/schemas/gate-run-v1.2.schema.json").read_text(encoding="utf-8"))
            self.assertEqual(validate_schema_value(gate_template, schema, schema), [])
            trust_policy = json.loads((target / ".sdd/trusted-ci.json").read_text(encoding="utf-8"))
            trust_schema = json.loads((target / ".sdd/schemas/trusted-ci-v1.schema.json").read_text(encoding="utf-8"))
            self.assertEqual(validate_schema_value(trust_policy, trust_schema, trust_schema), [])
            self.assertEqual(trust_policy["signer_digest"], lock["framework_revision"])
            generated_workflow = (target / ".github/workflows/sdd-contract-validation.yml").read_text(encoding="utf-8")
            self.assertIn(f"sdd-trusted-ci-attest.yml@{lock['framework_revision']}", generated_workflow)
            self.assertIn("framework-repository: naelmusleh/adversarial-sdd-boilerplate", generated_workflow)
            self.assertEqual(
                trust_policy["signer_workflow"],
                "naelmusleh/adversarial-sdd-boilerplate/.github/workflows/sdd-trusted-ci-attest.yml",
            )
            self.assertNotIn("python3 scripts/ci_checks.py", generated_workflow)
            self.assertNotIn("<FRAMEWORK_REVISION>", generated_workflow)
            req_template = json.loads((target / ".sdd/G-REQ-HANDOFF.json.template").read_text(encoding="utf-8"))
            self.assertEqual(req_template["framework_revision"], lock["framework_revision"])
            validation = subprocess.run(
                [sys.executable, str(target / "scripts" / "artifacts.py"), "validate"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)

            self.assertIn("Validated 5 artifact(s).", validation.stdout)

            required_manifest_path = target / ".sdd/required-checks.json"
            required_manifest = json.loads(required_manifest_path.read_text(encoding="utf-8"))
            required_manifest["status"] = "active"
            required_manifest_path.write_text(json.dumps(required_manifest), encoding="utf-8")
            invalid_manifest = subprocess.run(
                [sys.executable, str(target / "scripts" / "artifacts.py"), "validate"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(invalid_manifest.returncode, 1)
            self.assertIn("checks", invalid_manifest.stderr)
            required_manifest_path.write_text(json.dumps({"manifest_version": 1, "status": "unconfigured", "checks": []}), encoding="utf-8")

            # The initialized app enforces its pinned v1.2 gate schema and relational rules.
            gate_template["record_id"] = "EXAMPLE-GATE-RUN-INTENT-001"
            (target / ".sdd/gate-runs").mkdir()
            record_path = target / ".sdd/gate-runs/EXAMPLE-GATE-RUN-INTENT-001.json"
            record_path.write_text(json.dumps(gate_template, indent=2) + "\n", encoding="utf-8")
            valid_run = subprocess.run(
                [sys.executable, str(target / "scripts" / "artifacts.py"), "validate"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(valid_run.returncode, 0, valid_run.stderr)

            gate_template["gate_result"] = "passed"
            for criterion in gate_template["criteria_results"]:
                criterion["outcome"] = "pass"
            record_path.write_text(json.dumps(gate_template, indent=2) + "\n", encoding="utf-8")
            false_pass = subprocess.run(
                [sys.executable, str(target / "scripts" / "artifacts.py"), "validate"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(false_pass.returncode, 0)
            self.assertIn("criteria_results[0].evidence_ids", false_pass.stderr)
            self.assertIn("[G-INTENT]", false_pass.stderr)

    def test_optional_lifecycle_profile_generates_complete_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            result = self.invoke(target, "--include-lifecycle-records")
            self.assertEqual(result.returncode, 0, result.stderr)

            files = {str(path.relative_to(target)) for path in target.rglob("*") if path.is_file()}
            self.assertEqual(files, CORE_ARTIFACTS | SUPPORTING_ARTIFACTS | BASE_FILES)
            self.assertEqual(len(files), 46)
            generated_readme = (target / "README.md").read_text(encoding="utf-8")
            self.assertIn("EXAMPLE-DECISION-002", generated_readme)
            validation = subprocess.run(
                [sys.executable, str(target / "scripts" / "artifacts.py"), "validate"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)
            self.assertIn("Validated 17 artifact(s).", validation.stdout)
            schema = target / ".sdd/schemas/assumption-experiment-v1.schema.json"
            schema.write_text(schema.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            tampered_schema = subprocess.run(
                [sys.executable, str(target / "scripts" / "artifacts.py"), "validate"],
                cwd=target, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(tampered_schema.returncode, 0)
            self.assertIn("schema digest does not match", tampered_schema.stderr)
            handshake = (target / "architecture" / "EXAMPLE-ARCH-HANDSHAKE-001.md").read_text(encoding="utf-8")
            self.assertIn("./.sdd/G-ARCH-CONTRACT.json", handshake)
            self.assertIn("Choose commands for this app's actual stack", handshake)
            self.assertNotIn("LOCAL_FUNCTIONAL_ALPHA", handshake)

    def test_dry_run_does_not_create_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            result = self.invoke(target, "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("mission.md", result.stdout)
            self.assertNotIn("reviews/REVIEW-001.md", result.stdout)
            self.assertFalse(target.exists())

    def test_invalid_archive_revision_fails_before_creating_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            result = self.invoke(target, "--framework-revision", "main")
            self.assertEqual(result.returncode, 2)
            self.assertIn("exact 40-character lowercase commit SHA", result.stderr)
            self.assertFalse(target.exists())

    def test_explicit_revision_must_match_clean_git_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            result = self.invoke(target, "--framework-revision", "0" * 40)
            self.assertEqual(result.returncode, 2)
            self.assertIn("does not match the current Git checkout", result.stderr)
            self.assertFalse(target.exists())

    def test_nonempty_target_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            target.mkdir()
            sentinel = target / "keep.txt"
            sentinel.write_text("preserve", encoding="utf-8")
            result = self.invoke(target)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")
            self.assertEqual(list(target.iterdir()), [sentinel])

    def test_failed_staging_preserves_empty_target_and_cleans_transaction_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            target = parent / "app"
            target.mkdir()
            with self.assertRaises(UnicodeEncodeError):
                _write_outputs_transactionally(target, {"first.txt": "complete", "second.txt": chr(0xD800)})
            self.assertTrue(target.is_dir())
            self.assertEqual(list(target.iterdir()), [])
            self.assertEqual({path.name for path in parent.iterdir()}, {"app"})

    def test_explicit_next_profile_composes_scoped_files_and_reports_checks_not_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            fake_bin = Path(temporary) / "bin"
            fake_bin.mkdir()
            for executable, version in (("node", "v22.23.3"), ("npm", "12.1.0")):
                wrapper = fake_bin / executable
                wrapper.write_text(f"#!/bin/sh\nprintf '%s\\n' '{version}'\n", encoding="utf-8")
                wrapper.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}:{env['PATH']}"
            result = self.invoke(target, "--stack", "nextjs-typescript", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("checks are recorded as not-run", result.stdout)
            self.assertTrue((target / "profiles/nextjs-typescript/package.json").is_file())
            self.assertFalse((target / "profiles/fastapi-python").exists())
            selection = json.loads((target / ".sdd/profile-selection-v1.json").read_text(encoding="utf-8"))
            self.assertEqual(set(selection["selected_profiles"]), {"nextjs-typescript"})
            result_record = json.loads((target / ".sdd/profile-check-result-v1.json").read_text(encoding="utf-8"))
            self.assertEqual(result_record["check_results"]["nextjs-typescript"]["typecheck"]["state"], "not-run")
            self.assertEqual(result_record["check_results"]["nextjs-typescript"]["browser-device"]["state"], "unsupported")
            validation = subprocess.run(
                [sys.executable, str(target / "scripts" / "artifacts.py"), "validate"],
                cwd=target, capture_output=True, text=True, check=False,
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)

            drifted = target / "profiles/nextjs-typescript/src/GalleryItemV1.ts"
            drifted.write_text(drifted.read_text(encoding="utf-8") + "\n// post-initialization drift\n", encoding="utf-8")
            drift_validation = subprocess.run(
                [sys.executable, str(target / "scripts" / "artifacts.py"), "validate"],
                cwd=target, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(drift_validation.returncode, 0)
            self.assertIn("profile generated file", drift_validation.stderr)
            self.assertIn("bytes differ from the frozen inventory digest", drift_validation.stderr)

    def test_initializer_check_record_cannot_be_changed_to_claim_profile_checks_passed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            fake_bin = Path(temporary) / "bin"
            fake_bin.mkdir()
            for executable, version in (("node", "v22.23.3"), ("npm", "12.1.0")):
                wrapper = fake_bin / executable
                wrapper.write_text(f"#!/bin/sh\nprintf '%s\\n' '{version}'\n", encoding="utf-8")
                wrapper.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}:{env['PATH']}"
            result = self.invoke(target, "--stack", "nextjs-typescript", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)

            result_path = target / ".sdd/profile-check-result-v1.json"
            result_record = json.loads(result_path.read_text(encoding="utf-8"))
            result_record["check_results"]["nextjs-typescript"]["typecheck"] = {
                "state": "passed", "command": "npm run typecheck", "exit_code": 0,
            }
            result_path.write_text(json.dumps(result_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            lock_path = target / ".sdd/framework.lock.json"
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            lock["locked_files"][".sdd/profile-check-result-v1.json"] = (
                "sha256:" + hashlib.sha256(result_path.read_bytes()).hexdigest()
            )
            lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            validation = subprocess.run(
                [sys.executable, str(target / "scripts" / "artifacts.py"), "validate"],
                cwd=target, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn("initialization cannot claim command execution", validation.stderr)

    def test_all_profiles_compose_into_a_valid_app_without_running_profile_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            fake_bin = Path(temporary) / "bin"
            fake_bin.mkdir()
            versions = {
                "node": "v22.23.3", "npm": "12.1.0", "python3": "Python 3.13.2",
                "rustc": "rustc 1.97.0", "cargo": "cargo 1.97.0",
            }
            for executable, version in versions.items():
                wrapper = fake_bin / executable
                wrapper.write_text(f"#!/bin/sh\nprintf '%s\\n' '{version}'\n", encoding="utf-8")
                wrapper.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}:{env['PATH']}"
            result = self.invoke(
                target, "--stack", "nextjs-typescript", "--stack", "fastapi-python",
                "--stack", "rust-axum", env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / "profiles/nextjs-typescript/package.json").is_file())
            self.assertTrue((target / "profiles/fastapi-python/requirements.txt").is_file())
            self.assertTrue((target / "profiles/rust-axum/Cargo.toml").is_file())
            selection = json.loads((target / ".sdd/profile-selection-v1.json").read_text(encoding="utf-8"))
            result_record = json.loads((target / ".sdd/profile-check-result-v1.json").read_text(encoding="utf-8"))
            self.assertEqual(set(selection["selected_profiles"]), {"nextjs-typescript", "fastapi-python", "rust-axum"})
            self.assertTrue(all(check["state"] in {"not-run", "unsupported"}
                                for checks in result_record["check_results"].values() for check in checks.values()))
            validation = subprocess.run(
                [sys.executable, str(target / "scripts" / "artifacts.py"), "validate"],
                cwd=target, capture_output=True, text=True, check=False,
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)

    def test_unknown_and_duplicate_profiles_fail_before_writing(self) -> None:
        for selections in (("nextjs-typescript", "nextjs-typescript"), ("unknown-profile",)):
            with self.subTest(selections=selections), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary) / "app"
                extra = tuple(argument for profile in selections for argument in ("--stack", profile))
                result = self.invoke(target, *extra)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(target.exists())

    def test_dirty_framework_input_is_rejected_before_creating_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            input_file = self.template_root / ".sdd/G-REQ-HANDOFF.json.template"
            input_file.write_text(input_file.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            result = self.invoke(target)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Framework source inputs have uncommitted changes", result.stderr)
            self.assertFalse(target.exists())

    def test_unrelated_untracked_file_does_not_block_framework_initialization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            (self.template_root / "scratch.txt").write_text("unrelated", encoding="utf-8")
            result = self.invoke(target)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_downloaded_source_without_git_metadata_initializes_app(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            source = temporary_root / "downloaded-template"
            templates = source / "docs" / "templates" / "app-project"
            scripts = source / "scripts"
            templates.parent.mkdir(parents=True)
            scripts.mkdir(parents=True)
            shutil.copytree(self.template_root / "docs" / "templates" / "app-project", templates)
            shutil.copy2(self.template_root / "scripts" / INITIALIZER.name, scripts / INITIALIZER.name)
            shutil.copy2(self.template_root / "scripts" / "artifacts.py", scripts / "artifacts.py")
            shutil.copy2(self.template_root / "scripts" / "ci_checks.py", scripts / "ci_checks.py")
            shutil.copy2(self.template_root / "scripts" / "profile_composer.py", scripts / "profile_composer.py")
            shutil.copytree(self.template_root / ".sdd", source / ".sdd")
            (source / "docs" / "framework").mkdir(parents=True)
            shutil.copytree(
                self.template_root / "docs" / "framework" / "schemas",
                source / "docs" / "framework" / "schemas",
            )
            shutil.copytree(self.template_root / "framework" / "profiles", source / "framework" / "profiles")
            revision = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=self.template_root, capture_output=True, text=True, check=True
            ).stdout.strip()
            target = temporary_root / "example-app"

            result = subprocess.run(
                [
                    sys.executable,
                    str(scripts / INITIALIZER.name),
                    "--name",
                    "Example App",
                    "--prefix",
                    "EXAMPLE",
                    "--target",
                    str(target),
                    "--framework-revision",
                    revision,
                ],
                cwd=temporary_root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((source / ".git").exists())
            generated_readme = (target / "README.md").read_text(encoding="utf-8")
            self.assertIn(f"/tree/{revision}", generated_readme)
            self.assertIn("https://github.com/naelmusleh/adversarial-sdd-boilerplate", generated_readme)
            validation = subprocess.run(
                [sys.executable, str(target / "scripts" / "artifacts.py"), "validate"],
                cwd=temporary_root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)
            self.assertIn("Validated 5 artifact(s).", validation.stdout)


if __name__ == "__main__":
    unittest.main()
