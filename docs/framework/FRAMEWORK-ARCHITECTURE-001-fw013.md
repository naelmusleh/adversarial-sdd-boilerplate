---
id: FRAMEWORK-ARCHITECTURE-001
type: architecture-overview
title: FW-TASK-013 governance core and profile architecture
status: in-review
version: 0.2
created: 2026-10-23
updated: 2026-10-23
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-008, FRAMEWORK-EXERCISE-007, FRAMEWORK-ADV-017, FRAMEWORK-ADV-018, FRAMEWORK-GATE-CONTRACT-001, DECISION-LOG-001, DECISION-023, DECISION-025
---

# FRAMEWORK-ARCHITECTURE-001 — FW-TASK-013 architecture

## Scope and frozen inputs

This is a framework-only architecture proposal for FR-FW-025–027 under DECISION-023. It defines a runtime-neutral governance core, opt-in and separately versioned Next.js/TypeScript, FastAPI/Python, and Rust/Axum profiles, an explicit initializer composition contract, and stable versioned interfaces. It is not an implementation, support certification, package split, application architecture, or product decision.

| Input | Exact source / authority | Application to this architecture |
|---|---|---|
| Requirements and bounded task | FRAMEWORK-SPEC-001 FR-FW-025–027; FRAMEWORK-BACKLOG-001 FW-TASK-013 | Normative scope and acceptance criteria. |
| Owner decision | DECISION-023 (owner-approved bounded scope) | Allows this framework task only; excludes FW-TASK-028/FW-TASK-024 and repository split, extraction, migration. |
| Accepted sample | FRAMEWORK-EXERCISE-007 v0.2, `sha256:2bb91ef415110b336eb653c9ffaf9b1c1822d65ccad94b7710407ecd5357c17b`; DECISION-025 | Synthetic fixture only. Its Gallery facts do not select app stack/provider or expand app scope. |
| Feasibility | FRAMEWORK-FEASIBILITY-008, G-FEAS bounded PASS; FRAMEWORK-ADV-017 | Supports architecture planning at tested pins/commands only; no composer, isolation, initializer, or permanent-support claim. |
| Gate | FRAMEWORK-GATE-CONTRACT-001 GARCH-01–03 | Defines the architecture, ADR/task readiness, structural checks, frozen handoff, and independent-review criteria. |

Inputs freeze at review time by SHA-256 in the review record. A changed requirement, sample digest, feasibility condition, or decision invalidates affected architecture and downstream evidence.

## System boundary and context

The system being architected is the **framework's local initializer and governance helpers** plus the generated application's copied governance artifacts. The framework operates in a contributor's local checkout and in read-only CI. It is not a hosted agent runtime, policy service, package registry, application backend, or security sandbox.

```text
Owner / contributor
  └─ explicit initializer request: core + zero or more named profiles
       ├─ governance core (artifact IDs, lifecycle, evidence, validation contracts)
       ├─ selected profile manifests and profile-owned templates/check declarations
       └─ generated app tree + provenance manifest + per-check outcomes

Application code and its runtime are outside the framework core boundary.
```

Trust boundaries:

1. **Framework source → initializer:** repository content and profile declarations are trusted only at the exact reviewed framework revision. Project names, output paths, and CLI values are untrusted input; canonical-path validation and no-overwrite behavior remain required implementation controls.
2. **Initializer → target tree:** generation writes only within the explicitly selected empty target, creates the core once, composes only explicitly selected profile files, and records a deterministic inventory. A collision, unknown profile, invalid manifest, path escape, or unmet required prerequisite aborts before reporting success. Atomic staging/rename or a recoverable transaction is required before partial output can be called initialized.
3. **Generated app → project/CI:** generated governance validates declared artifacts and checks. Application source, dependency install/build steps, and model-produced records are untrusted; no secrets or write-capable credentials are supplied to checks executing project code.
4. **Profile → core / other profiles:** profiles are declarative adapters with separate version and dependency namespaces. Core imports/invokes no profile dependency unless the profile is explicitly selected. A selected profile cannot alter core gate semantics or silently add another profile's files, instructions, dependencies, or checks.

## Ownership, data, and interfaces

| Component | Owns | Reads | Writes / emits |
|---|---|---|---|
| Governance core | Gate/artifact identity, lifecycle semantics, evidence shape, core validation | Core artifacts and explicit selection manifest | Core files, core validation result; no stack-specific command result unless profile selection exists |
| Profile adapter | Versioned runtime/prerequisite/layout/check declaration and its own templates | Only core interface plus its own declared source inputs | Its own generated files and check outcomes |
| Initializer/composer | Selection, compatibility validation, staging, provenance, outcome aggregation | Core contract, selected profile manifests, target state | Generated inventory and manifest; never edits source templates or product files outside target |
| Application | Product data, runtime, secrets, persistence, providers, app checks | App-owned requirements and generated governance | Outside FW-TASK-013 implementation; no product state is owned by this framework architecture |

There is no persistent framework service database. Durable canonical state is version-controlled framework/app artifacts. Generated manifests are snapshots, not authorities over gate PASS. CI run outputs remain evidence only for their exact source revision and declared command.

**Profile selection contract:** an explicit list of profile IDs and exact profile versions; absence means core-only. Duplicate, unknown, incompatible, or unsupported selections fail before writing. Each selected profile declares the required fields in `profile-manifest-v1.schema.json`; its `checks` object uses each check ID as a unique key and one `status` (`applicable` or `unsupported`), so one check cannot appear in both categories. The strict JSON loader rejects duplicate keys before schema validation. The generated selection manifest records framework/core contract revision, each selected profile ID/version and source digest, generated file path+digest inventory, prerequisite observations, and the exact applicable/unsupported check declarations. It is covered by `profile-selection-manifest-v1.schema.json` and is not a check result or gate PASS.

The check runner emits a separate `profile-check-result-v1` record bound to the exact selection-manifest digest, framework revision, and each profile-manifest digest. For profile and selection manifests, the digest input is canonical JSON encoded as UTF-8 with lexicographically sorted object keys, separators `,` and `:` without extra whitespace, no trailing newline, and no non-finite numeric values; check-result records bind that digest. Generated-file digests remain SHA-256 of exact generated bytes. Selected profile IDs and check IDs are nested object-map keys, so the same identity cannot occur twice; the strict JSON loader rejects duplicate raw keys. `passed` requires the exact command and exit code 0; `failed` requires a command and nonzero exit; `not-run`, `not-configured`, and `unsupported` require a reason and cannot carry an exit code. The structural cross-record check requires the check record's framework revision and selected profiles to match the selection manifest, the profile digest and declarations to match the selected profile manifest, every check to be declared, every prerequisite to be declared, and every generated path/owner to match a selected source. The runner derives readiness, it does not accept it as input: a selected profile is ready only when every required applicable check has an observed `passed` result and all required prerequisites are observed available. Any required failure, missing result, unsupported/not-configured/not-run state, or unavailable prerequisite blocks readiness. Optional non-passing checks remain visible and never count as passed. The selected-scope aggregate is ready only when all explicitly selected profiles are ready. Core-only means no application profile was selected and makes no profile-support claim. None of these states passes an SDD lifecycle gate by itself.

**Cross-module sample contract:** FRAMEWORK-EXERCISE-007's `GalleryItemV1` is a synthetic compatibility fixture, not a framework product model. Its required fields, unknown-field handling, major-version rejection, stable identity, and removal visibility are preserved only to exercise independent consumers. The profile architecture does not infer upload, storage, authorization, deletion/purge, Gallery service boundaries, or a production API from the fixture.

## Security, privacy, and failure behavior

- The tool processes framework text and app project files. Framework fixtures contain synthetic metadata; this task neither receives nor stores photos, credentials, or application data.
- No network/provider integration or secret is needed for initializer composition. CI checks remain read-only. Any future dependency installation or app build is project-code execution and must use the app's separately approved checks/permissions; this architecture does not claim egress denial or sandboxing.
- Reject path traversal, symlink escapes, destination collisions, duplicate JSON keys, unknown schema versions, undeclared dependencies, and profile cross-loads. Do not overwrite canonical framework artifacts.
- On any preflight error, write nothing. During generation, stage to a sibling temporary directory and atomically finalize where supported; on interruption, preserve the prior target and remove only transaction-owned staging. If atomic finalization cannot be provided for a platform, fail closed and document the weaker recovery behavior before support is claimed.
- A failed or unavailable profile check cannot be converted to pass, skipped, or hidden by another profile's result. Aggregate result is non-passing when a selected profile's required check is failed, missing, unsupported, or unrun. Core-only success cannot be presented as selected-profile success.
- No service-level retention, disaster recovery, uptime, or support promise applies. Recovery means reproducible regeneration from versioned framework/app artifacts and a clean target; user/project source remains authoritative and is not deleted by cleanup.

## Deployment and operations

This architecture runs locally and in the existing repository/app CI. It adds no daemon, deployed endpoint, external provider, account model, persistent queue, or recurring worker. A clean CI checkout is the reproducibility boundary; checks report exact source revision, profile versions, tool versions, commands, exit statuses, and evidence references. CI configuration remains read-only and secret-free for untrusted pull request code. Registry access during package installation is an explicit supply-chain/egress exposure observed in G-FEAS; FW-TASK-013 may report it, not claim to control it.

Operational recovery is to discard only transaction-owned incomplete staging, retain the source tree, and rerun from an empty target with the same frozen core/profile revisions. No automated cleanup of a non-empty user target is allowed. No automatic update/migration of previously generated apps is defined by this task. Registry egress is not controlled or denied by this architecture.

## Architecture decisions (proposed for this bounded implementation)

### ADR-FW013-01 — Keep core and profiles in this repository as versioned modules

- **Decision:** Keep profile manifests/templates and core contracts in the existing framework repository, with explicit directory and version boundaries; do not extract or distribute separate packages in FW-TASK-013.
- **Alternatives:** (a) separate core repository/packages now; (b) one undifferentiated template; (c) versioned modules in this repository.
- **Evidence:** FEAS-FW013-04 only makes an analysis-only comparison; current helper validation and profile probes do not prove package independence. The owner explicitly excluded split/extraction/migration absent a separate proposal.
- **Authority/constraint:** DECISION-023 and FR-FW-025–027; a future split requires separate owner approval. This is a bounded implementation recommendation, not owner approval for a repository move.
- **Trade-off:** simpler one-revision provenance now; package release independence is not provided. Reopen if independent release cadence or version-conflict evidence demonstrates a need.

### ADR-FW013-02 — Compose only explicit, exact-version profile manifests

- **Decision:** Core-only is the default. Profiles are opt-in, independently versioned declarations; never infer profile from files or project name and never inherit commands/dependencies from another profile.
- **Alternatives:** implicit detection; one global stack; explicit profile selection.
- **Evidence:** FR-FW-025/026, accepted synthetic profile matrix, and G-FEAS's exact-command outcomes. The results do not prove the composer or leakage controls.
- **Authority/constraint:** DECISION-023 approved explicit profiles as task scope. The implementation must prove clean-target generation and leakage fixtures before reporting support.
- **Failure rule:** unknown version, invalid declaration, unmet required prerequisite, or collision aborts; unsupported optional checks remain visibly unsupported and non-passing.

### ADR-FW013-03 — Use major-versioned JSON contracts with fail-closed compatibility

- **Decision:** Profile manifests and cross-module payloads use versioned JSON Schema-compatible contracts. Consumers accept supported major versions, ignore only declared-compatible unknown optional fields, and reject unsupported major versions or missing required fields.
- **Alternatives:** unversioned ad hoc JSON; language-specific interfaces; shared versioned JSON contracts.
- **Evidence:** FRAMEWORK-EXERCISE-007 v0.2 and the six serialization outcomes observed across all three synthetic profiles. These prove only observed serialization results, not composition/leakage/runtime behavior.
- **Authority/constraint:** FR-FW-027 and owner-accepted sample digest DECISION-025. Any breaking field meaning/type requires a new major contract; compatibility policy is explicit per schema.

## Versioned structural contract

`schemas/profile-manifest-v1.schema.json` defines profile declarations; `schemas/profile-selection-manifest-v1.schema.json` defines generated selection/provenance; and `schemas/profile-check-result-v1.schema.json` defines command observations. [The isolated design-time contract verifier](../../experiments/fw013/validate_architecture_contracts.py) checks their Draft 2020-12 semantics, positive/negative instances, cross-record identity/ownership, readiness aggregation, and strict duplicate-key rejection; its temporary secret-free hosted workflow is evidence only and will be removed. These artifacts do not claim that current tools read or emit the formats. G-IMPL must add durable automated cases for all three contracts; compatibility and leakage behavior also need executable positive/negative fixtures.

## Implementation-ready work packages (all remain under FW-TASK-013)

| Work package | Scope and acceptance | Dependencies | Required verification |
|---|---|---|---|
| WP-013-A Core boundary | Keep existing artifact IDs, gate/evidence semantics and validator runnable with no app runtime; selecting no profile invokes no stack checks. | G-ARCH pass; FR-025. | Isolated core-only check records imports, child commands, and success/failure without app packages. |
| WP-013-B Profile contracts | Add separately versioned manifests for exactly Next.js/TypeScript, FastAPI/Python, Rust/Axum; each states prerequisites, versions, source layout, owned deps, applicable and unsupported checks. | WP-013-A; candidate pins in FEAS-008; no permanent support generalization. | Schema positives/negatives; selected-profile tests; missing-toolchain behavior; confirm no implicit inheritance. |
| WP-013-C Initializer composition | Add explicit profile-selection interface; default core-only; validate clean target, prerequisites, compatibility, deterministic inventory and source provenance; fail before writes for invalid selection. | WP-013-A/B; current initializer behavior recorded as baseline, not assumed to satisfy. | Clean-target fixtures for none/each profile/multiple/unknown/incompatible/duplicate/missing prerequisites/collisions; compare generated tree digests. |
| WP-013-D Cross-module contract | Pin the accepted synthetic exercise digest as test input; provide schema and valid/invalid compatibility cases, keep app-domain fixture isolated from core artifacts. | WP-013-B/C; DECISION-025. | Compare exact accept/reject matrix in three profiles; test major-version rejection and allowed unknown optional fields. |
| WP-013-E Composition leakage | Keep profile file/dependency/instruction sets disjoint and preserve core identities. | WP-013-C/D; implementation-level composer exists. | Inject wrong-profile dependency and instruction into isolated targets; require detection; clean composition passes; inspect generated inventories and canonical-source digests. |
| WP-013-F Layout comparison | Record single-repository versioned modules versus split-package costs/benefits only; no branch/repository/package/migration operation. | FEAS-FW013-04. | Review evidence and recommendation; any split recommendation becomes a separate owner-decision proposal. |

These work packages are acceptance mapping, not separate authorized tasks or an implementation authorization. Do not mark FW-TASK-013 complete until each applicable acceptance criterion has evidence and required checks pass. No profile support guarantee arises from G-FEAS or this architecture draft.

## Verification and handoff

| Criterion | Architecture evidence | Later implementation proof |
|---|---|---|
| GARCH-01 boundaries and failure/recovery | Boundary, ownership, security, privacy, operations and failure sections above | Clean-target, fail-closed, no-overwrite, interruption and recovery fixtures for WP-013-C/E |
| GARCH-02 ADRs and task readiness | ADR-FW013-01..03; WP-013-A..F linked to FR-025..027 and existing FW-TASK-013 | Each work-package check result, dependencies and changed paths recorded in selected task milestone |
| GARCH-03 schemas and frozen inputs | Three versioned contracts, semantic design-time fixtures, accepted sample digest, and exact-source review record | Durable schema/compatibility/leakage fixtures, then G-IMPL checks at exact commit |

**Next permitted transition:** after independent review passes G-ARCH and the exact-source handoff is recorded, FW-TASK-013 may enter G-IMPL within its approved scope. General/permanent profile support claims remain prohibited until the relevant implementation checks pass. Infinite Gallery product stack/provider/storage decisions, app implementation, native scope, repo split/extraction/migration, FW-TASK-028 and FW-TASK-024 remain excluded.
