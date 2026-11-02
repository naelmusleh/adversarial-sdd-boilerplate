---
id: WORKFLOW-RELEASE-001
type: workflow
title: Application release and operations workflow
status: draft
version: 0.2
created: 2026-10-07
updated: 2026-10-20
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, GATE-CATALOG-001, WORKFLOW-LIFECYCLE-001, FRAMEWORK-GATE-CONTRACT-001
---

# WORKFLOW-RELEASE-001 — Application release and operations workflow

## Purpose and boundary

Take an app-specific release candidate from verified code through a controlled deployment and ongoing learning. The workflow is provider-neutral; it prepares evidence and acts only within the app's documented authorization boundary. Production deployment, external communication, spending, destructive actions, and permission changes require the authority specified by the app's constitution and release plan.

## Roles

- **Release owner/approver:** authorizes the specific release after reviewing evidence and risk.
- **Release agent:** assembles checks, prepares deployment changes, records observed outcomes, and does not misstate an unexecuted step.
- **Operator:** owns service health, alerts, support, incident response, rollback/recovery, and access lifecycle.
- **Independent reviewer:** checks the release evidence and risk where the app's policy requires a distinct reviewer.

## Entry conditions

- G-REQ, applicable G-FEAS, G-CX, and G-ARCH outcomes are acceptable for the release scope.
- The release candidate has passed G-IMPL for its included work; required web/native technical audits and security/privacy/accessibility checks have evidence.
- Requirements, release scope, supported surfaces, known limitations, data lifecycle, user communication, monitoring, support, and rollback are documented.
- External access, environments, secrets, billing, domains, app-store accounts, and provider configuration are ready through approved secure channels; secrets are not written to repository artifacts.

If an entry condition is unmet, keep G-RELEASE blocked. A checklist cannot convert missing evidence into a pass.

## Release readiness procedure

1. Freeze release identity, source revision, scope, environments, supported platforms, included migrations, and excluded/known issues.
2. Collect the current evidence for all release-critical requirements and gates. Confirm results match the candidate revision and deployment target; stale evidence must be rerun if code/config changed materially.
3. Verify release mechanics: build/package provenance; environment configuration; secret access; data migration/backup and restore where applicable; compatibility; rollout/feature flag; health checks; alert routes; and rollback/disable procedure.
4. Verify user/operator readiness: release notes and limitations; support route and ownership; runbook; privacy/security communications if required; account/data export/deletion commitments; and escalation paths. Do not present unimplemented controls as available.
5. Assess residual risks and incidents. For each, record impact, likelihood/evidence, mitigation, operator, monitoring, rollback trigger, and whether the release owner can accept it under policy. Legal/security risks that require qualified review remain blocked until that review exists.
6. Conduct an independent release review where required. Fix blocking findings in a focused batch and rerun the affected full scope. If unresolved, stop and report options and consequences.
7. Present the accountable owner with a concrete release request: version, scope, evidence, remaining risk, deployment plan, rollback, operator, and required authorization. Do not deploy until authorized.
8. After authorization, perform only the agreed deployment actions. Record the actual start/end time, operator, revision, steps, outcome, health checks, rollback if triggered, and any deviation. If deployment was not executed, state that explicitly.

## G-RELEASE

Pass G-RELEASE only when the app's specific release criteria are met, required evidence is linked, an accountable operator is assigned, recovery/rollback is actionable, and the owner has authorized the particular release. “Ready to deploy” is distinct from “deployed successfully.” Store the gate record and outcome under the app's `delivery/` directory.

## Post-deployment operation

1. Confirm service health, key user journeys, data integrity, provider dependencies, and platform distribution status for the actual deployed scope.
2. Monitor agreed availability/error/latency/security/cost signals and support feedback. Each signal names its source, threshold rationale, owner, and response action; do not invent service-level promises.
3. For an incident, contain user/data harm first using the app's approved authority. Preserve relevant logs/evidence with privacy controls, inform the accountable operator, and record a timeline and impact. Avoid declaring root cause until evidence supports it.
4. Verify recovery and communicate user impact through approved channels. Link corrective tasks, owners, and due/revisit conditions.
5. At the agreed learning checkpoint, compare product outcomes and quality signals with baseline/targets; update hypotheses, decisions, and backlog. Product metrics must not be interpreted as causal proof without an appropriate evaluation method.
6. Record retention, export, and deletion operations based on approved policy. If the product lacks a supported path, state that limitation and keep promises aligned.

## G-OPERATE

Pass G-OPERATE when a named operator owns monitoring and response, support/incident procedures are usable, material incidents and learning are linked to decisions/tasks, and unresolved service risks have owners and next actions. Reopen earlier gates only when new evidence invalidates their acceptance or a changed requirement warrants review.

## References

- [FRAMEWORK-SPEC-001](../docs/framework/FRAMEWORK-SPEC-001.md)
- [GATE-CATALOG-001](../docs/framework/GATE-CATALOG-001.md)
- [Application lifecycle orchestrator](lifecycle.md)
- [Implementation quality gates](engineering-quality-gates.md)
- [Application release-record template](../docs/templates/app-project/release-record.md.template)
- [Application operations-runbook template](../docs/templates/app-project/operations-runbook.md.template)
