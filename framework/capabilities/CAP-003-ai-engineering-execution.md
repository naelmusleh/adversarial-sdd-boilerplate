---
id: CAP-003
type: framework-capability
title: General AI Engineering Execution
status: draft
version: 0.1
created: 2026-10-07
updated: 2026-10-07
related-artifacts: FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001
---

# CAP-003 — General AI Engineering Execution

## Need

Approved product intent must become a bounded, reviewable application code change without requiring the product owner to perform routine implementation. The process must preserve the application's own repository instructions, source of truth, and release boundaries.

## User

The product owner, lead agent/orchestrator, and implementation agent working in an application repository.

## Problem boundary

CAP-003 defines a reusable agent workflow for implementing exactly one explicitly selected, approved backlog item. It does not define a universal application architecture, language, test stack, CI provider, deployment provider, or domain-specific business rule. Those belong to the application repository's approved artifacts and existing conventions.

This capability is an execution contract, not an orchestration service. It does not itself provide repository access, credentials, or automated approval.

## Inputs

Before implementation begins, the agent must be able to identify and read:

1. The target application repository and its applicable `AGENTS.md`, contributor guidance, and local workflow instructions.
2. The canonical project artifacts defined by that application, including its constitution, specification, design/CX contract when relevant, architecture/ADRs, and backlog.
3. Exactly one backlog item by stable ID, with an approved/ready status, explicit acceptance criteria, dependencies, and links to relevant requirements and decisions.
4. The repository's current state: branch/ref, working-tree changes, relevant source files, and documented verification commands.
5. Any necessary access and authorization to perform the requested local work.

The agent records unavailable inputs as blockers. Chat history can clarify a request but does not replace missing canonical requirements or silently change the app's accepted decisions.

## Intended behavior

The implementation agent follows [`workflows/ai-engineering-execution.md`](../../workflows/ai-engineering-execution.md) to:

- Confirm one selected item is approved, unblocked, and sufficiently specified.
- Map each acceptance criterion to a planned implementation location and an observable verification method.
- Make the smallest coherent change that satisfies that item and existing project conventions.
- Run relevant checks that are available and permitted; report checks not run and why.
- Review the diff against scope, acceptance criteria, security/privacy considerations, and repository instructions.
- Update only the selected backlog item's milestone/status in its canonical source when evidence supports the transition.
- Provide a concise, evidence-backed completion or blocked report with changed files, checks/results, remaining risks, and next action.

## Constraints and decision rights

- Implement exactly one selected backlog item. Do not take adjacent tasks, opportunistic refactors, or unrelated cleanup. If another item is necessary, stop and report the dependency rather than silently expanding scope.
- Do not implement a task whose approval, dependencies, acceptance criteria, or controlling requirements are missing, contradictory, or materially ambiguous.
- Do not invent product behavior, data policy, technology choices, security policy, or acceptance criteria. Use documented project conventions only where they fit the approved contract.
- Preserve existing user changes. Inspect the working tree before editing; do not overwrite, revert, stage, commit, or discard unrelated changes without authorization.
- Do not expose, print, copy into artifacts, or commit secrets. Do not request broader access than the task requires.
- Local code changes and checks are within the execution scope when authorized by the task. Production deployment, external publication or messaging, purchases, destructive data operations, permission escalation, and other consequential external actions require the applicable owner authorization.
- A test pass does not establish production readiness or close a separate design, security, compliance, release, or operations gate.
- A failed or unavailable verification must remain visible. Never report a test, audit, review, or deployment as passed unless its result was observed.

## Preconditions and stop conditions

The workflow must stop before editing when:

- The repository root, governing instructions, canonical backlog, or selected item cannot be identified or read.
- The item is not explicitly selected, is not approved/ready under the app's documented status model, is blocked, or has unmet dependencies.
- Requirements conflict or a material product/architecture/security decision is needed to choose behavior.
- Acceptance criteria cannot be translated into a bounded change and an observable check.
- Required credentials, permissions, tools, or safe verification access are missing.
- The working tree contains changes that make the intended edit unsafe to isolate.

After editing, stop without marking the item complete when required checks fail, scope cannot be preserved, a consequential action is requested but not authorized, or evidence is insufficient. Make safe progress only when it does not depend on resolving the blocker; report that progress separately.

## Acceptance criteria

1. An agent can use the linked workflow to select and implement exactly one approved backlog item in the application's separate repository.
2. The workflow names required inputs, repository-context inspection, scope control, acceptance-criteria mapping, verification, diff review, status recording, and user reporting.
3. Missing or conflicting requirements, open owner decisions, unmet dependencies, unavailable permissions, and failed checks have explicit stop/report paths.
4. Only the selected backlog item may have its status/milestone updated; the update cites changed files and observed verification evidence.
5. Domain-specific practices are introduced only when the target project's contract requires them; the core workflow makes no app, financial, database, or technology-stack assumptions.
6. External consequential actions are not implied by local implementation and retain explicit owner authorization boundaries.
7. The final report distinguishes completed, partially completed, and blocked work and never claims unobserved verification.

## Evidence required to advance capability status

- Adversarial review of CAP-003 and its workflow, with all findings dispositioned and blocking findings resolved or explicitly owner-accepted under the framework policy.
- A bounded exercise implementing one approved backlog item in a separate application repository.
- Links to the selected requirement/task, changed files or code review, the selected backlog milestone, and actual verification output.
- A short exercise report identifying workflow friction, skipped/unavailable checks, remaining limitations, and any framework follow-up.

## Known limitations

- This specification and workflow are not yet adversarially reviewed or exercised as CAP-003.
- The current installed `execute-sdd-coder` skill assumes a particular `.codex-specs/` layout, is activated only by an exact phrase, requires backlog mutation, and includes finance/database-specific instructions. It is not a conforming generic implementation of CAP-003. It may be used only when the target project explicitly adopts and satisfies its contract; its domain-specific steps must not be generalized.
- Repository branch creation, CI behavior, code review policy, and test selection remain app-specific until a real project contract defines them.
