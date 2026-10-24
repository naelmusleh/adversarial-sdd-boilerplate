#!/usr/bin/env python3
"""Validate app-owned FW-028 quality profiles and assess scoped risk/metrics.

This module is a deterministic local contract evaluator. It does not authenticate
owner decisions or review references, query providers, mutate source, or claim
that profile declarations prove code quality.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import math
import re
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping


PROFILE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,63}$")
PROFILE_VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
RULE_ID_RE = re.compile(r"^[A-Z][A-Z0-9-]{2,63}$")
TIERS = {"low": 0, "medium": 1, "high": 2, "critical": 3}
RISK_DIMENSIONS = {
    "behavior-criticality", "data-security-consequence", "failure-severity",
    "change-type", "testability",
}
CLASSIFICATIONS = {
    "presentation", "configuration", "domain", "authorization", "tenancy",
    "migration", "security",
}
SENSITIVE_CLASSIFICATIONS = {"authorization", "tenancy", "migration", "security"}
ROOT_FIELDS = {
    "schema_version", "profile_id", "profile_version", "owner_ref", "adapter",
    "risk_dimensions", "metric_rules", "path_rules", "escalation_floors",
    "threshold_change_policy", "supersedes",
}


class Diagnostic(dict):
    """Stable machine-readable diagnostic with code, rule, path, and message."""

    def __init__(self, code: str, rule_id: str, path: str, message: str) -> None:
        super().__init__(code=code, rule_id=rule_id, path=path, message=message)


def _add(
    out: list[Diagnostic], code: str, rule_id: str, path: str, message: str
) -> None:
    out.append(Diagnostic(code, rule_id, path, message))


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _fields(
    value: Any,
    *,
    path: str,
    required: set[str],
    allowed: set[str],
    rule_id: str,
    out: list[Diagnostic],
) -> bool:
    if not isinstance(value, dict):
        _add(out, "PROFILE-OBJECT-REQUIRED", rule_id, path, "must be an object")
        return False
    for field in sorted(required - value.keys()):
        _add(
            out, "PROFILE-FIELD-MISSING", rule_id, f"{path}.{field}",
            f"required field {field!r} is missing",
        )
    for field in sorted(value.keys() - allowed):
        _add(
            out, "PROFILE-FIELD-UNKNOWN", rule_id, f"{path}.{field}",
            f"unknown field {field!r} is not allowed",
        )
    return True


def _string_field(
    value: Any, field: str, path: str, rule_id: str, out: list[Diagnostic]
) -> None:
    if field in value and not _text(value[field]):
        _add(out, "PROFILE-STRING-INVALID", rule_id, f"{path}.{field}", "must be a non-empty string")


def _unique_strings(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(_text(item) for item in value)
        and len(value) == len(set(value))
    )


def validate_profile(profile: Any) -> list[Diagnostic]:
    """Validate the v1 profile shape and cross-field invariants."""
    out: list[Diagnostic] = []
    if not isinstance(profile, dict):
        _add(out, "PROFILE-OBJECT-REQUIRED", "PROFILE", "$", "profile root must be an object")
        return out
    if not _fields(
        profile, path="$", required=ROOT_FIELDS - {"supersedes"},
        allowed=ROOT_FIELDS, rule_id="PROFILE", out=out,
    ):
        return out

    if profile.get("schema_version") != "1":
        _add(out, "PROFILE-VERSION-UNSUPPORTED", "PROFILE", "$.schema_version", "must be the string '1'")
    profile_id = profile.get("profile_id")
    if not isinstance(profile_id, str) or not PROFILE_ID_RE.fullmatch(profile_id):
        _add(out, "PROFILE-ID-INVALID", "PROFILE", "$.profile_id", "must be a lowercase stable profile ID")
    profile_version = profile.get("profile_version")
    if not isinstance(profile_version, str) or not PROFILE_VERSION_RE.fullmatch(profile_version):
        _add(out, "PROFILE-SEMVER-INVALID", "PROFILE", "$.profile_version", "must be semantic version text X.Y.Z")
    _string_field(profile, "owner_ref", "$", "PROFILE", out)
    if "supersedes" in profile:
        _string_field(profile, "supersedes", "$", "PROFILE", out)

    adapter = profile.get("adapter")
    if _fields(
        adapter, path="$.adapter", required={"id", "version"},
        allowed={"id", "version"}, rule_id="PROFILE-ADAPTER", out=out,
    ):
        _string_field(adapter, "id", "$.adapter", "PROFILE-ADAPTER", out)
        _string_field(adapter, "version", "$.adapter", "PROFILE-ADAPTER", out)

    dimensions = profile.get("risk_dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        _add(out, "PROFILE-RISK-DIMENSIONS-INVALID", "PROFILE-RISK", "$.risk_dimensions", "must be a non-empty array")
    else:
        if not _unique_strings(dimensions):
            _add(out, "PROFILE-RISK-DIMENSIONS-DUPLICATE", "PROFILE-RISK", "$.risk_dimensions", "values must be non-empty and unique")
        for index, dimension in enumerate(dimensions):
            if not isinstance(dimension, str) or dimension not in RISK_DIMENSIONS:
                _add(out, "PROFILE-RISK-DIMENSION-UNKNOWN", "PROFILE-RISK", f"$.risk_dimensions[{index}]", "unsupported risk dimension")

    metric_rules = profile.get("metric_rules")
    seen_rule_ids: set[str] = set()
    if not isinstance(metric_rules, list) or not metric_rules:
        _add(out, "PROFILE-METRIC-RULES-INVALID", "PROFILE-METRICS", "$.metric_rules", "must be a non-empty array")
        metric_rules = []
    for index, rule in enumerate(metric_rules):
        path = f"$.metric_rules[{index}]"
        if not _fields(
            rule, path=path,
            required={"rule_id", "metric_id", "risk_tier", "required", "availability", "scope", "rationale"},
            allowed={"rule_id", "metric_id", "risk_tier", "required", "availability", "threshold", "scope", "rationale", "unavailable_reason"},
            rule_id="PROFILE-METRICS", out=out,
        ):
            continue
        rule_id = rule.get("rule_id")
        label = rule_id if isinstance(rule_id, str) and rule_id else f"PROFILE-METRIC-{index + 1}"
        if not isinstance(rule_id, str) or not RULE_ID_RE.fullmatch(rule_id):
            _add(out, "PROFILE-RULE-ID-INVALID", label, f"{path}.rule_id", "must be a stable uppercase rule ID")
        elif rule_id in seen_rule_ids:
            _add(out, "PROFILE-RULE-ID-DUPLICATE", label, f"{path}.rule_id", "rule IDs must be unique")
        else:
            seen_rule_ids.add(rule_id)
        _string_field(rule, "metric_id", path, label, out)
        if not isinstance(rule.get("risk_tier"), str) or rule.get("risk_tier") not in TIERS:
            _add(out, "PROFILE-RISK-TIER-INVALID", label, f"{path}.risk_tier", "must be low, medium, high, or critical")
        if type(rule.get("required")) is not bool:
            _add(out, "PROFILE-BOOLEAN-INVALID", label, f"{path}.required", "must be a boolean")
        availability = rule.get("availability")
        if not isinstance(availability, str) or availability not in {"supported", "unavailable"}:
            _add(out, "PROFILE-AVAILABILITY-INVALID", label, f"{path}.availability", "must be supported or unavailable")
        _string_field(rule, "rationale", path, label, out)

        scope = rule.get("scope")
        if _fields(
            scope, path=f"{path}.scope", required={"include", "exclude"},
            allowed={"include", "exclude"}, rule_id=label, out=out,
        ):
            includes, excludes = scope.get("include"), scope.get("exclude")
            if not isinstance(includes, list) or not includes or not all(_text(item) for item in includes):
                _add(out, "PROFILE-SCOPE-INVALID", label, f"{path}.scope.include", "must contain at least one non-empty glob")
            if not isinstance(excludes, list) or not all(_text(item) for item in excludes):
                _add(out, "PROFILE-SCOPE-INVALID", label, f"{path}.scope.exclude", "must be an array of non-empty globs")

        if availability == "supported":
            if "unavailable_reason" in rule:
                _add(out, "PROFILE-AVAILABILITY-CONFLICT", label, f"{path}.unavailable_reason", "supported metrics cannot declare an unavailable reason")
            threshold = rule.get("threshold")
            if _fields(
                threshold, path=f"{path}.threshold",
                required={"comparator", "value", "unit"},
                allowed={"comparator", "value", "unit"}, rule_id=label, out=out,
            ):
                if not isinstance(threshold.get("comparator"), str) or threshold.get("comparator") not in {"min", "max", "equals"}:
                    _add(out, "PROFILE-THRESHOLD-COMPARATOR-INVALID", label, f"{path}.threshold.comparator", "must be min, max, or equals")
                number = threshold.get("value")
                if type(number) not in {int, float} or not math.isfinite(number):
                    _add(out, "PROFILE-THRESHOLD-VALUE-INVALID", label, f"{path}.threshold.value", "must be a finite number")
                _string_field(threshold, "unit", f"{path}.threshold", label, out)
        elif availability == "unavailable":
            if "threshold" in rule:
                _add(out, "PROFILE-AVAILABILITY-CONFLICT", label, f"{path}.threshold", "unavailable metrics cannot declare a threshold")
            _string_field(rule, "unavailable_reason", path, label, out)

    path_rules = profile.get("path_rules")
    path_rule_patterns: dict[str, str] = {}
    if not isinstance(path_rules, list) or not path_rules:
        _add(out, "PROFILE-PATH-RULES-INVALID", "PROFILE-PATHS", "$.path_rules", "must be a non-empty array")
        path_rules = []
    for index, rule in enumerate(path_rules):
        path = f"$.path_rules[{index}]"
        if not _fields(
            rule, path=path, required={"pattern", "classification"},
            allowed={"pattern", "classification", "reason"}, rule_id="PROFILE-PATHS", out=out,
        ):
            continue
        pattern = rule.get("pattern")
        classification = rule.get("classification")
        if not _text(pattern):
            _add(out, "PROFILE-PATH-PATTERN-INVALID", "PROFILE-PATHS", f"{path}.pattern", "must be a non-empty glob")
        elif pattern in path_rule_patterns:
            _add(out, "PROFILE-PATH-PATTERN-DUPLICATE", "PROFILE-PATHS", f"{path}.pattern", "path patterns must be unique")
        else:
            path_rule_patterns[pattern] = classification if isinstance(classification, str) else ""
        if not isinstance(classification, str) or classification not in CLASSIFICATIONS:
            _add(out, "PROFILE-PATH-CLASSIFICATION-INVALID", "PROFILE-PATHS", f"{path}.classification", "unsupported classification")
        if "reason" in rule:
            _string_field(rule, "reason", path, "PROFILE-PATHS", out)

    floors = profile.get("escalation_floors")
    floor_keys: set[tuple[str, str]] = set()
    if not isinstance(floors, list):
        _add(out, "PROFILE-FLOORS-INVALID", "PROFILE-RISK", "$.escalation_floors", "must be an array")
        floors = []
    for index, floor in enumerate(floors):
        path = f"$.escalation_floors[{index}]"
        if not _fields(
            floor, path=path, required={"match_kind", "match", "minimum_tier"},
            allowed={"match_kind", "match", "minimum_tier"}, rule_id="PROFILE-RISK", out=out,
        ):
            continue
        kind, match, tier = floor.get("match_kind"), floor.get("match"), floor.get("minimum_tier")
        if not isinstance(kind, str) or kind not in {"path-pattern", "criterion-tag"}:
            _add(out, "PROFILE-FLOOR-KIND-INVALID", "PROFILE-RISK", f"{path}.match_kind", "must be path-pattern or criterion-tag")
        if not _text(match):
            _add(out, "PROFILE-FLOOR-MATCH-INVALID", "PROFILE-RISK", f"{path}.match", "must be a non-empty pattern or tag")
        if not isinstance(tier, str) or tier not in TIERS:
            _add(out, "PROFILE-FLOOR-TIER-INVALID", "PROFILE-RISK", f"{path}.minimum_tier", "must be low, medium, high, or critical")
        if isinstance(kind, str) and isinstance(match, str):
            key = (kind, match)
            if key in floor_keys:
                _add(out, "PROFILE-FLOOR-DUPLICATE", "PROFILE-RISK", f"{path}.match", "floor matches must be unique")
            floor_keys.add(key)

    floor_patterns = {
        floor.get("match") for floor in floors
        if isinstance(floor, dict)
        and floor.get("match_kind") == "path-pattern"
        and isinstance(floor.get("match"), str)
    }
    for pattern, classification in path_rule_patterns.items():
        if classification in SENSITIVE_CLASSIFICATIONS and pattern not in floor_patterns:
            _add(
                out, "PROFILE-SENSITIVE-FLOOR-MISSING", "PROFILE-RISK",
                "$.escalation_floors",
                f"sensitive path rule {pattern!r} requires an explicit path-pattern risk floor",
            )

    if profile.get("threshold_change_policy") != "reviewed-profile-revision-only":
        _add(out, "PROFILE-THRESHOLD-POLICY-INVALID", "PROFILE-THRESHOLDS", "$.threshold_change_policy", "must require reviewed profile revisions")
    return out


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(raw: bytes | str, *, label: str = "input") -> Any:
    try:
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        return json.loads(text, object_pairs_hook=_pairs_no_duplicates, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"invalid number {value}")))
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"cannot parse {label}: {exc}") from exc


def _safe_changed_path(path: Any) -> bool:
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        return False
    parsed = PurePosixPath(path)
    return (
        not parsed.is_absolute()
        and parsed.as_posix() == path
        and all(part not in {"", ".", ".."} for part in parsed.parts)
        and not re.match(r"^[A-Za-z]:", path)
    )


def resolve_risk(
    profile: Mapping[str, Any],
    *,
    changed_paths: Iterable[str],
    criterion_tags: Iterable[str] = (),
    declared_task_risk_tier: str,
    declared_criterion_risk_tiers: Iterable[str] = (),
) -> dict[str, Any]:
    """Resolve strictest declared and matching profile risk tier; never downgrade."""
    diagnostics: list[Diagnostic] = []
    if not isinstance(declared_task_risk_tier, str) or declared_task_risk_tier not in TIERS:
        _add(diagnostics, "TASK-RISK-TIER-INVALID", "PROFILE-RISK", "task.declared_risk_tier", "must be low, medium, high, or critical")
    tiers = [declared_task_risk_tier] if isinstance(declared_task_risk_tier, str) and declared_task_risk_tier in TIERS else []
    try:
        criterion_tiers = list(declared_criterion_risk_tiers)
    except TypeError:
        criterion_tiers = []
        _add(diagnostics, "CRITERION-RISK-TIERS-INVALID", "PROFILE-RISK", "task.criterion_risk_tiers", "must be an array of risk tiers")
    for index, tier in enumerate(criterion_tiers):
        if not isinstance(tier, str) or tier not in TIERS:
            _add(diagnostics, "CRITERION-RISK-TIER-INVALID", "PROFILE-RISK", f"task.criterion_risk_tiers[{index}]", "must be low, medium, high, or critical")
        else:
            tiers.append(tier)
    if isinstance(changed_paths, str):
        paths = []
        _add(diagnostics, "TASK-PATHS-INVALID", "PROFILE-RISK", "task.changed_paths", "must be an array of paths")
    else:
        try:
            paths = list(changed_paths)
        except TypeError:
            paths = []
            _add(diagnostics, "TASK-PATHS-INVALID", "PROFILE-RISK", "task.changed_paths", "must be an array of paths")
    if isinstance(criterion_tags, str):
        tags = []
        _add(diagnostics, "CRITERION-TAGS-INVALID", "PROFILE-RISK", "task.criterion_tags", "must be an array of tags")
    else:
        try:
            tags = list(criterion_tags)
        except TypeError:
            tags = []
            _add(diagnostics, "CRITERION-TAGS-INVALID", "PROFILE-RISK", "task.criterion_tags", "must be an array of tags")
    for index, path in enumerate(paths):
        if not _safe_changed_path(path):
            _add(diagnostics, "TASK-PATH-INVALID", "PROFILE-RISK", f"task.changed_paths[{index}]", "must be a canonical repository-relative POSIX path")
    for index, tag in enumerate(tags):
        if not _text(tag):
            _add(diagnostics, "CRITERION-TAG-INVALID", "PROFILE-RISK", f"task.criterion_tags[{index}]", "must be a non-empty string")
    declared_base_tier = max(tiers, key=TIERS.__getitem__) if tiers else None
    for floor_index, floor in enumerate(profile.get("escalation_floors", [])):
        if not isinstance(floor, dict) or not isinstance(floor.get("minimum_tier"), str) or floor.get("minimum_tier") not in TIERS:
            continue
        matched = False
        if floor.get("match_kind") == "path-pattern":
            matched = any(_safe_changed_path(path) and fnmatch.fnmatchcase(path, floor["match"]) for path in paths)
        elif floor.get("match_kind") == "criterion-tag":
            matched = floor.get("match") in tags
        if matched:
            tiers.append(floor["minimum_tier"])
            if declared_base_tier is not None and TIERS[declared_base_tier] < TIERS[floor["minimum_tier"]]:
                _add(
                    diagnostics, "RISK-FLOOR-DOWNGRADE", f"ESCALATION-FLOOR-{floor_index + 1}",
                    f"task.declared_risk_tier",
                    f"declared {declared_task_risk_tier} is below the {floor['minimum_tier']} floor for {floor.get('match')!r}",
                )
    effective = max(tiers, key=TIERS.__getitem__) if tiers else None
    return {"effective_risk_tier": effective, "diagnostics": diagnostics}


def evaluate_profile(
    profile: Any,
    *,
    changed_paths: Iterable[str],
    declared_task_risk_tier: str,
    criterion_tags: Iterable[str] = (),
    declared_criterion_risk_tiers: Iterable[str] = (),
    measurements: Mapping[str, Any] | None = None,
    task_overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate declared profile rules for one task scope without source mutation."""
    diagnostics = validate_profile(profile)
    if diagnostics:
        return {"state": "blocked", "effective_risk_tier": None, "metrics": [], "diagnostics": diagnostics}
    if task_overrides:
        _add(
            diagnostics, "TASK-OVERRIDE-UNSUPPORTED", "PROFILE-THRESHOLDS",
            "task.overrides",
            "task-level quality/threshold overrides are not permitted; revise the reviewed profile instead",
        )
    risk = resolve_risk(
        profile,
        changed_paths=changed_paths,
        criterion_tags=criterion_tags,
        declared_task_risk_tier=declared_task_risk_tier,
        declared_criterion_risk_tiers=declared_criterion_risk_tiers,
    )
    diagnostics.extend(risk["diagnostics"])
    effective = risk["effective_risk_tier"]
    if effective is None:
        return {"state": "blocked", "effective_risk_tier": None, "metrics": [], "diagnostics": diagnostics}

    supplied = measurements if measurements is not None else {}
    if not isinstance(supplied, Mapping):
        _add(diagnostics, "MEASUREMENTS-INVALID", "PROFILE-METRICS", "measurements", "must be an object keyed by metric ID")
        supplied = {}
    metric_results: list[dict[str, Any]] = []
    blocked = bool(diagnostics)
    failed = False
    for index, rule in enumerate(profile["metric_rules"]):
        if TIERS[rule["risk_tier"]] > TIERS[effective]:
            continue
        rule_id = rule["rule_id"]
        metric_id = rule["metric_id"]
        item = {"rule_id": rule_id, "metric_id": metric_id, "scope": rule["scope"], "state": "not-applicable"}
        if rule["availability"] == "unavailable":
            item["state"] = "unavailable"
            if rule["required"]:
                _add(
                    diagnostics, "REQUIRED-METRIC-UNAVAILABLE", rule_id,
                    f"metric_rules[{index}].availability",
                    f"required metric {metric_id!r} is unavailable and cannot pass",
                )
                blocked = True
            metric_results.append(item)
            continue
        observation = supplied.get(metric_id)
        if observation is None:
            item["state"] = "missing"
            if rule["required"]:
                _add(
                    diagnostics, "REQUIRED-METRIC-MISSING", rule_id,
                    f"measurements.{metric_id}",
                    f"required metric {metric_id!r} has no observation",
                )
                blocked = True
            metric_results.append(item)
            continue
        if isinstance(observation, Mapping):
            observed_state = observation.get("state", "pass")
            observed_value = observation.get("value")
            if observed_state != "pass":
                item["state"] = str(observed_state)
                if rule["required"]:
                    _add(
                        diagnostics, "REQUIRED-METRIC-NONPASS", rule_id,
                        f"measurements.{metric_id}.state",
                        f"required metric {metric_id!r} is {observed_state!r}, not pass",
                    )
                    blocked = True
                metric_results.append(item)
                continue
        else:
            observed_value = observation
        if type(observed_value) not in {int, float} or not math.isfinite(observed_value):
            item["state"] = "invalid"
            _add(diagnostics, "METRIC-VALUE-INVALID", rule_id, f"measurements.{metric_id}.value", "must be a finite numeric value")
            blocked = blocked or rule["required"]
            metric_results.append(item)
            continue
        threshold = rule["threshold"]
        comparator = threshold["comparator"]
        target = threshold["value"]
        passed = (
            observed_value >= target if comparator == "min"
            else observed_value <= target if comparator == "max"
            else observed_value == target
        )
        item.update(state="pass" if passed else "fail", value=observed_value)
        if not passed:
            code = "METRIC-THRESHOLD-FAILED" if rule["required"] else "OPTIONAL-METRIC-THRESHOLD-FAILED"
            _add(
                diagnostics, code, rule_id,
                f"measurements.{metric_id}.value",
                f"{observed_value} does not satisfy {comparator} {target} {threshold['unit']}",
            )
            failed = failed or rule["required"]
        metric_results.append(item)

    state = "blocked" if blocked else "fail" if failed else "pass"
    return {
        "state": state,
        "effective_risk_tier": effective,
        "metrics": metric_results,
        "diagnostics": diagnostics,
    }


def _policy_view(profile: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "metric_rules": profile.get("metric_rules"),
        "path_rules": profile.get("path_rules"),
        "escalation_floors": profile.get("escalation_floors"),
    }


def validate_profile_revision(
    previous_raw: bytes,
    candidate_raw: bytes,
    *,
    review_ref: str | None,
    reviewed_profile_sha256: str | None,
) -> list[Diagnostic]:
    """Require a new, linked, digest-bound reviewed revision for policy changes."""
    diagnostics: list[Diagnostic] = []
    try:
        previous = parse_json(previous_raw, label="previous profile")
        candidate = parse_json(candidate_raw, label="candidate profile")
    except ValueError as exc:
        _add(diagnostics, "PROFILE-JSON-INVALID", "PROFILE-REVISION", "$", str(exc))
        return diagnostics
    diagnostics.extend(validate_profile(previous))
    diagnostics.extend(validate_profile(candidate))
    if diagnostics:
        return diagnostics
    if previous["profile_id"] != candidate["profile_id"]:
        _add(diagnostics, "PROFILE-ID-CHANGED", "PROFILE-REVISION", "$.profile_id", "profile updates must retain the same profile_id")
        return diagnostics
    if _policy_view(previous) == _policy_view(candidate):
        return diagnostics
    old_version = tuple(int(part) for part in previous["profile_version"].split("."))
    new_version = tuple(int(part) for part in candidate["profile_version"].split("."))
    if new_version <= old_version:
        _add(diagnostics, "PROFILE-REVISION-NOT-ADVANCED", "PROFILE-REVISION", "$.profile_version", "policy changes require a higher semantic profile version")
    expected_supersedes = f"{previous['profile_id']}@{previous['profile_version']}"
    if candidate.get("supersedes") != expected_supersedes:
        _add(diagnostics, "PROFILE-SUPERSESSION-MISSING", "PROFILE-REVISION", "$.supersedes", f"must identify {expected_supersedes!r}")
    if not _text(review_ref):
        _add(diagnostics, "PROFILE-REVISION-REVIEW-REQUIRED", "PROFILE-REVISION", "review_ref", "policy changes require a durable review reference")
    candidate_digest = hashlib.sha256(candidate_raw).hexdigest()
    if reviewed_profile_sha256 != candidate_digest:
        _add(
            diagnostics, "PROFILE-REVISION-DIGEST-MISMATCH", "PROFILE-REVISION",
            "reviewed_profile_sha256",
            "review evidence must bind the exact candidate profile bytes",
        )
    return diagnostics


def _load_file(path: str) -> tuple[bytes, Any]:
    raw = open(path, "rb").read()
    return raw, parse_json(raw, label=path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate_parser = commands.add_parser("validate", help="validate one quality profile")
    validate_parser.add_argument("profile")
    assess_parser = commands.add_parser("assess", help="assess task risk and profile metrics")
    assess_parser.add_argument("profile")
    assess_parser.add_argument("--risk-tier", required=True, choices=tuple(TIERS))
    assess_parser.add_argument("--path", action="append", default=[])
    assess_parser.add_argument("--criterion-tag", action="append", default=[])
    assess_parser.add_argument("--criterion-risk-tier", action="append", default=[])
    assess_parser.add_argument("--measurements", help="JSON object file keyed by metric ID")
    assess_parser.add_argument("--task-overrides", help="JSON object file; quality overrides are rejected")
    transition_parser = commands.add_parser("check-transition", help="check a reviewed profile policy revision")
    transition_parser.add_argument("previous")
    transition_parser.add_argument("candidate")
    transition_parser.add_argument("--review-ref")
    transition_parser.add_argument("--reviewed-profile-sha256")

    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            _, profile = _load_file(args.profile)
            diagnostics = validate_profile(profile)
            result = {"state": "fail" if diagnostics else "pass", "diagnostics": diagnostics}
        elif args.command == "assess":
            _, profile = _load_file(args.profile)
            measurements = _load_file(args.measurements)[1] if args.measurements else {}
            overrides = _load_file(args.task_overrides)[1] if args.task_overrides else {}
            result = evaluate_profile(
                profile, changed_paths=args.path, criterion_tags=args.criterion_tag,
                declared_task_risk_tier=args.risk_tier,
                declared_criterion_risk_tiers=args.criterion_risk_tier,
                measurements=measurements, task_overrides=overrides,
            )
        else:
            previous_raw = open(args.previous, "rb").read()
            candidate_raw = open(args.candidate, "rb").read()
            diagnostics = validate_profile_revision(
                previous_raw, candidate_raw, review_ref=args.review_ref,
                reviewed_profile_sha256=args.reviewed_profile_sha256,
            )
            result = {"state": "fail" if diagnostics else "pass", "diagnostics": diagnostics}
    except (OSError, ValueError) as exc:
        result = {
            "state": "blocked",
            "diagnostics": [Diagnostic("PROFILE-INPUT-INVALID", "PROFILE", "$", str(exc))],
        }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("state") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
