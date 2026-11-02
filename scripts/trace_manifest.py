#!/usr/bin/env python3
"""Validate FW-028 exact-revision trace manifests against supplied evidence.

The validator checks deterministic bindings and mapping completeness. It does not
authenticate a provider response, decide whether a path semantically implements
a criterion, establish branch protection, or modify the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit

from scripts.quality_profiles import parse_json, resolve_risk, validate_profile

SHA_RE = re.compile(r"^[a-f0-9]{40}$")
TASK_RE = re.compile(r"^[A-Z]+-TASK-[0-9]{3}$")
MANIFEST_FIELDS = {
    "schema_version", "repository", "source_sha", "task_id", "criterion_ids",
    "changed_paths", "path_criteria", "profile", "required_checks", "exceptions",
    "declared_risk_tier",
}


def _diag(items: list[dict[str, str]], code: str, path: str, message: str) -> None:
    items.append({"code": code, "path": path, "message": message})


def _unique_text_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
        and len(value) == len(set(value))
    )


def _canonical_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value or "\\" in value:
        return False
    parsed = PurePosixPath(value)
    return (
        not parsed.is_absolute()
        and value != "."
        and parsed.as_posix() == value
        and all(part not in {"", ".", ".."} for part in parsed.parts)
        and not re.match(r"^[A-Za-z]:", value)
    )


def _repository_uri(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = urlsplit(value)
        return bool(parsed.scheme and parsed.netloc and not parsed.username and not parsed.password)
    except ValueError:
        return False


def _check_symlink_components(
    path: str, root: Path, diagnostics: list[dict[str, str]]
) -> None:
    current = root
    for part in PurePosixPath(path).parts:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            # A deleted/new file may not exist; any existing ancestor was checked.
            break
        except OSError as exc:
            _diag(diagnostics, "PATH-INSPECTION-FAILED", path, f"cannot inspect path component: {exc}")
            break
        if stat.S_ISLNK(mode):
            _diag(diagnostics, "PATH-SYMLINK-ESCAPE", path, "changed path traverses a symlink")
            break


def _mapping_records(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def validate_trace_manifest(
    manifest_raw: bytes | str,
    *,
    expected_repository: str,
    expected_source_sha: str,
    expected_task_id: str,
    expected_criterion_ids: Sequence[str],
    observed_changed_paths: Sequence[str],
    profile_raw: bytes | str,
    required_check_policy: Sequence[Mapping[str, Any]],
    measurement_result: Mapping[str, Any],
    checkout_root: str | Path,
    criterion_tags: Sequence[str] = (),
    criterion_risk_tiers: Sequence[str] = (),
) -> dict[str, Any]:
    """Check trace semantics against independently supplied repository facts.

    The supplied provider result is data to validate, not cryptographic proof.
    A caller must obtain it from a trusted provider adapter before relying on it.
    """
    diagnostics: list[dict[str, str]] = []
    try:
        manifest = parse_json(manifest_raw, label="trace manifest")
    except (TypeError, ValueError) as exc:
        return {"state": "blocked", "diagnostics": [{
            "code": "TRACE-MANIFEST-JSON-INVALID", "path": "$", "message": str(exc)
        }]}
    try:
        profile = parse_json(profile_raw, label="quality profile")
    except (TypeError, ValueError) as exc:
        return {"state": "blocked", "diagnostics": [{
            "code": "TRACE-PROFILE-JSON-INVALID", "path": "$.profile", "message": str(exc)
        }]}

    if not isinstance(manifest, dict):
        return {"state": "blocked", "diagnostics": [{
            "code": "TRACE-MANIFEST-OBJECT-REQUIRED", "path": "$", "message": "manifest root must be an object"
        }]}
    missing_fields = MANIFEST_FIELDS - manifest.keys()
    unknown_fields = manifest.keys() - MANIFEST_FIELDS
    for field in sorted(missing_fields):
        _diag(diagnostics, "TRACE-FIELD-MISSING", f"$.{field}", "required field is missing")
    for field in sorted(unknown_fields):
        _diag(diagnostics, "TRACE-FIELD-UNKNOWN", f"$.{field}", "unknown field is not allowed")
    if manifest.get("schema_version") != "1":
        _diag(diagnostics, "TRACE-SCHEMA-VERSION-UNSUPPORTED", "$.schema_version", "must be string '1'")

    repo = manifest.get("repository")
    if not _repository_uri(repo):
        _diag(diagnostics, "TRACE-REPOSITORY-INVALID", "$.repository", "must be an absolute repository URI")
    if repo != expected_repository:
        _diag(diagnostics, "TRACE-REPOSITORY-MISMATCH", "$.repository", "repository differs from the expected repository")
    source_sha = manifest.get("source_sha")
    if not isinstance(source_sha, str) or not SHA_RE.fullmatch(source_sha):
        _diag(diagnostics, "TRACE-SOURCE-SHA-INVALID", "$.source_sha", "must be a full lowercase 40-character commit SHA")
    if source_sha != expected_source_sha:
        _diag(diagnostics, "TRACE-SOURCE-SHA-MISMATCH", "$.source_sha", "manifest source differs from the evaluated source revision")
    task_id = manifest.get("task_id")
    if not isinstance(task_id, str) or not TASK_RE.fullmatch(task_id):
        _diag(diagnostics, "TRACE-TASK-ID-INVALID", "$.task_id", "must be a stable TASK identifier")
    if task_id != expected_task_id:
        _diag(diagnostics, "TRACE-TASK-MISMATCH", "$.task_id", "manifest task differs from the selected task")

    criteria = manifest.get("criterion_ids")
    if not _unique_text_list(criteria):
        _diag(diagnostics, "TRACE-CRITERIA-INVALID", "$.criterion_ids", "must be a non-empty unique list of non-empty IDs")
        criteria = []
    try:
        expected_criteria = list(expected_criterion_ids)
    except TypeError:
        expected_criteria = []
        _diag(diagnostics, "TRACE-EXPECTED-CRITERIA-INVALID", "expected.criterion_ids", "expected criteria must be an array")
    if not _unique_text_list(expected_criteria):
        _diag(diagnostics, "TRACE-EXPECTED-CRITERIA-INVALID", "expected.criterion_ids", "expected criteria must be non-empty, unique IDs")
        expected_criteria = []
    if set(criteria) != set(expected_criteria):
        _diag(diagnostics, "TRACE-CRITERIA-MISMATCH", "$.criterion_ids", "manifest criteria must exactly match the selected task criteria")

    paths = manifest.get("changed_paths")
    if not isinstance(paths, list) or not paths:
        _diag(diagnostics, "TRACE-PATHS-INVALID", "$.changed_paths", "must be a non-empty array")
        paths = []
    seen_paths: set[str] = set()
    for index, path in enumerate(paths):
        if not _canonical_path(path):
            _diag(diagnostics, "TRACE-PATH-NONCANONICAL", f"$.changed_paths[{index}]", "path must be canonical repository-relative POSIX syntax")
        elif path in seen_paths:
            _diag(diagnostics, "TRACE-PATH-DUPLICATE", f"$.changed_paths[{index}]", "changed paths must be unique")
        else:
            seen_paths.add(path)
    try:
        observed = list(observed_changed_paths)
    except TypeError:
        observed = []
        _diag(diagnostics, "TRACE-OBSERVED-PATHS-INVALID", "observed.changed_paths", "observed paths must be an array")
    if any(not _canonical_path(path) for path in observed):
        _diag(diagnostics, "TRACE-OBSERVED-PATH-NONCANONICAL", "observed.changed_paths", "observed inventory contains a noncanonical path")
    observed_text = [path for path in observed if isinstance(path, str)]
    if len(observed_text) != len(set(observed_text)):
        _diag(diagnostics, "TRACE-OBSERVED-PATH-DUPLICATE", "observed.changed_paths", "observed inventory contains duplicates")
    valid_paths = {path for path in paths if isinstance(path, str)}
    if valid_paths != set(observed_text) or len(valid_paths) != len(paths):
        _diag(diagnostics, "TRACE-PATH-INVENTORY-MISMATCH", "$.changed_paths", "manifest paths must exactly match the observed changed-path inventory")

    try:
        root_path = Path(checkout_root)
        if root_path.is_symlink():
            raise ValueError("checkout root must not be a symlink")
        root = root_path.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("checkout root must be a directory")
        path_candidates = {path for path in paths + observed if isinstance(path, str)}
        for path in path_candidates:
            if _canonical_path(path):
                _check_symlink_components(path, root, diagnostics)
    except (OSError, ValueError, TypeError) as exc:
        _diag(diagnostics, "TRACE-CHECKOUT-ROOT-INVALID", "checkout_root", str(exc))

    pairs = manifest.get("path_criteria")
    if not isinstance(pairs, list) or not pairs:
        _diag(diagnostics, "TRACE-PATH-CRITERIA-INVALID", "$.path_criteria", "must contain path/criterion mappings")
        pairs = []
    known_paths = {path for path in paths if isinstance(path, str)}
    known_criteria = set(criteria)
    mapped_paths: set[str] = set()
    mapped_criteria: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    for index, pair in enumerate(pairs):
        prefix = f"$.path_criteria[{index}]"
        if not isinstance(pair, dict) or set(pair) != {"path", "criterion_ids"}:
            _diag(diagnostics, "TRACE-PATH-CRITERIA-SHAPE-INVALID", prefix, "mapping must contain only path and criterion_ids")
            continue
        path = pair.get("path")
        ids = pair.get("criterion_ids")
        if not _canonical_path(path):
            _diag(diagnostics, "TRACE-PATH-NONCANONICAL", f"{prefix}.path", "path must be canonical repository-relative POSIX syntax")
        if not isinstance(path, str) or path not in known_paths:
            _diag(diagnostics, "TRACE-MAPPING-PATH-UNKNOWN", f"{prefix}.path", "mapping path is not in changed_paths")
        if not _unique_text_list(ids):
            _diag(diagnostics, "TRACE-MAPPING-CRITERIA-INVALID", f"{prefix}.criterion_ids", "must be a non-empty unique list")
            continue
        for criterion in ids:
            if criterion not in known_criteria:
                _diag(diagnostics, "TRACE-MAPPING-CRITERION-UNKNOWN", f"{prefix}.criterion_ids", f"unknown criterion {criterion!r}")
            if not isinstance(path, str):
                continue
            key = (path, criterion)
            if key in seen_pairs:
                _diag(diagnostics, "TRACE-MAPPING-DUPLICATE", prefix, "path/criterion pair is duplicated")
            seen_pairs.add(key)
            mapped_paths.add(path)
            mapped_criteria.add(criterion)
    for path in sorted(known_paths - mapped_paths):
        _diag(diagnostics, "TRACE-PATH-UNMAPPED", "$.path_criteria", f"changed path {path!r} has no criterion link")
    for criterion in sorted(known_criteria - mapped_criteria):
        _diag(diagnostics, "TRACE-CRITERION-UNMAPPED", "$.path_criteria", f"criterion {criterion!r} has no changed-path link")

    profile_digest = hashlib.sha256(profile_raw.encode("utf-8") if isinstance(profile_raw, str) else profile_raw).hexdigest()
    profile_ref = manifest.get("profile")
    if not isinstance(profile_ref, dict):
        _diag(diagnostics, "TRACE-PROFILE-REFERENCE-INVALID", "$.profile", "must be a profile reference object")
        profile_ref = {}
    profile_id = profile.get("profile_id") if isinstance(profile, dict) else None
    profile_version = profile.get("profile_version") if isinstance(profile, dict) else None
    if set(profile_ref) != {"profile_id", "profile_version", "sha256"}:
        _diag(diagnostics, "TRACE-PROFILE-REFERENCE-INVALID", "$.profile", "profile reference must contain only profile_id, profile_version and sha256")
    if profile_ref.get("profile_id") != profile_id or profile_ref.get("profile_version") != profile_version:
        _diag(diagnostics, "TRACE-PROFILE-IDENTITY-MISMATCH", "$.profile", "profile ID/version differs from exact profile bytes")
    if profile_ref.get("sha256") != profile_digest:
        _diag(diagnostics, "TRACE-PROFILE-DIGEST-MISMATCH", "$.profile.sha256", "profile digest differs from exact profile bytes")
    profile_errors = validate_profile(profile)
    for issue in profile_errors:
        _diag(diagnostics, "TRACE-PROFILE-INVALID", issue.get("path", "$.profile"), issue.get("message", "profile is invalid"))

    declared_risk = manifest.get("declared_risk_tier")
    if isinstance(profile, dict):
        risk = resolve_risk(
            profile, changed_paths=paths, criterion_tags=criterion_tags,
            declared_task_risk_tier=declared_risk,
            declared_criterion_risk_tiers=criterion_risk_tiers,
        )
        for issue in risk["diagnostics"]:
            _diag(diagnostics, issue["code"], issue["path"], issue["message"])

    exceptions = manifest.get("exceptions")
    if not isinstance(exceptions, list):
        _diag(diagnostics, "TRACE-EXCEPTIONS-INVALID", "$.exceptions", "must be an array")
    elif exceptions:
        _diag(diagnostics, "TRACE-EXCEPTION-AUTHORITY-UNSUPPORTED", "$.exceptions", "positive exceptions are rejected until an independent authorization contract is approved")

    policy_by_id: dict[str, Mapping[str, Any]] = {}
    try:
        policy_entries = list(required_check_policy)
    except TypeError:
        policy_entries = []
        _diag(diagnostics, "TRACE-CHECK-POLICY-INVALID", "required_check_policy", "must be an array")
    for index, check in enumerate(policy_entries):
        prefix = f"required_check_policy[{index}]"
        if not isinstance(check, Mapping):
            _diag(diagnostics, "TRACE-CHECK-POLICY-INVALID", prefix, "check policy entry must be an object")
            continue
        required = check.get("required")
        if type(required) is not bool:
            _diag(diagnostics, "TRACE-CHECK-POLICY-INVALID", f"{prefix}.required", "required must be a boolean")
        task_ids = check.get("task_ids")
        if not _unique_text_list(task_ids) or not task_ids:
            _diag(diagnostics, "TRACE-CHECK-POLICY-INVALID", f"{prefix}.task_ids", "task_ids must be a non-empty array of unique IDs")
            task_ids = []
        check_id = check.get("check_id")
        if not isinstance(check_id, str) or not re.fullmatch(r"[A-Z0-9][A-Z0-9._-]{1,63}", check_id):
            _diag(diagnostics, "TRACE-CHECK-POLICY-INVALID", f"{prefix}.check_id", "check_id must be a stable check identifier")
            continue
        if check.get("execution") not in {"ci", "manual"}:
            _diag(diagnostics, "TRACE-CHECK-POLICY-INVALID", f"{prefix}.execution", "execution must be ci or manual")
        if not isinstance(check.get("provider"), str) or not check.get("provider"):
            _diag(diagnostics, "TRACE-CHECK-POLICY-INVALID", f"{prefix}.provider", "provider must be a non-empty string")
        if not isinstance(check.get("name"), str) or not check.get("name"):
            _diag(diagnostics, "TRACE-CHECK-POLICY-INVALID", f"{prefix}.name", "name must be a non-empty string")
        linked_criteria = check.get("acceptance_criteria")
        if not _unique_text_list(linked_criteria):
            _diag(diagnostics, "TRACE-CHECK-CRITERIA-INVALID", f"{prefix}.acceptance_criteria", "acceptance_criteria must be a non-empty array of unique IDs")
            linked_criteria = []
        applies_to_task = expected_task_id in task_ids
        if applies_to_task and any(item not in expected_criteria for item in linked_criteria):
            _diag(diagnostics, "TRACE-CHECK-CRITERIA-INVALID", f"{prefix}.acceptance_criteria", "required check references unknown task criteria")
        if required is True and applies_to_task:
            if check_id in policy_by_id:
                _diag(diagnostics, "TRACE-CHECK-POLICY-DUPLICATE", f"{prefix}.check_id", "required check IDs must be unique")
            else:
                policy_by_id[check_id] = check

    manifest_checks = manifest.get("required_checks")
    if not isinstance(manifest_checks, list):
        _diag(diagnostics, "TRACE-CHECKS-INVALID", "$.required_checks", "must be an array")
        manifest_checks = []
    manifest_by_id: dict[str, Mapping[str, Any]] = {}
    for index, check in enumerate(manifest_checks):
        if not isinstance(check, dict):
            _diag(diagnostics, "TRACE-CHECK-SHAPE-INVALID", f"$.required_checks[{index}]", "check must be an object")
            continue
        if set(check) != {"check_id", "provider", "name"}:
            _diag(diagnostics, "TRACE-CHECK-SHAPE-INVALID", f"$.required_checks[{index}]", "check must contain only check_id, provider and name")
            continue
        check_id = check.get("check_id")
        if not isinstance(check_id, str) or not check_id:
            _diag(diagnostics, "TRACE-CHECK-ID-INVALID", f"$.required_checks[{index}].check_id", "check ID must be non-empty")
            continue
        if check_id in manifest_by_id:
            _diag(diagnostics, "TRACE-CHECK-DUPLICATE", f"$.required_checks[{index}].check_id", "required check IDs must be unique")
        manifest_by_id[check_id] = check
    if set(manifest_by_id) != set(policy_by_id):
        _diag(diagnostics, "TRACE-CHECK-POLICY-MISMATCH", "$.required_checks", "manifest check IDs must exactly match required checks for the selected task")
    for check_id, policy in policy_by_id.items():
        declared = manifest_by_id.get(check_id)
        if declared is None:
            continue
        if policy.get("execution") != "ci":
            _diag(diagnostics, "TRACE-CHECK-MANUAL-UNSUPPORTED", f"$.required_checks[{check_id}]", "this provider-binding validator accepts only required CI checks")
        if declared.get("provider") != policy.get("provider") or declared.get("name") != policy.get("name"):
            _diag(diagnostics, "TRACE-CHECK-POLICY-IDENTITY-MISMATCH", f"$.required_checks[{check_id}]", "provider and check name must match the app-owned check policy")

    result = measurement_result
    if not isinstance(result, Mapping):
        _diag(diagnostics, "TRACE-RESULT-INVALID", "measurement_result", "normalized result must be an object")
        result = {}
    result_bindings = {
        "repository": expected_repository,
        "source_sha": expected_source_sha,
        "profile_sha256": profile_digest,
        "manifest_sha256": hashlib.sha256(manifest_raw.encode("utf-8") if isinstance(manifest_raw, str) else manifest_raw).hexdigest(),
    }
    for field, expected in result_bindings.items():
        if result.get(field) != expected:
            _diag(diagnostics, "TRACE-RESULT-BINDING-MISMATCH", f"measurement_result.{field}", "normalized result does not bind to the expected exact input")
    if result.get("overall_state") != "pass":
        _diag(diagnostics, "TRACE-RESULT-NONPASS", "measurement_result.overall_state", "normalized result must be pass for required provider checks to satisfy this evaluation")

    provider_checks = result.get("provider_checks", [])
    if not isinstance(provider_checks, list):
        _diag(diagnostics, "TRACE-PROVIDER-CHECKS-INVALID", "measurement_result.provider_checks", "must be an array")
        provider_checks = []
    by_required_id: dict[str, list[Mapping[str, Any]]] = {}
    provider_run_ids: set[tuple[str, str, str]] = set()
    for index, evidence in enumerate(provider_checks):
        if not isinstance(evidence, Mapping):
            _diag(diagnostics, "TRACE-PROVIDER-CHECK-INVALID", f"measurement_result.provider_checks[{index}]", "provider check must be an object")
            continue
        logical_id = evidence.get("required_check_id")
        if not isinstance(logical_id, str) or logical_id not in policy_by_id:
            _diag(diagnostics, "TRACE-PROVIDER-CHECK-UNKNOWN", f"measurement_result.provider_checks[{index}].required_check_id", "provider result does not map to a required check for this task")
            continue
        by_required_id.setdefault(logical_id, []).append(evidence)
        identity = (str(evidence.get("provider")), str(evidence.get("check_id")), str(evidence.get("run_id")))
        if identity in provider_run_ids:
            _diag(diagnostics, "TRACE-PROVIDER-CHECK-DUPLICATE", f"measurement_result.provider_checks[{index}]", "provider check/run identity is duplicated")
        provider_run_ids.add(identity)
        expected = policy_by_id[logical_id]
        declared = manifest_by_id.get(logical_id, {})
        if evidence.get("provider") != declared.get("provider") or evidence.get("provider") != expected.get("provider"):
            _diag(diagnostics, "TRACE-PROVIDER-IDENTITY-MISMATCH", f"measurement_result.provider_checks[{index}].provider", "provider differs from manifest or app policy")
        if evidence.get("repository") != expected_repository:
            _diag(diagnostics, "TRACE-PROVIDER-REPOSITORY-MISMATCH", f"measurement_result.provider_checks[{index}].repository", "provider check is for another repository")
        if evidence.get("check_name") != declared.get("name") or evidence.get("check_name") != expected.get("name"):
            _diag(diagnostics, "TRACE-PROVIDER-NAME-MISMATCH", f"measurement_result.provider_checks[{index}].check_name", "provider-reported name differs from the declared required check")
        if not isinstance(evidence.get("check_id"), str) or not evidence.get("check_id"):
            _diag(diagnostics, "TRACE-PROVIDER-CHECK-ID-INVALID", f"measurement_result.provider_checks[{index}].check_id", "provider check-run ID must be a non-empty string")
        if not isinstance(evidence.get("run_id"), str) or not evidence.get("run_id"):
            _diag(diagnostics, "TRACE-PROVIDER-RUN-ID-INVALID", f"measurement_result.provider_checks[{index}].run_id", "provider run ID must be a non-empty string")
        if evidence.get("head_sha") != expected_source_sha:
            _diag(diagnostics, "CHECK-HEAD-SHA-MISMATCH", f"measurement_result.provider_checks[{index}].head_sha", "provider check is not for the exact evaluated source SHA")
        if evidence.get("conclusion") != "success":
            _diag(diagnostics, "TRACE-CHECK-NONPASS", f"measurement_result.provider_checks[{index}].conclusion", "required provider check did not conclude success")
    for check_id in sorted(set(policy_by_id) - set(by_required_id)):
        _diag(diagnostics, "TRACE-CHECK-MISSING", f"measurement_result.provider_checks.{check_id}", "required check has no matching provider result")
    for check_id, records in by_required_id.items():
        if len(records) != 1:
            _diag(diagnostics, "TRACE-CHECK-RESULT-CARDINALITY", f"measurement_result.provider_checks.{check_id}", "each required check must have exactly one provider result")

    return {"state": "pass" if not diagnostics else "blocked", "diagnostics": diagnostics}


def _main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="exact trace manifest JSON")
    parser.add_argument("--context", required=True, type=Path, help="JSON containing expected repository/task/path/check facts and measurement result")
    parser.add_argument("--profile", required=True, type=Path, help="exact quality profile JSON bytes")
    parser.add_argument("--checkout-root", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        context_raw = args.context.read_bytes()
        context = parse_json(context_raw, label="validation context")
        manifest_raw = args.manifest.read_bytes()
        profile_raw = args.profile.read_bytes()
        if not isinstance(context, dict):
            raise ValueError("validation context must be an object")
        outcome = validate_trace_manifest(
            manifest_raw,
            expected_repository=context["repository"],
            expected_source_sha=context["source_sha"],
            expected_task_id=context["task_id"],
            expected_criterion_ids=context["criterion_ids"],
            observed_changed_paths=context["changed_paths"],
            profile_raw=profile_raw,
            required_check_policy=context["required_check_policy"],
            measurement_result=context["measurement_result"],
            checkout_root=args.checkout_root,
            criterion_tags=context.get("criterion_tags", []),
            criterion_risk_tiers=context.get("criterion_risk_tiers", []),
        )
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"state": "blocked", "diagnostics": [{
            "code": "TRACE-INPUT-ERROR", "path": "$", "message": str(exc)
        }]}, sort_keys=True))
        return 2
    print(json.dumps(outcome, sort_keys=True, indent=2))
    return 0 if outcome["state"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(_main())
