---
id: FRAMEWORK-ADV-002
type: adversarial-review
title: Independent review of CAP-002 status and gate-state conformance
status: approved
version: 0.2
created: 2026-10-08
updated: 2026-10-08
reviewed-artifact: WORKFLOW-ADV-001
reviewed-version: 0.2
related-artifacts: CAP-002, FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-ADV-001, FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001
---

# FRAMEWORK-ADV-002 — Independent CAP-002 conformance review

## Review request

- **Gate / lifecycle transition:** Determine whether CAP-002 and its workflow, template, and exercise record conform to the framework's artifact status rules and whether the evidence supports advancing FW-TASK-003.
- **Review scope:** Stable artifact identity/version; lifecycle status vs gate-result separation; CAP-002 active-capability scope; workflow procedure for inconclusive results; validator behavior; local links; and consistency with FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-SPEC-001, and FRAMEWORK-BACKLOG-001.
- **Explicit exclusions:** Review of unrelated application/CX materials, automated enforcement beyond the validator behavior inspected, and external factual claims.
- **Questions to answer:** Were the previous status-vocabulary findings corrected, and does any remaining instruction still conflate artifact lifecycle status with gate result?
- **Approval authority:** Framework owner under FRAMEWORK-001; this record is an independent review result, not owner authorization to accept residual risk.
- **Evidence cutoff:** 2026-10-08, America/New_York.
- **Source revision:** Base commit `0d85b6105cda0e58d9faf7bf336ade3143182c71`; reviewed working-tree versions are uncommitted. SHA-256 fingerprints at review time: WORKFLOW-ADV-001 v0.2 `301257463d0b650e790eb12a05383e50b610fcac1397689ae988802f7b04bc1c`; review template v0.2 `50e23c8d3f2217804a1ae7ce53b26bb49dbced2e8ed1f028b35a690e8f6c5e60`; CAP-002 v0.2 `22aefebf6fc46c16c638623f9e424907dcf30b6f2653e6683232867e7533ea3f`; FRAMEWORK-ADV-001 `78c0a5300510720b1684f55e9c55834901977629d12442b186ad8bac95c90175`; `scripts/artifacts.py` `499d40f6b71b4d87d6300e7a0fa9ffeeba8b33b672edc33cda762ec6f5481b34`.

## Review method

- **Critic / verifier:** Independent reviewer agent, separate from the authoring agent that made the fixes and from the prior self-review context.
- **Reviewer mode:** `independent` for this review of the current files; the earlier FRAMEWORK-ADV-001 exercise remains a `self-review` and is not upgraded.
- **Reviser:** The authoring agent that updated the workflow, template, exercise metadata, specification, backlog, and artifact CLI.
- **Sources inspected:** WORKFLOW-ADV-001 v0.2; CAP-002 v0.2; review template v0.2; FRAMEWORK-ADV-001; FRAMEWORK-001 and FRAMEWORK-002; FRAMEWORK-SPEC-001; FW-TASK-003 in FRAMEWORK-BACKLOG-001; `scripts/artifacts.py` and its observed output.
- **Limits:** The current target files and this new review are uncommitted. Hashes identify the inspected bytes, but repository history will preserve them only when the owner commits the working-tree changes. No production or external-system behavior was in scope.

## Initial finding and disposition

### FRAMEWORK-ADV-002/FINDING-001 — Review-result labels were used as artifact lifecycle statuses

- **Severity:** Major
- **Initial evidence (previous independent review):** The reusable review template used `status: ready`, and FRAMEWORK-ADV-001 used `status: inconclusive`, while FRAMEWORK-002's lifecycle vocabulary permits `draft`, `in-review`, `revision-required`, `approved`, `active`, `blocked`, `superseded`, and `retired`. The workflow also has a separate final gate-result field.
- **Impact:** Copied review artifacts could use invalid lifecycle states and conflate the review record's lifecycle with its PASS/FAIL/INCONCLUSIVE outcome.
- **Owner decision required:** No. The valid lifecycle states are defined in FRAMEWORK-002.
- **Disposition:** `resolved` for the metadata issue. The template now uses `status: draft`; FRAMEWORK-ADV-001 now uses `status: in-review` while its separate gate result remains `INCONCLUSIVE`. The artifact CLI now validates lifecycle status values.
- **Rerun evidence:** The updated template and exercise metadata use allowed lifecycle statuses; `python3 scripts/artifacts.py validate` passes and scans the workflow artifact set.
- **Limitation:** Full-scope rerun found a separate remaining instruction with the same semantic risk; see FINDING-002. This disposition resolves only the original metadata instances, not the new workflow instruction.

## Full-scope rerun and new finding

The rerun rechecked the original scope across the full current workflow, template, CAP-002, FRAMEWORK-ADV-001, status policy, and validator behavior. The metadata edits resolved FINDING-001, but the workflow still instructs reviewers to use a gate outcome as an artifact status.

### FRAMEWORK-ADV-002/FINDING-002 — Workflow still tells reviewers to mark the artifact `inconclusive`

- **Severity:** Major
- **Target location:** [WORKFLOW-ADV-001](../../workflows/adversarial-review.md), “Bound remediation and stop conditions,” final paragraph.
- **Evidence:** The workflow says: “The review artifact remains `revision-required` or `blocked` until the gate passes or is explicitly marked `inconclusive`.” `inconclusive` is a gate result defined separately in §6, not a permitted artifact lifecycle status under FRAMEWORK-002. The new validator rejects an artifact front matter status outside that lifecycle vocabulary, but it cannot detect this prose instruction.
- **Inference:** A reviewer following the workflow literally could set `status: inconclusive`, recreating the invalid state that the template and FRAMEWORK-ADV-001 metadata were just corrected to avoid.
- **Impact / failure mode:** The generic workflow can still generate an invalid review artifact and contradict the framework's distinction between lifecycle status and gate result.
- **Recommendation:** Keep the review artifact lifecycle status `revision-required` or `blocked` as appropriate, and record `INCONCLUSIVE` only in the final gate-result field. Clarify that distinction in the workflow sentence.
- **Owner decision required:** No; FRAMEWORK-002 determines the lifecycle status vocabulary.
- **Initial disposition:** `unresolved`.

## Rerun evidence

- **Rerun date:** 2026-10-08.
- **Verifier / independence:** Independent reviewer agent; no authoring or revision overlap.
- **Scope:** Full original scope: workflow identity and instructions, template metadata and result field, CAP-002 status/claim, prior exercise status/result, status vocabulary, validator scan/output, and relative Markdown links.
- **Prior finding:** FRAMEWORK-ADV-002/FINDING-001 — `verified-resolved` for the template and exercise metadata, based on current file contents and validator pass. Finding 002 remains unresolved, so the package does not pass.
- **New findings:** FRAMEWORK-ADV-002/FINDING-002, described above.
- **Exact checks run:**
  - `python3 scripts/artifacts.py validate` — **PASS**, `Validated 27 artifact(s).`
  - `python3 scripts/artifacts.py list` — **PASS**, listed `WORKFLOW-ADV-001` with status `active` at `workflows/adversarial-review.md`; listed `FRAMEWORK-ADV-001` with lifecycle status `in-review`.
  - Focused inline Python Markdown-link check over `framework/capabilities/CAP-002-adversarial-review.md`, `workflows/adversarial-review.md`, `docs/templates/adversarial-review.md`, and `docs/adversarial-reviews/FRAMEWORK-ADV-001.md` — **PASS**, 25 local links checked, none broken.
  - `git diff --check -- workflows/adversarial-review.md framework/capabilities/CAP-002-adversarial-review.md docs/templates/adversarial-review.md docs/adversarial-reviews/FRAMEWORK-ADV-001.md docs/framework/FRAMEWORK-SPEC-001.md docs/framework/FRAMEWORK-BACKLOG-001.md scripts/artifacts.py` — reported trailing spaces on four workflow metadata lines. These are intentional Markdown hard-break markers and do not affect gate behavior.
- **Post-record integrity checks:** After creating this review artifact, `python3 scripts/artifacts.py validate` — **PASS**, `Validated 29 artifact(s).`; an expanded inline Python local-link check across the four files above plus this review record — **PASS**, 34 links checked, none broken.
- **Verification limits:** Artifact validation checks metadata/status syntax and IDs, not the semantic meaning of workflow prose. The inline link check confirms local link targets exist; it does not validate headings or remote URLs.

## Final gate result

- **Result:** **FAIL — revision required**.
- **Why this result follows the criteria:** The original metadata status instances are corrected, and the current validator, artifact listing, and local-link checks passed. However, a major instruction in the workflow still says to set an invalid lifecycle status for an INCONCLUSIVE gate result. Under the workflow's PASS rule, this material finding must be resolved and rerun before the gate can pass. The current self-review remains inconclusive and is not independently upgraded by this review.
- **Approval:** Not granted. No residual risk accepted.
- **Next action / owner:** The workflow author should clarify the lifecycle status versus gate-result instruction, increment WORKFLOW-ADV-001's version, and request a focused full-scope rerun. No product-owner decision is needed.

## References

- [CAP-002 — Adversarial Review Workflow](../../framework/capabilities/CAP-002-adversarial-review.md)
- [WORKFLOW-ADV-001 — Adversarial Review Workflow](../../workflows/adversarial-review.md)
- [Reusable adversarial review template](../templates/adversarial-review.md)
- [FRAMEWORK-ADV-001 — Prior self-review exercise](FRAMEWORK-ADV-001.md)
- [FRAMEWORK-001](../constitution/FRAMEWORK-001.md) and [FRAMEWORK-002](../constitution/FRAMEWORK-002.md)
- [FRAMEWORK-SPEC-001](../framework/FRAMEWORK-SPEC-001.md) and [FRAMEWORK-BACKLOG-001](../framework/FRAMEWORK-BACKLOG-001.md)

## Follow-up review — 2026-10-08

### Review request and scope

Recheck the CAP-002 bundle after WORKFLOW-ADV-001 v0.3, CAP-002 v0.3, and review-template v0.3 clarified that lifecycle status and gate result are distinct. The rerun covered the full prior status/gate scope: artifact identity and versions; lifecycle-status wording in all relevant workflow and template instructions; template/exercise front matter; CAP-002 scope and claim; FRAMEWORK-002's status vocabulary; validator enforcement; cross-artifact status consistency; and local links. No authoring or revision work was performed by this reviewer.

### Finding dispositions and rerun evidence

| Finding | Disposition | Rerun state | Evidence |
| --- | --- | --- | --- |
| FRAMEWORK-ADV-002/FINDING-001 — gate-result labels used as artifact lifecycle statuses | `resolved` | `verified-resolved` | The template front matter now uses `status: draft`; FRAMEWORK-ADV-001 uses `status: in-review` while its body retains `INCONCLUSIVE` as the gate result. CAP-002 v0.3, workflow v0.3, and template v0.3 explicitly separate these concepts. The validator accepts the lifecycle values and rejects other values. |
| FRAMEWORK-ADV-002/FINDING-002 — workflow told reviewers to mark an artifact `inconclusive` | `resolved` | `verified-resolved` | WORKFLOW-ADV-001 v0.3 §7 now says to keep the artifact lifecycle status within FRAMEWORK-002's vocabulary and record PASS/FAIL/INCONCLUSIVE/NOT A GATE only in the separate gate-result field. The template repeats that distinction and states that an INCONCLUSIVE result blocks progression. A full text scan of the workflow, template, CAP-002, FRAMEWORK-ADV-001, FRAMEWORK-ADV-002, FRAMEWORK-002, and validator instructions found no remaining instruction to use `inconclusive` as an artifact status. Other uses refer to gate outcomes or finding evidence, not front matter status. |

No new findings were identified in the rerun scope. CAP-002 remains an active manual capability; the earlier FRAMEWORK-ADV-001 self-review remains INCONCLUSIVE and is not retroactively changed. This independent review supplies the separate conformance review evidence for the current v0.3 package.

### Exact verification performed

- `python3 scripts/artifacts.py validate` — **PASS**, `Validated 29 artifact(s).` This validates required metadata, ID uniqueness/format, and lifecycle status values across the scanned artifact roots.
- `python3 scripts/artifacts.py list` — **PASS**; it lists CAP-002 as `active`, WORKFLOW-ADV-001 as `active`, FRAMEWORK-ADV-001 as `in-review`, and this review as `in-review` before this follow-up was recorded.
- Focused inline Python check resolving relative Markdown link targets in CAP-002, WORKFLOW-ADV-001, its template, FRAMEWORK-ADV-001, and FRAMEWORK-ADV-002 — **PASS**, 34 local links checked, none broken.
- Focused text search of the full review workflow, template, capability, prior review, status constitution, and validator for lifecycle-status/gate-result terminology — **PASS** after manual contextual review; the only current instructions assigning INCONCLUSIVE describe gate outcomes, not artifact front matter.
- `git diff --check` for the reviewed bundle — **PASS**, no whitespace errors.
- **Post-follow-up integrity checks:** After appending this section and changing FRAMEWORK-ADV-002's lifecycle status to `approved`, `python3 scripts/artifacts.py validate` — **PASS**, `Validated 29 artifact(s).`; `python3 scripts/artifacts.py list` shows CAP-002 and WORKFLOW-ADV-001 as `active`, FRAMEWORK-ADV-001 as `in-review`, and FRAMEWORK-ADV-002 as `approved`; the expanded local-link check — **PASS**, 34 links across five review-scope files, none broken; the focused lifecycle/gate-result search found no current instruction to use INCONCLUSIVE as a front-matter status; and `git diff --check` produced no output.

**Reviewed v0.3 working-tree fingerprints:** WORKFLOW-ADV-001 `aab9fe9e9cd911bdb18431b84bd45d657a56e1ea631f028cb8eee445bd600a5a`; review template `98015f2c9f8a65f6ced936a68a50a57cf5997700b73bc51c3b1e1491be07fa6b`; CAP-002 `2a0d9783c71fc185204d190ae45aa01dfd5bfd063f270e9df5f0fb893fd54770`; artifact validator `499d40f6b71b4d87d6300e7a0fa9ffeeba8b33b672edc33cda762ec6f5481b34`. The files were uncommitted at review time; fingerprints identify the reviewed content, and Git history will retain it when the current changes are committed.

### Follow-up final gate result

- **Result:** **PASS** for the current CAP-002 v0.3 workflow/template status-conformance scope.
- **Why:** Both prior findings are resolved and verified against the complete relevant instruction set. No blocking or major findings remain; validator and link checks pass. This does not alter FRAMEWORK-ADV-001's separate INCONCLUSIVE result, nor does it claim a production or external-fact review.
- **Approval:** No residual-risk acceptance used. This is an independent conformance review; owner product approval is not required for this framework status clarification.
- **Lifecycle status:** Updated this review artifact to `approved`; the gate result is recorded here, separately from its front-matter status.
- **Next action / owner:** Continue FW-TASK-003 only after preserving these reviewed revisions in the repository's normal Git history. No owner decision is needed.
