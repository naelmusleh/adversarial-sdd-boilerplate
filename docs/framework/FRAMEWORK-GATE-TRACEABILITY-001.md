---
id: FRAMEWORK-GATE-TRACEABILITY-001
type: framework-traceability-matrix
title: Ten-gate contract source and enforcement traceability
status: draft
version: 1.1
created: 2026-10-20
updated: 2026-10-20
related-artifacts: FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-SPEC-001, GATE-CATALOG-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-EXERCISE-GATE-CONTRACT-001
---

# FRAMEWORK-GATE-TRACEABILITY-001 — Contract source and enforcement map

## Purpose and interpretation

This matrix maps every stable contract criterion to its governing requirement, lifecycle/catalog procedure, structural record fields, and the enforcement boundary. `Schema` means only that JSON structure can be checked; it is not evidence of semantic truth. `Validator (planned FW-TASK-018)` and `CI (planned FW-TASK-019)` are forward-looking work items, not current capabilities. Human judgment is explicit wherever a script cannot establish adequacy or authority.

## Criterion-level traceability

| Criterion ID | Governing requirement | Procedure source | Schema fields | Enforcement boundary |
|---|---|---|---|---|
| GINT-01 | FR-FW-003, FR-FW-004 | `GATE-CATALOG-001` Gate contracts; `workflows/product-discovery.md` Pass A | `gate_data.target_user`, `problem`, `evidence_class`; current mission artifact reference and accountable-owner decision bound to its SHA-256 | Validator checks exact current `mission.md` bytes, artifact identity, and decision choice; owner/reviewer judges problem relevance and evidence support; identity authenticity remains procedural. |
| GINT-02 | FR-FW-003, FR-FW-004, NFR-FW-004 | `workflows/product-discovery.md` Pass A | `gate_data.intended_outcome`, `success_signals[]`, criterion-linked mission artifact and owner approval | Schema checks explicit signals/status/plan; validator requires the current mission digest and matching owner decision; owner accepts outcome and validation plan. |
| GINT-03 | FR-FW-003, FR-FW-008 | `workflows/product-discovery.md` Pass A; source-of-truth map | `gate_data.constraints`, `assumptions[]`, `non_goals`, `decision_owners`, criterion-linked mission artifact and owner approval | Schema requires non-goals and assumption owners/plans; validator requires explicit accountable-owner approval of exact mission bytes; owner decides scope and authority. |
| GSET-01 | FR-FW-004, FR-FW-008, NFR-FW-006 | `workflows/lifecycle.md` lifecycle procedure; repository operating contract | `gate_data.repository_boundary`, `source_of_truth_map[]`, `owners_and_access[]` | Validator checks canonical paths/IDs; owner confirms ownership/access. |
| GSET-02 | FR-FW-004, FR-FW-014, NFR-FW-006 | `workflows/lifecycle.md`; app initializer and lock | `source_snapshot`, contract/lock version, `gate_data.toolchain[]` | FW-018 checks pin/digests; initializer creates lock; provenance must match actual source. |
| GSET-03 | FR-FW-004, NFR-FW-006 | `workflows/lifecycle.md`; generated SDD validation workflow | `gate_data.cold_start_evidence_ids`, `evidence[]` command/CI provenance, environments | FW-019 binds CI run to SHA; real cold start must execute; file presence is insufficient. |
| GREQ-01 | FR-FW-003, FR-FW-004 | `workflows/product-discovery.md` Pass B; `workflows/adversarial-review.md` | `gate_data.requirement_ids`, `decision_ids`, `task_ids` | FW-018 checks IDs/links; reviewer judges completeness and contradictions. |
| GREQ-02 | FR-FW-003, NFR-FW-004 | `workflows/product-discovery.md` Pass B | `gate_data.scope_in`, `scope_out`, criterion outcomes/evidence refs | Script checks linked verification method; owner/reviewer judges adequacy. |
| GREQ-03 | FR-FW-003, FR-FW-006, FR-FW-008 | `workflows/product-discovery.md` Pass B | `gate_data.task_ids`; universal `dependency_effects`, `next_action` | FW-018 checks references/state fields; owner resolves priorities and decisions. |
| GREQ-04 | FR-FW-005, FR-FW-009 | `workflows/product-discovery.md` Pass C; `workflows/adversarial-review.md` | `gate_data.review_evidence_ids`, `authority.reviewers`, findings, frozen artifact digests | Script checks frozen inputs/dispositions; reviewer identity/context independence remains procedural. |
| GFEAS-01 | FR-FW-003, FR-FW-004, FR-FW-008, NFR-FW-004 | `workflows/feasibility-architecture.md` Pass A | `gate_data.probes[]`: domain, question, evidence/source/date, classification/confidence/limits, requirements/tasks, owner/status, consequence/action | FW-018 checks probe/domain fields; experts/owner judge evidence and confidence. |
| GFEAS-02 | FR-FW-003, FR-FW-008 | `workflows/feasibility-architecture.md` Pass A | `gate_data.probes[].task_dependencies[]`, `state_change_trigger` (v1.1), and universal `dependency_effects` | Validator enforces every dependent task mapping/state and requires a trigger for conditional work; owner/expert decides safe boundaries and when triggers imply reassessment. |
| GFEAS-03 | FR-FW-008, FR-FW-009, NFR-FW-005 | `workflows/feasibility-architecture.md` Pass A and bounded experiments | probe `classification`, `negative_result_consequence`, `next_action`; owner decisions | Schema records probe/decision shape; owner risk decisions never prove unknown feasibility. |
| GCOV-01 | FR-FW-003, FR-FW-004, NFR-FW-005 | `workflows/cx-design.md` Required sources; design/CX matrix contract | `gate_data.journeys[]` actors, requirements, preconditions, transitions, exits, recovery | FW-018 checks requirement-to-journey linkage; reviewer judges completeness. |
| GCOV-02 | FR-FW-003, FR-FW-004, NFR-FW-004 | `workflows/cx-design.md` Procedure | journey `failure_exits`, `recovery_paths`; exclusions | Script checks failure/recovery categories; product/security reviewer judges applicability. |
| GCOV-03 | FR-FW-003, FR-FW-008, NFR-FW-005 | `workflows/cx-design.md` Cross-surface design | `gate_data.platform_applicability[]`, scope platforms/surfaces, exclusions | Validator requires per-surface applicability; owner approves exclusions and rationale. |
| GCX-01 | FR-FW-004, FR-FW-005, FR-FW-009 | `workflows/cx-design.md` Procedure and Gate sequence | `gate_data.frozen_scope_ref`, `interaction_evidence_ids`; typed evidence refs | Hash/scope can be checked; physical capture or product-appropriate trace must be reviewed. |
| GCX-02 | FR-FW-004, NFR-FW-004 | `workflows/cx-design.md` Record format | `gate_data.evaluator`, `method`, `tool_version`, `limitations`; evidence provenance | Schema checks fields; evaluator/tool adequacy and runtime limits are human judgment. |
| GCX-03 | FR-FW-005, FR-FW-009 | `workflows/cx-design.md`; `workflows/adversarial-review.md` rerun | `gate_data.finding_ids`, `rerun_ids`; findings, supersedes link | FW-018 checks finding/rerun links; reviewer verifies fixes against full affected scope. |
| GARCH-01 | FR-FW-003, FR-FW-004, NFR-FW-004 | `workflows/feasibility-architecture.md` Pass B | `gate_data.system_boundaries`, `trust_boundaries`, `identities_and_tenants`, `data_contracts`, `integrations_and_failures` | Structural contracts can be checked; threat/data-boundary adequacy requires review. |
| GARCH-02 | FR-FW-003, FR-FW-008 | `workflows/feasibility-architecture.md` Pass B | `gate_data.adrs`, `backlog_task_ids`; owner decisions, dependency effects | Validator checks alternative/decision/task linkage; accountable owner resolves tradeoffs. |
| GARCH-03 | FR-FW-005, FR-FW-009, NFR-FW-003 | `workflows/feasibility-architecture.md` G-ARCH evidence | `gate_data.verification_contracts[]`, artifact digests, reviewer records | FW-018 can run declared structural checks; digest or assertion text is not semantic verification. |
| GIMPL-01 | FR-FW-003, FR-FW-006 | `workflows/ai-engineering-execution.md` Confirm target/task; scope | `gate_data.selected_task_id`, `criterion_check_mappings[]`, scope paths | FW-018 checks one task/link shape; owner-approved backlog defines the actual task. |
| GIMPL-02 | FR-FW-005, FR-FW-006, NFR-FW-003 | `workflows/ai-engineering-execution.md` Verify and review; `workflows/engineering-quality-gates.md` | `gate_data.required_checks[]`, command/CI evidence, source SHA, scope/result | FW-019 ties CI to exact SHA; a runtime/CI system must produce observed output. |
| GIMPL-03 | FR-FW-006, FR-FW-015, NFR-FW-003 | `workflows/ai-engineering-execution.md` Preserve completed work in Git and Record milestone | `change_control`, `authority.reviewers`, findings, next action | Script checks SHA/ref/status shape; remote push and reviewer judgment require actual evidence. |
| GREL-01 | FR-FW-005, FR-FW-007, FR-FW-014 | `workflows/release-operations.md` Release readiness and G-RELEASE | `gate_data.tested_commit_sha`, `artifact_sha256`, `change_control.release_artifact_sha256`, CI refs | FW-019 binds artifact to tested revision; independent build provenance may require provider evidence. |
| GREL-02 | FR-FW-007, FR-FW-008, NFR-FW-004 | `workflows/release-operations.md` Release readiness procedure | `gate_data.required_check_evidence_ids`, security/platform refs, recovery plan, support owner | Checklist shape can be checked; security/recovery/support sufficiency is reviewed by responsible roles. |
| GREL-03 | FR-FW-005, FR-FW-007, FR-FW-015 | `workflows/release-operations.md` G-RELEASE | `gate_data.owner_authorization_id`, `environment`, exact artifact digest | Schema links decision/digest; owner authorization and provider branch protection must be observed, not inferred. |
| GOP-01 | FR-FW-007, NFR-FW-004 | `workflows/release-operations.md` Post-deployment operation and G-OPERATE | `gate_data.operator`, `escalation_owner`, `runbook_evidence_ids` | Owner and operator execute/review runbook; script checks ownership and record presence. |
| GOP-02 | FR-FW-003, FR-FW-007, NFR-FW-004 | `workflows/release-operations.md` G-OPERATE | `gate_data.health_signals`, `telemetry_gaps`, `outcome_records`; operational evidence provenance | Schema requires provenance/gaps; operator/reviewer interprets signal quality and missing telemetry. |
| GOP-03 | FR-FW-003, FR-FW-007, FR-FW-009 | `workflows/release-operations.md` G-OPERATE | `gate_data.incident_ids`, `learning_task_ids`, findings/decisions/dependency links | FW-018 checks linked learning records; operator/owner prioritizes action and incident response. |

## Contract-to-repository cross-reference

| Repository element | Relationship to the contract | Change/migration rule |
|---|---|---|
| `docs/framework/GATE-CATALOG-001.md` | Human-readable overview and gate workflow source; must link here for normative criterion/state semantics. | Reconcile divergent claims in same reviewed contract update; do not copy full criteria as an independent authority. |
| `workflows/product-discovery.md` | G-INTENT/G-REQ procedures. | Add criterion IDs and align handoff/result terms. |
| `workflows/feasibility-architecture.md` | G-FEAS/G-ARCH procedures. | Add criterion IDs and preserve feasibility-screen versus architecture-selection boundary. |
| `workflows/cx-design.md` | G-COVERAGE/G-CX procedures. | Add criterion IDs; preserve nonvisual evidence alternatives and full-scope reruns. |
| `workflows/adversarial-review.md` | Reviewer identity, findings, disposition, and rerun. | Reference separation-of-duty fields and allowed result transitions. |
| `workflows/ai-engineering-execution.md`, `workflows/engineering-quality-gates.md` | G-IMPL checks, scoped commit/push, observed verification. | Link criterion IDs; never accept copied terminal logs or local commit as push. |
| `workflows/release-operations.md` | G-RELEASE/G-OPERATE. | Bind authorization to artifact/environment and preserve local/offline recovery conditions. |
| `docs/templates/app-project/gate-record.md.template` | Human-readable record instructions. | Add contract version, criteria/evidence fields, state/result distinction, revision/change-control references. |
| `.sdd/G-REQ-HANDOFF.json.template`, `.sdd/G-ARCH-CONTRACT.json.template`, `.sdd/framework.lock.json.template` | App revision and G-REQ/G-ARCH frozen handoff inputs. | Contract/lock version pin is explicit; existing generated apps migrate only through a new reviewed task. |
| `scripts/init_app_project.py` | Copies and pins contract, schema, templates, and validator into new app. | FW-TASK-018/015 integration; generated bytes and lock digests must match exact pinned revision. |
| `scripts/artifacts.py` | Current structural artifact/handoff checker; not yet the ten-gate validator. | FW-TASK-018 adds gate-run validation under this contract and preserves legacy mode without silent promotion. |
| `.github/workflows/verify-pipeline.yml`, generated app SDD workflow | Framework/app structural and declared code checks. | FW-TASK-019 binds runs to commit SHA and records remote protection separately; do not create a competing workflow. |
| `docs/framework/schemas/gate-run-v1.schema.json`; `gate-run-v1.1.schema.json` | Structural schemas selected by the pinned contract version. | Any semantic schema change requires contract version/change-control update and fixtures. |
| `docs/framework/examples/gate-contract-v1/` | Synthetic valid/invalid fixtures, including per-gate and stale/hash cases. | Fixtures are never product evidence; update with schema/contract changes. |
| `FRAMEWORK-EXERCISE-GATE-CONTRACT-001` | Frozen adversarial cases for the independent contract review. | Reviewer records actual outcomes in a separate review artifact; this plan is not execution evidence. |

## Enforcement ownership

- **FW-TASK-017 (this contract):** semantics, stable criterion IDs, schema, traceability, migration rules, synthetic fixtures, and independent adversarial review.
- **FW-TASK-018:** standard-library app validator, schema/identity/linkage/state validation, full positive/negative fixture execution, and app initializer distribution. It may validate evidence shape and provenance linkage, not semantic truth.
- **FW-TASK-019:** workflow/check manifest, exact source/run/artifact binding, release authorization record, and provider-setting observation. Hosted CI and branch protection are reported `unverified` unless actually observed.
- **FW-TASK-020:** separate synthetic app adversarial bypass pilot and independent assessment. It tests controls; it does not prove production readiness.
