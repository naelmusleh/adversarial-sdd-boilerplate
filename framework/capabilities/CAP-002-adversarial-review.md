---
id: CAP-002
type: framework-capability
title: Adversarial Review Workflow
status: active
version: 0.3
created: 2026-10-05
updated: 2026-10-08
---

# CAP-002 — Adversarial Review Workflow

## Need

Requirements need an independent challenge before they become implementation commitments. Chat-based critique alone does not preserve the target version, findings, dispositions, and approval state.

## User

The product owner and AI agents producing and reviewing requirements or design artifacts.

## Capability boundary

CAP-002 is an executable **manual review procedure and artifact format**. AI agents perform the critic, disposition, revision-support, and verification work; the authorized owner makes product decisions and accepts residual risk. The capability does not provide automatic agent orchestration, guarantee factual correctness, or make same-agent review independent.

## Intended behavior

- Freeze the artifact ID and version being reviewed.
- Run a clearly labeled critic pass that identifies evidence-based findings and uncertainties.
- Give each finding a stable review-scoped ID, severity, evidence, impact, recommendation, and owner-decision flag.
- Record disposition for every finding and link any resulting revision.
- Keep the critic's findings separate from the source artifact and prevent silent approval.
- Rerun the original scope against a linked target revision and explicitly check each prior finding.
- Set a gate outcome using defined PASS, FAIL, INCONCLUSIVE, or NOT A GATE rules; do not use a score as a substitute.
- Keep the review artifact lifecycle status separate from the gate outcome; INCONCLUSIVE is a gate result and blocks progression, never an artifact status.
- Bound remediation cycles and stop with a decision-ready escalation when findings persist.
- Record explicit owner acceptance for any residual risk used to proceed, including scope, impact, mitigation, and revisit condition.

## Acceptance criteria

- Review records identify the exact artifact version and review scope.
- Findings are actionable, traceable, and distinguish evidence from inference.
- Every finding receives an explicit disposition.
- Blocking findings and owner decisions prevent approval until resolved or explicitly accepted by the authorized owner.
- Review output, revision, and final status can be followed from repository history.
- The reviewer can follow the procedure from its inputs without undocumented chat conventions; the workflow defines role overlap, rerun behavior, gate outcomes, and stop conditions.
- A self-review is disclosed and cannot pass a gate that requires independence.

## First exercise and evidence

Use review records from the current target repository as evidence examples. Keep the reviewed artifact version, evaluator independence, evidence scope, findings, dispositions, and rerun results explicit. A self-review or an example from another project does not establish independent approval for the current target.

The revised manual procedure was exercised on itself in [FRAMEWORK-ADV-001](../../docs/adversarial-reviews/FRAMEWORK-ADV-001.md). That bounded conformance exercise recorded findings, dispositions, a source revision, and a rerun. It confirmed the procedure's record and status transitions, but its reviewer was not independent; it does not independently approve this workflow or validate other artifact types.

## Limits and next evidence

- The process is manual; no script enforces finding completeness, disposition transitions, or gate status.
- Independent review requires another qualified reviewer or separate reasoning context and must be recorded; it is not guaranteed by this repository.
- Evidence quality depends on the reviewer, available sources, and declared scope. The workflow cannot prove external facts without appropriate verification.
- Do not add orchestration automation until manual exercises demonstrate a repeatable bottleneck.

## References

- [FRAMEWORK-001](../../docs/constitution/FRAMEWORK-001.md)
- [FRAMEWORK-002](../../docs/constitution/FRAMEWORK-002.md)
- [Adversarial review workflow](../../workflows/adversarial-review.md)
- [Reusable review template](../../docs/templates/adversarial-review.md)
- [FRAMEWORK-ADV-001 conformance exercise](../../docs/adversarial-reviews/FRAMEWORK-ADV-001.md)
