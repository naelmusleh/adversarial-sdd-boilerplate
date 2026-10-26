"""FW-031 v1 budget-contract validation; no execution or gate transition occurs."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping


_SCHEMA_DIR = Path(__file__).resolve().parents[1] / "docs/framework/schemas/fw031"
_SCHEMAS = {
    "policy": _SCHEMA_DIR / "budget-policy-v1.schema.json",
    "result": _SCHEMA_DIR / "budget-result-v1.schema.json",
}
_MAX_INPUT_BYTES = 512 * 1024
_MAX_DIAGNOSTICS = 32
_SCHEMA_KEYWORDS = {
    "$id", "$schema", "additionalProperties", "const", "enum", "items", "maxItems",
    "maxLength", "maximum", "minItems", "minLength", "minimum", "pattern",
    "properties", "required", "title", "type", "uniqueItems",
}
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
_HEX_REVISION_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


class _DuplicateKey(ValueError):
    pass


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey
        result[key] = value
    return result


def _reject_constant(_: str) -> None:
    raise ValueError


def _parse_finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or Decimal(str(number)) != Decimal(value):
        raise ValueError
    return number


def _diag(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _parse(raw: bytes | str, kind: str) -> tuple[Any | None, list[dict[str, str]]]:
    label = f"fw031.{kind}"
    if isinstance(raw, str):
        try:
            data = raw.encode("utf-8", errors="strict")
        except UnicodeError:
            return None, [_diag(f"{label}.invalid_json", "$", "input is not valid UTF-8")]
    elif isinstance(raw, bytes):
        data = raw
    else:
        return None, [_diag(f"{label}.invalid_json", "$", "input must be UTF-8 JSON bytes or text")]
    if len(data) > _MAX_INPUT_BYTES:
        return None, [_diag(f"{label}.size_limit", "$", "input exceeds the contract size limit")]
    try:
        value = json.loads(
            data.decode("utf-8", errors="strict"),
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=_reject_constant,
            parse_float=_parse_finite_float,
        )
    except (UnicodeError, json.JSONDecodeError, InvalidOperation, ValueError, RecursionError):
        return None, [_diag(f"{label}.invalid_json", "$", "input is not valid strict JSON")]
    return value, []


def _schema(kind: str) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    try:
        value = json.loads(_SCHEMAS[kind].read_text(encoding="utf-8"), object_pairs_hook=_pairs_no_duplicates)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return None, [_diag("fw031.schema.unavailable", "$", f"the {kind} schema is unavailable or invalid")]
    if not isinstance(value, dict):
        return None, [_diag("fw031.schema.unavailable", "$", f"the {kind} schema root is invalid")]
    return value, []


def _is_type(value: Any, expected: str) -> bool:
    return {
        "object": lambda: isinstance(value, dict),
        "array": lambda: isinstance(value, list),
        "string": lambda: isinstance(value, str),
        "integer": lambda: isinstance(value, int) and not isinstance(value, bool),
        "number": lambda: isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": lambda: isinstance(value, bool),
        "null": lambda: value is None,
    }.get(expected, lambda: False)()


def _validate_schema(value: Any, spec: Mapping[str, Any], path: str = "$") -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if set(spec) - _SCHEMA_KEYWORDS:
        return [_diag("fw031.schema.unsupported_keyword", path, "schema uses an unsupported validation keyword")]

    expected = spec.get("type")
    expected_types = expected if isinstance(expected, list) else [expected] if expected is not None else []
    if expected_types and not any(isinstance(kind, str) and _is_type(value, kind) for kind in expected_types):
        return [_diag("fw031.schema.invalid", path, "value has the wrong JSON type")]
    if "const" in spec and value != spec["const"]:
        issues.append(_diag("fw031.schema.invalid", path, "value does not match the required constant"))
    if "enum" in spec and value not in spec["enum"]:
        issues.append(_diag("fw031.schema.invalid", path, "value is outside the allowed set"))

    if isinstance(value, dict):
        properties = spec.get("properties", {})
        if not isinstance(properties, dict):
            return issues + [_diag("fw031.schema.invalid", path, "schema properties definition is invalid")]
        for key in spec.get("required", []):
            if key not in value:
                issues.append(_diag("fw031.schema.invalid", f"{path}.{key}", "required property is missing"))
        if spec.get("additionalProperties") is False and set(value) - set(properties):
            issues.append(_diag("fw031.schema.invalid", path, "additional property is not allowed"))
        for key, child_spec in properties.items():
            if key in value:
                if not isinstance(child_spec, dict):
                    issues.append(_diag("fw031.schema.invalid", f"{path}.{key}", "property schema is invalid"))
                else:
                    issues.extend(_validate_schema(value[key], child_spec, f"{path}.{key}"))
                    if len(issues) >= _MAX_DIAGNOSTICS:
                        return issues[:_MAX_DIAGNOSTICS]

    if isinstance(value, list):
        if len(value) < spec.get("minItems", 0) or len(value) > spec.get("maxItems", _MAX_INPUT_BYTES):
            issues.append(_diag("fw031.schema.invalid", path, "array length is outside the allowed range"))
        if spec.get("uniqueItems"):
            try:
                serialized = [json.dumps(item, sort_keys=True, separators=(",", ":"), allow_nan=False) for item in value]
                if len(serialized) != len(set(serialized)):
                    issues.append(_diag("fw031.schema.invalid", path, "array entries must be unique"))
            except (TypeError, ValueError):
                issues.append(_diag("fw031.schema.invalid", path, "array entries cannot be compared"))
        child_spec = spec.get("items")
        if child_spec is not None:
            if not isinstance(child_spec, dict):
                issues.append(_diag("fw031.schema.invalid", path, "array item schema is invalid"))
            else:
                for index, child in enumerate(value):
                    issues.extend(_validate_schema(child, child_spec, f"{path}[{index}]"))
                    if len(issues) >= _MAX_DIAGNOSTICS:
                        return issues[:_MAX_DIAGNOSTICS]

    if isinstance(value, str):
        if len(value) < spec.get("minLength", 0) or len(value) > spec.get("maxLength", _MAX_INPUT_BYTES):
            issues.append(_diag("fw031.schema.invalid", path, "string length is outside the allowed range"))
        pattern = spec.get("pattern")
        if pattern is not None:
            try:
                if re.fullmatch(pattern, value) is None:
                    issues.append(_diag("fw031.schema.invalid", path, "string does not match the required format"))
            except (TypeError, re.error):
                issues.append(_diag("fw031.schema.invalid", path, "schema pattern is invalid"))

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            numeric = Decimal(str(value))
            if "minimum" in spec and numeric < Decimal(str(spec["minimum"])):
                issues.append(_diag("fw031.schema.invalid", path, "number is below the allowed minimum"))
            if "maximum" in spec and numeric > Decimal(str(spec["maximum"])):
                issues.append(_diag("fw031.schema.invalid", path, "number is above the allowed maximum"))
        except InvalidOperation:
            issues.append(_diag("fw031.schema.invalid", path, "number is invalid"))
    return issues[:_MAX_DIAGNOSTICS]


def _canonical_policy_digest(policy: Mapping[str, Any]) -> str:
    payload = dict(policy)
    payload.pop("policy_digest", None)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def seal_policy(policy: Mapping[str, Any]) -> dict[str, Any]:
    """Return a copied policy with its canonical self-excluding SHA-256 digest."""
    if not isinstance(policy, Mapping):
        raise TypeError("policy must be a mapping")
    result = dict(policy)
    result.pop("policy_digest", None)
    result["policy_digest"] = _canonical_policy_digest(result)
    return result


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def _policy_semantics(policy: Mapping[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    try:
        if policy["policy_digest"] != _canonical_policy_digest(policy):
            issues.append(_diag("fw031.policy.digest_mismatch", "$.policy_digest", "policy digest does not match canonical policy content"))
        ids: set[str] = set()
        for index, limit in enumerate(policy["limits"]):
            path = f"$.limits[{index}]"
            if limit["id"] in ids:
                issues.append(_diag("fw031.policy.duplicate_limit", f"{path}.id", "limit identifiers must be unique"))
            ids.add(limit["id"])
            warning, exhaustion = limit["warning_threshold"], limit["exhaustion_threshold"]
            if warning is not None and exhaustion is not None and Decimal(str(warning)) >= Decimal(str(exhaustion)):
                issues.append(_diag("fw031.policy.threshold_order", path, "warning threshold must be below exhaustion threshold"))
            if not limit["requested"] and (warning is not None or exhaustion is not None):
                issues.append(_diag("fw031.policy.disabled_threshold", path, "an unrequested limit cannot carry active thresholds"))
            if limit["requested"] and warning is None and exhaustion is None:
                issues.append(_diag("fw031.policy.missing_threshold", path, "a requested limit needs an explicit threshold"))
            if limit["scope"] == "run-tree" and policy["nested_run_accounting"] != "aggregate-at-root":
                issues.append(_diag("fw031.policy.scope_accounting", path, "run-tree limits require aggregate-at-root accounting"))
            capability = limit["capability"]
            source_kind = limit["measurement_source"]["kind"]
            if capability == "unavailable" and limit["requested"] and limit["unavailable_behavior"] not in {"block-run", "disable-limit"}:
                issues.append(_diag("fw031.policy.unavailable_fallback", path, "unavailable measurements must block or disable the limit"))
            if capability == "enforced" and source_kind in {"unselected", "synthetic-fixture"}:
                issues.append(_diag("fw031.policy.unproven_enforcement", path, "unselected or synthetic sources cannot be declared enforced"))
            if capability == "enforced" and limit["unavailable_behavior"] != "block-run":
                issues.append(_diag("fw031.policy.enforced_fallback", path, "enforced limits must block when their measurement is unavailable"))
            if limit["kind"] == "spend":
                if limit["scope"] != "run":
                    issues.append(_diag("fw031.policy.spend_scope", path, "spend results are bound to one source run"))
                if not re.fullmatch(r"[A-Z]{3}", limit["unit"]):
                    issues.append(_diag("fw031.policy.spend_currency", f"{path}.unit", "spend units must be an uppercase currency code"))
                if limit["requested"] and source_kind not in {"host-meter", "provider-meter"}:
                    issues.append(_diag("fw031.policy.spend_source", path, "requested spend limits require an identified host or provider meter"))
                if limit["requested"] and capability == "enforced" and limit["unavailable_behavior"] != "block-run":
                    issues.append(_diag("fw031.policy.spend_unavailable", path, "spend-meter loss must block an enforced spend limit"))
    except (KeyError, TypeError, InvalidOperation):
        issues.append(_diag("fw031.policy.invalid", "$", "policy cross-field validation could not be completed"))
    return issues[:_MAX_DIAGNOSTICS]


def _validate_document(raw: bytes | str, kind: str) -> tuple[Any | None, list[dict[str, str]]]:
    value, issues = _parse(raw, kind)
    if issues:
        return None, issues
    schema, schema_errors = _schema(kind)
    if schema_errors:
        return None, schema_errors
    assert schema is not None
    issues = _validate_schema(value, schema)
    if not issues and not isinstance(value, dict):
        issues = [_diag(f"fw031.{kind}.invalid", "$", "document must be a JSON object")]
    return value, issues


def _result(valid: bool, kind: str, issues: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "contract": "FRAMEWORK-CONTRACT-031",
        "schema_version": "1.0",
        "document_kind": kind,
        "validation_scope": "structure-and-declared-invariants-only",
        "valid": valid,
        "diagnostics": issues[:_MAX_DIAGNOSTICS],
    }


def validate_budget_policy(raw: bytes | str) -> dict[str, Any]:
    """Validate policy structure and declared invariants without authorizing execution."""
    policy, issues = _validate_document(raw, "policy")
    if issues:
        return _result(False, "policy", issues)
    issues = _policy_semantics(policy)
    return _result(not issues, "policy", issues)


def _run_tree_issues(result: Mapping[str, Any], policy: Mapping[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    run_ids = [run["run_id"] for run in result["runs"]]
    if len(run_ids) != len(set(run_ids)):
        issues.append(_diag("fw031.result.duplicate_run", "$.runs", "run identifiers must be unique"))
    if result["run_id"] not in run_ids:
        issues.append(_diag("fw031.result.root_missing", "$.runs", "root run must be declared"))
        return issues
    parents = {run["run_id"]: run["parent_run_id"] for run in result["runs"]}
    if parents[result["run_id"]] is not None:
        issues.append(_diag("fw031.result.root_parent", "$.runs", "root run cannot have a parent"))
    for run_id, parent_id in parents.items():
        if run_id != result["run_id"] and (parent_id is None or parent_id not in parents):
            issues.append(_diag("fw031.result.parent_missing", "$.runs", "each child run must reference a declared parent"))
        seen: set[str] = set()
        current: str | None = run_id
        while current is not None and current in parents:
            if current in seen:
                issues.append(_diag("fw031.result.run_cycle", "$.runs", "run lineage cannot contain a cycle"))
                break
            seen.add(current)
            current = parents[current]
    if result["accounting_mode"] != policy["nested_run_accounting"]:
        issues.append(_diag("fw031.result.accounting_mismatch", "$.accounting_mode", "result accounting mode must match policy"))
    if policy["run_scope"] == "single-run" and (len(run_ids) != 1 or result["accounting_mode"] == "aggregate-at-root"):
        issues.append(_diag("fw031.result.scope_mismatch", "$.runs", "single-run policy cannot contain nested or aggregated runs"))
    if result["accounting_mode"] == "unavailable" and len(run_ids) != 1:
        issues.append(_diag("fw031.result.accounting_unavailable", "$.runs", "unavailable nested accounting cannot claim child runs"))
    return issues


def _result_semantics(result: Mapping[str, Any], policy: Mapping[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    try:
        for key in ("policy_id", "policy_revision", "policy_digest", "source_revision"):
            if result[key] != policy[key]:
                issues.append(_diag("fw031.result.policy_binding", f"$.{key}", "result does not match the bound policy/source revision"))

        started, ended = _timestamp(result["started_at"]), _timestamp(result["ended_at"])
        if started is None or ended is None or ended < started:
            issues.append(_diag("fw031.result.time_order", "$.started_at", "run timestamps must be timezone-aware and ordered"))

        issues.extend(_run_tree_issues(result, policy))
        runs = {run["run_id"] for run in result["runs"]}
        policy_limits = {limit["id"]: limit for limit in policy["limits"]}
        observation_ids: set[str] = set()
        ownership_keys: set[tuple[str, str, int]] = set()
        latest: dict[tuple[str, str], tuple[int, Decimal]] = {}
        for index, observation in enumerate(result["observations"]):
            path = f"$.observations[{index}]"
            observation_id = observation["observation_id"]
            if observation_id in observation_ids:
                issues.append(_diag("fw031.result.duplicate_observation", f"{path}.observation_id", "observation identifiers must be unique"))
            observation_ids.add(observation_id)
            limit = policy_limits.get(observation["limit_id"])
            if limit is None:
                issues.append(_diag("fw031.result.unknown_limit", f"{path}.limit_id", "observation references an undeclared limit"))
                continue
            owner = observation["accounting_owner_run_id"]
            if owner not in runs:
                issues.append(_diag("fw031.result.unknown_accounting_owner", f"{path}.accounting_owner_run_id", "observation owner must be in the declared run tree"))
            if result["accounting_mode"] == "aggregate-at-root" and owner != result["run_id"]:
                issues.append(_diag("fw031.result.aggregate_owner", f"{path}.accounting_owner_run_id", "aggregate observations must belong to the root run"))
            key = (owner, observation["limit_id"], observation["sequence"])
            if key in ownership_keys:
                issues.append(_diag("fw031.result.double_accounting", path, "one limit sequence cannot be counted twice for an accounting owner"))
            ownership_keys.add(key)
            if observation["unit"] != limit["unit"] or observation["source_id"] != limit["measurement_source"]["id"]:
                issues.append(_diag("fw031.result.observation_binding", path, "observation unit or source does not match policy"))
            state = observation["state"]
            if state == "observed":
                if observation["value"] is None or observation["unavailable_reason"] is not None:
                    issues.append(_diag("fw031.result.observation_state", path, "observed values require a value and no unavailable reason"))
                elif limit["capability"] == "unavailable" or not limit["requested"]:
                    issues.append(_diag("fw031.result.unavailable_observed", path, "unavailable or unrequested limits cannot carry observed values"))
                else:
                    latest_key = (owner, limit["id"])
                    value = Decimal(str(observation["value"]))
                    previous = latest.get(latest_key)
                    if previous is None or observation["sequence"] > previous[0]:
                        latest[latest_key] = (observation["sequence"], value)
            elif observation["value"] is not None or observation["unavailable_reason"] is None:
                issues.append(_diag("fw031.result.observation_state", path, "unavailable values require a reason and no numeric value"))

        warning_reached = False
        exhaustion_reached = False
        for (owner, limit_id), (_, value) in latest.items():
            del owner
            limit = policy_limits[limit_id]
            warning = limit["warning_threshold"]
            exhaustion = limit["exhaustion_threshold"]
            warning_reached |= warning is not None and value >= Decimal(str(warning))
            exhaustion_reached |= exhaustion is not None and value >= Decimal(str(exhaustion))
        spend = result["spend"]
        if spend["state"] == "reported":
            spend_limit = next(
                (
                    limit for limit in policy["limits"]
                    if limit["kind"] == "spend"
                    and limit["requested"]
                    and limit["unit"] == spend["currency"]
                    and limit["measurement_source"]["kind"] == spend["meter_kind"]
                    and limit["measurement_source"]["id"] == spend["meter_id"]
                ),
                None,
            )
            if spend_limit is not None:
                amount = Decimal(spend["amount"])
                warning = spend_limit["warning_threshold"]
                exhaustion = spend_limit["exhaustion_threshold"]
                warning_reached |= warning is not None and amount >= Decimal(str(warning))
                exhaustion_reached |= exhaustion is not None and amount >= Decimal(str(exhaustion))
        missing_or_unavailable: list[tuple[Mapping[str, Any], str]] = []
        for limit in policy["limits"]:
            if not limit["requested"]:
                continue
            if limit["kind"] == "spend":
                if spend["state"] == "unknown":
                    missing_or_unavailable.append((limit, result["run_id"]))
                continue
            owners = [result["run_id"]] if limit["scope"] == "run-tree" else list(runs)
            for owner in owners:
                samples = [
                    observation for observation in result["observations"]
                    if observation["limit_id"] == limit["id"]
                    and observation["accounting_owner_run_id"] == owner
                ]
                latest_sample = max(samples, key=lambda observation: observation["sequence"], default=None)
                if latest_sample is None or latest_sample["state"] == "unavailable":
                    missing_or_unavailable.append((limit, owner))
        blocking_measurement = any(limit["capability"] == "enforced" for limit, _ in missing_or_unavailable)
        uncertain_measurement = bool(missing_or_unavailable)
        state = result["stop_state"]
        if blocking_measurement and not exhaustion_reached:
            if state != "blocked" or result["execution_outcome"] != "blocked":
                issues.append(_diag("fw031.result.enforced_measurement_missing", "$.stop_state", "missing enforced measurements must block the run outcome"))
        elif state == "blocked":
            issues.append(_diag("fw031.result.false_blocked", "$.stop_state", "blocked state requires a missing or unavailable enforced measurement"))
        if result["execution_outcome"] == "blocked" and state != "blocked":
            issues.append(_diag("fw031.result.false_blocked_outcome", "$.execution_outcome", "blocked outcome requires blocked stop state"))
        if uncertain_measurement and not blocking_measurement and not warning_reached and not exhaustion_reached and state != "unknown":
            issues.append(_diag("fw031.result.measurement_unknown_state", "$.stop_state", "missing or unavailable measurements must remain unknown"))
        if state == "unknown" and (not uncertain_measurement or blocking_measurement or warning_reached or exhaustion_reached):
            issues.append(_diag("fw031.result.false_unknown", "$.stop_state", "unknown state requires unresolved measurements without a stronger stop condition"))
        if state == "clear" and (uncertain_measurement or blocking_measurement):
            issues.append(_diag("fw031.result.false_clear", "$.stop_state", "clear state cannot hide missing or unavailable measurements"))
        if exhaustion_reached and state != "exhausted":
            issues.append(_diag("fw031.result.exhaustion_missing", "$.stop_state", "an exceeded exhaustion threshold must be recorded"))
        if warning_reached and state == "clear":
            issues.append(_diag("fw031.result.warning_missing", "$.stop_state", "a reached warning threshold cannot be recorded as clear"))
        if state == "exhausted" and not exhaustion_reached:
            issues.append(_diag("fw031.result.false_exhaustion", "$.stop_state", "exhaustion requires an observed threshold breach"))
        if state == "exhausted" and result["execution_outcome"] == "completed":
            issues.append(_diag("fw031.result.exhausted_completion", "$.execution_outcome", "an exhausted run cannot claim completed execution"))

        cancellation = result["cancellation"]
        if cancellation["state"] == "confirmed" and cancellation["termination_observation_ref"] is None:
            issues.append(_diag("fw031.result.termination_unobserved", "$.cancellation", "confirmed cancellation requires an observation reference"))
        if (cancellation["state"] == "confirmed") != (result["execution_outcome"] == "terminated"):
            issues.append(_diag("fw031.result.termination_state_mismatch", "$.execution_outcome", "termination outcome and cancellation state must agree"))
        if cancellation["state"] != "confirmed" and cancellation["termination_observation_ref"] is not None:
            issues.append(_diag("fw031.result.termination_reference_mismatch", "$.cancellation", "termination reference requires confirmed status"))
        if cancellation["state"] == "requested" and result["execution_outcome"] == "completed":
            issues.append(_diag("fw031.result.pending_cancellation_completion", "$.execution_outcome", "pending cancellation cannot be reported as completed"))

        checkpoint = result["checkpoint"]
        if checkpoint["preservation_state"] == "preserved" and (
            checkpoint["last_durable_checkpoint_ref"] is None or checkpoint["preservation_evidence_ref"] is None
        ):
            issues.append(_diag("fw031.result.checkpoint_unsubstantiated", "$.checkpoint", "preserved work requires checkpoint and evidence references"))
        if state == "exhausted" and not checkpoint["next_authorized_action"].strip():
            issues.append(_diag("fw031.result.next_action_missing", "$.checkpoint.next_authorized_action", "exhausted runs require a next authorized action"))

        spend_fields = ("amount", "currency", "meter_kind", "meter_id", "source_run_id", "window", "provenance_ref")
        if spend["state"] == "unknown":
            if any(spend[field] is not None for field in spend_fields) or spend["unknown_reason"] is None:
                issues.append(_diag("fw031.result.unknown_spend_value", "$.spend", "unknown spend must not include amount or meter provenance"))
        else:
            if any(spend[field] is None for field in spend_fields):
                issues.append(_diag("fw031.result.reported_spend_incomplete", "$.spend", "reported spend requires complete amount and meter provenance"))
            if spend["unknown_reason"] is not None:
                issues.append(_diag("fw031.result.reported_spend_reason", "$.spend.unknown_reason", "reported spend cannot carry an unknown reason"))
            spend_limits = [limit for limit in policy["limits"] if limit["kind"] == "spend" and limit["requested"]]
            matching = [
                limit for limit in spend_limits
                if limit["unit"] == spend["currency"]
                and limit["measurement_source"]["id"] == spend["meter_id"]
                and limit["measurement_source"]["kind"] == spend["meter_kind"]
            ]
            if not matching:
                issues.append(_diag("fw031.result.spend_binding", "$.spend", "reported spend must match a requested meter limit"))
            if spend["source_run_id"] not in runs:
                issues.append(_diag("fw031.result.spend_run", "$.spend.source_run_id", "spend must identify a declared run"))
            window = spend["window"]
            if window is not None:
                window_start, window_end = _timestamp(window["start"]), _timestamp(window["end"])
                if window_start is None or window_end is None or window_end <= window_start:
                    issues.append(_diag("fw031.result.spend_window", "$.spend.window", "spend window must be timezone-aware and ordered"))
        for index, event in enumerate(result["reset_events"]):
            if event["previous_run_id"] == event["new_run_id"] or event["new_run_id"] != result["run_id"]:
                issues.append(_diag("fw031.result.in_place_reset", f"$.reset_events[{index}]", "reset must begin a distinct new root run"))
    except (KeyError, TypeError, InvalidOperation, OverflowError):
        issues.append(_diag("fw031.result.invalid", "$", "result cross-field validation could not be completed"))
    return issues[:_MAX_DIAGNOSTICS]


def validate_budget_result(raw: bytes | str, policy_raw: bytes | str) -> dict[str, Any]:
    """Validate a result against its exact policy; this does not verify its evidence."""
    policy, policy_issues = _validate_document(policy_raw, "policy")
    if not policy_issues:
        policy_issues = _policy_semantics(policy)
    if policy_issues:
        return _result(False, "result", [_diag("fw031.result.policy_invalid", "$", "bound policy is invalid")])
    result, issues = _validate_document(raw, "result")
    if issues:
        return _result(False, "result", issues)
    issues = _result_semantics(result, policy)
    return _result(not issues, "result", issues)


def _read(path: str) -> bytes:
    try:
        with Path(path).open("rb") as source:
            return source.read(_MAX_INPUT_BYTES + 1)
    except OSError:
        return b""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate FW-031 budget contract records (structural only).")
    subparsers = parser.add_subparsers(dest="kind", required=True)
    policy_parser = subparsers.add_parser("policy", help="validate a budget policy")
    policy_parser.add_argument("path")
    result_parser = subparsers.add_parser("result", help="validate a result against its policy")
    result_parser.add_argument("path")
    result_parser.add_argument("--policy", required=True, dest="policy_path")
    args = parser.parse_args(argv)
    outcome = (
        validate_budget_policy(_read(args.path))
        if args.kind == "policy"
        else validate_budget_result(_read(args.path), _read(args.policy_path))
    )
    print(json.dumps(outcome, sort_keys=True, separators=(",", ":")))
    return 0 if outcome["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
