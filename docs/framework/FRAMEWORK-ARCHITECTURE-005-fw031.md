---
id: FRAMEWORK-ARCHITECTURE-005
type: framework-architecture
title: FW-TASK-031 per-run limits and stop conditions architecture
status: draft
version: 0.1
created: 2026-10-26
updated: 2026-10-26
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, DECISION-036, FRAMEWORK-FEASIBILITY-012, FRAMEWORK-COVERAGE-004, FRAMEWORK-CX-004, FRAMEWORK-GATE-CONTRACT-001, WORKFLOW-FEASIBILITY-001
---

# FRAMEWORK-ARCHITECTURE-005 — FW-TASK-031 per-run limits and stop conditions architecture

## G-ARCH work record

- **Gate:** G-ARCH for FW-TASK-031 and FR-FW-038–040 under DECISION-036 only.
- **Inputs:** FRAMEWORK-SPEC-001 v0.29; FRAMEWORK-FEASIBILITY-012 v0.2; FRAMEWORK-COVERAGE-004 v0.2; FRAMEWORK-CX-004 v0.2; FRAMEWORK-GATE-CONTRACT-001; DECISION-036.
- **Target:** Define a runtime-neutral budget policy/result boundary, state ownership, evidence flow, failure behavior, trust boundaries, and a task-ready but unauthorized implementation breakdown.
- **Non-adoption boundary:** No execution host, runtime, provider, meter, threshold, currency, reset policy, or override policy is selected. FW-TASK-030's Podman evidence is not transferable support proof. No production/app use, credentials, deployment, or runtime execution is authorized.
- **Implementation boundary:** A schema/validator/fixture slice may be proposed as a separate G-IMPL authorization. Runtime counter collection, hard cancellation/resource enforcement, monetary spend, application integration, and production behavior remain blocked on the specific decisions and evidence in FRAMEWORK-FEASIBILITY-012.
- **Exclusions:** FW-TASK-030 follow-on units; app changes; changing gate contract semantics; choosing a provider or budget threshold; actual host/process control; monetary estimation from proxy counters; repository split; release or deployment.
- **Review plan:** Independent architecture review of GARCH-01–04, `python3 scripts/artifacts.py validate`, `git diff --check`, and exact-revision Verify Pipeline. A review PASS cannot select a deferred option or authorize implementation.

## Architecture summary

The framework treats a budget as an immutable, versioned per-run policy plus a sequence of typed observations. A policy validator checks completeness and declares each enabled limit's capability state before work is authorized. An optional executor reports only measurements it can identify and observe. Threshold handling records a warning or exhaustion independently from any cancellation attempt. The stop record links the original source/policy/run, last durable checkpoint, remaining verification, next authorized action, and any spend evidence. The transactional gate runner remains the authority for gate state: exhaustion or incomplete verification cannot produce PASS.

No runner, host, provider, meter, numeric threshold, or cost policy is adopted. Missing enforcement capability is explicit `unavailable` or `advisory`; absent/mismatched spend measurement is `unknown`. Provider-specific adapters require later owner choices and exact profile evidence.

## System context and responsibility boundaries

| Component / actor | Responsibility and authority | Boundary and failure behavior |
| --- | --- | --- |
| Policy author / task owner | Defines versioned limits, units, run scope, threshold behavior, and any required authorization. | Cannot claim capabilities, spend, or thresholds that have not been evidenced/authorized. |
| Policy validator (proposed, pure) | Validates schema/version, required fields, counter scope/reset definitions, and consistency of capability states. | Does not execute work, observe a host, or infer monetary cost. Missing/unknown capability is represented explicitly; invalid policy blocks preflight. |
| Run coordinator / executor adapter (not adopted) | Correlates a run and optional nested runs, collects supported observations, issues warnings or stop requests, and reports adapter state. | No adapter is currently selected. Unsupported controls remain unavailable; no unsandboxed or unmetered fallback is allowed. |
| Controller (not adopted) | Receives cancellation/resource-limit requests and, if supported, observes the relevant process tree. | A request is not termination. Report confirmed termination only from controller evidence; otherwise retain failed/unknown outcome. |
| Authoritative meter (not selected) | Supplies per-run spend, currency, window, identity/correlation, and provenance under its own contract. | No numeric amount without matching evidence; error/missing/stale/mismatch remains unknown. |
| Checkpoint/evidence recorder | Appends bounded stop/checkpoint/verification/evidence references through existing gate-run transaction contract. | Does not claim arbitrary worktree/process recovery; writes must preserve append-only history and exact revisions. |
| Independent reviewer | Challenges exact policy/run/evidence, reset/bypass behavior, limitations, and claims. | Review disposition is distinct from owner authorization and gate outcome. |
| Product owner / authorized policy owner | Selects future host/meter/threshold/override policy and accepts permitted residual risk. | No such material selection or risk acceptance is made by this architecture. |

## Trust boundaries and data flow

1. **Policy/source boundary:** Policy bytes are versioned and bound to exact source and policy revisions for the run. A changed policy invalidates preflight authorization. Policy is configuration, not proof that a counter is available.
2. **Run identity boundary:** Each run has an opaque run ID and, for nested work, a parent ID and declared accounting owner. A child observation must be attributable to one accounting scope. Retries preserve their identity/lineage; resets require a declared new run/window, never silent counter mutation.
3. **Execution/control boundary:** Agent and subprocess work is untrusted relative to the coordinator. Counter observation, warning, cancellation request, and confirmed termination are different event types. Unknown control state cannot be promoted to enforced.
4. **Meter boundary:** Spend observations enter only from the explicitly selected authoritative provider/host meter. The framework validates identity, currency, window, and provenance against the run; it does not calculate cost from time, tool use, retries, reads, or tokens.
5. **Gate/evidence boundary:** A stop record is appended through FRAMEWORK-GATE-CONTRACT-001/transactional runner semantics. It includes evidence references and incomplete verification status but contains no source content, secrets, personal data, or unrestricted logs. Gate PASS remains controlled by the applicable gate contract and required evidence.
6. **Review/owner boundary:** Review findings are advisory until disposition; a material override requires authorized actor, scope, reason, expiry/revisit condition, and exact revisions. Neither a successful pipeline nor a review score grants override authority.

## Proposed data model and invariants

These are architecture-level logical records, not committed JSON schemas or runtime APIs.

| Record | Required fields | Invariant |
| --- | --- | --- |
| `BudgetPolicy` | schema ID/version; policy revision/digest; limit set; run/nesting scope; counter units; start/reset semantics; threshold action; capability declaration; authorization requirement | Immutable during a run. Every enabled limit explicitly identifies source and `enforced` / `advisory` / `unavailable` state. Unknown capability cannot be called enforced. |
| `LimitDefinition` | stable limit ID; type; unit; scope; source; warning/exhaustion threshold; action; measurement-unavailable behavior | No default numeric threshold or reset rule is inferred. Unsupported monetary limits remain disabled/unavailable. |
| `UsageObservation` | run ID; parent ID when nested; limit ID; value/unit; observed-at and source identity; observation sequence; confidence/availability state | Values must match declared units and accounting scope. Duplicate/ambiguous lineage cannot silently change totals. |
| `StopEvent` | original limit-breach reason; policy/source revisions; requested action; cancellation state; controller/process observation reference; execution outcome | Cancellation request, controller response, termination observation, and original execution outcome are separate fields. |
| `CheckpointSummary` | last durable checkpoint reference; preserved-change/evidence status; remaining verification; next authorized action; recovery state | Missing/unknown checkpoint remains explicit. No task/gate PASS on exhaustion or incomplete verification. |
| `SpendObservation` | run correlation; meter identity; amount/currency; measurement window; provenance reference; availability/error state | A number exists only for an authoritative, matching observation. Missing/mismatch/error is `unknown`; proxy counters are never cost. |
| `OverrideAuthorization` | actor/authority; exact run/policy scope; reason; expiry/revisit condition; source revision; decision reference | Explicitly authorized, scoped, and auditable. Expired or stale authorization cannot be reused. |

## State flow and decision points

1. **Prepare:** Load immutable policy and source revisions; validate all required fields. Invalid or unknown-version policy blocks before execution.
2. **Resolve capabilities:** For each requested limit, resolve evidence from the selected profile. If absent/unverified, mark it unavailable or advisory and present the resulting limitation before owner/run authorization.
3. **Authorize:** Bind run request and explicit authorized scope to exact policy/source revisions. Any material field/revision change requires fresh validation and authorization.
4. **Observe:** Emit typed counter observations with stable run/parent IDs and sequence. Counter errors remain unavailable/unknown; no guessed value or double count.
5. **Warn/exhaust:** At configured thresholds, record warning or exhaustion and preserve the original breach. An advisory action requests human/host action without claiming stop success.
6. **Cancel/observe:** If a selected controller supports cancellation, record request, result, process observation, and cleanup independently. Only explicit observation supports a termination claim.
7. **Checkpoint and gate:** Append stop record, last durable checkpoint, remaining verification, next authorized action, and preservation status. Keep task/gate incomplete; the gate runner rejects PASS without required evidence.
8. **Spend:** Attach a matching authoritative meter observation or `unknown`; do not use other counters as an estimate. Monetary threshold behavior is unavailable until a meter profile is selected and tested.
9. **Review/recovery:** Reviewer checks frozen evidence. A valid owner override is appended as a separate authorization; recovery starts only through a later permitted run from a validated checkpoint.

## Failure behavior and recovery

| Failure | Required behavior | Recovery boundary |
| --- | --- | --- |
| Invalid policy, missing unit/scope/reset/action, or unknown version | Block preflight; name the field/category; do not dispatch work. | Correct in a new policy revision and repeat validation. |
| Counter missing, stale, resets unexpectedly, or scope ambiguous | Mark unavailable/unknown; disable dependent hard action; preserve last known observation and provenance. | Require a selected profile to prove measurement semantics; never infer a value. |
| Nested agent retries or duplicates | Retain parent/child lineage, reject ambiguous/double accounting, and preserve exhaustion state. | Resolve accounting ownership in a new policy/profile revision; run adversarial fixture before enablement. |
| Cancellation fails, times out, or cannot observe descendants | Keep original breach; set cancellation to failed/unknown; do not claim termination or completion. | Authorized host operator action; preserve event, checkpoint, and incomplete gate state. |
| Checkpoint or worktree preservation fails | Record last known durable checkpoint and recovery unavailable/unknown; retain user changes and evidence where observed; do not pass. | Operator/owner recovery decision; do not imply a safe resume point. |
| Spend meter missing, stale, mismatched, or unavailable | Report spend unknown; disable monetary comparison; never substitute proxy estimates. | Restore/select a meter with verified run correlation and provenance, then re-evaluate. |
| Unauthorized, expired, or stale override/reset | Reject action; keep stop state; log bounded reason and authorization reference. | Obtain fresh explicit owner authorization or retain the block. |
| Gate record transaction interrupted or concurrent | Reuse FRAMEWORK-GATE-CONTRACT-001 append/atomic recovery; fail closed on stale revisions or partial record. | Re-read authoritative gate records; preserve append-only history and run evidence. |

## Security, privacy, and operations

- Treat agent/user code and child processes as untrusted. The core records only bounded identifiers, counters, outcome states, checkpoint references, and evidence digests/links.
- Do not store prompts, source contents, secrets, environment dumps, full command output, or personal data in budget records. Redact provider diagnostics and cap their size.
- Store policy, meter configuration, and override authority through a future owner-selected protected channel. No secrets or access-token scheme is designed here.
- Restrict any future adapter to only the capabilities it reports and is authorized to use. No fallback to direct host execution or unaudited cost estimates.
- Record operational ownership and retention at the eventual host/provider decision. This document promises no durability beyond the existing gate-record contract and no provider log/attestation retention.
- A green CI run verifies only the repository revision and configured checks; it cannot prove live host enforcement or meter truth.

## Deferred architecture decisions

| Decision | Options kept open | Current safe state | Owner and evidence required to unblock |
| --- | --- | --- | --- |
| Execution host/profile/controller | Existing tested hosted runner candidate; a different managed runner; advisory-only operation; or no live adapter | No runtime adopted; hard termination/resource enforcement blocked. | Product owner selects profile and accepts its scoped residual risks; implementation supplies exact synthetic counter and process-tree tests. |
| Spend meter/provider | Per-run host/provider billing meter; no numeric spend in initial profile; or defer spend support | Spend remains `unknown`; monetary limit disabled. | Product owner selects meter; evidence must bind run identity, currency/window, provenance, and error/stale behavior. |
| Budget thresholds/reset windows | Per-project/per-run owner policy and explicit units; no enabled threshold where owner has not chosen one | No default values or reset semantics are invented. | Accountable policy owner chooses threshold/scope/reset and revisit trigger in a versioned policy. |
| Override authority and expiry | Task owner, repository owner, or explicitly delegated role | No override is valid until the authority model is approved for a concrete profile. | Product owner identifies authorized role, scope, reason, expiry/revisit, and durable decision record. |
| Checkpoint/worktree recovery | Gate-record-only checkpoint; executor-managed snapshot; or no resume after interruption | Framework gate records can be durable; executor recovery remains conditional. | Select executor and demonstrate preservation/recovery semantics with user-change/evidence fixtures. |

These are blocked decisions, not implicit selections or owner acceptance of residual risk.

## Proposed implementation decomposition — not authorized

| Proposed slice | Scope and acceptance evidence | Dependencies / hold |
| --- | --- | --- |
| A. Policy/result contract and pure validator | Versioned schemas and deterministic validation for policy fields, capability states, usage observations, stop/checkpoint summaries, spend provenance, override references; positive and negative synthetic fixtures for all declared states and cross-axis invariants. | Requires a separate explicit G-IMPL authorization. Does not execute code, choose limits, enable a runtime, query a provider, or claim real spend. |
| B. Advisory accounting coordinator | Count/time/tool observations only where a selected host exposes them; nested run lineage, warnings, stop records, and gate-state integration. | Blocked until host/profile and accounting semantics are owner-selected and evidenced; hard enforcement remains excluded absent controller proof. |
| C. Cancellation/resource controller adapter | Resource ceilings, cancellation propagation, observed process-tree result, interruption and checkpoint recovery. | Blocked until a named tested controller is selected, FW-TASK-030 dependencies are resolved for the chosen profile, and synthetic positive/negative boundary evidence is reviewed. |
| D. Authoritative spend adapter | Meter identity/run correlation/currency/window/provenance and unavailable/error handling. | Blocked until product owner selects the meter and exact provider contract is evidenced. Proxy estimate implementation is prohibited. |

No task IDs are assigned to slices B–D and no implementation unit is authorized here. If the owner later authorizes slice A, it remains confined to pure contracts, validator, and synthetic fixtures.

## Architecture acceptance and gate result

- **GARCH-01 — contract and ownership:** Every policy/run/stop/checkpoint/spend/override record has an owner, immutable revision boundary, and state invariant.
- **GARCH-02 — trust and failure boundaries:** Unsupported/unknown measurements fail closed; controller requests and observed termination are distinct; meter provenance is mandatory; gate records cannot pass on exhaustion.
- **GARCH-03 — dependencies and operations:** Every blocked or conditional dependency names the decision owner, evidence trigger, and held work; privacy/retention and recovery limits are explicit.
- **GARCH-04 — task readiness:** Proposed pure validation work has deterministic scope and evidence; runtime, meter, cancellation, and production slices stay held pending owner choices and separate G-IMPL authorization.

**Provisional G-ARCH finding:** The runtime-neutral contract and state flow are coherent for requirements-only planning, and deferred choices remain visible with owners, evidence triggers, and downstream holds. This architecture does not make the blocked capabilities feasible by assertion. Independent architecture review and exact-revision verification are required before a G-ARCH PASS.

**Next action:** Full-scope independent architecture review, targeted correction if needed, and exact-revision Verify Pipeline. After G-ARCH PASS, ask the owner whether to authorize proposed slice A; do not begin implementation without that decision.
