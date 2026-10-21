---
id: FRAMEWORK-ADV-008
type: adversarial-review
title: Independent G-IMPL review of versioned app handoffs and commit-push controls
status: revision-required
version: 0.3
created: 2026-10-20
updated: 2026-10-20
reviewed-artifact: FRAMEWORK-BACKLOG-001
reviewed-version: 2.1
related-artifacts: FRAMEWORK-SPEC-001, GATE-CATALOG-001, FRAMEWORK-BACKLOG-001, WORKFLOW-AI-ENGINEERING-001
---

# FRAMEWORK-ADV-008 — FW-TASK-015/016 G-IMPL review

## Review request

- **Gate / lifecycle transition:** G-IMPL — framework validator, app initializer/templates/workflow, and commit/push execution procedure.
- **Review scope:** FW-TASK-015 and FW-TASK-016 implementation and evidence in commits `23071ee3fd601ca5b154dc351a012126d866de55`, `856806f`, `0a1e1b7`, at reviewed repository revision `30d76cd3b8b59619a23f4ceb99b17d8c33e03652`.
- **Questions to answer:** Do the implementation and records satisfy each backlog acceptance criterion? Can malformed or retyped artifacts bypass the gate checks? Does framework revision pinning identify the content actually copied? Is the commit/push tabletop evidence inspectable?
- **Approval authority:** Framework owner. This review does not accept residual risk or mark either task complete.
- **Evidence cutoff:** 2026-10-20, America/New_York.
- **Source revision:** `30d76cd3b8b59619a23f4ceb99b17d8c33e03652`.

## Review method

- **Critic:** `/root/sdd_governance` independent review agent.
- **Reviewer mode:** `independent` source review.
- **Independence explanation:** The reviewer was assigned a read-only review of the frozen repository revision and was not the author of the reviewed implementation commits. The review report is recorded here; identity/context separation is a procedural claim, not cryptographic proof.
- **Reviser:** Framework implementation agent.
- **Verifier:** Pending after remediation.
- **Sources inspected:** `scripts/artifacts.py`, `scripts/init_app_project.py`, app handoff/lock/workflow templates, generated instructions, `workflows/ai-engineering-execution.md`, and FW-TASK-015/016 acceptance criteria and evidence in `FRAMEWORK-BACKLOG-001`.
- **Limits:** Read-only source review. The critic did not run tests, hosted CI, a fresh-app initialization, GitHub branch-protection inspection, or remote publication scenarios. Those require separately recorded execution evidence.

## Finding register

### FRAMEWORK-ADV-008/FINDING-001 — Gate PASS validation is bypassable by changing artifact type

- **Severity:** Major; blocking for FW-TASK-015 criterion 3.
- **Target location:** `scripts/artifacts.py`, `command_validate`, gate-record collection and governance checks.
- **Evidence:** Gate records are collected only when front matter `type` equals `gate-record` or `lifecycle-gate-record`. The governance checks then examine G-REQ/G-ARCH `gate-result` and require the corresponding manifest. A Markdown artifact can declare `gate-id: G-REQ` and `gate-result: passed` while using another type and avoid those checks.
- **Inference:** A mislabeled or deliberately retyped gate claim can pass general artifact validation without its required handoff manifest.
- **Impact / failure mode:** The validator does not meet the promise to reject a G-REQ/G-ARCH PASS claim lacking a valid manifest.
- **Recommendation / options:** Detect governance gate claims independently of the declared artifact type and reject invalid type/gate combinations; add a fixture that retypes a PASS record.
- **Owner decision required:** No; this is a validator correctness defect.
- **Initial disposition:** unresolved.

### FRAMEWORK-ADV-008/FINDING-002 — Invalid review-input type raises an uncontrolled diagnostic error

- **Severity:** Minor; actionable-diagnostic gap for FW-TASK-015 criterion 3 and NFR-FW-003.
- **Target location:** `scripts/artifacts.py`, G-ARCH `review_inputs` validation.
- **Evidence:** The validator tests `purpose` membership in a set before confirming that the JSON value is a string. An array or object raises `TypeError` rather than producing a controlled validation diagnostic.
- **Inference:** Validation remains non-zero, but malformed user input can surface as an uncaught exception/traceback instead of a file/field-specific actionable error.
- **Impact / failure mode:** Users and CI receive poor diagnostics and the schema boundary is not robust to arbitrary JSON value types.
- **Recommendation / options:** Type-check `purpose` before set membership and add array/object negative fixtures.
- **Owner decision required:** No.
- **Initial disposition:** unresolved.

### FRAMEWORK-ADV-008/FINDING-003 — Framework revision can misidentify dirty copied source

- **Severity:** Minor; provenance gap for FW-TASK-015 criterion 1 and FR-FW-014.
- **Target location:** `scripts/init_app_project.py`, `discover_framework_revision` and copied source inputs.
- **Evidence:** The initializer reads `HEAD` as the framework revision without checking whether the working tree is dirty, then reads templates and helper files from the working tree. The per-file lock digests identify several copied files but do not prove that all generated content corresponds to the declared clean commit or that revision-linked documentation matches copied bytes.
- **Inference:** Initialization from a dirty checkout may produce an app claiming an immutable source revision that does not identify the complete source used.
- **Impact / failure mode:** The app’s framework provenance can be overstated or ambiguous even when the locked files later match their digests.
- **Recommendation / options:** Refuse dirty-source initialization for tracked inputs or materialize the selected commit tree before generation; record and validate the exact copied-source state and add regression fixtures.
- **Owner decision required:** No; select the safer mechanism that preserves documented archive support.
- **Initial disposition:** unresolved.

### FRAMEWORK-ADV-008/FINDING-004 — FW-TASK-016 tabletop evidence is not inspectable

- **Severity:** Major; blocking for FW-TASK-016 evidence and FR-FW-015 acceptance.
- **Target location:** `FRAMEWORK-BACKLOG-001`, FW-TASK-016 execution evidence; expected scenario record absent.
- **Evidence:** The backlog states that a paper tabletop covered successful publication, unrelated dirty files, failed checks, missing authorization/remote/credentials, and post-push correction, but no task-specific record with scenario setup, expected outcomes, observed decisions, or evidence links was found. `FRAMEWORK-EXERCISE-001` covers a different lifecycle/feasibility tabletop.
- **Inference:** A future reviewer cannot reproduce or verify the claim that the commit/push procedure handles those cases.
- **Impact / failure mode:** FW-TASK-016 acceptance evidence is asserted but not auditable.
- **Recommendation / options:** Create a bounded, versioned commit/push tabletop record covering each required scenario and link it from FW-TASK-016. Keep it explicitly labeled as a paper exercise, not a live remote test.
- **Owner decision required:** No.
- **Initial disposition:** unresolved.

### FRAMEWORK-ADV-008/FINDING-005 — Explicit revision can mislabel Git checkout contents

- **Severity:** Major; blocking for FW-TASK-015 criterion 1.
- **Target location:** `scripts/init_app_project.py`, `discover_framework_revision`.
- **Evidence:** When run from a clean Git checkout, the initializer validates a supplied `--framework-revision` only as a 40-character SHA and returns it without comparing it with `HEAD`. It can therefore copy current-checkout inputs while recording a different revision.
- **Impact / failure mode:** The generated lock and README may claim provenance that does not identify the copied framework bytes.
- **Recommendation:** In Git checkout mode require the explicit SHA to equal the resolved `HEAD`; retain explicit SHA input for archive mode, which has no Git metadata.
- **Owner decision required:** No; provenance must be truthful.
- **Initial disposition:** unresolved.

### FRAMEWORK-ADV-008/FINDING-006 — Legacy PASS records may be forced into new handoff rules

- **Severity:** Major; potential compatibility break for FW-TASK-015 criterion 5.
- **Target location:** `scripts/artifacts.py`, `application_governance_problems`.
- **Evidence:** Gate-record handoff checks run even when an app has no framework lock and no handoff manifest. A pre-existing G-REQ/G-ARCH PASS record without the newly introduced manifest can fail validation despite the stated legacy compatibility promise.
- **Impact / failure mode:** Existing app repositories can become invalid merely by adopting an updated artifact helper, without having opted into the versioned lock/manifest contract.
- **Recommendation:** Define the opt-in boundary and preserve no-lock/no-manifest legacy behavior; retain strict enforcement once a lock or manifest is present. Add a regression fixture containing a legacy PASS record.
- **Owner decision required:** No, provided the existing legacy-compatibility acceptance criterion governs.
- **Initial disposition:** unresolved.

### FRAMEWORK-ADV-008/FINDING-007 — Declared but absent handoff can evade strict validation

- **Severity:** Major; blocking for FW-TASK-015 criterion 3.
- **Target location:** `scripts/artifacts.py`, `application_governance_problems` legacy opt-in guard.
- **Evidence:** The no-lock/no-manifest compatibility return occurs before inspecting whether a gate record itself declares `handoff-manifest`. A passed G-REQ/G-ARCH record can claim the versioned handoff while the referenced file and lock are absent, then avoid strict validation.
- **Impact / failure mode:** The validator can accept a false versioned handoff claim while preserving legacy compatibility.
- **Recommendation:** Preserve legacy behavior only when records do not claim handoff evidence; treat an explicit manifest link as opt-in and require the lock and populated valid manifest. Add a negative pointer-only fixture alongside the unlinked legacy PASS fixture.
- **Owner decision required:** No; the accepted legacy boundary is no-lock/no-manifest and no declared handoff.
- **Initial disposition:** unresolved.

## Disposition and revision

| Finding | Disposition | Rationale / decision evidence | Change made or follow-up | Target revision/link | Owner and revisit trigger if deferred/risk |
| --- | --- | --- | --- | --- | --- |
| FRAMEWORK-ADV-008/FINDING-001 | resolved in reviewed scope | A passed gate record must carry a recognized gate ID; gate metadata on non-gate artifact types is rejected, and G-REQ/G-ARCH claims remain collected for handoff validation. | Added recognized gate-ID/type checks and a missing-ID negative fixture. Independent source reviewer confirmed missing/misspelled IDs and type reclassification fail closed. | Pending commit; changed files `scripts/artifacts.py`, `tests/test_artifacts.py` | N/A |
| FRAMEWORK-ADV-008/FINDING-002 | resolved | Wrong-typed `review_inputs.purpose` now produces a controlled diagnostic before membership checks; negative fixture is present. | Implemented and exercised in local test suite at `8c47b52`. | `3119388` and local verification at `8c47b52` | N/A |
| FRAMEWORK-ADV-008/FINDING-003 | resolved for covered paths | Dirty tracked or relevant untracked framework inputs are rejected; unrelated untracked files are permitted; archive initialization requires explicit revision. | Implemented and regression-tested in local test suite at `8c47b52`. Archive-source provenance remains bounded by the supplied explicit revision. | `3119388` and local verification at `8c47b52` | N/A |
| FRAMEWORK-ADV-008/FINDING-004 | resolved as inspectable paper evidence | The seven-scenario commit/push tabletop is durable and explicitly does not claim live Git, remote, hosted CI, or branch-protection evidence. | Added `FRAMEWORK-EXERCISE-002` and linked it from FW-TASK-016. Independent reviewer confirmed the tabletop is inspectable and its limits are clear. | `8c47b52` | N/A |
| FRAMEWORK-ADV-008/FINDING-005 | unresolved | Explicit revision must identify the exact files used in a Git-backed initialization. | Require a supplied revision to match checkout `HEAD`; add a mismatch regression fixture. | Pending | N/A |
| FRAMEWORK-ADV-008/FINDING-006 | unresolved | No-lock apps must remain compatible with the legacy contract. | Scope strict gate handoff enforcement to versioned adoption and add a legacy PASS fixture. | Pending | N/A |
| FRAMEWORK-ADV-008/FINDING-007 | unresolved | An explicit versioned handoff claim cannot be accepted without its lock and populated manifest. | Make a declared handoff link opt into strict validation; add pointer-only negative fixture. | Pending | N/A |

No owner residual-risk approval used for this review.

## Rerun and verification

- **Rerun date:** 2026-10-20.
- **Verifier and reviewer mode:** `/root/sdd_governance`, independent read-only full-scope review at frozen HEAD `44d7d922a82b298275a9dada1bc0eee356e683dc`; no author overlap on the reviewed implementation. The reviewer did not execute tests.
- **Scope:** Full review of FW-TASK-015/016 acceptance criteria and earlier findings. The reviewer identified two additional gaps (FINDING-005/006), so the rerun failed. Local verification after remediation is reviser evidence and is not attributed to the reviewer.
- **Target revision:** `3e7d8805d83167e55b382ab02c422fe9d765792d` (reviewed); the reviewer identified ADV-008/FINDING-007. Its remediation is currently uncommitted.

| Finding | Rerun state | Evidence confirming resolution or explaining remaining risk |
| --- | --- | --- |
| FRAMEWORK-ADV-008/FINDING-001 | resolved in focused source review; execution verified by reviser | Independent review confirms missing/misspelled IDs and retyped gate metadata fail closed. New missing-ID fixture plus the retyping fixture pass in the full 29-test local suite. Broader test execution was performed by the reviser, not the reviewer. |
| FRAMEWORK-ADV-008/FINDING-002 | resolved; reviser-executed | Wrong-typed-purpose fixture passes; full suite executed locally. |
| FRAMEWORK-ADV-008/FINDING-003 | resolved for tested initializer modes; reviser-executed | Dirty relevant inputs reject, unrelated untracked files pass, and explicit-revision archive mode is covered; full suite executed locally. |
| FRAMEWORK-ADV-008/FINDING-004 | resolved as paper tabletop | Independent reviewer confirmed artifact inspectability from prior rerun; scope does not include live publication/CI/settings. |
| FRAMEWORK-ADV-008/FINDING-005 | not-resolved at reviewed revision | A Git checkout could accept an explicit revision different from HEAD and mislabel copied source. |
| FRAMEWORK-ADV-008/FINDING-006 | not-resolved at reviewed revision | Legacy PASS records without a lock/manifest could be rejected by newly adopted validation. |
| FRAMEWORK-ADV-008/FINDING-007 | not-resolved at reviewed revision | A PASS record with an explicit but missing handoff link bypasses strict checks through the legacy early return. |

- **New findings:** FRAMEWORK-ADV-008/FINDING-007 (major declared-handoff bypass). The rerun also resolved FINDING-005 and FINDING-006 within their reviewed scope.
- **Verification limits:** Reviewer did not run tests or inspect hosted repository settings. Local tests and artifact validation are reviser-executed evidence, not independent execution. Hosted CI and repository protection remain unverified.

## Final gate result

- **Result:** **FAIL — revision required.**
- **Why this result follows the criteria:** The rerun resolved the revision-mismatch and legacy-compatibility findings, but found that a record explicitly claiming a missing handoff manifest bypasses strict validation. This blocks FW-TASK-015 acceptance; therefore the combined G-IMPL gate and both backlog tasks remain open pending remediation, local regression checks, and another full-scope independent rerun.
- **Approval:** Not granted.
- **Next action / owner:** Framework implementation agent finishes F007 remediation, executes local checks, commits and pushes the change, then requests a full-scope independent rerun. Framework owner reviews the resulting evidence; neither FW-TASK-015 nor FW-TASK-016 is complete yet.

## References

- `FRAMEWORK-BACKLOG-001` v2.1, FW-TASK-015 and FW-TASK-016.
- `FRAMEWORK-SPEC-001` FR-FW-014/015 and NFR-FW-003.
- `GATE-CATALOG-001` G-IMPL and universal evidence requirements.
- `workflows/ai-engineering-execution.md` commit/push and review procedure.
