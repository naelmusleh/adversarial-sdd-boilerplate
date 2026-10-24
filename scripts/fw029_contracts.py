#!/usr/bin/env python3
"""Strict, dependency-free contracts for FW-TASK-029 receipt and policy v1.

This module checks JSON shape and deterministic contract bindings. It does not
verify signatures, authenticate provider responses, establish trust-root
freshness, authorize a gate, or make a release decision.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "docs" / "framework" / "schemas" / "fw029"
MAX_BYTES = {"receipt": 262_144, "policy": 65_536}
MAX_ARRAYS = {
    "receipt": {"checks": 100, "evidence": 100},
    "policy": {"required_checks": 100},
}
SCHEMA_FILES = {
    "receipt": SCHEMA_DIR / "receipt-v1.schema.json",
    "policy": SCHEMA_DIR / "verification-policy-v1.schema.json",
}
_SCHEMA_KEYWORDS = {
    "$defs", "$id", "$ref", "$schema", "additionalProperties", "const", "enum",
    "format", "items", "maxItems", "maxLength", "minItems", "minLength",
    "minimum", "pattern", "properties", "required", "title", "type",
}
_ANNOTATIONS = {"$id", "$schema", "title"}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class _DuplicateKey(ValueError):
    pass


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(f"duplicate object key {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard numeric constant {value!r}")


def _diag(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _result(state: str, diagnostics: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "state": state,
        "diagnostics": diagnostics,
        "signature_status": "not-verified",
        "provider_authentication": "not-performed",
    }


def _raw_bytes(raw: bytes | str, kind: str) -> tuple[bytes | None, list[dict[str, str]]]:
    label = "receipt" if kind == "receipt" else "policy"
    if raw is None:
        return None, [_diag(f"{label}.input_missing", "$", f"{label} input was not supplied")]
    if isinstance(raw, bytes):
        data = raw
    elif isinstance(raw, str):
        try:
            data = raw.encode("utf-8", errors="strict")
        except UnicodeError:
            return None, [_diag(f"{label}.json_invalid", "$", "input is not valid UTF-8")]
    else:
        return None, [_diag(f"{label}.json_invalid", "$", "input must be bytes or text")]
    if len(data) > MAX_BYTES[kind]:
        return data, [_diag(
            f"{label}.size_limit_exceeded", "$",
            f"input is {len(data)} bytes; limit is {MAX_BYTES[kind]} bytes",
        )]
    return data, []


def _parse(raw: bytes | str, kind: str) -> tuple[dict[str, Any] | None, bytes | None, list[dict[str, str]]]:
    data, diagnostics = _raw_bytes(raw, kind)
    if diagnostics:
        return None, data, diagnostics
    assert data is not None
    label = "receipt" if kind == "receipt" else "policy"
    try:
        text = data.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        return None, data, [_diag(f"{label}.json_invalid", "$", f"invalid JSON input: {exc}")]
    if not isinstance(value, dict):
        return None, data, [_diag(f"{label}.schema_invalid", "$", "document root must be an object")]
    return value, data, []


def _array_limit_diagnostics(value: Mapping[str, Any], kind: str) -> list[dict[str, str]]:
    label = "receipt" if kind == "receipt" else "policy"
    issues = []
    for field, limit in MAX_ARRAYS[kind].items():
        items = value.get(field)
        if isinstance(items, list) and len(items) > limit:
            issues.append(_diag(
                "contract.array_limit_exceeded", f"$.{field}",
                f"{field} contains {len(items)} entries; limit is {limit}",
            ))
    return issues


def _schema_for(kind: str) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    label = "receipt" if kind == "receipt" else "policy"
    try:
        data = SCHEMA_FILES[kind].read_bytes()
        schema = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs_no_duplicates)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return None, [_diag("contract.schema_unavailable", "$", f"cannot load {label} schema: {exc}")]
    if not isinstance(schema, dict):
        return None, [_diag("contract.schema_unavailable", "$", f"{label} schema root is not an object")]
    return schema, []


def _resolve_ref(root_schema: Mapping[str, Any], ref: str) -> Any:
    if not ref.startswith("#/"):
        raise ValueError("external or non-pointer schema references are unsupported")
    current: Any = root_schema
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            raise ValueError(f"unresolved schema reference {ref!r}")
        current = current[token]
    return current


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def _format_valid(value: str, fmt: str) -> bool:
    if fmt == "uri":
        if any(ord(ch) <= 32 or ord(ch) == 127 for ch in value):
            return False
        try:
            return bool(urlsplit(value).scheme)
        except ValueError:
            return False
    if fmt == "date-time":
        try:
            parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
            return parsed.tzinfo is not None and parsed.utcoffset() is not None
        except (ValueError, OverflowError):
            return False
    return False


def _validate_schema(
    value: Any,
    schema: Mapping[str, Any],
    root_schema: Mapping[str, Any],
    kind: str,
    path: str = "$",
) -> list[dict[str, str]]:
    label = "receipt" if kind == "receipt" else "policy"
    issues: list[dict[str, str]] = []
    unsupported = sorted(set(schema) - _SCHEMA_KEYWORDS)
    if unsupported:
        return [_diag(
            "contract.schema_unsupported", path,
            f"unsupported schema keyword(s): {', '.join(unsupported)}",
        )]
    if "$ref" in schema:
        try:
            target = _resolve_ref(root_schema, schema["$ref"])
        except (TypeError, ValueError) as exc:
            return [_diag("contract.schema_unsupported", path, str(exc))]
        if not isinstance(target, dict):
            return [_diag("contract.schema_unsupported", path, "schema reference target must be an object")]
        issues.extend(_validate_schema(value, target, root_schema, kind, path))

    expected = schema.get("type")
    if expected is not None:
        if not isinstance(expected, str) or not _matches_type(value, expected):
            issues.append(_diag(
                f"{label}.schema_invalid", path,
                f"value must have JSON type {expected!r}",
            ))
            return issues

    if "const" in schema and value != schema["const"]:
        issues.append(_diag(f"{label}.schema_invalid", path, "value does not match required constant"))
    if "enum" in schema and value not in schema["enum"]:
        issues.append(_diag(f"{label}.schema_invalid", path, "value is outside the allowed enumeration"))

    if isinstance(value, dict):
        for field in sorted(schema.get("required", [])):
            if field not in value:
                issues.append(_diag(
                    f"{label}.schema_invalid", f"{path}.{field}", "required property is missing",
                ))
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            return issues + [_diag("contract.schema_unsupported", path, "properties must be an object")]
        if schema.get("additionalProperties") is False:
            for field in sorted(set(value) - set(properties)):
                issues.append(_diag(
                    f"{label}.schema_invalid", f"{path}.{field}", "additional property is not allowed",
                ))
        for field, subschema in properties.items():
            if field in value:
                if not isinstance(subschema, dict):
                    issues.append(_diag("contract.schema_unsupported", f"{path}.{field}", "property schema must be an object"))
                else:
                    issues.extend(_validate_schema(value[field], subschema, root_schema, kind, f"{path}.{field}"))

    if isinstance(value, list):
        minimum = schema.get("minItems")
        maximum = schema.get("maxItems")
        if isinstance(minimum, int) and len(value) < minimum:
            issues.append(_diag(f"{label}.schema_invalid", path, f"array must contain at least {minimum} item(s)"))
        if isinstance(maximum, int) and len(value) > maximum:
            issues.append(_diag(f"{label}.schema_invalid", path, f"array must contain at most {maximum} item(s)"))
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                issues.extend(_validate_schema(item, item_schema, root_schema, kind, f"{path}[{index}]"))
        elif item_schema is not None:
            issues.append(_diag("contract.schema_unsupported", path, "items schema must be an object"))

    if isinstance(value, str):
        if isinstance(schema.get("minLength"), int) and len(value) < schema["minLength"]:
            issues.append(_diag(f"{label}.schema_invalid", path, "string is shorter than the allowed minimum"))
        if isinstance(schema.get("maxLength"), int) and len(value) > schema["maxLength"]:
            issues.append(_diag(f"{label}.schema_invalid", path, "string exceeds the allowed maximum length"))
        if "pattern" in schema:
            try:
                matched = re.search(schema["pattern"], value) is not None
            except (TypeError, re.error):
                return issues + [_diag("contract.schema_unsupported", path, "schema pattern is invalid")]
            if not matched:
                issues.append(_diag(f"{label}.schema_invalid", path, "string does not match the required pattern"))
        if "format" in schema and not _format_valid(value, schema["format"]):
            issues.append(_diag(f"{label}.schema_invalid", path, f"string is not a valid {schema['format']}"))

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            issues.append(_diag(f"{label}.schema_invalid", path, f"number must be at least {minimum}"))
    return issues


def _schema_diagnostics(value: dict[str, Any], kind: str) -> list[dict[str, str]]:
    schema, issues = _schema_for(kind)
    if issues:
        return issues
    assert schema is not None
    return _validate_schema(value, schema, schema, kind)


def validate_receipt(raw: bytes | str) -> dict[str, Any]:
    """Validate receipt JSON shape and contract limits; does not verify a signature."""
    value, _, issues = _parse(raw, "receipt")
    if issues:
        return _result("failed", issues)
    assert value is not None
    issues = _array_limit_diagnostics(value, "receipt")
    if not issues:
        issues = _schema_diagnostics(value, "receipt")
    return _result("contract_valid" if not issues else "failed", issues)


def validate_policy(raw: bytes | str) -> dict[str, Any]:
    """Validate policy JSON shape and limits; does not establish policy trust."""
    value, _, issues = _parse(raw, "policy")
    if issues:
        return _result("failed", issues)
    assert value is not None
    issues = _array_limit_diagnostics(value, "policy")
    if not issues:
        issues = _schema_diagnostics(value, "policy")
    return _result("contract_valid" if not issues else "failed", issues)


def _same(left: Any, right: Any) -> bool:
    return left == right


def _identity_diagnostics(
    receipt: Mapping[str, Any],
    policy: Mapping[str, Any],
    *,
    evidence_bytes: Mapping[str, bytes] | None,
    provider_check_ids: Mapping[str, str] | None,
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for field in ("host", "owner", "name", "id"):
        if receipt.get("repository", {}).get(field) != policy.get("repository", {}).get(field):
            issues.append(_diag("receipt.repository_mismatch", f"$.repository.{field}", "receipt repository differs from pinned policy"))
    for field in ("sha",):
        if receipt.get("source", {}).get(field) != policy.get("source", {}).get(field):
            issues.append(_diag("receipt.source_mismatch", f"$.source.{field}", "receipt source revision differs from pinned policy"))
    if receipt.get("source", {}).get("ref") != policy.get("source", {}).get("ref"):
        issues.append(_diag("receipt.source_ref_mismatch", "$.source.ref", "receipt source ref differs from pinned policy"))
    for field in ("id", "version", "sha256"):
        if receipt.get("gate_contract", {}).get(field) != policy.get("gate_contract", {}).get(field):
            issues.append(_diag("receipt.contract_mismatch", f"$.gate_contract.{field}", "receipt gate contract differs from pinned policy"))
    for field in ("path", "revision_sha", "identity"):
        if receipt.get("workflow", {}).get(field) != policy.get("workflow", {}).get(field):
            issues.append(_diag("receipt.workflow_mismatch", f"$.workflow.{field}", "receipt workflow differs from pinned policy"))
    for field in ("provider", "run_id", "attempt", "event", "ref"):
        if receipt.get("provider_run", {}).get(field) != policy.get("provider_run", {}).get(field):
            issues.append(_diag("receipt.run_mismatch", f"$.provider_run.{field}", "receipt provider run differs from pinned policy"))
    if receipt.get("required_check_manifest_sha256") != policy.get("required_check_manifest_sha256"):
        issues.append(_diag("receipt.manifest_mismatch", "$.required_check_manifest_sha256", "receipt check-manifest digest differs from pinned policy"))
    for field in ("provider", "identity"):
        if receipt.get("issuer", {}).get(field) != policy.get("issuer", {}).get(field):
            issues.append(_diag("issuer.identity_untrusted", f"$.issuer.{field}", "receipt issuer claim differs from pinned policy"))

    actual_checks = receipt.get("checks", [])
    required_checks = policy.get("required_checks", [])
    if isinstance(actual_checks, list) and isinstance(required_checks, list):
        actual_ids = [item.get("logical_id") for item in actual_checks if isinstance(item, dict)]
        required_ids = [item.get("logical_id") for item in required_checks if isinstance(item, dict)]
        if (
            len(actual_ids) != len(actual_checks)
            or len(required_ids) != len(required_checks)
            or len(actual_ids) != len(set(actual_ids))
            or len(required_ids) != len(set(required_ids))
            or set(actual_ids) != set(required_ids)
        ):
            issues.append(_diag("receipt.check_set_mismatch", "$.checks", "receipt logical check set is not exactly the pinned required set"))
        else:
            required_by_id = {item["logical_id"]: item for item in required_checks}
            for index, check in enumerate(actual_checks):
                check_path = f"$.checks[{index}]"
                logical_id = check["logical_id"]
                if check.get("name") != required_by_id[logical_id].get("name"):
                    issues.append(_diag("receipt.check_identity_mismatch", f"{check_path}.name", "provider check name differs from the pinned logical check"))
                if check.get("conclusion") != "success":
                    issues.append(_diag("receipt.check_failed", f"{check_path}.conclusion", "required check did not conclude successfully"))
                if check.get("head_sha") != receipt.get("source", {}).get("sha"):
                    issues.append(_diag("receipt.check_source_mismatch", f"{check_path}.head_sha", "required check head SHA differs from receipt source SHA"))
                if provider_check_ids is not None:
                    expected_id = provider_check_ids.get(logical_id)
                    if expected_id is None or check.get("provider_check_id") != expected_id:
                        issues.append(_diag("receipt.check_identity_mismatch", f"{check_path}.provider_check_id", "provider check ID differs from the supplied normalized provider observation"))

    if evidence_bytes is not None:
        for index, item in enumerate(receipt.get("evidence", [])):
            if not isinstance(item, dict):
                continue
            evidence_id = item.get("evidence_id")
            if evidence_id in evidence_bytes:
                actual = hashlib.sha256(evidence_bytes[evidence_id]).hexdigest()
                expected = item.get("sha256")
                if not isinstance(expected, str) or not hmac.compare_digest(actual, expected):
                    issues.append(_diag("evidence.digest_mismatch", f"$.evidence[{index}].sha256", "supplied evidence bytes differ from receipt digest"))
    return issues


def validate_receipt_policy(
    receipt_raw: bytes | str,
    policy_raw: bytes | str,
    *,
    expected_policy_sha256: str | None,
    trust_root_bytes: bytes | None,
    evidence_bytes: Mapping[str, bytes] | None = None,
    provider_check_ids: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Check exact contract bindings against caller-supplied pins and bytes.

    Provider check IDs and evidence bytes are compared when supplied. These
    values are observations only; this function does not authenticate them.
    A contract_valid result is not a signature, issuer, gate, or release pass.
    """
    receipt, _, receipt_issues = _parse(receipt_raw, "receipt")
    if receipt_issues:
        state = "blocked" if receipt_issues[0]["code"].endswith("input_missing") else "failed"
        return _result(state, receipt_issues)
    policy, policy_bytes, policy_issues = _parse(policy_raw, "policy")
    if policy_issues:
        state = "blocked" if policy_issues[0]["code"].endswith("input_missing") else "failed"
        return _result(state, policy_issues)
    assert receipt is not None and policy is not None and policy_bytes is not None

    limit_issues = _array_limit_diagnostics(receipt, "receipt") + _array_limit_diagnostics(policy, "policy")
    if limit_issues:
        return _result("failed", limit_issues)
    if expected_policy_sha256 is None:
        return _result("blocked", [_diag("policy.expected_digest_missing", "$", "separately supplied expected policy digest is required")])
    if not isinstance(expected_policy_sha256, str) or not _HEX64.fullmatch(expected_policy_sha256):
        return _result("blocked", [_diag("policy.expected_digest_invalid", "$", "expected policy digest must be 64 lowercase hexadecimal characters")])
    actual_policy_sha256 = hashlib.sha256(policy_bytes).hexdigest()
    if not hmac.compare_digest(actual_policy_sha256, expected_policy_sha256):
        return _result("failed", [_diag("policy.digest_mismatch", "$", "policy bytes differ from separately pinned digest")])

    policy_shape_issues = _schema_diagnostics(policy, "policy")
    if policy_shape_issues:
        return _result("failed", policy_shape_issues)
    if policy.get("verification_mode") != "read-only-repeatable":
        return _result("failed", [_diag("policy.replay_mode_unsupported", "$.verification_mode", "v1 supports only read-only-repeatable verification")])
    if trust_root_bytes is None:
        return _result("blocked", [_diag("trust_root.missing", "$", "caller-supplied trust-root bytes are required")])
    if not isinstance(trust_root_bytes, bytes):
        return _result("blocked", [_diag("trust_root.missing", "$", "trust-root input must be supplied as bytes")])
    expected_root_sha256 = policy.get("issuer", {}).get("trust_root_sha256")
    actual_root_sha256 = hashlib.sha256(trust_root_bytes).hexdigest()
    if not isinstance(expected_root_sha256, str) or not hmac.compare_digest(actual_root_sha256, expected_root_sha256):
        return _result("failed", [_diag("trust_root.digest_mismatch", "$.issuer.trust_root_sha256", "trust-root bytes differ from policy-bound digest")])

    issues = _identity_diagnostics(
        receipt, policy,
        evidence_bytes=evidence_bytes,
        provider_check_ids=provider_check_ids,
    )
    if issues:
        return _result("failed", issues)
    receipt_shape_issues = _schema_diagnostics(receipt, "receipt")
    if receipt_shape_issues:
        return _result("failed", receipt_shape_issues)
    return _result("contract_valid", [])


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON with UTF-8, sorted keys, and no insignificant whitespace."""
    try:
        text = json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        )
        return text.encode("utf-8", errors="strict")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ValueError(f"value cannot be serialized as canonical contract JSON: {exc}") from exc
