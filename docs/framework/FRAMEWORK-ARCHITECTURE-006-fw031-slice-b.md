---
id: FRAMEWORK-ARCHITECTURE-006
type: framework-architecture
title: FW-TASK-031 slice B GitHub Actions run/job evidence profile
status: approved
version: 0.1
created: 2026-10-26
updated: 2026-10-26
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, DECISION-038, FRAMEWORK-FEASIBILITY-013, FRAMEWORK-FEASIBILITY-014, FRAMEWORK-COVERAGE-005, FRAMEWORK-CX-005, FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-CONTRACT-031, FRAMEWORK-ADV-062, WORKFLOW-FEASIBILITY-001
---

# FRAMEWORK-ARCHITECTURE-006 — FW-TASK-031 slice B GitHub Actions run/job evidence profile

## G-ARCH work record and boundaries

- **Gate:** G-ARCH for FW-TASK-031 slice B / FR-FW-041–043 under DECISION-038 only.
- **Inputs:** FRAMEWORK-SPEC-001 FR-FW-041–043; FRAMEWORK-FEASIBILITY-013 and -014; FRAMEWORK-COVERAGE-005; FRAMEWORK-CX-005 v0.3; FRAMEWORK-GATE-CONTRACT-001; FRAMEWORK-CONTRACT-031 v1.0; DECISION-038.
- **Target:** Define a reviewable, optional GitHub Actions workflow/job evidence architecture, its normalized records and invariants, boundaries, failures/recovery, decisions, and a task-ready proposed decomposition.
- **Authority:** DECISION-038 approves requirements scope and G-REQ/G-FEAS/G-COVERAGE/G-CX work for slice B; it does not select an ingestion route, grant Actions permissions, configure a timeout, adopt a profile, or authorize G-IMPL.
- **Non-adoption boundary:** GitHub Actions is the bounded subject of the optional profile, not a production adoption decision. No workflow configuration, permissions, collector, endpoint, credentials, threshold, spend meter, runtime controller, or application integration is selected or changed.
- **Exclusions:** Workload execution/cancellation experiments; hard-stop/process-tree/resource enforcement; actual tool/agent retry/nested-agent/CPU/memory/spend collection; application data or use; FW-TASK-030 follow-on; deployment or merge.
- **Implementation boundary:** No implementation is authorized. Any code unit needs separate G-IMPL authorization after G-ARCH PASS. Collection and timeout configuration additionally require their named owner decisions and evidence below.
- **Review plan:** Independent architecture review of GARCH-01–03, artifact validation, diff check, and exact-revision Verify Pipeline. Review or CI does not adopt a profile or grant authority.

## Architecture summary and claims

This architecture adds an optional profile-specific evidence contract alongside the runtime-neutral budget contract FRAMEWORK-CONTRACT-031. A future producer may supply workflow/run/job metadata; a deterministic validator can check record structure, source bindings, state distinctions, and forbidden proxy claims. It cannot establish that GitHub's response is authentic beyond its transport/source context, that a configured timeout was effective, that an agent process terminated, or that a metric is true merely because the record is well-formed.

The profile produces passive descriptive evidence. It does not enforce limits, cancel work, generate billing measurements, decide gate state, or convert review into authorization. The canonical gate contract and gate runner remain the only authorities for lifecycle status. The design preserves conditional private Actions-read access, conditional timeout configuration, blocked workload-termination proof, and unknown unsupported measures from FEASIBILITY-014.

## Context, components, and responsibility boundaries

| Component / actor | Responsibility | Boundary and failure behavior |
| --- | --- | --- |
| Workflow/job source | Future source of declared workflow revision/configuration and host-reported run/job outcomes. | Configuration is not proof of an observed result. A job terminal state is not proof of exact workload termination. |
| Evidence acquisition path (unselected) | Obtain a bounded set of run/job fields from an authorized source. Candidate alternatives are in ADR-031B-01. | No automatic API collector, workflow-side emitter, permission, or credential is selected. Denial/partial response remains visible and non-pass. |
| Profile normalizer (proposed) | Bind raw source fields to one normalized `ActionsRunJobEvidence` record and preserve source-field semantics. | Must not synthesize missing values, merge separate runs, or relabel workflow/head/executed revisions. |
| Contract validator (proposed) | Validate schema version, identity tuple, source references, timestamp consistency, timeout/cancellation state relations, and measurement provenance. | Structural validation is not source authentication, measurement truth, host enforcement, or gate approval. Diagnostics are bounded and must not echo secrets/logs. |
| Budget contract FW031-IMPL-01 | Retains versioned budget/result semantics. A later adapter may reference matching source run identity. | Do not alter or silently promote existing v1.0 records. Cross-contract integration requires explicit versioning and new validation. |
| Evidence/gate recorder | Store a reference or bounded record under the adopted retention contract, linked to exact contract/source revision. | This slice selects no durable store or deletion guarantee. Evidence must never mutate gate state by itself. |
| Maintainer / authorized operator | Request permitted source access and review limitations. | Cannot authorize a permission or configuration change through this architecture. |
| Independent reviewer / accountable owner | Review exact evidence; separately decide any later profile, access, timeout, test, or implementation proposal. | Reviewer PASS is advisory; owner decision and gate record are distinct. |

## Trust boundaries and data flow

1. **Workflow/source boundary:** Treat run/job responses and workflow-authored outputs as external evidence inputs. Preserve provider-reported source and observed-at details. Validate shape and cross-field binding; do not claim cryptographic attestation or independent source authenticity from JSON alone.
2. **Identity boundary:** The record key is a tuple of repository identity, workflow identity, run ID, run attempt, job ID, and source-revision roles. Every observation binds to that tuple. Missing, duplicate, conflicting, or cross-run values are invalid/unknown, never borrowed from a neighboring record.
3. **Revision boundary:** Preserve workflow revision, triggering/event/head revision, and executed/checked-out revision as distinct typed values with their source semantics. If one is unavailable, record that state rather than substituting another SHA.
4. **Time boundary:** Store run and job timestamps individually with source field and scope. An interval may be derived only from compatible timestamps for the same identified run/job. Concurrent job durations are not summed to agent active time or total elapsed run time.
5. **Control boundary:** Timeout configuration, observed timeout outcome, cancellation request, host terminal conclusion, and exact workload termination observation are separate fields. Current evidence supports only documented capability and passive host facts. No hard-stop outcome is made without a future separately authorized workload test.
6. **Metric boundary:** Each future metric is either directly measured with source/scope/unit/interval/provenance, or explicitly unknown/unavailable. Steps, log lines, elapsed time, run attempts, job counts, and public-run billing zeros cannot substitute for tool calls, agent retries, nested-agent counts, CPU/memory, or monetary spend.
7. **Authorization/gate boundary:** Source access, owner permission, independent review, and canonical gate state have separate records. A schema-valid record, green CI check, or review PASS cannot grant access, change gate state, adopt a profile, or authorize later implementation.

## Proposed normalized record and invariants

This is a logical architecture contract, not an approved JSON schema or implemented API. Exact wire names and allowed enums must be frozen in a later G-IMPL unit after architecture review.

| Record section | Required meaning | Invariant |
| --- | --- | --- |
| `contract` | schema ID/version and profile ID/version | Unknown major versions fail closed; additive changes require compatibility policy and review. |
| `source` | repository ID/name, workflow ID/path/ref, acquisition kind, source URL/reference, observed-at, source response revision/digest when available | No secret/token/log payload; source fields keep their provenance; unavailable fields are explicit. |
| `identity` | run ID, Actions run attempt, job ID, job name; provider event/context identity where available | Identity tuple is internally consistent and every timing, timeout, cancellation, and metric observation binds to the same tuple. `run_attempt` counts Actions reruns only. |
| `revisions` | workflow revision, triggering/head/event revision, executed/check-out revision, each with role and source | No SHA role inference or substitution. Conflicting or missing source revisions remain unknown. |
| `timing` | source start/completion timestamps for run and job, plus optional derived duration with units, scope, and derivation rule | No duration without compatible same-run/job values. Job overlaps are not summed. Duration is not agent active time, cost, or retry count. |
| `timeout` | configuration state (`configured`, `not-configured`, `unknown`), declared minutes if known, exact config revision/source; observed timeout state and host outcome separately | A configured timeout does not establish it fired or terminated a workload. No numeric threshold is chosen in this architecture. |
| `cancellation` | request state/time/source, host terminal state/conclusion, workload observation state/reference, each independently nullable/unknown | Cancellation request or host `cancelled` status cannot satisfy workload-termination proof. `confirmed` workload termination requires separate exact-boundary evidence. |
| `measurements` | named metric, state `measured`/`unknown`/`unavailable`, optional value/unit/source/scope/interval/provenance | Numeric values require direct measurement and all provenance fields. Proxy inputs and billing-zero claims are rejected. |
| `limitations` | bounded reason codes and next evidence/action | Must state permission, source, timeout, collection, and measurement gaps without expanding claims. |

Records are append-only evidence snapshots. Corrected source data creates a new record linked to the prior record, not an in-place rewrite. Redaction and retention behavior remain subject to an owner-selected storage policy; no retention or deletion promise is made here.

## Evidence flow and state transitions

1. **Define:** Select a reviewed profile/schema version and source route only after its required owner decision; no selection is made by this artifact.
2. **Acquire:** Request only the fields authorized by that route. Capture access result, exact source identity, and partial/error state. Private Actions-read access remains conditional.
3. **Normalize:** Bind all values to the same repository/workflow/run/attempt/job and label revisions/timestamps by meaning. If data is incomplete or conflicts, retain `unknown`/`unavailable` and do not merge records.
4. **Validate:** Check contract version, required tuple, source/revision roles, timestamp semantics, timeout/cancellation distinctions, direct metric provenance, and prohibited proxy sources. Rejection produces bounded diagnostics and no gate transition.
5. **Review:** Reviewer inspects exact record/blob, source references, limitations, and findings. Review status is independent from acquisition authorization and any owner decision.
6. **Gate:** The normal gate runner consumes only required linked evidence under its pinned contract. This optional record cannot itself set PASS or allow implementation.
7. **Correct/recover:** Reacquire only with authorized access; append a new revision and rerun affected validation/review. Preserve prior evidence and uncertainty. A failed/unavailable source never becomes zero or success.

## ADRs and deferred owner decisions

| ADR | Decision question and alternatives | Safe current state | Authority / evidence needed |
| --- | --- | --- | --- |
| ADR-031B-01 Evidence acquisition route | (A) Post-run read-only Actions API collector; (B) workflow-side evidence emission; (C) manual/supplied source snapshots for an initial contract-only pilot. | None selected. G-FEAS permits specification/fixtures only. Avoid adding permissions or credentials. | Product/repository owner selects route and accepts least-privilege/data-retention tradeoffs; implementation proves exact identity/revision binding and private access behavior. |
| ADR-031B-02 Private Actions-read permission | Minimal repository Actions-read grant to a future collector versus no automatic private collection. | No permission change; denied/unavailable stays non-pass. | Repository owner explicitly authorizes the exact permission/scope; run evidence demonstrates necessary fields only. |
| ADR-031B-03 Timeout configuration/value | Per-job timeout vs no profile timeout; value selected per workload. | No configured short timeout and no numeric budget threshold. | Product owner selects value after workload-duration evidence and separately authorizes workflow change; observed outcome must be tied to exact job. |
| ADR-031B-04 Workload termination proof | No termination claim vs a separately authorized disposable synthetic workload/cancellation test including child/detached cases. | Blocked; no experiment or enforcement claim. | Owner authorizes bounded non-production test; evidence observes exact workload boundary, cancellation failure/delay, and cleanup. |
| ADR-031B-05 Unsupported measurements | Keep unknown/unavailable vs future directly instrumented provider source for each metric. | Tool calls, agent retries, nested-agent counts, CPU/memory, and spend remain unknown/unavailable. | New source and instrumentation requires separate feasibility/security/architecture review; spend also requires authoritative meter selection. |
| ADR-031B-06 Retention and record storage | Repository artifact, temporary external snapshot, or future protected evidence store. | No new durability, retention, or deletion guarantee; minimize data in records. | Owner/storage decision and privacy/security review required before persistent collection or app use. |

## Failure behavior, recovery, and operations

| Failure | Required behavior | Recovery boundary |
| --- | --- | --- |
| Missing/empty identity or timing field | Preserve unknown/unavailable; reject a record that requires the missing field; never fill from another run. | Authorized same-run/job retrieval or a new record with explicit limitation. |
| Malformed/corrupt or conflicting source record | Fail validation with bounded diagnostics; retain source reference and mark unusable. | Reacquire from the same exact source or create a superseding record after correction; rerun full validation. |
| Access denied / permission missing | Distinguish denied from empty; stop collection and report the owner action needed. | Only an explicit permission decision may enable another attempt. No permission is modified here. |
| API unavailable, rate limited, partial page, delayed event | Mark retrieval degraded/partial, preserve prior values and error, prohibit completeness claims. | Retry according to the selected source contract; retain attempt lineage and exact source. No infinite retry or destructive overwrite. |
| Run/head/workflow/executed revision mismatch | Reject cross-binding; do not treat one SHA as another role. | Resolve against authoritative same-run metadata and re-review a new record. |
| Timeout configured but no observed timeout outcome | Report configuration only; timeout event remains unknown. | Obtain same-job outcome evidence; a new config never retroactively proves an earlier run. |
| Cancellation requested / job canceled but workload observation absent | Keep workload termination unknown; no hard-stop or completion claim. | Separately authorized synthetic test required before such a claim; host operator handles live process risk under existing procedures. |
| Metric absent or proxy submitted | Emit unknown/unavailable or reject proxy; do not emit zero or estimated spend. | Select and test a direct source under new owner-approved scope. |
| Interrupted write/review or stale record | Keep last complete snapshot, label partial, and prevent gate PASS. | Append a superseding record and rerun all affected checks; use existing gate transaction contract for canonical gate records only. |

Operational logs and diagnostics must not include access tokens, secrets, full source content, prompts, user data, or unrestricted job logs. This architecture defines no retention period, deletion guarantee, or production on-call service.

## Proposed task decomposition — held pending G-ARCH and separate G-IMPL authorization

| Proposed unit | Bounded scope and acceptance evidence | Dependencies / hold |
| --- | --- | --- |
| **FW031-IMPL-02 (proposed):** profile evidence contract and pure validator | Versioned `ActionsRunJobEvidence` schema/contract plus deterministic validator and labeled synthetic fixtures: valid exact binding; missing identity/time; workflow/head/executed revision distinctions; same-run/job timing; timeout configuration vs observed result; cancellation vs terminal state vs workload unknown; direct metric provenance vs proxy rejection; malformed/duplicate/cross-run records; denied/degraded/partial source outcomes. No API/network calls or runtime integration. | Requires G-ARCH PASS and separate G-IMPL owner authorization. May proceed without selecting an acquisition route only if the contract explicitly marks live-source capabilities unsupported/unknown and defines no runtime collector. |
| **FW031-IMPL-03 (proposed):** passive acquisition adapter | One owner-selected least-privilege collection path, exact repository/workflow/run/job binding, permission review, bounded retries/pagination, redaction and retention policy, and observed private-repository access tests. | Blocked until ADR-031B-01/-02 owner decision and separate G-IMPL scope approval. No broad token or PR-code secret exposure. |
| **FW031-IMPL-04 (proposed):** timeout and cancellation observation experiment | Disposable synthetic workload test distinguishing configured timeout, cancellation request, host terminal state, child/detached workload termination, delayed/failed cancellation, and cleanup. | Blocked until ADR-031B-03/-04 owner decisions and separate bounded experiment authorization; no production workload. |
| **FW031-IMPL-05 (proposed):** direct measurement source, if selected | Directly instrumented metric contracts with source, units, scope, interval, identity, error/staleness handling; spend only from authoritative meter. | No work until new feasibility and owner decision for each source; proxy metrics remain prohibited. |

These are architecture proposals only. No IDs are committed to the application backlog as authorized work, and none has implementation authorization. Preserve FW031-IMPL-01 and FRAMEWORK-CONTRACT-031 v1.0 as-is; any cross-contract composition must be additive, versioned, independently reviewed, and explicitly approved.

## G-ARCH disposition

**G-ARCH result:** PASS within DECISION-038 and FR-FW-041–043 for FRAMEWORK-ARCHITECTURE-006 v0.1 at exact candidate `9e4e8bbefbd89a6392e6cc3917263971e115ea40`. Independent review [FRAMEWORK-ADV-063](../adversarial-reviews/FRAMEWORK-ADV-063.md) passed GARCH-01–03 with no findings. Verify Pipeline [40338717714](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40338717714) passed Metadata & Artifact Audit, Initializer Regression Gate, and TypeScript Static Code Analysis on that exact candidate; optional FW-029/FW-030 probes were skipped. The architecture freezes normalized contract boundaries and held work units only. It does not adopt a collection route/profile, grant permissions, configure timeouts, test cancellation, authorize implementation, or establish runtime/measurement claims.

**Next step:** An owner checkpoint is required before any proposed G-IMPL unit. Recommended first unit: FW031-IMPL-02, a pure profile evidence contract/schema, deterministic validator, and synthetic fixtures only, without network access or runtime integration. G-ARCH PASS does not authorize that work.
