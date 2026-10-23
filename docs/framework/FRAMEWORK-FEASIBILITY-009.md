---
id: FRAMEWORK-FEASIBILITY-009
type: feasibility-register
title: FW-TASK-028 risk-quality and traceability feasibility
status: draft
version: 1.0
created: 2026-10-23
updated: 2026-10-23
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-ADV-020, DECISION-026, FRAMEWORK-EXERCISE-007
---

# FRAMEWORK-FEASIBILITY-009 — FW-TASK-028 risk-quality and traceability feasibility

## Scope and exclusions

This is a bounded G-FEAS plan for FR-FW-029–031 under DECISION-026. It examines whether three already exercised synthetic framework profiles—Next.js/TypeScript, FastAPI/Python, and Rust/Axum—can report useful coverage and mutation evidence, bind task criteria to changed paths and checks at an exact revision, and expose anti-gaming limits.

The work uses generated toy fixtures on a disposable, secret-free hosted runner. It does not set numeric thresholds, change the framework repository's current checks, classify a real product task, collect user/product data, approve an exception, adopt another gate contract, implement FW-TASK-028, or authorize FW-TASK-024 or other v2 tasks. Measurement availability and cost are feasibility inputs, not policy decisions.

## G-REQ and source baseline

G-REQ passed for exact scope revision `dc4c982effad35652802278d301b532c555c6388`; independent findings are in [FRAMEWORK-ADV-020](../adversarial-reviews/FRAMEWORK-ADV-020.md). The approved requirements and seven backlog criteria remain the scope. FW-TASK-013 already exercised the three synthetic profile toolchains on hosted runners; its exact limitations and run evidence remain in [FRAMEWORK-FEASIBILITY-008](FRAMEWORK-FEASIBILITY-008-fw013.md) and [FRAMEWORK-ADV-019](../adversarial-reviews/FRAMEWORK-ADV-019.md). These are reusable setup observations, not evidence for FW-028 policy or anti-gaming behavior.

## Dated technical observations

Official tool documentation indicates candidate measurement capabilities:
- Vitest documents V8 and Istanbul coverage providers and coverage collection/configuration. Coverage is execution evidence and does not establish assertion quality: [Vitest coverage guide](https://vitest.dev/guide/coverage.html).
- Coverage.py documents branch measurement through its `--branch` option: [Coverage.py documentation](https://coverage.readthedocs.io/en/latest/).
- LLVM `llvm-cov` exports line and branch coverage; the `cargo-llvm-cov` subcommand is a candidate Rust adapter: [LLVM coverage command guide](https://llvm.org/docs/CommandGuide/llvm-cov.html), [cargo-llvm-cov project](https://github.com/taiki-e/cargo-llvm-cov).
- StrykerJS documents TypeScript/JavaScript mutation testing support: [StrykerJS introduction](https://stryker-mutator.io/docs/stryker-js/introduction/).
- Mutmut is a Python mutation-testing candidate: [mutmut documentation](https://mutmut.readthedocs.io/en/latest/).
- cargo-mutants is a Rust mutation-testing candidate: [cargo-mutants documentation](https://mutants.rs/).

These documents establish that candidate tools describe relevant features, not that their exact pinned versions interoperate with this repository's synthetic profiles or produce directly comparable scores. Mutation operators, equivalent-mutant handling, generated-code treatment, test selection, runtime, and tool support can vary. The probes must retain exact toolchain/tool versions and classify unsupported or unavailable results explicitly.

## Applicability screen

Applicable: toolchain installation and runtime compatibility; coverage and mutation report semantics; test fixture integrity; exact commit/path/check metadata; authorization evidence for exceptions; runner cost and duration; registry egress and supply-chain exposure; reproducibility and artifact retention.

Not applicable to this synthetic probe: real product security classification, customer/privacy data, data rights, application deployment, provider costs, production service SLOs, photo/media behavior, release authorization, and operational support. No production threshold or user-data decision is made.

Security boundary: use a temporary GitHub-hosted VM, read-only permissions, no secrets, no persistent checkout credentials, no product data, no source/host mounts, and no privileged token in child processes. Package-registry/network egress during setup remains exposed and must be disclosed. If a safe read-only runner cannot execute a probe, mark it unavailable; do not weaken permissions or claim isolation.

## Probe register

| Probe | Question and exact evidence | Classification rule | Requirements / dependency |
| --- | --- | --- | --- |
| FEAS-FW028-01 — coverage adapters | For each synthetic profile, can a clean target produce named line and branch/condition reports from pinned tools, identify measured source files and exclusions, and distinguish unavailable from zero or pass? Capture toolchain/tool versions, source and config digests, exact command/exit code, raw summary, excluded/generated paths, and repeated-run stability. | Supported only for exact profile/tool pins and report fields observed. A missing provider, unsupported metric, or missing report is unavailable/unsupported, never pass. No numeric threshold is evaluated. | FR-FW-029; FW-TASK-028 remains conditional on exact adapters and honest missing-metric behavior. |
| FEAS-FW028-02 — test-strength signals | In each profile, compare a trivial test that executes a target branch but lacks a meaningful assertion with a behaviorally asserted test. Seed one small non-equivalent behavior mutant that the asserted test kills; verify the trivial case may retain high execution coverage while failing to kill it. Capture mutant identity, kill/survive/compile-error/timeout status, command, duration, and report digest. | Demonstrates only the named mutation operators and fixtures. Do not compare mutation percentages across languages or treat a killed mutant as proof of correctness. If tooling cannot run reproducibly within a declared pilot budget, record that limitation and an alternative evidence path. | FR-FW-029, FR-FW-031; critical-invariant evidence remains a per-app policy choice. |
| FEAS-FW028-03 — exact task/path/check trace | On a frozen synthetic Git revision, map one selected task ID and all its acceptance-criteria IDs to changed paths and required check IDs. Exercise a valid complete mapping, an unmapped changed path, missing criterion, missing required check, stale source revision, and an authorized exception record. Capture manifest/source digests, Git diff path set, check identity/conclusion, diagnostics, and whether any source bytes changed. | Mapping is deterministic and revision-bound; stale/missing/unmapped cases fail closed or require an explicit exception. The probe must identify an independently verifiable authorization source. A free-form author name or self-asserted JSON field is insufficient evidence of authority. | FR-FW-030; exception authority and record fields are an open design item, not presumed resolved. |
| FEAS-FW028-04 — anti-gaming and exclusions | Try deliberately misleading cases: high line coverage with ineffective/trivial assertions; omitted exported symbol; generated file counted or excluded without declaration; and unrelated mixed-scope file. Check whether policy/trace validators surface each case without editing or deleting source. | Report what deterministic checks actually detect. If a case requires human judgment (e.g. an export is intentionally obsolete or a test assertion is semantically weak), classify it as review-required; no static metric may claim to prove semantic test quality or product intent. | FR-FW-031 and FW-TASK-028 criteria 2, 4, 6, 7. |

## Candidate trace and exception evidence

The probe should test a versioned, machine-readable trace shape carrying: repository identity; exact source commit; selected task ID; the complete selected acceptance-criteria ID set; changed canonical paths; required check IDs/names and exact run conclusions; declared generated/excluded paths with rationale; and trace-manifest revision/digest.

An exception candidate binds one missing/unmapped element to the exact source revision, task and criteria, affected path/check, reason, scope, authenticated authorizer identity and role, review/run reference, creation time, and expiry or revisit condition. The application must declare permitted authorizer roles. G-FEAS must establish whether the chosen CI/review provider can independently verify the identity and approval at that revision. The reviewer flagged this as unresolved at G-REQ; no particular user, role, team, or exception is pre-approved.

## Run method and safety

1. Have the independent reviewer assess this exact plan and fixture design before execution.
2. Freeze plan, generator, and workflow revisions. Use only generated toy code in temporary workspaces.
3. Run the four probes on a disposable hosted Linux VM using exact setup pins and read-only workflow permissions; do not pass the repository token into package/test/mutation processes.
4. Retain only bounded summaries: exact commit, OS/architecture, versions, paths/digests, named outcomes, duration, and error classification. Do not upload full source or environment variables.
5. Delete the temporary workflow and generated files after evidence capture. Run the repository's existing Verify Pipeline on the final evidence commit.
6. Update every probe's per-task dependency state and request independent review of the observed results. Stop on any false authorization, source mutation, secret exposure, missing exact-revision binding, or runner-boundary violation.

## G-FEAS acceptance and boundary

G-FEAS may pass only if the frozen probes establish feasible, bounded profile-specific metrics; show why raw coverage alone can mislead; demonstrate the available strength/limits of mutation and contract evidence; verify deterministic trace mapping and stale/missing behavior; and either verify an independent authorization source for exceptions or explicitly keep exceptions blocked pending a future owner-authorized alternative. Any unsupported metric or unverified authorization path must be reported as such and cannot produce a PASS claim. No numeric threshold is selected here.

Even a G-FEAS PASS would authorize only architecture planning within DECISION-026. Implementation remains blocked pending subsequent gate evidence. The framework repository's current test/coverage policy is unchanged. FW-TASK-024 and all other proposed v2 work remain excluded.

## Initial status

Plan prepared 2026-10-23. No FW-028 feasibility probe has run. The three FW-013 profile toolchains are prior setup observations only. Next action: independent exact-revision plan review; after plan approval, run the bounded probes and record results.
