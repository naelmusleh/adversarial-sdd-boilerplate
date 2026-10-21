#!/usr/bin/env python3
"""Initialize an application repository with the Adversarial SDD starter artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
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
FRAMEWORK_REVISION_RE = re.compile(r"^[a-f0-9]{40}$")
REQUIRED_METADATA = {"id", "type", "title", "status", "version", "created", "updated"}
APP_LOCKED_FILES = (
    "scripts/artifacts.py",
    ".sdd/G-REQ-HANDOFF.json.template",
    ".sdd/G-ARCH-CONTRACT.json.template",
    "docs/templates/app-project/gate-record.md.template",
    ".github/workflows/sdd-contract-validation.yml",
)
FRAMEWORK_SOURCE_PATHS = (
    "scripts/init_app_project.py",
    "scripts/artifacts.py",
    ".sdd",
    "docs/templates/app-project",
)

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
    "architect-handshake.md.template": "architecture/<APP>-ARCH-HANDSHAKE-001.md",
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
        if relative.startswith("docs/templates/"):
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


def framework_link(base: str, path: str, revision: str) -> str:
    return f"{base.rstrip('/')}/blob/{revision}/{path}"


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


def discover_framework_revision(explicit_revision: str | None = None) -> str:
    """Return an immutable source commit and reject dirty Git-backed inputs."""
    try:
        top_level = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        is_framework_checkout = Path(top_level).resolve() == ROOT.resolve()
    except (OSError, subprocess.CalledProcessError):
        is_framework_checkout = False

    if is_framework_checkout:
        try:
            status = subprocess.run(
                ["git", "status", "--porcelain", "--untracked-files=all", "--", *FRAMEWORK_SOURCE_PATHS],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise ValueError("Could not verify that framework source inputs match a clean commit.") from exc
        if status.stdout.strip():
            raise ValueError(
                "Framework source inputs have uncommitted changes. Commit them before initializing an app "
                "so the recorded framework revision identifies the copied source."
            )

    if explicit_revision is not None:
        revision = explicit_revision.strip().lower()
        if not FRAMEWORK_REVISION_RE.fullmatch(revision):
            raise ValueError("Framework revision must be an exact 40-character lowercase commit SHA.")
        if is_framework_checkout:
            try:
                head = subprocess.run(
                    ["git", "rev-parse", "--verify", "HEAD^{commit}"],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip().lower()
            except (OSError, subprocess.CalledProcessError) as exc:
                raise ValueError("Could not verify the explicit framework revision against the current checkout.") from exc
            if revision != head:
                raise ValueError(
                    "The supplied framework revision does not match the current Git checkout. "
                    "Use a clean checkout at that commit or provide the matching archive revision."
                )
        return revision
    if not is_framework_checkout:
        raise ValueError(
            "Could not identify an exact framework commit. When using a source archive, pass "
            "--framework-revision with the 40-character commit SHA for that archive."
        )
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD^{commit}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(
            "Could not identify an exact framework commit. When using a source archive, pass "
            "--framework-revision with the 40-character commit SHA for that archive."
        ) from exc
    revision = result.stdout.strip().lower()
    if not FRAMEWORK_REVISION_RE.fullmatch(revision):
        raise ValueError("Framework checkout did not resolve to an exact 40-character commit SHA.")
    return revision


def sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def generated_readme(
    name: str,
    prefix: str,
    framework_url: str,
    framework_revision: str,
    *,
    include_lifecycle_records: bool,
) -> str:
    first_decision_number = 2 if include_lifecycle_records else 1
    return f'''# {name}

**Project status:** Ideation
**Active gate:** None; discovery has not started
**Next action:** Give your AI agent the app idea, intended user, problem evidence, desired outcome, and known constraints. Ask it to draft `mission.md` and lead the [product discovery workflow]({framework_link(framework_url, "workflows/product-discovery.md", framework_revision)}) in this repository.
**Canonical status source:** [`backlog.md`](backlog.md)

This repository is the source of truth for {name}: its product decisions, code, and delivery evidence belong here. It was initialized from the reusable [Adversarial SDD template]({framework_url}/tree/{framework_revision}); there is no framework service to install or operate. The exact source revision is recorded in [`.sdd/framework.lock.json`](.sdd/framework.lock.json). No gate has passed and no product decisions are pre-approved by this starter.

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
2. Have the agent follow the [product discovery workflow]({framework_link(framework_url, "workflows/product-discovery.md", framework_revision)}) to draft `constitution.md`, `specification.md`, and `backlog.md`, then return only material decisions and the G-INTENT/G-REQ evidence for your review.
3. Keep `design.md` as the canonical experience contract. Use the [CX design workflow]({framework_link(framework_url, "workflows/cx-design.md", framework_revision)}) and link visual review evidence there.
4. Use [`backlog.md`](backlog.md) for prioritized, approved implementation work and the [lifecycle workflow]({framework_link(framework_url, "workflows/lifecycle.md", framework_revision)}) for the next stage.

## Gates and tools

Use the framework's [gate catalog]({framework_link(framework_url, "docs/framework/GATE-CATALOG-001.md", framework_revision)}) for transition criteria and its [tool and skill catalog]({framework_link(framework_url, "docs/framework/TOOL-CATALOG-001.md", framework_revision)}) to select currently available tools. Record applicable gates, their results, and evidence in `reviews/`; a score alone never passes a required gate.

## Artifact identities

This project uses the `{prefix}` prefix for stable artifact IDs. Do not reuse IDs. Keep gate results separate from artifact lifecycle statuses, and link decisions/reviews to the exact versions they affect.

## Framework checks

The generated SDD Contract Validation workflow checks artifact metadata, framework snapshot integrity, and populated G-REQ/G-ARCH handoffs. It does not run application tests or prove semantic correctness. Add the app's required code checks from its verification plan to CI and require the relevant status checks in repository settings before treating them as merge or release controls. A workflow file by itself does not block merges.

## Supporting records as needed

Create decision and review records when a decision or gate requires one; add architecture, delivery, and operations records when the lifecycle reaches those stages. The template source provides detailed record templates. This starter does not create empty lifecycle folders or imply that those gates have run.

The SDD `design.md` is canonical. The Impeccable `document` command writes `DESIGN.md` in its project root; on case-insensitive file systems this can collide with `design.md`. Run that command only in an isolated staging copy/worktree, review its output, then place the generated file under `.impeccable/generated/`. Never run it at this repository root.
'''


def generated_agents(framework_url: str, framework_revision: str) -> str:
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
        f"- {label}: {framework_link(framework_url, path, framework_revision)}"
        for label, path in links.items()
    )
    return f'''# Agent instructions

This is an application repository initialized from Adversarial SDD. Read this file and the canonical `mission.md`, `constitution.md`, `specification.md`, `design.md`, and `backlog.md` before substantive work.

- Keep application code and its product artifacts in this repository. The template source owns reusable procedures, not this application's implementation.
- Treat repository artifacts as the durable source of truth. Maintain stable IDs, versions, links, open-decision records, and gate evidence.
- Do not implement work that is blocked by a failed mandatory gate, unresolved owner decision, missing access, or unmet dependency. State the blocker and the next actionable step.
- AI agents perform authorized documentation and implementation work. The product owner makes material product decisions, accepts residual risk, and authorizes consequential external actions.
- At each coherent, verified task checkpoint, commit only reviewed in-scope files and inspect the staged diff. Push to the authorized feature branch when standing or task-specific push authorization exists; never force-push, bypass branch protection, merge, or deploy under this rule. If checks fail, authorization is absent, or the remote is unavailable, report the exact state and do not claim the change is complete or published.
- Do not claim checks, approvals, deployments, or production readiness without observed evidence.
- Keep `design.md` canonical. Do not run Impeccable `document` at this repository root; use an isolated staging copy and store reviewed generated output in `.impeccable/generated/`.
- Use `python3 scripts/artifacts.py list`, `validate`, and `new` for local artifact management. The helper is a snapshot of the framework tool; structural validation does not prove links, decisions, gate evidence, or app readiness.
- The `.sdd/framework.lock.json` file pins the exact framework commit and digests of the copied validator and handoff checks. Update it only as part of a reviewed framework migration.
- A passed G-REQ or G-ARCH record requires its corresponding populated manifest under `.sdd/`; the validator checks frozen files and exact digests. A passing validator is not itself a gate pass.
- Add SDD Contract Validation and app-specific required checks to branch protection before claiming they block merges. Do not treat this workflow alone as a release gate.
- Record each change's commit SHA, branch/ref, push outcome, required-check results, and review status in its task milestone.

## Framework procedures

Use the current procedures from the configured Adversarial SDD template source. Record the procedure path/version used in gate and review records.

- Gate catalog: {framework_link(framework_url, "docs/framework/GATE-CATALOG-001.md", framework_revision)}
- Tool and skill catalog: {framework_link(framework_url, "docs/framework/TOOL-CATALOG-001.md", framework_revision)}

{procedure_list}
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Human-readable application name")
    parser.add_argument("--prefix", required=True, help="Stable artifact prefix, e.g. ACME")
    parser.add_argument("--target", required=True, type=Path, help="New or empty application repository directory")
    parser.add_argument("--framework-url", help="Override the GitHub repository URL for the reusable framework")
    parser.add_argument("--framework-revision", help="Exact 40-character framework commit SHA (required for source archives)")
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
    try:
        framework_revision = discover_framework_revision(args.framework_revision)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
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
        destination.replace("<APP>", prefix): render_template(
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
        framework_revision,
        include_lifecycle_records=args.include_lifecycle_records,
    )
    outputs["AGENTS.md"] = generated_agents(framework_url, framework_revision)
    outputs[".gitignore"] = ".impeccable/staging/\n"
    outputs["scripts/artifacts.py"] = artifact_helper.read_text(encoding="utf-8")
    outputs["docs/templates/app-project/gate-record.md.template"] = render_template(
        (TEMPLATES / "gate-record.md.template").read_text(encoding="utf-8"),
        name=name,
        prefix=prefix,
        today=today,
    )
    outputs[".sdd/G-REQ-HANDOFF.json.template"] = (
        (ROOT / ".sdd" / "G-REQ-HANDOFF.json.template").read_text(encoding="utf-8")
        .replace("<APP>", prefix)
        .replace("<40-character framework commit SHA>", framework_revision)
    )
    outputs[".sdd/G-ARCH-CONTRACT.json.template"] = (
        (ROOT / ".sdd" / "G-ARCH-CONTRACT.json.template").read_text(encoding="utf-8")
        .replace("<APP>", prefix)
        .replace("<40-character framework commit SHA>", framework_revision)
    )
    outputs[".github/workflows/sdd-contract-validation.yml"] = (
        (TEMPLATES / "sdd-contract-validation.yml.template").read_text(encoding="utf-8")
    )
    lock = {
        "lock_version": 1,
        "framework_repository": framework_url,
        "framework_revision": framework_revision,
        "artifact_contract_id": "ARTIFACT-CONTRACT-001",
        "artifact_contract_version": 1,
        "locked_files": {
            relative: sha256_text(outputs[relative])
            for relative in APP_LOCKED_FILES
        },
    }
    outputs[".sdd/framework.lock.json"] = json.dumps(lock, indent=2, sort_keys=True) + "\n"
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
