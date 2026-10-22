from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_SCRIPT = ROOT / "scripts" / "artifacts.py"
CONTRACT_PATH = Path("docs/framework/ARTIFACT-CONTRACT-001.json")
RFC_2119_KEYWORDS = [
    "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
    "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", "OPTIONAL",
]


def artifact_text(artifact_id: str, artifact_type: str) -> str:
    return (
        "---\n"
        f"id: {artifact_id}\n"
        f"type: {artifact_type}\n"
        f"title: {artifact_id} fixture\n"
        "status: draft\n"
        "version: 0.1\n"
        "created: 2026-10-13\n"
        "updated: 2026-10-13\n"
        "---\n\n"
        f"# {artifact_id} fixture\n"
    )


def write_app_fixture(root: Path, *, functional_row: str, quality_row: str) -> None:
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ARTIFACTS_SCRIPT, root / "scripts" / "artifacts.py")
    files = {
        "mission.md": ("TEST-MISSION-001", "mission"),
        "constitution.md": ("TEST-CONSTITUTION-001", "constitution"),
        "design.md": ("TEST-DESIGN-001", "design"),
        "backlog.md": ("TEST-BACKLOG-001", "backlog"),
    }
    for filename, (artifact_id, artifact_type) in files.items():
        (root / filename).write_text(artifact_text(artifact_id, artifact_type), encoding="utf-8")
    specification = (
        artifact_text("TEST-SPEC-001", "specification")
        + "## Functional requirements\n\n"
        + "| ID | Requirement | Acceptance evidence |\n"
        + "| --- | --- | --- |\n"
        + functional_row
        + "\n\n## Quality requirements\n\n"
        + "| ID | Requirement | Acceptance evidence |\n"
        + "| --- | --- | --- |\n"
        + quality_row
        + "\n"
    )
    (root / "specification.md").write_text(specification, encoding="utf-8")


def run_validation(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "artifacts.py"), "validate"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


class ArtifactValidationTests(unittest.TestCase):
    def test_current_framework_repository_passes_its_manifest_and_requirement_tables(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ARTIFACTS_SCRIPT), "validate"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"Validated \d+ artifact\(s\)\.")

    def test_missing_required_framework_artifact_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            shutil.copy2(ARTIFACTS_SCRIPT, root / "scripts" / "artifacts.py")
            (root / "README.md").write_text("Framework fixture\n", encoding="utf-8")
            artifact_path = root / "docs/missions/MISSION-001.md"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text(artifact_text("MISSION-001", "mission"), encoding="utf-8")
            manifest_path = root / CONTRACT_PATH
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "contract_id": "ARTIFACT-CONTRACT-001",
                        "contract_version": 1,
                        "normative_keywords": RFC_2119_KEYWORDS,
                        "framework": {
                            "required_paths": ["README.md", CONTRACT_PATH.as_posix()],
                            "required_artifacts": [
                                {"path": "docs/missions/MISSION-001.md", "id": "MISSION-001"},
                                {"path": "docs/framework/FRAMEWORK-001.md", "id": "FRAMEWORK-001"},
                            ],
                            "requirement_tables": [],
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("docs/framework/FRAMEWORK-001.md: required artifact required file is missing", result.stderr)

    def test_missing_framework_manifest_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            shutil.copy2(ARTIFACTS_SCRIPT, root / "scripts" / "artifacts.py")
            (root / "README.md").write_text("Framework fixture\n", encoding="utf-8")
            (root / "docs/missions").mkdir(parents=True)
            (root / "docs/missions/MISSION-001.md").write_text(
                artifact_text("MISSION-001", "mission"), encoding="utf-8"
            )
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("docs/framework/ARTIFACT-CONTRACT-001.json: required framework artifact contract is missing (required file is missing)", result.stderr)

    def test_valid_uppercase_normative_rows_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service SHOULD respond within one second. | A measured request completes within one second. |",
            )
            result = run_validation(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Validated 5 artifact(s).", result.stdout)

    def test_missing_normative_keyword_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system saves the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("must contain an uppercase RFC 2119 keyword", result.stderr)

    def test_lowercase_normative_keyword_alone_fails_with_line_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system shall save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("must contain an uppercase RFC 2119 keyword", result.stderr)
            self.assertIn("specification.md (## Functional requirements)", result.stderr)

    def test_wrong_requirement_id_kind_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| NFR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-002 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("must identify a FR requirement", result.stderr)

    def test_missing_acceptance_evidence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. |   |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("has an empty Acceptance evidence cell", result.stderr)

    def test_missing_app_canonical_file_still_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            shutil.copy2(ARTIFACTS_SCRIPT, root / "scripts" / "artifacts.py")
            (root / "mission.md").write_text(artifact_text("TEST-MISSION-001", "mission"), encoding="utf-8")
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("constitution.md: required app SDD root file is missing", result.stderr)

    def test_fw026_hosted_merge_block_rehearsal_deliberately_fails_required_check(self) -> None:
        self.fail("FW-026 hosted rehearsal sentinel: deliberate required-check failure; do not merge")


if __name__ == "__main__":
    unittest.main()
