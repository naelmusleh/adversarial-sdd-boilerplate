"""Validate FW-031 GitHub Actions evidence records; never collect or authorize evidence."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

try:  # Support both `python -m scripts...` and direct script execution.
    from scripts.fw031_budget_contract import _MAX_DIAGNOSTICS, _diag, _parse, _validate_schema
except ModuleNotFoundError:
    from fw031_budget_contract import _MAX_DIAGNOSTICS, _diag, _parse, _validate_schema

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs/framework/schemas/fw031/actions-run-job-evidence-v1.schema.json"
)
_MAX_INPUT_BYTES = 512 * 1024
_ALLOWED_LIMITATIONS = {
    "identity-incomplete", "source-partial", "source-denied", "source-unavailable",
    "revision-unknown", "timing-unknown", "timeout-unknown", "cancellation-unknown",
    "workload-termination-unobserved", "metrics-unknown", "metrics-unavailable",
}


def _issue(code: str, path: str, message: str) -> dict[str, str]:
    return _diag(f"fw031.actions_evidence.{code}", path, message)


def _schema() -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    try:
        value = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None, [_issue("schema_unavailable", "$", "the evidence schema is unavailable or invalid")]
    if not isinstance(value, dict):
        return None, [_issue("schema_unavailable", "$", "the evidence schema root must be an object")]
    return value, []


def _expand_schema_refs(schema: Mapping[str, Any]) -> dict[str, Any]:
    """Expand the local JSON Pointer refs into the subset supported by FW-031-01."""
    def expand(node: Any) -> Any:
        if isinstance(node, dict):
            ref = node.get("$ref")
            if ref is not None:
                if not isinstance(ref, str) or not ref.startswith("#/definitions/"):
                    raise ValueError("unsupported schema reference")
                target: Any = schema
                for part in ref[2:].split("/"):
                    target = target[part]
                if not isinstance(target, dict):
                    raise ValueError("invalid schema reference")
                return expand(target)
            return {key: expand(value) for key, value in node.items() if key != "definitions"}
        if isinstance(node, list):
            return [expand(value) for value in node]
        return node

    expanded = expand(schema)
    if not isinstance(expanded, dict):
        raise ValueError("schema root is invalid")
    return expanded


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def _identity_tuple(identity: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    return identity.get("run_id"), identity.get("run_attempt"), identity.get("job_id")


def _semantics(record: Mapping[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    source, identity = record["source"], record["identity"]
    state = identity["state"]
    required = (identity["run_id"], identity["run_attempt"], identity["job_id"], identity["job_name"])
    present = sum(item is not None for item in required)
    if state == "available" and present != 4:
        issues.append(_issue("identity_state", "$.identity", "available identity requires the full run/attempt/job tuple"))
    elif state == "partial" and not 0 < present < 4:
        issues.append(_issue("identity_state", "$.identity", "partial identity requires some but not all tuple fields"))
    elif state in {"unknown", "unavailable"} and present != 0:
        issues.append(_issue("identity_state", "$.identity", "unknown or unavailable identity cannot carry tuple values"))
    acquisition = source["acquisition_state"]
    source_identity = (source["repository_id"], source["repository_name"], source["workflow_id"], source["workflow_path"], source["workflow_ref"])
    if acquisition == "complete" and any(item is None for item in source_identity):
        issues.append(_issue("source_identity", "$.source", "complete acquisition requires repository and workflow identity"))
    if _timestamp(source["observed_at"]) is None:
        issues.append(_issue("source_timestamp", "$.source.observed_at", "source observation time must be offset-aware"))
    if acquisition == "complete" and state != "available":
        issues.append(_issue("source_identity", "$.source.acquisition_state", "complete acquisition requires a complete identity"))
    if acquisition in {"denied", "unavailable"} and state not in {"unknown", "unavailable"}:
        issues.append(_issue("source_identity", "$.identity.state", "denied or unavailable acquisition cannot claim partial identity"))

    identity_tuple = _identity_tuple(identity)
    for section_name in ("run", "job"):
        interval = record["timing"][section_name]
        actual = (interval["run_id"], interval["run_attempt"], interval["job_id"])
        if state == "available" and (actual[:2] != identity_tuple[:2] or (section_name == "job" and actual[2] != identity_tuple[2])):
            issues.append(_issue("identity_mismatch", f"$.timing.{section_name}", "timing must bind to the record run/attempt/job"))
        if section_name == "run" and actual[2] is not None and state == "available" and actual[2] != identity_tuple[2]:
            issues.append(_issue("identity_mismatch", f"$.timing.{section_name}.job_id", "populated timing job ID must match the record identity"))
        points = (interval["started_at"], interval["completed_at"])
        for offset, point in enumerate(points):
            value = point["value"]
            if point["state"] == "available":
                if value is None or point["source"] is None or _timestamp(value) is None:
                    issues.append(_issue("timestamp_provenance", f"$.timing.{section_name}", "available timestamp requires an offset-aware value and source"))
            elif value is not None or point["source"] is not None:
                issues.append(_issue("timestamp_state", f"$.timing.{section_name}", "unknown/unavailable timestamp cannot carry a value or source"))
            if state != "available" and point["state"] == "available":
                issues.append(_issue("identity_incomplete", f"$.timing.{section_name}", "timing cannot be populated without complete identity"))
        start, end = (_timestamp(point["value"]) for point in points)
        if start is not None and end is not None and end < start:
            issues.append(_issue("time_order", f"$.timing.{section_name}", "completion must not precede start"))

    for name, revision in record["revisions"].items():
        if revision["state"] == "available":
            if revision["value"] is None or revision["source"] is None:
                issues.append(_issue("revision_provenance", f"$.revisions.{name}", "available revision requires its own SHA and source"))
        elif revision["value"] is not None or revision["source"] is not None:
            issues.append(_issue("revision_state", f"$.revisions.{name}", "unknown/unavailable revision cannot borrow a value or source"))

    timeout = record["timeout"]
    if timeout["configuration_state"] == "configured":
        if timeout["minutes"] is None or timeout["configuration_revision"] is None or timeout["configuration_source"] is None:
            issues.append(_issue("timeout_configuration", "$.timeout", "configured timeout requires value, revision, and source"))
    elif any(timeout[key] is not None for key in ("minutes", "configuration_revision", "configuration_source")):
        issues.append(_issue("timeout_configuration", "$.timeout", "timeout values require configured state"))
    if timeout["observed_state"] in {"timed-out", "not-timed-out"}:
        if timeout["observation_source"] is None:
            issues.append(_issue("timeout_observation", "$.timeout.observation_source", "observed timeout state requires a source"))
        expected_conclusion = "timed_out" if timeout["observed_state"] == "timed-out" else None
        if expected_conclusion and timeout["host_conclusion"] not in {expected_conclusion, "unknown", "unavailable"}:
            issues.append(_issue("timeout_outcome", "$.timeout.host_conclusion", "timed-out observation conflicts with host conclusion"))
        if timeout["observed_state"] == "not-timed-out" and timeout["host_conclusion"] == "timed_out":
            issues.append(_issue("timeout_outcome", "$.timeout.host_conclusion", "not-timed-out observation conflicts with host conclusion"))
        if state != "available":
            issues.append(_issue("identity_incomplete", "$.timeout", "timeout outcome cannot be attributed without complete identity"))
    elif timeout["host_conclusion"] in {"unknown", "unavailable"} and timeout["observation_source"] is not None:
        issues.append(_issue("timeout_observation", "$.timeout.observation_source", "unavailable timeout and host outcome cannot carry an observation source"))
    if timeout["host_conclusion"] not in {"unknown", "unavailable"}:
        if timeout["observation_source"] is None:
            issues.append(_issue("timeout_observation", "$.timeout.observation_source", "observed host conclusion requires a source"))
        if state != "available":
            issues.append(_issue("identity_incomplete", "$.timeout.host_conclusion", "host conclusion cannot be attributed without complete identity"))

    cancellation = record["cancellation"]
    if cancellation["request_state"] == "requested":
        if cancellation["requested_at"] is None or cancellation["request_source"] is None or _timestamp(cancellation["requested_at"]) is None:
            issues.append(_issue("cancellation_request", "$.cancellation", "requested cancellation requires a sourced offset-aware timestamp"))
        if state != "available":
            issues.append(_issue("identity_incomplete", "$.cancellation", "cancellation request cannot be attributed without complete identity"))
    elif cancellation["requested_at"] is not None or cancellation["request_source"] is not None:
        issues.append(_issue("cancellation_request", "$.cancellation", "request timestamp/source requires requested state"))
    if cancellation["host_terminal_state"] in {"cancelled", "completed", "timed_out", "failure"} and cancellation["terminal_source"] is None:
        issues.append(_issue("terminal_source", "$.cancellation.terminal_source", "observed terminal state requires a source"))
    if cancellation["host_terminal_state"] not in {"unknown", "unavailable"} and state != "available":
        issues.append(_issue("identity_incomplete", "$.cancellation.host_terminal_state", "host terminal state cannot be attributed without complete identity"))
    if cancellation["workload_state"] == "confirmed":
        if cancellation["workload_observation"] is None or state != "available":
            issues.append(_issue("workload_confirmation", "$.cancellation", "workload confirmation requires an observation and complete identity"))
    elif cancellation["workload_observation"] is not None:
        issues.append(_issue("workload_confirmation", "$.cancellation.workload_observation", "workload observation reference requires confirmed state"))
    if cancellation["host_terminal_state"] == "cancelled" and cancellation["workload_state"] == "confirmed":
        pass  # Separate fields remain independent; the source is still only a claim.

    names: set[str] = set()
    for index, metric in enumerate(record["measurements"]):
        path = f"$.measurements[{index}]"
        if metric["name"] in names:
            issues.append(_issue("duplicate_measurement", path, "measurement names must be unique"))
        names.add(metric["name"])
        if metric["state"] == "measured":
            if any(metric[key] is None for key in ("value", "unit", "source_kind", "source", "scope", "interval")) or metric["reason"] is not None:
                issues.append(_issue("measurement_provenance", path, "measured values require complete provenance and no unavailable reason"))
            if metric["source_kind"] == "synthetic-fixture" and not record["fixture_only"]:
                issues.append(_issue("synthetic_claim", path, "synthetic measurement requires fixture_only=true"))
            if metric["source_kind"] == "proxy":
                issues.append(_issue("measurement_proxy", path, "proxy values cannot be represented as direct measurements"))
            if metric["name"] == "spend" and metric["source_kind"] not in {"authoritative-meter", "synthetic-fixture"}:
                issues.append(_issue("spend_source", path, "spend requires an authoritative meter or an explicitly synthetic fixture"))
            if state != "available":
                issues.append(_issue("identity_incomplete", path, "measured value cannot be attributed without complete identity"))
            if metric["interval"] is not None:
                a, b = (_timestamp(metric["interval"][key]) for key in ("started_at", "completed_at"))
                if a is None or b is None or b < a:
                    issues.append(_issue("measurement_interval", f"{path}.interval", "measurement interval must be offset-aware and ordered"))
        elif any(metric[key] is not None for key in ("value", "unit", "source_kind", "source", "scope", "interval")) or metric["reason"] is None:
            issues.append(_issue("measurement_state", path, "unknown/unavailable measurement requires a reason and no value or provenance"))
        elif metric["state"] == "unknown" and metric["reason"] in {"access-denied", "source-unavailable"}:
            issues.append(_issue("measurement_state", path, "access or source failures must use unavailable state"))
        elif metric["state"] == "unavailable" and metric["reason"] in {"not-observed", "not-instrumented", "unknown-provenance"}:
            issues.append(_issue("measurement_state", path, "unobserved or uninstrumented values must use unknown state"))

    limitations = record["limitations"]
    if len(limitations) != len(set(limitations)):
        issues.append(_issue("duplicate_limitation", "$.limitations", "limitation codes must be unique"))
    required_limit = {
        "partial": "source-partial", "denied": "source-denied", "unavailable": "source-unavailable"
    }.get(acquisition)
    if required_limit is not None and required_limit not in limitations:
        issues.append(_issue("limitation_missing", "$.limitations", "non-complete acquisition requires its matching limitation"))
    if state != "available" and "identity-incomplete" not in limitations:
        issues.append(_issue("limitation_missing", "$.limitations", "incomplete identity requires an explicit limitation"))
    if any(item["state"] != "available" for item in record["revisions"].values()) and "revision-unknown" not in limitations:
        issues.append(_issue("limitation_missing", "$.limitations", "unknown revisions require an explicit limitation"))
    if any(
        point["state"] != "available"
        for interval in record["timing"].values()
        for point in (interval["started_at"], interval["completed_at"])
    ) and "timing-unknown" not in limitations:
        issues.append(_issue("limitation_missing", "$.limitations", "unknown timing requires an explicit limitation"))
    if timeout["configuration_state"] in {"unknown", "unavailable"} or timeout["observed_state"] in {"unknown", "unavailable"}:
        if "timeout-unknown" not in limitations:
            issues.append(_issue("limitation_missing", "$.limitations", "unknown timeout state requires an explicit limitation"))
    if cancellation["request_state"] in {"unknown", "unavailable"} or cancellation["host_terminal_state"] in {"unknown", "unavailable"} or cancellation["workload_state"] in {"unknown", "unavailable"}:
        if "cancellation-unknown" not in limitations:
            issues.append(_issue("limitation_missing", "$.limitations", "unknown cancellation state requires an explicit limitation"))
    if cancellation["workload_state"] in {"unknown", "unavailable", "not-observed"} and "workload-termination-unobserved" not in limitations:
        issues.append(_issue("limitation_missing", "$.limitations", "unconfirmed workload termination requires an explicit limitation"))
    if any(item["state"] == "unknown" for item in record["measurements"]) and "metrics-unknown" not in limitations:
        issues.append(_issue("limitation_missing", "$.limitations", "unknown measurements require an explicit limitation"))
    if any(item["state"] == "unavailable" for item in record["measurements"]) and "metrics-unavailable" not in limitations:
        issues.append(_issue("limitation_missing", "$.limitations", "unavailable measurements require an explicit limitation"))
    return issues[:_MAX_DIAGNOSTICS]


def validate_actions_evidence(raw: bytes | str) -> dict[str, Any]:
    """Validate one record's structure only. The result is never a gate or source-truth claim."""
    value, issues = _parse(raw, "actions_evidence")
    if issues:
        normalized = [_issue(item["code"].split(".")[-1], item["path"], item["message"]) for item in issues]
        return _result(False, normalized)
    schema, schema_issues = _schema()
    if schema_issues:
        return _result(False, schema_issues)
    assert schema is not None
    try:
        expanded_schema = _expand_schema_refs(schema)
    except (KeyError, TypeError, ValueError):
        return _result(False, [_issue("schema_unavailable", "$", "the evidence schema contains an unsupported reference")])
    issues = _validate_schema(value, expanded_schema)
    if issues:
        return _result(False, [_issue("schema_invalid", item["path"], item["message"]) for item in issues])
    if not isinstance(value, dict):
        return _result(False, [_issue("invalid", "$", "evidence must be a JSON object")])
    issues = _semantics(value)
    return _result(not issues, issues)


def _result(valid: bool, issues: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "contract": "FRAMEWORK-CONTRACT-032",
        "schema_version": "1.0",
        "validation_scope": "structure-and-declared-invariants-only",
        "valid": valid,
        "diagnostics": issues[:_MAX_DIAGNOSTICS],
    }


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="path to one UTF-8 JSON record, or - for standard input")
    args = parser.parse_args()
    try:
        if args.input == "-":
            raw = sys.stdin.buffer.read(_MAX_INPUT_BYTES + 1)
        else:
            with Path(args.input).open("rb") as stream:
                raw = stream.read(_MAX_INPUT_BYTES + 1)
    except OSError:
        print(json.dumps(_result(False, [_issue("input_unavailable", "$", "input could not be read")]), sort_keys=True))
        raise SystemExit(2)
    result = validate_actions_evidence(raw)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    raise SystemExit(0 if result["valid"] else 1)
