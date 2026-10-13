---
id: GATE-CATALOG-001
type: framework-gate-catalog
title: Lifecycle gate contracts for application projects
status: draft
version: 0.5
created: 2026-10-07
updated: 2026-10-11
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-001, FRAMEWORK-002, WORKFLOW-QUALITY-001
---

# GATE-CATALOG-001 — Lifecycle gate contracts for application projects

## Purpose

Define the evidence and outcome vocabulary for transitions in the application lifecycle. The catalog is the canonical definition of gate semantics. Stage-specific workflows explain how to prepare the evidence and act on the result.

## Gate outcome vocabulary

- **Not ready:** required input/evidence is missing; assessment has not begun.
- **In progress:** evidence is being gathered or reviewed.
- **Passed:** every required criterion for this gate is met and its evidence is linked.
- **Failed:** one or more blocking findings remain or a required criterion is unmet.
- **Blocked:** an owner decision, external access, dependency, or unavailable validation environment is required.
- **Passed with accepted risk:** permitted only when the gate allows an exception and the authorized owner records the finding, scope, risk, mitigation, expiry/revisit condition, and explicit acceptance.
- **Not applicable:** the project records why the gate does not apply and who accepted the scope exclusion.

A score, a completed checklist without evidence, a prototype, or an implementer's assertion is not a gate result by itself. A later-stage gate cannot clear a failed earlier gate by implication.

## Gate contracts

| ID | Transition governed | Required inputs/evidence | Pass condition | Failure route |
| --- | --- | --- | --- | --- |
| G-INTENT | Idea framing to project setup | Intent brief with target user/problem, evidence, desired outcome, constraints, known assumptions, explicit non-goals, and initial success signals. | Owner confirms intent is sufficient to establish a project; uncertainties are explicit. | Return a concise evidence/decision brief; defer unresolved discovery without inventing a product. |
| G-SETUP | Project setup to specification | Separate application repository, project instructions, canonical artifact map, owners, initial backlog/status location, and access prerequisites. | Project boundary and source of truth are unambiguous and a cold-start contributor can find the next action. | Fix repository ownership, missing access, template/path collisions, or ownership gaps before product artifacts multiply. |
| G-REQ | Specification to design/feasibility | Versioned constitution/specification/backlog, linked requirements and decisions, explicit scope/exclusions, acceptance outcomes, and independent adversarial review. | No unresolved blocking contradiction or requirement ambiguity; open decisions are linked to dependent work; required review findings are resolved or explicitly accepted. | Focused requirement revision; if a second review still fails, return decision-ready findings and stop dependent design/implementation. |
| G-FEAS | Feasibility findings to committed scope | Evidence and owner/status for provider/data rights, legal, security/privacy, platform, cost, operational, and other high-impact dependencies. | Blocking assumptions are disproven, mitigated, or scoped as explicit decision dependencies; requirements reflect actual feasibility. | Re-scope or ask the accountable owner; do not design unavailable capabilities as promised behavior. |
| G-COVERAGE | Journey definition to design critique | Active journey inventory; actor/start/exit and recovery paths; applicability/exclusion reasons; requirements mapping; cross-surface contract; linked prototype or other design evidence. | Every in-scope capability and lifecycle journey is covered at the required depth and can be reviewed without relying on chat. | Fill identified journey/state gaps or revise scope; do not use critique as a substitute for missing coverage. |
| G-CX | CX design to architecture/build readiness | Complete active design target, scoped UX critique method and evidence, rendered/prototype evidence, finding register, targeted fixes, and full affected-set rerun. Use Impeccable `critique` when the app has adopted it; otherwise use the tool-neutral procedure below. | Every finding is resolved with evidence and verified in the rerun, or explicitly accepted by the authorized owner under the residual-risk policy. No finding is silently waived by severity or score. Static design limits are routed to runtime/device gates, not misrepresented as tested. | Focused remediation batch and rerun; on repeated fail, report findings, options, and owner decision; stop CX handoff. |
| G-ARCH | Architecture to implementation | Approved requirements and CX contract, feasibility evidence, architecture/data/trust boundaries, integration failure behavior, security review, deployment/operations assumptions, and task-ready backlog. | High-impact constraints and dependencies are resolved or explicitly gated; tasks have acceptance and verification paths. | Revise architecture or return affected requirements to owner; stop implementation of dependent tasks. |
| G-IMPL | Task completion to integration/release candidate | Selected task, linked criteria, app-specific required-check plan, reviewed changes, observed task/integration verification tied to the proposed revision, review dispositions, and truthful backlog milestone. | Every selected criterion has observed evidence, or a gate-permitted, explicitly owner-accepted exception is recorded; all app-required checks pass on the applicable revision/scope; code review is complete. An unrun, unavailable, failed, or unscoped required check cannot be counted as passed or silently waived. | Fix and rerun targeted checks; if still failing or blocked, leave task incomplete and report the cause and next action. |
| G-RELEASE | Release candidate to production | App-specific release checklist; applicable web/native/security/accessibility checks; environment/secrets readiness; monitoring/support/rollback ownership; data migration/recovery plan as applicable; release authorization. | Evidence meets project release criteria and accountable owner authorizes the specific release. | Block deployment; present unmet checks, risk, remediation, and who can authorize/resume. |
| G-OPERATE | Initial operation to learned next cycle | Health/usage/cost/support/incident evidence, service owner, user feedback and outcomes, and backlog/decision updates. | Operational ownership is active; material incidents and learning are captured and prioritized. | Escalate unresolved service risk; retain last known state and name accountable operator. |

### G-IMPL required-check and coverage evidence

The application repository's approved verification plan defines which checks are required for a task and why. For each selected task, map every acceptance criterion to one or more required check IDs or a documented manual/operational method. Record the exact command or procedure, tool/runtime version, source revision, included code paths and platforms, pass condition, result, and durable evidence location. The G-IMPL record and backlog milestone must link to that mapping. A check that is optional, skipped, not run, unavailable, or run against a different revision/scope cannot satisfy a required criterion.

Coverage is optional unless the application's approved requirements or quality policy makes it mandatory. Where required, the app verification plan must declare the coverage provider/tool and version, source include/exclude scope, measured dimensions, threshold for each dimension, enforcement command/CI job, and result evidence. A passing unit-test command does not prove coverage. Do not inherit a framework-wide 100% rule from the bundled starter: the repository's Vitest 100% thresholds cover this template's configured `src/` TypeScript/TSX source only, while its Python initializer `unittest` suite has no coverage threshold. Any app adopting the web starter must decide and document its own app gate scope; other stacks define their own scope. Existing pilot metrics remain scoped to the modules and run named in [FRAMEWORK-PILOT-001](FRAMEWORK-PILOT-001.md).

The `G-IMPL` outcome is tied to the app's required-check matrix, not to a universal list of commands or a repository-level test count. The matrix is an evidence plan; it does not make checks run automatically unless the app's CI configuration enforces them.

### Tool-neutral UX critique procedure

G-CX is mandatory even when no plugin, desktop agent, or paid design tool is available. Use Impeccable `critique` when the app's own constitution or tool decision requires it; do not use the fallback to bypass that requirement. Otherwise, a qualified human or AI reviewer may run this documented procedure using Markdown, screenshots, exported frames, and prototype links:

1. Freeze the target, active journey inventory, supported surfaces, source versions, reviewer, and exclusions. Include all in-scope journeys/states, not a hand-picked screen subset.
2. Inspect rendered screens and prototype paths. Evaluate visibility of status; real-world match; user control; consistency; error prevention; recognition; flexibility; visual hierarchy; error recovery; help; accessibility; content clarity; and cross-surface behavior.
3. Walk representative first-time, returning, mobile, edge-case, and failure scenarios. Record cognitive-load clusters, emotional trust dips, and any mismatch between requirements/decisions and the prototype.
4. Record each actionable finding with stable ID, evidence/location, severity, user impact, recommendation, owner-decision need, and disposition. A numeric score prioritizes work but never substitutes for a finding or passes the gate.
5. Fix in a bounded batch and rerun the same full scope. Record the evaluator/tool/version or state `manual tool-neutral review`, exact evidence, remaining findings, and gate outcome. Any finding that is unresolved and not explicitly owner-accepted keeps G-CX failed or blocked; do not infer waiver from its severity or score.

For projects using Impeccable, preserve its critique report and rerun evidence alongside the same gate record. For either method, static design review does not establish runtime behavior or device accessibility; route those checks to implementation verification.

## Universal gate record

Every gate record includes:

1. Gate ID and transition; project/repository identity; date; accountable agent and owner/reviewer.
2. Exact artifacts, versions, platforms, code paths, and validation methods in scope; explicit exclusions and reasons.
3. Criteria checked, evidence links/results, findings with severity and blocking status, and dispositions.
4. Outcome, decision authority, residual risks and acceptance record where permitted.
5. Next stage/action, owner, prerequisites, and any work explicitly not authorized yet.

Use the gate record template in `docs/templates/app-project/gate-record.md.template`. Keep records in the app repository under its `reviews/` or `delivery/` directory, depending on the gate.

## Bounded review and rerun policy

1. Prepare one complete, explicitly scoped gate run.
2. Resolve findings in one coherent batch when the evidence permits.
3. Rerun the gate on the complete affected scope and record fix-to-finding evidence.
4. If blocking findings remain, set `failed` or `blocked`, stop dependent work, and return the evidence, impact, viable options, recommendation, owner decision needed, and next safe independent task.
5. Do not restart a broad redesign loop merely to improve a score. Reopen a passed gate only if scope or evidence materially changes, a linked requirement changes, or a relevant defect/incident invalidates the prior evidence.

## References

- [FRAMEWORK-SPEC-001](FRAMEWORK-SPEC-001.md)
- [FRAMEWORK-BACKLOG-001](FRAMEWORK-BACKLOG-001.md)
- [Application gate record template](../templates/app-project/gate-record.md.template)
