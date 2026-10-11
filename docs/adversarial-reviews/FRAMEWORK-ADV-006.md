---
id: FRAMEWORK-ADV-006
type: adversarial-review
title: Independent local portability and artifact-safety review
status: approved
version: 0.1
created: 2026-10-10
updated: 2026-10-10
reviewed-artifact: CAP-004
reviewed-version: 0.3
related-artifacts: CAP-001, CAP-004, FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-BACKLOG-001, FRAMEWORK-ADV-003
---

# FRAMEWORK-ADV-006 — Local portability and artifact-safety review

## Review request

- **Scope:** Independently review CAP-004 v0.3, CAP-001 v0.5, `scripts/init_app_project.py`, `scripts/artifacts.py`, the app-project README and templates, and a fresh generated app repository.
- **Safety/conformance questions:** Does the copied helper root itself in the app repository and manage only app artifacts? Do `list`, `validate`, and `new` work against the app when invoked from another current directory? Are stable starter paths and IDs accepted? Do decision, ADR, and generic artifact paths validate? Are duplicate IDs and path collisions refused without overwriting data? Does app-mode fail closed for incomplete canonical SDD roots and empty repositories? Do generated docs accurately describe what the bootstrap and validator establish?
- **Comparison basis:** CAP-001, CAP-004, FRAMEWORK-001, FRAMEWORK-002, and the relevant app-project starter contracts.
- **Explicit exclusions:** GitHub access or repository creation, Git initialization/remote behavior, live cloud use, app implementation readiness, application feature correctness, and production deployment.
- **Reviewer role:** Independent verification; reviewed implementation and templates were not edited by this reviewer.
- **Evidence date:** 2026-10-10, America/New_York.

## Review method and limitations

- Inspected the named current artifacts and helper/initializer sources, including generated README and all app-project templates.
- Generated a fresh app in a temporary directory and invoked its copied helper from the framework repository working directory to test self-rooting behavior.
- Exercised list, validate, new for decision/ADR/generic types, duplicate-ID rejection, existing-path collision, initializer rerun refusal, incomplete-root behavior, and empty-directory validation.
- Injected a deterministic file-creation race between the preflight collision scan and exclusive file creation to verify that an intervening user file is not truncated.
- Temporary test repositories were removed after each run. No reviewed target was edited. These are local structural/safety checks, not a separate-app engineering pilot or staging exercise.

## Initial findings and dispositions

### FRAMEWORK-ADV-006/FINDING-001 — Copied helper must remain app-local

- **Severity:** Major
- **Initial evidence:** The original concern was that a helper could resolve a framework-root path and operate on framework artifacts after it had been copied into a separate app repository. That would make app validation/listing misleading and could direct new artifacts into the wrong repository.
- **Impact:** A user following the starter README from another working directory could read or mutate framework artifacts rather than the app's canonical SDD set.
- **Owner decision required:** No; CAP-001/CAP-004 already establish the separate application repository boundary.
- **Disposition:** **Verified resolved.** The copied helper resolves its root from its own `scripts` location. In the fresh-app exercise, it was invoked with the framework repository as the current working directory; it listed 16 app artifacts, including `QAAPP-SPEC-001`, and no `FRAMEWORK-` IDs. It did not list the app README or `AGENTS.md` as artifacts. App `validate` reported `Validated 16 artifact(s).`

### FRAMEWORK-ADV-006/FINDING-002 — Partial app roots could be misclassified as an empty framework repository

- **Severity:** Major
- **Initial evidence:** Before the fail-closed change, removing a required app SDD root file allowed the helper to fall back to framework mode: `list` returned zero, `validate` reported `Validated 0 artifact(s)` with exit 0, and `new` selected a fallback framework-style path. An empty directory could likewise validate zero artifacts.
- **Impact:** Missing canonical app documents could be hidden by a false successful validation, while new artifacts could be written outside their intended app artifact folders.
- **Owner decision required:** No; failing closed is required to preserve the canonical app layout contract.
- **Disposition:** **Verified resolved.** Current helper treats any canonical app root file as app mode. With `specification.md` removed, `list` exits 1 with an incomplete-layout error, `validate` exits 1 and names the missing required root file, and `new` exits 2 without creating either the canonical or fallback artifact. In an empty directory with the copied helper, `validate` exits 1 and reports that no artifacts were discovered rather than accepting zero artifacts.

### FRAMEWORK-ADV-006/FINDING-003 — Artifact creation had a check-then-write overwrite race

- **Severity:** Major
- **Initial evidence:** `new` performed a destination existence check before writing. If another file appeared after that preflight and before `write_text`, the later write could overwrite it. A pre-fix injected collision reproduced this behavior.
- **Impact:** A concurrent/user-created file at the target path could be silently truncated even though the initial collision check had passed.
- **Owner decision required:** No; refusing overwrite is part of artifact-management safety.
- **Disposition:** **Verified resolved.** Current implementation opens the destination exclusively and catches `FileExistsError`. In a deterministic race test, a sentinel file was injected immediately before the exclusive create; `new` exited 2 with a refusal message and preserved the sentinel contents.

## Current source identity

The hashes below identify the exact reviewed working-tree bytes; they do not imply a committed revision.

| Source | Version | SHA-256 |
| --- | --- | --- |
| `framework/capabilities/CAP-001-artifact-management.md` | CAP-001 v0.5 | `60d5b84980a0fd9f26a79689396cafae9d018d3eab19b748a97345ddccbe9d98` |
| `framework/capabilities/CAP-004-app-repository-bootstrap.md` | CAP-004 v0.3 | `f03832851538d7f6e6dfb75c77a8956e5cb38040abe83b275c5fe2fde775ed92` |
| `scripts/artifacts.py` | Working-tree implementation | `90e7d404f7ee7b5b2f7668f4e6ee73752d9e2e14dd0a2ce8dfce62beae924f07` |
| `scripts/init_app_project.py` | Working-tree implementation | `95b58d01f36a087920cdb44bbb5c76a1cdd123341096e83da4b2c732d1581f42` |
| `docs/templates/app-project/README.md.template` | Starter guide | `d4d78aca4292657c2328a4cf21b688f711f593faa47956a6a9a851012ef61062` |
| App-project README and 16 templates | Aggregate | `4d6b2a330b5e493f6243187bbb95b7a477273f63bb4d5613a4ab78a139c20e69` |

## Observed exercise results

- Fresh initialization created **21 files**, including **18 Markdown files**; expected canonical roots and stable starter paths were present.
- All **16/16** seeded artifact records had `status: draft`.
- Copied-helper `list` returned **16 app artifacts**, and validation passed with `Validated 16 artifact(s).`
- `new decision QAAPP-DECISION-002`, `new adr QAAPP-ADR-002`, and `new research-note QAAPP-RESEARCH-001` each wrote to the expected app artifact folder. Subsequent validation counts were 17, 18, and 19.
- Duplicate-ID request exited 2 and left the pre-existing artifact unchanged.
- Existing destination-path collision exited 2 and preserved sentinel content.
- Re-running initialization against the non-empty target refused; the generated mission remained unchanged.
- Missing `specification.md`: `list` exit 1, `validate` exit 1 with the missing file identified, and `new` exit 2 without writing an artifact.
- Empty repository: `validate` exit 1 with an explicit no-artifacts error.
- Intervening-file race injection: `new` exit 2; the injected sentinel remained intact.

## Generated-document claim boundaries

The generated README states that no gate has passed and that the helper does not read or change a separate framework checkout. Generated `AGENTS.md` says structural validation does not prove links, decisions, gate evidence, or app readiness. The starter guide and CAP-004 define the bootstrap as a local filesystem scaffold; the generated README does not claim that GitHub created a remote repository. This review did not test remote creation, authentication, or Git operations.

## Review result

- **Result:** **PASS for this bounded local portability and artifact-safety review.** All three findings are verified resolved by current-source inspection and observed local exercises. No new finding was identified within scope.
- **Acceptance evidence already present:** App-local root discovery, scoped artifact operations, starter IDs/paths, decision/ADR/generic creation, duplicate refusal, no-overwrite behavior including the race, incomplete-root failure, empty-repository failure, and accurate generated-document limits were exercised or inspected as recorded above.
- **Evidence still outstanding:** A separate application repository pilot with a real selected engineering task; owner/operator usability feedback; any app-specific link or gate-evidence validation; and staging/production behavior. These checks are outside this review and remain separate acceptance evidence where required by the backlog.
- **Backlog status:** This review does not mark CAP-001, CAP-004, or any framework backlog task complete.
- **Residual limitations:** Local temporary-directory behavior only; no GitHub, remote, authentication, permissions, deployment, app implementation, or production claims. The source hashes describe uncommitted working-tree contents.
