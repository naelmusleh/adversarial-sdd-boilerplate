---
id: FRAMEWORK-COVERAGE-004
type: coverage-matrix
title: FW-TASK-031 per-run limits and stop-condition journeys and surfaces
status: draft
version: 0.1
created: 2026-10-26
updated: 2026-10-26
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-012, FRAMEWORK-ADV-053, DECISION-036, GATE-CATALOG-001, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-COVERAGE-004 — FW-TASK-031 per-run limits and stop-condition journeys and surfaces

## Scope and evidence boundary

This is the G-COVERAGE journey/state inventory for FW-TASK-031 and FR-FW-038–040, approved by DECISION-036. It uses FRAMEWORK-FEASIBILITY-012's bounded findings: contract and synthetic-fixture work is feasible to explore; live counter collection is conditional; hard cancellation/resource enforcement and monetary spend remain blocked pending a selected controller and authoritative meter.

No runtime, provider, meter, threshold, spend policy, implementation, or application UI is adopted or implied. Journeys describe the future framework operator contract and distinguish states that are specified from capabilities that remain unavailable or unverified. Test fixtures may use labeled synthetic values only.

## Actors and journey inventory

| Journey | Actor | Entry / preconditions | Main transitions and decision points | Success and failure exits | Recovery | Surface(s) | Requirements / acceptance mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J-031-01 Define and validate a versioned per-run policy | Framework maintainer / authorized policy owner | A later implementation has a versioned policy schema; each enabled limit declares unit, run scope, accounting owner, start/reset rule, threshold action, enforcement source, and unavailable state. | Validate policy version and fields → resolve enabled counters and capabilities → label each `enforced`, `advisory`, or `unavailable` → reject unsupported combinations before dispatch. | A valid policy enters preflight with explicit capability states. Malformed, unknown-version, or missing capability state is rejected without silently enabling a limit. | Correct the policy under a new reviewed revision; retain the rejected attempt and diagnostics. Schema-only feasibility does not establish an executor. | P-01 repository/policy interface; P-03 review | FR-FW-038; AC-1, AC-2 |
| J-031-02 Observe thresholds, scope, reset, and nested runs | Framework maintainer / runner operator | A synthetic or later approved run has named counters, thresholds, scope, reset point, and parent/child correlation rules. Live counters require an adopted profile; contract fixtures may be synthetic. | Start the declared accounting window → update counters → produce warning at threshold → apply the declared action at exhaustion → account for nested runs exactly once. | Below-threshold run may continue. Warning/exhaustion is reported at the correct scope. Missing counters remain unavailable; nested counts cannot be silently duplicated or lost. | Preserve raw bounded counter provenance and correct scope in a new policy revision; do not infer a monetary value from counters. | P-02 execution/probe surface (conditional); P-01 policy/schema and fixtures | FR-FW-038; AC-1, AC-2, AC-6 |
| J-031-03 Request cancellation and distinguish observed termination | Runner operator / execution controller | An enabled limit reaches its stop threshold. Hard cancellation is only applicable after selection and testing of a controlling runner; otherwise the stop action is advisory. | Record stop request → send cancellation through the declared controller → observe the relevant process tree if supported → record `confirmed`, `failed`, or `unknown` outcome separately from the budget breach. | Confirmed process termination may be claimed only with controller observation. Unsupported or failed cancellation remains visible and cannot be relabeled as completion or successful stop. | Escalate only through an authorized controller procedure; preserve the failed attempt and require host/operator follow-up. | P-02 controller/execution surface (blocked for hard enforcement); P-03 evidence/review | FR-FW-038, FR-FW-039; AC-2, AC-3, AC-6 |
| J-031-04 Report measured spend or preserve unknown | Framework maintainer / authorized meter owner | A future host/provider meter is explicitly selected and exposes per-run identity, amount, currency, window, provenance, and unavailable/error states; no such meter is evidenced now. | Query or ingest the authoritative meter → bind response to run identity/window → validate currency and provenance → report amount or `unknown`. | A numeric value is emitted only with matching meter evidence. Missing, stale, failed, or mismatched measurements remain unknown and cannot activate monetary enforcement. | Retry only under documented meter semantics; retain error/provenance; require a new owner decision for another meter. | P-02 host/provider meter surface (blocked); P-03 evidence/review | FR-FW-040; AC-2, AC-4, AC-6 |
| J-031-05 Preserve partial work and prevent false gate PASS | Runner operator / gate owner | A run stops at a threshold, cancellation fails, or verification remains incomplete; FRAMEWORK-GATE-CONTRACT-001 and the transactional runner own gate state. | Record immutable stop reason and execution outcome → capture last durable checkpoint → enumerate remaining verification → state next authorized action → keep gate non-PASS. | The stop record is durable and linked to exact revisions. User changes/evidence remain preserved according to the selected executor's observed recovery semantics. No exhausted or incomplete run passes a gate. | Resume only from a validated checkpoint with fresh authorization where required; otherwise retain state and route to owner/operator. | P-01 gate records; P-02 executor/worktree (conditional); P-03 review | FR-FW-039; AC-2, AC-3, AC-5, AC-6 |
| J-031-06 Review overrides, resets, and retry storms | Independent reviewer / product owner | A stop or warning record, policy revision, nested-run lineage, and any proposed override are available for review. | Compare policy/source revisions and counter lineage → inspect resets/bypass attempts and repeated retries → verify override authority, scope, reason, and expiry/revisit trigger → disposition findings. | Authorized override is explicit and auditable. Unauthorized reset, hidden retry, or invalid override is rejected; independent review does not itself create owner authorization. | Preserve the finding and stopped state; correct policy/implementation under a new revision and rerun full affected review. | P-03 pull request / independent review; P-01 policy and gate records | FR-FW-038, FR-FW-039, FR-FW-040; AC-2, AC-5, AC-6 |

## State axes and cross-surface contract

| Axis | Required states / invariant | Journey coverage |
| --- | --- | --- |
| Policy readiness | `valid`, `invalid`, `unsupported`, or `missing`; only a valid policy may proceed to preflight. | J-031-01, J-031-06 |
| Limit capability | Per-limit `enforced`, `advisory`, or `unavailable`; warnings, requests, and observed enforcement remain distinct. | J-031-01–03 |
| Execution outcome | `running`, `completed`, `limit_exhausted`, `cancel_requested`, `cancel_failed`, `terminated_confirmed`, or `unknown`; the budget breach is not overwritten by cleanup/review state. | J-031-02, J-031-03, J-031-05 |
| Checkpoint and verification | Last durable checkpoint, outstanding checks, and next authorized action are explicit; an incomplete run cannot create gate PASS. | J-031-05 |
| Spend evidence | Numeric amount with meter identity/currency/window/provenance or `unknown`; counters are never a monetary substitute. | J-031-02, J-031-04 |
| Review and authorization | Review finding/disposition is independent from owner authorization; an override binds actor, scope, reason, expiry/revisit, and exact policy/run revision. | J-031-06 |

Cross-surface invariant: the policy declares intended actions; the execution surface reports only observed capability and outcome; the gate record preserves stop/checkpoint state; the reviewer checks exact evidence; and the owner alone authorizes a material override or profile/meter decision. A warning, request, or `unknown` value must never be rendered as a successful enforcement or measured spend claim.

## Surface and applicability matrix

| Surface ID | Surface / platform | Applicability | In-scope task and evidence | Exclusions / downstream effect |
| --- | --- | --- | --- | --- |
| P-01 | Framework repository, policy/schema, fixtures, and gate records | Applicable | Maintainers define versioned policy/result contracts, run structural validation, and inspect durable stop evidence. | No runtime execution or counter enforcement follows from schema/fixture coverage. |
| P-02 | Selected execution host, controller, and provider/host meter | Conditionally applicable; no FW-031 profile or meter is selected | Future execution could collect counters, request cancellation, observe termination, and query spend. Evidence must bind the named profile, run identity, capabilities, and source. | Hard control and numeric spend remain blocked until selected and observed; the prior FW-030 pilot is not transferable proof. |
| P-03 | GitHub pull request, required checks, independent review, and owner disposition | Applicable | Review exact source/policy/evidence, check failure and skipped states, record findings, and preserve owner decision boundaries. | Green CI is not proof of semantic adequacy, host control, process termination, or spend-meter authority. |
| P-04 | End-user web, Android, or iOS application UI | Not applicable | FW-TASK-031 is a framework execution/governance capability, with no user-facing feature in DECISION-036. | No device parity, end-user interaction, or application adoption is implied. Revisit only under separate application scope. |
| P-05 | Language-specific application stack profiles | Not applicable to this bounded assessment | No application code or language-specific executor is selected. | No Next.js, FastAPI, Rust, or native support is inferred. |

## Declared failure-mode inventory

| Failure category | Required visible outcome and recovery | Journey coverage |
| --- | --- | --- |
| FM-031-01 Malformed, missing, or unknown-version policy | Reject before dispatch; identify the policy-level failure without enabling defaults silently. | J-031-01 |
| FM-031-02 Counter unavailable, resets unexpectedly, or has ambiguous scope | Mark unavailable/unknown, block dependent enforcement, retain provenance, and require a corrected profile/policy. | J-031-01, J-031-02 |
| FM-031-03 Nested runs or retries are double-counted, hidden, or reset to bypass limits | Preserve parent/child lineage, stop false accounting claims, reject the bypass, and require full affected rerun. | J-031-02, J-031-06 |
| FM-031-04 Cancellation requested but child process remains or termination cannot be observed | Keep the original breach; report cancellation failed/unknown; do not claim termination or PASS; route to authorized host operator. | J-031-03, J-031-05 |
| FM-031-05 Checkpoint, user changes, or evidence cannot be durably preserved | Mark recovery unavailable/failed and the task incomplete; retain last known durable checkpoint and remaining work. | J-031-05 |
| FM-031-06 Meter missing, stale, mismatched, or errors | Report spend as unknown; do not estimate from time/tool/retry counts; block monetary limit use. | J-031-04, J-031-06 |
| FM-031-07 Unauthorized, expired, or overbroad override | Reject or hold the override, preserve the exhaustion state, and request accountable owner authorization. | J-031-06 |

Every in-scope journey covers at least one applicable failure category. All declared categories have an outcome and recovery path. P-04/P-05 are explicitly out of scope rather than unexamined product surfaces.

## Coverage result and next step

**Provisional G-COVERAGE finding:** The journey/state inventory covers FR-FW-038–040 and all six backlog acceptance criteria, including unavailable capabilities, cancellation uncertainty, partial-work recovery, authoritative meter failure, nested accounting, and override/reset attacks. Applicable, conditional, and excluded surfaces have explicit rationales. This finding awaits independent full-scope review and exact-revision verification.

**Next gate:** G-CX, using a nonvisual operator/reviewer interaction trace. Do not create an end-user prototype or claim a live host, enforcement, cost, or accessibility capability from this coverage inventory.
