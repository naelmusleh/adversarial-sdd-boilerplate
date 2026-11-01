---
id: FRAMEWORK-CX-004
type: framework-cx
title: FW-TASK-033 founder-facing coordination interaction contract
status: draft
version: 0.3
created: 2026-11-01
updated: 2026-11-01
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-012, FRAMEWORK-COVERAGE-004, DECISION-057, DECISION-058, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-CX-004 — FW-TASK-033 founder-facing coordination interaction contract

## Target and limits

This is a nonvisual interaction contract for the nontechnical product owner using the framework through conversation and repository records. It covers FR-FW-041–045 and J-033-01 through J-033-08. It does not claim that a specific chat product, agent runtime, dashboard, or connector implements this behavior.

The core experience should reduce the owner's coordination burden: the owner states the desired outcome in ordinary language; the orchestrator reports the current evidence-based state, brings in relevant bounded expertise, and asks only for material owner decisions. It must make uncertainty and authority visible without turning each task into a long questionnaire.

## Interaction contract

### A. Owner asks what happens next

The orchestrator's response presents, in this order. It leads with ordinary language; lifecycle IDs and technical status tokens are optional references after their meaning is explained.

1. **Goal in progress:** one sentence grounded in the mission or approved task.
2. **Current step:** active task and lifecycle gate, with status and linked evidence.
3. **What is complete:** only outcomes supported by observed evidence.
4. **What is blocked or unknown:** the concrete dependency and its consequence.
5. **Owner action:** only if needed; state the decision/input, options, business impact, and recommendation.
6. **Next step:** the next permitted action and responsible role.

If canonical records conflict or are missing, the response says which record is unresolved and does not invent state from chat history.

### Plain-language labels and example

Do not present gate IDs or internal state tokens by themselves. When they help the owner locate evidence, show the short explanation first and place the ID after it.

| Internal term | Owner-facing wording |
| --- | --- |
| G-INTENT | Agreeing on the problem and goal |
| G-SETUP | Setting up the project and its source records |
| G-REQ | Agreeing on what the product must do |
| G-FEAS | Checking whether the proposed approach can work |
| G-COVERAGE | Checking that the agreed user journey is accounted for |
| G-CX | Reviewing whether the experience is clear and usable |
| G-ARCH | Deciding how to structure the approved work |
| G-IMPL | Building and checking the approved task |
| G-RELEASE | Checking readiness for the authorized launch |
| G-OPERATE | Operating the product and learning from its use |
| `stale` | Needs a fresh check because a source changed |
| `conflicted` | Project records disagree; the owner needs to resolve the mismatch |
| `unavailable` | Could not access or complete this check |
| `unknown` | Not established yet |
| `blocked` | Waiting for a named decision, dependency, or correction |

Example response shape:

> **Goal:** Let a new customer complete the approved first task.
>
> **Current step:** We are deciding how to structure the approved work (architecture review, `G-ARCH`).
>
> **Verified:** Requirements review passed; the role model is documented for all 26 roles in the pinned reference.
>
> **Still needed:** One independent review of the updated founder-facing wording and the final CI result. The app’s status record is current.
>
> **From you:** Nothing right now.
>
> **Next:** After review and CI, I’ll report whether this planning stage passed and what approval is needed before implementation.

The example is a format illustration, not evidence that these statements are true for another project. In an actual report, each statement must link to current app records.

### B. Orchestrator assigns a specialist

Before handing work off, the owner-facing summary identifies the specialist capability, the trigger, and expected result in plain language. The durable handoff carries the task/requirement IDs, exact relevant artifact revisions, bounded question, output shape, decision limits, and evidence location. A role unavailable in the current environment remains unavailable; the orchestrator may continue only with work that does not depend on it.

### C. MVP task

The orchestrator starts from the approved primary persona and launch outcome. It selects only the roles necessary for the smallest end-to-end slice. It does not activate growth, social media, dashboard, optimization, or platform-specific roles by default. If a concrete risk or launch dependency requires specialist input, it explains why that work is necessary and keeps the scope brief. Existing gate-required applicability decisions and safeguards remain visible.

### D. Market bet or post-launch objective

For a market, audience, price, or platform bet, the orchestrator may bring in researcher, feasibility, and growth capabilities before build. It presents assumptions, evidence limits, a falsifier/experiment, likely cost, and owner decision. For post-launch objectives, it may engage growth, communications, operational reporting, or optimization. Drafting is allowed within scope; external publication, spend, commitments, deployment, or destructive recovery remain under the app's explicit authorization policy.

### E. Risk escalation and release

When the task implicates legal, privacy, security, safety, or platform risk, the orchestrator names the trigger and the kind of qualified evidence needed. It distinguishes advisor output from owner decision and gate evidence. At release, reviewer findings, QA acceptance, operator readiness, and release authorization appear as separate evidence/status items; no single agent summary rolls them into a generic green status.

## Interaction state vocabulary

Use the canonical task/gate states defined by the app; summarize them in plain language. Preserve `unknown`, `unavailable`, `blocked`, `stale`, and `conflicted` as distinct conditions. A role assignment is not proof that work started; a specialist recommendation is not owner approval; an observed CI pass is not a release decision. Do not create an alternate dashboard or copy of canonical status.

## G-CX critique checklist

| Criterion | Review question |
| --- | --- |
| CX-033-01 Founder clarity | Can a nontechnical owner identify the goal, current step, evidence, blocker, owner action, and next step without decoding agent names or gate jargon? |
| CX-033-02 Low coordination load | Does the orchestrator select and explain a small relevant capability set rather than ask the owner to choose agents or manage handoffs? |
| CX-033-03 Truthful progress | Are unknown/unavailable/stale/conflicted states clear, and are completed claims tied to evidence? |
| CX-033-04 Authority and trust | Can the owner distinguish advice, independent review, QA, operator action, and approval? Are external actions explicitly authorized? |
| CX-033-05 MVP focus | Does the MVP example stay on the primary journey and avoid ceremonial specialists while retaining required safeguards? |
| CX-033-06 Broader business support | Do market-bet and post-launch examples show useful growth/communications/operations support without treating those roles as mandatory? |
| CX-033-07 Recovery | When records conflict or a role/check is unavailable, is the safe next action understandable and bounded? |

## G-CX disposition template

Record the exact revision, evaluator, target journeys, each criterion's finding/evidence, severity, disposition, and whether a full affected-scope rerun was completed. A static text contract does not establish usability with actual owners or prove that an installed runtime follows the interaction. Those require a later cold-start exercise using an initialized app and the exact selected tool.

## Critique finding disposition

| Finding | Initial critique | Correction | Rerun state |
| --- | --- | --- | --- |
| CX-033-F01 | Gate IDs and states such as `stale`/`conflicted` lacked a required plain-language mapping and example for a nontechnical owner. | Added owner-facing translations, required IDs-after-meaning rule, and a sample status update with evidence/authorization limits. | Full affected-scope independent rerun is pending the owner checkpoint required before a third consecutive review pass. No G-CX PASS is claimed. |
