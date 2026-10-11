---
id: FRAMEWORK-BACKLOG-001
type: framework-backlog
title: Remaining work to complete Adversarial SDD Framework v1
status: draft
version: 1.1
created: 2026-10-07
updated: 2026-10-10
related-artifacts: MISSION-001, FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-SPEC-001
---

# FRAMEWORK-BACKLOG-001 — Remaining work to complete Adversarial SDD Framework v1

## Purpose and status

This is the ordered backlog for finishing the reusable framework, not an application backlog. Items are sequenced by dependency and can be adjusted when evidence exposes a better order. An item is complete only when its acceptance evidence is recorded in the repository. The slide is a target-state overview; this backlog is the execution plan.

**Current framework state (updated 2026-10-10):** CAP-001 artifact management and CAP-004 app bootstrap are implemented. To reduce startup overhead, CAP-004 now defaults to five canonical SDD artifacts plus README, agent instructions, `.gitignore`, and the local helper; detailed lifecycle records remain available on demand. FRAMEWORK-ADV-007 independently passed the profile split and generated README review; five local tests also cover downloaded-source use without Git metadata. CAP-002 has an independent passing conformance review; the lifecycle/gate contract has passed independent review with a completed paper tabletop; and the CAP-003 through release/operations workflow set has passed bounded written review. The first app implementation remains the principal proof gap; distribution-package review is outstanding before public use.

## Recommended execution sequence

```text
FW-TASK-001 Canonical project artifact model
        ↓
FW-TASK-002 Lifecycle and gate contracts
        ↓
FW-TASK-003 Complete adversarial-review capability ─┐
FW-TASK-004 Specify general AI engineering execution ├─→ FW-TASK-005 Feasibility/architecture
                                                     ├─→ FW-TASK-006 Verification and release
                                                     └─→ FW-TASK-007 Operations and learning
                                                              ↓
FW-TASK-008 Starter package + repository handoff
        ↓
FW-TASK-009 End-to-end pilot in separate app repository
        ↓
FW-TASK-010 Framework v1 review, release record, and operator guide
```

The lifecycle and gate contract (002) establishes shared handoff semantics. CAP-002 is complete against the review-status subset of that contract; the full lifecycle review remains open. CAP-003 (004) can proceed against the current contract and receive a focused review independently. Items 005–007 are drafted against the same handoffs and can be reviewed in parallel where their acceptance evidence does not depend on another workflow. Run a bounded app-repository pilot only after its product inputs and mandatory gates permit it; otherwise use a small neutral example with synthetic data and no production dependencies.

## Backlog items

### FW-TASK-001 — Define the canonical project artifact model

- **Goal:** Establish the single-source-of-truth file map and starter structure for a new app project.
- **Requirements:** FR-FW-002, FR-FW-003, FR-FW-012; NFR-FW-002.
- **Dependencies:** None.
- **Work:** Define the roles and boundaries of `constitution.md`, `specification.md`, `design.md`, `backlog.md`, decisions, reviews, architecture, delivery evidence, and operations records. Map Impeccable `PRODUCT.md` and `DESIGN.md` as canonical/derived inputs. Choose one canonical CX matrix location; eliminate unsynchronized required duplicates. Keep `FRAMEWORK-001` and `FRAMEWORK-002` authoritative for this repository.
- **Acceptance criteria:**
  1. A documented project tree and artifact ownership table exist.
  2. Every artifact specifies ID/metadata needs, purpose, owner/editor, lifecycle status, and links to its inputs/outputs.
  3. No document instructs users to independently maintain duplicate canonical copies.
  4. App-specific artifacts are explicitly required to live in the app repository after setup.
  5. Nested project scaffolding is excluded from the framework artifact inventory and validator, so the starter's ordinary README and placeholders are not treated as live artifacts.
- **Evidence:** [App-project starter guide](../templates/app-project/README.md), generated sample behavior, and independent review [FRAMEWORK-ADV-003](../adversarial-reviews/FRAMEWORK-ADV-003.md).
- **State:** Complete — D-FW-05 is resolved; the artifact map, templates, initializer, and fresh-repository generation are independently reviewed in FRAMEWORK-ADV-003.

- **Execution update (2026-10-08):** The owner chose canonical SDD `design.md` and separate Impeccable generated output under `.impeccable/generated/`. The installed `document` workflow writes at project root, so the starter specifies running it in an isolated staging copy and moving reviewed output into `.impeccable/generated/`; safety and tool compatibility remain to be exercised during the app-repository pilot. The initializer creates a 20-file starter tree in a clean temporary repository; template review remains open.

### FW-TASK-002 — Write the end-to-end lifecycle and gate contracts

- **Goal:** Convert the ten-stage slide into a usable process that says what to do next and how a stage ends.
- **Requirements:** FR-FW-001, FR-FW-004, FR-FW-005, FR-FW-008, FR-FW-009, FR-FW-010.
- **Dependencies:** FW-TASK-001.
- **Work:** Define lifecycle statuses, stage entry/exit criteria, stage owner, agent work, artifacts, gate evidence, dependencies, escalation, and re-entry routes. Add early/parallel feasibility checks for data/provider, legal, security, platform, cost, and operations. Define finite critique/fix/rerun loops and escalation instead of “repeat until perfect.”
- **Acceptance criteria:**
  1. Each lifecycle stage maps to one or more named workflows, inputs, durable outputs, and explicit gate or reason no gate applies.
  2. Requirements, CX, architecture/security, implementation, release, and operations gates have different evidence contracts.
  3. The flow supports parallel feasibility research and feedback loops without obscuring the main sequence.
  4. A blocked project status tells the owner what is blocked, why, who can resolve it, and the next useful action.
  5. A tabletop walkthrough of a new app idea identifies no unexplained handoff or “what next?” gap.
- **Evidence:** Lifecycle runbook, gate catalog, and walkthrough record linked to the framework specification.
- **State:** Complete — lifecycle, discovery workflow, gate catalog, and paper tabletop are recorded; independent lifecycle/gate review FRAMEWORK-ADV-004 v0.2 passed with all three findings verified resolved. The review explicitly limits its claim: empirical owner usability, fresh-app initialization, and implementation/release pilot evidence remain FW-TASK-008/009 work.

- **Execution update (2026-10-10):** FRAMEWORK-ADV-004 v0.2 passed after the gate-table correction. The paper tabletop remains a paper exercise; it supports FW-TASK-002's lifecycle handoff criterion but does not replace the separate-app pilot in FW-TASK-009.

### FW-TASK-003 — Complete CAP-002 adversarial review as a usable capability

- **Goal:** Establish CAP-002 as a usable, accurately bounded manual review capability with independent conformance evidence.
- **Requirements:** FR-FW-003, FR-FW-005, FR-FW-009; NFR-FW-003.
- **Dependencies:** FW-TASK-001 and the review-status/gate-result semantics defined in FW-TASK-002; full lifecycle tabletop evidence is not a prerequisite for the manual review capability.
- **Work:** Update the review workflow and templates to capture exact target/version/scope, independent review method, evidence vs inference, severity, owner-decision flag, disposition, revised artifact, rerun, and final gate state. Clarify which steps are manual practice and which are tool-supported; do not invent orchestration automation.
- **Acceptance criteria:**
  1. A reviewer can execute the workflow from its inputs without relying on undocumented chat conventions.
  2. Findings cannot disappear through silent edits; every finding has a disposition and evidence.
  3. A failed review remains failed until a verified rerun passes or the authorized owner accepts the documented residual risk.
  4. CAP-002 status accurately reflects demonstrated capability and evidence.
  5. Existing review artifacts are linked as exercises, with historical statuses preserved where they remain accurate.
- **Evidence:** [FRAMEWORK-ADV-001](../adversarial-reviews/FRAMEWORK-ADV-001.md) records the bounded self-review exercise; [FRAMEWORK-ADV-002](../adversarial-reviews/FRAMEWORK-ADV-002.md) records the independent conformance gate and rerun.
- **State:** Complete — manual capability, bounded exercise, and independent conformance review are recorded; FRAMEWORK-ADV-002 passed after the workflow, template, and capability clarified lifecycle-status versus gate-result fields.

### FW-TASK-004 — Specify CAP-003 general AI engineering execution

- **Goal:** Make implementation from approved SDD work agent-executable across app stacks without embedding app-specific assumptions.
- **Requirements:** FR-FW-003, FR-FW-006, FR-FW-008, FR-FW-011, FR-FW-012; NFR-FW-001, NFR-FW-003.
- **Dependencies:** FW-TASK-001, FW-TASK-002.
- **Work:** Define backlog task selection, repository/context loading, branch/change scope, acceptance-criteria mapping, implementation, verification selection, code review, failure handling, status update, and user report. Reconcile the narrow current coder skill with a general framework capability; retain domain-specific execution as an optional profile rather than core behavior.
- **Acceptance criteria:**
  1. An agent can identify the selected approved task, source requirements, dependencies, and repository instructions.
  2. The workflow stops when requirements conflict, a product decision is unresolved, credentials/permissions are missing, or an acceptance criterion cannot be verified.
  3. The agent reports changed files, checks actually run, results, unresolved risk, and the next task/status update.
  4. No workflow claims all tests passed or a change is production-ready without observed evidence.
  5. CAP-003 specification names user, behavior, constraints, acceptance criteria, and evidence before implementation begins.
- **Evidence:** CAP-003 specification adversarial review and one bounded task exercise in a separate app repository.
- **State:** In progress — CAP-003 specification and execution workflow passed bounded written review in FRAMEWORK-ADV-005 v0.3; the separate-app task exercise with observed verification evidence remains.

### FW-TASK-005 — Define feasibility and architecture readiness workflow

- **Goal:** Find constraints early and produce an implementation-ready technical plan at the right point in the lifecycle.
- **Requirements:** FR-FW-004, FR-FW-005, FR-FW-008; NFR-FW-004, NFR-FW-005.
- **Dependencies:** FW-TASK-002, FW-TASK-004.
- **Work:** Separate early feasibility screening from detailed architecture. Define data/provider/legal/security/platform/cost probes before design commitments; later define system boundaries, state/data contracts, integration behavior, threat/security review, deployment shape, and technical task decomposition without defaulting to a universal stack.
- **Acceptance criteria:**
  1. Each feasibility question has an owner, evidence source, affected requirements, and dependency state.
  2. The detailed architecture workflow consumes approved specification/CX contracts and explicitly records assumptions and alternatives.
  3. Architecture review can block handoff on unresolved high-impact risks with a decision-ready report.
  4. App-specific technical selections are not written back as universal framework rules.
- **Evidence:** Feasibility checklist, architecture workflow, sample architecture decision record, and review evidence.
- **State:** In progress — the feasibility/architecture workflow passed independent written review in FRAMEWORK-ADV-005 v0.3 after fixing dependent-task status traceability. A concrete sample architecture decision record and its review evidence remain.

### FW-TASK-006 — Define verification and quality gates for implementation

- **Goal:** Specify how approved code is checked, with evidence matched to the app’s actual platforms and risks.
- **Requirements:** FR-FW-004, FR-FW-005, FR-FW-006; NFR-FW-003, NFR-FW-004, NFR-FW-005.
- **Dependencies:** FW-TASK-002, FW-TASK-004, FW-TASK-005.
- **Work:** Define task-level verification, integration checks, code review, web audit, native audit, accessibility, security/privacy, performance, responsive/adaptive, and failure-path evidence. Make tool choice conditional on the implemented target; distinguish Figma critique from code/device audits.
- **Acceptance criteria:**
  1. Every requirement has an appropriate verification method or a documented reason that validation is manual/operational.
  2. Web, Android, and iOS receive platform-appropriate evidence where in scope; visual similarity alone is not feature parity evidence.
  3. Failed checks route to a bounded fix-and-rerun or an owner decision; they cannot be hidden by a general score.
  4. The checklist never asks an agent to run unavailable checks or claim unsupported coverage.
- **Evidence:** Verification workflow, platform applicability matrix, sample gate record, and observed pilot results.
- **State:** In progress — the verification workflow passed bounded written review in FRAMEWORK-ADV-005 v0.3; the starter verification plan now contains a Web/iOS/Android applicability matrix. A project-filled matrix, sample completed gate record, and observed pilot results remain.

### FW-TASK-007 — Define release, deployment, operations, and learning workflows

- **Goal:** Close the lifecycle after implementation through a controlled release and feedback loop.
- **Requirements:** FR-FW-004, FR-FW-005, FR-FW-007, FR-FW-008, FR-FW-010; NFR-FW-004.
- **Dependencies:** FW-TASK-002, FW-TASK-004, FW-TASK-006.
- **Work:** Define release-readiness evidence, owner authorization, environment/secrets prerequisites, deployment/rollback, health checks, monitoring and alert ownership, support and incidents, cost review, user feedback, and backlog learning. Keep provider-specific details in app artifacts or provider adapters.
- **Acceptance criteria:**
  1. Release checklist includes evidence, accountable authorizer, deployment plan, health checks, rollback/recovery, and unresolved-risk disposition.
  2. Operations workflow records monitoring, support route, incident severity/ownership, response, and learning.
  3. No production deployment, permission escalation, purchase, or destructive action is implied without the required app-owner authorization.
  4. Post-launch findings can create or update linked backlog work without losing incident or decision history.
- **Evidence:** Release/operations workflow, staging rehearsal record, and completed post-release learning example.
- **State:** In progress — release/operations workflow passed bounded written review in FRAMEWORK-ADV-005 v0.3; staging rehearsal and completed post-release learning evidence remain.

### FW-TASK-008 — Build the app starter package and repository handoff

- **Goal:** Make the framework usable in a newly created application repository with low setup effort and no source-of-truth ambiguity.
- **Requirements:** FR-FW-002, FR-FW-003, FR-FW-008, FR-FW-011, FR-FW-012; NFR-FW-001, NFR-FW-002, NFR-FW-005, NFR-FW-006.
- **Dependencies:** FW-TASK-001 through FW-TASK-007; D-FW-01 and D-FW-04 when their dependent choices are needed.
- **Work:** Package templates, agent instructions, workflow entry points, tool/skill catalog, required repository labels, and initial status mechanism. Include a clean project creation/handoff guide. Decide which setup steps are generated versus performed by an agent or owner.
- **Acceptance criteria:**
  1. A new app repo can be initialized with a small set of explicit inputs and no copied content from another application.
  2. The new repo contains its canonical artifacts and actionable starting backlog with stable links and valid metadata.
  3. The owner can locate current state and next action from the repo front page/status artifact.
  4. Framework updates do not overwrite an application's accepted product artifacts without explicit migration/review.
- **Evidence:** Fresh-repository generation from an empty directory and a downloaded-source simulation without `.git`; exact file inventories and valid unique artifact IDs for both starter profiles; app-local validation; dry-run non-mutation; and non-empty-target preservation. Independent review must cover the current default and optional profile.
- **State:** In progress — the previous 21-file scaffold (including an unnecessary empty generated-output folder) and its safety behavior were independently reviewed in FRAMEWORK-ADV-006 v0.1. The revised default generates nine files with five canonical artifacts; `--include-lifecycle-records` generates 20 files with 16 unique draft artifacts. Five regression tests cover both profiles, profile-correct decision IDs, copied-helper validation, dry-run, non-empty-target refusal, and downloaded-source use without Git metadata. FRAMEWORK-ADV-007 independently passed the profile split and generated README corrections. Remaining FW-TASK-008 evidence is a full checklist of every acceptance criterion and cold-start owner usability; app initialization does not establish implementation or release readiness.

- **Execution update (2026-10-10):** Starter simplification follows the product owner's template/boilerplate direction. Keep the reusable template source as the framework product; each actual app gets its own repository as its source of truth. Supporting templates are added when lifecycle events need them instead of pre-populating empty records by default.

### FW-TASK-009 — Run a bounded end-to-end implementation pilot

- **Goal:** Prove the framework can move approved intent into reviewed code and release evidence without requiring the owner to act as the routine implementer.
- **Requirements:** FR-FW-003, FR-FW-006, FR-FW-007, FR-FW-010, FR-FW-012; NFR-FW-001, NFR-FW-003.
- **Dependencies:** FW-TASK-008; an application candidate with approved requirements and all applicable gates passed; D-FW-03.
- **Work:** Use a separate app repository to trace one small vertical slice through approved intent, requirements, adversarial review, applicable CX/architecture gates, a selected implementation task, observed verification, a reversible non-production release rehearsal, and one operations/learning record. If a candidate app is not eligible because a product gate or decision remains open, use a neutral sample app with synthetic data and no external provider, payment, account, or production deployment dependency; record the selection rationale. Keep the pilot to framework evidence: do not expand into market discovery, a full product, multi-platform feature implementation, public launch, or production operations. Choose the minimum platform needed to exercise the selected slice and map other platform checks as out of scope for this pilot with rationale; framework requirements/templates must still preserve multi-platform applicability for future app projects.
- **Acceptance criteria:**
  1. The pilot traces from one approved product requirement through design/architecture as applicable, backlog task, code change, verification, and release evidence.
  2. The owner is asked only for material decisions, access, authorization, or review—not routine coding or workflow assembly.
  3. Friction, missing templates, failed gates, and tool limitations are recorded as framework findings with dispositions.
  4. Application code and deployment artifacts remain in a separate app repository.
- **Evidence:** Pilot report with artifact links, code review, criterion-to-check results, reversible non-production release/rollback evidence, operations/learning record, owner-decision log, and retrospective. Evidence must distinguish this pilot's platform and release scope from production launch or unsupported native/platform claims.
- **State:** Ready to start — FW-TASK-008 is complete and its approved starter has been copied into the separate synthetic pilot repository. The pilot remains local-first and non-production; no cloud hosting, GitHub remote, or production access is required. The synthetic Reading Queue is only a framework exercise and carries no claim about a real product problem. Pilot design and implementation evidence remain outstanding.

### FW-TASK-010 — Adversarially review, release, and operate Framework v1

- **Goal:** Establish a finite v1 completion decision and publish a usable framework release record.
- **Requirements:** FR-FW-001 through FR-FW-013; NFR-FW-001 through NFR-FW-006.
- **Dependencies:** FW-TASK-001 through FW-TASK-009.
- **Work:** Run a complete framework review against FRAMEWORK-SPEC-001 and the app starter; resolve required findings; run the framework readiness and pilot evidence checklist; update the README and lifecycle overview; record remaining limitations and v1.1 improvements. Prepare a template-only distribution package with clean Git history under the MIT License; exclude app-specific artifacts and owner data; ask the owner to review the concrete package; publish only after explicit owner authorization.
- **Acceptance criteria:**
  1. Every in-scope requirement is linked to an artifact, workflow, tool, or pilot evidence.
  2. Every required gate has a current pass/fail status and evidence; failures are not relabeled as complete.
  3. No blocker remains without an explicit owner-accepted exception.
  4. README identifies who should use the framework, how to start a new app, where app artifacts live, and how to find the next action.
  5. The release record distinguishes “ready for application implementation” from “proven through production launch.”
  6. The published/downloadable repository has clean history, contains only approved framework materials, includes the MIT License, and does not expose application-specific or private owner data.
- **Evidence:** Framework adversarial review and rerun, v1 readiness report, version/release note, and updated README.
- **State:** In progress — local-first README and starter behavior are documented; public fork/download access and MIT License are owner-approved. Prepare a clean-history template package for owner review; explicit publication authorization is still required before anyone can access it publicly.

## Explicitly not in the v1 backlog

- Building a hosted orchestration platform or agent marketplace.
- Supporting every language, cloud, identity provider, CI service, design tool, and product category with custom automation.
- Requiring every Impeccable command on every product. Commands are selected from actual findings and target capabilities; mandatory gates remain explicit.
- Expanding a particular application's screens or code in the reusable template source.
- Moving app-specific requirements, code, credentials, or operations data into the framework repository.

## V1 completion report format

When FW-TASK-010 is complete, report only:

1. Framework version and readiness state.
2. Completed backlog IDs with links to evidence.
3. Gates passed, failed, or explicitly accepted by the owner.
4. Pilot and release-rehearsal evidence, including actual verification results.
5. Remaining limitations, open decisions, and the next version's bounded scope.

## References

- [FRAMEWORK-SPEC-001](FRAMEWORK-SPEC-001.md)
- [MISSION-001](../missions/MISSION-001.md)
- [FRAMEWORK-001](../constitution/FRAMEWORK-001.md)
- [FRAMEWORK-002](../constitution/FRAMEWORK-002.md)
- [CAP-001](../../framework/capabilities/CAP-001-artifact-management.md)
- [CAP-002](../../framework/capabilities/CAP-002-adversarial-review.md)
