---
id: CAP-001
type: framework-capability
title: Artifact Management
status: active
version: 0.5
created: 2026-10-05
updated: 2026-10-08
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
- Git history as the revision record; no duplicate database or generated registry to reconcile.

## Acceptance criteria

- A contributor can discover existing artifacts from the CLI.
- A contributor can scaffold a new artifact with a stable ID and required metadata.
- The tool detects missing required metadata, duplicate IDs, and filename/ID mismatches.
- Reusable templates nested below `docs/templates/` are not misclassified as project artifacts.
- Durable workflows are discoverable and validated instead of silently omitted from the artifact index.
- Established human-readable workflow paths retain their stable links while workflow identities are checked through unique metadata IDs.
- Artifact lifecycle metadata is checked against the status vocabulary in FRAMEWORK-002; gate outcomes remain a separate field in review records.
- No runtime package dependencies are required.
- An initialized app repository can list and validate its canonical SDD files and create new records in the appropriate app-owned folders.

## Known limitations and next work

- Front matter is intentionally a constrained flat key/value format, not a full YAML parser.
- Validation is structural; it does not yet validate cross-references, version history, or status transitions.
- Add link validation and richer schemas only when real work demonstrates the need.

## Evidence

Implementation: [`scripts/artifacts.py`](../../scripts/artifacts.py). The tool detects the framework layout or the initialized app layout relative to its own `scripts/` directory. CAP-004 copies this standard-library-only helper to new app repositories. Fresh generation produced 21 files and 16 uniquely identified draft artifacts; the copied app helper validated all 16, listed the app specification, created a new decision in `decisions/`, then validated 17 artifacts. The framework helper also passed repository validation with 33 artifacts after these changes. These checks cover structure and CLI behavior; link, decision, gate, application, and production readiness validation remain outside CAP-001.
