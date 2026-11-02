---
id: CAP-001
type: framework-capability
title: Artifact Management
status: active
version: 0.7
created: 2026-10-05
updated: 2026-10-20
related-artifacts: ARTIFACT-CONTRACT-001, FRAMEWORK-002, FRAMEWORK-BACKLOG-001
---

# CAP-001 — Artifact Management

## Need

Durable framework and product work must be findable, consistently identified, and checked without treating chat as the archive.

## User

The product owner and AI agents contributing to the framework or an initialized application repository.

## Scope delivered

- A GitHub-ready repository layout and artifact conventions.
- A standard-library Python command-line tool to list, create, and validate Markdown artifacts in the framework repository.
- An app-root-aware copy of the same tool included in each initialized application repository so app artifacts can be managed without the framework checkout or ChatGPT Desktop.
- Metadata front matter with stable IDs and lifecycle fields.
- Recursive exclusion of `docs/templates/` scaffolding from the live artifact index and metadata validator.
- Discovery and structural validation of versioned workflow artifacts under `workflows/` as well as `docs/` and `framework/`.
- A machine-readable framework-template required-file and artifact-ID inventory in [`ARTIFACT-CONTRACT-001.json`](../../docs/framework/ARTIFACT-CONTRACT-001.json); a missing contract or listed file/artifact fails validation.
- RFC 2119 keyword checks for requirement tables under explicitly configured headings. The check requires stable IDs, non-empty requirement and acceptance-evidence cells, and uppercase normative keywords; it does not lint ordinary prose or judge requirement meaning.
- Versioned app framework locks that pin the source commit and SHA-256 digests of the copied validator, handoff/gate templates, and generated SDD CI workflow.
- Strict validation of populated G-REQ and G-ARCH JSON handoffs, including duplicate-key rejection, exact contract versions, safe repository paths, frozen artifact IDs/versions/digests, independent review references, explicit architecture checks, and gate-record linkage.
- A compatibility path for older app repositories: absence of the new lock/manifests retains their prior structural validation; any newly recorded G-REQ/G-ARCH pass must use the versioned handoff contract.
- Git history as the revision record; no duplicate database or generated registry to reconcile.

## Acceptance criteria

- A contributor can discover existing artifacts from the CLI.
- A contributor can scaffold a new artifact with a stable ID and required metadata.
- The tool detects missing required metadata, duplicate IDs, and filename/ID mismatches.
- Reusable templates nested below `docs/templates/` are not misclassified as project artifacts.
- Durable workflows are discoverable and validated instead of silently omitted from the artifact index.
- Established human-readable workflow paths retain their stable links while workflow identities are checked through unique metadata IDs.
- Artifact lifecycle metadata is checked against the status vocabulary in FRAMEWORK-002; gate outcomes remain a separate field in review records.
- A controlled omission of a required framework artifact, a malformed normative requirement, and a malformed acceptance-evidence row produce non-zero results with file/section/line diagnostics; valid uppercase requirement rows pass.
- The initialized-app profile continues to require `mission.md`, `constitution.md`, `specification.md`, `design.md`, and `backlog.md`; other app lifecycle records remain optional until their workflow requires them.
- No runtime package dependencies are required.
- An initialized app repository can list and validate its canonical SDD files and create new records in the appropriate app-owned folders.
- A generated app records its exact framework revision; controlled gate fixtures prove that passed G-REQ/G-ARCH records fail validation when their matching manifest or frozen evidence is missing or changed.

## Known limitations and next work

- Front matter is intentionally a constrained flat key/value format, not a full YAML parser.
- Validation checks the specified handoff fields and frozen-file integrity; it cannot judge whether the requirements, review, architecture, commands, or evidence are semantically adequate.
- Framework locks are integrity records, not signed attestations. Git history and required branch protection remain necessary to protect them from deliberate edits.
- Legacy app repositories are not silently migrated. They enter strict handoff validation when they adopt the lock and new gate metadata through a reviewed migration.

## Evidence

Implementation: [`scripts/artifacts.py`](../../scripts/artifacts.py). The tool detects the framework layout or initialized app layout relative to its own `scripts/` directory. CAP-004 copies this standard-library-only helper to new app repositories. Framework mode reads the checked-in artifact contract and validates required paths, stable artifact IDs, and configured requirement tables. App mode retains the five canonical root documents, checks configured requirement tables, and validates the framework lock and populated gate handoffs when adopted. Focused execution evidence for the versioned app profile is recorded under FW-TASK-015. These checks cover declared structure and frozen-file integrity; they do not prove semantic correctness, actual test execution, gate passage, application behavior, or production readiness.
