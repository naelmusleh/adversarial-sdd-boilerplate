"""FW-030 v1 wire-contract validation; this module never launches workloads.

Profile observations accepted by ``preflight_request`` must be explicitly marked
synthetic. No runtime/profile registry is adopted by this implementation unit.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit


_SCHEMA_DIR = Path(__file__).resolve().parents[1] / "docs/framework/schemas/fw030"
_SCHEMAS = {
    "request": _SCHEMA_DIR / "request-v1.schema.json",
    "result": _SCHEMA_DIR / "result-v1.schema.json",
}
_MAX_INPUT_BYTES = 256 * 1024
_MAX_DIAGNOSTICS = 32
_SCHEMA_KEYWORDS = {
    "$defs", "$id", "$ref", "$schema", "additionalProperties", "const",
    "enum", "format", "items", "maxItems", "maxLength", "maximum",
    "minItems", "minLength", "minimum", "pattern", "properties", "required",
    "title", "type", "uniqueItems",
}
_CONTRACT_VERSION = "1.0"
_INVOCATION_ID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


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


def _diag(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _parse(raw: bytes | str, kind: str) -> tuple[Any | None, bytes | None, list[dict[str, str]]]:
    label = f"fw030.{kind}"
    if isinstance(raw, str):
        try:
            data = raw.encode("utf-8", errors="strict")
        except UnicodeError:
            return None, None, [_diag(f"{label}.invalid_json", "$", "input is not valid UTF-8")]
    elif isinstance(raw, bytes):
        data = raw
    else:
        return None, None, [_diag(f"{label}.invalid_json", "$", "input must be UTF-8 JSON bytes or text")]
    if len(data) > _MAX_INPUT_BYTES:
        return None, data, [_diag(f"{label}.size_limit", "$", "input exceeds the contract size limit")]
    try:
        value = json.loads(
            data.decode("utf-8", errors="strict"),
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError, RecursionError):
        # Parser details are intentionally omitted because they can contain input values.
        return None, data, [_diag(f"{label}.invalid_json", "$", "input is not valid strict JSON")]
    return value, data, []


def _schema(kind: str) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    try:
        raw = _SCHEMAS[kind].read_bytes()
        schema = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs_no_duplicates)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return None, [_diag("fw030.schema.unavailable", "$", f"the {kind} contract schema is unavailable or invalid")]
    if not isinstance(schema, dict):
        return None, [_diag("fw030.schema.unavailable", "$", f"the {kind} contract schema root is invalid")]
    return schema, []


def _resolve_ref(root: Mapping[str, Any], ref: str) -> Any:
    if not isinstance(ref, str) or not ref.startswith("#/"):
        raise ValueError
    current: Any = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            raise ValueError
        current = current[part]
    return current


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


def _valid_format(value: str, fmt: str) -> bool:
    if fmt == "uri":
        if any(ord(char) <= 32 or ord(char) == 127 for char in value):
            return False
        try:
            return bool(urlsplit(value).scheme)
        except ValueError:
            return False
    return False


def _validate(value: Any, spec: Mapping[str, Any], root: Mapping[str, Any], path: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if set(spec) - _SCHEMA_KEYWORDS:
        return [_diag("fw030.schema.unsupported_keyword", path, "schema uses an unsupported validation keyword")]
    if "$ref" in spec:
        try:
            target = _resolve_ref(root, spec["$ref"])
        except (TypeError, ValueError):
            return [_diag("fw030.schema.invalid_reference", path, "schema contains an invalid local reference")]
        if not isinstance(target, dict):
            return [_diag("fw030.schema.invalid_reference", path, "schema reference target is invalid")]
        issues.extend(_validate(value, target, root, path))

    expected = spec.get("type")
    types = expected if isinstance(expected, list) else [expected] if expected is not None else []
    if types and not any(isinstance(item, str) and _is_type(value, item) for item in types):
        return issues + [_diag("fw030.schema.invalid", path, "value has the wrong JSON type")]
    if "const" in spec and value != spec["const"]:
        issues.append(_diag("fw030.schema.invalid", path, "value does not match the required constant"))
    if "enum" in spec and value not in spec["enum"]:
        issues.append(_diag("fw030.schema.invalid", path, "value is outside the allowed values"))

    if isinstance(value, dict):
        properties = spec.get("properties", {})
        if not isinstance(properties, dict):
            return issues + [_diag("fw030.schema.invalid", path, "schema properties definition is invalid")]
        for field in spec.get("required", []):
            if field not in value:
                issues.append(_diag("fw030.schema.invalid", f"{path}.{field}", "required property is missing"))
        if spec.get("additionalProperties") is False:
            for field in sorted(set(value) - set(properties)):
                issues.append(_diag("fw030.schema.invalid", f"{path}.{field}", "additional property is not allowed"))
        for field, child_spec in properties.items():
            if field in value:
                if not isinstance(child_spec, dict):
                    issues.append(_diag("fw030.schema.invalid", f"{path}.{field}", "property schema is invalid"))
                else:
                    issues.extend(_validate(value[field], child_spec, root, f"{path}.{field}"))

    if isinstance(value, list):
        if len(value) < spec.get("minItems", 0) or len(value) > spec.get("maxItems", _MAX_INPUT_BYTES):
            issues.append(_diag("fw030.schema.invalid", path, "array length is outside the allowed range"))
        if spec.get("uniqueItems") and len(value) != len({json.dumps(x, sort_keys=True) for x in value}):
            issues.append(_diag("fw030.schema.invalid", path, "array entries must be unique"))
        child_spec = spec.get("items")
        if child_spec is not None:
            if not isinstance(child_spec, dict):
                issues.append(_diag("fw030.schema.invalid", path, "array item schema is invalid"))
            else:
                for index, child in enumerate(value):
                    issues.extend(_validate(child, child_spec, root, f"{path}[{index}]"))

    if isinstance(value, str):
        if len(value) < spec.get("minLength", 0) or len(value) > spec.get("maxLength", _MAX_INPUT_BYTES):
            issues.append(_diag("fw030.schema.invalid", path, "string length is outside the allowed range"))
        pattern = spec.get("pattern")
        if pattern is not None:
            try:
                if re.search(pattern, value) is None:
                    issues.append(_diag("fw030.schema.invalid", path, "string does not match the required format"))
            except (TypeError, re.error):
                issues.append(_diag("fw030.schema.invalid", path, "schema pattern is invalid"))
        if "format" in spec and not _valid_format(value, spec["format"]):
            issues.append(_diag("fw030.schema.invalid", path, "string does not match the required format"))

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < spec.get("minimum", value) or value > spec.get("maximum", value):
            issues.append(_diag("fw030.schema.invalid", path, "number is outside the allowed range"))
    return issues


def _schema_issues(value: Any, kind: str) -> list[dict[str, str]]:
    schema, issues = _schema(kind)
    if issues:
        return issues
    assert schema is not None
    try:
        issues = _validate(value, schema, schema, "$")
    except (RecursionError, TypeError, ValueError):
        return [_diag(f"fw030.{kind}.invalid", "$", "document exceeds contract validation limits")]
    # The adapter boundary needs local/hosted provider presence to be unambiguous.
    if kind == "request" and not issues and isinstance(value, dict):
        context = value["execution_context"]
        if context["kind"] == "local":
            if context["provider_context"] is not None or context.get("absence_reason") != "local_execution_has_no_provider_run":
                issues.append(_diag("fw030.request.context_inconsistent", "$.execution_context", "local context requires explicit provider absence"))
        elif context["provider_context"] is None or "absence_reason" in context:
            issues.append(_diag("fw030.request.context_inconsistent", "$.execution_context", "hosted context requires provider identity and no absence reason"))
        workload = value["workload"]
        if workload["argv"][0] != workload["executable"]:
            issues.append(_diag("fw030.request.command_identity_mismatch", "$.workload", "argv[0] must match the declared executable"))
        for index, mount in enumerate(value["policy"]["mounts"]):
            expected_mode = "read_only" if mount["kind"] == "input" else "write_only"
            if mount["mode"] != expected_mode:
                issues.append(_diag("fw030.request.mount_mode_mismatch", f"$.policy.mounts[{index}].mode", "mount mode does not match its declared purpose"))
        policy_payload = {key: item for key, item in value["policy"].items() if key != "sha256"}
        canonical_policy = json.dumps(policy_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        if hashlib.sha256(canonical_policy).hexdigest() != value["policy"]["sha256"]:
            issues.append(_diag("fw030.request.policy_digest_mismatch", "$.policy.sha256", "policy digest does not match canonical policy fields"))
    return issues[:_MAX_DIAGNOSTICS]


def validate_request(raw: bytes | str) -> dict[str, Any]:
    """Validate request JSON shape and semantic consistency without profile lookup or execution."""
    value, _, parse_issues = _parse(raw, "request")
    issues = parse_issues or _schema_issues(value, "request")
    return {"valid": not issues, "diagnostics": issues[:_MAX_DIAGNOSTICS]}


def validate_result(raw: bytes | str) -> dict[str, Any]:
    """Validate a result record; schema validity is not a gate disposition."""
    value, _, parse_issues = _parse(raw, "result")
    issues = parse_issues or _schema_issues(value, "result")
    if not issues and isinstance(value, dict):
        if value["readiness_status"] != value["states"]["request_readiness"]:
            issues.append(_diag("fw030.result.state_mismatch", "$.states.request_readiness", "request readiness axis must match readiness_status"))
        if value["states"]["authorization"] == "authorized" and value["readiness_status"] != "prerequisites_valid":
            issues.append(_diag("fw030.result.authorization_inconsistent", "$.states.authorization", "authorization cannot be marked before prerequisites are valid"))
    return {"valid": not issues, "diagnostics": issues[:_MAX_DIAGNOSTICS]}


def _valid_synthetic_observation(value: Mapping[str, Any] | None) -> bool:
    if not isinstance(value, Mapping) or value.get("synthetic_test_only") is not True:
        return False
    allowed = {
        "synthetic_test_only", "profile_id", "profile_revision", "support_status",
        "observed_host", "supported_hosts", "runtime_available", "available_capabilities",
    }
    if set(value) != allowed:
        return False
    if not isinstance(value.get("profile_id"), str) or not isinstance(value.get("profile_revision"), str):
        return False
    if value.get("support_status") not in {"supported", "unsupported"}:
        return False
    if not isinstance(value.get("observed_host"), str):
        return False
    supported_hosts = value.get("supported_hosts")
    capabilities = value.get("available_capabilities")
    return (
        isinstance(supported_hosts, list)
        and all(isinstance(host, str) for host in supported_hosts)
        and isinstance(value.get("runtime_available"), bool)
        and isinstance(capabilities, list)
        and all(isinstance(capability, str) for capability in capabilities)
    )


def preflight_request(
    raw: bytes | str,
    profile_observation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate a request against one explicitly synthetic profile observation.

    A ``prerequisites_valid`` result is a structural fixture outcome only. This
    function performs no authorization, host probing, runtime invocation, or gate review.
    """
    request, request_bytes, parse_issues = _parse(raw, "request")
    issues = parse_issues or _schema_issues(request, "request")
    request_id = request.get("invocation_id") if isinstance(request, dict) else None
    if issues:
        status = "invalid"
    elif not _valid_synthetic_observation(profile_observation):
        status = "unsupported"
        code = "fw030.profile.unavailable" if profile_observation is None else "fw030.profile.observation_invalid"
        message = "no synthetic profile observation was supplied; no runtime profile is adopted" if profile_observation is None else "profile observation is malformed or is not explicitly synthetic"
        issues = [_diag(code, "$.profile", message)]
    else:
        profile = request["profile"]
        if profile_observation.get("profile_id") != profile["id"] or profile_observation.get("profile_revision") != profile["revision"]:
            status = "unsupported"
            issues = [_diag("fw030.profile.identity_mismatch", "$.profile", "profile observation does not match the requested profile revision")]
        elif profile_observation.get("support_status") != "supported":
            status = "unsupported"
            issues = [_diag("fw030.profile.unsupported", "$.profile", "the supplied profile observation marks this host/runtime unsupported")]
        elif profile_observation.get("observed_host") not in profile_observation.get("supported_hosts", []):
            status = "unsupported"
            issues = [_diag("fw030.host.unsupported", "$.profile", "the supplied profile observation does not support this host")]
        elif profile_observation.get("runtime_available") is not True:
            status = "blocked"
            issues = [_diag("fw030.runtime.missing", "$.profile", "the required runtime is not available in the supplied observation")]
        else:
            available = profile_observation.get("available_capabilities", [])
            missing = [cap for cap in request["required_capabilities"] if cap not in available]
            if missing:
                status = "blocked"
                issues = [_diag("fw030.capability.unavailable", "$.required_capabilities", "one or more required capabilities are unavailable")]
            else:
                status = "prerequisites_valid"
                issues = []

    result = {
        "schema_version": _CONTRACT_VERSION,
        "invocation_id": request_id if isinstance(request_id, str) and _INVOCATION_ID.fullmatch(request_id) else "00000000-0000-4000-8000-000000000000",
        "request_sha256": hashlib.sha256(request_bytes).hexdigest() if request_bytes is not None else None,
        "readiness_status": status,
        "states": {
            "request_readiness": status,
            "authorization": "not_requested",
            "execution": "not_started",
            "cleanup": "not_applicable",
            "evidence": "not_collected",
            "review": "not_performed",
        },
        "diagnostics": issues[:_MAX_DIAGNOSTICS],
    }
    checked = validate_result(json.dumps(result, separators=(",", ":")))
    if not checked["valid"]:
        # This indicates a bundled schema/code mismatch; keep a valid fail-closed result.
        result["readiness_status"] = "invalid"
        result["states"]["request_readiness"] = "invalid"
        result["diagnostics"] = [_diag("fw030.result.internal_contract_error", "$", "the generated result did not satisfy the result contract")]
    return result
