from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.artifacts import validate_assumption_records


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / "tests/fixtures/fw023_assumption_experiments.json").read_text(encoding="utf-8"))


class AssumptionExperimentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        schema_path = self.root / "docs/framework/schemas/assumption-experiment-v1.schema.json"
        schema_path.parent.mkdir(parents=True)
        shutil.copy2(ROOT / "docs/framework/schemas/assumption-experiment-v1.schema.json", schema_path)
        (self.root / "specification.md").write_text("| FR-APP-001 | Requirement | Evidence |\n", encoding="utf-8")
        (self.root / "backlog.md").write_text("- APP-TASK-001: sample task\n- APP-TASK-002: independent task\n", encoding="utf-8")
        self.data = copy.deepcopy(FIXTURE)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def check(self, data: dict, today: str = "2026-10-22") -> list[str]:
        with patch("scripts.artifacts.ROOT", self.root):
            from datetime import date
            return validate_assumption_records(data, date.fromisoformat(today))

    def test_synthetic_proposal_passes_but_is_not_an_outcome(self) -> None:
        self.assertEqual(self.check(self.data), [])
        self.assertEqual(self.data["experiments"][0]["status"], "proposed")
        self.assertIsNone(self.data["experiments"][0]["outcome"])

    def test_missing_owner_and_falsifier_fail_schema(self) -> None:
        del self.data["assumptions"][0]["owner"]
        del self.data["experiments"][0]["wrong_if"]
        del self.data["experiments"][0]["method"]
        problems = self.check(self.data)
        self.assertTrue(any("owner" in item for item in problems))
        self.assertTrue(any("wrong_if" in item for item in problems))
        self.assertTrue(any("method" in item for item in problems))

    def test_assumption_dates_are_required(self) -> None:
        del self.data["assumptions"][0]["due_date"]
        del self.data["assumptions"][0]["review_date"]
        problems = self.check(self.data)
        self.assertTrue(any("due_date" in item for item in problems))
        self.assertTrue(any("review_date" in item for item in problems))

    def test_overdue_open_assumption_fails_deterministically(self) -> None:
        self.data["assumptions"][0]["due_date"] = "2026-10-21"
        self.assertTrue(any("overdue" in item for item in self.check(self.data)))

    def test_expired_confirmed_assumption_cannot_support_gate(self) -> None:
        assumption = self.data["assumptions"][0]
        assumption.update({"status": "confirmed", "previous_status": "open", "gate_supporting": True, "review_date": "2026-10-21"})
        assumption["evidence"] = [{"id": "SAMPLE-EVID-002", "type": "observed", "source": "Study", "observed_at": "2026-10-20", "limits": "Small sample", "result": "Confirmed"}]
        self.assertTrue(any("review_date has expired" in item for item in self.check(self.data)))

    def test_inference_cannot_support_gate_pass(self) -> None:
        assumption = self.data["assumptions"][0]
        assumption.update({"status": "confirmed", "previous_status": "open", "gate_supporting": True})
        assumption["evidence"] = [{"id": "SAMPLE-EVID-002", "type": "inference", "source": "Reasoning", "observed_at": "2026-10-22", "limits": "Unverified", "result": "Likely"}]
        self.assertTrue(any("observed or external evidence" in item for item in self.check(self.data)))

    def test_reopening_confirmation_requires_rationale_and_dependent_reevaluation(self) -> None:
        assumption = self.data["assumptions"][0]
        assumption.update({"status": "open", "previous_status": "confirmed", "disposition": None})
        self.assertTrue(any("disposition" in item for item in self.check(self.data)))
        assumption["disposition"] = "New evidence challenges the prior result."
        assumption["task_effects"][0]["state"] = "blocked"
        self.assertEqual(self.check(self.data), [])

    def test_status_history_catches_reopen_even_when_previous_status_is_omitted(self) -> None:
        assumption = self.data["assumptions"][0]
        assumption["status_history"] = [
            {"status": "open", "recorded_at": "2026-10-20", "reason": "Initial record."},
            {"status": "confirmed", "recorded_at": "2026-10-21", "reason": "Evidence reviewed."},
            {"status": "open", "recorded_at": "2026-10-22", "reason": "Prior evidence challenged."},
        ]
        assumption["status"] = "open"
        assumption["previous_status"] = None
        assumption["disposition"] = None
        assumption["task_effects"][0]["state"] = "unblocked"
        self.assertTrue(any("disposition" in item for item in self.check(self.data)))
        assumption["disposition"] = "Prior evidence challenged."
        self.assertTrue(any("reopened after confirmation" in item for item in self.check(self.data)))
        assumption["task_effects"][0]["state"] = "blocked"
        self.assertEqual(self.check(self.data), [])

    def test_invalid_status_transition_and_broken_requirement_link_fail(self) -> None:
        self.data["assumptions"][0]["previous_status"] = "open"
        self.data["assumptions"][0]["status"] = "retired"
        self.data["assumptions"][0]["requirement_ids"] = ["MISSING-FR-999"]
        problems = self.check(self.data)
        self.assertTrue(any("transition" in item for item in problems))
        self.assertTrue(any("unknown canonical link" in item for item in problems))

    def test_synthetic_evidence_cannot_fabricate_completed_result_or_decision(self) -> None:
        experiment = self.data["experiments"][0]
        experiment.update({"status": "completed", "previous_status": "running", "outcome": {"observed_at": "2026-10-22", "actual_result": "4 of 5 completed", "evidence_ids": ["SAMPLE-EVID-001"]}})
        self.assertTrue(any("only linked observed/external evidence" in item for item in self.check(self.data)))

    def test_mixed_synthetic_and_observed_outcome_is_rejected(self) -> None:
        experiment = self.data["experiments"][0]
        experiment.update({"status": "completed", "previous_status": "running", "read_date": "2026-10-22", "outcome": {"observed_at": "2026-10-22", "actual_result": "Observed outcome", "evidence_ids": ["SAMPLE-EVID-001", "SAMPLE-EVID-002"]}})
        experiment["evidence"].append({"id": "SAMPLE-EVID-002", "type": "observed", "source": "Study", "observed_at": "2026-10-22", "limits": "Small sample", "result": "Observed"})
        self.assertTrue(any("only linked observed/external evidence" in item for item in self.check(self.data)))

    def test_decision_must_reference_completed_experiment_and_non_synthetic_evidence_in_canonical_log(self) -> None:
        experiment = self.data["experiments"][0]
        experiment.update({"status": "completed", "previous_status": "running", "read_date": "2026-10-22", "decision_id": "DECISION-001", "outcome": {"observed_at": "2026-10-22", "actual_result": "Observed outcome", "evidence_ids": ["SAMPLE-EVID-002"]}})
        experiment["evidence"] = [{"id": "SAMPLE-EVID-002", "type": "observed", "source": "Consent-based session record", "observed_at": "2026-10-22", "limits": "Small sample.", "result": "Recorded result."}]
        decision_log = self.root / "decisions/DECISION-LOG.md"
        decision_log.parent.mkdir()
        decision_log.write_text("---\nid: APP-DECISION-LOG-001\ntype: decision-log\ntitle: Decisions\nstatus: active\nversion: 0.1\ncreated: 2026-10-22\nupdated: 2026-10-22\n---\n\nDECISION-001 cites SAMPLE-EXP-001 and SAMPLE-EVID-002.\n", encoding="utf-8")
        self.assertEqual(self.check(self.data), [])
        decision_log.write_text(decision_log.read_text(encoding="utf-8").replace("SAMPLE-EVID-002", "MISSING-EVIDENCE"), encoding="utf-8")
        self.assertTrue(any("canonical decision log" in item for item in self.check(self.data)))

    def test_disproved_assumption_needs_disposition_and_conditional_work_can_reopen(self) -> None:
        assumption = self.data["assumptions"][0]
        assumption.update({"status": "disproved", "previous_status": "open", "disposition": None, "blocking_state": "blocked"})
        assumption["task_effects"][0]["state"] = "blocked"
        self.assertEqual(assumption["task_effects"][1]["state"], "unblocked")
        self.assertTrue(any("disposition" in item for item in self.check(self.data)))

    def test_disproved_assumption_cannot_leave_dependent_task_unblocked(self) -> None:
        assumption = self.data["assumptions"][0]
        assumption.update({"status": "disproved", "previous_status": "open", "disposition": "Revise setup flow.", "blocking_state": "blocked"})
        assumption["task_effects"][0]["state"] = "unblocked"
        self.assertTrue(any("disproval cannot leave an affected task unblocked" in item for item in self.check(self.data)))


if __name__ == "__main__":
    unittest.main()
