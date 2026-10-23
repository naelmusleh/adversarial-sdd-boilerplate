Warning: truncated output (original token count: 46745)
Total output lines: 753

---
id: FRAMEWORK-BACKLOG-001
type: framework-backlog
title: Remaining work to complete Adversarial SDD Framework v1
status: draft
version: 4.8
created: 2026-10-07
updated: 2026-10-22
related-artifacts: MISSION-001, FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-SPEC-001, ARTIFACT-CONTRACT-001, CAP-000, CAP-004, CAP-005, FRAMEWORK-ADV-007, FRAMEWORK-ADV-008, FRAMEWORK-ADV-009, FRAMEWORK-ADV-014, FRAMEWORK-ADV-015, FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-GATE-TRACEABILITY-001, FRAMEWORK-EXERCISE-003, FRAMEWORK-EXERCISE-004, FRAMEWORK-EXERCISE-005, FRAMEWORK-EXERCISE-006, FRAMEWORK-EXERCISE-007, WORKFLOW-DISCOVERY-001, WORKFLOW-FEASIBILITY-001, WORKFLOW-AI-ENGINEERING-001, DECISION-LOG-001, DECISION-022, DECISION-023, DECISION-024, DECISION-025
---

# FRAMEWORK-BACKLOG-001 — Remaining work to complete Adversarial SDD Framework v1

## Purpose and status

This is the ordered backlog for finishing the reusable framework, not an application backlog. Items are sequenced by dependency and can be adjusted when evidence exposes a better order. An item is complete only when its acceptance evidence is recorded in the repository. The slide is a target-state overview; this backlog is the execution plan.

**Current framework state (updated 2026-10-11):** CAP-001 artifact management and CAP-004 app bootstrap are implemented. FW-TASK-008 starter handoff is complete after the cold-start acceptance checklist and focused fixes recorded below. CAP-004 defaults to five canonical SDD artifacts plus README, agent instructions, `.gitignore`, and the local helper; detailed lifecycle records remain available on demand. FRAMEWORK-ADV-007 independently passed the profile split and generated README review; the current five-test run also covers downloaded-source use without Git metadata. CAP-002 has an independent passing conformance review; the lifecycle/gate contract has passed independent review with a completed paper tabletop; and the CAP-003 through release/operations workflow set has passed bounded written review. FW-TASK-009 is complete for its bounded Python ping slice, with its evidence summarized in [FRAMEWORK-PILOT-001](FRAMEWORK-PILOT-001.md); this does not establish production readiness. The framework-only candidate passes its local artifact, Python, TypeScript, Vitest, coverage, and Next.js build checks. Owner direction has pulled initial server-side verification and the scheduled governance proposal forward from the deferred roadmap into active work under FW-TASK-012 and FW-TASK-014. Workflow execution and merge-protection configuration remain unverified. Clean-history clone/archive validation and owner review remain before any public distribution.

**Execution update (2026-10-20):** Completed FW-TASK-006 by adding the project-filled Python pilot platform matrix and criterion-to-check G-IMPL example in [FRAMEWORK-EXAMPLE-001](FRAMEWORK-EXAMPLE-001-python-pilot-gimpl.md), and tightening the workflow, gate catalog, and starter verification-plan contract. Evidence is limited to the recorded terminal-only pilot slice; source pilot commands were not rerun while preparing the example, and no web, iOS, or Android quality claim is made. Initial worktree validation reported `Validated 33 artifact(s).`; no application or production code changed.

**Execution update (2026-10-21):** Refreshed the owner-prioritized v2 backlog after reviewing [Fadi88/one-man-startup](https://github.com/Fadi88/one-man-startup), [ai-driven-dev/framework](https://github.com/ai-driven-dev/framework), the owner's five-part proposal, and the [awesome AI-driven development catalog](https://github.com/eltociear/awesome-AI-driven-development). Expanded FW-TASK-013 for a stack-neutral governance core and app profiles; added FW-TASK-026 through FW-TASK-029 for transactional lifecycle transitions, scoped context projections, risk-scaled quality/traceability, and signed hosted evidence receipts; aligned FW-TASK-024 to consume the quality policy. Added FW-TASK-030 and FW-TASK-031 for optional isolated execution and bounded agent-run budgets. The proposals explicitly reject false claims about local write prevention, symlink isolation, cryptographic truth, or automatic code deletion. FW-TASK-020 remains in progress pending full bypass coverage and final independent review; hosted app attestation has since been issued and recorded in FRAMEWORK-ADV-013.

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

**Owner-prioritized governance-hardening sequence (added 2026-10-20):** Complete the outstanding verification/review for FW-TASK-015 and FW-TASK-016 first; then execute FW-TASK-017 (normative ten-gate contract) → FW-TASK-018 (fail-closed app validator) → FW-TASK-019 (CI, revision, and release evidence binding) → FW-TASK-020 (separate-app adversarial bypass pilot). FW-TASK-012's existing framework CI is an input to FW-TASK-019 and must be extended where needed, not duplicated. These planned tasks do not mean the current framework already enforces every gate.

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
- **Evidence:** [CAP-004 — App Repository Bootstrap](../../framework/capabilities/CAP-004-app-repository-bootstrap.md), generated sample behavior, and independent review [FRAMEWORK-ADV-003](../adversarial-reviews/FRAMEWORK-ADV-003.md).
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
- **State:** Complete — the verification workflow and starter matrix passed bounded written review; [FRAMEWORK-EXAMPLE-001](FRAMEWORK-EXAMPLE-001-python-pilot-gimpl.md) provides a project-filled platform applicability matrix and a completed, evidence-linked G-IMPL example for the approved Python pilot slice. Web, iOS, and Android are explicitly out of scope for that CLI slice; the example does not claim those platforms passed or establish a universal coverage threshold. The underlying pilot evidence and its limits remain in [FRAMEWORK-PILOT-001](FRAMEWORK-PILOT-001.md).

- **Execution update (2026-10-11, initial clarification):** Clarified the app-specific required-check to G-IMPL evidence contract in `workflows/engineering-quality-gates.md`, `docs/framework/GATE-CATALOG-001.md`, and `docs/templates/app-project/verification-plan.md.template`. The contract separates the template's Vitest-only TypeScript/TSX 100% thresholds from the Python `unittest` suite, which has no configured coverage threshold, and from the separate pilot's module-scoped metrics in FRAMEWORK-PILOT-001. Each app must state its own required checks, coverage scope/policy if applicable, revision, pass condition, and evidence links. This clarification alone did not complete FW-TASK-006; at that point, the project-filled platform matrix and sample completed gate record remained outstanding.

- **Execution update (2026-10-11):** Completed the remaining FW-TASK-006 evidence using the Python pilot selected by the owner. FRAMEWORK-EXAMPLE-001 transcribes `PILOT-VERIFICATION-001`, `PILOT-VERIFY-002`, `PILOT-GATE-PING-IMPL-001`, and `PILOT-PING-REVIEW-001`, separates the terminal target from out-of-scope Web/iOS/Android surfaces, maps task criteria to checks and observed evidence, identifies the tested code as an uncommitted working tree, and distinguishes APP-TASK-003's local G-IMPL result from its separate G-RELEASE rehearsal. The source pilot check outputs were not rerun while preparing this example; their provenance and limits are explicit in FRAMEWORK-EXAMPLE-001.

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
- **Dependencies:** The canonical artifact model, lifecycle/gate contract, adversarial review procedure, and written feasibility, engineering, verification, and operations workflows from FW-TASK-001 through FW-TASK-007; D-FW-01 and D-FW-04 where their dependent choices apply. The remaining implementation/release/operations demonstrations for FW-TASK-004 through FW-TASK-007 are pilot evidence tracked by FW-TASK-009 and are not prerequisites for initializing or navigating the starter.
- **Work:** Package templates, agent instructions, workflow entry points, tool/skill catalog, required repository labels, and initial status mechanism. Include a clean project creation/handoff guide. Decide which setup steps are generated versus performed by an agent or owner.
- **Acceptance criteria:**
  1. A new app repo can be initialized with a small set of explicit inputs and no copied content from another application.
  2. The new repo contains its canonical artifacts and actionable starting backlog with stable links and valid metadata.
  3. The owner can locate current state and next action from the repo front page/status artifact.
  4. Framework updates do not overwrite an application's accepted product artifacts without explicit migration/review.
- **Evidence:** Fresh-repository generation from an empty directory and a downloaded-source simulation without `.git`; exact file inventories and valid unique artifact IDs for both starter profiles; app-local validation; dry-run non-mutation; and non-empty-target preservation. Independent review must cover the current default and optional profile.
- **State: [COMPLETE]** — the starter handoff and cold-start usability criteria below passed on 2026-10-11. Completion means a new app can be initialized, validated, and handed to the documented first product action. It does not claim that the app has passed product gates or that the framework has completed its implementation/release pilot.

#### Onboarding Acceptance Checklist — [COMPLETE] (2026-10-11)

Validation target: a fresh app named `Cold Start Verification App`, prefix `COLDSTART`, generated under a disposable temporary directory from the template repository. The generated app folder was verification output, not a second source of truth. The template checkout was on `main` at `4b0132e`, tracking `origin/main`. The checkout also contained pre-existing `package.json` changes and an untracked `package-lock.json`; these were left untouched.

| CAP-000 check | Result | Verification evidence |
| --- | --- | --- |
| 1. Identify the checkout and preserve existing work. | **PASS** | Confirmed the template root, branch, remote-tracking branch, and working-tree status before validation. The initializer wrote only to the new temporary app target; unrelated package changes were preserved. A generated app intentionally has no Git history yet; the README tells the owner to review files, then initialize Git and create its first commit. |
| 2. Read repository instructions and canonical app state. | **PASS** | Read the template README and CAP-000. The generated app contains `README.md`, `AGENTS.md`, `mission.md`, `constitution.md`, `specification.md`, `design.md`, and `backlog.md`. Read those generated files; all start in draft and make no claim that a product decision or gate is approved. |
| 3. Parse applicable framework documentation. | **PASS** | Read `docs/framework/GATE-CATALOG-001.md`, `docs/framework/TOOL-CATALOG-001.md`, and `workflows/product-discovery.md`. After following the README's runtime/docs copy step, verified the app-local gate catalog, tool catalog, workflow set, templates, and CAP-000 through CAP-004 files are present. Corrected stale links in the root README, CAP-004, and product-discovery workflow that pointed to a missing `docs/templates/app-project/README.md`. |
| 4. Inspect product, data, and database contracts. | **PASS — blocker behavior verified by inspection** | The generated specification explicitly requires domain/data ownership, retention/deletion, integrations, permissions, and failure behavior to be decided. Those sections are intentionally unfilled in a new app; the agent must record missing contracts as blockers and must not invent a schema, provider, or authorization policy. |
| 5. Preserve design-system constraints. | **PASS — no product design is implied** | The generated `design.md` reserves the canonical product experience, journey inventory, cross-surface matrix, status/content contract, brand system, and design decisions. CAP-000 requires applicable Material 3 and Apple HIG review and warns that neutral starter tokens do not approve a product design. The starter does not pre-fill product-specific tokens or claim design approval. |
| 6. Establish objective project state. | **PASS** | In the generated app, `python3 scripts/artifacts.py list` found 12 artifacts after the documented framework copy step, including all five `COLDSTART` canonical artifacts; `python3 scripts/artifacts.py validate` reported `Validated 12 artifact(s).` In the template checkout, the corresponding commands listed and validated 29 artifacts. A fresh app has no Git history before its instructed initial commit, which is explicitly a setup state rather than missing evidence. |
| 7. Select one authorized next action and confirm its gate/dependencies. | **PASS** | The generated README and backlog agree: the owner gives the agent the app idea, intended user, problem evidence, desired outcome, and known constraints; the agent drafts `mission.md` and leads `workflows/product-discovery.md` toward G-INTENT/G-REQ. The generated backlog says no gate has passed. There is no approved implementation task yet, so coding is not the next permitted action. The README and CAP-004 were revised to make the owner input and agent action explicit. |
| 8. Execute the selected application task and update its records. | **NOT APPLICABLE AT BOOTSTRAP** | No product intent was supplied for the disposable app, so the next action is owner-led mission framing. The bootstrap contract correctly prohibits inventing app behavior or starting implementation before that input and the required gates. Durable app records are updated when the owner supplies intent and work begins. |
| 9. Verify and report actual outcomes and remaining risks. | **PASS** | The initializer reported nine created files. The app-local helper listed and validated the generated SDD artifacts. This entry records exact checks, outputs, setup limits, and the next allowed action. The successful structural validator is not represented as a product gate or implementation proof. |

**Starter-package acceptance evidence:**

1. Fresh empty-target generation produced exactly nine files: five canonical SDD documents, `README.md`, `AGENTS.md`, `.gitignore`, and `scripts/artifacts.py`. The generated README and backlog were inspected; both identify owner-provided product context as the immediate input and agent-led mission/discovery as the next action. The README links to discovery guidance.
2. The five initializer regression tests passed: lean profile/file inventory and five valid draft artifacts; optional profile/file inventory and 16 valid draft artifacts; dry-run creates no target; a non-empty target and its sentinel file are preserved; and a downloaded-source simulation initializes successfully without `.git` metadata.
3. The downloaded-source test found a stale fallback URL naming the previous repository. Updated `scripts/init_app_project.py` to use `https://github.com/naelmusleh/adversarial-sdd-boilerplate` and changed the regression assertion. Also changed the generated README and backlog to ask the owner for app context and have the agent draft the project documents, consistent with `WORKFLOW-DISCOVERY-001`. The five-test suite passed after these corrections.
4. `python3 scripts/artifacts.py validate` passed in the template checkout with `Validated 29 artifact(s).`; the generated app helper passed with `Validated 12 artifact(s).` after framework docs were copied. `git diff --check` passed.
5. FRAMEWORK-ADV-007 v0.1 independently passed its bounded nine-file/20-file profile and generated-README review. That review predates the fallback-URL and link corrections recorded here; today's regression run verifies the URL correction. No claim is made that the reviewer reran the newly corrected links.

**Cold-start conclusion:** a new engineer can locate project status and the exact next action from the app repository without chat history. The next action is product discovery with owner input, not an implementation task. CAP-000 remains explicit that unresolved product/data/security decisions block dependent work. FW-TASK-009 remains responsible for proving an approved app requirement through implementation, observed verification, reversible non-production release rehearsal, and operations/learning evidence; FW-TASK-010 remains the final framework readiness/release review.

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
- **State:** **Complete for the approved one-slice scope** — a separate local Python ping slice was traced through scoped requirements, feasibility, journey coverage, CX, architecture, implementation, independent code review, measured coverage, reversible local release rehearsal, and operations/learning records. [FRAMEWORK-PILOT-001](FRAMEWORK-PILOT-001.md) preserves the observed metrics and scope limits. This does not complete the sample queue application, validate a real product problem, prove Web/iOS/Android quality, or claim production readiness.

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
- **State:** **Complete for private v1 use.** The verified framework-only MIT candidate was merged to the private repository's `main` branch through [PR #1](https://github.com/naelmusleh/adversarial-sdd-boilerplate/pull/1) at `f9f8f28c20559a9bb5f9ef859a9b11fa1feac6fa`. GitHub Actions artifact validation passed; local checks passed for five Python tests, typecheck, 30 Vitest tests, 100% coverage, and the Next.js production build. The owner deferred public distribution until after using the template to launch a couple of applications. See [FRAMEWORK-READINESS-001](FRAMEWORK-READINESS-001.md). The unused `tree` and `underscore` dependencies have been removed.

## Deferred roadmap — v2 candidates

FW-TASK-011 and FW-TASK-013 remain proposed v2 work and are deferred until prioritized. FW-TASK-012 has been pulled forward by owner direction for its initial CI implementation; FW-TASK-014 tracks the companion scheduled governance proposal. FW-TASK-017 through FW-TASK-020 are a newly owner-prioritized governance-hardening sequence, not a claim of current enforcement; execution is planned after outstanding FW-TASK-015/016 verification and review. Other deferred work is not a v1 completion or private-use release blocker unless it is separately promoted.

### FW-TASK-011 — Process velocity telemetry and metrics tracker

- **Goal:** Measure framework setup and delivery efficiency from reproducible evidence across application initializations.
- **Requirements:** Future-version requirements to be assigned when v2 scope is opened.
- **Dependencies:** A defined manual-setup baseline; an agreed event and retention model; a decision about whether measurements remain local to each template checkout or are deliberately aggregated.
- **Work:** Add a versioned schema at `docs/framework/METRICS-LEDGER.json` for `time_to_scaffold_seconds`, `defect_escape_count`, and `agent_autonomy_steps`. Define each metric, unit, start/end event, provenance, and missing-data behavior. Instrument `scripts/init_app_project.py` to record the initialization start timestamp and a completed scaffold event with elapsed time. Keep measurements evidence-based: derive elapsed time from recorded timestamps, count escaped defects only from linked defect records and a declared observation window, and derive autonomy steps from recorded workflow checkpoints rather than an agent's unsupported estimate. Do not collect credentials, personal data, or application content in the ledger.
- **Acceptance criteria:**
  1. The JSON schema validates ledger entries and rejects missing, malformed, or internally inconsistent timestamps and metric values.
  2. A controlled fresh-project initialization writes a start event and a completion entry with a measurable `time_to_scaffold_seconds` value.
  3. The record identifies the script/template revision and the evidence source for each metric; unavailable metrics are represented explicitly rather than as zero.
  4. A documented manual baseline uses the same start/end definitions and artifact scope as the automated run.
  5. The measured comparison reports the observed setup-time ratio and limitations; it does not claim velocity compression from estimates or incomparable baselines.
  6. Tests cover successful recording, interrupted initialization, malformed ledger data, and repeat runs without corrupting prior entries.
- **Evidence:** Schema validation, controlled initialization log, resulting ledger entry, test results, and a reproducible comparison against the documented manual baseline.
- **State:** **TODO — deferred to v2.**

### FW-TASK-012 — Automated GitHub Actions gate linting matrix

- **Goal:** Enforce selected, machine-checkable SDD artifact and code-quality requirements on the GitHub server for pull requests.
- **Requirements:** Future-version requirements to be assigned when v2 scope is opened.
- **Dependencies:** A finalized machine-readable artifact contract; test and coverage scope; repository branch-protection configuration and an authorized owner to make the CI check required.
- **Work:** Implement `.github/workflows/verify-pipeline.yml` as the consolidated pull-request/push gate for artifact metadata, initializer regressions, strict TypeScript compilation, Vitest, and the repository's configured 100% coverage thresholds. Separately add a bounded RFC 2119 metadata/language linter only after its machine-checkable scope and rules are specified. Document and verify the required status-check, pull-request, bypass, and branch-protection settings because workflow YAML alone does not block merges. Keep any CI-generated PR handling consistent with GitHub's `GITHUB_TOKEN` workflow-event restrictions.
- **Acceptance criteria:**
  1. The workflow runs on pushes and pull requests targeting `main` and reports artifact-contract, initializer, typecheck, unit-test, and coverage results as distinct checks.
  2. Missing required artifacts or invalid required metadata fail the workflow with actionable file-level diagnostics.
  3. A controlled fixture with an invalid or missing normative requirement fails the language check; valid normative statements pass under the documented rule.
  4. A controlled test change that reduces branch coverage to 95% fails the coverage check, while the passing baseline meets exactly 100% across all configured dime…26745 tokens truncated…d distinguishes ordinary test fixtures from real-data operations.
  2. A rehearsal proves the selected target changed as intended, records before/after counts or equivalent scope evidence, checks unaffected data according to the declared verification method, and returns a machine-readable outcome with differences.
  3. A failed or partial proof causes a safe stop and documented undo; undo itself is recorded and its result is read back.
  4. Tests cover wrong target selection, duplicate/replayed change IDs, partial application, journal failure, changed unrelated records, failed undo, and sensitive-data redaction.
  5. Large-data limitations are explicit and prevent unsupported “all rows verified” claims; the app owner approves any residual verification limit before production use.
  6. The release/operations record links the migration artifact digest, tested source revision, rehearsal evidence, backup/recovery proof where applicable, operator, and specific owner authorization.
- **Evidence:** Stack-neutral procedure, app adapter contract, disposable data rehearsal, failure/undo fixtures, security review of evidence handling, and G-RELEASE linkage test.
- **State:** **TODO — proposed v2; activate only for app profiles with persistent user/business data writes.**

### FW-TASK-026 — Enforce lifecycle transitions through a transactional gate runner

- **Priority:** P1 — closes the gap between a documented lifecycle and a workflow that can reject illegal transitions.
- **Goal:** Provide a deterministic command-line runner that reads the versioned gate contract, computes permitted next actions, validates transition requests, and records append-only state tied to exact repository and artifact revisions.
- **Requirements:** FR-FW-019, FR-FW-020, and FR-FW-021, approved for this bounded scope by DECISION-021.
- **Dependencies:** FW-TASK-017 approved transition contract; FW-TASK-018 validator and complete gate-specific fixtures; FW-TASK-019 CI evidence binding. Reuse these contracts; do not create a second policy source.
- **Work:** Implement an explicit DAG transition planner with prerequisite checks, upstream evidence invalidation, transition authorization, rerun/supersession links, and deterministic diagnostics. Treat validated gate records as durable source of truth; any `.sdd_state` is a regenerable cache, not an encrypted authority. Encryption without a key owner, recovery model, and threat model is not a security control. Use atomic writes and locking for concurrent updates, detect stale source revisions, and preserve append-only history. A local pre-commit hook can reject prohibited staged paths but cannot prevent arbitrary writes, hook bypass, or direct tool access; required CI and repository rules must enforce merge eligibility. Represent adversarial critique as a separately invoked review run with frozen inputs and structured findings; do not embed an opaque network/API LLM call in the deterministic validator or automatically pass a gate based on model output.
- **Acceptance criteria:**
  1. A machine-readable transition table defines every legal/illegal transition, prerequisite, authorized actor, invalidation effect, and next permitted action for the versioned gate contract.
  2. The runner rejects passing a gate without required evidence and rejects downstream transitions when prerequisites are failed, blocked, stale, or absent; all ten gate routes have positive and negative fixtures.
  3. A source/scope change makes affected evidence stale under exact revision rules; reruns append or supersede records without rewriting history.
  4. Concurrent updates, interrupted writes, malformed cache state, lock contention, and stale-run attempts recover or fail safely without partial state corruption; authoritative state is reconstructible from validated records.
  5. Hook tests show prohibited staged changes are rejected locally, while documentation states that hooks do not stop writes or bypasses; a hosted required-check rehearsal proves invalid transition evidence cannot merge when repository policy is configured.
  6. Review-run records bind reviewer/mode, frozen inputs, contract version, findings, dispositions, and rerun identity; the runner distinguishes model critique from verified CI evidence and owner authorization.
  7. No API credential is required by the core validator; any optional review provider uses an explicitly configured, separately permissioned adapter and remains advisory until accepted under the review contract.
- **Evidence:** Versioned transition table, runner/cache schema, ten-gate transition fixtures, concurrency/interruption tests, local-hook and hosted-policy rehearsal, independent reliability/security review, and exact-revision verification record.
- **State:** **COMPLETE — owner approved bounded FW-TASK-026 v2 scope and FR-FW-019 through FR-FW-021 on 2026-10-21 (DECISION-021); active gate G-IMPL.** All seven acceptance criteria have implementation, fixture, hosted rehearsal, independent review, and exact-descendant verification evidence recorded below and in FRAMEWORK-ADV-014. Run `39715836630` passed all three required jobs on `4a00e0a3f7853fd373777d2e25621f1e15d37731`, a documentation-only descendant of implementation/evidence SHA `f2ca403`. Scope excludes FW-TASK-027 and other v2 proposals; no change to app lock compatibility or gate contract semantics is authorized without a separately versioned decision.
- **Implementation checkpoint (2026-10-22, revision `a6e90a65057e87f27b1a7a61b963b09893c3495c`):** Added `gate plan`/`gate append`, atomic create-only writes under an interprocess lock, exact prerequisite record links, source revision checks, a separate frozen-input advisory review schema/append path, and a staged-record guard. Local verification passed: focused runner tests (15), full Python suite (130), `Validated 51 artifact(s).`, TypeScript typecheck, Vitest (30), configured statement/branch/function/line coverage (100%), production build, and `git diff --check`. Commit was pushed to `origin/codex/v2-backlog-roadmap`; Verify Pipeline run [39710112306](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39710112306), attempt 1, event `push`, completed successfully on the exact SHA with all three jobs passing. Independent review [FRAMEWORK-ADV-014](../adversarial-reviews/FRAMEWORK-ADV-014.md) confirms source/symlink/atomicity fixes but returns **BLOCK**: no accepted positive append routes are shown for G-SETUP through G-OPERATE, and hosted policy rehearsal is unverified because branch-protection read returned HTTP 403. Keep task IN PROGRESS. No contract migration, merge, or deployment is claimed.
- **Route-coverage follow-up (2026-10-22, revision `591847987a15dff30c4b6501b4296648995252ae`):** Added a test-only accepted `not-applicable` record chain through all ten gates plus a negative prerequisite-in-progress check at each downstream transition. Local full suite passed (131 tests) and artifact validation reported 52 artifacts. Independent reviewer `/root/fw021_review` accepted this as closing ADV-014-01 for runner-plumbing coverage only; the synthetic fixtures do not establish application applicability or PASS. At the checkpoint, the TypeScript/Vitest/coverage job was still running; it later completed successfully. Verify Pipeline run [39710983844](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39710983844) completed all three jobs successfully on this exact SHA. The contemporaneous independent review closed ADV-014-01 for runner-plumbing coverage only; the synthetic fixtures do not establish application applicability or PASS.
- **Hosted rules/rehearsal follow-up (2026-10-22; observed ruleset and rehearsals):** Owner supplied Settings screenshots; read-only GitHub rulesets API independently observed active `main` ruleset `25609658`, targeting `refs/heads/main`, requiring PRs and strict status checks `Metadata & Artifact Audit`, `Initializer Regression Gate`, `TypeScript Static Code Analysis`, prohibiting deletion/non-fast-forward updates, with no bypass actors and `current_user_can_bypass: never`; required approvals are zero. Disposable PR [#13](https://github.com/naelmusleh/adversarial-sdd-boilerplate/pull/13) deliberately disabled prerequisite completion; run [39712514713](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39712514713) failed the required `Metadata & Artifact Audit` while the other two required checks passed. PR #13 remained draft and conflicted with `main`, so it did not independently establish merge blocking; it was closed unmerged and its temporary branch deleted. Clean-based, ready PR [#14](https://github.com/naelmusleh/adversarial-sdd-boilerplate/pull/14) was mergeable with no conflicts, but contained only a test-only failure sentinel. Run [39715440984](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39715440984) failed only `Metadata & Artifact Audit`; the other two required checks passed. GitHub then reported `mergeable_state: blocked` for that ready, otherwise-mergeable PR. Together, the two runs show that the actual prerequisite-guard regression triggers the same required check whose failure blocks an eligible merge. PR #14 was closed unmerged and its temporary branch deleted. Independent reviewer `/root/fw021_review` reviewed the paired evidence against exact implementation/evidence revision `f2ca403e4b0af68d439b58857c359615f69e810c` and accepted criterion 5 with no remaining technical blockers. PR #13 demonstrated the real prerequisite-guard regression fails the required audit check; ready, conflict-free PR #14 demonstrated failure of that same required check blocks an otherwise mergeable PR. Both were closed unmerged and temporary branches removed. This is hosted-policy rehearsal evidence, not an authorization to merge or deploy.
- **Completion checkpoint (2026-10-22, implementation/evidence revision `f2ca403e4b0af68d439b58857c359615f69e810c`):** Independent review accepted the hosted rehearsal evidence and blocked the first closure record because run [39715592727](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39715592727) still had TypeScript Static Code Analysis in progress on `f2ca403`. A later descendant Verify Pipeline run [39715836630](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39715836630), attempt 1, event `push`, completed successfully on `4a00e0a3f7853fd373777d2e25621f1e15d37731`: Metadata & Artifact Audit, Initializer Regression Gate, and TypeScript Static Code Analysis all passed. That revision changed documentation only relative to `f2ca403`, so the same implementation was verified. Independent reviewer `/root/fw021_review` approved this corrected closure record with no remaining technical or evidence blockers. The earlier run `39715592727` on `f2ca403` remains in progress and is not claimed as passing; the full successful descendant run `39715836630` on `4a00e0a` verifies the unchanged implementation.

### FW-TASK-027 — Provide gate-scoped context projections with truthful isolation claims

- **Priority:** P2 — reduces irrelevant context and accidental role leakage while preserving files required to build and verify a task.
- **Goal:** Generate an auditable task-specific workspace view without claiming that symlinks alone create a security boundary.
- **Requirements:** FR-FW-022, FR-FW-023, and FR-FW-024, approved for this bounded scope by DECISION-022.
- **Dependencies:** FW-TASK-013 stack/profile contract; FW-TASK-017 artifact/evidence scope model; FW-TASK-026 lifecycle runner. No sandbox dependency is needed for context minimization; any later access-isolation claim requires a named OS/container sandbox and separate host/runtime evidence.
- **Work:** Define versioned per-gate context manifests listing required, optional, and excluded paths for each role. Generate an auditable temporary copy with canonical-path checks, symlink-escape rejection, cleanup/recovery behavior, and included/excluded path and source-digest records. For G-IMPL include applicable requirements/specification, architecture/security constraints, selected task, relevant source, tests, fixtures, dependency manifests, and build configuration; do not reduce context to one implementation file if that makes validation impossible. Keep required global instructions and app-owned source available. This bounded task does not enforce filesystem read/write permissions. Describe the feature as context minimization only; claim access isolation only when a separately approved OS/container sandbox demonstrably denies excluded paths.
- **Acceptance criteria:**
  1. Each gate and role has a tested path policy; missing required context blocks invocation rather than silently omitting a contract.
  2. Generated views record source revision, contract/profile revision, included/excluded paths, and hashes, and safely handle spaces, case-insensitive paths, symlinks, ignored files, and concurrent invocations.
  3. Positive/negative tests demonstrate build/test dependencies and contracts are present, unrelated material is omitted, and no path resolves outside the authorized root.
  4. A separate sandbox test attempts absolute-path, parent-traversal, symlink, and subprocess reads of excluded files; only successful denial permits an “access isolated” claim. Otherwise docs limit the claim to reducing supplied context.
  5. Context reduction is measured against a complete-context baseline on representative tasks, with no omitted acceptance criterion or increased missed-contract findings in a bounded review exercise.
  6. Projection generation and cleanup never mutate canonical app artifacts, and interrupted runs leave recoverable state.
- **Evidence:** Context manifests, generated projection snapshots, sandbox boundary tests where supported, representative build/test runs, measured context comparison, and independent review for omitted constraints and false isolation claims.
- **State:** **COMPLETE — owner approved bounded FW-TASK-027 scope and FR-FW-022 through FR-FW-024 on 2026-10-21 (DECISION-022); active gate G-IMPL.** Scope is limited to versioned per-gate/role policies, fail-closed required context, auditable source-bound projection generation/cleanup, and context-minimization-only claims. No sandbox, access-isolation claim, FW-TASK-028, or other v2 work is included. All six acceptance criteria are satisfied by the policy/manifest contract, positive and negative path/symlink/digest/concurrency/interruption fixtures, canonical-source preservation checks, the bounded two-task reduction and semantic review, independent review, and exact-revision verification. Criterion 4 is satisfied through its documented fallback: sandbox denial was not tested, and projections are described as context minimization only.
- **Work record (2026-10-21):** Selected FW-TASK-027 only after DECISION-022; approved scope and FR-FW-022–024 are recorded in FRAMEWORK-SPEC-001. Baseline repository state was clean on `codex/v2-backlog-roadmap`; `scripts/artifacts.py list` found 52 artifacts and `validate` passed. Active gate is G-IMPL. The implementation target is an opt-in stdlib projection generator driven by an explicit policy, producing a temporary copied view plus auditable manifest. Required context will fail closed; symlinks and out-of-root paths will be rejected. The projection will make no access-control claim. Acceptance evidence will map each of the six task criteria to deterministic tests, a bounded context reduction exercise, independent review, and exact-revision CI.
- **Implementation checkpoint (2026-10-22):** Added the versioned policy schema/reference example, stdlib projection generator and cleanup, implementation-workflow instructions, and [FRAMEWORK-EXERCISE-006](FRAMEWORK-EXERCISE-006-context-projection.md). Commits `1df3e4b` and `d081456` contain the initial implementation and provenance hardening. The manifest binds source revision/worktree state, selected file hashes, exact policy bytes, and generator digest; source and policy changes are rechecked before publication; byte reduction is explicitly a proxy. Cleanup walks directories with no-follow descriptors, verifies ownership and inode through descriptors, uses a recoverable quarantine name, requires a user-owned non-shared-writable output parent, and has tests for concurrent cleanup and shared-parent refusal. Independent reviewer `/root/fw021_review` returned **PASS for cleanup within the approved context-minimization scope**; same-UID hostile mutation is explicitly outside the tool's isolation claims. The focused suite passes (13); the complete Python suite passes (144) on implementation commit `d40785a95e8e22d49e53fdcca1c08e16d067fe44`; artifact validation passes (53 artifacts); compilation and whitespace checks pass. Verify Pipeline run [39720612708](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39720612708) passed all three jobs on that exact commit, and the commit was pushed to `codex/v2-backlog-roadmap`.
- **Bounded semantic-review checkpoint (2026-10-22):** Under the owner's separate approval, an independent reviewer compared FW-TASK-026 at clean revision `a6e90a65057e87f27b1a7a61b963b09893c3495c` and APP-TASK-003 at dirty worktree snapshot `61b196ec126d2bfb46614994fe627830d1b17bce` against their complete contexts. The first pass found omissions; expanded round-2 policies added the CI/release and initializer dependencies for FW-026 and the release/rollback procedure for APP-003. The second pass returned **PASS for content coverage in both paired cases**, with no material criterion or repository-local dependency gaps in the final projections. Complete-context UTF-8 proxy reductions were 42.98% (FW-026) and 32.54% (APP-003); the app case is retrospective and its dirty-tree tracked-byte baseline is incomplete. The independent reviewer confirmed criteria 4 and 5 are satisfied: criterion 4 through the no-isolation-claim fallback, and criterion 5 for this bounded two-task review. This is not a tokenizer, causal, broader statistical, or isolation result. See [FRAMEWORK-EXERCISE-006](FRAMEWORK-EXERCISE-006-context-projection.md). Documentation commits `717a495510af7fcf4f50e8fa14c87eb508df81ac` and `80b8af12ae036a3bdeeac3d630ff87d428ece29f` were pushed; Verify Pipeline run [39721922203](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39721922203) passed all three jobs on exact commit `80b8af12ae036a3bdeeac3d630ff87d428ece29f`. No sandbox denial test was run, and no access-isolation claim is made. **FW-TASK-027 is COMPLETE within DECISION-022's approved context-minimization scope.**

### FW-TASK-028 — Define risk-scaled quality thresholds and deterministic change traceability

- **Priority:** P1 — avoids both brittle universal thresholds and untraceable changes.
- **Goal:** Define a stack-neutral impact policy that strongly verifies critical behavior and links code changes to approved intent without treating coverage or AST output as proof of correctness.
- **Requirements:** Assign v2 requirement IDs only after v2 scope is opened and approved.
- **Dependencies:** FW-TASK-017 gate/evidence contract; FW-TASK-019 check manifest and trusted CI evidence; FW-TASK-013 stack profiles. The framework repository's current checks retain their policy until a separately reviewed, evidence-backed change is approved.
- **Work:** Define an app-owned impact matrix by behavior criticality, data/security consequence, failure severity, change type, and testability, with stack-specific measurement adapters. Permit strict thresholds for critical domain logic where coverage is meaningful and calibrated lower or alternative evidence for presentation/configuration code; do not adopt universal 100% or arbitrary 80% thresholds without rationale. Define test evidence beyond line counts, including branch/condition coverage where applicable and mutation/property/contract tests for high-impact invariants. Add deterministic change traceability binding a selected task and acceptance criteria to changed paths and required checks. AST analysis may flag exported symbols without trace links for review; it cannot prove product intent, force a one-method-to-one-task mapping, or automatically strip source code.
- **Acceptance criteria:**
  1. Every supported stack profile declares metrics, thresholds, exclusions, and limitations; unavailable metrics are reported as unavailable rather than passed.
  2. Critical domain, authorization, tenancy, data migration, and security changes receive stronger evidence than low-risk presentation/configuration changes; escalation cannot be avoided by misclassifying a file or task.
  3. Thresholds have documented rationale, exact scope, and failure diagnostics; lowering an established threshold requires a reviewed policy change and cannot occur through a task-level override.
  4. Fixtures demonstrate that core logic, UI/presentation, generated/configuration files, security-sensitive exports, and mixed-scope tasks receive intended checks across at least two stack profiles.
  5. Changed paths and acceptance criteria are machine-linked through review/CI metadata or a versioned trace manifest; unmapped changes fail or require an authorized, documented exception.
  6. No tool deletes or rewrites code because an AST symbol lacks a backlog entry; diagnostics identify the symbol/path and required disposition without mutating source.
  7. Adversarial tests show that high coverage with ineffective tests, trivial tests written only to inflate coverage, omitted exports, generated code, and unrelated changes do not produce misleading quality claims.
- **Evidence:** Versioned impact matrix/profile schema, stack-specific fixtures, traceability validator and negative cases, threshold rationale, mutation/property/contract evidence for selected critical invariants, and independent review of gaming and false-pass vectors.
- **State:** **TODO — proposed v2; FW-TASK-024 must consume this policy rather than define competing thresholds.**

### FW-TASK-029 — Produce verifiable signed CI evidence receipts

- **Priority:** P2 — strengthens portability and offline review of hosted gate evidence after exact-run CI binding exists.
- **Goal:** Produce a compact signed receipt that lets another verifier confirm who issued a gate-evidence claim and which repository revision, workflow, contract, checks, and artifact digests it identifies.
- **Requirements:** Assign v2 requirement IDs only after v2 scope is opened and approved.
- **Dependencies:** FW-TASK-019 completed app CI/evidence binding; FW-TASK-017 evidence types and contract versioning; FW-TASK-020's app-hosted run requirement remains independent and cannot be replaced by a locally generated receipt.
- **Work:** Define a versioned receipt schema and deterministic verifier. Bind repository identity, exact commit, gate contract and workflow revisions, provider run/attempt/event/ref, required check conclusions, applicable artifact/evidence digests, issuer identity, and verification instructions. Sign only in a trusted hosted CI identity with an explicit trust root; local receipt generation is unsigned and cannot satisfy trusted-attestation requirements. Reference durable evidence by bounded digest and provider link rather than embedding full source, diffs, secrets, personal data, or unrestricted logs. Specify keyless/key rotation or provider identity discovery, trust-root enrollment, replay/revocation/expiry behavior where supported, and transparent failure modes. Explicitly state that cryptographic integrity/authorship does not prove test adequacy, semantic correctness, reviewer independence, or production outcome.
- **Acceptance criteria:**
  1. A verifier accepts a valid receipt only when signature, trusted issuer, repository, exact commit, workflow/contract revisions, run attempt, required checks, and evidence digests all match the declared policy.
  2. Negative fixtures reject payload alteration, wrong repository/commit, stale workflow or contract, missing/failed check, unknown signer, invalid signature, replay where prohibited, and artifact-digest mismatch with specific diagnostics.
  3. A local unsigned receipt is clearly marked untrusted and cannot be upgraded to trusted status by editing JSON or copying terminal output.
  4. Receipt contents pass a privacy/data-minimization review and contain no raw source, credentials, personal data, or unrestricted command logs.
  5. Verification succeeds outside the originating CI run using documented public or repository-authorized trust material; missing trust data fails closed.
  6. Documentation limits receipt claims to provenance and integrity and preserves separate semantic review and release authorization requirements.
- **Evidence:** Versioned receipt schema, signer/trust configuration, standalone verifier, tamper/mismatch/replay fixtures, privacy review, exact hosted positive/negative runs, and independent cryptographic/provenance review.
- **State:** **TODO — proposed v2; cannot satisfy FW-TASK-020 until an actual app-hosted CI run is observed.**

### FW-TASK-030 — Define a least-privilege isolated execution adapter

- **Priority:** P2 — optional app-level defense in depth for untrusted or higher-risk agent execution; not required for every project.
- **Goal:** Specify and pilot a runner adapter that executes selected agent commands in a rootless container or equivalent OS sandbox with explicit, reviewable boundaries.
- **Requirements:** Assign v2 requirement IDs only after v2 scope is opened and approved.
- **Dependencies:** FW-TASK-013 stack/profile and runner interfaces; FW-TASK-017 evidence/provenance contract; FW-TASK-026 transition runner where execution is lifecycle-triggered; an app-approved threat model and supported host/runtime.
- **Work:** Define an optional invocation contract for command allowlists, image/runtime pinning, user identity, read/write mounts, network policy, secret injection, CPU/memory/time limits, audit records, cleanup, interruption, and failure handling. Default to no secrets and no network unless explicitly required and authorized. Keep container startup out of `init_app_project.py`; initialization may report adapter prerequisites but must not launch workloads. Treat mounts, runtime sockets, host paths, credentials, and kernel/runtime vulnerabilities as boundary risks. Describe a runner as context containment or defense in depth unless tests on the named host demonstrate denied host/excluded-path access and the documented threat model supports the stronger claim. Do not claim complete host separation.
- **Acceptance criteria:**
  1. The adapter contract is stack-neutral, versioned, optional, and documents supported host/runtime prerequisites and unsupported environments without silently falling back to unsandboxed execution.
  2. A disposable pilot proves the configured user, mount, network, secret, resource, and cleanup policies with positive and negative cases; secret material is not placed in image layers, command logs, or evidence artifacts.
  3. Adversarial cases cover parent/absolute path access, symlinks, subprocesses, runtime socket or host mount exposure, denied network, timeout/resource exhaustion, interruption, and cleanup failure; findings narrow the guarantee instead of being waived by documentation.
  4. Commands run, image/runtime identity, policy revision, source revision, exit status, and bounded logs are recorded as evidence without embedding sensitive values.
  5. The initializer remains a file-generation operation and neither starts a container nor implies that later agent commands are sandboxed.
  6. Independent security review confirms the exact guarantee and residual risks; “isolated” or “host access denied” claims are limited to observed enforcement on the tested environment.
- **Evidence:** Versioned runner contract, threat model, disposable integration pilot, positive/negative boundary results, audit/cleanup evidence, exact host/runtime details, and independent security review.
- **State:** **TODO — proposed v2; optional adapter only, pending threat model and a supported-environment pilot.**

### FW-TASK-031 — Define per-run agent budgets and stop conditions

- **Priority:** P2 — prevents unbounded automated work when a runner exposes enforceable limits; may begin as advisory where the host cannot enforce them.
- **Goal:** Bound automated agent runs with explicit resource ceilings and produce truthful stop evidence when a limit is reached.
- **Requirements:** Assign v2 requirement IDs only after v2 scope is opened and approved.
- **Dependencies:** FW-TASK-013 runner/profile interface; FW-TASK-026 lifecycle transition runner; FW-TASK-030 when hard process termination or OS resource enforcement is claimed; an explicit provider/host metering interface for spend limits.
- **Work:** Define per-run policy fields for wall-clock duration, retry/iteration count, tool invocations, subprocess/runtime resources, and spend only where authoritative metering is available. Specify when each counter starts/resets, which components enforce it, warning and stop behavior, cancellation propagation, partial-work preservation, override authority, and evidence retention. Distinguish enforced limits from advisory counters and unavailable measurements. Do not estimate monetary cost from elapsed time, repeated reads, or tool-call counts; do not claim a process was terminated unless the controlling runner observed and confirmed termination. Avoid double-counting retries across nested agents by defining scope and correlation IDs.
- **Acceptance criteria:**
  1. A versioned budget policy defines units, scope, enforcement source, reset behavior, threshold action, and unavailable-data representation for every enabled limit.
  2. Deterministic fixtures cover below-limit completion, threshold warning, exceeded retry/time/tool/resource/spend limits where supported, missing metering, nested-run accounting, cancellation failure, and partial-work preservation.
  3. Hard-stop claims are made only when a tested controller can stop the relevant process tree and observe termination; otherwise the policy reports an advisory breach and requests host-level cancellation without claiming it succeeded.
  4. Spend values come from an identified provider/host meter with currency, time window, and provenance; unknown spend remains unknown and cannot be replaced with a tool-count estimate.
  5. Budget exhaustion cannot mark a task or gate passed; it records the stop reason, last durable checkpoint, remaining verification, and next authorized action.
  6. Independent review checks retry storms, nested agents, reset/bypass attempts, meter failure, and preservation of user changes and evidence after stop.
- **Evidence:** Budget-policy schema, runner/provider adapters where available, deterministic limit fixtures, observed cancellation and checkpoint recovery, spend-meter provenance, and independent reliability review.
- **State:** **TODO — proposed v2; hard limits require a controlling runner, and spend limits require authoritative metering.**

### FW-TASK-032 — Define and review a small multi-platform sample contract

- **Priority:** P1 — prerequisite for exercising FW-TASK-013's stack profiles and cross-module contract against explicit platform applicability.
- **Goal:** Produce one small framework-only sample contract that separates a real product's confirmed browser requirements from synthetic native-platform and stack-composition fixtures.
- **Requirements:** FR-FW-028; separately authorized by the owner on 2026-10-22 in DECISION-024.
- **Dependencies:** DECISION-024; owner-confirmed Infinite Gallery v0.6 facts from the current conversation. The full app specification is not present in this framework checkout, so no additional app facts may be inferred.
- **Work:** Create FRAMEWORK-EXERCISE-007 using only the owner-confirmed Infinite Gallery browser requirements as source context. Add explicitly synthetic iOS and Android lanes and synthetic Next.js/TypeScript, FastAPI/Python, and Rust/Axum module assignments to exercise framework profile applicability and one versioned cross-module interface. Label every synthetic addition and state that it is not part of Infinite Gallery's approved scope, implementation, or evidence. Obtain a bounded independent review, correct material findings, and present the exact final revision for owner acceptance before it can satisfy FW-TASK-013's prerequisite.
- **Acceptance criteria:**
  1. The sample states its purpose and clearly separates owner-confirmed facts, framework fixture choices, unknowns, and excluded claims.
  2. The platform matrix distinguishes the approved responsive browser target (phone and desktop browsers) from synthetic-only native iOS/Android lanes; none are represented as Infinite Gallery requirements.
  3. The profile matrix maps the three FW-TASK-013 stacks to isolated synthetic modules, records versions/applicability/unsupported checks as not-yet-verified where appropriate, and makes no claim that any app stack was selected.
  4. One small, versioned cross-module data contract has concrete valid and invalid examples and explicit compatibility behavior; example values are synthetic and contain no real photos or credentials.
  5. An independent reviewer checks source provenance, product-scope leakage, platform/profile applicability, interface consistency, and whether the artifact is sufficient for FW-TASK-013; findings and disposition are recorded.
  6. The owner accepts the exact independently reviewed artifact revision before FW-TASK-013 may cite it as an approved prerequisite.
- **Evidence:** FRAMEWORK-EXERCISE-007, independent review and disposition, owner decision bound to the exact artifact revision, and `python3 scripts/artifacts.py validate`.
- **State:** **COMPLETE — bounded sample contract defined, independently reviewed, and accepted by the owner for FW-TASK-013 prerequisite use in DECISION-025.** This does not complete FW-TASK-013 or add native app scope to Infinite Gallery.
- **Work record (2026-10-22):** Baseline was clean on `codex/v2-backlog-roadmap` at `d2ec60c`. `scripts/artifacts.py list` found 53 artifacts and validation passed. Owner-authorized boundary: use Infinite Gallery only for confirmed responsive-browser facts; synthetic iOS/Android lanes and stack assignments are framework fixtures, not app decisions. Acceptance evidence is the versioned sample contract, independent review, owner acceptance of the exact revision, and artifact validation. No app code, real-photo data, provider choice, or application gate record is in scope.
- **Draft and acceptance checkpoint (2026-10-22):** Added FRAMEWORK-EXERCISE-007 v0.2 with provenance, browser/native applicability matrix, synthetic stack mapping, and a versioned metadata interface with valid/invalid examples. Independent review round 1 blocked on required-field and removal-visibility ambiguity; the correction was independently re-reviewed and passed AC-1–5 in [FRAMEWORK-ADV-015](../adversarial-reviews/FRAMEWORK-ADV-015.md). The owner accepted exact digest `sha256:2bb91ef415110b336eb653c9ffaf9b1c1822d65ccad94b7710407ecd5357c17b` through DECISION-025. Validation reported 55 artifacts and `git diff --check` passed. Commit `24e64db0555063cd0b6e21a2ba9e28fc693d4672` was pushed to `codex/v2-backlog-roadmap`; Verify Pipeline run [39886358555](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39886358555) passed all three jobs on that exact commit. Follow-up evidence-record commit `94e9c07bcd375a4256dd8436bf9d0c2cf4892a38` was pushed and Verify Pipeline run [39886473209](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39886473209) also passed all three jobs.

### Comparative review dispositions

- **Already represented; preserve and test rather than duplicate:** stable artifact/requirement/task links; explicit G-INTENT exclusions and owner approval; formal G-FEAS dependency and cost probes; bounded specialist/reviewer inputs; separate app source of truth; exact commit/push/CI/release state distinctions; residual-risk authority; artifact validation and server-side CI evidence. FW-TASK-026 through FW-TASK-028 make remaining runtime, context, and quality work explicit without claiming it is already enforced.
- **Accepted with stronger boundaries:** transactional lifecycle planning and stale-state detection; scoped context projections; stack-neutral governance with selected profiles; risk-based quality policy; signed hosted evidence receipts; state-aware onboarding; bounded feasibility spikes; explicit outcome challenge; managed-file drift diagnosis; least-privilege CI; and generated-file drift checks.
- **Not adopted as stated:** encrypting a local state file without a key/threat model; claiming pre-commit hooks or a file watcher can stop arbitrary writes; embedding an opaque LLM API critique inside the deterministic artifact validator; treating symlinks as absolute filesystem isolation; automatically stripping code that AST analysis cannot map to a backlog row; universal 100% or arbitrary 80% coverage thresholds; splitting the governance engine into a separate repository before release/ownership evidence justifies it; calling signed JSON “tamper-proof” proof of semantic truth; bundling private diffs or raw logs into broadly accessible receipts; supporting Claude, Gemini, or Copilot adapters; or allowing mandatory security, data, provenance, review, CI, and release controls to be bypassed.
- **Source and evidence boundary:** The external comparisons and owner-supplied proposal informed candidate discovery only. They are not evidence that these candidates are implemented here or that the external projects have validated them in production.

- **Reference points:** [AIDD architecture and layer boundaries](https://github.com/ai-driven-dev/framework/blob/main/docs/ARCHITECTURE.md), [AIDD onboarding loop](https://github.com/ai-driven-dev/framework/blob/main/plugins/aidd-context/skills/00-onboard/SKILL.md), [AIDD bounded spike](https://github.com/ai-driven-dev/framework/blob/main/plugins/aidd-pm/skills/05-spike/SKILL.md), [AIDD independent review and outcome challenge](https://github.com/ai-driven-dev/framework/blob/main/plugins/aidd-orchestrator/skills/01-sdlc/references/03-check.md), [AIDD managed-file CLI](https://github.com/ai-driven-dev/framework/blob/main/cli/README.md), [AIDD CI permissions and validation](https://github.com/ai-driven-dev/framework/blob/main/.github/workflows/ci.yml).

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
