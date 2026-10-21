from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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
}
BASE_FILES = {
    "README.md",
    "AGENTS.md",
    ".gitignore",
    "scripts/artifacts.py",
    ".sdd/framework.lock.json",
    ".sdd/G-REQ-HANDOFF.json.template",
    ".sdd/G-ARCH-CONTRACT.json.template",
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
        shutil.copytree(ROOT / ".sdd", self.template_root / ".sdd")
        (self.template_root / "docs" / "templates").mkdir(parents=True)
        shutil.copytree(
            ROOT / "docs" / "templates" / "app-project",
            self.template_root / "docs" / "templates" / "app-project",
        )
        subprocess.run(["git", "init", "-q"], cwd=self.template_root, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture Author"], cwd=self.template_root, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.com"], cwd=self.template_root, check=True)
        subprocess.run(["git", "add", "scripts", ".sdd", "docs/templates/app-project"], cwd=self.template_root, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture baseline"], cwd=self.template_root, check=True)

    def tearDown(self) -> None:
        self.source_temp.cleanup()

    def invoke(self, target: Path, *extra: str) -> subprocess.CompletedProcess[str]:
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
                "https://github.com/example/adversarial-sdd",
                *extra,
            ],
            cwd=self.template_root,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_default_generates_only_core_project_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            result = self.invoke(target)
            self.assertEqual(result.returncode, 0, result.stderr)

            files = {str(path.relative_to(target)) for path in target.rglob("*") if path.is_file()}
            self.assertEqual(files, CORE_ARTIFACTS | BASE_FILES)
            self.assertEqual(len(files), 14)
            generated_readme = (target / "README.md").read_text(encoding="utf-8")
            self.assertIn("EXAMPLE-DECISION-001", generated_readme)
            self.assertIn("Give your AI agent the app idea", generated_readme)
            self.assertIn("The agent drafts [`mission.md`](mission.md)", generated_readme)
            lock = json.loads((target / ".sdd/framework.lock.json").read_text(encoding="utf-8"))
            self.assertRegex(lock["framework_revision"], r"^[a-f0-9]{40}$")
            self.assertIn(f"/blob/{lock['framework_revision']}/", generated_readme)
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

    def test_optional_lifecycle_profile_generates_complete_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            result = self.invoke(target, "--include-lifecycle-records")
            self.assertEqual(result.returncode, 0, result.stderr)

            files = {str(path.relative_to(target)) for path in target.rglob("*") if path.is_file()}
            self.assertEqual(files, CORE_ARTIFACTS | SUPPORTING_ARTIFACTS | BASE_FILES)
            self.assertEqual(len(files), 26)
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
            shutil.copytree(self.template_root / ".sdd", source / ".sdd")
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
