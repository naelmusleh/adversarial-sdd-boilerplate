---
id: FRAMEWORK-COVERAGE-001
type: framework-coverage
title: FW-TASK-028 journey and surface coverage
status: draft
version: 0.1
created: 2026-10-23
updated: 2026-10-23
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-009, DECISION-026, GATE-CATALOG-001, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-COVERAGE-001 — FW-TASK-028 journey and surface coverage

## Gate work record

- **Gate:** G-COVERAGE — in progress; no pass is asserted.
- **Task:** FW-TASK-028.
- **Approved requirements:** FR-FW-029, FR-FW-030, FR-FW-031 under DECISION-026.
- **Prerequisite:** G-REQ passed for the approved bounded scope; G-FEAS passed within its bounded feasibility scope in FRAMEWORK-FEASIBILITY-009.
- **Source baseline:** feature branch `codex/v2-backlog-roadmap`, work-record checkpoint `f696af1e791f97e0e41204e7ff0af18d821a30d9`; this artifact will be assessed on its own exact committed revision.
- **Boundary:** coverage planning and interaction-surface mapping only. No code implementation, numeric threshold selection, production-validator claim, positive exception authorization, FW-TASK-024, or other v2 task is included.
- **Proposed scope interpretation for independent review:** the capability is part of a local-first framework, not a hosted end-user application. Its interaction surfaces are local repository/CLI artifacts, hosted CI/check results, and pull-request review. Next.js/TypeScript, FastAPI/Python, and Rust/Axum are synthetic verification profile lanes, not product platform commitments. No Android or iOS client is declared by DECISION-026 or the framework mission. If this interpretation is not supported, G-COVERAGE remains blocked pending the necessary owner scope decision.

## Capability and user roles

The capability lets an application team declare its own quality policy, connect a selected task and its acceptance criteria to changed paths and required checks, inspect evidence tied to the tested source revision, and understand when a result is missing, stale, unavailable, or fail-closed. Framework agents prepare records and diagnostics. The application owner decides scope, risk policy, and any permitted exception authority. Developers/reviewers inspect changes and resolve findings. CI reports measurements and provider checks; it does not decide product intent or exception authority.

This artifact describes intended flows derived from FR-FW-029–031. It is not evidence that a production validator or UI exists.

## Journey and state inventory

| Journey | Requirement IDs | Actor | Preconditions and start | Main transitions | Success exit | Failure exits | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J-028-01 — Declare app quality policy | FR-FW-029, FR-FW-031 | App owner with agent assistance | App requirements and a selected stack profile exist; owner opens policy authoring in the repository. | Choose risk dimensions → declare applicable metrics, scope, thresholds, exclusions and rationale → mark unsupported metrics unavailable → review the versioned policy. | Policy is complete, app-owned and versioned; threshold rationale and limits are reviewable; no framework default is inherited silently. | Missing rationale or required field; unsupported metric represented as passing; profile or threshold silently copied from framework defaults. | Correct policy and record a reviewed version; keep unavailable metrics explicit; retain the prior version for comparison. |
| J-028-02 — Bind a change to task intent | FR-FW-030 | Developer/agent | A task and its complete acceptance-criteria set are approved; the candidate source revision and changed paths are known. | Select task → enumerate all criteria → map each changed canonical path to applicable criteria → declare required check identities → freeze the trace manifest to the source revision. | Every changed path and criterion has a deterministic link and the manifest names the exact revision and required checks. | Missing task/criterion/path/check link; duplicate or swapped semantic mapping; stale revision; unknown path; attempted self-asserted exception. | Fix mapping and regenerate at the new revision; preserve a failed diagnostic; an exception remains blocked unless an independently authorized, scoped approval path is configured. |
| J-028-03 — Run quality and anti-gaming checks | FR-FW-029, FR-FW-031 | CI runner with agent/developer as consumer | A versioned app policy, trace manifest and exact source revision are available; required profile adapter is supported. | Select policy checks → run profile-native tests/metrics → compare expected exports and generated-path declarations → detect weak assertion, omitted export, unclassified generated path or unrelated change → report results and source digests. | Each supported check reports its method, scope, revision and result; unavailable checks remain unavailable; diagnostics do not mutate source. | Check fails or is missing; adapter/metric unavailable; line coverage is high but assertions miss a boundary mutant; export/generated/mixed-scope discrepancy appears; input changes during the probe. | Stop any pass claim, retain bounded diagnostics, fix policy/tests/mapping, then rerun on the exact updated source revision. |
| J-028-04 — Review results and resume safely | FR-FW-029, FR-FW-030, FR-FW-031 | Reviewer and app owner | CI results and provider check identities are linked to the candidate revision; review occurs in pull-request UI or equivalent. | Inspect task/criteria/path/check links → verify check identities and conclusions match source SHA → review risk/quality diagnostics → accept, request changes, or leave blocked → resolve and rerun if needed. | Reviewer can trace each claim to the same source revision and understands limits, exclusions and unavailable states. | Missing/stale provider result; unsuccessful/in-progress check; authorization source unavailable; discrepancy lacks owner or disposition; review input does not match current revision. | Keep the gate blocked or request changes; update exact revision and rerun required checks; do not treat an unverified exception as accepted. |

### Requirement and task-criterion coverage

| Requirement / acceptance criterion | Covered journey(s) | Observable state or evidence |
| --- | --- | --- |
| FR-FW-029 | J-028-01, J-028-03 | Versioned app-owned policy; per-profile metrics, thresholds, exclusions, unavailable state and rationale; no claim that coverage alone proves correctness. |
| FR-FW-030 | J-028-02, J-028-04 | Revision-bound task/criteria/path/check manifest; exact provider check identity/conclusion; stale, missing, unmapped and unauthorized cases fail closed. |
| FR-FW-031 | J-028-01, J-028-03, J-028-04 | Stronger evidence is requested for critical behavior; adversarial diagnostics expose misleading claims; no source mutation; review/disposition is explicit. |
| FW-TASK-028 AC-1 | J-028-01, J-028-03 | Each supported profile declares its measurement policy and limitations; unavailable is not pass. |
| FW-TASK-028 AC-2 | J-028-01, J-028-03 | Risk classification routes critical domain/security/authorization/tenancy/migration behavior to stronger evidence; review can challenge misclassification. |
| FW-TASK-028 AC-3 | J-028-01 | Threshold rationale, scope and diagnostics are explicit; no task-level override silently lowers policy. |
| FW-TASK-028 AC-4 | J-028-03 | Profile lanes and behavior classes are considered separately; actual application coverage remains future implementation evidence. |
| FW-TASK-028 AC-5 | J-028-02, J-028-04 | Trace manifest binds selected task/criteria, paths, checks and exact revision; exceptions require authorization and remain fail-closed until supported. |
| FW-TASK-028 AC-6 | J-028-03 | Diagnostics only; no AST or trace finding deletes or rewrites source. |
| FW-TASK-028 AC-7 | J-028-03, J-028-04 | Weak/trivial tests, omitted exports, generated files and unrelated changes produce reviewable evidence without overstating semantic quality. |

## Surface and profile applicability

| Surface/profile | Platform or execution context | Applicability | Rationale and boundary |
| --- | --- | --- | --- |
| Local repository and CLI | Developer/agent worktree; host OS is not specified by this task | Applicable | Policy and trace artifacts are authored/reviewed here. This task does not claim cross-OS runner compatibility or sandboxing. |
| Hosted CI and provider checks | GitHub Actions / GitHub Checks on exact repository revisions | Applicable | Measures and provider check IDs/conclusions are observed here. G-FEAS established provider check-run identity for one bounded feature-branch run; production validator integration remains unimplemented. |
| Pull-request review | GitHub web review surface or equivalent review UI | Applicable | Owner/reviewer examines mappings, exceptions, diagnostics and evidence. A positive exception authorization is unavailable; the path remains fail-closed. |
| Next.js/TypeScript profile lane | Synthetic web-profile fixture in hosted CI | Applicable as a measurement adapter only | Prior FW-TASK-013 and FW-TASK-028 probes exercised this stack fixture. It does not declare an app user-facing web product or demonstrate production integration. |
| FastAPI/Python profile lane | Synthetic API-profile fixture in hosted CI | Applicable as a measurement adapter only | Prior probes establish bounded tool behavior only; no production adapter support is claimed. |
| Rust/Axum profile lane | Synthetic API-profile fixture in hosted CI | Applicable as a measurement adapter only | Prior probes establish bounded tool behavior only; branch coverage is unavailable on the pinned stable toolchain. |
| Native Android/iOS app UI | No native mobile client in the approved FW-TASK-028 scope | Not applicable | DECISION-026 and MISSION-001 declare a reusable local-first framework capability, not a native app UI. The tested stack profiles are not mobile platforms. Revisit if an owner-approved product surface later introduces a mobile client. |

## Required failure-mode applicability

All seven G-COVERAGE categories are applicable to this policy and evidence workflow.

| Category | Applicable | Expected state and reason |
| --- | --- | --- |
| Empty | Yes | Missing policy, task, criteria, path set or result set cannot imply a passing assessment. |
| Malformed or corrupt | Yes | Invalid policy/trace data or corrupted evidence must be rejected with a diagnostic. |
| Unavailable | Yes | Unsupported metric, absent adapter, provider API failure or missing check identity is reported unavailable/blocked, never passed. |
| Unauthorized | Yes | An exception without a configured, independently verifiable authorized identity is rejected; current behavior remains fail-closed. |
| Degraded | Yes | Partial/in-progress checks, incomplete profile output or provider degradation cannot support a complete pass claim. |
| Abuse | Yes | Trivial coverage inflation, criterion/path gaming, omitted exports, generated-file omission and unrelated changed files must be surfaced. |
| Recovery | Yes | After policy, test or mapping corrections, results must be regenerated for the new exact revision; stale results remain invalid. |

## G-COVERAGE criterion review

| Criterion | Prepared evidence | Current status |
| --- | --- | --- |
| GCOV-01 | J-028-01 through J-028-04 map all approved requirements and all seven task acceptance criteria to actors, preconditions, transitions, exits and recovery. | Prepared; independent review pending. |
| GCOV-02 | Empty, malformed/corrupt, unavailable, unauthorized, degraded, abuse and recovery categories are each explicitly included with expected fail-closed behavior. | Prepared; independent review pending. |
| GCOV-03 | Surface matrix includes only the approved framework interaction surfaces and clearly distinguishes synthetic stack-profile adapters from user-facing platforms; native mobile is explicitly excluded with rationale. | Prepared; owner/reviewer confirmation of scope interpretation pending. |

## Evidence, exclusions and next action

- **Evidence refs:** DECISION-026; FR-FW-029–031 in FRAMEWORK-SPEC-001; bounded G-FEAS evidence and provider-check limitations in FRAMEWORK-FEASIBILITY-009; GATE-CATALOG-001 and approved FRAMEWORK-GATE-CONTRACT-001 v1.0.
- **Exclusions:** No application-specific threshold values, real application stack, web/mobile end-user UI, positive exception authorization, production validator, code implementation, deployment, or release behavior is claimed.
- **Open scope interpretation:** Treat local CLI/repository artifacts, hosted CI checks, and pull-request review as this framework capability’s interaction surfaces. Stack profiles are adapters, not user-facing platform commitments. This is an inference from the approved framework mission and DECISION-026 and is submitted for independent review; an owner decision is required if the reviewer finds it materially changes the approved scope.
- **Current gate result:** In progress. No G-COVERAGE pass is claimed.
- **Next action:** Independent review of this exact artifact revision and its scope interpretation. If passed, prepare G-CX interaction-contract evidence for this nonvisual framework capability. If blocked on owner scope, stop and request that decision before G-CX.
- **Permitted next work:** Coverage review/remediation, then bounded G-CX design evidence if G-COVERAGE passes.
- **Prohibited next work:** Implementation, selecting app numeric thresholds, accepting exceptions, deploying, or starting excluded v2 tasks.
