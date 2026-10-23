#!/usr/bin/env python3
"""Design-time semantic checks for FW-013 schemas; not a production runner."""

from __future__ import annotations

import json
import hashlib
import copy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "docs" / "framework" / "schemas"
SCHEMA_FILES = {
    "profile": "profile-manifest-v1.schema.json",
    "selection": "profile-selection-manifest-v1.schema.json",
    "result": "profile-check-result-v1.schema.json",
}


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def strict_json(text: str) -> Any:
    return json.loads(text, object_pairs_hook=strict_pairs)


def read_schema(name: str) -> dict[str, Any]:
    return strict_json((SCHEMA_DIR / SCHEMA_FILES[name]).read_text(encoding="utf-8"))


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validator(name: str) -> Draft202012Validator:
    schema = read_schema(name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def expect_valid(v: Draft202012Validator, instance: Any, label: str) -> None:
    errors = sorted(v.iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        raise AssertionError(f"{label} should validate: {errors[0].message}")
    print(f"PASS {label}")


def expect_invalid(v: Draft202012Validator, instance: Any, label: str) -> None:
    errors = list(v.iter_errors(instance))
    if not errors:
        raise AssertionError(f"{label} unexpectedly validated")
    print(f"PASS {label} rejected")


def profile_fixture() -> dict[str, Any]:
    return {
        "schema_version": "1",
        "profile_id": "sample-next-ts",
        "profile_version": "0.1.0",
        "language": {"name": "TypeScript", "version_range": "5.9.x"},
        "runtime": {"name": "Node.js", "version_range": "22.x"},
        "prerequisites": {
            "node": {"required": True, "version_constraint": ">=22"},
            "browser": {"required": False, "version_constraint": "not-applicable"},
        },
        "source_layout": ["src/"],
        "checks": {
            "typecheck": {
                "status": "applicable",
                "required": True,
                "command": "npm run typecheck",
                "scope": "generated profile source",
            },
            "browser-run": {
                "status": "unsupported",
                "required": False,
                "reason": "No browser/device execution is part of this synthetic profile contract.",
            },
            "integration-run": {
                "status": "applicable",
                "required": False,
                "command": "npm run integration",
                "scope": "generated profile integration fixtures",
            },
        },
        "owned_dependencies": [
            {"name": "typescript", "version_constraint": "5.9.x", "purpose": "type checking"}
        ],
        "generated_files": ["package.json", "tsconfig.json"],
    }


def selection_fixture(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "framework_revision": "a" * 40,
        "core_contract_version": "1.0.0",
        "selected_profiles": {
            "sample-next-ts": {
                "profile_version": profile["profile_version"],
                "manifest_sha256": canonical_digest(profile),
            }
        },
        "generated_files": {
            ".sdd/mission.md": {"sha256": "c" * 64, "owner": {"kind": "core"}},
            "package.json": {
                "sha256": "d" * 64,
                "owner": {"kind": "profile", "profile_id": "sample-next-ts"},
            },
        },
        "prerequisites": {
            "sample-next-ts/node": {
                "required": True,
                "state": "available",
                "observed_version": "22.23.3",
            },
            "sample-next-ts/browser": {
                "required": False,
                "state": "not-checked",
                "reason": "Optional browser runtime is not part of profile initialization.",
            },
        },
        "profile_checks": {
            "sample-next-ts": {
                "typecheck": {
                    "status": "applicable",
                    "required": True,
                    "command": "npm run typecheck",
                    "scope": "generated profile source",
                },
                "browser-run": {
                    "status": "unsupported",
                    "required": False,
                    "reason": "No browser/device execution is part of this synthetic profile contract.",
                },
                "integration-run": {
                    "status": "applicable",
                    "required": False,
                    "command": "npm run integration",
                    "scope": "generated profile integration fixtures",
                },
            }
        },
    }


def result_fixture(selection: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "framework_revision": "a" * 40,
        "selection_manifest_sha256": canonical_digest(selection),
        "selected_profiles": selection["selected_profiles"],
        "check_results": {
            "sample-next-ts": {
                "typecheck": {"state": "passed", "command": "npm run typecheck", "exit_code": 0},
                "browser-run": {
                    "state": "unsupported",
                    "reason": "The selected profile declares this check unsupported.",
                },
                "integration-run": {"state": "not-run", "reason": "This design-time fixture does not execute app integration."},
            }
        },
    }


def cross_record_problems(
    profile: dict[str, Any], selection: dict[str, Any], result: dict[str, Any]
) -> list[str]:
    problems: list[str] = []
    selected = selection["selected_profiles"]
    result_profiles = result["selected_profiles"]
    if result_profiles != selected:
        problems.append("check result selected profiles differ from the frozen selection manifest")
    if set(result["check_results"]) != set(selected):
        problems.append("check result profile set differs from the frozen selection manifest")
    if result["framework_revision"] != selection["framework_revision"]:
        problems.append("check result framework revision differs from the frozen selection manifest")
    if profile["profile_id"] not in selected:
        problems.append("profile declaration is absent from selected profiles")
    if profile["profile_id"] in selected and selected[profile["profile_id"]]["manifest_sha256"] != canonical_digest(profile):
        problems.append("selection manifest profile digest does not match the profile declaration")
    if result["selection_manifest_sha256"] != canonical_digest(selection):
        problems.append("check result is not bound to the exact selection manifest")
    declared = profile["checks"]
    if set(selection["profile_checks"]) != set(selected) or selection["profile_checks"].get(profile["profile_id"]) != declared:
        problems.append("selection-manifest check declarations differ from the frozen profile declaration")
    for owner in selection["generated_files"].values():
        if owner["owner"]["kind"] == "profile" and owner["owner"]["profile_id"] not in selected:
            problems.append("generated file is owned by a profile that was not selected")
    for key, observation in selection["prerequisites"].items():
        profile_id, prerequisite_name = key.split("/", 1)
        if profile_id not in selected:
            problems.append("prerequisite belongs to an unselected profile")
        prereq = profile["prerequisites"].get(prerequisite_name)
        if prereq is None:
            problems.append("prerequisite is absent from the selected profile declaration")
        elif observation["required"] != prereq["required"]:
            problems.append("prerequisite requiredness differs from its frozen profile declaration")
    for profile_id, checks in result["check_results"].items():
        if profile_id not in selected:
            problems.append("check result belongs to an unselected profile")
            continue
        for check_id, outcome in checks.items():
            declaration = declared.get(check_id)
            if declaration is None:
                problems.append("check result has no matching profile declaration")
            else:
                if declaration["status"] == "unsupported" and outcome.get("state") != "unsupported":
                    problems.append("unsupported profile check is not reported as unsupported")
                if declaration["status"] == "applicable" and outcome.get("state") == "unsupported":
                    problems.append("applicable profile check is misreported as unsupported")
                if outcome.get("state") in {"passed", "failed"} and outcome.get("command") != declaration.get("command"):
                    problems.append("check command differs from the frozen profile declaration")
    if set(result["check_results"].get(profile["profile_id"], {})) != set(declared):
        problems.append("check result omits or adds a declared profile check")
    return problems


def profile_ready(profile: dict[str, Any], selection: dict[str, Any], result: dict[str, Any]) -> bool:
    profile_id = profile["profile_id"]
    if profile_id not in selection["selected_profiles"]:
        return False
    observed_prerequisites = selection["prerequisites"]
    for name, declaration in profile["prerequisites"].items():
        observed = observed_prerequisites.get(f"{profile_id}/{name}")
        if declaration["required"] and (observed is None or observed["state"] != "available"):
            return False
    observed_checks = result["check_results"].get(profile_id, {})
    for check_id, declaration in profile["checks"].items():
        if not declaration["required"]:
            continue
        observed = observed_checks.get(check_id)
        if declaration["status"] != "applicable" or observed is None or observed["state"] != "passed":
            return False
        if observed.get("command") != declaration["command"] or observed.get("exit_code") != 0:
            return False
    return True


def selection_readiness(profiles: dict[str, dict[str, Any]], selection: dict[str, Any], result: dict[str, Any]) -> str:
    selected_ids = set(selection["selected_profiles"])
    if not selected_ids:
        return "core-only"
    if selected_ids != set(profiles) or result["selected_profiles"] != selection["selected_profiles"]:
        return "blocked"
    if any(cross_record_problems(profiles[profile_id], selection, result) for profile_id in selected_ids):
        return "blocked"
    return "ready" if all(profile_ready(profiles[profile_id], selection, result) for profile_id in selected_ids) else "blocked"


def main() -> None:
    profile_validator = validator("profile")
    selection_validator = validator("selection")
    result_validator = validator("result")
    print("PASS all three schemas are valid Draft 2020-12 schemas")

    profile = profile_fixture()
    selection = selection_fixture(profile)
    result = result_fixture(selection)
    expect_valid(profile_validator, profile, "profile-applicable-and-unsupported-checks")
    expect_valid(selection_validator, selection, "selection-manifest-profile-and-core-files")
    core_only = {**selection, "selected_profiles": {}, "generated_files": {}, "prerequisites": {}, "profile_checks": {}}
    expect_valid(selection_validator, core_only, "selection-manifest-core-only")
    expect_valid(result_validator, result, "check-result-passed-and-unsupported")

    invalid_profile = profile_fixture()
    invalid_profile["checks"]["typecheck"].pop("command")
    expect_invalid(profile_validator, invalid_profile, "applicable-check-missing-command")
    invalid_profile = profile_fixture()
    invalid_profile["checks"]["browser-run"]["command"] = "npm test"
    expect_invalid(profile_validator, invalid_profile, "unsupported-check-cannot-have-command")

    invalid_selection = selection_fixture(profile)
    invalid_selection["generated_files"]["../outside.txt"] = {"sha256": "f" * 64, "owner": {"kind": "core"}}
    expect_invalid(selection_validator, invalid_selection, "selection-path-traversal")
    invalid_selection = selection_fixture(profile)
    invalid_selection["prerequisites"]["sample-next-ts/node"] = {"required": True, "state": "available"}
    expect_invalid(selection_validator, invalid_selection, "available-prerequisite-missing-observed-version")
    invalid_selection = selection_fixture(profile)
    invalid_selection["profile_checks"]["sample-next-ts"]["browser-run"]["command"] = "npm test"
    expect_invalid(selection_validator, invalid_selection, "unsupported-profile-check-with-command")

    invalid_result = result_fixture(selection)
    invalid_result["check_results"]["sample-next-ts"]["typecheck"]["exit_code"] = 1
    expect_invalid(result_validator, invalid_result, "passed-result-with-nonzero-exit")
    invalid_result = result_fixture(selection)
    invalid_result["check_results"]["sample-next-ts"]["browser-run"]["exit_code"] = 0
    expect_invalid(result_validator, invalid_result, "unsupported-result-cannot-have-exit-code")
    try:
        strict_json('{"checks":{"typecheck":1,"typecheck":2}}')
    except ValueError:
        print("PASS duplicate raw JSON keys rejected before schema validation")
    else:
        raise AssertionError("duplicate raw JSON keys were accepted")

    problems = cross_record_problems(profile, selection, result)
    if problems:
        raise AssertionError("valid cross-record fixture rejected: " + "; ".join(problems))
    print("PASS cross-record selection, ownership, command, and profile identity bindings")
    tampered_selection = copy.deepcopy(selection)
    tampered_selection["selected_profiles"]["sample-next-ts"]["manifest_sha256"] = "f" * 64
    tampered_result = result_fixture(tampered_selection)
    if not cross_record_problems(profile, tampered_selection, tampered_result):
        raise AssertionError("mismatched profile digest was accepted")
    print("PASS profile digest drift rejected by cross-record binding")
    if selection_readiness({profile["profile_id"]: profile}, selection, result) != "ready":
        raise AssertionError("complete required profile evidence should aggregate to ready")
    print("PASS all required checks passed and required prerequisites available => ready")

    required_unsupported = profile_fixture()
    required_unsupported["checks"]["browser-run"]["required"] = True
    unsupported_selection = selection_fixture(required_unsupported)
    unsupported_result = result_fixture(unsupported_selection)
    if selection_readiness({required_unsupported["profile_id"]: required_unsupported}, unsupported_selection, unsupported_result) != "blocked":
        raise AssertionError("required unsupported check was counted as ready")
    print("PASS required unsupported check => blocked")
    incomplete_result = {**result, "check_results": {"sample-next-ts": {"browser-run": result["check_results"]["sample-next-ts"]["browser-run"]}}}
    if selection_readiness({profile["profile_id"]: profile}, selection, incomplete_result) != "blocked":
        raise AssertionError("missing required check result was counted as ready")
    print("PASS missing required check result => blocked")
    missing_prerequisite = selection_fixture(profile)
    missing_prerequisite["prerequisites"]["sample-next-ts/node"] = {
        "required": True,
        "state": "missing",
        "reason": "No required Node.js runtime is available.",
    }
    missing_prerequisite_result = {**result, "selection_manifest_sha256": canonical_digest(missing_prerequisite)}
    if selection_readiness({profile["profile_id"]: profile}, missing_prerequisite, missing_prerequisite_result) != "blocked":
        raise AssertionError("missing required prerequisite was counted as ready")
    print("PASS missing required prerequisite => blocked")
    if selection_readiness({}, core_only, {**result, "selected_profiles": {}}) != "core-only":
        raise AssertionError("empty profile selection was not reported as core-only")
    print("PASS empty profile selection => core-only; no profile support claim")
    print("Architecture contract fixtures completed; no initializer/profile support is claimed.")


if __name__ == "__main__":
    main()
