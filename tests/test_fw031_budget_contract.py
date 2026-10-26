"""Synthetic-only contract fixtures for FW-031 policy and stop records."""
from __future__ import annotations

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

from scripts import fw031_budget_contract as contract


ROOT_RUN = "00000000-0000-4000-8000-000000000001"
CHILD_RUN = "00000000-0000-4000-8000-000000000002"
PREVIOUS_RUN = "00000000-0000-4000-8000-000000000003"


def _limit(
    limit_id: str,
    kind: str,
    unit: str,
    source_kind: str,
    source_id: str,
    *,
    requested: bool = True,
    capability: str = "advisory",
    warning: int | float | None = None,
    exhaustion: int | float | None = None,
) -> dict[str, Any]:
    return {
        "id": limit_id,
        "kind": kind,
        "unit": unit,
        "scope": "run-tree" if kind == "retry-count" else "run",
        "requested": requested,
        "measurement_source": {"kind": source_kind, "id": source_id},
        "capability": capability,
        "start_event": "agent-start" if kind == "retry-count" else "run-start",
        "reset_behavior": "new-run-only",
        "warning_threshold": warning,
        "exhaustion_threshold": exhaustion,
        "threshold_action": "record-exhaustion",
        "unavailable_behavior": "continue-advisory" if capability == "advisory" else "block-run",
    }


def _policy(**changes: Any) -> dict[str, Any]:
    value = {
        "schema_version": "1.0",
        "policy_id": "synthetic-budget-fixture",
        "policy_revision": "fixture-r1",
        "policy_digest": "0" * 64,
        "source_revision": "a" * 40,
        "run_scope": "agent-tree",
        "nested_run_accounting": "per-run-exclusive",
        "reset_behavior": "new-run-only",
        "override_policy": "disabled",
        "limits": [
            _limit("wall-time", "wall-clock", "seconds", "synthetic-fixture", "fixture-clock", warning=8, exhaustion=10),
            _limit("retries", "retry-count", "count", "synthetic-fixture", "fixture-coordinator", warning=2, exhaustion=4),
            _limit("tool-calls", "tool-invocation", "count", "synthetic-fixture", "fixture-coordinator", warning=10, exhaustion=20),
            _limit("memory", "resource", "MiB", "synthetic-fixture", "fixture-controller", warning=512, exhaustion=1024),
            _limit("spend", "spend", "USD", "unselected", "not-selected", requested=False, capability="unavailable"),
        ],
    }
    value.update(changes)
    return contract.seal_policy(value)


def _observation(
    observation_id: str,
    limit_id: str,
    owner: str,
    sequence: int,
    value: float | int,
    unit: str,
    source_id: str,
) -> dict[str, Any]:
    return {
        "observation_id": observation_id,
        "limit_id": limit_id,
        "accounting_owner_run_id": owner,
        "sequence": sequence,
        "state": "observed",
        "value": value,
        "unit": unit,
        "source_id": source_id,
        "unavailable_reason": None,
    }


def _result(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "policy_id": policy["policy_id"],
        "policy_revision": policy["policy_revision"],
        "policy_digest": policy["policy_digest"],
        "source_revision": policy["source_revision"],
        "run_id": ROOT_RUN,
        "started_at": "2026-10-26T10:00:00Z",
        "ended_at": "2026-10-26T10:01:00Z",
        "accounting_mode": policy["nested_run_accounting"],
        "runs": [
            {"run_id": ROOT_RUN, "parent_run_id": None},
            {"run_id": CHILD_RUN, "parent_run_id": ROOT_RUN},
        ],
        "observations": [
            _observation("00000000-0000-4000-8000-000000000010", "wall-time", ROOT_RUN, 1, 3, "seconds", "fixture-clock"),
            _observation("00000000-0000-4000-8000-000000000011", "retries", CHILD_RUN, 1, 1, "count", "fixture-coordinator"),
        ],
        "stop_state": "clear",
        "execution_outcome": "completed",
        "cancellation": {"state": "none", "termination_observation_ref": None},
        "checkpoint": {
            "last_durable_checkpoint_ref": None,
            "preservation_state": "unknown",
            "preservation_evidence_ref": None,
            "remaining_verification": [],
            "next_authorized_action": "Continue with remaining verification.",
        },
        "spend": {
            "state": "unknown",
            "amount": None,
            "currency": None,
            "meter_kind": None,
            "meter_id": None,
            "source_run_id": None,
            "window": None,
            "provenance_ref": None,
            "unknown_reason": "not-selected",
        },
        "override_authorization": None,
        "reset_events": [],
    }


def _validate_result(result: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    return contract.validate_budget_result(json.dumps(result), json.dumps(policy))


class Fw031BudgetContractTests(unittest.TestCase):
    def test_schemas_are_versioned_and_valid_records_are_deterministic(self) -> None:
        policy = _policy()
        result = _result(policy)
        policy_text = json.dumps(policy, sort_keys=True)
        result_text = json.dumps(result, sort_keys=True)

        self.assertTrue(contract.validate_budget_policy(policy_text)["valid"])
        first = contract.validate_budget_result(result_text, policy_text)
        second = contract.validate_budget_result(result_text, policy_text)
        self.assertTrue(first["valid"])
        self.assertEqual(first, second)
        self.assertEqual(first["validation_scope"], "structure-and-declared-invariants-only")
        for path in contract._SCHEMAS.values():
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_policy_digest_version_required_fields_and_limit_invariants_fail_closed(self) -> None:
        base = _policy()
        cases = []

        stale_digest = copy.deepcopy(base)
        stale_digest["limits"][0]["unit"] = "minutes"
        cases.append(stale_digest)

        unknown_version = copy.deepcopy(base)
        unknown_version["schema_version"] = "2.0"
        cases.append(contract.seal_policy(unknown_version))

        missing_scope = copy.deepcopy(base)
        missing_scope.pop("nested_run_accounting")
        cases.append(contract.seal_policy(missing_scope))

        extra_field = copy.deepcopy(base)
        extra_field["unreviewed_claim"] = True
        cases.append(contract.seal_policy(extra_field))

        reversed_thresholds = copy.deepcopy(base)
        reversed_thresholds["limits"][0]["warning_threshold"] = 10
        reversed_thresholds["limits"][0]["exhaustion_threshold"] = 8
        cases.append(contract.seal_policy(reversed_thresholds))

        synthetic_enforcement = copy.deepcopy(base)
        synthetic_enforcement["limits"][0]["capability"] = "enforced"
        synthetic_enforcement["limits"][0]["unavailable_behavior"] = "block-run"
        cases.append(contract.seal_policy(synthetic_enforcement))

        unavailable_fallback = copy.deepcopy(base)
        unavailable_fallback["limits"][4].update(
            requested=True,
            warning_threshold=3,
            exhaustion_threshold=5,
            unavailable_behavior="continue-advisory",
        )
        cases.append(contract.seal_policy(unavailable_fallback))

        disabled_threshold = copy.deepcopy(base)
        disabled_threshold["limits"][0]["requested"] = False
        cases.append(contract.seal_policy(disabled_threshold))

        for case in cases:
            with self.subTest(policy=case):
                self.assertFalse(contract.validate_budget_policy(json.dumps(case))["valid"])

    def test_policy_rejects_duplicate_ids_and_unselected_requested_spend(self) -> None:
        policy = _policy()
        duplicate = copy.deepcopy(policy)
        duplicate["limits"].append(copy.deepcopy(duplicate["limits"][0]))
        self.assertIn("fw031.policy.duplicate_limit", {d["code"] for d in contract.validate_budget_policy(json.dumps(contract.seal_policy(duplicate)))["diagnostics"]})

        unselected = copy.deepcopy(policy)
        unselected["limits"][4].update(requested=True, exhaustion_threshold=10)
        out = contract.validate_budget_policy(json.dumps(contract.seal_policy(unselected)))
        self.assertIn("fw031.policy.spend_source", {d["code"] for d in out["diagnostics"]})

    def test_strict_json_duplicate_keys_invalid_utf8_nan_and_size_limit(self) -> None:
        for raw in (
            '{"schema_version":"1.0","schema_version":"1.0"}',
            '{"schema_version": NaN}',
            '{"schema_version":"1.0","value":1e999}',
            '{"private-value":',
            b"\xff",
            " " * (contract._MAX_INPUT_BYTES + 1),
        ):
            outcome = contract.validate_budget_policy(raw)
            self.assertFalse(outcome["valid"])
            self.assertTrue(outcome["diagnostics"])
        rendered = json.dumps(contract.validate_budget_policy('{"secret-token-value":'), sort_keys=True)
        self.assertNotIn("secret-token-value", rendered)

    def test_result_requires_exact_policy_and_source_revision_binding(self) -> None:
        policy = _policy()
        result = _result(policy)
        mutations = (
            lambda value: value.update(policy_revision="other"),
            lambda value: value.update(policy_digest="0" * 64),
            lambda value: value.update(source_revision="b" * 40),
        )
        for mutate in mutations:
            case = copy.deepcopy(result)
            mutate(case)
            out = _validate_result(case, policy)
            self.assertIn("fw031.result.policy_binding", {d["code"] for d in out["diagnostics"]})

        invalid_policy = copy.deepcopy(policy)
        invalid_policy["policy_digest"] = "0" * 64
        out = contract.validate_budget_result(json.dumps(result), json.dumps(invalid_policy))
        self.assertIn("fw031.result.policy_invalid", {d["code"] for d in out["diagnostics"]})

    def test_observations_enforce_owner_scope_unit_source_and_unique_accounting(self) -> None:
        policy = _policy()
        result = _result(policy)

        duplicate = copy.deepcopy(result)
        duplicate_obs = copy.deepcopy(duplicate["observations"][1])
        duplicate_obs["observation_id"] = "00000000-0000-4000-8000-000000000012"
        duplicate["observations"].append(duplicate_obs)
        self.assertIn("fw031.result.double_accounting", {d["code"] for d in _validate_result(duplicate, policy)["diagnostics"]})

        unknown_owner = copy.deepcopy(result)
        unknown_owner["observations"][0]["accounting_owner_run_id"] = PREVIOUS_RUN
        self.assertIn("fw031.result.unknown_accounting_owner", {d["code"] for d in _validate_result(unknown_owner, policy)["diagnostics"]})

        mismatched_source = copy.deepcopy(result)
        mismatched_source["observations"][0]["source_id"] = "unrelated-source"
        self.assertIn("fw031.result.observation_binding", {d["code"] for d in _validate_result(mismatched_source, policy)["diagnostics"]})

        duplicate_run = copy.deepcopy(result)
        duplicate_run["runs"].append(copy.deepcopy(duplicate_run["runs"][1]))
        self.assertIn("fw031.result.duplicate_run", {d["code"] for d in _validate_result(duplicate_run, policy)["diagnostics"]})

    def test_nested_aggregation_is_root_owned_and_unavailable_accounting_cannot_claim_children(self) -> None:
        policy = _policy(nested_run_accounting="aggregate-at-root")
        result = _result(policy)
        result["observations"][1]["accounting_owner_run_id"] = CHILD_RUN
        self.assertIn("fw031.result.aggregate_owner", {d["code"] for d in _validate_result(result, policy)["diagnostics"]})
        result["observations"][1]["accounting_owner_run_id"] = ROOT_RUN
        self.assertTrue(_validate_result(result, policy)["valid"])

        unavailable_policy = _policy(nested_run_accounting="unavailable")
        unavailable_result = _result(unavailable_policy)
        self.assertIn("fw031.result.accounting_unavailable", {d["code"] for d in _validate_result(unavailable_result, unavailable_policy)["diagnostics"]})
        unavailable_result["runs"] = [{"run_id": ROOT_RUN, "parent_run_id": None}]
        for observation in unavailable_result["observations"]:
            observation["accounting_owner_run_id"] = ROOT_RUN
        self.assertTrue(_validate_result(unavailable_result, unavailable_policy)["valid"])

    def test_unavailable_measurements_are_unknown_and_not_numeric(self) -> None:
        policy = _policy()
        result = _result(policy)
        result["observations"][0].update(state="unavailable", value=None, unavailable_reason="source-error")
        self.assertTrue(_validate_result(result, policy)["valid"])
        result["observations"][0]["value"] = 3
        self.assertIn("fw031.result.observation_state", {d["code"] for d in _validate_result(result, policy)["diagnostics"]})

    def test_warning_exhaustion_and_completed_outcome_are_consistent(self) -> None:
        policy = _policy()
        result = _result(policy)
        result["observations"][0]["value"] = 9
        result["stop_state"] = "warning"
        self.assertTrue(_validate_result(result, policy)["valid"])

        result["observations"][0]["value"] = 10
        result["stop_state"] = "exhausted"
        result["execution_outcome"] = "stop-requested"
        result["cancellation"]["state"] = "requested"
        result["checkpoint"].update(remaining_verification=["FW031-IMPL-01-AC-5"], next_authorized_action="Resume only after an authorized new run.")
        self.assertTrue(_validate_result(result, policy)["valid"])

        result["execution_outcome"] = "completed"
        self.assertIn("fw031.result.exhausted_completion", {d["code"] for d in _validate_result(result, policy)["diagnostics"]})

        result["execution_outcome"] = "stop-requested"
        result["observations"][0]["value"] = 3
        out = _validate_result(result, policy)
        self.assertIn("fw031.result.false_exhaustion", {d["code"] for d in out["diagnostics"]})

    def test_cancellation_claims_require_separate_termination_observation(self) -> None:
        policy = _policy()
        result = _result(policy)
        result["cancellation"]["state"] = "confirmed"
        result["execution_outcome"] = "terminated"
        out = _validate_result(result, policy)
        self.assertIn("fw031.result.termination_unobserved", {d["code"] for d in out["diagnostics"]})

        result["cancellation"]["termination_observation_ref"] = "synthetic://termination-observation/1"
        self.assertTrue(_validate_result(result, policy)["valid"])
        result["cancellation"].update(state="failed", termination_observation_ref=None)
        result["execution_outcome"] = "unknown"
        self.assertTrue(_validate_result(result, policy)["valid"])

    def test_checkpoint_claims_require_evidence_and_exhaustion_keeps_follow_up(self) -> None:
        policy = _policy()
        result = _result(policy)
        result["checkpoint"]["preservation_state"] = "preserved"
        self.assertIn("fw031.result.checkpoint_unsubstantiated", {d["code"] for d in _validate_result(result, policy)["diagnostics"]})
        result["checkpoint"].update(
            last_durable_checkpoint_ref="synthetic://checkpoint/1",
            preservation_evidence_ref="synthetic://preservation/1",
        )
        self.assertTrue(_validate_result(result, policy)["valid"])

        result["observations"][0]["value"] = 11
        result["stop_state"] = "exhausted"
        result["execution_outcome"] = "interrupted"
        result["cancellation"]["state"] = "unknown"
        result["checkpoint"]["next_authorized_action"] = " "
        self.assertIn("fw031.result.next_action_missing", {d["code"] for d in _validate_result(result, policy)["diagnostics"]})

    def test_spend_provenance_must_match_policy_and_unknown_cannot_contain_estimates(self) -> None:
        policy = _policy()
        policy["limits"][4].update(
            requested=True,
            measurement_source={"kind": "provider-meter", "id": "fixture-meter"},
            capability="advisory",
            warning_threshold=5,
            exhaustion_threshold=10,
            unavailable_behavior="continue-advisory",
        )
        policy = contract.seal_policy(policy)
        result = _result(policy)
        result["spend"].update(
            state="reported",
            amount="1.25",
            currency="USD",
            meter_kind="provider-meter",
            meter_id="fixture-meter",
            source_run_id=ROOT_RUN,
            window={"start": "2026-10-26T10:00:00Z", "end": "2026-10-26T10:01:00Z"},
            provenance_ref="synthetic://meter-record/1",
            unknown_reason=None,
        )
        self.assertTrue(_validate_result(result, policy)["valid"])

        result["spend"]["amount"] = "5.00"
        result["stop_state"] = "warning"
        self.assertTrue(_validate_result(result, policy)["valid"])
        result["spend"]["amount"] = "10.00"
        result["stop_state"] = "exhausted"
        result["execution_outcome"] = "stop-requested"
        result["cancellation"]["state"] = "requested"
        self.assertTrue(_validate_result(result, policy)["valid"])
        result["spend"]["amount"] = "1.00"
        self.assertIn("fw031.result.false_exhaustion", {d["code"] for d in _validate_result(result, policy)["diagnostics"]})

        result = _result(policy)
        result["spend"].update(
            state="reported", amount="1.00", currency="USD", meter_kind="provider-meter",
            meter_id="fixture-meter", source_run_id=ROOT_RUN,
            window={"start": "2026-10-26T10:00:00Z", "end": "2026-10-26T10:01:00Z"},
            provenance_ref="synthetic://meter-record/1", unknown_reason=None,
        )
        result["spend"]["provenance_ref"] = None
        self.assertIn("fw031.result.reported_spend_incomplete", {d["code"] for d in _validate_result(result, policy)["diagnostics"]})

        result["spend"]["meter_id"] = "other-meter"
        self.assertIn("fw031.result.spend_binding", {d["code"] for d in _validate_result(result, policy)["diagnostics"]})

        result = _result(policy)
        result["spend"]["amount"] = "0.25"
        self.assertIn("fw031.result.unknown_spend_value", {d["code"] for d in _validate_result(result, policy)["diagnostics"]})

        result = _result(policy)
        result["spend"].update(
            state="reported", amount="1.00", currency="USD", meter_kind="provider-meter",
            meter_id="fixture-meter", source_run_id=PREVIOUS_RUN,
            window={"start": "2026-10-26T10:00:00Z", "end": "2026-10-26T10:01:00Z"},
            provenance_ref="synthetic://meter-record/1", unknown_reason=None,
        )
        self.assertIn("fw031.result.spend_run", {d["code"] for d in _validate_result(result, policy)["diagnostics"]})

    def test_overrides_bypass_and_in_place_reset_are_rejected(self) -> None:
        policy = _policy()
        result = _result(policy)
        result["override_authorization"] = {"actor": "owner", "reason": "synthetic"}
        self.assertFalse(_validate_result(result, policy)["valid"])

        result = _result(policy)
        result["gate_result"] = "PASS"
        self.assertFalse(_validate_result(result, policy)["valid"])

        result = _result(policy)
        result["reset_events"] = [{"kind": "manual", "previous_run_id": PREVIOUS_RUN, "new_run_id": ROOT_RUN}]
        self.assertFalse(_validate_result(result, policy)["valid"])

        result["reset_events"] = [{"kind": "new-run", "previous_run_id": ROOT_RUN, "new_run_id": ROOT_RUN}]
        self.assertIn("fw031.result.in_place_reset", {d["code"] for d in _validate_result(result, policy)["diagnostics"]})

        result["reset_events"] = [{"kind": "new-run", "previous_run_id": PREVIOUS_RUN, "new_run_id": ROOT_RUN}]
        self.assertTrue(_validate_result(result, policy)["valid"])

    def test_policy_sealing_and_cli_are_read_only_and_truthful(self) -> None:
        original = _policy()
        before = copy.deepcopy(original)
        self.assertEqual(contract.seal_policy(original), original)
        self.assertEqual(original, before)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            path.write_text(json.dumps(original), encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(contract.main(["policy", str(path)]), 0)
            output = json.loads(stdout.getvalue())
            self.assertTrue(output["valid"])
            self.assertEqual(output["validation_scope"], "structure-and-declared-invariants-only")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), original)


if __name__ == "__main__":
    unittest.main()
