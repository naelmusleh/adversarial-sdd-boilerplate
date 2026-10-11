---
id: FRAMEWORK-002
type: framework-process
title: Artifact system and framework build loop
status: active
version: 1.5
created: 2026-10-05
updated: 2026-10-10
---

# FRAMEWORK-002 — Artifact system and build loop

## Artifact rules

- Give each durable artifact a unique, stable ID, such as `MISSION-001`, `PRD-001`, `ADR-001`, or `PRODUCT-ADV-001`.
- Store project Markdown artifacts under `docs/` or the app repository's canonical SDD folders.
- Include `id`, `type`, `title`, `status`, `version`, `created`, and `updated` in YAML-style flat front matter.
- Link related artifacts by ID and relative path where known. Never reuse a retired ID.
- Record substantive changes in Git; increment the artifact version when content or status materially changes.
- Keep decision records and review records distinct from the requirements they affect.
- Use the controlled lifecycle statuses `draft`, `in-review`, `revision-required`, `approved`, `active`, `blocked`, `superseded`, and `retired`. Gate outcome is a separate field.

## Build loop

```text
Mission or product need
  → identify a missing capability
  → specify the smallest reusable capability
  → challenge the specification
  → implement and record evidence
  → exercise it in an application repository
  → capture gaps and improve the template
```

Capability IDs use `CAP-###`; implementation tasks use `TASK-###`. A capability specification identifies the user, problem, behavior, constraints, acceptance criteria, and evidence. Do not build speculative infrastructure ahead of a demonstrated need.

## Review and CX gates

A review record captures the reviewed artifact/version, reviewer mode, findings, severity, evidence, disposition, revision, and final status. G-CX is mandatory for CX design sign-off and engineering handoff. Use the evaluator selected in the app's own constitution; when Impeccable is adopted, run its complete-scope `critique` and preserve evidence. Otherwise follow the tool-neutral procedure in `docs/framework/GATE-CATALOG-001.md`. Fix findings and rerun the complete affected scope. A score cannot override unresolved findings. Static design inspection cannot prove runtime behavior, device accessibility, or service integration.

## Initial document map

| Artifact | Purpose |
| --- | --- |
| [MISSION-001](../missions/MISSION-001.md) | Why the reusable lifecycle exists. |
| [FRAMEWORK-001](FRAMEWORK-001.md) | Durable principles and quality bar. |
| [FRAMEWORK-002](FRAMEWORK-002.md) | Artifact conventions and build loop. |
| [FRAMEWORK-SPEC-001](../framework/FRAMEWORK-SPEC-001.md) | Framework scope, behavior, and v1 exit evidence. |
| [FRAMEWORK-BACKLOG-001](../framework/FRAMEWORK-BACKLOG-001.md) | Ordered framework work and current evidence state. |
| [GATE-CATALOG-001](../framework/GATE-CATALOG-001.md) | Gate outcomes and evidence contracts. |
| [TOOL-CATALOG-001](../framework/TOOL-CATALOG-001.md) | Current tools and verified limitations. |
| [CAP-000](../../framework/capabilities/CAP-000-template-initialization.md) | Fresh-session bootstrap and source-of-truth rules. |
| [CAP-001](../../framework/capabilities/CAP-001-artifact-management.md) | Local artifact helper behavior. |
| [CAP-004](../../framework/capabilities/CAP-004-app-repository-bootstrap.md) | App repository starter and handoff. |
