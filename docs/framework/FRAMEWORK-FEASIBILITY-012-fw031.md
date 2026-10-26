---
id: FRAMEWORK-FEASIBILITY-012
type: feasibility-register
title: FW-TASK-031 per-run limits and stop conditions feasibility
status: draft
version: 0.1
created: 2026-10-26
updated: 2026-10-26
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, DECISION-036, FRAMEWORK-FEASIBILITY-011, FRAMEWORK-GATE-CONTRACT-001, WORKFLOW-FEASIBILITY-001
---

# FRAMEWORK-FEASIBILITY-012 — FW-TASK-031 per-run limits and stop conditions feasibility

## Scope and evidence boundary

This register evaluates feasibility for FW-TASK-031 and FR-FW-038–040 under DECISION-036. It checks available evidence for per-run counters, enforced cancellation and recovery, and authoritative spend measurement. It does not select a runtime, provider, meter, budget threshold, or spend policy; execute a workload; implement an adapter; or authorize application use, credentials, merge, or deployment. No live customer data or production secrets are used.

Evidence is limited to the repository at G-REQ candidate `620f7676b6a78b3a3ff614b59b138c7ffa727267`, the prior FW-TASK-030 feasibility record FRAMEWORK-FEASIBILITY-011, existing FW-TASK-026 completion evidence, and the current framework tool/workflow surface inspected on 2026-10-26. A capability described by another task is not treated as adopted or as proof for FW-TASK-031.

## Feasibility probes

| Probe | Domain and affected requirements | Evidence and classification | Dependency state, owner, trigger, and safe boundary |
| --- | --- | --- | --- |
| F031-01 | Runtime counter collection and policy state; FR-FW-038; FW-TASK-031 | The approved requirement permits elapsed-time, retry/iteration, tool-invocation, and runtime-resource limits only when each is labeled `enforced`, `advisory`, or `unavailable`. The framework repository has no FW-031 runner or budget adapter. **Unknown** which counters a future host exposes and at what accounting scope. | FW-TASK-031 implementation is **conditional** on a host/profile selection and a versioned capability probe. Until then, schema and fixtures may represent unavailable measurements, but cannot claim a working runtime limit. Owner: product owner for host/profile adoption. Trigger: a concrete profile and observable counter contract are proposed. |
| F031-02 | Wall-clock cutoff and process-tree cancellation; FR-FW-038/039; FW-TASK-031, with FW-TASK-030 dependency for hard-stop claims | Existing FW-TASK-030 G-FEAS evidence is specific to a GitHub-hosted Ubuntu 24.04/rootless Podman candidate and includes timeout/interruption cases, but its recorded runner-image version discrepancy limits reproducibility. It does not establish a FW-031 controller integration, nor does this repository contain an FW-031 child-process termination observation. **Constrained / unknown for FW-031.** | Hard enforcement and termination claims are **blocked** pending a selected controller, exact runtime profile, and a synthetic end-to-end cancellation test that observes the relevant process tree. Advisory warning/request behavior remains feasible as a contract only. Owner: product owner selects profile; implementation owner supplies observation. Trigger: profile selection and test plan. |
| F031-03 | Durable partial-work evidence and recovery; FR-FW-039; FW-TASK-026 and FW-TASK-031 | FW-TASK-026 is complete and provides append-only gate records, exact-revision linkage, atomic updates, and recovery-oriented transaction behavior. This supports a durable gate/checkpoint record at that boundary, but does not prove that an arbitrary child process can be stopped or that uncommitted application edits are recoverable. **Supported for gate-record persistence; conditional for process/worktree recovery.** | Recording stop reason, last validated checkpoint, remaining verification, and next action is **unblocked** at the record-contract layer. Preservation of in-flight work is **conditional** on the chosen executor's working-tree and checkpoint model. Owner: implementation owner specifies the boundary. Trigger: executor/profile selected. |
| F031-04 | Authoritative monetary metering; FR-FW-040; FW-TASK-031 | No provider/host meter is selected in DECISION-036 or evidenced in the FW-031 candidate. Existing elapsed-time, retry, read, and tool counters are explicitly disallowed as cost substitutes. **Unknown / unavailable for the current framework contract.** | Monetary limit enforcement and numeric spend reporting are **blocked** until a named meter provides currency, measurement window, per-run identity/correlation, and provenance with documented failure semantics. The requirements can safely represent spend as `unknown`; no proxy estimate is permitted. Owner: product owner selects a meter-bearing host/provider. Trigger: meter API/account evidence and a bounded query test. |
| F031-05 | Nested-run accounting and retry scope; FR-FW-038; FW-TASK-031 | The requirement defines deterministic nested-run correlation and no double-counting as acceptance evidence, but no live orchestrator counter implementation is in scope or available. **Unknown for live execution; feasible to specify and fixture.** | Contract/schema work is **unblocked**; live enforcement is **conditional** on an executor exposing stable run/parent IDs and counter ownership. Owner: implementation owner after profile selection. Trigger: profile contract supplies correlation identifiers. |
| F031-06 | Thresholds, operational ownership, and override authorization; FR-FW-038/039/040; FW-TASK-031 | DECISION-036 approves requirements only and selects no threshold, currency policy, owner role, or runtime. FR-FW-039 requires explicit scoped authorization and audit for any override. **Open owner decisions, not technical facts.** | No threshold or override is adopted here. Any deployment policy using a limit remains **blocked** until its accountable owner, numeric value, scope, expiry/revisit rule, and failure behavior are approved. Schema fixtures may use labeled synthetic values only. Owner: product owner. Trigger: a later concrete policy proposal. |

## Feasible bounded path

Requirements and architecture-neutral validation can model every measurement with its unit, accounting scope, source, status, reset behavior, and provenance. Tests can use clearly labeled synthetic fixtures to prove threshold arithmetic, unavailable states, nested-run correlation, no false PASS on exhaustion, and checkpoint record shape. These activities do not establish live enforcement or real spend.

An advisory-only policy can warn and request cancellation without claiming that a host stopped work. Hard stop, OS resource ceilings, and monetary limits remain disabled until the matching controller or meter is selected and observed. This is a feasibility boundary, not an owner-approved budget policy or implementation authorization.

## Dependency matrix and gate disposition

| Work item | State | State-change condition |
| --- | --- | --- |
| FW-TASK-031 specification-level policy/result schema and synthetic contract fixtures | **Unblocked in principle; still requires a separate G-IMPL scope authorization** | Owner authorizes the bounded implementation unit after G-COVERAGE, G-CX, and G-ARCH. |
| FW-TASK-031 live counter collection and warning behavior | **Conditional / held** | Select a host/profile and demonstrate each exposed counter's scope and reset semantics. |
| FW-TASK-031 hard cancellation and runtime-resource enforcement | **Blocked** | Select a controlling runner; complete synthetic process-tree cancellation/resource tests with observed outcomes; resolve the FW-TASK-030 reproducibility limitation for any reused candidate. |
| FW-TASK-031 monetary spend limit or numeric spend report | **Blocked** | Select a provider/host meter and demonstrate run correlation, currency/window, provenance, and unavailable/error behavior. |
| Any application or production use | **Blocked** | Separate application-specific decision, architecture, authorization, and release evidence. |

**G-FEAS finding:** The bounded assessment supports a PASS because every material unknown affecting hard enforcement or spend is retained as a blocking dependency and dependent implementation/use remains held. This finding is pending independent review and exact-revision verification. It establishes no runtime/provider/meter adoption, controller capability, process termination, spend value, or implementation permission.

**Next gate:** G-COVERAGE for FR-FW-038–040. Preserve the blocked/conditional rows in downstream coverage and architecture work; do not promote any capability to `enforced` without the corresponding observed evidence.
