---
id: FRAMEWORK-ADV-001
type: adversarial-review
title: CAP-002 adversarial review workflow conformance exercise
status: in-review
version: 0.1
created: 2026-10-07
updated: 2026-10-08
reviewed-artifact: WORKFLOW-ADV-001
reviewed-version: 0.1
related-artifacts: CAP-002, FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-SPEC-001
---

# FRAMEWORK-ADV-001 — CAP-002 workflow conformance exercise

## Review request

- **Gate / lifecycle transition:** Validate whether the manual adversarial review procedure can be followed, records findings and dispositions, and yields an evidence-based gate state before it is reused for a framework/product approval.
- **Review scope:** Inputs and frozen target; critic/reviser/verifier/approver roles; evidence vs inference; finding fields and severities; disposition; revision; rerun; pass/fail/inconclusive states; bounded stop; owner residual-risk acceptance.
- **Questions to answer:** Can the procedure produce a traceable finding, disposition, revision, rerun result, and justified final state without relying on undocumented chat convention?
- **Approval authority:** Framework/product owner, as applicable to the reviewed artifact.
- **Evidence cutoff:** 2026-10-07, America/New_York.
- **Source revision:** Initial workflow v0.1 at repository commit `0d85b6105cda0e58d9faf7bf336ade3143182c71`; revised workflow is the current working-tree version linked below. No commit was created for this exercise.

## Review method

- **Critic:** Current authoring agent.
- **Reviewer mode:** `self-review`.
- **Independence explanation:** The same agent inspected, revised, and reran the procedure in one task context. This is a bounded conformance exercise, not an independent adversarial review.
- **Reviser:** Current authoring agent.
- **Verifier:** Current authoring agent.
- **Sources inspected:** CAP-002 v0.1; workflow v0.1 at the source revision above; FRAMEWORK-001 and FRAMEWORK-002; FRAMEWORK-SPEC-001 and FRAMEWORK-BACKLOG-001; prior application-review examples in the development source; reusable review template v0.1.
- **Limits:** No independent critic or verifier participated. No owner decision or residual-risk approval was requested. This exercise checks procedure completeness and status logic; it does not verify external product facts or retroactively validate existing product review approvals.

## Finding register

### FRAMEWORK-ADV-001/FINDING-001 — Rerun and gate status did not have deterministic criteria

- **Severity:** Major
- **Target location:** Workflow v0.1, procedure steps 5–7 and Completion.
- **Evidence:** The initial procedure said to rerun after revision and mark approved when acceptance criteria were satisfied, but did not require checking each prior finding, define PASS/FAIL/INCONCLUSIVE, state reviewer-independence effects, or separate accepted residual risk from resolution.
- **Inference:** Reviewers could report “approved” while a blocking finding remained unverified or a required independent review had not occurred.
- **Impact / failure mode:** A lifecycle gate could be treated as passed without reproducible evidence or authorized risk acceptance.
- **Recommendation / options:** Define exact rerun states, full-scope recheck, gate outcomes, independence rule, and the data required for owner risk acceptance.
- **Owner decision required:** No; this is a framework process control grounded in FRAMEWORK-001 §§3, 5, and 9.
- **Initial disposition:** resolved

### FRAMEWORK-ADV-001/FINDING-002 — The remediation loop had no bounded stop condition

- **Severity:** Major
- **Target location:** Workflow v0.1, procedure and Completion.
- **Evidence:** The initial procedure required resolving findings and rerunning but set no limit or escalation path for findings that persisted after revision.
- **Inference:** The process could repeat critique and polish indefinitely without new evidence or a clear owner action.
- **Impact / failure mode:** Work may become an unbounded exercise and leave the owner without a decision-ready account of blockers or next steps.
- **Recommendation / options:** Define a bounded critic/revise/rerun cycle and an escalation/replanning route when a rerun remains failed.
- **Owner decision required:** No; the bounded rule implements the framework’s finite-gate intent.
- **Initial disposition:** resolved

### FRAMEWORK-ADV-001/FINDING-003 — Review records did not require a complete, auditable risk-acceptance record

- **Severity:** Major
- **Target location:** Template v0.1, finding register/result; workflow v0.1, disposition step.
- **Evidence:** The initial template provided a generic disposition cell and an approval field, but did not require risk scope, impact, mitigation, revisit condition, authorized owner, or decision evidence.
- **Inference:** A finding could be called accepted without demonstrating informed, authorized acceptance or a plan to revisit it.
- **Impact / failure mode:** A blocking concern might be silently waived, and future reviewers would not know what risk was accepted or when to reconsider it.
- **Recommendation / options:** Separate `accepted-risk` from `resolved`; require owner authority, scope, risk/impact, mitigation/monitoring, revisit trigger/date, and a durable decision reference.
- **Owner decision required:** No for defining the required record; an actual residual-risk approval remains an owner decision.
- **Initial disposition:** resolved

## Disposition and revision

| Finding | Disposition | Rationale / decision evidence | Change made or follow-up | Target revision/link | Owner and revisit trigger if deferred/risk |
| --- | --- | --- | --- | --- | --- |
| FRAMEWORK-ADV-001/FINDING-001 | resolved | Workflow now defines prior-finding verification, explicit result states, independence restrictions, and required residual-risk evidence. | Added rerun procedure, status rules, and residual-risk disposition. | [WORKFLOW-ADV-001 v0.2](../../workflows/adversarial-review.md), §§4–6; [template v0.2](../templates/adversarial-review.md) | N/A |
| FRAMEWORK-ADV-001/FINDING-002 | resolved | Workflow now bounds each cycle and defines stop/escalation routes for persistent failures. | Added a bounded remediation section and completion checklist. | [WORKFLOW-ADV-001 v0.2](../../workflows/adversarial-review.md), §7 | N/A |
| FRAMEWORK-ADV-001/FINDING-003 | resolved | Template and workflow now distinguish risk acceptance from resolution and prescribe the approval evidence. | Added a dedicated owner residual-risk acceptance section and decision requirements. | [Template v0.2](../templates/adversarial-review.md); [WORKFLOW-ADV-001 v0.2](../../workflows/adversarial-review.md), §4 | N/A |

**Initial gate result on workflow v0.1:** FAIL — revision required. The three major findings above left rerun, status, bounded-stop, and risk-acceptance behavior too ambiguous to use as a deterministic gate procedure.

### Residual-risk acceptance (complete only when used)

No owner residual-risk approval used for this review. This exercise did not seek to waive any finding. The lack of independent review is recorded as a limitation and is not owner-accepted risk.

## Rerun and verification

- **Rerun date:** 2026-10-07.
- **Verifier and reviewer mode:** Current authoring agent; `self-review`, same context as critic and reviser.
- **Scope:** Rechecked the full original procedure/template scope against the revised workflow and template.
- **Target revision:** WORKFLOW-ADV-001 v0.2 (working-tree file `workflows/adversarial-review.md`) and template v0.2 (`docs/templates/adversarial-review.md`); these files have not been committed.
- **Prior finding checks:**

| Finding | Rerun state | Evidence confirming resolution or explaining remaining risk |
| --- | --- | --- |
| FRAMEWORK-ADV-001/FINDING-001 | verified-resolved | Workflow §5 requires a full-scope rerun and checks each prior finding; §6 defines PASS, FAIL, INCONCLUSIVE, and NOT A GATE; mandatory independence prevents self-review PASS. Template has per-finding rerun evidence and final-result fields. |
| FRAMEWORK-ADV-001/FINDING-002 | verified-resolved | Workflow §7 defines one critic/disposition/revision/full-rerun cycle, conditions for one specifically bounded further cycle, and escalation after a second failed attempt. |
| FRAMEWORK-ADV-001/FINDING-003 | verified-resolved | Workflow §4 defines `accepted-risk` as owner-only and requires scope, impact, mitigation, revisit condition, and authority; template captures these fields and decision evidence. |

- **New findings:** None identified in the self-review rerun scope. This statement is limited by the non-independent method.
- **Verification limits during the exercise:** Manual document inspection only; no independent review, automated completeness check, or external evidence check occurred. The repository-wide artifact validator was run afterward and its result is recorded below.

**Procedure conformance on rerun:** The revised text satisfies the checks mapped to all three findings. This is a self-check result only; it is not a separate PASS authorization for a mandatory independent review gate.

## Final gate result

- **Result:** **INCONCLUSIVE**.
- **Why this result follows the criteria:** The three identified procedure gaps were addressed and their revised clauses were checked. However, the critic, reviser, and verifier were the same agent/context, so this exercise cannot pass a framework gate that requires independent adversarial review. It demonstrates the record/status path and supports CAP-002’s manual-workflow status; it does not certify independent review or approve the procedure for a mandatory independent gate.
- **Approval:** Not granted.
- **Next action / owner:** Obtain an independent review of CAP-002 v0.2 and this exercise before claiming that CAP-002 satisfies an independent-review gate. If that review finds material gaps, follow the bounded remediation and rerun procedure. No owner decision is needed to use the manual workflow for reviews whose governance does not require independence.

## References

- [CAP-002 — Adversarial Review Workflow](../../framework/capabilities/CAP-002-adversarial-review.md)
- [Adversarial Review Workflow v0.2](../../workflows/adversarial-review.md)
- [Reusable adversarial review template](../templates/adversarial-review.md)
- [FRAMEWORK-001](../constitution/FRAMEWORK-001.md) and [FRAMEWORK-002](../constitution/FRAMEWORK-002.md)

## Repository checks performed after the exercise

- Ran `python3 scripts/artifacts.py validate`. It **failed** on the separate untracked `docs/templates/app-project/README.md`, which is a plain starter README without artifact front matter. That file is outside this task's scope and was not modified. The validator did not report a problem in the four artifacts changed for CAP-002.
- Ran a focused manual script over CAP-002, the workflow, review template, and this record. It checked required front-matter fields for artifact files and resolved relative Markdown links in all four changed files. Result: **PASS**; 25 Markdown links scanned. This is a focused structural check, not a replacement for the repository validator or independent review.

## Follow-up repository validation — 2026-10-07

The earlier repository validation failure is historical and was caused by the artifact tool scanning the nested app-starter README as if it were a live artifact. The tool was updated to exclude the entire `docs/templates/` subtree. A later independent check ran `python3 scripts/artifacts.py validate` and observed **PASS — Validated 18 artifacts**. This updates repository validation evidence only; it does not change this exercise's `INCONCLUSIVE` independence result.
