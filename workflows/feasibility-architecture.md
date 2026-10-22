---
id: WORKFLOW-FEASIBILITY-001
type: workflow
title: Early feasibility and architecture readiness
status: draft
version: 0.4
created: 2026-10-07
updated: 2026-10-20
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, GATE-CATALOG-001, WORKFLOW-LIFECYCLE-001, FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-EXERCISE-004
---

# WORKFLOW-FEASIBILITY-001 — Early feasibility and architecture readiness

## Purpose

Find material constraints early enough to shape scope, then produce an app-specific architecture only after product and experience contracts are sufficiently stable. This workflow has two passes: **feasibility screening** can run during discovery and design exploration; **detailed architecture** runs before implementation readiness. Do not delay obvious feasibility risks until after polished design, and do not freeze architecture before requirements justify it.

## Roles

- **Product owner:** decides product trade-offs and selects a path when feasibility changes promised scope.
- **Lead agent:** links each probe to requirements/decisions/tasks and keeps status visible.
- **Domain specialists:** validate legal, data, security, platform, cost, or operational claims in their area; their role and evidence are named.
- **Architect agent:** turns accepted constraints into system boundaries, contracts, failure behavior, and implementation-ready tasks.
- **Independent reviewer:** challenges material architecture risks before G-ARCH.

## Pass A — Early feasibility screen

### Inputs

- Intent brief and draft requirements/use cases.
- Expected users, geography, platforms, sensitive data, external dependencies, and operational promises (known or marked unknown).
- Applicable open-decision vectors and target timing for decisions.
- Any pre-spec dependency probes from `WORKFLOW-DISCOVERY-001`, reconciled to current requirement and backlog IDs.

### Procedure

1. Import and reconcile the early dependency screen, if present. Preserve stable probe keys and source history, replace intent-text anchors with current requirement IDs where available, and split capability, account/permission, cost, data-rights, and operational claims when evidence differs. An early `supported` result does not pass G-FEAS or establish access/readiness; repeat or deepen probes when scope, source, or conditions changed.
2. Extract high-impact feasibility claims implied by the intended outcome. Do not evaluate hypothetical components with no link to a user/product requirement.
3. For each claim, record a probe: **domain**, **question**, **evidence needed**, **source/validator**, **date/access** (or a dated `not checked` observation), **confidence/limitations**, **affected requirement IDs**, **dependent backlog task IDs**, **dependency state for each task**, **owner**, **decision deadline or gate**, and **consequence of delay or a negative result**. Dependency state is one of `blocked`, `unblocked`, or `conditional`; explain the condition and safe work boundary for every conditional task. A task is not unblocked merely because investigation can continue.
4. Probe applicable domains:
   - data/provider access, rights, coverage, freshness, permitted use, cost, and fallback;
   - law/regulation, privacy, retention/deletion, consent, and data residency where relevant;
   - identity, authorization, secrets, threat exposure, and abuse cases;
   - platform capabilities, store/deployment requirements, accessibility, and parity assumptions;
   - operational ownership, service dependencies, support, recovery, and observability;
   - unit economics, infrastructure cost, rate/volume constraints, and budget where relevant.
5. Classify each item as `supported`, `unsupported`, `unknown`, `constrained`, or `not-applicable`. Include the evidence that supports the classification; “agent believes feasible” is not evidence.
6. Update affected requirements, dependent tasks, and options. If a core promise depends on unknown or unsupported feasibility, either defer the promise or record an owner decision before it becomes a commitment. Re-evaluate and record each dependent task's state when evidence or a decision changes; do not leave downstream work status implicit.
7. Record external access/account/permission requests separately. Do not ask for credentials in chat or artifacts; name the secure channel or environment setup needed.

### Output and G-FEAS

Promote the discovery screen into `feasibility-register.md` or the app's traceable feasibility table in `specification.md`; do not maintain conflicting copies. Include a dependency matrix mapping each unresolved or constrained probe to affected requirement IDs, dependent task IDs, each task's `blocked`/`unblocked`/`conditional` state, and the trigger or consequence that changes that state. Pass **G-FEAS** only when high-impact unknowns are either resolved with evidence, mitigated by accepted scope, or explicitly recorded as blocking decisions with downstream work held. A decision to proceed with an unknown is a product-owner risk decision, not a feasibility pass. The pre-spec screen alone can never satisfy G-FEAS. The handoff shape and negative/positive examples are in [FRAMEWORK-EXERCISE-004](../docs/framework/FRAMEWORK-EXERCISE-004-pre-spec-dependency-discovery.md).

## Pass B — Detailed architecture readiness

### Entry conditions

- G-REQ and G-FEAS passed for the scope being architected.
- G-CX passed where user-facing journeys or interaction contracts are affected.
- Material product/provider/platform decisions that constrain architecture are resolved or represented as nonblocking alternatives with bounded discovery tasks.

If an upstream gate is still failed, do not invent architecture to work around it. Continue only architecture-neutral exploration and report the dependency.

### Procedure

1. Read accepted `constitution.md`, `specification.md`, `design.md`, linked decisions, feasibility register, and applicable reviews.
2. Define system context, actors/trust boundaries, state/data ownership, key domain entities, integrations, and operational responsibilities. Keep the smallest system that meets approved requirements.
3. For each external integration, define contract ownership, authentication/authorization boundary, timeout/retry/idempotency behavior, rate/cost constraints, data minimization, failure/partial/unknown result behavior, and safe fallback. Label the contract as proposed until provider details are evidenced.
4. Identify security/privacy risks, abuse/threat scenarios, sensitive data flows, retention/deletion, auditability, and required controls. Route legal/security judgments to authorized qualified reviewers where necessary.
5. Define app-specific quality and delivery approach: platforms, build/release shape, environments, secrets management, observability, recovery, test levels, accessibility/device evidence, and support ownership. Record provider/stack choices only with their decision authority and rationale.
6. Record alternatives and trade-offs in ADRs. Do not convert a recommendation into an accepted choice without the authorized decision.
7. Decompose the approved architecture into backlog tasks with requirement/decision links, dependencies, acceptance criteria, verification evidence, and sequencing. Each task must be implementable without inventing a material product contract.
8. Request an independent architecture/security review against the declared scope. Disposition all findings, revise once in a focused batch, and rerun the full affected scope. If still blocked, produce options and owner decision, then stop dependent implementation.

### G-ARCH evidence

Pass **G-ARCH** when the app-specific architecture, trust/data/integration boundaries, failure behavior, applicable security/privacy controls, deployment/operations needs, and task-ready backlog are coherent with accepted product/CX contracts; no blocking review findings remain; and every unresolved choice is visibly linked to the work it blocks. A diagram alone is not sufficient evidence.

## Record schema

Each feasibility/architecture record includes: artifact IDs/versions; scope and exclusions; requirement/decision links; claim/question; evidence and date; confidence/limits; affected behavior; dependent backlog task IDs and per-task dependency state (`blocked`, `unblocked`, or `conditional`); the state-change trigger or consequence of delay/negative evidence; owner and status; options/trade-offs; review findings/dispositions; gate result; and next action.

## References

- [FRAMEWORK-SPEC-001](../docs/framework/FRAMEWORK-SPEC-001.md)
- [GATE-CATALOG-001](../docs/framework/GATE-CATALOG-001.md)
- [Application lifecycle orchestrator](lifecycle.md)
- [AI engineering execution workflow](ai-engineering-execution.md)
