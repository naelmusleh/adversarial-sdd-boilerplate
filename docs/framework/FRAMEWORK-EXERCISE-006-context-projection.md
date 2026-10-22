---
id: FRAMEWORK-EXERCISE-006
type: framework-exercise
title: Context projection integrity and bounded reduction
status: draft
version: 0.1
created: 2026-10-21
updated: 2026-10-21
related-artifacts: FRAMEWORK-BACKLOG-001, FRAMEWORK-SPEC-001, DECISION-LOG-001, DECISION-022
---

# FRAMEWORK-EXERCISE-006 — Context projection integrity and bounded reduction

## Boundary

This is a deterministic synthetic fixture exercise, not a measurement of model tokens, task success, production workload, or security isolation. It does not establish that a human or agent reviewer finds no missed contract. No sandbox is configured or tested; generated directories are context-minimization copies only.

## Fixture and observations

`tests/test_context_projection.py` creates a temporary Git repository with required contract markers (`FW-027-AC-01`, `-02`, `-03`, `-05`, and `-06`), role-specific context, a large unrelated file, explicitly excluded private fixture data, and an untracked `.env`. For each of ten lifecycle gates and two roles, it creates a projection and verifies that required markers and role context are present, unrelated/private/secret material is absent, path and digest entries are recorded, and the reported tracked-byte reduction is positive. The generator labels the byte measure as a proxy, not a tokenizer count or quality measure.

Negative cases cover missing policy/required input, unsafe relative paths, symlink escape, selected/excluded conflicts, source-tree output, concurrent unique creation, cleanup ownership, and interrupted staging recovery. Hashes taken over canonical fixture files before and after generation/cleanup must match.

## Limits and follow-up

The exercise covers structural retention of explicit fixture markers, not semantic acceptance-criteria review or increased missed-contract rates across representative real tasks. Those require a separately bounded reviewer study. Acceptance criterion 4 in FW-TASK-027 (host/runtime denial testing) is outside DECISION-022's approved scope; no access-isolation claim is made. A future sandbox or representative-review study requires a separately approved task/scope.

Reproduce the focused cases with `python3 -m unittest discover -s tests -p 'test_context_projection.py' -v`. The output manifest records source revision/worktree state, policy and generator digests, profile/contract revisions, paths, file digests, and the byte-size proxy.
