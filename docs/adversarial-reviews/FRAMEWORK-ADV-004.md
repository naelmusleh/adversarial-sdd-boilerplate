---
id: FRAMEWORK-ADV-004
type: adversarial-review
title: Independent review of lifecycle and gate contracts
status: approved
version: 0.2
created: 2026-10-10
updated: 2026-10-10
reviewed-artifact: GATE-CATALOG-001
reviewed-version: 0.4
related-artifacts: FRAMEWORK-SPEC-001, GATE-CATALOG-001, WORKFLOW-LIFECYCLE-001, WORKFLOW-DISCOVERY-001, FRAMEWORK-EXERCISE-001, FRAMEWORK-002, DECISION-017
---

# FRAMEWORK-ADV-004 — Independent lifecycle and gate review

## Review request

- **Gate / lifecycle transition:** Independently assess FW-TASK-002's lifecycle handoffs, gate evidence, bounded loops, portability, and tabletop demonstration.
- **Review scope:** Current FRAMEWORK-SPEC-001 v0.6, GATE-CATALOG-001 v0.3, WORKFLOW-LIFECYCLE-001 v0.2, WORKFLOW-DISCOVERY-001 v0.1, FRAMEWORK-EXERCISE-001 v0.2, FRAMEWORK-002 v1.4, and DECISION-017 in DECISION-LOG-001 v2.6. The rerun specifically rechecked the project-setup handoff, G-CX finding disposition rule, tool-neutral evaluator boundary, per-app evaluator policy, and Markdown structure of the gate contracts.
- **Explicit exclusions:** Review of implementation workflows outside the lifecycle handoffs, the separate app-project starter, product-specific app requirements, and external service behavior.
- **Questions to answer:** Can an owner/agent identify a safe next action through blocked setup and feasibility states? Are G-CX findings and tool choices governed consistently with the two decisions? Are finite remediation loops and gate contracts usable and unambiguous?
- **Approval authority:** Framework owner under FRAMEWORK-001. This review does not accept residual risk on the owner's behalf.
- **Evidence cutoff:** 2026-10-10, America/New_York.
- **Source revision:** Base commit `0d85b6105cda0e58d9faf7bf336ade3143182c71`; all reviewed changes were uncommitted working-tree versions. Exact artifact versions are listed above; current observed bytes are identified by those versions and the evidence below.

## Review method

- **Critic / verifier:** Independent reviewer agent, separate from the author making the lifecycle and gate edits.
- **Reviewer mode:** `independent`.
- **Independence explanation:** The reviewer reopened the named current files after the author reported fixes and did not edit the reviewed targets.
- **Reviser:** Framework author.
- **Sources inspected:** The seven artifacts named in the review scope, including the full GATE-CATALOG-001 gate table and tool-neutral procedure, lifecycle next-action and loop sections, discovery setup requirements, tabletop, status rules, and the decision-log entry for DECISION-017.
- **Limits:** The exercise is a paper tabletop and does not establish usability with an external owner, actual GitHub permissions, Impeccable execution, or a real project repository. Those limits are declared in the exercise.

## Finding register

### FRAMEWORK-ADV-004/FINDING-001 — Setup-blocked exercise left canonical drafting boundary unclear

- **Severity:** Major
- **Target location:** FRAMEWORK-EXERCISE-001 v0.1, Stage 2 next action; WORKFLOW-DISCOVERY-001 Pass B.
- **Initial evidence:** The earlier exercise said that if repository access was missing, the agent could “continue repository-neutral product drafting.” Discovery Pass B says to establish the app repository and canonical paths before creating product artifacts.
- **Inference:** “Drafting” could produce durable product content outside the app repository or leave it in chat, contrary to the repository source-of-truth model.
- **Impact / failure mode:** A blocked G-SETUP could create orphaned or competing product artifacts, undermining the canonical handoff.
- **Recommendation:** Permit local app-repository work without a GitHub remote; if no local app repository can be created, restrict work to ephemeral exploration and do not treat it as canonical product documentation.
- **Owner decision required:** No; repository/source-of-truth policy already governs this boundary.
- **Initial disposition:** unresolved.

### FRAMEWORK-ADV-004/FINDING-002 — G-CX residual-finding rule did not explicitly cover every finding

- **Severity:** Major
- **Target location:** GATE-CATALOG-001 v0.2, G-CX pass condition and tool-neutral procedure step 5; app-specific evaluator and risk policy boundary.
- **Initial evidence:** The earlier catalog said G-CX passed with “no unresolved blocking finding” and that unresolved blocking/major findings fail or block. The app-specific critique policy requires every finding to be resolved with evidence or explicitly accepted by the owner, including residual findings.
- **Inference:** An evaluator could read the severity threshold as allowing unresolved minor findings without owner acceptance, weakening the current app's explicit gate and leaving the reusable policy ambiguous.
- **Impact / failure mode:** G-CX could be marked passed with an unaccepted finding, contrary to the framework's explicit residual-risk policy.
- **Recommendation:** State that every finding must be evidenced resolved or explicitly owner-accepted; no severity or score silently waives a finding.
- **Owner decision required:** No; generic G-CX requires explicit per-project policy and documented owner acceptance.
- **Initial disposition:** unresolved.

### FRAMEWORK-ADV-004/FINDING-003 — G-ARCH through G-OPERATE are outside the gate-contract table

- **Severity:** Major
- **Target location:** GATE-CATALOG-001 v0.3, “Gate contracts” section, lines containing G-ARCH, G-IMPL, G-RELEASE, and G-OPERATE after the tool-neutral G-CX procedure.
- **Evidence:** The gate table begins with a Markdown header and rows G-INTENT through G-CX. The table is interrupted by the “Tool-neutral UX critique procedure” heading and prose. The G-ARCH, G-IMPL, G-RELEASE, and G-OPERATE pipe-delimited rows follow that prose without a new table header; the preceding line to G-ARCH is ordinary prose, not a table row. Markdown therefore does not render those four contracts as rows/columns in the canonical table.
- **Inference:** Readers may miss the required-input, pass-condition, and failure-route column mapping for the final lifecycle gates, or treat their text as malformed content instead of contracts.
- **Impact / failure mode:** The canonical catalog presents the earlier gates as structured contracts but the architecture, implementation, release, and operations gates as unstructured pipe text, weakening handoffs at the later and higher-risk stages.
- **Recommendation:** Keep all gate rows contiguous beneath one header and move the tool-neutral G-CX procedure after the complete table, or create an explicitly headed second table for the remaining gates with the same columns.
- **Owner decision required:** No; this is a document-structure correction, not a policy choice.
- **Initial disposition:** unresolved.

## Disposition and revision

| Finding | Disposition | Rationale / decision evidence | Change made or follow-up | Target revision/link | Owner and revisit trigger if deferred/risk |
| --- | --- | --- | --- | --- | --- |
| FRAMEWORK-ADV-004/FINDING-001 | `resolved` | Exercise v0.2 differentiates absence of a GitHub remote from absence of a local app repository and explicitly protects canonical docs from being left outside the app repo. | Continue in the local app repository with remote access recorded as a prerequisite; if a local repo cannot be created, exploration is ephemeral only. | FRAMEWORK-EXERCISE-001 v0.2 | N/A |
| FRAMEWORK-ADV-004/FINDING-002 | `resolved` | GATE-CATALOG-001 v0.3 says every finding must be evidenced resolved or explicitly accepted by the authorized owner and no finding is silently waived by severity or score. Its procedure says any unresolved, unaccepted finding keeps G-CX failed or blocked. DECISION-017 preserves per-app evaluator choice while G-CX remains mandatory. | Clarified pass condition and tool-neutral procedure without bypassing an app's chosen evaluator. | GATE-CATALOG-001 v0.3; DECISION-LOG-001 v2.6 | N/A |
| FRAMEWORK-ADV-004/FINDING-003 | `unresolved` | Current Markdown structure still interrupts the single gate table before G-ARCH, leaving four later gate contracts without the table header/columns. | Move the procedure after the full table or start a second complete table, then rerun this structural review. | GATE-CATALOG-001 v0.3 | Framework author; revisit after the table structure is corrected. |

No owner residual-risk approval used for this review.

## Rerun and verification

- **Rerun date:** 2026-10-10.
- **Verifier and reviewer mode:** Independent reviewer agent; no target edits or authoring overlap.
- **Scope:** Reopened the updated exercise and gate catalog plus the named lifecycle, discovery, specification, constitution, and decision documents. Checked both prior findings, scanned the narrow set for setup/CX portability contradictions, and checked gate-table structure.
- **Target revision:** FRAMEWORK-SPEC-001 v0.6; GATE-CATALOG-001 v0.3; WORKFLOW-LIFECYCLE-001 v0.2; WORKFLOW-DISCOVERY-001 v0.1; FRAMEWORK-EXERCISE-001 v0.2; FRAMEWORK-002 v1.4; DECISION-LOG-001 v2.6.
- **Prior finding checks:**

| Finding | Rerun state | Evidence confirming resolution or explaining remaining risk |
| --- | --- | --- |
| FRAMEWORK-ADV-004/FINDING-001 | verified-resolved | Exercise v0.2 says a missing remote does not prevent work in a separate local app repository and explicitly says not to treat any exploration outside a local app repo as canonical documentation. This reconciles discovery Pass B's requirement to establish canonical app paths before creating product artifacts. |
| FRAMEWORK-ADV-004/FINDING-002 | verified-resolved | GATE-CATALOG-001 v0.3's G-CX pass condition covers every finding; procedure step 5 keeps any unresolved, unaccepted finding failed/blocked. DECISION-017 makes tools adapters for the portable core and assigns future apps their own evaluator while retaining mandatory G-CX. Lifecycle v0.2 reflects this split. |
| FRAMEWORK-ADV-004/FINDING-003 | unresolved | Direct source structure check confirmed that G-ARCH follows prose from the tool-neutral subsection rather than a table header; the G-ARCH through G-OPERATE lines are not contiguous with the earlier table. No correction is present in GATE-CATALOG-001 v0.3. |

- **New findings:** None beyond FRAMEWORK-ADV-004/FINDING-003.
- **Exact checks run:**
  - `python3 scripts/artifacts.py validate` before recording this review — **PASS**, `Validated 31 artifact(s).`
  - Focused Python relative-Markdown-link resolution over the seven requested source artifacts — **PASS**, 47 local links checked, none broken.
  - Focused source-structure check — **FAIL**, confirmed the line before `| G-ARCH |` is ordinary G-CX prose, with no intervening Markdown table header. The G-ARCH/G-IMPL/G-RELEASE/G-OPERATE rows therefore are not part of the earlier Markdown table.
  - Manual cross-document comparison of current G-SETUP handling, G-CX result policy, DECISION-017, lifecycle next-action procedure, and finite review loops — prior findings 001 and 002 are resolved; no additional substantive contradiction found in the requested scope.
- **Post-record integrity checks:** To be recorded after creating this review artifact.
- **Verification limits:** No visual Markdown renderer was available in the checks; the table result follows Markdown table structure in source. The exercise is illustrative rather than an empirical owner walkthrough, as it states.

## Final gate result (initial review and first rerun)

- **Result:** **FAIL — revision required**.
- **Why this result follows the criteria:** The setup and G-CX policy findings are resolved and verified, and local links pass. However, the canonical gate catalog still breaks the table before four lifecycle gate contracts, leaving their evidence/pass/failure columns structurally unrendered. This Major finding affects the clarity of the core lifecycle handoff. Resolve it and rerun the full-scope review before marking FW-TASK-002 complete.
- **Approval:** Not granted. No residual risk accepted.
- **Next action / owner:** Framework author should restore a complete, correctly headed table for G-INTENT through G-OPERATE (with the tool-neutral G-CX procedure outside the table), then request an independent rerun. No owner decision is needed.

## Independent rerun 2 — after gate table correction

- **Rerun date:** 2026-10-10.
- **Verifier and reviewer mode:** Independent reviewer agent, separate from the author of the gate-catalog correction; no reviewed target was edited.
- **Source revision:** Same base commit as above; reviewed working-tree bytes, with exact artifact versions below.
- **Scope:** Rechecked the full prior scope and all three registered findings, including the complete gate catalog structure; compared project-setup behavior, G-CX finding policy, evaluator/tool boundaries, lifecycle next-action and bounded-loop rules, and the tabletop limitations.
- **Current target versions:** FRAMEWORK-SPEC-001 v0.7; GATE-CATALOG-001 v0.4; WORKFLOW-LIFECYCLE-001 v0.2; WORKFLOW-DISCOVERY-001 v0.1; FRAMEWORK-EXERCISE-001 v0.2; FRAMEWORK-002 v1.4; DECISION-LOG-001 v2.7.

### Prior finding verification

| Finding | Rerun state | Evidence |
| --- | --- | --- |
| FRAMEWORK-ADV-004/FINDING-001 | verified-resolved | FRAMEWORK-EXERCISE-001 v0.2 allows work in a separate local app repository without a GitHub remote, and says that if even a local app repository cannot be created, exploration is ephemeral and not canonical product documentation. WORKFLOW-DISCOVERY-001 Pass B requires canonical app paths before product artifacts are created. These rules now agree. |
| FRAMEWORK-ADV-004/FINDING-002 | verified-resolved | GATE-CATALOG-001 v0.4 G-CX pass condition covers every finding, and procedure step 5 says any unresolved, unaccepted finding leaves the gate failed or blocked. DECISION-017 keeps the reusable core provider-neutral and assigns each app its evaluator. WORKFLOW-LIFECYCLE-001 preserves that split. |
| FRAMEWORK-ADV-004/FINDING-003 | verified-resolved | The source now has one contiguous table under the gate-contract header, containing G-INTENT, G-SETUP, G-REQ, G-FEAS, G-COVERAGE, G-CX, G-ARCH, G-IMPL, G-RELEASE, and G-OPERATE in that order. The tool-neutral critique procedure starts after the final row. A focused source-structure check confirmed all ten rows are in the table. |

- **New findings:** None. The tabletop remains explicitly limited: it is not a fresh-repository pilot or an empirical owner walkthrough, and it does not establish external GitHub access, Impeccable execution, or real application behavior. Those are declared limitations and remain future evidence, not defects in the reviewed lifecycle contract.
- **Exact checks run:**
  - `python3 scripts/artifacts.py validate` — **PASS**, `Validated 32 artifact(s).`
  - Focused gate-table source-structure check — **PASS**; verified the table header, all ten expected gate IDs in order and contiguous rows, and the procedure heading after the table.
  - Focused relative-Markdown-link resolution across the seven scoped artifacts — **PASS**, 47 local links checked, zero broken.
  - Manual cross-artifact review of findings 001/002, setup boundary, G-CX policy, DECISION-017, lifecycle next-action and bounded-loop rules, and exercise limitations — **PASS**, no new substantive finding.
  - `git diff --check` before recording this rerun — **PASS**, no whitespace errors.
- **Verification limits:** This is an artifact-level independent review, not an external-owner usability test, clean-room application-repository pilot, live GitHub permission check, Impeccable execution, or rendered Markdown screenshot test. The Markdown table result is established from source structure.
- **Post-record integrity checks:** `python3 scripts/artifacts.py validate` — **PASS**, 32 artifacts; focused record-integrity assertions — **PASS** (historical first rerun retained, all three findings marked verified-resolved in rerun 2, latest result present); trailing-whitespace scan of this review record — **PASS**. `git diff --check` also passed for tracked changes; this review record is untracked, so the dedicated whitespace scan was used for it.

## Latest gate result

- **Result:** **PASS** for the scoped FW-TASK-002 lifecycle and gate-contract review.
- **Basis:** All three prior Major findings are verified resolved; the complete table is structurally correct; the cross-artifact setup and critique policies are coherent; and the scoped link and artifact-integrity checks passed. No owner decision or residual-risk acceptance was used.
- **Approval:** Independent review gate passed. The framework owner retains authority over FW-TASK-002 completion and any broader lifecycle evidence claims.
- **Remaining evidence boundary:** This pass does not claim empirical owner usability, fresh-app initialization, or a production-lifecycle pilot; the exercise itself identifies those as future evidence.

## References

- [FRAMEWORK-SPEC-001](../framework/FRAMEWORK-SPEC-001.md)
- [GATE-CATALOG-001](../framework/GATE-CATALOG-001.md)
- [WORKFLOW-LIFECYCLE-001](../../workflows/lifecycle.md) and [WORKFLOW-DISCOVERY-001](../../workflows/product-discovery.md)
- [FRAMEWORK-EXERCISE-001](../framework/FRAMEWORK-EXERCISE-001.md)
- [FRAMEWORK-002](../constitution/FRAMEWORK-002.md) and [DECISION-LOG-001](../decisions/DECISION-LOG-001.md) (DECISION-017)
