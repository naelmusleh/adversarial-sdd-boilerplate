---
id: WORKFLOW-QUALITY-001
type: workflow
title: Implementation verification and technical quality gates
status: draft
version: 0.3
created: 2026-10-07
updated: 2026-10-20
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, GATE-CATALOG-001, WORKFLOW-LIFECYCLE-001, FRAMEWORK-GATE-CONTRACT-001
---

# WORKFLOW-QUALITY-001 — Implementation verification and technical quality gates

## Purpose

Define how application code and requirements are verified before integration and release. Verification evidence must match the changed behavior, risk, and target surfaces. A design critique, compilation, passing unit tests, or an audit score alone does not prove every quality property.

## Inputs

- Selected backlog task and controlling approved requirement/design/architecture/decision IDs.
- The task's acceptance criteria, affected platforms, risk classification, and verification plan.
- App repository instructions, existing CI/checks, environments, and safe test data/access.
- Applicable passed design/architecture gates and their documented limitations.

## Procedure

1. Map each selected backlog acceptance criterion to a named check or manual verification method, its required/optional status, exact command or procedure, runtime/tool version, scope, pass condition, and evidence location. Draw required checks from the app's approved specification, architecture, backlog, verification plan, and existing CI contract. If no feasible method exists, record the gap and do not claim the criterion verified.
2. Select checks proportionate to the change and risk. Follow the app's documented stack and do not invent a universal test runner or coverage policy. Inspect existing CI and local instructions before running commands. A check configured by this template is not automatically a required check for an initialized app; the app's own approved contract must adopt, replace, or exclude it with rationale.
3. Verify affected behavior at the appropriate levels: unit/component, integration/API, end-to-end journey, data migration/integrity, security/privacy, accessibility, performance/reliability, and manual product review as applicable. Record excluded levels with a reason.
4. For web UI, use Impeccable `audit` on implemented UI where supported and inspect representative viewport, interaction, state, and assistive-technology behavior. Use `critique` separately for UX quality where the CX gate applies.
5. For native iOS/Android UI, use `audit.native` and representative simulators/devices as available; verify platform adaptation, accessibility (including VoiceOver/TalkBack), text scaling, input/keyboard, lifecycle/interruption, and relevant OS behavior. A Figma frame is not device verification.
6. Exercise failure/partial/empty/unknown states and recovery for integrations, persistence, and background/scheduled work when the task changes them. Do not use production user data unless the app's approved procedure allows it.
7. Run every required automated check and record the exact command/environment, source revision, scope, observed result, and date. For coverage, record the tool/provider and version, measured source paths, exclusions, dimensions reported, threshold, and actual result. Distinguish “not run,” “unavailable,” “not applicable,” and “failed.” A skipped or unavailable required check is not a pass. Never summarize a subset as “all checks pass.”
8. Inspect the complete diff for requirement coverage, unintended files, secrets, dependency changes, accessibility regressions, generated content, and project instructions. Obtain a separate reviewer when the gate requires independence.
9. Fix failures in the selected task's scope and rerun the failed checks. If a second focused attempt still fails or exposes a new owner decision/task, stop, preserve the failed status, and report the evidence and next action.
10. Record criterion-to-evidence mapping in the backlog milestone or linked verification record, including which checks were required and which ran. Update only the selected task unless the owner authorizes a broader change.

## G-IMPL and technical audit outcome

For **G-IMPL**, every selected task acceptance criterion must map to observed evidence from its planned required check(s), or to an explicitly authorized, scoped exception where the gate contract permits one. The linked verification plan identifies the task's required checks; the milestone identifies exact run evidence and results. All required checks must pass, and each criterion must have a disposition. A required check that did not run, lacks an observable result, or has a mismatched revision/scope cannot support a pass. The implementation milestone must be reviewed. A `G-IMPL` pass is not a `G-RELEASE` pass.

Coverage is a scoped metric, not a universal framework threshold. An application may require a coverage gate, but its approved verification plan must define the target source set, exclusions, coverage tool/provider and version, measured dimensions, threshold by dimension, and CI command that enforces it. Do not infer a threshold from a sample project or template repository. If an application has no approved coverage requirement or enforcement, report coverage as unconfigured/not measured rather than claiming 100% or treating a passing test suite as a coverage pass.

The bundled template's Vitest configuration requires 100% statements, branches, functions, and lines for the configured TypeScript/TSX files under this template's `src/` directory, excluding test/spec files and declaration files. That is a check of this bundled starter source set; it becomes an app requirement only when the app adopts that runtime/configuration in its own repository and verification contract. The template's Python initializer `unittest` suite has no configured coverage threshold. Its passing test count is test execution evidence, not Python coverage evidence. The separate Python pilot's recorded coverage applies only to its two named modules and pilot run as documented in `FRAMEWORK-PILOT-001`; it does not establish a default for future apps.

Use the verification plan's required-check matrix to connect task criteria to evidence. At minimum, each G-IMPL record cites the task/criterion, required check ID, exact command or procedure, revision and environment, scoped paths/platforms, pass condition, result, and durable evidence link. Optional checks may add information but do not replace a failed or missing required check.

For web/native technical audit gates, record target build/revision, tested routes/states/surfaces, audit scope, findings, severity, evidence, dispositions, rerun, and limitations. If platform/runtime verification is not available, mark the affected gate `blocked` or criteria `not run`; do not substitute design screenshots.

## Routing

- New product semantics, changed acceptance, or a user-visible trade-off → return to specification/owner decision.
- New structural/security/data boundaries → update architecture/ADR and rerun G-ARCH as needed.
- Unresolved design usability or visual issue → route through the CX design workflow and Impeccable gate.
- Release-only configuration, monitoring, or rollback gap → keep G-RELEASE blocked and route to release operations.

## References

- [FRAMEWORK-SPEC-001](../docs/framework/FRAMEWORK-SPEC-001.md)
- [GATE-CATALOG-001](../docs/framework/GATE-CATALOG-001.md)
- [Application lifecycle orchestrator](lifecycle.md)
- [AI engineering execution workflow](ai-engineering-execution.md)
- [Platform-aware CX design workflow](cx-design.md)
