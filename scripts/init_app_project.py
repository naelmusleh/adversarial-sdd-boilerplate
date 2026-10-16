#!/usr/bin/env python3
"""Initialize an application repository with the Adversarial SDD starter artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "docs" / "templates" / "app-project"
DEFAULT_FRAMEWORK_URL = "https://github.com/naelmusleh/adversarial-sdd-boilerplate"
PREFIX_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*$")
ARTIFACT_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[0-9]{3}$")
REQUIRED_METADATA = {"id", "type", "title", "status", "version", "created", "updated"}

# The default is the smallest complete app starter: the five canonical SDD files.
# Supporting records are created when their lifecycle triggers are reached.
CORE_FILES = {
    "mission.md.template": "mission.md",
    "constitution.md.template": "constitution.md",
    "specification.md.template": "specification.md",
    "design.md.template": "design.md",
    "backlog.md.template": "backlog.md",
}

# Optional preseeded records for teams that explicitly prefer the full tree.
LIFECYCLE_FILES = {
    "decision-log.md.template": "decisions/DECISION-LOG.md",
    "decision-record.md.template": "decisions/DECISION-001.md",
    "review-record.md.template": "reviews/REVIEW-001.md",
    "gate-record.md.template": "reviews/GATE-REQ-001.md",
    "feasibility-register.md.template": "architecture/feasibility-register.md",
    "architecture-overview.md.template": "architecture/architecture.md",
    "architecture-decision-record.md.template": "architecture/ADR-001.md",
    "verification-plan.md.template": "delivery/verification-plan.md",
    "verification-record.md.template": "delivery/verification/VERIFY-001.md",
    "release-record.md.template": "delivery/releases/RELEASE-001.md",
    "operations-runbook.md.template": "operations/RUNBOOK.md",
}


def render_template(source: str, *, name: str, prefix: str, today: str) -> str:
    rendered = source.replace("<APP>", prefix).replace("<Application>", name)
    rendered = rendered.replace("YYYY-MM-DD", today)
    rendered = rendered.replace("<GATE-ID>", "REQ")
    rendered = rendered.replace("<Gate name>", "Requirements readiness")
    rendered = rendered.replace("<project/revision>", f"{name} initial")
    # A new project has not completed reviews, approved decisions, or release gates.
    rendered = re.sub(r"(?m)^status:.*$", "status: draft", rendered)
    return rendered


def validate_generated_artifacts(outputs: dict[str, str]) -> None:
    seen: set[str] = set()
    for relative, content in outputs.items():
        if not relative.endswith(".md") or not content.startswith("---\n"):
            continue
        lines = content.splitlines()
        try:
            end = lines.index("---", 1)
        except ValueError as exc:
            raise ValueError(f"{relative}: missing front matter terminator") from exc
        metadata: dict[str, str] = {}
        for line in lines[1:end]:
            if ":" not in line:
                raise ValueError(f"{relative}: invalid front matter line {line!r}")
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
        missing = REQUIRED_METADATA - metadata.keys()
        if missing:
            raise ValueError(f"{relative}: missing metadata {', '.join(sorted(missing))}")
        artifact_id = metadata["id"]
        if not ARTIFACT_ID_RE.fullmatch(artifact_id) or "<" in artifact_id or ">" in artifact_id:
            raise ValueError(f"{relative}: invalid generated artifact ID {artifact_id!r}")
        if artifact_id in seen:
            raise ValueError(f"{relative}: duplicate generated artifact ID {artifact_id}")
        seen.add(artifact_id)
        if metadata["status"] != "draft":
            raise ValueError(f"{relative}: starter artifact must begin in draft status")


def framework_link(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/blob/main/{path}"


def discover_framework_url() -> str:
    """Use the clone's GitHub origin when present, with a ZIP-friendly fallback."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return DEFAULT_FRAMEWORK_URL
    remote = result.stdout.strip()
    match = re.fullmatch(r"(?:https://github\.com/|git@github\.com:)([^/]+)/([^/]+?)(?:\.git)?/?", remote)
    if match:
        return f"https://github.com/{match.group(1)}/{match.group(2)}"
    return DEFAULT_FRAMEWORK_URL


def generated_readme(
    name: str,
    prefix: str,
    framework_url: str,
    *,
    include_lifecycle_records: bool,
) -> str:
    first_decision_number = 2 if include_lifecycle_records else 1
    return f'''# {name}

**Project status:** Ideation
**Active gate:** None; discovery has not started
**Next action:** Give your AI agent the app idea, intended user, problem evidence, desired outcome, and known constraints. Ask it to draft `mission.md` and lead the [product discovery workflow]({framework_link(framework_url, "workflows/product-discovery.md")}) in this repository.
**Canonical status source:** [`backlog.md`](backlog.md)

This repository is the source of truth for {name}: its product decisions, code, and delivery evidence belong here. It was initialized from the reusable [Adversarial SDD template]({framework_url}); there is no framework service to install or operate. No gate has passed and no product decisions are pre-approved by this starter.

## Local artifact commands

This repository includes the dependency-free artifact helper. Run it from this repository to list, validate, or create app artifacts:

```sh
python3 scripts/artifacts.py list
python3 scripts/artifacts.py validate
python3 scripts/artifacts.py new decision {prefix}-DECISION-{first_decision_number:03} "Choose the initial data-retention rule"
```

The helper discovers this repository's canonical SDD files and artifact folders; it does not read or change the separate framework checkout.

## Start here

1. Give the agent the app idea, intended user, problem evidence, desired outcome, and known constraints. The agent drafts [`mission.md`](mission.md) with you and records evidence, assumptions, exclusions, and unresolved decisions.
2. Have the agent follow the [product discovery workflow]({framework_link(framework_url, "workflows/product-discovery.md")}) to draft `constitution.md`, `specification.md`, and `backlog.md`, then return only material decisions and the G-INTENT/G-REQ evidence for your review.
3. Keep `design.md` as the canonical experience contract. Use the [CX design workflow]({framework_link(framework_url, "workflows/cx-design.md")}) and link visual review evidence there.
4. Use [`backlog.md`](backlog.md) for prioritized, approved implementation work and the [lifecycle workflow]({framework_link(framework_url, "workflows/lifecycle.md")}) for the next stage.

## Gates and tools

Use the framework's [gate catalog]({framework_link(framework_url, "docs/framework/GATE-CATALOG-001.md")}) for transition criteria and its [tool and skill catalog]({framework_link(framework_url, "docs/framework/TOOL-CATALOG-001.md")}) to select currently available tools. Record applicable gates, their results, and evidence in `reviews/`; a score alone never passes a required gate.

## Artifact identities

This project uses the `{prefix}` prefix for stable artifact IDs. Do not reuse IDs. Keep gate results separate from artifact lifecycle statuses, and link decisions/reviews to the exact versions they affect.

## Supporting records as needed

Create decision and review records when a decision or gate requires one; add architecture, delivery, and operations records when the lifecycle reaches those stages. The template source provides detailed record templates. This starter does not create empty lifecycle folders or imply that those gates have run.

The SDD `design.md` is canonical. The Impeccable `document` command writes `DESIGN.md` in its project root; on case-insensitive file systems this can collide with `design.md`. Run that command only in an isolated staging copy/worktree, review its output, then place the generated file under `.impeccable/generated/`. Never run it at this repository root.
'''


def generated_agents(framework_url: str) -> str:
    links = {
        "lifecycle": "workflows/lifecycle.md",
        "discovery": "workflows/product-discovery.md",
        "adversarial review": "workflows/adversarial-review.md",
        "CX design": "workflows/cx-design.md",
        "feasibility and architecture": "workflows/feasibility-architecture.md",
        "AI engineering execution": "workflows/ai-engineering-execution.md",
        "implementation quality gates": "workflows/engineering-quality-gates.md",
        "release and operations": "workflows/release-operations.md",
    }
    procedure_list = "\n".join(
        f"- {label}: {framework_link(framework_url, path)}"
        for label, path in links.items()
    )
    return f'''# Agent instructions

This is an application repository initialized from Adversarial SDD. Read this file and the canonical `mission.md`, `constitution.md`, `specification.md`, `design.md`, and `backlog.md` before substantive work.

- Keep application code and its product artifacts in this repository. The template source owns reusable procedures, not this application's implementation.
- Treat repository artifacts as the durable source of truth. Maintain stable IDs, versions, links, open-decision records, and gate evidence.
- Do not implement work that is blocked by a failed mandatory gate, unresolved owner decision, missing access, or unmet dependency. State the blocker and the next actionable step.
- AI agents perform authorized documentation and implementation work. The product owner makes material product decisions, accepts residual risk, and authorizes consequential external actions.
- Do not claim checks, approvals, deployments, or production readiness without observed evidence.
- Keep `design.md` canonical. Do not run Impeccable `document` at this repository root; use an isolated staging copy and store reviewed generated output in `.impeccable/generated/`.
- Use `python3 scripts/artifacts.py list`, `validate`, and `new` for local artifact management. The helper is a snapshot of the framework tool; structural validation does not prove links, decisions, gate evidence, or app readiness.
- Default to token-efficient `quiet` progress: report material milestones, observed check outcomes, blockers, and the next permitted action; summarize logs instead of pasting them. The owner may switch to `standard`, `detailed`, or `trace` at any time. No mode may hide failed checks, required evidence, or safety stops. Omit greetings, filler, and repeated summaries.
- Keep final chat output to targeted diffs or localized artifact changes. Load only task-relevant context and use repository artifacts to recover state; do not repeat full files or rely on chat history as the source of truth.
- Use one lead agent by default; use additional reviewers only when the selected gate requires them or the expected value warrants their usage. Stop after at most two author-review-revision rounds if blocking findings remain.
- Do not claim the $100 account-wide monthly cap is enforced unless an authoritative account-wide meter and hard stop cover Codex, agents, and tools. Distinguish measured, estimated, and unknown usage; treat omitted subagent/tool/background usage as unknown. Avoid optional paid calls with unknown costs when no applicable control is available.
- Do not automatically advance to another task or gate after the selected handoff. For owner-directed local checks, provide exact commands and mark them unverified until results are supplied; report automatic CI only after observing it on the exact revision.

## Framework procedures

Use the current procedures from the configured Adversarial SDD template source. Record the procedure path/version used in gate and review records.

- Gate catalog: {framework_link(framework_url, "docs/framework/GATE-CATALOG-001.md")}
- Tool and skill catalog: {framework_link(framework_url, "docs/framework/TOOL-CATALOG-001.md")}

{procedure_list}
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Human-readable application name")
    parser.add_argument("--prefix", required=True, help="Stable artifact prefix, e.g. ACME")
    parser.add_argument("--target", required=True, type=Path, help="New or empty application repository directory")
    parser.add_argument("--framework-url", help="Override the GitHub repository URL for the reusable framework")
    parser.add_argument(
        "--include-lifecycle-records",
        action="store_true",
        help="Preseed decision, review, architecture, delivery, and operations records",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the planned file list without writing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    name = " ".join(args.name.split())
    prefix = args.prefix.strip().upper()
    framework_url = (args.framework_url or discover_framework_url()).strip().rstrip("/")
    if not name:
        print("Application name must not be empty.", file=sys.stderr)
        return 2
    if not PREFIX_RE.fullmatch(prefix):
        print("Prefix must start with a letter and contain only uppercase letters, digits, or hyphens.", file=sys.stderr)
        return 2
    parsed = urlparse(framework_url)
    repo_parts = parsed.path.strip("/").split("/")
    if (parsed.scheme != "https" or parsed.netloc.lower() != "github.com"
            or len(repo_parts) != 2 or any(c.isspace() or c in "()<>" for c in framework_url)):
        print("Framework URL must be an HTTPS GitHub repository URL such as https://github.com/owner/repository.", file=sys.stderr)
        return 2
    repo_name = repo_parts[1].removesuffix(".git")
    if not repo_name:
        print("Framework URL must include a repository name.", file=sys.stderr)
        return 2
    framework_url = f"https://github.com/{repo_parts[0]}/{repo_name}"

    target = args.target.expanduser().absolute()
    if target.is_symlink():
        print(f"Refusing to initialize a symlink target: {target}", file=sys.stderr)
        return 2
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        print(f"Refusing to overwrite a non-empty or non-directory target: {target}", file=sys.stderr)
        return 2

    selected_files = CORE_FILES | (LIFECYCLE_FILES if args.include_lifecycle_records else {})
    missing = [filename for filename in selected_files if not (TEMPLATES / filename).is_file()]
    if missing:
        print("Starter package is incomplete; missing: " + ", ".join(missing), file=sys.stderr)
        return 2
    artifact_helper = ROOT / "scripts" / "artifacts.py"
    if not artifact_helper.is_file():
        print("Starter package is incomplete; missing: scripts/artifacts.py", file=sys.stderr)
        return 2

    today = dt.date.today().isoformat()
    outputs = {
        destination: render_template(
            (TEMPLATES / source).read_text(encoding="utf-8"),
            name=name,
            prefix=prefix,
            today=today,
        )
        for source, destination in selected_files.items()
    }
    outputs["README.md"] = generated_readme(
        name,
        prefix,
        framework_url,
        include_lifecycle_records=args.include_lifecycle_records,
    )
    outputs["AGENTS.md"] = generated_agents(framework_url)
    outputs[".gitignore"] = ".impeccable/staging/\n"
    outputs["scripts/artifacts.py"] = artifact_helper.read_text(encoding="utf-8")
    try:
        validate_generated_artifacts(outputs)
    except ValueError as exc:
        print(f"Starter package validation failed: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"Would initialize {name} ({prefix}) at {target}")
        for relative in sorted(outputs):
            print(f"  {relative}")
        return 0

    try:
        target.mkdir(parents=True, exist_ok=True)
        for relative, content in outputs.items():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation closes the race between the initial empty-target
            # check and writing. If another process creates a file meanwhile,
            # stop rather than replacing that file.
            with destination.open("x", encoding="utf-8") as output_file:
                output_file.write(content)
    except OSError as exc:
        print(f"Initialization stopped: {exc}", file=sys.stderr)
        return 1
    print(f"Initialized {name} ({prefix}) at {target}")
    print(f"Created {len(outputs)} files. Review mission.md and README.md before proceeding.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
