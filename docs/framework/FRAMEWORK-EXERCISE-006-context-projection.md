---
id: FRAMEWORK-EXERCISE-006
type: framework-exercise
title: Context projection integrity and bounded reduction
status: draft
version: 0.1
created: 2026-10-21
updated: 2026-10-22
related-artifacts: FRAMEWORK-BACKLOG-001, FRAMEWORK-SPEC-001, DECISION-LOG-001, DECISION-022
---

# FRAMEWORK-EXERCISE-006 — Context projection integrity and bounded reduction

## Boundary

This is a deterministic synthetic fixture exercise plus a separately owner-approved, bounded two-case semantic review (study `FW027-SEMANTIC-CONTEXT-REVIEW-001`, 2026-10-22). Neither part measures tokenizer tokens, causal task success, production workload, or security isolation. The semantic review covers only the named task revisions below. No sandbox is configured or tested; generated directories are context-minimization copies only. Cleanup is designed for owned projections and concurrent framework invocations, not as a defense against a hostile same-user process that can replace directory entries in a writable parent during deletion.

## Fixture and observations

`tests/test_context_projection.py` creates a temporary Git repository with required contract markers (`FW-027-AC-01`, `-02`, `-03`, `-05`, and `-06`), role-specific context, a large unrelated file, explicitly excluded private fixture data, and an untracked `.env`. For each of ten lifecycle gates and two roles, it creates a projection and verifies that required markers and role context are present, unrelated/private/secret material is absent, path and digest entries are recorded, and the reported tracked-byte reduction is positive. The generator labels the byte measure as a proxy, not a tokenizer count or quality measure.

Negative cases cover missing policy/required input, unsafe relative paths, symlink escape, selected/excluded conflicts, source-tree output, concurrent unique creation, cleanup ownership, and interrupted staging recovery. Hashes taken over canonical fixture files before and after generation/cleanup must match.

## Bounded semantic context review (2026-10-22)

The owner approved a read-only comparison of the G-IMPL contexts for FW-TASK-026 and APP-TASK-003. An independent reviewer compared each final projection with its complete context and the task's acceptance criteria. This is a two-case content-coverage review, not a clean implementation replay or a generalization to other tasks.

| Case | Source snapshot | Complete context | Final projection | UTF-8 byte reduction | Independent result |
|---|---|---:|---:|---:|---|
| FW-TASK-026 | `a6e90a65057e87f27b1a7a61b963b09893c3495c`, clean | 148 files / 1,873,210 bytes | 53 files / 1,068,198 bytes | 42.98% | PASS for paired content coverage |
| APP-TASK-003 | `61b196ec126d2bfb46614994fe627830d1b17bce`, dirty worktree snapshot | 49 files / 183,259 bytes | 30 files / 123,618 bytes | 32.54% | PASS for paired content coverage |

The first review round identified material context omissions. The final FW-TASK-026 policy added `.github/workflows/verify-pipeline.yml`, `docs/framework/FRAMEWORK-CI-RELEASE-POLICY-001.md`, `scripts/init_app_project.py`, and `tests/test_init_app_project.py`. The final APP-TASK-003 policy added `delivery/releases/RELEASE-PING-001.md` and `operations/RUNBOOK.md`. The independent second pass found those omissions resolved and no remaining material acceptance-criterion or local dependency gap in either final projection. It noted one unresolved link from the included runbook to excluded `operations/PILOT-OPS-001.md`; the reviewer found its relevant instructions covered by the included specification and release procedure, so did not consider it a material gap.

For FW-TASK-027, acceptance criterion 4 is satisfied through its documented fallback: because no sandbox denial evidence exists, the framework describes projections as context minimization only and makes no access-isolation claim, consistent with FR-FW-024 and DECISION-022. The host/runtime sandbox test was not run. Criterion 5 is satisfied for this bounded exercise: the complete-context baselines cover two task types, and the independent second pass found no material acceptance-criterion or local-dependency omissions in either final projection after the first-round policies were corrected. This result is limited to the two reviewed cases.

The byte counts are UTF-8 size proxies, not tokenizer counts. In the dirty APP-TASK-003 worktree, the generator's tracked-file-only measure undercounts the complete context because untracked files are omitted from that denominator; the percentages above use the same complete-context inventory and projected inventory for both cases. The app case is retrospective and cannot show that the projection caused successful implementation. Hosted GitHub settings are external to the FW-TASK-026 snapshot and are not established by this study. The study does not establish an increased or decreased missed-contract rate, representative-task generalization, or isolation. Temporary projection outputs and full source inventories remain under `/private/tmp/fw027-semantic-study-20261022`; round-2 projection IDs and policy digests are recorded in the study summary there.

## Limits and follow-up

The bounded review supplies evidence for the two named task contexts only; it does not estimate missed-contract rates across a larger task population or establish task-success causality. The sandbox-denial test was not run, and no access-isolation claim is made. Any future sandbox study or isolation claim requires a separately approved task/scope.

Reproduce the focused cases with `python3 -m unittest discover -s tests -p 'test_context_projection.py' -v`. The output manifest records source revision/worktree state, policy and generator digests, profile/contract revisions, paths, file digests, and the byte-size proxy.
