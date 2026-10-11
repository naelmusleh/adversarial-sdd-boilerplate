---
id: ADV-000
type: adversarial-review
title: <reviewed artifact> adversarial review
status: draft
version: 0.1
created: YYYY-MM-DD
updated: YYYY-MM-DD
reviewed-artifact: <ARTIFACT-ID>
reviewed-version: <exact version>
related-artifacts: <comma-separated IDs>
---

**Template version:** 0.3

# <REVIEW-ID> — <reviewed artifact> adversarial review

## Review request

- **Gate / lifecycle transition:** <transition this review informs>
- **Review scope:** <sections, decisions, actors, platforms, risks; explicit exclusions>
- **Questions to answer:** <questions or “None specified”>
- **Approval authority:** <role/person named by governing project rules>
- **Evidence cutoff:** <date/time and timezone>
- **Source revision:** <Git commit, immutable document version, or other exact reference>

## Review method

- **Critic:** <agent/person or role>
- **Reviewer mode:** `independent` | `partially independent` | `self-review`
- **Independence explanation:** <what context was isolated, or why not>
- **Reviser:** <agent/person or role>
- **Verifier:** <agent/person or role>
- **Sources inspected:** <paths, artifact IDs, links, external sources with access date>
- **Limits:** <missing evidence, uninspected scope, unavailable tools, or “None identified”>

## Finding register

Each finding must distinguish direct evidence from inference and identify the target location. Use IDs scoped to this review, for example `<REVIEW-ID>/FINDING-001`.

### <REVIEW-ID>/FINDING-001 — <short, actionable finding>

- **Severity:** Blocking | Major | Minor | Question
- **Target location:** <section, requirement, screen/node, file/line, or decision>
- **Evidence:** <direct evidence and precise reference>
- **Inference:** <interpretation, or “None”>
- **Impact / failure mode:** <what could happen and to whom>
- **Recommendation / options:** <specific change or decision options>
- **Owner decision required:** Yes | No — <why and which authority if yes>
- **Initial disposition:** unresolved

<!-- Duplicate the finding block for each finding. If no findings, state the scope and evidence supporting that result. -->

## Disposition and revision

For each finding, record exactly one disposition: `resolved`, `rejected`, `deferred`, `owner-decision-required`, or `accepted-risk`.

| Finding | Disposition | Rationale / decision evidence | Change made or follow-up | Target revision/link | Owner and revisit trigger if deferred/risk |
| --- | --- | --- | --- | --- | --- |
| <REVIEW-ID>/FINDING-001 | <state> | <reason or owner decision link/date> | <change or follow-up> | <artifact ID/version/path> | <owner/date/trigger or N/A> |

### Residual-risk acceptance (complete only when used)

- **Authorized owner and decision date:** <name/role and date>
- **Finding(s) and affected scope:** <IDs and in/out-of-scope boundary>
- **Risk and impact accepted:** <specific risk, who/what may be affected>
- **Mitigation and monitoring:** <controls and who owns them>
- **Revisit condition/date:** <measurable trigger or date>
- **Decision evidence:** <linked decision record or explicit approval reference>

If no residual risk is accepted, state: `No owner residual-risk approval used for this review.` Do not fill this section on the owner's behalf.

## Rerun and verification

- **Rerun date:** <date>
- **Verifier and reviewer mode:** <identity/mode; disclose overlap>
- **Scope:** <confirm original full scope or explain omissions>
- **Target revision:** <exact artifact ID/version and source reference>
- **Prior finding checks:**

| Finding | Rerun state | Evidence confirming resolution or explaining remaining risk |
| --- | --- | --- |
| <REVIEW-ID>/FINDING-001 | verified-resolved | <specific evidence and location, or unresolved rationale> |

- **New findings:** <IDs and links, or “None in the rerun scope”>
- **Verification limits:** <what this rerun could not establish>

## Final gate result

Choose one: **PASS**, **FAIL — revision required**, **INCONCLUSIVE**, or **NOT A GATE**. Apply the criteria in [`workflows/adversarial-review.md`](../../workflows/adversarial-review.md). A self-review cannot pass a gate that requires independence.

Record this result only in the gate-result section. The review artifact's front matter `status` describes its lifecycle and must use the FRAMEWORK-002 vocabulary; do not set it to `PASS`, `FAIL`, or `INCONCLUSIVE`. An `INCONCLUSIVE` result blocks progression.

- **Result:** <one permitted result>
- **Why this result follows the criteria:** <finding states, scope, evidence, owner decisions, independence>
- **Approval:** <not granted, or authorized approver + date + evidence>
- **Next action / owner:** <bounded action, decision request, or “None; transition may proceed”>

## References

- <reviewed artifact and exact version>
- <governing criteria and related decisions>
- <resulting revision and evidence>
