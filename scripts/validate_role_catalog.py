#!/usr/bin/env python3
"""Validate the structure and canonical references in the framework role catalog."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.artifacts import markdown_files, read_front_matter  # noqa: E402


REQUIRED_COLUMNS = (
    "role_id",
    "source_role",
    "name",
    "classification",
    "purpose",
    "activate_when",
    "do_not_activate_when",
    "required_inputs",
    "deliverable",
    "decision_limits",
    "escalate_when",
    "handoff",
    "execution_mode",
    "artifact_refs",
)
CLASSIFICATIONS = {
    "existing-role",
    "on-demand-specialist",
    "operational-responsibility",
    "product-capability",
    "excluded",
}
FROZEN_SOURCE_ROLES = {
    "orchestrator",
    "setup",
    "researcher",
    "feasibility",
    "architect",
    "agentic-workflow",
    "platform-architect",
    "product-designer",
    "platform-designer",
    "web-dev",
    "android-dev",
    "ios-dev",
    "desktop-dev",
    "backend-dev",
    "debugger",
    "reviewer",
    "qa",
    "rollback",
    "security",
    "legal",
    "dashboard",
    "devops",
    "growth",
    "social-media",
    "explainer-writer",
    "optimizer",
}
EXECUTION_MODES = {
    "sequential-role-mode",
    "separate-agent-justified",
    "qualified-external-review",
    "operational-procedure",
    "not-applicable",
}
ROLE_ID = re.compile(r"^ROLE-[A-Z0-9-]+$")
ARTIFACT_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[0-9]{3}$")
CATALOG_VERSION = re.compile(r"^\*\*Schema version:\*\* (\d+\.\d+\.\d+)\s*$")
EXPECTED_COUNT = re.compile(r"^\*\*Expected source-role count:\*\* (\d+)\s*$")
SUPPORTED_SCHEMA_MAJOR = 1


def markdown_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def catalog_table(lines: list[str]) -> tuple[list[str], list[tuple[int, list[str]]]] | None:
    for index, line in enumerate(lines):
        header = markdown_cells(line)
        if not header or "role_id" not in header:
            continue
        if index + 1 >= len(lines):
            return header, []
        separator = markdown_cells(lines[index + 1])
        if not separator or any(not re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
            return header, []
        rows: list[tuple[int, list[str]]] = []
        for row_index in range(index + 2, len(lines)):
            cells = markdown_cells(lines[row_index])
            if cells is None:
                break
            rows.append((row_index + 1, cells))
        return header, rows
    return None


def validate_catalog(root: Path, catalog: Path) -> list[str]:
    problems: list[str] = []
    try:
        text = catalog.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{catalog}: cannot read catalog ({exc})"]
    lines = text.splitlines()

    versions = [CATALOG_VERSION.fullmatch(line.strip()) for line in lines]
    version = next((match.group(1) for match in versions if match), None)
    if not version:
        problems.append("catalog must declare a semantic schema version such as 1.0.0")
    elif int(version.split(".", maxsplit=1)[0]) != SUPPORTED_SCHEMA_MAJOR:
        problems.append(
            f"unsupported catalog schema major version '{version}'; "
            f"this validator supports major {SUPPORTED_SCHEMA_MAJOR}"
        )

    counts = [EXPECTED_COUNT.fullmatch(line.strip()) for line in lines]
    expected_count = next((int(match.group(1)) for match in counts if match), None)
    if expected_count is None or expected_count < 1:
        problems.append("catalog must declare a positive expected source-role count")

    parsed = catalog_table(lines)
    if not parsed:
        return problems + ["catalog must contain one Markdown role table with a role_id column"]
    headers, rows = parsed
    missing = [column for column in REQUIRED_COLUMNS if column not in headers]
    if missing:
        return problems + ["catalog is missing required column(s): " + ", ".join(missing)]
    if len(set(headers)) != len(headers):
        problems.append("catalog table contains duplicate column names")

    seen_ids: set[str] = set()
    seen_source_roles: set[str] = set()
    known_artifacts: set[str] = set()
    for artifact_path in markdown_files(root):
        metadata, metadata_error = read_front_matter(artifact_path)
        if metadata_error is None and metadata.get("id"):
            known_artifacts.add(metadata["id"])

    for line_number, cells in rows:
        if len(cells) != len(headers):
            problems.append(
                f"line {line_number}: expected {len(headers)} table cells, found {len(cells)}"
            )
            continue
        values = dict(zip(headers, cells, strict=True))
        for column in REQUIRED_COLUMNS:
            if not values[column].strip():
                problems.append(f"line {line_number}: required field '{column}' is empty")

        role_id = values["role_id"]
        if role_id and not ROLE_ID.fullmatch(role_id):
            problems.append(f"line {line_number}: invalid role_id '{role_id}'")
        if role_id in seen_ids:
            problems.append(f"line {line_number}: duplicate role_id '{role_id}'")
        seen_ids.add(role_id)

        source_role = values["source_role"].casefold()
        if source_role in seen_source_roles:
            problems.append(f"line {line_number}: duplicate source_role '{values['source_role']}'")
        seen_source_roles.add(source_role)

        if values["classification"] and values["classification"] not in CLASSIFICATIONS:
            problems.append(
                f"line {line_number}: unsupported classification '{values['classification']}'"
            )
        if values["execution_mode"] and values["execution_mode"] not in EXECUTION_MODES:
            problems.append(
                f"line {line_number}: unsupported execution_mode '{values['execution_mode']}'"
            )

        references = [item.strip() for item in values["artifact_refs"].split(";")]
        for reference in references:
            if not ARTIFACT_ID.fullmatch(reference):
                problems.append(f"line {line_number}: invalid artifact reference '{reference}'")
            elif reference not in known_artifacts:
                problems.append(f"line {line_number}: artifact reference '{reference}' does not resolve")

    if expected_count is not None and len(rows) != expected_count:
        problems.append(
            f"catalog declares {expected_count} source roles but contains {len(rows)} role rows"
        )
    if len(seen_source_roles) != len(rows):
        problems.append("source_role values must be unique")
    missing_roles = sorted(FROZEN_SOURCE_ROLES - seen_source_roles)
    extra_roles = sorted(seen_source_roles - FROZEN_SOURCE_ROLES)
    if missing_roles:
        problems.append("catalog is missing pinned source role(s): " + ", ".join(missing_roles))
    if extra_roles:
        problems.append("catalog has role(s) outside the pinned source roster: " + ", ".join(extra_roles))
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog",
        type=Path,
        default=ROOT / "docs/framework/ROLE-CAPABILITIES-001.md",
        help="path to the role catalog (default: %(default)s)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root used to resolve canonical artifact references",
    )
    args = parser.parse_args()
    problems = validate_catalog(args.root.resolve(), args.catalog.resolve())
    if problems:
        for problem in problems:
            print(f"ERROR {problem}", file=sys.stderr)
        return 1
    print(f"Validated role catalog: {args.catalog.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
