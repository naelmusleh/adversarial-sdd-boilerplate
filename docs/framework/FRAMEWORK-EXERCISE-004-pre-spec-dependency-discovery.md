---
id: FRAMEWORK-EXERCISE-004
type: framework-exercise
title: Pre-specification dependency discovery examples
status: draft
version: 0.1
created: 2026-10-21
updated: 2026-10-21
related-artifacts: FRAMEWORK-BACKLOG-001, WORKFLOW-DISCOVERY-001, WORKFLOW-FEASIBILITY-001, GATE-CATALOG-001
---

# FRAMEWORK-EXERCISE-004 — Pre-specification dependency discovery

## Purpose and evidence boundary

Show how an early dependency screen identifies provider/service claims before requirements are treated as settled, separates capability evidence from account/cost/permission evidence, and blocks only dependent promises. This is a process example, not a formal G-FEAS run or provider approval. The machine-readable scenarios in [`tests/fixtures/fw022_dependency_scenarios.json`](../../tests/fixtures/fw022_dependency_scenarios.json) are synthetic routing fixtures. Only the linked Google documentation is real primary-source evidence, accessed 2026-10-21; it proves documented API functionality and published billing conditions, not access for a particular project, legal suitability, budget acceptability, or successful runtime behavior.

## Source-linked example register

| Probe | Claim and classification | Primary evidence | Limits and downstream effect |
| --- | --- | --- | --- |
| `DEP-PLACE-CAPABILITY` | **Supported, narrowly:** Google Places API (New) documents autocomplete capability for place predictions. | [Places API overview](https://developers.google.com/maps/documentation/places/web-service/overview/) (Google for Developers; accessed 2026-10-21). | Does not establish a particular account, enabled API, permission, region, cost, rights, or privacy controls. Provider-neutral UX exploration can proceed; the live integration stays separately blocked on access evidence. |
| `DEP-PLACE-ACCESS` | **Unknown:** this product/project's API account and permission state have not been checked. | No project credential or authorized account probe was available; no credential was requested or read. | Keep integration blocked; identify secure setup. Do not infer unavailable from missing credentials. |
| `DEP-PLACE-COST` | **Constrained:** the provider documents billing requirements and usage/SKU-based pricing, while the sample owner budget and workload estimate are unknown. | [Places API usage and billing](https://developers.google.com/maps/documentation/places/web-service/usage-and-billing/) (Google for Developers; accessed 2026-10-21). | Mock-only design may continue. Keep billable/live work conditional until current pricing, workload estimate, and owner cost ceiling are reviewed. The cited source is a constraint signal, not a completed cost estimate. |

The source supports the existence of a documented feature and billing conditions only. It must not be summarized as “Google is approved/available for this project.” Separate region, terms, permissions, data flow, cost and operational probes are still required where material.

## Positive and negative routing cases

The remaining scenarios deliberately use synthetic fixtures so tests can exercise the route without network calls, real credentials, or provider claims:

- **Unsupported:** an exact sandbox endpoint returns a fixture HTTP 410. Mark only that endpoint unsupported; block its live integration, keep unrelated manual inventory work available, and investigate a scoped alternative. This does not claim a real vendor endpoint returned 410.
- **Unknown:** a fixture environment says a credential is absent, without reading a credential value. Block the private integration, leave independent mock UX unblocked, and record the secure access route. Absence of credentials is not evidence the service is unavailable.
- **Constrained:** billing and usage-based charges exist but the owner budget and workload estimate do not. Keep provider-dependent work conditional with a synthetic-data/no-billable-call boundary and a clear owner decision trigger.
- **Not applicable:** a synthetic owner decision excludes native iOS from a web-only pilot. Create no iOS-store task; keep web discovery unblocked; reopen if scope changes. A real project requires its own owner-approved exclusion.

## Handoff to formal G-FEAS

During specification drafting, replace intent-text anchors with requirement IDs and map every material probe to actual backlog tasks. Before specification lock, copy verified constraints into requirements and preserve open probes and their task states. At formal G-FEAS, reconcile these stable probe keys into the app's feasibility register, deepen evidence for applicable legal/privacy/security/cost/platform/operations domains, and declare explicit `blocked`, `unblocked`, or `conditional` states for every dependent task. This early screen neither selects a system nor passes G-FEAS. G-FEAS remains governed by the existing gate contract.

## Check boundary

Automated tests assert the fixture classifications, evidence provenance shape, downstream task effects, owner/scope basis for `not-applicable`, credential non-disclosure, conditional safe-work boundaries, and the explicit `not-run` G-FEAS marker. They do not fetch provider pages, validate pricing for a real workload, exercise credentials, or execute an integration.
