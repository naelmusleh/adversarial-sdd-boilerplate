from __future__ import annotations

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
    "delivery/verification-plan.md",
    "delivery/verification/VERIFY-001.md",
    "delivery/releases/RELEASE-001.md",
    "operations/RUNBOOK.md",
}
BASE_FILES = {"README.md", "AGENTS.md", ".gitignore", "scripts/artifacts.py"}


class InitAppProjectTests(unittest.TestCase):
    def invoke(self, target: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(INITIALIZER),
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
            cwd=ROOT,
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
            self.assertEqual(len(files), 9)
            generated_readme = (target / "README.md").read_text(encoding="utf-8")
            self.assertIn("EXAMPLE-DECISION-001", generated_readme)
            self.assertIn("Give your AI agent the app idea", generated_readme)
            self.assertIn("The agent drafts [`mission.md`](mission.md)", generated_readme)
            generated_agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("token-efficient `quiet` progress", generated_agents)
            self.assertIn("`standard`, `detailed`, or `trace`", generated_agents)
            self.assertIn("Do not automatically advance to another task or gate", generated_agents)
            self.assertIn("authoritative account-wide meter and hard stop", generated_agents)
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
            self.assertEqual(len(files), 20)
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
            self.assertIn("Validated 16 artifact(s).", validation.stdout)

    def test_dry_run_does_not_create_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "app"
            result = self.invoke(target, "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("mission.md", result.stdout)
            self.assertNotIn("reviews/REVIEW-001.md", result.stdout)
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

    def test_downloaded_source_without_git_metadata_initializes_app(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            source = temporary_root / "downloaded-template"
            templates = source / "docs" / "templates" / "app-project"
            scripts = source / "scripts"
            templates.parent.mkdir(parents=True)
            scripts.mkdir(parents=True)
            shutil.copytree(ROOT / "docs" / "templates" / "app-project", templates)
            shutil.copy2(INITIALIZER, scripts / INITIALIZER.name)
            shutil.copy2(ROOT / "scripts" / "artifacts.py", scripts / "artifacts.py")
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
                ],
                cwd=temporary_root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((source / ".git").exists())
            generated_readme = (target / "README.md").read_text(encoding="utf-8")
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
