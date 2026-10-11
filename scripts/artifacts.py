#!/usr/bin/env python3
"""Dependency-free artifact helper for framework and initialized app repositories."""

from __future__ import annotations

import argparse
import datetime as dt
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
ALLOWED_STATUSES = {
    "draft", "in-review", "revision-required", "approved", "active",
    "blocked", "superseded", "retired",
}
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[0-9]{3}$")
KEY_RE = re.compile(r"^([a-z][a-z0-9-]*):\s*(.*?)\s*$")


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
    app_project = is_app_project(ROOT)
    if app_project:
        for filename in missing_app_canonical_files(ROOT):
            problems.append(f"{filename}: required app SDD root file is missing")
    elif not markdown_files(ROOT):
        problems.append("no artifacts discovered; refusing to validate an empty repository")
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
