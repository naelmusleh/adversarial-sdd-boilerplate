---
id: WORKFLOW-AI-ENGINEERING-001
type: workflow
title: Execute one approved application backlog item
status: draft
version: 0.1
created: 2026-10-07
updated: 2026-10-07
related-artifacts: CAP-003, FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001
---

# AI engineering execution workflow

## Purpose

Guide an AI implementation agent through exactly one approved task in an application's own repository. This workflow turns an existing backlog item into a reviewable code change and evidence record. It does not authorize deployment or silently make product decisions.

## Roles

- **Product owner or delegated decision owner:** resolves product choices, accepts/rejects results and residual risks, and authorizes consequential actions.
- **Lead agent/orchestrator:** identifies the selected task, supplies repository context, coordinates specialist review if needed, and reports current lifecycle status.
- **Implementation agent:** inspects, changes, verifies, reviews, and records the selected task within its agreed boundary.
- **Independent reviewer:** reviews the resulting diff or required quality gate when the application process requires a separate reviewer. The implementer must not represent its own work as an independent review.

## Required inputs

Record or link these before editing:

- Application repository identity and root.
- Selected backlog task ID and canonical backlog path.
- Accepted project instructions and canonical artifact paths.
- Task status, dependencies, requirement/design/ADR links, and all acceptance criteria.
- Relevant branch/ref and working-tree state, including pre-existing user changes.
- Project-prescribed verification and review commands, available tools, and any access limits.
- Any owner decisions that constrain the implementation.

If any required input is absent, do not infer it from a similarly named task or from framework examples. Identify the missing input in the blocked report.

## Procedure

### 1. Confirm the target and task

1. Resolve the application repository root and read its `AGENTS.md` or equivalent instructions before substantive work.
2. Find the application's canonical specification, design/CX contract when relevant, architecture decisions, and backlog. Follow the project's artifact map; do not impose a framework file layout if the app has an approved one.
3. Find exactly one task matching the explicit task ID. Confirm its status is eligible for implementation under that repository's documented status model, its dependencies are complete, and it links to controlling approved requirements.
4. If task eligibility or scope cannot be established, stop before editing and report the evidence and owner action needed.

### 2. Establish a safe change boundary

1. Inspect the current branch/ref, working-tree changes, relevant files, and repository verification guidance.
2. Preserve pre-existing changes. Never reset, clean, overwrite, stage, or commit user work as a convenience.
3. Determine whether the repository expects an isolated branch or another review mechanism. Follow its instructions; do not invent a branch naming rule or create a remote branch unless the task and available authorization support it.
4. Confirm whether standing or task-specific authorization covers pushing to the configured remote. Do not ask again when a valid standing authorization already covers this repository and branch; do not push when authorization is absent.
5. List the selected task's acceptance criteria and their source links. For each, identify the intended code/configuration/documentation change and the check or observation that can demonstrate it.

### 3. Resolve readiness before coding

Proceed only if the task has enough information to implement without making a material owner decision. Stop and route a decision when:

- Approved requirements conflict or leave product behavior materially ambiguous.
- A security, privacy, legal, data-use, architecture, or platform choice changes scope or user-visible behavior and lacks an approved decision.
- A dependency is unmet or a separate task must be completed first.
- Required service credentials, permissions, unavailable tools, or a safe test environment are missing.
- A criterion has no feasible way to verify and the project owner has not accepted the limitation.

When stopping, offer evidence-based options, impacts, the recommended resolution where useful, and the artifact/task that decision affects. Do not choose for the owner. Continue only with independent work that does not prejudge the decision, and label it as partial.

### 4. Implement only the selected item

1. Inspect relevant code and local patterns; prefer the smallest coherent change that meets the accepted criteria.
2. Preserve compatibility and behavior outside the task's stated scope. Avoid unrelated refactors, dependency upgrades, formatting churn, new providers, or speculative abstractions.
3. Add or update source, configuration, documentation, and task-level checks only when needed for this item's acceptance criteria and consistent with project conventions.
4. Apply the application's security, privacy, accessibility, reliability, and platform requirements where relevant; record any risk that cannot be addressed within the task.
5. Do not add secrets to source, logs, shell output, or artifacts. Do not use production data for local verification unless the project's approved procedure explicitly permits it.
6. If implementation reveals that another task or scope change is required, stop that expansion and report the dependency. Do not implement the additional task under the selected ID.

### 5. Verify and review

1. Run the narrowest relevant checks first, then the project's required broader checks for the changed area, when available and safe.
2. Use the app's prescribed checks; do not assume a particular language, database, test runner, CI system, or design tool.
3. Record the exact check or manual procedure, observed result, and scope. If not run, state why (for example, unavailable tooling, missing credentials, unsafe environment, or time/access constraint).
4. Inspect the full diff for acceptance coverage, unintended files, secrets, generated artifacts, repository instruction compliance, and unrelated changes.
5. Request or perform the required independent code/quality review. Resolve findings within this task's scope; if they require a new task or owner decision, report and stop that portion.
6. A failed check leaves the task incomplete. Make a focused correction and rerun the relevant failed check when safe. If it still fails, stop and provide the failure evidence and next action; do not loop indefinitely or waive the gate yourself.

### 5A. Preserve completed work in Git

After the selected change reaches a coherent, reviewed checkpoint and applicable checks have run:

1. Inspect `git status` and the complete diff. Stage only explicit in-scope paths; inspect the staged diff and confirm it contains no unrelated, generated, secret, or user-owned changes.
2. Create a descriptive, atomic commit for the completed change. Do not bundle unrelated tasks merely to reduce commit count. If a required check fails, do not claim completion; a failing feature-branch commit may be pushed only when the owner has authorized publication and it is clearly reported as unready for merge.
3. When push authorization exists, push the commit to the task's authorized feature branch/remote and verify the resulting remote ref. Respect required pull requests and branch protections. Never force-push, bypass required checks, merge, or deploy under this protocol.
4. If no authorization, remote, or usable credentials exist, preserve the local changes, report the specific blocker, and do not claim that the change has been published. Do not expose credentials while diagnosing access.
5. After a commit is published, correct it with a new commit; do not amend, rebase, or force-push shared history unless a separate explicit authorization and repository procedure allow it.
6. Record the commit SHA, branch/ref, push result, check results, and review state in the task milestone and final report.

### 6. Record the milestone

Update only the selected task in its canonical backlog after implementation and evidence review:

- Mark complete only when every acceptance criterion has supporting evidence and the repository's completion conditions are met.
- Otherwise retain the appropriate in-progress, blocked, or review status defined by the app.
- Record a concise milestone with changed files or review link, checks run and results, checks not run and reasons, unresolved findings/risks, and any owner decision needed.
- Do not update neighboring backlog items or duplicate the milestone in an independently maintained status registry.

If editing the backlog itself is unsafe or disallowed, leave its status unchanged and report the exact proposed milestone text for the authorized project maintainer to apply.

### 7. Report outcome and next action

Provide a user-facing summary with:

- Selected task ID and outcome: completed, partially completed, or blocked.
- Changed files and how they satisfy the acceptance criteria.
- Verification commands/procedures actually run and observed results.
- Required checks not run and reasons.
- Review status and unresolved risks/findings.
- Backlog status/milestone change, or why it was not changed.
- Next action and its owner; explicitly name any required product-owner decision or authorization.

Do not claim the app is production-ready from a task-level implementation result. Release, deployment, security, CX, and operations gates remain separate unless the selected task explicitly includes their evidence and the relevant workflow authorizes it.

## Explicitly outside this workflow

- Selecting or changing product scope, user-visible behavior, provider policy, or acceptance criteria.
- Implementing more than the selected backlog item.
- Merging, releasing, deploying, publishing, purchasing, contacting external parties, deleting production data, or changing permissions without the applicable authorization.
- Declaring an independent review, quality gate, or production readiness based only on the implementer's own assertion.

## Completion conditions

This workflow run is complete when either:

1. The selected item has a reviewable change, criterion-linked observed verification, a truthful milestone record, and a user report; or
2. Work is stopped with the selected task left accurately incomplete, a durable blocker/milestone when safe, cited evidence, and a clear owner or agent next action.

No additional polish or adjacent task is implied by either outcome.
