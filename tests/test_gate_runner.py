from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.artifacts import (
    APP_GATE_RUNS,
    GATE_ORDER,
    _atomic_create_json,
    _application_identity,
    _gate_write_lock,
    candidate_source_revision_problems,
    _cleanup_governance_temps,
    gate_transition_table,
    staged_governance_problems,
    validate_gate_run_records,
    validate_review_run,
    REVIEW_RUN_SCHEMA,
    schema_definition_problems,
)


ROOT = Path(__file__).resolve().parents[1]
V1_SCHEMA = ROOT / "docs/framework/schemas/gate-run-v1.schema.json"
V1_FIXTURE = ROOT / "docs/framework/examples/gate-contract-v1/valid/G-INTENT.json"
INPUT_FIXTURE = ROOT / "docs/framework/examples/gate-contract-v1/inputs/FIXTURE-INPUT-001.md"
MISSION = "---\nid: SYNTHETIC-MISSION-001\ntype: mission\ntitle: Synthetic mission\nstatus: draft\nversion: 1.0\n---\n\nSynthetic fixture.\n"


class GateRunnerTests(unittest.TestCase):
    def _app_root(self, parent: Path) -> Path:
        root = parent / "app"
        root.mkdir()
        (root / "mission.md").write_text(MISSION, encoding="utf-8")
        (root / "specification.md").write_text("Synthetic requirement: FIXTURE-REQ-001\n", encoding="utf-8")
        (root / "backlog.md").write_text("Synthetic task: FIXTURE-TASK-001\n", encoding="utf-8")
        input_path = root / "docs/framework/examples/gate-contract-v1/inputs/FIXTURE-INPUT-001.md"
        input_path.parent.mkdir(parents=True)
        input_path.write_bytes(INPUT_FIXTURE.read_bytes())
        return root

    def test_plan_enumerates_legal_and_illegal_results_for_all_ten_gates(self) -> None:
        plan = gate_transition_table("1.0")
        rows = plan["transitions"]
        self.assertEqual({row["gate_id"] for row in rows}, set(GATE_ORDER))
        self.assertEqual(len(rows), 10 * 8 * 8)
        self.assertTrue(any(row["legal"] for row in rows))
        self.assertTrue(any(not row["legal"] for row in rows))
        self.assertEqual(plan["contract_version"], "1.0")

    def test_runner_refuses_to_adopt_pinned_draft_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._app_root(Path(temporary))
            lock_path = root / ".sdd/framework.lock.json"
            lock_path.parent.mkdir(parents=True)
            lock_path.write_text(json.dumps({"lock_version": 4, "gate_contract_id": "FRAMEWORK-GATE-CONTRACT-001", "gate_contract_version": "1.2"}), encoding="utf-8")
            _, version, errors = _application_identity(root)
            self.assertEqual(version, "1.2")
            self.assertTrue(any("not approved for runner use" in error for error in errors))

    def test_runner_reports_malformed_lock_version_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._app_root(Path(temporary))
            lock_path = root / ".sdd/framework.lock.json"
            lock_path.parent.mkdir(parents=True)
            lock_path.write_text(json.dumps({"lock_version": "four"}), encoding="utf-8")
            _, _, errors = _application_identity(root)
            self.assertTrue(any("lock_version must be an integer" in error for error in errors), errors)

    def test_candidate_run_is_validated_before_publication(self) -> None:
        schema = json.loads(V1_SCHEMA.read_text(encoding="utf-8"))
        record = json.loads(V1_FIXTURE.read_text(encoding="utf-8"))
        record["application_id"] = "SYNTHETIC"
        with tempfile.TemporaryDirectory() as temporary:
            root = self._app_root(Path(temporary))
            errors = validate_gate_run_records(root, schema, "SYNTHETIC", candidate=record)
            self.assertEqual(errors, [])
            self.assertFalse((root / APP_GATE_RUNS / f"{record['record_id']}.json").exists())

    def test_downstream_candidate_without_current_prerequisite_is_rejected(self) -> None:
        schema = json.loads(V1_SCHEMA.read_text(encoding="utf-8"))
        record = json.loads((ROOT / "docs/framework/examples/gate-contract-v1/valid/G-SETUP.json").read_text(encoding="utf-8"))
        record["application_id"] = "SYNTHETIC"
        with tempfile.TemporaryDirectory() as temporary:
            root = self._app_root(Path(temporary))
            errors = validate_gate_run_records(root, schema, "SYNTHETIC", candidate=record)
            self.assertTrue(any("prerequisite G-INTENT has no current run" in error for error in errors), errors)

    def test_candidate_validation_routes_every_gate_fixture(self) -> None:
        schema = json.loads(V1_SCHEMA.read_text(encoding="utf-8"))
        fixture_dir = ROOT / "docs/framework/examples/gate-contract-v1/valid"
        for gate_id in GATE_ORDER:
            with self.subTest(gate=gate_id), tempfile.TemporaryDirectory() as temporary:
                root = self._app_root(Path(temporary))
                record = json.loads((fixture_dir / f"{gate_id}.json").read_text(encoding="utf-8"))
                record["application_id"] = "SYNTHETIC"
                errors = validate_gate_run_records(root, schema, "SYNTHETIC", candidate=record)
                if gate_id == "G-INTENT":
                    self.assertEqual(errors, [])
                else:
                    self.assertTrue(any("prerequisite G-INTENT has no current run" in error for error in errors), errors)
                invalid = json.loads((ROOT / "docs/framework/examples/gate-contract-v1/invalid" / f"{gate_id}.json").read_text(encoding="utf-8"))
                invalid["application_id"] = "SYNTHETIC"
                invalid_errors = validate_gate_run_records(root, schema, "SYNTHETIC", candidate=invalid)
                self.assertTrue(invalid_errors, f"invalid {gate_id} fixture unexpectedly validated")

    def test_atomic_create_never_overwrites_and_cleans_temp_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / ".sdd/gate-runs/record.json"
            _atomic_create_json(root, target, {"record_id": "FIRST"})
            with self.assertRaises(FileExistsError):
                _atomic_create_json(root, target, {"record_id": "SECOND"})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"record_id": "FIRST"})
            target.unlink()
            with patch("scripts.artifacts.os.link", side_effect=OSError("injected interruption")):
                with self.assertRaisesRegex(OSError, "injected interruption"):
                    _atomic_create_json(root, target, {"record_id": "THIRD"})
            self.assertFalse(target.exists())
            self.assertEqual(list((root / ".sdd").glob(".governance-*.tmp")), [])

    def test_interrupted_staging_file_is_recovered_without_entering_record_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            gate_runs = root / ".sdd/gate-runs"
            gate_runs.mkdir(parents=True)
            stale_temp = root / ".sdd/.governance-interrupted.tmp"
            stale_temp.write_text("partial", encoding="utf-8")
            _cleanup_governance_temps(root)
            self.assertFalse(stale_temp.exists())
            self.assertEqual(list(gate_runs.iterdir()), [])

    def test_lock_contention_fails_closed_after_bounded_wait(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with _gate_write_lock(root):
                with self.assertRaisesRegex(TimeoutError, "contention"):
                    with _gate_write_lock(root, timeout=0.05):
                        self.fail("contending writer unexpectedly acquired the lock")

    def test_lock_symlink_is_rejected_without_touching_outside_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "app"
            root.mkdir()
            sdd = root / ".sdd"
            sdd.mkdir()
            outside = Path(temporary) / "outside.lock"
            outside.write_text("untouched", encoding="utf-8")
            (sdd / ".governance-write.lock").symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "must not be a symlink"):
                with _gate_write_lock(root):
                    pass
            self.assertEqual(outside.read_text(encoding="utf-8"), "untouched")

    def test_atomic_publication_rejects_symlinked_record_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "app"
            root.mkdir()
            outside = Path(temporary) / "outside"
            outside.mkdir()
            (root / ".sdd").mkdir()
            (root / ".sdd/gate-runs").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "inside the repository|real directory"):
                _atomic_create_json(root, root / ".sdd/gate-runs/record.json", {"record_id": "SYMLINK-001"})
            self.assertEqual(list(outside.iterdir()), [])

    def test_candidate_clean_commit_must_match_current_head_and_clean_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._app_root(Path(temporary))
            subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "fixture@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Fixture"], check=True)
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
            head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
            record = json.loads(V1_FIXTURE.read_text(encoding="utf-8"))
            self.assertTrue(candidate_source_revision_problems(root, record, "candidate.json"))
            record["source_snapshot"]["commit_sha"] = head
            self.assertEqual(candidate_source_revision_problems(root, record, "candidate.json"), [])
            (root / "specification.md").write_text("changed after snapshot\n", encoding="utf-8")
            self.assertTrue(any("uncommitted source changes" in error for error in candidate_source_revision_problems(root, record, "candidate.json")))

    def test_staged_guard_rejects_mutation_but_allows_json_append(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch("scripts.artifacts.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout=b"M\0.sdd/gate-runs/OLD.json\0", stderr=b"")):
                errors = staged_governance_problems(root)
            self.assertTrue(any("may only be added" in error for error in errors))
            with patch("scripts.artifacts.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout=b"A\0.sdd/review-runs/NEW.json\0", stderr=b"")):
                self.assertEqual(staged_governance_problems(root), [])

    def test_review_record_is_advisory_and_frozen_inputs_are_digest_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._app_root(Path(temporary))
            frozen = root / "mission.md"
            import hashlib
            digest = "sha256:" + hashlib.sha256(frozen.read_bytes()).hexdigest()
            record = {
                "record_id": "SYNTHETIC-REVIEW-001", "record_version": 1,
                "created_at": "2026-10-21T12:00:00Z", "application_id": "SYNTHETIC",
                "contract_id": "FRAMEWORK-GATE-CONTRACT-001", "contract_version": "1.0",
                "reviewer": {"identity": "reviewer-1", "mode": "independent", "context_disclosure": "frozen input only", "author_overlap": "none"},
                "mode": "independent", "target_ids": ["SYNTHETIC-MISSION-001"],
                "frozen_inputs": [{"path": "mission.md", "sha256": digest}],
                "findings": [{"finding_id": "REVIEW-001/FINDING-001", "severity": "minor", "evidence": "fixture observation", "disposition": "open", "disposition_evidence": ""}],
                "rerun_of": None, "result": "advisory",
                "authority_boundary": {"gate_authority": False, "ci_evidence": False, "owner_authorization": False},
            }
            self.assertEqual(validate_review_run(root, record, "1.0"), [])
            record["result"] = "passed"
            self.assertTrue(any("const" in error for error in validate_review_run(root, record, "1.0")))
            record["result"] = "advisory"
            frozen.write_text(MISSION + "changed\n", encoding="utf-8")
            self.assertTrue(any("digest does not match" in error for error in validate_review_run(root, record, "1.0")))

    def test_machine_readable_review_schema_is_valid_and_advisory_only(self) -> None:
        self.assertEqual(schema_definition_problems(REVIEW_RUN_SCHEMA), [])
        self.assertEqual(REVIEW_RUN_SCHEMA["properties"]["result"]["const"], "advisory")
        self.assertFalse(REVIEW_RUN_SCHEMA["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
