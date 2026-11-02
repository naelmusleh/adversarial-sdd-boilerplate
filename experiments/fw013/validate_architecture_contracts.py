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
    "core": "core-file-manifest-v1.schema.json",
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


def core_fixture() -> dict[str, Any]:
    return {
        "schema_version": "1",
        "core_contract_version": "1.0.0",
        "files": {".sdd/mission.md": {"source_sha256": "e" * 64}},
    }


def selection_fixture(profiles: dict[str, dict[str, Any]], core: dict[str, Any]) -> dict[str, Any]:
    selected_profiles = {
        profile_id: {
            "profile_version": profile["profile_version"],
            "manifest_sha256": canonical_digest(profile),
        }
        for profile_id, profile in profiles.items()
    }
    generated_files = {
        path: {"sha256": "c" * 64, "owner": {"kind": "core"}}
        for path in core["files"]
    }
    prerequisites: dict[str, dict[str, Any]] = {}
    for profile_id, profile in profiles.items():
        for path in profile["generated_files"]:
            generated_files[path] = {
                "sha256": hashlib.sha256(f"{profile_id}:{path}".encode("utf-8")).hexdigest(),
                "owner": {"kind": "profile", "profile_id": profile_id},
            }
        for name, declaration in profile["prerequisites"].items():
            key = f"{profile_id}/{name}"
            if declaration["required"]:
                prerequisites[key] = {"required": True, "state": "available", "observed_version": "1.0.0"}
            else:
                prerequisites[key] = {"required": False, "state": "not-checked", "reason": "Optional fixture prerequisite."}
    return {
        "schema_version": "1",
        "framework_revision": "a" * 40,
        "core_contract_version": "1.0.0",
        "core_manifest_sha256": canonical_digest(core),
        "selected_profiles": selected_profiles,
        "generated_files": generated_files,
        "prerequisites": prerequisites,
        "profile_checks": {profile_id: copy.deepcopy(profile["checks"]) for profile_id, profile in profiles.items()},
    }


def core_only_selection_fixture(core: dict[str, Any]) -> dict[str, Any]:
    return selection_fixture({}, core)


def result_fixture(selection: dict[str, Any]) -> dict[str, Any]:
    check_results: dict[str, dict[str, Any]] = {}
    for profile_id, checks in selection["profile_checks"].items():
        check_results[profile_id] = {}
        for check_id, declaration in checks.items():
            if declaration["status"] == "unsupported":
                check_results[profile_id][check_id] = {"state": "unsupported", "reason": "Declared unsupported by the selected profile."}
            elif declaration["required"]:
                check_results[profile_id][check_id] = {"state": "passed", "command": declaration["command"], "exit_code": 0}
            else:
                check_results[profile_id][check_id] = {"state": "not-run", "reason": "Optional fixture check was not executed."}
    return {
        "schema_version": "1",
        "framework_revision": "a" * 40,
        "selection_manifest_sha256": canonical_digest(selection),
        "selected_profiles": copy.deepcopy(selection["selected_profiles"]),
        "check_results": check_results,
    }


def cross_record_problems(
    profiles: dict[str, dict[str, Any]], core: dict[str, Any], selection: dict[str, Any], result: dict[str, Any]
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
    if selection["core_contract_version"] != core["core_contract_version"]:
        problems.append("selection core contract version differs from the authoritative core inventory")
    if selection["core_manifest_sha256"] != canonical_digest(core):
        problems.append("selection core inventory digest does not match the authoritative core manifest")
    if set(selected) != set(profiles):
        problems.append("selected profile IDs differ from the supplied profile declarations")
    for profile_id, profile in profiles.items():
        entry = selected.get(profile_id)
        if entry is None:
            problems.append("profile declaration is absent from selected profiles")
            continue
        if entry["profile_version"] != profile["profile_version"]:
            problems.append("selection profile version differs from the selected profile declaration")
        if entry["manifest_sha256"] != canonical_digest(profile):
            problems.append("selection manifest profile digest does not match the profile declaration")
    if result["selection_manifest_sha256"] != canonical_digest(selection):
        problems.append("check result is not bound to the exact selection manifest")
    selection_checks_by_profile = selection["profile_checks"]
    if set(selection_checks_by_profile) != set(selected):
        problems.append("selection-manifest profile check declaration set differs from selected profiles")
    for profile_id, profile in profiles.items():
        checks_for_profile = selection_checks_by_profile.get(profile_id)
        if checks_for_profile != profile["checks"]:
            problems.append("selection-manifest check declarations differ from the frozen profile declaration")

    core_paths = {path for path, entry in selection["generated_files"].items() if entry["owner"]["kind"] == "core"}
    if core_paths != set(core["files"]):
        problems.append("generated core path inventory differs from the authoritative core file manifest")
    for profile_id, profile in profiles.items():
        expected_paths = set(profile["generated_files"])
        actual_paths = {
            path for path, entry in selection["generated_files"].items()
            if entry["owner"]["kind"] == "profile" and entry["owner"]["profile_id"] == profile_id
        }
        if actual_paths != expected_paths:
            problems.append("generated profile path inventory differs from its declared profile file inventory")
    for path, entry in selection["generated_files"].items():
        owner = entry["owner"]
        if owner["kind"] == "profile" and owner["profile_id"] not in selected:
            problems.append("generated file is owned by a profile that was not selected")
    for key, observation in selection["prerequisites"].items():
        profile_id, prerequisite_name = key.split("/", 1)
        if profile_id not in selected:
            problems.append("prerequisite belongs to an unselected profile")
        profile = profiles.get(profile_id)
        prereq = profile["prerequisites"].get(prerequisite_name) if profile else None
        if prereq is None:
            problems.append("prerequisite is absent from the selected profile declaration")
        elif observation["required"] != prereq["required"]:
            problems.append("prerequisite requiredness differs from its frozen profile declaration")
    expected_prerequisites = {
        f"{profile_id}/{name}"
        for profile_id, profile in profiles.items()
        for name in profile["prerequisites"]
    }
    if set(selection["prerequisites"]) != expected_prerequisites:
        problems.append("selection prerequisite inventory differs from selected profile declarations")
    if set(result["check_results"]) != set(selected):
        problems.append("check-result profile inventory differs from selected profiles")
    for profile_id, checks in result["check_results"].items():
        profile = profiles.get(profile_id)
        if profile is None:
            problems.append("check result belongs to an undeclared or unselected profile")
            continue
        declared = profile["checks"]
        for check_id, outcome in checks.items():
            declaration = declared.get(check_id)
            if declaration is None:
                problems.append("check result has no matching profile declaration")
            else:
                if declaration["status"] == "unsupported" and outcome.get("state") != "unsupported":
                    problems.append("unsupported profile check is not reported as unsupported")
                if declaration["status"] == "applicable" and outcome.get("state") == "unsupported":
                    problems.append("applicable profile check is misreported as unsupported")
                if "command" in outcome and outcome.get("command") != declaration.get("command"):
                    problems.append("check command differs from the frozen profile declaration")
    for profile_id, profile in profiles.items():
        if set(result["check_results"].get(profile_id, {})) != set(profile["checks"]):
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


def selection_readiness(profiles: dict[str, dict[str, Any]], core: dict[str, Any], selection: dict[str, Any], result: dict[str, Any]) -> str:
    selected_ids = set(selection["selected_profiles"])
    if not selected_ids:
        return "core-only" if not cross_record_problems({}, core, selection, result) else "blocked"
    if any(cross_record_problems(profiles, core, selection, result)):
        return "blocked"
    return "ready" if all(profile_ready(profiles[profile_id], selection, result) for profile_id in selected_ids) else "blocked"


def main() -> None:
    core_validator = validator("core")
    profile_validator = validator("profile")
    selection_validator = validator("selection")
    result_validator = validator("result")
    print("PASS all four schemas are valid Draft 2020-12 schemas")

    core = core_fixture()
    profile = profile_fixture()
    selection = selection_fixture({profile["profile_id"]: profile}, core)
    result = result_fixture(selection)
    expect_valid(core_validator, core, "authoritative-core-file-inventory")
    expect_valid(profile_validator, profile, "profile-applicable-and-unsupported-checks")
    expect_valid(selection_validator, selection, "selection-manifest-profile-and-core-files")
    core_only = core_only_selection_fixture(core)
    core_only_result = {
        "schema_version": "1",
        "framework_revision": core_only["framework_revision"],
        "selection_manifest_sha256": canonical_digest(core_only),
        "selected_profiles": {},
        "check_results": {},
    }
    expect_valid(selection_validator, core_only, "selection-manifest-core-only")
    expect_valid(result_validator, result, "check-result-passed-and-unsupported")
    expect_valid(result_validator, core_only_result, "check-result-core-only")

    invalid_core = copy.deepcopy(core)
    invalid_core["files"]["../outside.txt"] = {"source_sha256": "f" * 64}
    expect_invalid(core_validator, invalid_core, "core-inventory-path-traversal")

    invalid_profile = profile_fixture()
    invalid_profile["checks"]["typecheck"].pop("command")
    expect_invalid(profile_validator, invalid_profile, "applicable-check-missing-command")
    invalid_profile = profile_fixture()
    invalid_profile["checks"]["browser-run"]["command"] = "npm test"
    expect_invalid(profile_validator, invalid_profile, "unsupported-check-cannot-have-command")

    invalid_selection = selection_fixture({profile["profile_id"]: profile}, core)
    invalid_selection["generated_files"]["../outside.txt"] = {"sha256": "f" * 64, "owner": {"kind": "core"}}
    expect_invalid(selection_validator, invalid_selection, "selection-path-traversal")
    invalid_selection = selection_fixture({profile["profile_id"]: profile}, core)
    invalid_selection["prerequisites"]["sample-next-ts/node"] = {"required": True, "state": "available"}
    expect_invalid(selection_validator, invalid_selection, "available-prerequisite-missing-observed-version")
    invalid_selection = selection_fixture({profile["profile_id"]: profile}, core)
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

    profiles = {profile["profile_id"]: profile}
    problems = cross_record_problems(profiles, core, selection, result)
    if problems:
        raise AssertionError("valid cross-record fixture rejected: " + "; ".join(problems))
    print("PASS cross-record selection, ownership, command, and profile identity bindings")
    tampered_selection = copy.deepcopy(selection)
    tampered_selection["selected_profiles"]["sample-next-ts"]["manifest_sha256"] = "f" * 64
    tampered_result = result_fixture(tampered_selection)
    if not cross_record_problems(profiles, core, tampered_selection, tampered_result):
        raise AssertionError("mismatched profile digest was accepted")
    print("PASS profile digest drift rejected by cross-record binding")
    wrong_version = copy.deepcopy(selection)
    wrong_version["selected_profiles"][profile["profile_id"]]["profile_version"] = "9.9.9"
    if not cross_record_problems(profiles, core, wrong_version, result_fixture(wrong_version)):
        raise AssertionError("selected profile version drift was accepted")
    print("PASS selected profile version must match the digested declaration")
    wrong_profile_inventory = copy.deepcopy(selection)
    wrong_profile_inventory["generated_files"]["package.json"]["owner"]["profile_id"] = "other-profile"
    if not cross_record_problems(profiles, core, wrong_profile_inventory, result_fixture(wrong_profile_inventory)):
        raise AssertionError("undeclared generated-file ownership was accepted")
    print("PASS profile-generated path ownership must match its declared inventory")
    wrong_core_inventory = copy.deepcopy(selection)
    wrong_core_inventory["generated_files"].pop(".sdd/mission.md")
    if not cross_record_problems(profiles, core, wrong_core_inventory, result_fixture(wrong_core_inventory)):
        raise AssertionError("missing authoritative core path was accepted")
    print("PASS generated core paths must match authoritative core inventory")
    if selection_readiness(profiles, core, selection, result) != "ready":
        raise AssertionError("complete required profile evidence should aggregate to ready")
    print("PASS all required checks passed and required prerequisites available => ready")

    second_profile = copy.deepcopy(profile)
    second_profile.update({
        "profile_id": "sample-fastapi",
        "profile_version": "0.2.0",
        "language": {"name": "Python", "version_range": "3.13.x"},
        "runtime": {"name": "FastAPI", "version_range": "0.157.x"},
        "prerequisites": {"python": {"required": True, "version_constraint": ">=3.13"}},
        "source_layout": ["api/"],
        "checks": {
            "unit-tests": {
                "status": "applicable", "required": True,
                "command": "python -m pytest", "scope": "generated API contract fixtures",
            }
        },
        "owned_dependencies": [{"name": "fastapi", "version_constraint": "0.157.x", "purpose": "synthetic service profile"}],
        "generated_files": ["requirements.txt"],
    })
    multiple_profiles = {profile["profile_id"]: profile, second_profile["profile_id"]: second_profile}
    multi_selection = selection_fixture(multiple_profiles, core)
    multi_result = result_fixture(multi_selection)
    expect_valid(selection_validator, multi_selection, "selection-manifest-two-profiles")
    expect_valid(result_validator, multi_result, "check-result-two-profiles")
    if cross_record_problems(multiple_profiles, core, multi_selection, multi_result):
        raise AssertionError("valid multi-profile fixture rejected: " + "; ".join(cross_record_problems(multiple_profiles, core, multi_selection, multi_result)))
    if selection_readiness(multiple_profiles, core, multi_selection, multi_result) != "ready":
        raise AssertionError("valid multi-profile selection should aggregate to ready")
    print("PASS multi-profile declarations and required checks aggregate independently to ready")
    mismatched_multi_selection = copy.deepcopy(multi_selection)
    mismatched_multi_selection["profile_checks"]["sample-fastapi"]["unit-tests"]["command"] = "python -m unittest"
    if not cross_record_problems(multiple_profiles, core, mismatched_multi_selection, result_fixture(mismatched_multi_selection)):
        raise AssertionError("mismatched second profile declaration was accepted")
    print("PASS mismatch in one selected profile is rejected without conflating profile declarations")

    required_unsupported = profile_fixture()
    required_unsupported["checks"]["browser-run"]["required"] = True
    unsupported_selection = selection_fixture({required_unsupported["profile_id"]: required_unsupported}, core)
    unsupported_result = result_fixture(unsupported_selection)
    if selection_readiness({required_unsupported["profile_id"]: required_unsupported}, core, unsupported_selection, unsupported_result) != "blocked":
        raise AssertionError("required unsupported check was counted as ready")
    print("PASS required unsupported check => blocked")
    incomplete_result = {**result, "check_results": {"sample-next-ts": {"browser-run": result["check_results"]["sample-next-ts"]["browser-run"]}}}
    if selection_readiness(profiles, core, selection, incomplete_result) != "blocked":
        raise AssertionError("missing required check result was counted as ready")
    print("PASS missing required check result => blocked")
    missing_prerequisite = selection_fixture({profile["profile_id"]: profile}, core)
    missing_prerequisite["prerequisites"]["sample-next-ts/node"] = {
        "required": True,
        "state": "missing",
        "reason": "No required Node.js runtime is available.",
    }
    missing_prerequisite_result = {**result, "selection_manifest_sha256": canonical_digest(missing_prerequisite)}
    if selection_readiness(profiles, core, missing_prerequisite, missing_prerequisite_result) != "blocked":
        raise AssertionError("missing required prerequisite was counted as ready")
    print("PASS missing required prerequisite => blocked")
    if selection_readiness({}, core, core_only, core_only_result) != "core-only":
        raise AssertionError("empty profile selection was not reported as core-only")
    print("PASS empty profile selection => core-only; no profile support claim")
    inconsistent_core_only_result = {**core_only_result, "selected_profiles": {"sample-next-ts": selection["selected_profiles"]["sample-next-ts"]}}
    if selection_readiness({}, core, core_only, inconsistent_core_only_result) != "blocked":
        raise AssertionError("core-only result with residual selected profile was accepted")
    print("PASS inconsistent core-only result => blocked")
    residual_profile_selection = copy.deepcopy(core_only)
    residual_profile_selection["generated_files"]["package.json"] = selection["generated_files"]["package.json"]
    if selection_readiness({}, core, residual_profile_selection, {**core_only_result, "selection_manifest_sha256": canonical_digest(residual_profile_selection)}) != "blocked":
        raise AssertionError("core-only selection with profile-owned output was accepted")
    print("PASS core-only selection with residual profile-owned file => blocked")
    print("Architecture contract fixtures completed; no initializer/profile support is claimed.")


if __name__ == "__main__":
    main()
