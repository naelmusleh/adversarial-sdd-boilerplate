#!/usr/bin/env python3
"""Dependency-free artifact helper for framework and initialized app repositories."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_CANONICAL_FILES = ("mission.md", "constitution.md", "specification.md", "design.md", "backlog.md")
APP_ARTIFACT_DIRS = ("decisions", "reviews", "architecture", "delivery", "operations", "docs")
APP_STABLE_FILENAMES = {
    "decision-log": "DECISION-LOG.md",
    "architecture-overview": "architecture.md",
    "feasibility-register": "feasibility-register.md",
    "verification-plan": "verification-plan.md",
    "operations-runbook": "RUNBOOK.md",
}
REQUIRED = ("id", "type", "title", "status", "version", "created", "updated")
FRAMEWORK_CONTRACT = Path("docs/framework/ARTIFACT-CONTRACT-001.json")
APP_FRAMEWORK_LOCK = Path(".sdd/framework.lock.json")
APP_HANDOFFS = {
    "G-REQ": Path(".sdd/G-REQ-HANDOFF.json"),
    "G-ARCH": Path(".sdd/G-ARCH-CONTRACT.json"),
}
APP_LOCKED_FILES = (
    "scripts/artifacts.py",
    ".sdd/G-REQ-HANDOFF.json.template",
    ".sdd/G-ARCH-CONTRACT.json.template",
    "docs/templates/app-project/gate-record.md.template",
    ".github/workflows/sdd-contract-validation.yml",
)
APP_LOCK_VERSION = 1
HANDOFF_CONTRACT_VERSION = 1
MAX_JSON_BYTES = 1_048_576
APP_REQUIREMENT_TABLES = (
    {"path": "specification.md", "heading": "## Functional requirements", "requirement_kind": "FR", "minimum_rows": 0},
    {"path": "specification.md", "heading": "## Quality requirements", "requirement_kind": "NFR", "minimum_rows": 0},
)
RFC_2119_KEYWORDS = (
    "MUST NOT", "SHALL NOT", "SHOULD NOT", "MUST", "REQUIRED", "SHALL",
    "SHOULD", "RECOMMENDED", "MAY", "OPTIONAL",
)
ALLOWED_STATUSES = {
    "draft", "in-review", "revision-required", "approved", "active",
    "blocked", "superseded", "retired",
}
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[0-9]{3}$")
KEY_RE = re.compile(r"^([a-z][a-z0-9-]*):\s*(.*?)\s*$")
FRAMEWORK_REVISION_RE = re.compile(r"^[a-f0-9]{40}$")
SHA256_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
GATE_RESULTS = {"not-run", "passed", "failed", "blocked", "passed-with-accepted-risk", "not-applicable"}
GATE_IDS = {
    "G-INTENT", "G-SETUP", "G-REQ", "G-FEAS", "G-COVERAGE",
    "G-CX", "G-ARCH", "G-IMPL", "G-RELEASE", "G-OPERATE",
}


def is_app_project(root: Path) -> bool:
    """Recognize an app SDD repository, including an incomplete one.

    Any canonical root document is enough to identify the app layout. Requiring
    every file here made a damaged app repository fall back to framework mode,
    where validation could misleadingly succeed with zero artifacts.
    """
    return any((root / filename).is_file() for filename in APP_CANONICAL_FILES)


def missing_app_canonical_files(root: Path) -> tuple[str, ...]:
    """Return required app SDD documents that are absent from a recognized app."""
    if not is_app_project(root):
        return ()
    return tuple(filename for filename in APP_CANONICAL_FILES if not (root / filename).is_file())


def artifact_roots(root: Path) -> tuple[Path, ...]:
    if is_app_project(root):
        return tuple([root / filename for filename in APP_CANONICAL_FILES] + [root / name for name in APP_ARTIFACT_DIRS])
    return (root / "docs", root / "framework", root / "workflows")


def markdown_files(root: Path = ROOT) -> list[Path]:
    files: set[Path] = set()
    for base in artifact_roots(root):
        if base.is_file() and base.suffix.lower() == ".md":
            files.add(base)
            continue
        if not base.is_dir():
            continue
        files.update(p for p in base.rglob("*.md") if p.is_file())
    # Templates are scaffolding, never live framework or app artifacts.
    files = {p for p in files if not (root / "docs" / "templates" in p.parents)}
    return sorted(files)


def read_front_matter(path: Path) -> tuple[dict[str, str], str | None]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return {}, str(exc)
    if not lines or lines[0].strip() != "---":
        return {}, "missing front matter opening delimiter"
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, "missing front matter closing delimiter"
    data: dict[str, str] = {}
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip():
            continue
        match = KEY_RE.match(line)
        if not match:
            return data, f"unsupported front matter at line {number}; expected flat key: value"
        key, value = match.groups()
        if key in data:
            return data, f"duplicate metadata key: {key}"
        data[key] = value.strip().strip("\"'")
    return data, None


def load_json_object(path: Path) -> tuple[dict[str, object] | None, str | None]:
    """Load strict JSON, rejecting duplicate keys instead of silently keeping the last value."""
    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key '{key}'")
            result[key] = value
        return result

    def reject_constant(value: str) -> object:
        raise ValueError(f"non-standard JSON constant '{value}'")

    try:
        if path.stat().st_size > MAX_JSON_BYTES:
            return None, f"JSON file exceeds {MAX_JSON_BYTES} byte limit"
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        return None, str(exc)
    if not isinstance(value, dict):
        return None, "top-level JSON value must be an object"
    return value, None


def file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def check_frozen_artifact(root: Path, item: object, label: str) -> list[str]:
    if not isinstance(item, dict) or set(item) != {"path", "id", "version", "sha256"}:
        return [f"{label}: each frozen artifact must define exactly path, id, version, and sha256"]
    relative, expected_id, expected_version, expected_digest = (
        item.get("path"), item.get("id"), item.get("version"), item.get("sha256")
    )
    if not all(isinstance(value, str) and value.strip() for value in (relative, expected_id, expected_version)):
        return [f"{label}: frozen artifact path, id, and version must be non-empty strings"]
    if not isinstance(expected_digest, str) or not SHA256_RE.fullmatch(expected_digest):
        return [f"{label} ({relative}): sha256 must use the form sha256:<64 lowercase hexadecimal characters>"]
    path, error = safe_file(root, relative)
    if error or path is None:
        return [f"{label} ({relative}): {error or 'could not resolve file'}"]
    metadata, metadata_error = read_front_matter(path)
    if metadata_error:
        return [f"{label} ({relative}): frozen artifact metadata could not be read: {metadata_error}"]
    problems = []
    if metadata.get("id") != expected_id:
        problems.append(f"{label} ({relative}): expected artifact ID '{expected_id}', found '{metadata.get('id', '')}'")
    if metadata.get("version") != expected_version:
        problems.append(f"{label} ({relative}): expected version '{expected_version}', found '{metadata.get('version', '')}'")
    if file_sha256(path) != expected_digest:
        problems.append(f"{label} ({relative}): frozen file digest does not match")
    return problems


def check_review_reference(root: Path, value: object, label: str) -> list[str]:
    expected_fields = {"path", "id", "version", "sha256", "reviewer_mode", "result"}
    if not isinstance(value, dict) or set(value) != expected_fields:
        return [f"{label}: independent_review must define exactly {', '.join(sorted(expected_fields))}"]
    if value.get("reviewer_mode") != "independent" or value.get("result") != "PASS":
        return [f"{label}: handoff requires an independent review with result PASS"]
    return check_frozen_artifact(
        root,
        {key: value.get(key) for key in ("path", "id", "version", "sha256")},
        label + " independent_review",
    )


def validate_handoff_manifest(root: Path, gate_id: str, revision: str) -> list[str]:
    manifest_path = APP_HANDOFFS[gate_id]
    path, error = safe_file(root, manifest_path.as_posix())
    if error or path is None:
        return [f"{manifest_path.as_posix()}: required handoff manifest {error or 'is missing'}"]
    manifest, parse_error = load_json_object(path)
    if parse_error or manifest is None:
        return [f"{manifest_path.as_posix()}: invalid JSON handoff manifest: {parse_error or 'invalid object'}"]

    if gate_id == "G-REQ":
        expected_fields = {"contract_id", "contract_version", "framework_revision", "source_gate", "scope", "frozen_artifacts", "independent_review"}
        expected_id = "G-REQ-HANDOFF-001"
        required_paths = {"mission.md", "constitution.md", "specification.md", "backlog.md"}
    else:
        expected_fields = {"contract_id", "contract_version", "framework_revision", "source_gate", "scope", "frozen_artifacts", "contract_file", "required_checks", "review_inputs", "independent_review"}
        expected_id = "G-ARCH-CONTRACT-001"
        required_paths = {"specification.md", "design.md", "backlog.md"}

    problems: list[str] = []
    if set(manifest) != expected_fields:
        problems.append(f"{manifest_path.as_posix()}: fields must be exactly {', '.join(sorted(expected_fields))}")
    if manifest.get("contract_id") != expected_id or manifest.get("contract_version") != HANDOFF_CONTRACT_VERSION:
        problems.append(f"{manifest_path.as_posix()}: unsupported contract identity or version")
    if manifest.get("source_gate") != gate_id:
        problems.append(f"{manifest_path.as_posix()}: source_gate must be '{gate_id}'")
    if manifest.get("framework_revision") != revision:
        problems.append(f"{manifest_path.as_posix()}: framework_revision does not match .sdd/framework.lock.json")
    scope = manifest.get("scope")
    if not isinstance(scope, str) or not scope.strip() or "<" in scope or ">" in scope:
        problems.append(f"{manifest_path.as_posix()}: scope must be a populated string without template markers")

    frozen_artifacts = manifest.get("frozen_artifacts")
    if not isinstance(frozen_artifacts, list) or not frozen_artifacts:
        problems.append(f"{manifest_path.as_posix()}: frozen_artifacts must be a non-empty array")
    else:
        seen_paths: set[str] = set()
        observed_paths: set[str] = set()
        for index, item in enumerate(frozen_artifacts, 1):
            label = f"{manifest_path.as_posix()} frozen_artifacts[{index}]"
            problems.extend(check_frozen_artifact(root, item, label))
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                relative = item["path"]
                if relative in seen_paths:
                    problems.append(f"{label}: duplicate frozen artifact path '{relative}'")
                seen_paths.add(relative)
                observed_paths.add(relative)
        for required_path in sorted(required_paths - observed_paths):
            problems.append(f"{manifest_path.as_posix()}: frozen_artifacts must include '{required_path}'")

    problems.extend(check_review_reference(root, manifest.get("independent_review"), manifest_path.as_posix()))

    if gate_id == "G-ARCH":
        contract_file = manifest.get("contract_file")
        if not isinstance(contract_file, dict) or set(contract_file) != {"path", "sha256"}:
            problems.append(f"{manifest_path.as_posix()}: contract_file must define exactly path and sha256")
        else:
            contract_path, contract_error = safe_file(root, str(contract_file.get("path", "")))
            digest = contract_file.get("sha256")
            if contract_error or contract_path is None:
                problems.append(f"{manifest_path.as_posix()} contract_file: {contract_error or 'file is missing'}")
            elif not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
                problems.append(f"{manifest_path.as_posix()} contract_file: sha256 is malformed")
            elif file_sha256(contract_path) != digest:
                problems.append(f"{manifest_path.as_posix()} contract_file: frozen contract digest does not match")
        checks = manifest.get("required_checks")
        if not isinstance(checks, list) or not checks:
            problems.append(f"{manifest_path.as_posix()}: required_checks must be a non-empty array")
        else:
            check_ids: set[str] = set()
            for index, check in enumerate(checks, 1):
                label = f"{manifest_path.as_posix()} required_checks[{index}]"
                if not isinstance(check, dict) or set(check) != {"id", "command", "assertions"}:
                    problems.append(f"{label}: each check must define exactly id, command, and assertions")
                    continue
                check_id, command, assertions = check.get("id"), check.get("command"), check.get("assertions")
                if not isinstance(check_id, str) or not check_id.strip() or check_id in check_ids:
                    problems.append(f"{label}: id must be a unique non-empty string")
                else:
                    check_ids.add(check_id)
                if not isinstance(command, str) or not command.strip() or "<" in command or ">" in command:
                    problems.append(f"{label}: command must be a populated exact command")
                if not isinstance(assertions, list) or not assertions or not all(isinstance(item, str) and item.strip() for item in assertions):
                    problems.append(f"{label}: assertions must be a non-empty array of non-empty strings")
        review_inputs = manifest.get("review_inputs")
        if not isinstance(review_inputs, list):
            problems.append(f"{manifest_path.as_posix()}: review_inputs must be an array")
        else:
            purposes: set[str] = set()
            for index, review_input in enumerate(review_inputs, 1):
                label = f"{manifest_path.as_posix()} review_inputs[{index}]"
                if not isinstance(review_input, dict) or set(review_input) != {"purpose", "path", "id", "version", "sha256"}:
                    problems.append(f"{label}: each review input must define exactly purpose, path, id, version, and sha256")
                    continue
                purpose = review_input.get("purpose")
                if not isinstance(purpose, str) or not purpose.strip():
                    problems.append(f"{label}: purpose must be a non-empty string")
                    continue
                if purpose not in {"historical-rule-index", "domain-contract", "security-review", "other"}:
                    problems.append(f"{label}: unsupported review input purpose '{purpose}'")
                problems.extend(
                    check_frozen_artifact(
                        root,
                        {key: review_input.get(key) for key in ("path", "id", "version", "sha256")},
                        label,
                    )
                )
                if isinstance(purpose, str):
                    key = f"{purpose}:{review_input.get('path')}"
                    if key in purposes:
                        problems.append(f"{label}: duplicate review input '{key}'")
                    purposes.add(key)
    return problems


def application_governance_problems(root: Path, gate_records: list[tuple[Path, dict[str, str]]]) -> list[str]:
    """Check a versioned app framework lock and gate handoff manifests when adopted."""
    lock_path = root / APP_FRAMEWORK_LOCK
    has_manifest = any((root / path).exists() for path in APP_HANDOFFS.values())
    problems: list[str] = []
    # Pre-lock app repositories retain legacy gate-record semantics. Once a
    # lock or handoff manifest is present, enforce the versioned handoff rules.
    if not lock_path.exists() and not has_manifest:
        return problems
    revision = ""
    if lock_path.exists():
        safe_lock_path, lock_path_error = safe_file(root, APP_FRAMEWORK_LOCK.as_posix())
        if lock_path_error or safe_lock_path is None:
            return [f"{APP_FRAMEWORK_LOCK.as_posix()}: {lock_path_error or 'could not resolve lock'}"]
        lock, parse_error = load_json_object(safe_lock_path)
        if parse_error or lock is None:
            return [f"{APP_FRAMEWORK_LOCK.as_posix()}: invalid JSON framework lock: {parse_error or 'invalid object'}"]
        expected_fields = {"lock_version", "framework_repository", "framework_revision", "artifact_contract_id", "artifact_contract_version", "locked_files"}
        if set(lock) != expected_fields:
            problems.append(f"{APP_FRAMEWORK_LOCK.as_posix()}: fields must be exactly {', '.join(sorted(expected_fields))}")
        revision_value = lock.get("framework_revision")
        if lock.get("lock_version") != APP_LOCK_VERSION or lock.get("artifact_contract_id") != "ARTIFACT-CONTRACT-001" or lock.get("artifact_contract_version") != 1:
            problems.append(f"{APP_FRAMEWORK_LOCK.as_posix()}: unsupported framework or artifact contract version")
        if not isinstance(revision_value, str) or not FRAMEWORK_REVISION_RE.fullmatch(revision_value):
            problems.append(f"{APP_FRAMEWORK_LOCK.as_posix()}: framework_revision must be a 40-character lowercase commit SHA")
        else:
            revision = revision_value
        repository = lock.get("framework_repository")
        if not isinstance(repository, str) or not repository.startswith("https://github.com/"):
            problems.append(f"{APP_FRAMEWORK_LOCK.as_posix()}: framework_repository must be an HTTPS GitHub repository URL")
        locked_files = lock.get("locked_files")
        if not isinstance(locked_files, dict) or set(locked_files) != set(APP_LOCKED_FILES):
            problems.append(f"{APP_FRAMEWORK_LOCK.as_posix()}: locked_files must cover exactly the validator, both handoff templates, gate-record template, and SDD workflow")
        else:
            for relative in APP_LOCKED_FILES:
                expected_digest = locked_files.get(relative)
                path, error = safe_file(root, relative)
                if error or path is None:
                    problems.append(f"{APP_FRAMEWORK_LOCK.as_posix()} ({relative}): locked file {error or 'is missing'}")
                elif not isinstance(expected_digest, str) or not SHA256_RE.fullmatch(expected_digest):
                    problems.append(f"{APP_FRAMEWORK_LOCK.as_posix()} ({relative}): locked digest is malformed")
                elif file_sha256(path) != expected_digest:
                    problems.append(f"{APP_FRAMEWORK_LOCK.as_posix()} ({relative}): file digest differs from the initialized framework snapshot")

    for gate_id, manifest_path in APP_HANDOFFS.items():
        if (root / manifest_path).exists():
            if not revision:
                problems.append(f"{manifest_path.as_posix()}: a versioned .sdd/framework.lock.json is required")
            else:
                problems.extend(validate_handoff_manifest(root, gate_id, revision))

    for path, data in gate_records:
        gate_id = data.get("gate-id", "")
        if gate_id not in APP_HANDOFFS:
            continue
        result = data.get("gate-result", "").lower()
        if not result:
            problems.append(f"{path.relative_to(root).as_posix()}: {gate_id} gate record must declare gate-result")
        elif result not in GATE_RESULTS:
            problems.append(f"{path.relative_to(root).as_posix()}: invalid gate-result '{data.get('gate-result')}'")
        if result in {"passed", "passed-with-accepted-risk"}:
            expected_manifest = APP_HANDOFFS[gate_id].as_posix()
            if data.get("handoff-manifest") != expected_manifest:
                problems.append(f"{path.relative_to(root).as_posix()}: passed {gate_id} record must link handoff-manifest '{expected_manifest}'")
            if not revision:
                problems.append(f"{path.relative_to(root).as_posix()}: passed {gate_id} record requires a versioned .sdd/framework.lock.json")
            if not (root / APP_HANDOFFS[gate_id]).is_file():
                problems.append(f"{path.relative_to(root).as_posix()}: passed {gate_id} record has no populated {expected_manifest}")

    if has_manifest and not lock_path.exists():
        problems.append(f"{APP_FRAMEWORK_LOCK.as_posix()}: required because a handoff manifest is present")
    return problems


def safe_file(root: Path, relative: str) -> tuple[Path | None, str | None]:
    """Resolve a repository-relative file without allowing manifest path escape."""
    candidate_path = Path(relative)
    if candidate_path.is_absolute() or ".." in candidate_path.parts:
        return None, "path must be repository-relative and must not contain '..'"
    root_resolved = root.resolve()
    candidate = (root / candidate_path).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError:
        return None, "path resolves outside the repository"
    if not candidate.is_file():
        return None, "required file is missing"
    return candidate, None


def section_bounds(lines: list[str], heading: str) -> tuple[int, int] | None:
    """Find one exact Markdown heading and return its body bounds."""
    target = re.fullmatch(r"(#{1,6})\s+(.+?)\s*", heading)
    if not target:
        return None
    target_level = len(target.group(1))
    target_title = target.group(2).strip().rstrip("#").strip()
    matches = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line.strip())
        if match and len(match.group(1)) == target_level and match.group(2).strip() == target_title:
            matches.append(index)
    if len(matches) != 1:
        return None
    start = matches[0] + 1
    end = len(lines)
    for index in range(start, len(lines)):
        match = re.match(r"^(#{1,6})\s+", lines[index].strip())
        if match and len(match.group(1)) <= target_level:
            end = index
            break
    return start, end


def split_table_row(line: str) -> list[str]:
    return [cell.strip().strip("`").strip() for cell in line.strip().strip("|").split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def requirement_table_problems(
    root: Path,
    table_spec: dict[str, object],
    keywords: tuple[str, ...] = RFC_2119_KEYWORDS,
) -> list[str]:
    """Validate requirement tables in one explicitly configured document section."""
    relative = table_spec.get("path")
    heading = table_spec.get("heading")
    requirement_kind = table_spec.get("requirement_kind")
    minimum_rows = table_spec.get("minimum_rows")
    if not isinstance(relative, str) or not isinstance(heading, str):
        return ["requirement-table rule must define string path and heading fields"]
    if requirement_kind not in {"FR", "NFR"} or not isinstance(minimum_rows, int) or minimum_rows < 0:
        return [f"{relative}: requirement-table rule has invalid requirement_kind or minimum_rows"]
    path, error = safe_file(root, relative)
    if error or path is None:
        return [f"{relative}: {error or 'could not resolve file'}"]
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return [f"{relative}: could not read requirement document: {exc}"]
    bounds = section_bounds(lines, heading)
    if bounds is None:
        return [f"{relative}: required heading '{heading}' must occur exactly once"]
    start, end = bounds
    section_lines = lines[start:end]
    problem_prefix = f"{relative} ({heading})"
    table_runs: list[list[tuple[int, str]]] = []
    current_run: list[tuple[int, str]] = []
    for offset, line in enumerate(section_lines, start + 1):
        if line.strip().startswith("|") and line.strip().endswith("|"):
            current_run.append((offset, line))
        elif current_run:
            table_runs.append(current_run)
            current_run = []
    if current_run:
        table_runs.append(current_run)

    counted_rows = 0
    expected_headers = ("ID", "Requirement", "Acceptance evidence")
    keyword_pattern = re.compile(
        r"(?<![A-Za-z])(?:"
        + "|".join(re.escape(word) for word in sorted(keywords, key=len, reverse=True))
        + r")(?![A-Za-z])",
        re.IGNORECASE,
    )
    for table_number, run in enumerate(table_runs, 1):
        header_line, header_text = run[0]
        headers = tuple(split_table_row(header_text))
        if len(run) < 2 or not is_table_separator(run[1][1]):
            return [f"{problem_prefix}: table {table_number} at line {header_line} is missing a Markdown separator row"]
        if tuple(value.casefold() for value in headers) != tuple(value.casefold() for value in expected_headers):
            return [
                f"{problem_prefix}: table {table_number} at line {header_line} must use columns "
                "ID | Requirement | Acceptance evidence"
            ]
        for line_number, row_text in run[2:]:
            if is_table_separator(row_text):
                continue
            cells = split_table_row(row_text)
            if len(cells) != 3:
                return [f"{problem_prefix}: row at line {line_number} must contain exactly three columns"]
            artifact_id, statement, acceptance = cells
            if artifact_id.startswith("<") and artifact_id.endswith(">"):
                continue
            counted_rows += 1
            if not ID_RE.fullmatch(artifact_id):
                return [f"{problem_prefix}: row at line {line_number} has invalid stable ID '{artifact_id}'"]
            if requirement_kind not in artifact_id.split("-"):
                return [
                    f"{problem_prefix}: row at line {line_number} ID '{artifact_id}' must identify a {requirement_kind} requirement"
                ]
            if not statement:
                return [f"{problem_prefix}: row at line {line_number} has an empty Requirement cell"]
            if not acceptance:
                return [f"{problem_prefix}: row at line {line_number} has an empty Acceptance evidence cell"]
            matches = list(keyword_pattern.finditer(statement))
            uppercase_matches = [match.group(0) for match in matches if match.group(0) in keywords]
            if not uppercase_matches:
                return [
                    f"{problem_prefix}: row at line {line_number} must contain an uppercase RFC 2119 keyword "
                    "in the Requirement cell"
                ]
    if counted_rows < minimum_rows:
        return [
            f"{problem_prefix}: expected at least {minimum_rows} requirement row(s), found {counted_rows}"
        ]
    return []


def framework_contract_problems(root: Path) -> list[str]:
    """Load and enforce the framework repository's required-artifact contract."""
    contract_path, path_error = safe_file(root, FRAMEWORK_CONTRACT.as_posix())
    if path_error or contract_path is None:
        return [f"{FRAMEWORK_CONTRACT.as_posix()}: required framework artifact contract is missing ({path_error})"]
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"{FRAMEWORK_CONTRACT.as_posix()}: invalid JSON artifact contract: {exc}"]
    if not isinstance(contract, dict) or contract.get("contract_id") != "ARTIFACT-CONTRACT-001" or contract.get("contract_version") != 1:
        return [f"{FRAMEWORK_CONTRACT.as_posix()}: unsupported artifact contract identity or version"]
    profile = contract.get("framework")
    if not isinstance(profile, dict):
        return [f"{FRAMEWORK_CONTRACT.as_posix()}: missing framework profile"]
    required_paths = profile.get("required_paths")
    required_artifacts = profile.get("required_artifacts")
    requirement_tables = profile.get("requirement_tables")
    keywords = contract.get("normative_keywords")
    if not isinstance(required_paths, list) or not all(isinstance(item, str) for item in required_paths):
        return [f"{FRAMEWORK_CONTRACT.as_posix()}: framework required_paths must be a list of strings"]
    if not isinstance(required_artifacts, list) or not all(isinstance(item, dict) for item in required_artifacts):
        return [f"{FRAMEWORK_CONTRACT.as_posix()}: framework required_artifacts must be a list of objects"]
    if not isinstance(requirement_tables, list) or not all(isinstance(item, dict) for item in requirement_tables):
        return [f"{FRAMEWORK_CONTRACT.as_posix()}: framework requirement_tables must be a list of objects"]
    if (not isinstance(keywords, list) or not keywords or not all(isinstance(item, str) and item and item == item.upper() for item in keywords)
            or len(set(keywords)) != len(keywords)):
        return [f"{FRAMEWORK_CONTRACT.as_posix()}: normative_keywords must be a non-empty list of unique uppercase strings"]
    keyword_tuple = tuple(keywords)
    if set(keyword_tuple) != set(RFC_2119_KEYWORDS):
        return [f"{FRAMEWORK_CONTRACT.as_posix()}: normative_keywords must match the supported RFC 2119 keyword set"]
    problems: list[str] = []
    for relative in required_paths:
        _, error = safe_file(root, relative)
        if error:
            problems.append(f"{relative}: required template file {error}")
    for artifact in required_artifacts:
        relative = artifact.get("path")
        expected_id = artifact.get("id")
        if not isinstance(relative, str) or not isinstance(expected_id, str):
            problems.append(f"{FRAMEWORK_CONTRACT.as_posix()}: each required artifact must define string path and id fields")
            continue
        path, error = safe_file(root, relative)
        if error or path is None:
            problems.append(f"{relative}: required artifact {error or 'could not resolve file'}")
            continue
        metadata, metadata_error = read_front_matter(path)
        if metadata_error:
            problems.append(f"{relative}: required artifact metadata could not be read: {metadata_error}")
        elif metadata.get("id") != expected_id:
            problems.append(
                f"{relative}: required artifact ID must be '{expected_id}', found '{metadata.get('id', '') or 'missing'}'"
            )
    for table_spec in requirement_tables:
        problems.extend(requirement_table_problems(root, table_spec, keyword_tuple))
    return problems


def application_requirement_problems(root: Path) -> list[str]:
    """Lint only configured requirement tables in an initialized app specification."""
    spec = root / "specification.md"
    if not spec.is_file():
        return []
    problems: list[str] = []
    for table_spec in APP_REQUIREMENT_TABLES:
        problems.extend(requirement_table_problems(root, table_spec))
    return problems


def command_list(_: argparse.Namespace) -> int:
    rows = []
    for path in markdown_files(ROOT):
        data, _ = read_front_matter(path)
        if data.get("id"):
            rows.append((data["id"], data.get("status", "?"), path.relative_to(ROOT).as_posix(), data.get("title", "")))
    for artifact_id, status, path, title in sorted(rows):
        print(f"{artifact_id:24} {status:20} {path} — {title}")
    print(f"{len(rows)} artifact(s)")
    missing = missing_app_canonical_files(ROOT)
    if missing:
        print(
            "ERROR incomplete app SDD layout; missing required root file(s): "
            + ", ".join(missing),
            file=sys.stderr,
        )
        return 1
    return 0


def command_validate(_: argparse.Namespace) -> int:
    problems: list[str] = []
    seen: dict[str, Path] = {}
    gate_records: list[tuple[Path, dict[str, str]]] = []
    app_project = is_app_project(ROOT)
    if app_project:
        for filename in missing_app_canonical_files(ROOT):
            problems.append(f"{filename}: required app SDD root file is missing")
    elif not markdown_files(ROOT):
        problems.append("no artifacts discovered; refusing to validate an empty repository")
    if app_project:
        problems.extend(application_requirement_problems(ROOT))
    else:
        problems.extend(framework_contract_problems(ROOT))
    for path in markdown_files(ROOT):
        data, error = read_front_matter(path)
        rel = path.relative_to(ROOT).as_posix()
        if error:
            problems.append(f"{rel}: {error}")
            continue
        for key in REQUIRED:
            if not data.get(key):
                problems.append(f"{rel}: missing required field '{key}'")
        status = data.get("status", "")
        if status and status not in ALLOWED_STATUSES:
            problems.append(
                f"{rel}: invalid artifact status '{status}'; expected one of "
                f"{', '.join(sorted(ALLOWED_STATUSES))}"
            )
        gate_id = data.get("gate-id", "")
        declares_handoff_gate = gate_id in APP_HANDOFFS
        gate_record_type = data.get("type") in {"gate-record", "lifecycle-gate-record"}
        has_gate_metadata = any(key in data for key in ("gate-id", "gate-result", "handoff-manifest"))
        if has_gate_metadata and not gate_record_type:
            problems.append(
                f"{rel}: gate metadata requires type 'gate-record' or 'lifecycle-gate-record'"
            )
        if gate_record_type and gate_id not in GATE_IDS:
            problems.append(
                f"{rel}: gate record must declare a recognized gate-id; expected one of "
                f"{', '.join(sorted(GATE_IDS))}"
            )
        if "handoff-manifest" in data and gate_id not in APP_HANDOFFS:
            problems.append(f"{rel}: handoff-manifest is supported only for G-REQ or G-ARCH records")
        if gate_record_type or declares_handoff_gate:
            gate_records.append((path, data))
        artifact_id = data.get("id", "")
        if artifact_id:
            if not ID_RE.fullmatch(artifact_id):
                problems.append(f"{rel}: invalid artifact ID '{artifact_id}'")
            if artifact_id in seen:
                problems.append(f"{rel}: duplicate ID {artifact_id} (also {seen[artifact_id].relative_to(ROOT)})")
            else:
                seen[artifact_id] = path
            # Keep established human-readable workflow paths stable; their
            # metadata ID remains the canonical identity and is still checked
            # for presence and duplication. Other artifact paths are ID-led.
            canonical_app_file = app_project and path.parent == ROOT and path.name in APP_CANONICAL_FILES
            app_prefix = ""
            if app_project:
                mission, _ = read_front_matter(ROOT / "mission.md")
                app_prefix = mission.get("id", "").removesuffix("-MISSION-001")
            app_id_suffix = artifact_id.removeprefix(f"{app_prefix}-") if app_prefix else artifact_id
            stable_app_name = app_project and APP_STABLE_FILENAMES.get(data.get("type", "")) == path.name
            stable_workflow_path = not app_project and path.parent == ROOT / "workflows"
            valid_app_id_name = app_project and (
                path.stem == artifact_id or path.stem.startswith(artifact_id + "-")
                or path.stem == app_id_suffix or path.stem.startswith(app_id_suffix + "-")
                or stable_app_name
            )
            if not canonical_app_file and not stable_workflow_path and not valid_app_id_name and not path.name.startswith(artifact_id):
                problems.append(f"{rel}: filename must begin with {artifact_id}")
    if app_project:
        problems.extend(application_governance_problems(ROOT, gate_records))
    if problems:
        print("\n".join(f"ERROR {item}" for item in problems), file=sys.stderr)
        return 1
    print(f"Validated {len(seen)} artifact(s).")
    return 0


def command_new(args: argparse.Namespace) -> int:
    if not ID_RE.fullmatch(args.artifact_id):
        print("ID must look like ADR-001, PRD-014, or PRODUCT-ADV-001.", file=sys.stderr)
        return 2
    title = " ".join(args.title.split())
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "artifact"
    type_slug = re.sub(r"[^a-z0-9]+", "-", args.artifact_type.lower()).strip("-")
    app_project = is_app_project(ROOT)
    missing = missing_app_canonical_files(ROOT)
    if missing:
        print(
            "Refusing to create an artifact in an incomplete app SDD layout; "
            "missing required root file(s): " + ", ".join(missing),
            file=sys.stderr,
        )
        return 2
    app_type_directories = {
        "decision": "decisions",
        "decision-record": "decisions",
        "review": "reviews",
        "adversarial-review": "reviews",
        "gate-record": "reviews",
        "architecture": "architecture",
        "adr": "architecture",
        "architecture-decision-record": "architecture",
        "feasibility-register": "architecture",
        "verification": "delivery/verification",
        "verification-record": "delivery/verification",
        "verification-plan": "delivery",
        "release": "delivery/releases",
        "release-record": "delivery/releases",
        "operations": "operations",
        "operations-runbook": "operations",
        "incident": "operations/incidents",
    }
    if app_project:
        directory = ROOT / app_type_directories.get(type_slug, f"docs/{type_slug}")
    else:
        directory = ROOT / "docs" / type_slug
    path = directory / f"{args.artifact_id}-{slug}.md"
    for existing in markdown_files(ROOT):
        data, _ = read_front_matter(existing)
        if data.get("id") == args.artifact_id:
            print(f"ID already exists in {existing.relative_to(ROOT)}", file=sys.stderr)
            return 2
    today = dt.date.today().isoformat()
    content = (
        "---\n"
        f"id: {args.artifact_id}\n"
        f"type: {type_slug}\n"
        f"title: {title}\n"
        "status: draft\n"
        "version: 0.1\n"
        f"created: {today}\n"
        f"updated: {today}\n"
        "---\n\n"
        f"# {args.artifact_id} — {title}\n\n"
        "## Purpose\n\n"
        "<Why this artifact exists and what decision or work it supports.>\n\n"
        "## Content\n\n"
        "<Artifact-specific content.>\n\n"
        "## References\n\n- <Related artifact IDs and links>\n"
    )
    directory.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as artifact_file:
            artifact_file.write(content)
    except FileExistsError:
        print(f"Refusing to overwrite {path.relative_to(ROOT)}", file=sys.stderr)
        return 2
    print(path.relative_to(ROOT))
    return 0


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list discovered artifacts").set_defaults(run=command_list)
    sub.add_parser("validate", help="check front matter and artifact identities").set_defaults(run=command_validate)
    create = sub.add_parser("new", help="create a new Markdown artifact")
    create.add_argument("artifact_type", help="artifact type, used as the docs subdirectory")
    create.add_argument("artifact_id", help="stable ID, such as ADR-001")
    create.add_argument("title")
    create.set_defaults(run=command_new)
    return cli


if __name__ == "__main__":
    arguments = parser().parse_args()
    raise SystemExit(arguments.run(arguments))
