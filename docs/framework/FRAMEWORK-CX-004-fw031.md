---
id: FRAMEWORK-CX-004
type: cx-contract
title: FW-TASK-031 operator and reviewer interaction contract
status: draft
version: 0.1
created: 2026-10-26
updated: 2026-10-26
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-012, FRAMEWORK-COVERAGE-004, DECISION-036, WORKFLOW-CX-001, GATE-CATALOG-001
---

# FRAMEWORK-CX-004 — FW-TASK-031 operator and reviewer interaction contract

## Scope and interaction target

This conceptual G-CX artifact covers FW-TASK-031 and FR-FW-038–040 under DECISION-036. Its users are framework maintainers, authorized run operators, independent reviewers, and owners who may approve an override or later host/meter choice. It provides a reviewable, nonvisual interaction trace across policy, execution, gate evidence, review, and owner authorization.

No application end-user interface is in scope. No runtime, provider, meter, threshold, spend policy, CLI command, API endpoint, visual prototype, or implementation is selected. The trace describes required information and state transitions; it does not claim any current tool emits them. Execution-host and meter states remain conditional or blocked as specified by FRAMEWORK-FEASIBILITY-012. Examples of values are synthetic contract values only.

## Actors and decision jobs

| Actor | Decision job | Authority boundary |
| --- | --- | --- |
| Framework maintainer | Define and validate the versioned policy and its capability declarations. | Cannot mark unavailable controls as enforced or authorize a material override by authorship alone. |
| Run operator | Inspect preflight, warnings, stop requests, observed outcomes, and recovery state. | Can request or execute only actions allowed by the selected profile and authorization; cannot claim unobserved termination or spend. |
| Independent reviewer | Compare exact source, policy, run, meter/cancellation evidence, and findings. | Review disposition is advisory evidence and does not grant owner authorization or gate PASS. |
| Product owner / authorized policy owner | Select any future host/meter/policy and decide scoped overrides or accepted residual risks. | Must record actor, scope, reason, expiry/revisit trigger, and exact revisions for material authorization. |

## Journey interaction traces

| Journey | Start and user action | System response / decision point | Success and destination | Back, cancel, interruption, and recovery | Required information and unverified limits |
| --- | --- | --- | --- | --- | --- |
| J-031-01 Define and validate policy | Maintainer supplies a policy revision and chooses which supported counters to enable. | Validator identifies version, units, accounting scope, start/reset point, source, threshold action, and per-counter capability. Missing/unknown capability blocks dispatch; no silent defaults. | A valid request summary shows every limit's `enforced`, `advisory`, or `unavailable` status and can proceed only to a separately authorized preflight. | Edit creates a new policy revision; the invalid attempt remains visible. Cancel before dispatch leaves no run. If validation is interrupted, report incomplete validation and require a fresh validation on resume. | Explain why a field is required and which run action it gates. No schema validator or current command is claimed. |
| J-031-02 Observe warning/exhaustion and nested accounting | Operator reviews the preflight summary and starts an authorized run; during work, the runner reports a warning or limit breach. | Show the counter, unit, scope, threshold, observed value, source, and action. Distinguish nested child values from parent totals. If measurement fails, say `unavailable`/`unknown` and explain whether that limit blocks dispatch or becomes advisory. | Below-threshold work may continue. Warning and exhaustion appear as different states; exhaustion records a stop request or advisory breach and does not mark work complete. | On interruption, preserve last observed count and run lineage with its timestamp/source. Resume uses the declared reset/scope policy and a new authorization when required; never reset silently. | Live values require a selected, observed profile. Contract fixtures do not establish live counters. |
| J-031-03 Request cancellation and report termination truthfully | On exhaustion, operator sees the reason and chooses an allowed stop action; automatic policy may request cancellation only if previously authorized. | Controller response is shown separately as `requested`, `confirmed`, `failed`, or `unknown`. A process-tree termination claim appears only after the controlling runner observes it. If no controller exists, report the breach as advisory and identify required host action. | Confirmed stop retains the original exhaustion reason. Failed/unknown cancellation remains incomplete and routes to authorized operator follow-up; it never becomes a successful completion. | Operator may retry only through the declared controller path. A lost connection yields `unknown`, not presumed success. Preserve each attempt and process observation. | No FW-031 controller or child-process observation currently exists; hard-stop interactions remain specified only. |
| J-031-04 Inspect spend evidence | Owner/operator inspects an available measurement for a completed or stopped run. | Show meter identity, run correlation, currency, measurement window, provenance, and measurement/error state together. Reject mismatch; render absent/failed/stale evidence as `unknown`. | Numeric spend appears only when all required provenance matches. Monetary limits remain disabled while meter evidence is unavailable. | Retry or query history only as the selected meter contract allows; do not use tool counts/time as fallback. A partial response remains unknown with its error reason. | No authoritative FW-031 meter is selected or evidenced. No numeric cost or monetary promise is shown in this design. |
| J-031-05 Review partial work and next action | After exhaustion or cancellation uncertainty, operator opens the stop record. | Show immutable stop reason, run/policy/source revisions, last durable checkpoint, remaining verification, user-change/evidence preservation status, and next authorized action. Keep execution outcome separate from checkpoint and cleanup/recovery status. | Record is durable at the gate-record boundary; incomplete verification keeps the gate non-PASS. Recovery destination is named only when the executor has observed support for it. | Resume from a validated checkpoint with required fresh authorization. If checkpoint or worktree preservation is unavailable, retain the last known durable record and route to the owner/operator; do not imply work was recovered. | FW-TASK-026 supports gate record persistence; an arbitrary executor's worktree/child-process recovery remains conditional. |
| J-031-06 Review reset, retry, or override | Reviewer follows a warning/stop record and any proposed override from its exact policy/run revision. | Present retry lineage, counter resets, actor/authorization, scope, reason, expiry/revisit trigger, meter/cancel evidence, and missing evidence. Separate review finding from owner decision and final gate state. | Reviewer records pass/findings for the declared evidence scope. Only an authorized owner action changes override permission; it does not erase the original exhaustion or review history. | Finding returns to the owner/maintainer with a preserved stopped state and a new revision/review route. If authorization expires or inputs change, mark it stale and require a fresh owner action. | Review surface is a conceptual contract; no automated review provider or UI is implied. |

## Interaction state axes

Each axis has independent state and provenance. A transition on one axis must not erase or imply success on another.

| Axis | Required states | User-facing meaning |
| --- | --- | --- |
| Request readiness | `missing`, `invalid`, `unsupported`, `ready` | Whether policy and environment are complete enough for preflight. |
| Authorization | `not-required`, `pending`, `authorized`, `denied`, `expired`, `stale` | Whether this exact run/action is permitted by the accountable owner. |
| Limit capability | `enforced`, `advisory`, `unavailable` per limit | Whether a control is observed, only requested/warned, or cannot be measured. |
| Execution outcome | `not-started`, `running`, `completed`, `limit-exhausted`, `cancel-requested`, `cancel-failed`, `terminated-confirmed`, `unknown` | What actually happened to the run. `unknown` is not success. |
| Checkpoint/recovery | `none`, `durable-checkpoint`, `preserved`, `recovery-available`, `recovery-failed`, `unknown` | What work/evidence is known to survive and where resumption may begin. |
| Verification | `complete`, `incomplete`, `not-run`, `unknown` | Whether remaining checks can support the task/gate outcome. |
| Spend evidence | `measured`, `unknown`, `unavailable`, `mismatched` | Whether a provider/host measurement is authoritative for this run. |
| Review disposition | `unreviewed`, `findings`, `pass-within-scope`, `blocked` | Whether evidence has been independently assessed, separate from owner authorization. |

**Invariant:** A stop request does not prove process termination; termination does not prove checkpoint recovery; checkpoint recovery does not prove verification completion; green verification does not supply owner authorization; a review PASS does not create a gate PASS; and a proxy counter never creates measured spend.

## Information hierarchy and diagnostics

For an active or stopped run, present this order in human-readable output and any machine-readable record:

1. Current state and required next actor/action.
2. Why the run can or cannot proceed, naming the affected limit and its capability state.
3. The original warning/exhaustion reason and exact run, policy, and source revisions.
4. Cancellation outcome and observed process result, if any.
5. Last durable checkpoint, remaining verification, and preservation/recovery status.
6. Metered spend with provenance, or an explicit `unknown` state and reason.
7. Review findings and owner authorization as separate recorded decisions.

Diagnostics must be actionable without exposing secrets, full source, user content, or unrestricted logs. This contract does not define a CLI syntax, visual layout, or localization policy.

## Surface and applicability decisions

| Surface | Applicability | Interaction contract | Limits |
| --- | --- | --- | --- |
| Framework policy/schema and gate records | Applicable | Define policy, inspect state, validate traceability, and record durable stop/review decisions. | No live runtime behavior follows from the document or validator schema. |
| Selected execution host/controller/meter | Conditional; none selected for FW-031 | Must report observed capability, cancellation result, process observation, meter provenance, and unavailable states. | Hard enforcement and spend remain blocked pending owner choice and evidence. |
| Pull request and independent review | Applicable | Review exact revision, required-check results, findings/dispositions, and owner checkpoints. | CI status does not prove control semantics or grant owner authorization. |
| End-user web, Android, iOS, or desktop product UI | Not applicable | No end-user feature or platform is in this scope. | No parity, device accessibility, or visual design claim is made. |
| Material Design 3 and Apple HIG | Not applicable to this nonvisual framework operator contract | No Material/native UI controls, layouts, or visual tokens are designed. | Revisit only if a future approved scope adds a matching visual/native surface. |
| Figma prototype / Impeccable rendered critique | Not applicable | The reviewable equivalent is this linked interaction trace and state contract; there is no visual target to render. | No Figma flow, screenshot, visual audit, or accessibility test is claimed. |

## Design guidance and review evidence

| Source/page | Accessed | Applies to | CX decision |
| --- | --- | --- | --- |
| WORKFLOW-CX-001 and GATE-CATALOG-001 tool-neutral G-CX procedure | 2026-10-26 | Framework operator/reviewer contract | Use full journey, failure, recovery, state, and applicability traces; no visual evidence is claimed for a nonvisual target. |
| Material Design 3 / Apple Human Interface Guidelines | Not consulted; not applicable | No Android, iOS, or visual product UI in DECISION-036 | No platform-specific visual pattern is adopted. |

## G-CX finding and next step

**Provisional finding:** All six FRAMEWORK-COVERAGE-004 journeys now have start, actor action, system response, decision/authorization boundary, success/failure exit, interruption/cancel behavior, and recovery. Independent review must challenge all eight axes across the full trace set, especially separation of cancellation, checkpoint, verification, spend, review, and authorization states. No UX implementation, visual audit, accessibility result, runtime guarantee, or spend capability is claimed.

**Next gate:** G-ARCH may proceed only after this full-scope interaction review passes and exact-revision CI passes. Preserve G-FEAS blocked/conditional dependencies in the architecture and implementation breakdown.
