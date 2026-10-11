---
id: FRAMEWORK-ADV-007
type: adversarial-review
title: Independent review of lean and full app starter profiles
status: approved
version: 0.1
created: 2026-10-10
updated: 2026-10-10
reviewed-artifact: CAP-004
reviewed-version: 0.4
related-artifacts: FRAMEWORK-ADV-006, FRAMEWORK-BACKLOG-001, FRAMEWORK-SPEC-001
---

# FRAMEWORK-ADV-007 — App starter profile review

## Review request

- **Gate / lifecycle transition:** CAP-004 starter-profile safety and usability review.
- **Review scope:** The default nine-file starter, the optional 20-file lifecycle scaffold, profile-specific artifact IDs, generated README guidance, template-source portability, and regression evidence for initialization safety.
- **Questions to answer:** Does the lean default preserve the canonical SDD entry point without implying that later gates ran? Is the full scaffold available when desired? Do output claims and example IDs match each profile?
- **Approval authority:** Framework owner.
- **Evidence cutoff:** 2026-10-10, America/New_York.
- **Source revision:** Uncommitted working tree. SHA-256 of `scripts/init_app_project.py`: `45bfe373da8b3d2a2abd9a0071c88bc79929d72d5f347aaafc502aa84ac6cd44`; SHA-256 of `docs/templates/app-project/README.md`: `86e35f0509a1284483efcd36b6491264534ce1db22d4f92677d10f3440d662a4`.

## Review method

- **Critic:** Independent review agent `/root/starter_review`.
- **Reviewer mode:** `independent`.
- **Independence explanation:** The reviewer inspected the starter implementation, generated-document logic, templates, and tests without editing the reviewed files; it first reported findings and then rechecked the fixes.
- **Reviser:** `/root`.
- **Verifier:** The independent reviewer rechecked the two reported changes; `/root` ran the expanded five-test suite and repository artifact validation afterward.
- **Sources inspected:** CAP-004 v0.4, `scripts/init_app_project.py`, `docs/templates/app-project/README.md`, and `tests/test_init_app_project.py`.
- **Limits:** The reviewer did not exercise invalid input combinations, symlink targets, every partial-write failure, GitHub operations, or app implementation. These limits do not invalidate the bounded starter-profile review.

## Finding register

### FRAMEWORK-ADV-007/FINDING-001 — Decision ID example skipped the first ID in the lean profile

- **Severity:** Major
- **Target location:** Generated README example in `scripts/init_app_project.py`.
- **Evidence:** The lean profile has no preseeded decision artifact, while the optional full profile seeds `DECISION-001`. A single hard-coded `DECISION-002` example therefore skipped the first available ID for default users.
- **Inference:** This could teach new projects to start with a gap in their stable decision sequence.
- **Impact / failure mode:** Users may create inconsistent artifact numbering or assume an unrecorded decision exists.
- **Recommendation / options:** Make the example depend on the selected profile or direct users to choose the next unused ID.
- **Owner decision required:** No; this is a documentation consistency defect.
- **Initial disposition:** unresolved.
- **Final disposition:** **Verified resolved.** The generated README now emits `DECISION-001` for the lean default and `DECISION-002` for the optional preseeded profile. Regression assertions cover both outputs.

### FRAMEWORK-ADV-007/FINDING-002 — Supporting-record section mislabeled canonical SDD files

- **Severity:** Minor
- **Target location:** Supporting-record section in the generated README.
- **Evidence:** The section listed the five canonical SDD files as a bullet immediately under a heading about supporting records.
- **Inference:** Readers could mistake required project documents for optional supporting records.
- **Impact / failure mode:** A new user may not understand which files are the core project contract and which records are added later.
- **Recommendation / options:** Remove the unrelated list or explain the distinction in the section.
- **Owner decision required:** No; this is a documentation clarity issue.
- **Initial disposition:** unresolved.
- **Final disposition:** **Verified resolved.** The generated README now has a dedicated supporting-record heading and explains when those records are created; the canonical files remain described in the app-project guide.

## Rerun and verification

- **Rerun date:** 2026-10-10.
- **Verifier and reviewer mode:** Independent review agent rechecked both fixes; local regression checks were then expanded and run by `/root`.
- **Scope:** Original profile-selection and README-accuracy findings.
- **Target revision:** CAP-004 v0.4 in the uncommitted working tree.
- **Prior finding checks:**

| Finding | Rerun state | Evidence confirming resolution or explaining remaining risk |
| --- | --- | --- |
| FRAMEWORK-ADV-007/FINDING-001 | verified-resolved | Profile-aware output inspected; tests assert `EXAMPLE-DECISION-001` for default and `EXAMPLE-DECISION-002` for the optional scaffold. |
| FRAMEWORK-ADV-007/FINDING-002 | verified-resolved | Generated supporting-record section no longer lists canonical files as supporting records. |

- **New findings:** None in the bounded rerun scope.
- **Verification limits:** The final local run passed five starter tests. It does not establish all CAP-004 acceptance criteria or app/release readiness.

## Final gate result

- **Result:** **PASS** for the bounded starter-profile review.
- **Why this result follows the criteria:** Both findings were verified resolved; the independent reviewer approved the lean/default split and optional scaffold within the stated scope. The default generates nine files and five canonical artifacts; the optional profile generates 20 files and 16 draft artifacts. Neither profile claims that a gate has passed.
- **Approval:** No owner residual-risk approval used for this review.
- **Next action / owner:** Continue remaining CAP-004 evidence and the framework v1 backlog. This review does not by itself mark FW-TASK-008 complete.

## References

- [CAP-004 — App Repository Bootstrap](../../framework/capabilities/CAP-004-app-repository-bootstrap.md)
- [FW-TASK-008 and framework status](../framework/FRAMEWORK-BACKLOG-001.md)
- [FRAMEWORK-ADV-006 — Prior portability and artifact-safety review](FRAMEWORK-ADV-006.md)
