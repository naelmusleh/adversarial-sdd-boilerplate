---
id: FRAMEWORK-CX-001
type: framework-interaction-contract
title: FW-TASK-028 nonvisual quality and traceability interactions
status: draft
version: 0.1
created: 2026-10-23
updated: 2026-10-23
related-artifacts: FRAMEWORK-COVERAGE-001, FRAMEWORK-FEASIBILITY-009, FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, DECISION-026, GATE-CATALOG-001
---

# FRAMEWORK-CX-001 — FW-TASK-028 nonvisual quality and traceability interactions

## G-CX work record

- **Gate:** G-CX — in progress; no pass is asserted.
- **Task and requirements:** FW-TASK-028; FR-FW-029, FR-FW-030, FR-FW-031.
- **Frozen journey/surface scope:** FRAMEWORK-COVERAGE-001 v0.2, independently passed at commit `7300427d0e18b0b6367321cb52e9992eaf8af7ba`; G-COVERAGE Verify Pipeline run [40013869197](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40013869197) passed on that revision.
- **Design target:** A nonvisual, repository-based governance workflow. The interaction artifact is a CLI/CI/review trace, not a rendered UI or clickable prototype. No production command is claimed to exist.
- **Surfaces:** local repository/CLI artifacts; hosted GitHub Actions/Checks; GitHub pull-request review or equivalent.
- **Evaluator/method:** the framework has no product UI or tool decision selecting Impeccable. Use the tool-neutral critique procedure in GATE-CATALOG-001. Independent reviewer will inspect the full trace and record findings; this document does not claim runtime, device, or accessibility testing.
- **Boundary:** No code implementation, app-specific threshold selection, positive exception authorization, real application profile, Figma artifact, or excluded v2 work.

## Interaction principles

1. Every result names the selected task, exact source revision, policy/profile revision, measured scope, required checks, and status in plain text. Color or icons may reinforce a state but never carry it alone.
2. Report distinct states for pass, fail, stale, in-progress, unavailable, and blocked. An unsupported metric or missing provider result cannot be rendered as a pass.
3. Show the reason and next safe action next to each blocked state. Do not silently retry, edit source, lower policy, accept an exception, or convert missing data into zero.
4. Let reviewers follow each assertion to its criterion, changed path, check-run identity/conclusion, and evidence link. Keep raw logs bounded; never expose secrets or send tokens to package/test tools.
5. Explain that coverage is execution evidence, not proof of assertion quality or correctness. Present mutation/contract evidence with its exact fixture and limitations.
6. Keep an exception path visibly unavailable while no authorized identity/role is configured. Do not show a misleading “approve exception” affordance.
7. Provide equivalent information in local traces, hosted check summaries, and review artifacts. This does not promise identical layouts or mobile behavior.

## Proposed interaction traces

These are conceptual, non-executable examples of what the reviewed interaction should communicate. They intentionally avoid defining unapproved command names, configuration syntax, or threshold values.

### Trace A — owner reviews an app quality policy

**Entry:** The owner opens the app-owned profile record with the approved app requirements and selected profile in view.

**System/agent summary:**

```text
Quality policy review
Application profile: <profile-id> / <version>
Policy owner: <owner identity>
Risk dimensions: <declared dimensions>
Metrics and scope: <declared metrics, included paths, excluded paths>
Unavailable metrics: <metric> — <reason>
Threshold rationale: <linked policy rationale>

Framework defaults applied: none
Coverage proves correctness: no
Result: REVIEW REQUIRED
```

The owner can inspect rationale and exclusions, amend the policy, or leave the policy unaccepted. A missing rationale or unsupported metric labeled as passing is shown as a named blocking issue. No numeric values are proposed by this framework task.

**Success exit:** A complete, versioned, app-owned policy is ready for owner review and later architecture/implementation work.

**Failure exit and recovery:** Missing or contradictory policy fields remain visible and blocked; the owner/agent corrects the record and presents the revised version. The system does not silently inherit a framework threshold.

### Trace B — developer/agent binds a change to intent

**Entry:** A selected task and its complete acceptance-criteria set are approved, and the candidate repository revision is available.

**Trace summary:**

```text
Change trace
Task: <task-id>
Source revision: <full commit SHA>
Changed paths: <canonical path list>
Criteria: <complete selected criterion set>
Path-to-criterion links: <reviewable mapping>
Required checks: <provider check names/IDs>

Trace result: BLOCKED
Finding: src/<path> has no valid criterion link
Next action: update the mapping, then regenerate evidence for the new revision
```

A complete mapping moves to provider-check verification. A swapped or unknown mapping, stale SHA, missing criterion, missing check, or unmapped changed path stays blocked. Diagnostics identify affected paths and criteria; they never delete or rewrite source.

**Success exit:** The exact source SHA, selected task/criteria, changed paths, and required check identities are linked.

**Failure exit and recovery:** Correct the mapping or task scope, create a new source revision if code changes, and rerun. Prior results remain tied to their earlier SHA and cannot be reused as current evidence.

### Trace C — CI reports quality and trace results

**Entry:** The policy and trace are versioned and bind to the candidate SHA; a supported profile adapter is selected.

**Check summary:**

```text
Verification result
Repository: <repository identity>
Source revision: <full commit SHA>
Profile: <profile-id> / <version>
Measured scope: <included paths and dimensions>
Excluded/generated paths: <paths and declared reasons>

Coverage: <measured value and scope>
Assertion-strength probe: <fixture, command, observed outcome>
Required provider checks:
  <check name> — <run ID> — <conclusion> — <head SHA>

Unavailable: <metric/check> — <reason>
Overall state: <PASS | FAIL | BLOCKED | UNAVAILABLE>
Evidence: <stable links/digests>
Limits: coverage and mutation evidence do not prove semantic correctness
```

The summary can show PASS only when the app policy’s declared conditions and exact-revision checks are satisfied. Missing, in-progress, failed, stale, or provider-unverified checks remain distinct and block a pass claim. A high line percentage beside an ineffective assertion is explicitly called out as weak evidence.

**Success exit:** Reviewer can inspect the evidence and exact-revision provider checks without inferring success from a score.

**Failure exit and recovery:** Failed checks identify the affected criterion/scope and link to bounded output. Unsupported tooling is reported as unavailable. Rerun only after correction, and bind the new output to the new exact SHA.

### Trace D — reviewer resolves an exception or abuse finding

**Entry:** A pull request contains a mixed-scope path, suspicious quality claim, or proposed exception.

**Review state:**

```text
Review required
Finding: <stable finding ID>
Affected path/check: <canonical path or provider check>
Task and criteria: <linked IDs>
Source revision: <full commit SHA>
Evidence: <diagnostic and provider references>

Exception authorization: UNAVAILABLE
Reason: no configured, independently verifiable authorized identity/role
Decision: BLOCKED — exception not accepted
Next action: resolve the mapping/check or obtain a separately approved authorization model
```

The reviewer can request changes or leave the result blocked. There is no pass-through based on a free-text approver name, score, or unexplained risk label. If a future owner-approved authorization model exists, its authority and scope must be designed and reviewed separately.

**Success exit:** Findings are resolved and the complete affected scope is rerun at the new current revision, or remain blocked with an explicit owner decision required.

## State and recovery coverage

| State | User-visible information | Safe action |
| --- | --- | --- |
| Ready for review | Policy/trace version, exact SHA, scope, required checks, evidence links | Inspect and accept or request a change under the applicable owner/reviewer role. |
| Pass | Criteria/checks satisfied for the named scope and SHA; limitations remain visible | Continue only to the next lifecycle gate; do not infer implementation/release readiness. |
| Fail | Failed criterion/check, affected path, expected condition, bounded evidence | Correct the cause and rerun the affected complete scope. |
| Stale | Current SHA differs from the evidence SHA | Regenerate trace/check evidence for the current SHA. |
| In progress | Required check is pending or incomplete | Wait for that exact run or treat it as blocked; do not claim pass. |
| Unavailable | Tool/provider/metric is unsupported or unreachable, with reason | Keep the relevant claim unavailable; use only a separately approved alternative evidence method. |
| Blocked | Missing mapping, authority, evidence, or required decision | Resolve the stated dependency; no automatic retry, policy weakening, or exception acceptance. |

## Cross-surface contract

| Information/action | Local repository/CLI | Hosted CI/checks | Pull-request review |
| --- | --- | --- | --- |
| Task, criteria, source SHA | Canonical policy/trace records; exact revision shown | Consumed from checkout event and manifest | Linked for reviewer inspection |
| Risk policy and scope | Owner-authored, versioned artifacts | Read-only evaluation input | Rationale/exclusions reviewable |
| Metric/check state | Local diagnostic only if explicitly run; not trusted CI evidence | Provider results and supported measurements | Exact IDs, conclusions, scope and limits visible |
| Failure and recovery | Named fields/paths and next action | Nonzero/blocking result with bounded details | Request changes or keep blocked |
| Exceptions | No local author string grants authority | No positive exception support in this scope | No approval affordance; fail closed pending separate owner-approved model |
| Source mutation | None from diagnostics | Runner operates on disposable fixtures or checkout; no auto-edit | Reviewer disposition does not rewrite source |

## Tool-neutral critique record

- **Reviewer/evaluator:** Independent reviewer assignment pending.
- **Method:** Manual tool-neutral review of the complete interaction contract and all four covered journeys; no visual prototype exists or is claimed.
- **Scope to inspect:** Traces A–D; all seven failure categories; all three interaction surfaces; six synthetic profile and product-boundary statements in FRAMEWORK-COVERAGE-001; accessibility of textual status and evidence navigation; clarity of recovery actions and owner-decision boundaries.
- **Evidence location:** This artifact at its exact committed revision; G-COVERAGE evidence in FRAMEWORK-COVERAGE-001; product requirements FR-FW-029–031 and DECISION-026.
- **Runtime/device limits:** No command/UI execution, screen-reader, responsive/mobile, or production CI behavior is verified by these text traces. Those are later implementation checks only if approved.
- **Findings/disposition:** Pending independent critique. No finding is silently treated as resolved.
- **Gate result:** In progress.

## Exclusions and next action

This interaction contract does not choose thresholds or configuration fields, implement commands, integrate production profile validators, introduce an authorized-exception workflow, or claim correctness/security from a coverage number. Provider-check binding was shown in bounded G-FEAS only; production integration remains unproven.

**Next action:** Independent reviewer critiques this complete artifact against GCX-01–03. Resolve and rerun the full scope if findings are raised. G-CX can pass only after review and exact-revision Verify Pipeline succeed. G-ARCH is the next permitted lifecycle stage if G-CX passes; G-IMPL remains unauthorized pending architecture and its other required evidence.
