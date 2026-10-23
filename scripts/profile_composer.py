"""Compose explicitly selected, versioned application profile fixtures."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any


PROFILE_ROOT = Path(__file__).resolve().parents[1] / "framework" / "profiles"
PROFILE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,63}$")
SEMVER_RE = re.compile(r"(?<!\d)(\d+)\.(\d+)\.(\d+)")
MINIMUM_VERSION_RE = re.compile(r"^>=(\d+)\.(\d+)\.(\d+)$")


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for key, value in pairs:
        if key in values:
            raise ValueError(f"duplicate JSON key: {key}")
        values[key] = value
    return values


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def byte_digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def safe_relative_path(value: str) -> bool:
    path = PurePosixPath(value)
    return bool(value) and path.as_posix() == value and not path.is_absolute() and ".." not in path.parts and "\\" not in value


def validate_profile(profile: Any, expected_id: str) -> None:
    if not isinstance(profile, dict) or profile.get("schema_version") != "1":
        raise ValueError(f"{expected_id}: unsupported profile manifest version")
    if profile.get("profile_id") != expected_id or not PROFILE_ID_RE.fullmatch(expected_id):
        raise ValueError(f"{expected_id}: profile ID does not match its directory")
    if not isinstance(profile.get("profile_version"), str) or not SEMVER_RE.fullmatch(profile["profile_version"]):
        raise ValueError(f"{expected_id}: profile_version must be semantic version text")
    for field in ("language", "runtime"):
        value = profile.get(field)
        if not isinstance(value, dict) or set(value) != {"name", "version_range"} or not all(
            isinstance(part, str) and part.strip() for part in value.values()
        ):
            raise ValueError(f"{expected_id}: invalid {field} declaration")
    prerequisites = profile.get("prerequisites")
    if not isinstance(prerequisites, dict):
        raise ValueError(f"{expected_id}: prerequisites must be an object")
    for name, prerequisite in prerequisites.items():
        if not PROFILE_ID_RE.fullmatch(name) or not isinstance(prerequisite, dict):
            raise ValueError(f"{expected_id}: invalid prerequisite declaration {name!r}")
        if set(prerequisite) != {"required", "version_constraint"} or not isinstance(prerequisite["required"], bool):
            raise ValueError(f"{expected_id}: invalid prerequisite fields for {name}")
        if not isinstance(prerequisite["version_constraint"], str) or not MINIMUM_VERSION_RE.fullmatch(prerequisite["version_constraint"]):
            raise ValueError(f"{expected_id}: prerequisite {name} must use a supported >=X.Y.Z version constraint")
    layout = profile.get("source_layout")
    if not isinstance(layout, list) or not layout or not all(isinstance(path, str) and safe_relative_path(path) for path in layout) or len(layout) != len(set(layout)):
        raise ValueError(f"{expected_id}: source_layout must list unique safe relative paths")
    checks = profile.get("checks")
    if not isinstance(checks, dict) or not checks:
        raise ValueError(f"{expected_id}: checks must be a non-empty object keyed by check ID")
    for check_id, check in checks.items():
        if not PROFILE_ID_RE.fullmatch(check_id) or not isinstance(check, dict):
            raise ValueError(f"{expected_id}: invalid check declaration {check_id!r}")
        if not isinstance(check.get("required"), bool):
            raise ValueError(f"{expected_id}: check {check_id} must declare boolean requiredness")
        if check.get("status") == "applicable" and set(check) == {"status", "required", "command", "scope"}:
            if not all(isinstance(check.get(field), str) and check[field].strip() for field in ("command", "scope")):
                raise ValueError(f"{expected_id}: applicable check {check_id} requires non-empty command and scope")
        elif check.get("status") == "unsupported" and set(check) == {"status", "required", "reason"}:
            if check["required"] or not isinstance(check.get("reason"), str) or not check["reason"].strip():
                raise ValueError(f"{expected_id}: unsupported check {check_id} must be optional and explain why")
        else:
            raise ValueError(f"{expected_id}: check {check_id} must be applicable with command/scope or unsupported with reason")
    dependencies = profile.get("owned_dependencies")
    if not isinstance(dependencies, list) or any(
        not isinstance(item, dict) or set(item) != {"name", "version_constraint", "purpose"}
        or not all(isinstance(item[key], str) and item[key].strip() for key in item)
        for item in dependencies
    ):
        raise ValueError(f"{expected_id}: owned_dependencies must be complete dependency declarations")
    dependency_names = [item["name"].casefold() for item in dependencies]
    if len(dependency_names) != len(set(dependency_names)):
        raise ValueError(f"{expected_id}: owned_dependencies cannot declare one package more than once")
    generated = profile.get("generated_files")
    if not isinstance(generated, list) or not generated or not all(isinstance(path, str) for path in generated) or len(generated) != len(set(generated)):
        raise ValueError(f"{expected_id}: generated_files must list unique output paths")
    manifest_destination = f".sdd/profiles/{expected_id}.json"
    if manifest_destination not in generated:
        raise ValueError(f"{expected_id}: generated_files must include its copied profile manifest")
    prefix = f"profiles/{expected_id}/"
    for path in generated:
        if not isinstance(path, str) or not safe_relative_path(path):
            raise ValueError(f"{expected_id}: unsafe generated path {path!r}")
        if path != manifest_destination and not path.startswith(prefix):
            raise ValueError(f"{expected_id}: generated path is outside its owned profile directory: {path}")


def observe_prerequisite(name: str, constraint: str) -> dict[str, Any]:
    executable = shutil.which(name)
    if not executable:
        return {"state": "missing", "reason": f"Executable '{name}' is not available on PATH (requires {constraint})."}
    try:
        result = subprocess.run([executable, "--version"], check=False, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"state": "missing", "reason": f"Could not inspect '{name}' version: {exc}."}
    output = (result.stdout + " " + result.stderr).strip()
    match = SEMVER_RE.search(output)
    if result.returncode != 0 or not match:
        return {"state": "missing", "reason": f"Could not determine '{name}' version for constraint {constraint}."}
    observed = tuple(int(part) for part in match.groups())
    minimum = MINIMUM_VERSION_RE.fullmatch(constraint)
    if minimum is None:
        return {"state": "missing", "reason": f"Version constraint {constraint!r} for '{name}' is unsupported; expected >=X.Y.Z."}
    if observed < tuple(int(part) for part in minimum.groups()):
        return {"state": "missing", "reason": f"'{name}' {'.'.join(map(str, observed))} is below required {constraint}."}
    return {"state": "available", "observed_version": ".".join(map(str, observed))}


def compose_profiles(
    selected_ids: list[str],
    core_outputs: dict[str, str],
    core_sources: dict[str, Path],
    framework_revision: str,
    *,
    profile_root: Path = PROFILE_ROOT,
    prerequisite_probe=observe_prerequisite,
) -> tuple[dict[str, str], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Return profile output files and three contracts, without writing to disk."""
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError("Duplicate --stack selections are not allowed.")
    all_ids: set[str] = set()
    for path in profile_root.iterdir():
        if path.is_symlink():
            raise ValueError(f"Profile registry contains a symlink: {path.name}")
        if path.is_dir() and (path / "profile.json").is_file():
            all_ids.add(path.name)
    unknown = sorted(set(selected_ids) - all_ids)
    if unknown:
        raise ValueError("Unknown application profile(s): " + ", ".join(unknown) + ". Available profiles: " + ", ".join(sorted(all_ids)))

    profiles: dict[str, dict[str, Any]] = {}
    source_bytes: dict[str, bytes] = {}
    prerequisites: dict[str, dict[str, Any]] = {}
    missing_required: list[str] = []
    output_files: dict[str, str] = {}
    profile_owners: dict[str, str] = {}
    for profile_id in sorted(selected_ids):
        profile_dir = profile_root / profile_id
        manifest_path = profile_dir / "profile.json"
        try:
            raw = manifest_path.read_bytes()
            profile = json.loads(raw.decode("utf-8"), object_pairs_hook=strict_pairs)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"{profile_id}: could not load strict JSON profile manifest: {exc}") from exc
        validate_profile(profile, profile_id)
        profiles[profile_id] = profile
        source_bytes[profile_id] = raw
        for prereq_name, declaration in profile["prerequisites"].items():
            observation = prerequisite_probe(prereq_name, declaration["version_constraint"])
            state = observation.get("state")
            if state not in {"available", "missing"}:
                raise ValueError(f"{profile_id}: prerequisite probe returned invalid state for {prereq_name}")
            record = {"required": declaration["required"], "state": state}
            if state == "available":
                record["observed_version"] = observation["observed_version"]
            else:
                record["reason"] = observation["reason"]
                if declaration["required"]:
                    missing_required.append(f"{profile_id}/{prereq_name}: {observation['reason']}")
            prerequisites[f"{profile_id}/{prereq_name}"] = record

        for destination in profile["generated_files"]:
            if destination == f".sdd/profiles/{profile_id}.json":
                content = raw.decode("utf-8")
            else:
                relative = destination.removeprefix(f"profiles/{profile_id}/")
                source_path = profile_dir / "files" / relative
                files_root = (profile_dir / "files").resolve(strict=True)
                if profile_dir.is_symlink() or (profile_dir / "files").is_symlink() or source_path.is_symlink() or not source_path.is_file():
                    raise ValueError(f"{profile_id}: declared generated source is missing or symlinked: {relative}")
                if not source_path.resolve(strict=True).is_relative_to(files_root):
                    raise ValueError(f"{profile_id}: generated source escapes its profile files directory: {relative}")
                content = source_path.read_text(encoding="utf-8")
            if destination in core_outputs or destination in output_files:
                raise ValueError(f"Generated path collision: {destination}")
            output_files[destination] = content
            profile_owners[destination] = profile_id

    if missing_required:
        raise ValueError("Required profile prerequisites are missing; no files were written:\n- " + "\n- ".join(missing_required))

    for profile_id, profile in profiles.items():
        foreign_markers: dict[str, set[str]] = {}
        for other_id, other in profiles.items():
            if other_id == profile_id:
                continue
            markers = {other_id.casefold(), other["language"]["name"].casefold(), other["runtime"]["name"].casefold()}
            markers.update(item["name"].casefold() for item in other["owned_dependencies"])
            foreign_markers[other_id] = {marker for marker in markers if len(marker) >= 3}
        for path, owner in profile_owners.items():
            if owner != profile_id:
                continue
            content = output_files[path].casefold()
            for other_id, markers in foreign_markers.items():
                if any(re.search(rf"(?<![a-z0-9]){re.escape(marker)}(?![a-z0-9])", content) for marker in markers):
                    raise ValueError(f"Profile leakage detected: {profile_id} output {path!r} contains a dependency or instruction marker owned by {other_id}.")

    core_inventory = {
        "schema_version": "1",
        "core_contract_version": "1.0.0",
        "files": {
            path: {"source_sha256": byte_digest(core_sources[path].read_bytes())}
            for path in sorted(core_outputs)
        },
    }
    generated_files = {
        path: {"sha256": byte_digest(content.encode("utf-8")), "owner": {"kind": "core"}}
        for path, content in sorted(core_outputs.items())
    }
    for path, content in sorted(output_files.items()):
        generated_files[path] = {
            "sha256": byte_digest(content.encode("utf-8")),
            "owner": {"kind": "profile", "profile_id": profile_owners[path]},
        }
    selection = {
        "schema_version": "1",
        "framework_revision": framework_revision,
        "core_contract_version": core_inventory["core_contract_version"],
        "core_manifest_sha256": canonical_digest(core_inventory),
        "selected_profiles": {
            profile_id: {
                "profile_version": profile["profile_version"],
                "manifest_sha256": canonical_digest(profile),
            }
            for profile_id, profile in sorted(profiles.items())
        },
        "generated_files": generated_files,
        "prerequisites": prerequisites,
        "profile_checks": {profile_id: profile["checks"] for profile_id, profile in sorted(profiles.items())},
    }
    check_results = {
        profile_id: {
            check_id: (
                {"state": "unsupported", "reason": declaration["reason"]}
                if declaration["status"] == "unsupported"
                else {"state": "not-run", "reason": "Initialization does not execute profile checks."}
            )
            for check_id, declaration in profile["checks"].items()
        }
        for profile_id, profile in sorted(profiles.items())
    }
    result = {
        "schema_version": "1",
        "framework_revision": framework_revision,
        "selection_manifest_sha256": canonical_digest(selection),
        "selected_profiles": selection["selected_profiles"],
        "check_results": check_results,
    }
    return output_files, core_inventory, selection, result
