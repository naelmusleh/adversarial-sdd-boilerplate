---
id: FRAMEWORK-EXERCISE-002
type: workflow-exercise
title: Commit and push policy tabletop for scoped SDD changes
status: active
version: 0.1
created: 2026-10-20
updated: 2026-10-20
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, WORKFLOW-AI-ENGINEERING-001
---

# FRAMEWORK-EXERCISE-002 — Commit and push policy tabletop

## Purpose and boundary

Exercise the decision rules in FW-TASK-016 and `workflows/ai-engineering-execution.md` for preserving verified work in Git. This is a **paper tabletop**: no repository was staged, committed, pushed, merged, deployed, or modified for these scenarios. It tests whether the written procedure leads to a safe and truthful action; it does not prove Git commands, credentials, remotes, CI, or branch protection work in a live repository.

## Scope and frozen inputs

- **Framework revision used:** `3119388398d7639b1e21801a5b48c92d36f531d7` (feature-branch checkpoint before this exercise record was added).
- **Procedure under test:** `WORKFLOW-AI-ENGINEERING-001`, section “Preserve completed work in Git”; `AGENTS.md`, implementation and evidence rules; FW-TASK-016 acceptance criteria.
- **Scenario scope:** verified task checkpoint, unrelated dirty files, failed required check, absent push authorization, unavailable remote/credentials, branch protection requiring a pull request, and correction after publication.
- **Out of scope:** actual Git command execution, live remote access, GitHub settings inspection, pull-request creation, merges, release/deployment, credential handling in a real environment, and production data.
- **Exercise facilitator:** Framework implementation agent.
- **Reviewer:** Pending separate review with FRAMEWORK-ADV-008 rerun.

## Decision rule applied in each scenario

1. Identify the selected task and inspect repository state and the full diff.
2. Stage only explicit in-scope paths; inspect the staged diff and preserve unrelated/user-owned changes.
3. Run applicable checks and required review. A failing or unreviewed checkpoint is not complete or merge-ready.
4. Commit a coherent reviewed change with a scoped message; record the exact SHA.
5. Push only to an authorized feature branch/remote when standing or task-specific authorization exists. Verify the remote ref. Respect PR and branch-protection requirements; never force-push, bypass, merge, or deploy under this procedure.
6. If publication cannot happen, record the specific blocker and do not report the change as pushed.
7. Correct a published change with a follow-up commit; do not rewrite shared history.

## Scenario results

| ID | Scenario input | Expected safe decision | Tabletop result |
| --- | --- | --- | --- |
| EX-001 | A selected task is reviewed, required checks pass, the staged diff contains only task files, and the owner has authorized the feature-branch push. | Commit the scoped change, push to the authorized feature branch, verify the remote ref, and record commit/ref/check/review evidence. Do not merge or deploy. | **PASS (paper):** the procedure yields an atomic, reviewable published checkpoint and makes no merge/deployment claim. |
| EX-002 | Required task files are changed alongside an unrelated user edit and an unrelated untracked file. | Stage only explicit task paths; inspect staged and unstaged diffs; leave unrelated changes untouched and out of the commit. | **PASS (paper):** unrelated edits stay outside the task commit; if they prevent a trustworthy diff review, stop and report that blocker. |
| EX-003 | A required check fails or is unavailable at the checkpoint. | Keep the task incomplete. A failing feature-branch commit may be pushed only if authorized and clearly marked unready; it cannot satisfy the gate or be merged. An unavailable check is unverified, not passed. | **PASS (paper):** failure/unavailability remains visible and does not advance the task or release state. |
| EX-004 | Checks pass, but no standing or task-specific authorization to push exists. | Do not push. Preserve the verified local commit/work and report authorization as a publication blocker; do not infer permission from a configured remote. | **PASS (paper):** no external write is attempted or claimed. The local-only state is explicitly not considered published. |
| EX-005 | Push is authorized, but the remote is unavailable or credentials are missing/expired. | Do not expose secrets, place tokens in a remote URL, or retry through an unapproved channel. Report the concrete connectivity/credential blocker and leave push status unverified/failed. | **PASS (paper):** the agent does not claim publication; it can continue only with safe local work and the repository's authorization policy. |
| EX-006 | Repository policy requires a PR and protected-branch checks after feature-branch publication. | Push only the authorized feature branch. Follow the PR/review process; do not push directly to protected `main`, bypass a required check, or treat a successful workflow file/run as proof the setting is enforced. | **PASS (paper):** branch protection is respected and remains unverified until hosting settings are inspected. |
| EX-007 | A defect is found after the commit was pushed. | Make a corrective follow-up commit, run relevant checks, push the authorized branch, and link both revisions. Do not amend/rebase/force-push shared history under this policy. | **PASS (paper):** history and review evidence remain attributable; prior failed evidence is not silently rewritten. |

## Findings and limits

- All seven scenarios produce a safe action under the written procedure without requiring the agent to invent authorization or claim an unobserved push.
- The exercise does not validate shell behavior, Git staging boundaries in a live dirty worktree, actual remote credentials, CI event delivery, pull-request status, or repository protection settings.
- A real run must still capture the exact commit SHA, remote/ref result, CI run identity, and required settings observation. If those cannot be observed, record the corresponding evidence as unavailable or unverified.
- This paper exercise is evidence for policy clarity only; it is not an independent review, automated test, hosted CI result, G-RELEASE pass, or production-readiness claim.

## Result

- **Tabletop result:** PASS for bounded policy consistency.
- **FW-TASK-016 status:** Remains incomplete pending independent review/rerun and its other acceptance evidence. This exercise does not close G-IMPL by itself.
- **Next action:** Resolve FRAMEWORK-ADV-008 findings, request a full-scope independent rerun, and keep live remote/branch-protection evidence explicitly separate.

## References

- [FW-TASK-016](FRAMEWORK-BACKLOG-001.md#fw-task-016--commit-and-publish-scoped-implementation-changes)
- [AI engineering execution workflow](../../workflows/ai-engineering-execution.md)
- [Framework specification FR-FW-015](FRAMEWORK-SPEC-001.md#functional-requirements)
- [FRAMEWORK-ADV-008](../adversarial-reviews/FRAMEWORK-ADV-008.md)
