from __future__ import annotations

import hashlib
import json
import re
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


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def install_governance_bundle(root: Path) -> str:
    revision = "a" * 40
    (root / ".sdd").mkdir(parents=True, exist_ok=True)
    (root / ".github/workflows").mkdir(parents=True, exist_ok=True)
    (root / ".sdd/G-REQ-HANDOFF.json.template").write_text(
        (ROOT / ".sdd/G-REQ-HANDOFF.json.template").read_text(encoding="utf-8")
        .replace("<APP>", "TEST")
        .replace("<40-character framework commit SHA>", revision),
        encoding="utf-8",
    )
    (root / ".sdd/G-ARCH-CONTRACT.json.template").write_text(
        (ROOT / ".sdd/G-ARCH-CONTRACT.json.template").read_text(encoding="utf-8")
        .replace("<APP>", "TEST")
        .replace("<40-character framework commit SHA>", revision),
        encoding="utf-8",
    )
    gate_template = (ROOT / "docs/templates/app-project/gate-record.md.template").read_text(encoding="utf-8")
    gate_template = gate_template.replace("<APP>", "TEST").replace("YYYY-MM-DD", "2026-10-20")
    gate_template = gate_template.replace("<GATE-ID>", "REQ").replace("<Gate name>", "Requirements readiness")
    gate_template = gate_template.replace("<project/revision>", "Fixture")
    gate_template = re.sub(r"(?m)^status:.*$", "status: draft", gate_template)
    (root / "docs/templates/app-project").mkdir(parents=True, exist_ok=True)
    (root / "docs/templates/app-project/gate-record.md.template").write_text(gate_template, encoding="utf-8")
    shutil.copy2(
        ROOT / "docs/templates/app-project/sdd-contract-validation.yml.template",
        root / ".github/workflows/sdd-contract-validation.yml",
    )
    locked_files = {
        relative: sha256(root / relative)
        for relative in (
            "scripts/artifacts.py",
            ".sdd/G-REQ-HANDOFF.json.template",
            ".sdd/G-ARCH-CONTRACT.json.template",
            "docs/templates/app-project/gate-record.md.template",
            ".github/workflows/sdd-contract-validation.yml",
        )
    }
    (root / ".sdd/framework.lock.json").write_text(
        json.dumps(
            {
                "lock_version": 1,
                "framework_repository": "https://github.com/example/framework",
                "framework_revision": revision,
                "artifact_contract_id": "ARTIFACT-CONTRACT-001",
                "artifact_contract_version": 1,
                "locked_files": locked_files,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return revision


def frozen_artifact(root: Path, relative: str, artifact_id: str) -> dict[str, str]:
    return {
        "path": relative,
        "id": artifact_id,
        "version": "0.1",
        "sha256": sha256(root / relative),
    }


def write_review(root: Path, gate_id: str) -> dict[str, str]:
    review_id = f"TEST-REVIEW-{gate_id.removeprefix('G-')}-001"
    relative = f"reviews/{review_id}.md"
    review_path = root / relative
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(artifact_text(review_id, "review-record"), encoding="utf-8")
    return {
        "path": relative,
        "id": review_id,
        "version": "0.1",
        "sha256": sha256(review_path),
        "reviewer_mode": "independent",
        "result": "PASS",
    }


def write_gate_record(
    root: Path,
    gate_id: str,
    manifest_path: str,
    *,
    result: str | None = "passed",
    artifact_type: str = "lifecycle-gate-record",
) -> None:
    gate_slug = gate_id.removeprefix("G-")
    gate_id_artifact = f"TEST-GATE-{gate_slug}-001"
    content = artifact_text(gate_id_artifact, artifact_type)
    metadata = f"updated: 2026-10-13\ngate-id: {gate_id}\n"
    if result is not None:
        metadata += f"gate-result: {result}\n"
    metadata += f"handoff-manifest: {manifest_path}\n---"
    content = content.replace("updated: 2026-10-13\n---", metadata)
    path = root / f"reviews/{gate_id_artifact}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_req_manifest(root: Path, revision: str) -> None:
    review = write_review(root, "G-REQ")
    manifest = {
        "contract_id": "G-REQ-HANDOFF-001",
        "contract_version": 1,
        "framework_revision": revision,
        "source_gate": "G-REQ",
        "scope": "Approved test scope for web",
        "frozen_artifacts": [
            frozen_artifact(root, "mission.md", "TEST-MISSION-001"),
            frozen_artifact(root, "constitution.md", "TEST-CONSTITUTION-001"),
            frozen_artifact(root, "specification.md", "TEST-SPEC-001"),
            frozen_artifact(root, "backlog.md", "TEST-BACKLOG-001"),
        ],
        "independent_review": review,
    }
    path = root / ".sdd/G-REQ-HANDOFF.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_gate_record(root, "G-REQ", ".sdd/G-REQ-HANDOFF.json")


def write_arch_manifest(root: Path, revision: str) -> None:
    review = write_review(root, "G-ARCH")
    contract_path = root / "packages/contracts/openapi.json"
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text('{"openapi":"3.1.0","paths":{}}\n', encoding="utf-8")
    manifest = {
        "contract_id": "G-ARCH-CONTRACT-001",
        "contract_version": 1,
        "framework_revision": revision,
        "source_gate": "G-ARCH",
        "scope": "Approved test architecture scope for web",
        "frozen_artifacts": [
            frozen_artifact(root, "specification.md", "TEST-SPEC-001"),
            frozen_artifact(root, "design.md", "TEST-DESIGN-001"),
            frozen_artifact(root, "backlog.md", "TEST-BACKLOG-001"),
        ],
        "contract_file": {
            "path": "packages/contracts/openapi.json",
            "sha256": sha256(contract_path),
        },
        "required_checks": [
            {
                "id": "CHECK-API-001",
                "command": "python3 -m unittest discover -s tests",
                "assertions": ["The approved API error shape is returned for invalid input."],
            }
        ],
        "review_inputs": [],
        "independent_review": review,
    }
    path = root / ".sdd/G-ARCH-CONTRACT.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_gate_record(root, "G-ARCH", ".sdd/G-ARCH-CONTRACT.json")


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

    def test_legacy_app_without_version_lock_remains_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            result = run_validation(root)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_legacy_passed_gate_record_without_handoff_remains_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            write_gate_record(root, "G-REQ", ".sdd/G-REQ-HANDOFF.json")
            gate_path = root / "reviews/TEST-GATE-REQ-001.md"
            gate_path.write_text(
                gate_path.read_text(encoding="utf-8").replace(
                    "handoff-manifest: .sdd/G-REQ-HANDOFF.json\n", ""
                ),
                encoding="utf-8",
            )
            result = run_validation(root)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_legacy_passed_record_declaring_missing_handoff_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            write_gate_record(root, "G-REQ", ".sdd/G-REQ-HANDOFF.json")
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("requires a versioned .sdd/framework.lock.json", result.stderr)
            self.assertIn("has no populated .sdd/G-REQ-HANDOFF.json", result.stderr)

    def test_frozen_greq_handoff_and_gate_record_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            revision = install_governance_bundle(root)
            write_req_manifest(root, revision)
            result = run_validation(root)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_passed_greq_without_manifest_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            install_governance_bundle(root)
            write_gate_record(root, "G-REQ", ".sdd/G-REQ-HANDOFF.json")
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("passed G-REQ record has no populated .sdd/G-REQ-HANDOFF.json", result.stderr)

    def test_passed_greq_cannot_evade_handoff_validation_by_retyping_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            install_governance_bundle(root)
            write_gate_record(
                root,
                "G-REQ",
                ".sdd/G-REQ-HANDOFF.json",
                artifact_type="decision-record",
            )
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("gate metadata requires type", result.stderr)
            self.assertIn("passed G-REQ record has no populated .sdd/G-REQ-HANDOFF.json", result.stderr)

    def test_passed_gate_record_without_gate_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            install_governance_bundle(root)
            write_gate_record(root, "G-REQ", ".sdd/G-REQ-HANDOFF.json")
            gate_path = root / "reviews/TEST-GATE-REQ-001.md"
            gate_path.write_text(
                gate_path.read_text(encoding="utf-8").replace("gate-id: G-REQ\n", ""),
                encoding="utf-8",
            )
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("gate record must declare a recognized gate-id", result.stderr)

    def test_greq_gate_record_without_result_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            install_governance_bundle(root)
            write_gate_record(root, "G-REQ", ".sdd/G-REQ-HANDOFF.json", result=None)
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("G-REQ gate record must declare gate-result", result.stderr)

    def test_frozen_garch_contract_and_explicit_check_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            revision = install_governance_bundle(root)
            write_arch_manifest(root, revision)
            result = run_validation(root)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_review_input_purpose_wrong_type_fails_with_actionable_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            revision = install_governance_bundle(root)
            write_arch_manifest(root, revision)
            manifest_path = root / ".sdd/G-ARCH-CONTRACT.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["review_inputs"] = [{
                "purpose": ["security-review"],
                "path": "specification.md",
                "id": "TEST-SPEC-001",
                "version": "0.1",
                "sha256": sha256(root / "specification.md"),
            }]
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("purpose must be a non-empty string", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_frozen_greq_detects_source_drift_and_duplicate_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            revision = install_governance_bundle(root)
            write_req_manifest(root, revision)
            (root / "specification.md").write_text(
                (root / "specification.md").read_text(encoding="utf-8") + "\nChanged after freeze.\n",
                encoding="utf-8",
            )
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("frozen file digest does not match", result.stderr)

            manifest = root / ".sdd/G-REQ-HANDOFF.json"
            manifest.write_text('{"scope":"one","scope":"two"}\n', encoding="utf-8")
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("duplicate JSON key 'scope'", result.stderr)

    def test_framework_lock_detects_modified_validator(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            install_governance_bundle(root)
            helper = root / "scripts/artifacts.py"
            helper.write_text(helper.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("file digest differs from the initialized framework snapshot", result.stderr)

    def test_handoff_rejects_unsupported_version_and_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            revision = install_governance_bundle(root)
            write_req_manifest(root, revision)
            manifest_path = root / ".sdd/G-REQ-HANDOFF.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["contract_version"] = 2
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("unsupported contract identity or version", result.stderr)

            manifest["contract_version"] = 1
            manifest["frozen_artifacts"][0]["path"] = "../mission.md"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("must be repository-relative and must not contain '..'", result.stderr)

    def test_handoff_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "app"
            root.mkdir()
            write_app_fixture(
                root,
                functional_row="| FR-001 | The system MUST save the item. | A persisted item is visible after reload. |",
                quality_row="| NFR-001 | The service MUST respond within one second. | A measured request completes within one second. |",
            )
            revision = install_governance_bundle(root)
            write_req_manifest(root, revision)
            outside = base / "outside.md"
            outside.write_text(artifact_text("TEST-OUTSIDE-001", "evidence"), encoding="utf-8")
            escaped = root / ".sdd/outside.md"
            escaped.symlink_to(outside)
            manifest_path = root / ".sdd/G-REQ-HANDOFF.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["frozen_artifacts"][0].update(
                {"path": ".sdd/outside.md", "id": "TEST-OUTSIDE-001", "sha256": sha256(outside)}
            )
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = run_validation(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("path resolves outside the repository", result.stderr)


if __name__ == "__main__":
    unittest.main()
