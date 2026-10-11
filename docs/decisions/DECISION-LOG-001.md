---
id: DECISION-LOG-001
type: decision-log
title: Reusable template decisions
status: active
version: 0.1
created: 2026-10-10
updated: 2026-10-10
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001
---

# DECISION-LOG-001 — Reusable template decisions

| ID | Date | Decision | Rationale and scope | References |
| --- | --- | --- | --- | --- |
| DECISION-017 | 2026-10-08 | The framework core is usable from a local checkout without ChatGPT Desktop or any single AI provider. Markdown and local helper scripts are the canonical procedures; humans and any available agent may execute them. | Integrations remain optional adapters unless a particular application records an approved tool-specific decision. | FRAMEWORK-SPEC-001, TOOL-CATALOG-001 |
| DECISION-018 | 2026-10-10 | License the public framework distribution under the MIT License. | The owner selected MIT. This decision does not publish the package; the package must first be reviewed and explicitly approved for public release. | FRAMEWORK-SPEC-001, LICENSE |

## Decision discipline

Add a stable ID for each new material decision. Record the decision authority, date, rationale, impacted artifacts, consequences, and revisit conditions. Preserve app-specific decisions in that app's repository.
