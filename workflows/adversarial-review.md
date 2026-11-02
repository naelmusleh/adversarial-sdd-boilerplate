---
id: WORKFLOW-ADV-001
type: workflow
title: Adversarial review workflow
status: active
version: 0.4
created: 2026-10-05
updated: 2026-10-20
related-artifacts: CAP-002, FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-SPEC-001, GATE-CATALOG-001, FRAMEWORK-GATE-CONTRACT-001
---

# WORKFLOW-ADV-001 — Adversarial Review Workflow v0.3

**Artifact:** WORKFLOW-ADV-001
**Updated:** 2026-10-08

**Capability:** [CAP-002](../framework/capabilities/CAP-002-adversarial-review.md) (active; manual workflow)
**Workflow owner:** artifact owner
**Approval authority:** the owner named by the governing project constitution
**Automation:** none; the procedure is executed manually by AI agents and recorded in repository artifacts.

## Purpose and boundary

Find material weaknesses in a requirements, design, architecture, or other decision artifact before it is accepted as an input to the next lifecycle stage. The review record preserves the target version, scope, evidence, findings, dispositions, revisions, rerun, and gate result. The critic does not edit the reviewed artifact or decide product questions.

This workflow defines review practice; it does not create independent reviewers, run a second agent, or validate facts beyond the evidence actually inspected. If the reviewer is the author or shares the same reasoning context, disclose that limitation. A self-review cannot satisfy a governing requirement for independent review or independently pass that gate.

## Inputs and start conditions

Before starting, the review requester or agent records:

1. The stable ID, exact version, status, and path of each target artifact. If the target has no version, establish one before review.
2. The review scope: sections, decisions, user journeys, platforms, risks, and explicit exclusions.
3. The lifecycle transition being gated, its applicable acceptance criteria, and the authority that can approve it.
4. Relevant governing artifacts and evidence, including open decisions, constraints, prior reviews, and external sources when needed.
5. Reviewer identity/mode and independence: `independent`, `partially independent`, or `self-review`, with a short explanation.

If the target is changing during review, stop and re-freeze it. Do not quietly review a moving target. Record a source-control commit when available; otherwise record the exact file version and capture the reviewed text in repository history before revisions begin.

## Roles

- **Requester / artifact owner:** defines scope and supplies context; retains product and risk-acceptance authority.
- **Critic:** identifies evidence-backed weaknesses and does not revise or approve the target.
- **Reviser:** maps every finding to a disposition and makes only authorized, accepted changes. A reviser may be the author but must label that mode.
- **Verifier:** checks the resulting artifact against each finding on rerun. Prefer a different agent/context from the critic. Disclose when this is not possible.
- **Approver:** the authority specified by the project's governance. Only this person can accept residual risk on the owner's behalf.

One person or agent may perform multiple roles only if the record names the overlap. Role separation in a single-agent environment is a prompt/context discipline, not proof of independence.

## Review procedure

### 1. Create and freeze the review record

Copy [`docs/templates/adversarial-review.md`](../docs/templates/adversarial-review.md) to `docs/adversarial-reviews/<REVIEW-ID>.md`. Use a new stable ID; never overwrite or reuse an existing review ID. Record the target IDs and versions, scope, gate, reviewer mode, evidence cutoff, and links to governing artifacts.

### 2. Perform the critic pass

Inspect the target and cited evidence. Challenge, as relevant to scope:

- internal contradictions, missing actors/states/paths, and invalid assumptions;
- untestable, unverifiable, or ambiguous claims and acceptance criteria;
- security, privacy, safety, fairness, accessibility, reliability, and operational failure;
- misuse, abuse, data/provider/legal constraints, edge cases, and failure recovery;
- disconfirming evidence, alternatives, and consequences of being wrong.

Create one finding per independently actionable issue. Assign IDs scoped to the review (`<REVIEW-ID>/FINDING-001`). A finding records severity, target location, direct evidence, inference (if any), impact/failure mode, recommended resolution or explicit options, owner-decision flag, and disposition. Cite file sections or source links precisely enough for another reviewer to locate the evidence. Never present inference as fact.

### 3. Classify findings

- **Blocking:** prevents safe or meaningful progression, invalidates the intended outcome, or leaves a critical requirement unverifiable.
- **Major:** likely to cause material user, product, legal, security, operational, or delivery failure.
- **Minor:** bounded quality gap that does not invalidate the gated transition.
- **Question:** unresolved ambiguity or evidence request. State whether it blocks the transition and why.

Severity is not a numeric score. A score cannot override a blocking finding, unresolved required owner decision, or missing evidence.

### 4. Record dispositions before changing the target

The reviser assigns exactly one disposition to every finding:

- `resolved` — accepted change is made and a specific resulting artifact/version/section is linked; resolution remains subject to rerun verification.
- `rejected` — not adopted, with evidence-based rationale and reviewer/approver authority recorded. Rejection does not erase a blocking risk; it must be nonblocking under the gate contract or become an owner-accepted residual risk.
- `deferred` — intentionally moved out of scope, with reason, affected scope, owner, due/revisit trigger, and confirmation that deferral does not block this transition. Otherwise it remains a blocker.
- `owner-decision-required` — options and consequences are presented; status remains blocked until the authorized owner decides.
- `accepted-risk` — only the authorized owner may use this. Record explicit acceptance, affected scope, risk and impact, mitigation, monitoring, revisit date/trigger, and owner/date. It is not the same as `resolved`.

Do not change the target while dispositions or required owner decisions are unrecorded. Apply approved changes to the source artifact, preserve its stable ID, increment its version, and link the resulting revision. Keep the original reviewed version available in Git history.

### 5. Rerun and verify

After revisions, record the exact revised target version and change reference. The verifier checks every prior finding against the revised artifact and relevant evidence, records `verified-resolved`, `not-resolved`, `accepted-risk`, or `not-applicable-with-rationale`, and adds any newly discovered findings with new IDs. The rerun must cover the original scope; a narrower rerun must explain the omitted scope and cannot pass a gate that requires full coverage.

For `resolved`, include the evidence that the issue is fixed; merely editing text is not evidence when behavior or facts need validation. For external facts, identify the source and access date. If evidence is unavailable, retain the finding as unresolved or inconclusive.

### 6. Set the gate result

Use exactly one final result:

- **PASS:** required review scope is covered; no unresolved blocking or major findings remain; all required owner decisions are settled; every accepted change has passed rerun verification; and reviewer independence meets the governing gate. Minor findings may remain only if their nonblocking disposition, owner, and revisit condition are recorded. Any residual risk used to pass must meet the `accepted-risk` requirements above.
- **FAIL — revision required:** one or more blocking/major findings remain unresolved, an accepted change failed rerun, required evidence is missing, or the owner decision needed for progression is pending.
- **INCONCLUSIVE:** scope could not be completed, evidence is insufficient to classify a material issue, or required reviewer independence/authority is unavailable. Treat as blocked for lifecycle progression.
- **NOT A GATE:** the review was advisory and no transition is being authorized. This cannot be relabeled PASS.

If a governing constitution says a class of review is mandatory and independent, `self-review` or `partially independent` cannot produce PASS. It can still produce findings and a decision-ready report.

### 7. Bound remediation and stop conditions

For each review cycle, perform one critic pass, one disposition/revision batch, and one full-scope rerun. If the rerun is still FAIL or INCONCLUSIVE, record the remaining findings and choose a next action: one specifically bounded remediation cycle with a named scope, an owner decision, a narrower/replanned scope proposal, or stop/block. Do not repeat polishing or critique without identifying what new evidence or changed condition will make another cycle useful. A second attempted remediation cycle requires a recorded rationale and bounded acceptance criteria; if it also fails, stop and escalate to the owner with options and consequences.

Keep the review artifact's **lifecycle status** within the vocabulary in FRAMEWORK-002: use `revision-required` while findings require revision, `blocked` when progression depends on an unresolved prerequisite, and an appropriate terminal/accepted state only when its criteria are met. Record `PASS`, `FAIL — revision required`, `INCONCLUSIVE`, or `NOT A GATE` only in the separate **gate-result** field. An `INCONCLUSIVE` gate blocks lifecycle progression; it is never an artifact lifecycle status. A failed review is not made passing by closing the chat or documenting the failure.

## Record and evidence

The review artifact is the durable record. Include a finding register, dispositions, revision links, rerun evidence, final gate result, approval evidence if any, and limitations. Do not silently edit prior review records to remove findings; append a dated follow-up section or create a linked rerun record. Keep the reviewed requirement/design artifact separate from the review.

## Completion checklist

- [ ] Exact target ID/version and scope are frozen and linked.
- [ ] Gate, authority, reviewer mode, and independence are recorded.
- [ ] Evidence and inference are distinguished; findings are actionable and individually identified.
- [ ] Every finding has a disposition and required authority/evidence.
- [ ] Resulting source revision is linked and versioned.
- [ ] Full-scope rerun checks each prior finding and records new findings.
- [ ] Final status follows the gate rules; owner-accepted risk has the full required record.
- [ ] Limitations and next action are explicit.
