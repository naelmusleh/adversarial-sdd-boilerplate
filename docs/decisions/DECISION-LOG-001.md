---
id: DECISION-LOG-001
type: decision-log
title: Reusable template decisions
status: active
version: 0.6
created: 2026-10-10
updated: 2026-10-21
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-EXERCISE-005, FRAMEWORK-GATE-CONTRACT-001
---

# DECISION-LOG-001 — Reusable template decisions

| ID | Date | Decision | Rationale and scope | References |
| --- | --- | --- | --- | --- |
| DECISION-017 | 2026-10-08 | The framework core is usable from a local checkout without ChatGPT Desktop or any single AI provider. Markdown and local helper scripts are the canonical procedures; humans and any available agent may execute them. | Integrations remain optional adapters unless a particular application records an approved tool-specific decision. | FRAMEWORK-SPEC-001, TOOL-CATALOG-001 |
| DECISION-018 | 2026-10-10 | License the public framework distribution under the MIT License. | The owner selected MIT. This decision does not publish the package; the package must first be reviewed and explicitly approved for public release. | FRAMEWORK-SPEC-001, LICENSE |
| DECISION-019 | 2026-10-21 | Require trusted CI attestation for G-IMPL PASS. | Repository owner Nael Musleh selected provider-verifiable attestation bound to the exact source revision, required-check manifest, and trusted workflow identity. Local command evidence may aid diagnosis but cannot support G-IMPL PASS. Apps without configured and successfully verified trusted provenance remain `in-progress` or `blocked`. This authorizes a versioned framework-contract and new-app initializer change; it does not authorize migrating existing apps or claim that an attestation proves test quality, repository protection, or production readiness. Revisit when a provider-neutral verifier is available or the configured CI provider/trust boundary changes. | FRAMEWORK-GATE-CONTRACT-001, GATE-CATALOG-001, FRAMEWORK-CI-RELEASE-POLICY-001, FRAMEWORK-ADV-013, FRAMEWORK-BACKLOG-001 |
| DECISION-020 | 2026-10-21 | Accept G-INTENT and G-SETUP as the only eligible synthetic PASS fixtures for FW-TASK-020's product-free pilot. | Owner Nael Musleh accepted this pilot-specific reading of “where permitted.” Other gates may have synthetic route/schema probes, but their pilot records remain `in-progress`; no product evidence or PASS is implied. This does not waive or change any gate requirement for initialized applications or amend the versioned gate contract. Revisit only if the FW-TASK-020 scope changes. | FRAMEWORK-ADV-013, FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-BACKLOG-001 |
| DECISION-021 | 2026-10-21 | Approve the bounded v2 scope for FW-TASK-026 and requirements FR-FW-019 through FR-FW-021. | Owner Nael Musleh approved a local transactional transition runner using the pinned approved contract, recoverable append-only gate state, and separately frozen advisory review records. The selected scope excludes other proposed v2 tasks. Approval does not authorize changes to normative gate semantics or adoption of a draft contract version without a separate reviewed decision. | FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-GATE-CONTRACT-001 |
| DECISION-022 | 2026-10-21 | Approve bounded v2 scope for FW-TASK-027 and requirements FR-FW-022 through FR-FW-024. | Owner Nael Musleh approved versioned gate/role context policies, fail-closed required-input handling, auditable source-bound projections with path/digest evidence and safe cleanup, and truthful context-minimization claims. This scope excludes FW-TASK-028 and other v2 tasks. No OS/container access-isolation claim or sandbox adapter is authorized; any future claim requires separately named host/runtime denial evidence and review. | FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, WORKFLOW-AI-ENGINEERING-001 |

## Decision discipline

Add a stable ID for each new material decision. Record the decision authority, date, rationale, impacted artifacts, consequences, and revisit conditions. Preserve app-specific decisions in that app's repository.

Decisions based on an assumption or experiment link its stable ID and evidence IDs, state the limits considered, and record the accountable owner’s actual choice and date. A recommendation, experiment status, or synthetic result is not an owner decision. Reopened or superseded decisions preserve prior records and identify affected requirements/tasks for reevaluation.
