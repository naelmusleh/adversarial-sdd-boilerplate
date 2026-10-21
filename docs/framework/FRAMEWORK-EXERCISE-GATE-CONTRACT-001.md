---
id: FRAMEWORK-EXERCISE-GATE-CONTRACT-001
type: framework-adversarial-exercise
title: Frozen v1.0 gate-contract adversarial review cases
status: draft
version: 1.0
created: 2026-10-20
updated: 2026-10-20
related-artifacts: FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-GATE-TRACEABILITY-001, FRAMEWORK-ADV-008, FRAMEWORK-BACKLOG-001
---

# FRAMEWORK-EXERCISE-GATE-CONTRACT-001 — Adversarial review cases

## Scope and evidence boundary

This is the required adversarial test plan for a reviewer who did not author FRAMEWORK-GATE-CONTRACT-001 v1.0. It freezes the attack questions and expected disposition; it is not a claim that any case has already been executed or passed. The reviewer records actual inspected contract/schema/fixture revision, conclusions, findings, and rerun evidence in a separate review artifact. Fixtures are synthetic structure only, not application gate evidence.

For each case the reviewer must identify which layer can reject it: JSON Schema shape, FW-TASK-018 relational validator, workflow/CI runtime evidence, or accountable human judgment. A prose rule must not be described as machine-enforced unless an executable check exists.

| Case | Adversarial input / attack | Expected contract outcome | Enforcement layer to verify |
|---|---|---|---|
| ADV-GC-01 Transition skip | Prior immutable G-REQ record is `failed`; new record claims `passed` directly, omits remediation linkage, or reuses old run IDs. | Reject transition; require a new `in-progress` run and supersession/fix evidence. Previous record remains immutable. | FW-018 prior-run/transition validator; schema only provides linkage fields. |
| ADV-GC-02 Changed-file digest | A frozen requirement/specification file changes while its old digest remains in the run/manifest. | Reject evidence as stale and keep affected gate/downstream runs incomplete. | FW-018 recomputes bytes/digests and invalidates linked runs; `invalid/changed-file-hash.json`. |
| ADV-GC-03 Stale source evidence | A command/CI/review record references a different source commit or scope than the gate run. | Reject evidence for current pass; require rerun at the proposed source revision/scope. | FW-018/019 cross-links; `invalid/stale-source-revision.json`. |
| ADV-GC-04 Unsupported PASS | Gate record says `passed` based on a score, artifact existence, copied terminal text, or rationale text with no permitted evidence IDs. | Reject structurally where possible; otherwise remain `not-ready`, `failed`, or `blocked`; never infer a pass. | Schema outcome/evidence constraints plus FW-018 ID/type/provenance and FW-019 observed-run checks. |
| ADV-GC-05 Improper waiver | An owner accepts risk for a blocking requirement, security boundary, failed required check, or unrelated finding. | Reject `passed-with-accepted-risk`; mandatory blockers remain failed/blocked and dependent work stops. | Schema excludes blocking finding in risk result; FW-018 cross-checks finding IDs/authority; owner policy is human-reviewed. |
| ADV-GC-06 Premature architecture selection | G-FEAS marks a provider/model/service unknown or unsupported, yet dependent task becomes unblocked and G-ARCH treats selection as approved capability. | Keep dependent work blocked or explicitly conditional with a safe-work boundary; architecture cannot assert feasibility. | FW-018 probe/task state consistency; owner/expert verifies evidence and scope. |
| ADV-GC-07 False independence | Reviewer is the author, shares the same review context, omits input disclosure, or labels a self-review `independent`. | Record overlap/limits; where policy requires independence, result is blocked/inconclusive and cannot satisfy the review gate. | Schema captures fields; workflow and reviewer/owner judgment establish identity/context limitations. |
| ADV-GC-08 Platform applicability gap | A requirement is covered for web but omitted for supported iOS/Android or failure/recovery states are silently excluded. | Missing surface/category blocks coverage; each exclusion needs scope-specific rationale and authority. | Schema requires applicability/failure-category rows; FW-018 checks requirement/platform coverage; reviewer judges applicability. |
| ADV-GC-09 Feasibility-as-implementation | Agent writes production code or selects a committed dependency while claiming the feasibility gate itself proved the capability. | G-FEAS output remains evidence, dependency states, and bounded experiments only; implementation waits for a task-ready G-ARCH contract. | Workflow/contract boundary and task-state check; owner/reviewer judges whether experiment was bounded/non-production. |
| ADV-GC-10 Legacy auto-promotion | An old app has no contract pin, or a legacy record is silently rewritten into v1.0 and reported as passed. | Preserve old semantics until explicit migration; migration creates linked new records and does not edit/promote history. | App lock/version policy, initializer/validator, and migration review. |

## Reviewer completion record

Before execution, record frozen contract version, source commit, schema/fixture digests, reviewer identity/mode, author overlap, context/input disclosure, tools, and limits. For each case record `pass`, `fail`, `blocked`, or `inconclusive`, the actual control exercised, observed diagnostic/evidence, and any false positive/negative. Resolve blocking findings and rerun the full affected case set before changing this exercise's status or approving contract v1.0.
