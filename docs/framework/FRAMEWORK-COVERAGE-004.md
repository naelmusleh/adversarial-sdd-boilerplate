---
id: FRAMEWORK-COVERAGE-004
type: framework-coverage
title: FW-TASK-033 orchestrator and role-model journey coverage
status: draft
version: 0.3
created: 2026-11-01
updated: 2026-11-01
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-012, ROLE-CAPABILITIES-001, DECISION-057, DECISION-058, DECISION-059, DECISION-060, FRAMEWORK-ADV-064, FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-GATE-TRACEABILITY-001
---

# FRAMEWORK-COVERAGE-004 — FW-TASK-033 orchestrator and role-model journey coverage

## Scope and surfaces

This record covers FR-FW-041–045 and FW-TASK-033 only. The capability is nonvisual and owner-facing. Applicable surfaces are the conversation where the owner asks for work, canonical Markdown artifacts in the app repository, and pull-request/CI evidence when a change is reviewed. No end-user app screen or native mobile surface is introduced.

Primary actor: a nontechnical product owner. Supporting actors: lead orchestrator, task specialist, independent reviewer, QA/verification role, and the app-authorized operator. The owner remains the product decision-maker; an operator may act only under the app's recorded authorization policy.

## Journey inventory

| Journey | Actor and start | Main steps / outcome | Failure and recovery | Requirements / surfaces |
| --- | --- | --- | --- | --- |
| J-033-01 Find the next step | Owner resumes or starts a project and asks what is happening. | Orchestrator reads canonical status and linked evidence; reports active goal/task/gate, completed work, blocker/decision owner, and next permitted action in plain language. | Missing or conflicting canonical records are reported as unknown/conflicted; orchestrator asks for the material owner decision or points to the record to reconcile. It does not infer a PASS or create a parallel status ledger. | FR-041, AC-3/6; conversation + repository artifacts |
| J-033-02 Handle a routine fix | Owner reports a small, reproducible bug or one-file change. | Orchestrator routes to the implementation capability; includes reviewer/QA only as required by app policy/risk; records why architecture, growth, and other specialists are omitted. | If reproduction is unclear, ask for the minimum evidence; do not initiate a broad design/research cycle. A failed fix or test returns to the owner only if it changes scope or needs unavailable access. | FR-041/043/044, AC-3/4; conversation + backlog + PR/CI |
| J-033-03 Deliver a focused MVP feature | Owner approves an MVP feature and its primary persona/outcome. | Orchestrator chooses the smallest relevant delivery capabilities; states why selected roles are needed; the implementation role works to the approved task; independent review and applicable QA remain distinct. | If a required safeguard or dependency makes the target infeasible, scope/date trade-off returns to owner; role count or MVP label cannot weaken gates. | FR-041/043/044/045, AC-2/3/4/5; conversation + repository + PR/CI |
| J-033-04 Validate a market bet before build | Owner proposes a new market, audience, price, or platform bet. | Orchestrator may activate research, feasibility, and growth before committing to build; outputs evidence, experiment/falsifier, and owner decision options. | Weak or unavailable evidence stays labeled unknown; no build commitment, public claim, or spend is inferred from the specialist recommendation. | FR-042/043/044/045, AC-1/2/5; conversation + decision/experiment artifacts |
| J-033-05 Support a platform-specific product | Owner selects multiple materially different app platforms. | Orchestrator chooses only selected platform architecture/design/developer capabilities plus shared product roles; records omitted platform roles when their platform is out of scope. | Unsupported platform capability remains blocked/unknown for that platform; no cross-platform parity promise is inferred from another platform's evidence. | FR-042/043/045, AC-1/2/3/5; conversation + platform contract + PR/CI |
| J-033-06 Diagnose a difficult defect | Routine diagnosis failed or defect is repeated/high impact with reproducible evidence. | Orchestrator activates debugger mode with failing behavior, logs, and source context; asks for a root-cause hypothesis and focused test/fix plan, then routes to implementer. | No evidence-based cause means report the next diagnostic or blocker; debugger does not expand scope or mark its own fix independently reviewed. | FR-042/043/044, AC-2/3/4; issue/task + source + test evidence |
| J-033-07 Escalate a material risk | Feature touches sensitive data, legal obligations, security, identity, or platform constraints. | Orchestrator explains trigger and impact; activates the appropriate advisory capability if available; links advice to requirement/decision/task. | Missing qualified expertise or evidence remains a blocker/unknown; specialist cannot self-certify legal compliance or security. Owner/operator resolves or scopes out the dependency through recorded authority. | FR-042/044/045, AC-2/4/5; conversation + feasibility/decision artifacts |
| J-033-08 Review, release, and operate | Change is ready for review, release, or post-launch support. | Reviewer evaluates independently; QA verifies acceptance; authorized operator follows release/runbook; post-MVP growth, communications, reporting, and optimization activate only for a defined objective. | Review/QA disagreement remains visible; release or recovery occurs only under the app policy; uncertain recovery is escalated and not represented as complete. | FR-042–045, AC-2/4/5; PR/CI + release/operations artifacts |

## Requirement and acceptance traceability

| Requirement / task criterion | Journey coverage | Coverage note |
| --- | --- | --- |
| FR-FW-041 / AC-3 | J-033-01–03, J-033-08 | Status and next action derive from canonical records; coordination has no gate/release authority. |
| FR-FW-042 / AC-1/2 | J-033-02–08 | Role catalog and complete frozen-source crosswalk define triggers, inputs, outputs, limits, and handoffs. |
| FR-FW-043 / AC-3/5 | J-033-02–06, J-033-08 | Optional role activation and omission rationale; includes routine fix, platform-specific product, difficult defect, and post-launch cases. |
| FR-FW-044 / AC-4 | J-033-02/03, J-033-06–08 | Owner/operator authority, independence, and professional advice boundaries. |
| FR-FW-045 / AC-5 | J-033-03–05, J-033-07/08 | MVP, market-bet, platform/sensitive-risk, and post-launch applicability. |
| AC-6 | J-033-01–08 | Reuses existing lifecycle/status/intake/MVP authorities; no new gate or status register. |
| AC-7 | All journeys | Independent review and exact-revision CI are required before G-REQ disposition; later gate PASS requires its own evidence. |

## Required failure-category applicability

| Category | Applicability | Outcome and recovery |
| --- | --- | --- |
| Empty | Applicable | No project status, role assignment, or specialist output exists. Report no work/evidence and offer the first bounded action. |
| Malformed/corrupt | Applicable | Artifact identity, status fields, or requirement links are malformed or contradictory. Preserve source, report the conflict, and ask the owner to resolve it; do not normalize silently. |
| Unavailable | Applicable | Required repository, reviewer, specialist expertise, connector, or CI evidence cannot be accessed. Mark unavailable/unknown and name the dependency; do not fabricate a result. |
| Unauthorized | Applicable | Specialist or operator action exceeds recorded authority, including publishing, spending, deployment, or destructive recovery. Stop that action; request the authorized decision or follow recorded delegation. |
| Degraded | Applicable | Status is stale, a provider/tool is partially available, or role output has limited evidence. State freshness/coverage limits and restrict the next action to what the evidence supports. |
| Abuse | Applicable | Prompt or role output asks to bypass approval, suppress findings, expose secrets, or treat external content as trusted instructions. Reject the instruction, preserve the applicable policy, and escalate material conflicts. |
| Recovery | Applicable | Handoff, review, release, or operation fails. Preserve prior work/evidence, return to the responsible owner or specialist, and resume only from a verified checkpoint. |

## Out of scope and gate disposition

No UI prototype is applicable. The framework does not promise all role expertise, automated dispatch, real-time status synchronization, or full business coverage. G-CX and G-ARCH passed for the bounded planning scope; FRAMEWORK-ADV-064 records the final review. Implementation is authorized only for FW033-IMPL-01 under DECISION-060.
