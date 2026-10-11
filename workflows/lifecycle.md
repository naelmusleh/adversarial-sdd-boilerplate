---
id: WORKFLOW-LIFECYCLE-001
type: workflow
title: Application lifecycle orchestrator
status: draft
version: 0.2
created: 2026-10-07
updated: 2026-10-09
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, GATE-CATALOG-001, FRAMEWORK-001, FRAMEWORK-002
---

# WORKFLOW-LIFECYCLE-001 — Application lifecycle orchestrator

## Purpose

Give the owner and agents one bounded answer to “what happens next?” for an application project. Use this as the navigation workflow; stage specialists use their linked workflows for detailed execution. The lifecycle applies to the app's own repository after project setup. Framework files are references, not competing app requirements.

## Roles and operating rules

- **Owner:** sets product intent, makes reserved product decisions, accepts/rejects results, and authorizes consequential release or external actions.
- **Lead agent:** reads the current app status/backlog, determines the next eligible action, assigns work, updates artifacts/status, and reports evidence and blockers.
- **Specialist agents:** perform bounded tasks under linked specifications, acceptance criteria, and repository instructions.
- **Independent reviewer:** performs the required review for its gate; an implementer may not label self-review independent.
- Use the app's `backlog.md` and linked gate records as the durable status. Keep a short current-status section in `README.md` pointing to the active milestone, blocker, and next action. Do not create an independent hand-maintained dashboard with duplicate state.
- If the requested action or task is not clear, select the highest-priority dependency-complete approved task. If no task qualifies, identify the exact decision/input needed and continue only independent work.
- Preserve existing work, secrets, credentials, and application/framework repository boundaries. Do not merge, deploy, purchase, contact external parties, alter permissions, or perform destructive actions without the applicable owner authorization.

## Project state model

Each app repository records a lifecycle stage and gate outcomes using the same IDs as [GATE-CATALOG-001](../docs/framework/GATE-CATALOG-001.md). Store current stage, last passed gate, active task, blockers, and next action in the canonical backlog's current-status section; gate evidence lives in linked review/delivery records.

Task statuses are project-defined but must distinguish at least: `planned`, `ready`, `in-progress`, `in-review`, `blocked`, `done`, and `deferred`. Never mark a task `done` while its required evidence is absent. If the repository already has a compatible system, adapt to it instead of creating a second status scheme.

## Lifecycle procedure

| Stage | Agent action | Durable outputs | Gate / next-stage condition |
| --- | --- | --- | --- |
| 1. Ideate and frame | Elicit the target user/problem/outcome, collect supplied evidence, identify constraints and likely exclusions, and record uncertainties without silently resolving them. | Intent brief; initial hypothesis/assumption list. | Pass **G-INTENT** or record discovery blockers and a focused next step. |
| 2. Project setup | Create or prepare a separate app repository; apply the approved project template; set instructions, owners, source-of-truth links, and access prerequisites. | App repository; starter artifacts; current-status section. | Pass **G-SETUP**. Do not place app code in the framework repo. |
| 3. Specify | Build/maintain constitution, specification, and initial backlog. Record research, decisions, acceptance outcomes, open vectors, and traceability. Run adversarial review. | Approved or in-review SDD package; review record; dependency-linked backlog. | Pass **G-REQ**. Unresolved blocking decisions are returned with options and impact. |
| 4. Feasibility and challenge | Probe high-impact provider/data rights, legal, security/privacy, platform, cost, and operational constraints. Run independent challenge. These checks may run in parallel with requirements/design exploration when no commitment is implied. | Feasibility register; evidence; decision requests; revised scope/requirements when needed. | Pass **G-FEAS** for committed scope. Unsupported capability claims remain out of promised behavior. |
| 5. Experience design | Map applicable public/foundational, access, primary task, conversion, support/exception, and retention/return journeys; establish platform contract and visual direction; create linked reviewable prototype. | Canonical `design.md` and linked interaction matrix; active journey inventory; design system; Figma or equivalent evidence. | Pass **G-COVERAGE** before critique. Exclude irrelevant journeys with a reason. |
| 6. Design quality | Run G-CX with the evaluator selected in the app's tool/evaluation decision. If Impeccable is selected, run `critique` on the complete active design scope and use only relevant refine commands for findings; otherwise use the tool-neutral procedure in GATE-CATALOG-001. Rerun after a focused remediation batch. | Critique report, dispositions, and full affected-scope rerun. | Pass **G-CX**. Technical audits are not substitutes for critique, and a static prototype does not prove runtime or native behavior. |
| 7. Architecture and build readiness | Convert accepted product/CX contracts and feasibility evidence into architecture, trust/data/integration behavior, verification approach, and ordered tasks. | Architecture/ADR records; threat/dependency view; implementation-ready backlog. | Pass **G-ARCH**. Stop dependent coding when a material contract remains open. |
| 8. Implementation | Execute one approved app backlog item per run using `ai-engineering-execution.md`; inspect existing state, implement, verify, review, and record the milestone. | App code/configuration, review evidence, observed checks, backlog update. | Pass applicable **G-IMPL** criteria for each milestone. Failed checks keep task incomplete. |
| 9. Verification and launch | Run app-specific test and technical audit plan (web `audit`, native `audit.native`, security/accessibility as applicable); rehearse release, rollback, and support ownership; request release authorization. | QA/release record, deployment evidence, rollback/recovery plan, operator assignment. | Pass **G-RELEASE** only with evidence and explicit owner authorization for the release. |
| 10. Operate and learn | Review service health, incidents, support, cost, outcomes, and feedback; update decisions and prioritize follow-up work. | Runbooks, incident/learning records, changed decisions, prioritized backlog. | Pass **G-OPERATE** when operational ownership exists and material learning is recorded; loop to ideation/specification for justified change. |

## Next-action algorithm

At each work session:

1. Read `README.md`, project instructions, the canonical backlog's current-status section, linked controlling requirements, and latest gate evidence.
2. If a gate failed or is blocked, choose its remediation/decision route before downstream work. Do not advance by changing the status label.
3. Otherwise, choose the highest-priority ready item whose dependencies and required gate inputs are satisfied.
4. If none is ready, identify whether the blocker is an owner decision, external access, evidence gap, or missing framework capability. Make independent progress where safe; report the owner action in decision-ready form.
5. Update the canonical backlog and linked artifacts when starting/completing/blocking work. At turn end, report completed, active, blocked, and next items with evidence links.

## Bounded loop and return rules

- Use one complete review, one focused remediation batch, and one full affected-scope rerun as the normal gate cycle.
- If the rerun remains failed, stop the same loop. Keep the gate failed, report severity/evidence/impact, present viable choices and recommended next action, and route any reserved decision to the owner.
- Return to an earlier lifecycle stage only when a finding changes a controlling requirement, scope, design contract, architecture assumption, or acceptance condition. Record that trace link.
- Fixes to out-of-scope defects are new backlog tasks unless a safety/security issue requires immediate containment under the app's incident procedure.
- No gate requires perfection or speculative future-state screens. Gate closure is based on the approved, complete-in-scope criteria and required evidence.

## Required user report

After work, state the current stage and gate status; work started/completed; files/artifacts changed; observed verification; blockers/owner decisions; and the next eligible action. Do not report unchanged polls or list tasks as complete without evidence.

## References

- [Framework specification](../docs/framework/FRAMEWORK-SPEC-001.md)
- [Framework backlog](../docs/framework/FRAMEWORK-BACKLOG-001.md)
- [Gate catalog](../docs/framework/GATE-CATALOG-001.md)
- [AI engineering execution workflow](ai-engineering-execution.md)
- [CX design workflow](cx-design.md)
- [Adversarial review workflow](adversarial-review.md)
