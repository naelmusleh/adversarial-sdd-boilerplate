---
id: FRAMEWORK-EXERCISE-001
type: framework-lifecycle-exercise
title: Lifecycle tabletop for a new app with unresolved data feasibility
status: draft
version: 0.2
created: 2026-10-08
updated: 2026-10-10
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, GATE-CATALOG-001, WORKFLOW-LIFECYCLE-001, WORKFLOW-DISCOVERY-001, WORKFLOW-FEASIBILITY-001
---

# FRAMEWORK-EXERCISE-001 — Lifecycle tabletop for a new app with unresolved data feasibility

## Purpose and limits

Exercise whether the draft lifecycle can route a hypothetical product idea, show the next action, and stop at a real feasibility blocker instead of pushing the owner through every stage or inventing a data provider. This is a paper tabletop, not an implemented application, usability study, deployment, or formal independent lifecycle-gate approval.

## Scenario

An owner proposes a mobile-first application that helps a household track local service availability and compare options against user preferences. The owner has not chosen an initial geography, source/provider, or business model. No external research or provider access is assumed in this exercise.

This intentionally small scenario is synthetic. It is not a recommendation for a real product and establishes no data, provider, legal, pricing, or user-research facts.

## Tabletop walkthrough

| Stage | Agent action / artifact | Gate/status in the exercise | Next action or hold condition |
| --- | --- | --- | --- |
| 1. Ideate and frame | Capture user/problem hypothesis, target outcome, evidence supplied, exclusions, and unknowns in an intent brief. | G-INTENT can be proposed; owner confirmation is required for intended user and outcome. | Ask a bounded decision bundle only if user/geography choices change the initial workflow; continue drafting the assumption register meanwhile. |
| 2. Project setup | Create a separate local app repository and instantiate the approved starter; record owner, agent boundaries, canonical artifact links, and any remote/access gaps. A GitHub remote is optional for local framework use and can be connected later. | G-SETUP is not passed until the separate app repository, template, ownership, and source of truth are reviewable. | If remote access is missing, continue in the local app repository and record the remote as an external prerequisite. If even a local app repository cannot be created, keep any exploration ephemeral and do not treat it as canonical product documentation. |
| 3. Specify | Draft constitution, specification, and backlog. Make provider/data source availability a linked decision/dependency rather than a hidden implementation assumption. | G-REQ requires traceable, testable requirements and a scoped adversarial review. | Keep provider-dependent requirements explicitly provisional; review against evidence and open decisions. |
| 4. Feasibility and challenge | Register source coverage, rights, access, freshness, cost, legal/privacy, and outage/fallback probes. No provider evidence exists in the scenario. | G-FEAS is **blocked** for any promised live availability comparison. | Ask owner to choose which evidence path to investigate or defer live comparison. Do not build a “live” results design or claim provider coverage. Independent, provider-neutral work may continue. |
| 5. Experience design | Design the request, preferences, interpretation/confirmation, unavailable/unknown state, and source disclosure. Keep example content visibly illustrative. | G-COVERAGE can pass for provider-neutral journeys; it does not clear G-FEAS. | Design user control and fallback around unknown source coverage; avoid results implying real data. |
| 6. Design quality | Critique the complete in-scope active journeys; batch fixes and rerun. | G-CX is a separate result from feasibility. A design may pass CX while live data remains blocked. | If critique fails twice, stop repeating broad polish and return findings/options to owner. |
| 7. Architecture and build readiness | Define data ownership and integration contracts only after the provider strategy is supported; keep fallback behavior and open choices linked. | G-ARCH is blocked for provider-dependent tasks until G-FEAS decisions are resolved. | Build only provider-independent tasks whose requirements and verification are approved. |
| 8. Implementation | Select one ready task and implement it in the app repo, mapping each criterion to observed checks. | G-IMPL is task-specific; passing a shell/task does not clear G-RELEASE. | If no task is dependency-complete, update the backlog with the precise owner/external blocker and next independent work. |
| 9. Verification and launch | Gather app/platform/security/accessibility evidence; prepare rollback and support; request release authorization. | G-RELEASE requires actual app evidence and owner authorization; none exists in the tabletop. | Do not claim launch readiness or deploy. Rehearse in staging only after access and environment are defined. |
| 10. Operate and learn | Assign operator, monitoring/support, incident path, outcome measurement, and learning review. | G-OPERATE requires a real operator and operational evidence; not satisfied by a plan alone. | Record the operational setup as a launch prerequisite, then update the backlog with evidence after deployment. |

## What the exercise establishes

- The workflow separates “design coverage” from “data feasibility”; a visually complete design cannot make an unsupported live-data promise feasible.
- A blocked gate identifies a specific owner/evidence decision and allows safe provider-independent work to continue.
- Each stage has an output and named gate; task completion, design critique, release readiness, and operations are not interchangeable approvals.
- A launch claim requires runtime, release, and operator evidence not available in a tabletop.

## Limitations and next action

This exercise has not been independently reviewed, and it does not prove that a fresh application repository can be initialized or implemented from the templates. Its next use is a separate-repository pilot after the starter and workflows pass framework review. Record new lifecycle defects as bounded framework findings rather than adding speculative automation.

## References

- [FRAMEWORK-SPEC-001](FRAMEWORK-SPEC-001.md)
- [FRAMEWORK-BACKLOG-001](FRAMEWORK-BACKLOG-001.md)
- [GATE-CATALOG-001](GATE-CATALOG-001.md)
- [WORKFLOW-LIFECYCLE-001](../../workflows/lifecycle.md)
- [WORKFLOW-DISCOVERY-001](../../workflows/product-discovery.md)
- [WORKFLOW-FEASIBILITY-001](../../workflows/feasibility-architecture.md)
