"""Synthetic-only tests for the FW-031 Actions evidence contract."""
from __future__ import annotations

import copy
import json
import unittest

from scripts import fw031_actions_evidence as contract


RUN_ID = 81234567
ATTEMPT = 2
JOB_ID = 9876543
SHA_WORKFLOW = "a" * 40
SHA_TRIGGER = "b" * 40
SHA_EXECUTED = "c" * 40


def _point(value: str | None, state: str = "available", source: str | None = "synthetic-fixture:time") -> dict[str, object]:
    return {"state": state, "value": value, "source": source}


def _fixture() -> dict[str, object]:
    return {
        "contract": "FRAMEWORK-CONTRACT-032",
        "schema_version": "1.0",
        "profile": "github-actions-run-job",
        "fixture_only": True,
        "source": {
            "acquisition_state": "complete",
            "repository_id": 1413825865,
            "repository_name": "naelmusleh/adversarial-sdd-boilerplate",
            "workflow_id": 381421429,
            "workflow_path": ".github/workflows/verify-pipeline.yml",
            "workflow_ref": "refs/heads/fixture",
            "source_ref": "synthetic-fixture://run/81234567/attempt/2/job/9876543",
            "observed_at": "2026-10-26T15:00:00Z",
            "response_revision": "fixture-response-v1",
            "response_digest": "sha256:" + "d" * 64,
        },
        "identity": {
            "state": "available", "run_id": RUN_ID, "run_attempt": ATTEMPT,
            "job_id": JOB_ID, "job_name": "fixture-check", "event_name": "pull_request",
        },
        "revisions": {
            "workflow": {"state": "available", "value": SHA_WORKFLOW, "source": "synthetic-fixture:workflow-revision"},
            "triggering": {"state": "available", "value": SHA_TRIGGER, "source": "synthetic-fixture:head-revision"},
            "executed": {"state": "available", "value": SHA_EXECUTED, "source": "synthetic-fixture:checkout-revision"},
        },
        "timing": {
            "run": {
                "run_id": RUN_ID, "run_attempt": ATTEMPT, "job_id": JOB_ID,
                "started_at": _point("2026-10-26T14:00:00Z"),
                "completed_at": _point("2026-10-26T14:05:00Z"),
            },
            "job": {
                "run_id": RUN_ID, "run_attempt": ATTEMPT, "job_id": JOB_ID,
                "started_at": _point("2026-10-26T14:00:05Z"),
                "completed_at": _point("2026-10-26T14:04:55Z"),
            },
        },
        "timeout": {
            "configuration_state": "configured", "minutes": 30,
            "configuration_revision": SHA_WORKFLOW, "configuration_source": "synthetic-fixture:workflow-config",
            "observed_state": "unknown", "host_conclusion": "success", "observation_source": "synthetic-fixture:job-conclusion",
        },
        "cancellation": {
            "request_state": "not-requested", "requested_at": None, "request_source": None,
            "host_terminal_state": "completed", "terminal_source": "synthetic-fixture:job-conclusion",
            "workload_state": "unknown", "workload_observation": None,
        },
        "measurements": [],
        "limitations": ["timeout-unknown", "cancellation-unknown", "workload-termination-unobserved", "metrics-unknown"],
    }


def _validate(record: dict[str, object]) -> dict[str, object]:
    return contract.validate_actions_evidence(json.dumps(record, separators=(",", ":")))


class ActionsEvidenceContractTests(unittest.TestCase):
    def test_complete_labeled_synthetic_fixture_is_structurally_valid(self) -> None:
        result = _validate(_fixture())
        self.assertTrue(result["valid"], result["diagnostics"])
        self.assertEqual(result["validation_scope"], "structure-and-declared-invariants-only")
        self.assertEqual(result["contract"], "FRAMEWORK-CONTRACT-032")

    def test_denied_source_can_preserve_unknown_identity_without_claiming_success(self) -> None:
        record = _fixture()
        record["source"]["acquisition_state"] = "denied"
        record["identity"] = {"state": "unavailable", "run_id": None, "run_attempt": None, "job_id": None, "job_name": None, "event_name": None}
        record["source"]["repository_id"] = None
        record["source"]["repository_name"] = None
        record["source"]["workflow_id"] = None
        record["source"]["workflow_path"] = None
        record["source"]["workflow_ref"] = None
        record["revisions"] = {name: {"state": "unknown", "value": None, "source": None} for name in ("workflow", "triggering", "executed")}
        for interval in record["timing"].values():
            interval.update(run_id=None, run_attempt=None, job_id=None)
            interval["started_at"] = _point(None, "unavailable", None)
            interval["completed_at"] = _point(None, "unavailable", None)
        record["timeout"] = {"configuration_state": "unknown", "minutes": None, "configuration_revision": None, "configuration_source": None, "observed_state": "unavailable", "host_conclusion": "unavailable", "observation_source": None}
        record["cancellation"] = {"request_state": "unavailable", "requested_at": None, "request_source": None, "host_terminal_state": "unavailable", "terminal_source": None, "workload_state": "unavailable", "workload_observation": None}
        record["limitations"] = ["source-denied", "identity-incomplete", "revision-unknown", "timing-unknown", "timeout-unknown", "cancellation-unknown", "workload-termination-unobserved", "metrics-unknown"]
        result = _validate(record)
        self.assertTrue(result["valid"], result["diagnostics"])

    def test_partial_and_unavailable_source_states_are_explicit(self) -> None:
        for acquisition_state, limitation in (("partial", "source-partial"), ("unavailable", "source-unavailable")):
            with self.subTest(acquisition_state=acquisition_state):
                record = _fixture()
                record["source"]["acquisition_state"] = acquisition_state
                record["identity"] = {"state": "unknown", "run_id": None, "run_attempt": None, "job_id": None, "job_name": None, "event_name": None}
                record["revisions"] = {name: {"state": "unknown", "value": None, "source": None} for name in ("workflow", "triggering", "executed")}
                for interval in record["timing"].values():
                    interval.update(run_id=None, run_attempt=None, job_id=None)
                    interval["started_at"] = _point(None, "unknown", None)
                    interval["completed_at"] = _point(None, "unknown", None)
                record["timeout"] = {"configuration_state": "unknown", "minutes": None, "configuration_revision": None, "configuration_source": None, "observed_state": "unknown", "host_conclusion": "unknown", "observation_source": None}
                record["cancellation"] = {"request_state": "unknown", "requested_at": None, "request_source": None, "host_terminal_state": "unknown", "terminal_source": None, "workload_state": "unknown", "workload_observation": None}
                record["limitations"] = [limitation, "identity-incomplete", "revision-unknown", "timing-unknown", "timeout-unknown", "cancellation-unknown", "workload-termination-unobserved", "metrics-unknown"]
                self.assertTrue(_validate(record)["valid"])

    def test_unknown_identity_cannot_carry_only_some_tuple_fields(self) -> None:
        record = _fixture()
        record["identity"]["state"] = "unknown"
        result = _validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("fw031.actions_evidence.identity_state", {item["code"] for item in result["diagnostics"]})

    def test_timing_cannot_cross_run_attempt_or_job(self) -> None:
        record = _fixture()
        record["timing"]["job"]["run_attempt"] = ATTEMPT - 1
        result = _validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("fw031.actions_evidence.identity_mismatch", {item["code"] for item in result["diagnostics"]})

    def test_reversed_job_interval_is_rejected(self) -> None:
        record = _fixture()
        record["timing"]["job"]["completed_at"] = _point("2026-10-26T13:00:00Z")
        result = _validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("fw031.actions_evidence.time_order", {item["code"] for item in result["diagnostics"]})

    def test_available_revision_requires_its_own_source_and_sha(self) -> None:
        record = _fixture()
        record["revisions"]["executed"]["value"] = None
        result = _validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("fw031.actions_evidence.revision_provenance", {item["code"] for item in result["diagnostics"]})

    def test_configured_timeout_is_separate_from_observed_timeout(self) -> None:
        record = _fixture()
        record["timeout"]["observed_state"] = "timed-out"
        record["timeout"]["host_conclusion"] = "success"
        result = _validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("fw031.actions_evidence.timeout_outcome", {item["code"] for item in result["diagnostics"]})

    def test_cancelled_host_does_not_imply_workload_termination(self) -> None:
        record = _fixture()
        record["cancellation"]["host_terminal_state"] = "cancelled"
        record["cancellation"]["terminal_source"] = "synthetic-fixture:host"
        record["cancellation"]["workload_state"] = "unknown"
        result = _validate(record)
        self.assertTrue(result["valid"], result["diagnostics"])

    def test_workload_confirmation_requires_observation_reference(self) -> None:
        record = _fixture()
        record["cancellation"]["workload_state"] = "confirmed"
        result = _validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("fw031.actions_evidence.workload_confirmation", {item["code"] for item in result["diagnostics"]})

    def test_proxy_metric_is_rejected_even_with_numeric_value(self) -> None:
        record = _fixture()
        record["measurements"] = [{"name": "tool_calls", "state": "measured", "binding": {"run_id": RUN_ID, "run_attempt": ATTEMPT, "job_id": JOB_ID}, "value": 3, "unit": "calls", "source_kind": "proxy", "source": "synthetic-fixture:steps-count", "scope": "job", "interval": {"started_at": "2026-10-26T14:00:05Z", "completed_at": "2026-10-26T14:04:55Z"}, "reason": None}]
        result = _validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("fw031.actions_evidence.measurement_proxy", {item["code"] for item in result["diagnostics"]})

    def test_synthetic_provenance_cannot_be_mislabeled_as_observed(self) -> None:
        record = _fixture()
        record["fixture_only"] = False
        record["measurements"] = [{"name": "cpu_time", "state": "measured", "binding": {"run_id": RUN_ID, "run_attempt": ATTEMPT, "job_id": JOB_ID}, "value": 1.5, "unit": "seconds", "source_kind": "synthetic-fixture", "source": "synthetic-fixture:invented", "scope": "job", "interval": None, "reason": None}]
        result = _validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("fw031.actions_evidence.synthetic_claim", {item["code"] for item in result["diagnostics"]})

    def test_unknown_measurement_cannot_be_treated_as_zero(self) -> None:
        record = _fixture()
        record["measurements"] = [{"name": "spend", "state": "unknown", "binding": {"run_id": RUN_ID, "run_attempt": ATTEMPT, "job_id": JOB_ID}, "value": 0, "unit": None, "source_kind": None, "source": None, "scope": None, "interval": None, "reason": "not-observed"}]
        result = _validate(record)
        self.assertFalse(result["valid"])

    def test_synthetic_metric_provenance_is_structural_only_and_bound_to_fixture(self) -> None:
        record = _fixture()
        record["measurements"] = [
            {"name": "tool_calls", "state": "measured", "binding": {"run_id": RUN_ID, "run_attempt": ATTEMPT, "job_id": JOB_ID}, "value": 4, "unit": "calls", "source_kind": "synthetic-fixture", "source": "synthetic-fixture:invented-counter", "scope": "job", "interval": {"started_at": "2026-10-26T14:00:05Z", "completed_at": "2026-10-26T14:04:55Z"}, "reason": None},
            {"name": "spend", "state": "measured", "binding": {"run_id": RUN_ID, "run_attempt": ATTEMPT, "job_id": JOB_ID}, "value": 1.25, "unit": "USD", "source_kind": "synthetic-fixture", "source": "synthetic-fixture:invented-meter", "scope": "run", "interval": {"started_at": "2026-10-26T14:00:00Z", "completed_at": "2026-10-26T14:05:00Z"}, "reason": None},
        ]
        result = _validate(record)
        self.assertTrue(result["valid"], result["diagnostics"])
        self.assertTrue(record["fixture_only"])

    def test_measurement_cannot_cross_run_attempt_or_job(self) -> None:
        record = _fixture()
        record["measurements"] = [{"name": "tool_calls", "state": "measured", "binding": {"run_id": RUN_ID, "run_attempt": ATTEMPT - 1, "job_id": JOB_ID}, "value": 4, "unit": "calls", "source_kind": "synthetic-fixture", "source": "synthetic-fixture:invented-counter", "scope": "job", "interval": {"started_at": "2026-10-26T14:00:05Z", "completed_at": "2026-10-26T14:04:55Z"}, "reason": None}]
        result = _validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("fw031.actions_evidence.measurement_binding", {item["code"] for item in result["diagnostics"]})

    def test_spend_cannot_use_generic_instrumentation_as_meter(self) -> None:
        record = _fixture()
        record["measurements"] = [{"name": "spend", "state": "measured", "binding": {"run_id": RUN_ID, "run_attempt": ATTEMPT, "job_id": JOB_ID}, "value": 1, "unit": "USD", "source_kind": "direct-instrumentation", "source": "synthetic-fixture:counter", "scope": "run", "interval": {"started_at": "2026-10-26T14:00:00Z", "completed_at": "2026-10-26T14:05:00Z"}, "reason": None}]
        result = _validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("fw031.actions_evidence.spend_source", {item["code"] for item in result["diagnostics"]})

    def test_duplicate_measurements_are_rejected(self) -> None:
        record = _fixture()
        unknown = {"name": "spend", "state": "unknown", "binding": {"run_id": RUN_ID, "run_attempt": ATTEMPT, "job_id": JOB_ID}, "value": None, "unit": None, "source_kind": None, "source": None, "scope": None, "interval": None, "reason": "not-observed"}
        record["measurements"] = [copy.deepcopy(unknown), copy.deepcopy(unknown)]
        result = _validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("fw031.actions_evidence.duplicate_measurement", {item["code"] for item in result["diagnostics"]})

    def test_duplicate_json_keys_are_rejected_without_echoing_input(self) -> None:
        result = contract.validate_actions_evidence('{"contract":"x","contract":"secret"}')
        self.assertFalse(result["valid"])
        self.assertNotIn("secret", json.dumps(result))

    def test_extra_fields_and_unknown_metric_names_fail_closed(self) -> None:
        record = _fixture()
        record["unreviewed_claim"] = "anything"
        result = _validate(record)
        self.assertFalse(result["valid"])
        record = _fixture()
        record["measurements"] = [{"name": "agent_tokens", "state": "unknown", "value": None, "unit": None, "source_kind": None, "source": None, "scope": None, "interval": None, "reason": "not-instrumented"}]
        self.assertFalse(_validate(record)["valid"])

    def test_diagnostics_are_bounded_and_deterministic(self) -> None:
        record = _fixture()
        for key in ("unexpected-a", "unexpected-b", "unexpected-c"):
            record[key] = "private-value"
        first, second = _validate(record), _validate(record)
        self.assertEqual(first, second)
        self.assertLessEqual(len(first["diagnostics"]), 32)
        self.assertNotIn("private-value", json.dumps(first))


if __name__ == "__main__":
    unittest.main()
