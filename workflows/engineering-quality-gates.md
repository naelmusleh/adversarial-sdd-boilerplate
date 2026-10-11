---
id: WORKFLOW-QUALITY-001
type: workflow
title: Implementation verification and technical quality gates
status: draft
version: 0.1
created: 2026-10-07
updated: 2026-10-08
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, GATE-CATALOG-001, WORKFLOW-LIFECYCLE-001
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

1. Map each acceptance criterion to a verification method before or during implementation: automated test/check, static inspection, browser/device procedure, external evidence, or owner acceptance. If no method exists, record the gap and do not claim the criterion verified.
2. Select checks proportionate to the change and risk. Follow the app's documented stack and do not invent a universal test runner. Inspect existing CI and local instructions before running commands.
3. Verify affected behavior at the appropriate levels: unit/component, integration/API, end-to-end journey, data migration/integrity, security/privacy, accessibility, performance/reliability, and manual product review as applicable. Record excluded levels with a reason.
4. For web UI, use Impeccable `audit` on implemented UI where supported and inspect representative viewport, interaction, state, and assistive-technology behavior. Use `critique` separately for UX quality where the CX gate applies.
5. For native iOS/Android UI, use `audit.native` and representative simulators/devices as available; verify platform adaptation, accessibility (including VoiceOver/TalkBack), text scaling, input/keyboard, lifecycle/interruption, and relevant OS behavior. A Figma frame is not device verification.
6. Exercise failure/partial/empty/unknown states and recovery for integrations, persistence, and background/scheduled work when the task changes them. Do not use production user data unless the app's approved procedure allows it.
7. Run required automated checks and record the exact command/environment, scope, observed result, and date. Distinguish “not run,” “unavailable,” “not applicable,” and “failed.” Never summarize a subset as “all checks pass.”
8. Inspect the complete diff for requirement coverage, unintended files, secrets, dependency changes, accessibility regressions, generated content, and project instructions. Obtain a separate reviewer when the gate requires independence.
9. Fix failures in the selected task's scope and rerun the failed checks. If a second focused attempt still fails or exposes a new owner decision/task, stop, preserve the failed status, and report the evidence and next action.
10. Record criterion-to-evidence mapping in the backlog milestone or linked verification record. Update only the selected task unless the owner authorizes a broader change.

## G-IMPL and technical audit outcome

For **G-IMPL**, every selected task acceptance criterion must be supported by observed evidence or an explicitly authorized, scoped exception. The implementation milestone must be reviewed. A `G-IMPL` pass is not a `G-RELEASE` pass.

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
