---
id: FRAMEWORK-BACKLOG-001
type: framework-backlog
title: Remaining work to complete Adversarial SDD Framework v1
status: draft
version: 1.9
created: 2026-10-07
updated: 2026-10-13
related-artifacts: MISSION-001, FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-SPEC-001, ARTIFACT-CONTRACT-001, CAP-000, CAP-004, CAP-005, FRAMEWORK-ADV-007
---

# FRAMEWORK-BACKLOG-001 — Remaining work to complete Adversarial SDD Framework v1

## Purpose and status

This is the ordered backlog for finishing the reusable framework, not an application backlog. Items are sequenced by dependency and can be adjusted when evidence exposes a better order. An item is complete only when its acceptance evidence is recorded in the repository. The slide is a target-state overview; this backlog is the execution plan.

**Current framework state (updated 2026-10-11):** CAP-001 artifact management and CAP-004 app bootstrap are implemented. FW-TASK-008 starter handoff is complete after the cold-start acceptance checklist and focused fixes recorded below. CAP-004 defaults to five canonical SDD artifacts plus README, agent instructions, `.gitignore`, and the local helper; detailed lifecycle records remain available on demand. FRAMEWORK-ADV-007 independently passed the profile split and generated README review; the current five-test run also covers downloaded-source use without Git metadata. CAP-002 has an independent passing conformance review; the lifecycle/gate contract has passed independent review with a completed paper tabletop; and the CAP-003 through release/operations workflow set has passed bounded written review. FW-TASK-009 is complete for its bounded Python ping slice, with its evidence summarized in [FRAMEWORK-PILOT-001](FRAMEWORK-PILOT-001.md); this does not establish production readiness. The framework-only candidate passes its local artifact, Python, TypeScript, Vitest, coverage, and Next.js build checks. Owner direction has pulled initial server-side verification and the scheduled governance proposal forward from the deferred roadmap into active work under FW-TASK-012 and FW-TASK-014. Workflow execution and merge-protection configuration remain unverified. Clean-history clone/archive validation and owner review remain before any public distribution.

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

FW-TASK-011 and FW-TASK-013 remain proposed v2 work and are deferred until prioritized. FW-TASK-012 has been pulled forward by owner direction for its initial CI implementation; FW-TASK-014 tracks the companion scheduled governance proposal. Remaining deferred work is not a v1 completion or private-use release blocker unless it is separately promoted.

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
  4. A controlled test change that reduces branch coverage to 95% fails the coverage check, while the passing baseline meets exactly 100% across all configured dimensions.
  5. A test pull request demonstrates non-zero CI failure for each negative case, and repository settings demonstrate that the relevant status check is required before merge.
  6. The workflow uses least-privilege permissions, pinned or otherwise controlled actions, and does not expose secrets to untrusted pull-request code.
- **Evidence:** Workflow run links for passing and failing fixtures, coverage reports, and verified required-status/branch-protection configuration.
- **State:** **In progress — pulled forward by owner direction (2026-10-11).** The consolidated workflow, reviewable framework artifact manifest, and bounded RFC 2119 requirement-table linter are implemented and pushed on a review branch. Hosted positive and negative behavior is evidenced below. GitHub reports the default `main` branch as unprotected, so these checks currently run but are not enforced as merge blockers. FW-TASK-012 remains open pending an owner decision on required-check and pull-request protection.
- **Execution evidence (2026-10-12, local negative-fixture rehearsal):** From the clean baseline of the current temporary fixture copies, `python3 scripts/artifacts.py validate` returned exit code 0 and `Validated 33 artifact(s).` Removing `docs/constitution/FRAMEWORK-001.md` from an isolated repository copy returned exit code 0 and `Validated 32 artifact(s).`; therefore, the current artifact validator does **not** enforce the required-artifact inventory in acceptance criterion 2. Removing the `type` front-matter field from that artifact in a separate isolated copy returned exit code 1 with `ERROR docs/constitution/FRAMEWORK-001.md: missing required field 'type'`, confirming actionable rejection for malformed metadata. The copies were created under temporary directories and discarded; tracked repository documents were not changed by these fixtures.
- **Execution evidence (2026-10-12, coverage):** Runtime was Node.js `v22.23.3`, npm `12.1.0`, Vitest `5.0.0`. The unmodified repository command `npm run test:coverage` passed: 30 tests, statements `55/55 (100%)`, branches `57/57 (100%)`, functions `10/10 (100%)`, and lines `52/52 (100%)`. In an isolated temporary copy, a first attempt to remove one existing test case still produced 100% coverage, showing that the behavior remained covered by other tests. A separate synthetic fixture added 20 ternary branches and tests that covered both outcomes for 18 branches and only one outcome for two; the fixture source reported 95% branch coverage. `npm run test:coverage` exited 1 as configured: aggregate branch coverage `95/97 (97.93%)`, with the fixture at `19/20 (95%)`; statements `77/77 (100%)`, functions `11/11 (100%)`, and lines `74/74 (100%)`. This verifies local threshold enforcement for a 95% scoped fixture, not a hosted CI run or a PR result. All temporary fixture files were discarded.
- **Execution evidence (2026-10-13, artifact contract and RFC 2119 lint):** Added [ARTIFACT-CONTRACT-001](ARTIFACT-CONTRACT-001.json), a reviewable JSON inventory of the framework's required starter paths and stable-ID artifacts, plus the two named framework requirement tables. The contract retains the app validator's five canonical root documents and scopes normative checks to configured requirement tables. `tests/test_artifacts.py` ran 9 tests successfully, covering the current framework manifest, a missing required framework artifact, fail-closed behavior when the manifest is missing, valid uppercase RFC 2119 rows, absent and lowercase-only keyword rejection, requirement-kind ID mismatch, missing acceptance evidence, and a missing app canonical file. `python3 scripts/artifacts.py validate` reported `Validated 33 artifact(s).` The lint verifies table structure, stable requirement IDs, a non-empty requirement and acceptance-evidence cell, and an exact uppercase keyword in each requirement cell; it intentionally does not lint ordinary prose or assess semantic quality/testability.
- **Execution evidence (2026-10-13, local checks):** `python3 -m unittest discover -s tests -v` passed all 14 Python tests. `python3 -m json.tool docs/framework/ARTIFACT-CONTRACT-001.json` succeeded. `npm ci` succeeded with 195 packages installed; npm reported install scripts blocked for `esbuild` and `fsevents` under the local npm policy. With that clean install and no generated `.next` directory, `npm run typecheck` exited 0. `npm test` passed 30 tests. `npm run test:coverage` passed with statements `55/55`, branches `57/57`, functions `10/10`, and lines `52/52` (100% in each configured TypeScript source dimension). The pre-existing `node_modules` and `.next` directories were restored after the isolated clean-install check. `git diff --check` passed. `actionlint` is unavailable in this environment; workflow YAML has not been checked by that tool.
- **Execution evidence (2026-10-13, isolated hosted-rehearsal preparation):** A clean scratch worktree based on the current GitHub `main` tree contained only the FW-TASK-012 changes. It validated 32 framework artifacts and passed all 14 Python tests. A missing `docs/constitution/FRAMEWORK-001.md` fixture made artifact validation exit 1 with a file-specific missing-required-artifact error, then the original file was restored byte-for-byte and validation passed. A temporary TypeScript fixture reported 95% branch coverage for its own module and reduced aggregate coverage to `95/97 (97.93%)`; `npm run test:coverage` exited 1 against the 100% threshold. After removing the fixture, coverage passed again at 100%: statements `55/55`, branches `57/57`, functions `10/10`, lines `52/52`. These are isolated local rehearsals, not GitHub Actions runs.
- **GitHub read-only observations (2026-10-13):** The repository is private, GitHub reported `main` as the default branch, and no open pull requests were returned. The branch listing marked `main` as `protected: false`. The detailed branch-protection endpoint returned HTTP 403 `Resource not accessible by integration`; the repository-rulesets endpoint returned HTTP 403 stating that GitHub Pro or a public repository is required. Therefore required status checks, bypass rules, and any merge-blocking configuration could not be verified. No repository setting was changed.
- **Hosted GitHub Actions evidence (2026-10-13):** Clean draft PR [#5](https://github.com/naelmusleh/adversarial-sdd-boilerplate/pull/5), head `c4135147643848ada6f46b8775b34642cbbc91fd`, passed Verify Pipeline run [38432801456](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/38432801456): Metadata & Artifact Audit, Initializer Regression Gate, and TypeScript Static Code Analysis all concluded `success`. Missing-artifact fixture PR [#6](https://github.com/naelmusleh/adversarial-sdd-boilerplate/pull/6) failed run [38433148735](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/38433148735) at `Test required-artifact contract and normative requirement linter`; initializer and TypeScript jobs passed. The 95%-branch-coverage fixture PR [#7](https://github.com/naelmusleh/adversarial-sdd-boilerplate/pull/7) failed run [38433325076](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/38433325076) at `Enforce configured 100 percent coverage thresholds`; its metadata and initializer jobs passed. The local fixture measured 95% branch coverage for the added module while statements, functions, and lines remained 100%. Fixture PRs #6 and #7 were closed without merging after results were observed.
- **Remaining evidence / release boundary:** The hosted positive run passed all three Verify Pipeline jobs, and both hosted negative fixtures failed at their intended gates; the temporary fixture PRs were closed. The owner requires passing checks before merge, which is satisfied for the clean review PR, but `main` is reported `protected: false` and the repository settings do not currently enforce required checks. No settings were changed and the clean review PR remains unmerged. Resolve the branch-protection decision before claiming merge enforcement or completing FW-TASK-012.

### FW-TASK-013 — Polyglot AI architecture compiler specifications

- **Goal:** Define and validate language-specific execution boundaries for applications that combine web, backend, and native mobile components.
- **Requirements:** Future-version requirements to be assigned when v2 scope is opened.
- **Dependencies:** An approved multi-platform sample project contract; explicit language/toolchain applicability; a stable cross-module data contract.
- **Work:** Extend `framework/capabilities/CAP-003-ai-engineering-execution.md` with a translation and verification matrix for TypeScript, Python, and native mobile environments. Define how an agent maps requirements to independently scoped subprojects, loads only the applicable language instructions and dependency manifests, and reports cross-project interfaces. Specify a strict JSON serialization contract for inter-module telemetry, including a versioned schema, validation rules, compatibility behavior, and rejection of malformed or unknown critical fields. Keep this as a specification until a bounded compiler/initializer implementation is separately scoped; do not imply that prose instructions alone provide automated isolation.
- **Acceptance criteria:**
  1. The matrix covers TypeScript, Python, and native mobile targets with language-specific instructions, manifests, verification commands, and boundaries; platform/language assumptions are explicit.
  2. The data interface has a versioned JSON Schema (or an equally machine-checkable schema), valid and invalid fixtures, and documented compatibility behavior.
  3. A multi-platform sample initialization maps web, native mobile, and data/backend directories without copying dependencies or instructions across unrelated language environments.
  4. Automated checks detect deliberately injected cross-stack dependency or instruction leakage and pass when the fixture is isolated correctly.
  5. The capability distinguishes the specified behavior from any compiler or orchestration behavior that has not yet been implemented and verified.
- **Evidence:** Updated CAP-003, language/platform applicability matrix, versioned serialization schema and fixtures, multi-platform sample tree, and isolation-check results.
- **State:** **TODO — deferred to v2.**

### FW-TASK-014 — Weekly platform governance audit and strategic R&D proposal

- **Goal:** Establish a bounded weekly operations loop that audits locked dependencies and gathers evidence about relevant SDD, context-engineering, and multi-agent execution practices.
- **Requirements:** Future-version requirements to be assigned when the automation scope is fully evaluated.
- **Dependencies:** CAP-005 runtime and evidence boundaries; `TAVILY_API_KEY` Actions secret; GitHub Actions permissions limited to read-only collection and draft pull-request creation; append-only decision-record location; a human owner for source and proposal disposition.
- **Work:** Schedule a Sunday UTC workflow and permit manual execution from `main`; run `npm ci` and `npm audit --json`; execute the three exact CAP-005 research questions using the provider credential only in the collection step; apply deterministic source diversity, evidence, recency, promotional-language, and topic-specific lexical coverage checks against framework docs/workflows/helpers (excluding `/src`); combine dependency metrics, source links, template-tree matches/gaps, filter outcomes, and qualified `FW-TASK-XXX` candidate templates into one new run-specific report under `docs/decisions/architecture-audits/`; validate and submit that record in an updated draft PR on `automation/weekly-architecture-audit`. Never change `/src`, product logic, dependency manifests, lockfiles, prior records, canonical backlog, or repository settings. Candidate task IDs remain provisional until a maintainer reconciles and accepts them. Clearly mark unavailable sources/scanner results and preserve a non-zero workflow conclusion for findings or operational failure.
- **Acceptance criteria:**
  1. A controlled clean audit, vulnerability-found audit, and unavailable-scanner case produce the specified status behavior and preserve accurate evidence.
  2. Each of the three exact research questions is attempted; complete, partial, missing-credential, malformed-response, and no-qualified-source outcomes are distinguishable and never misreported as equivalent.
  3. A qualifying task draft requires all three sweeps complete, at least three usable sources across two domains, qualifying primary-source evidence, independent non-promotional corroboration, and an unobserved topic-specific template coverage probe; the report lists matching paths and missing markers while labeling this check lexical rather than semantic. Unqualified trends produce no task draft and include the reason.
  4. The single generated report includes audit metrics, query/source provenance, bounded excerpts, per-source scores/reasons, candidate acceptance criteria, source revision, workflow run ID, and run attempt; it passes the artifact validator.
  5. A controlled PR run creates or updates a draft PR on the fixed branch `automation/weekly-architecture-audit` containing only the new report. No previous record, canonical backlog item, `/src` file, product file, dependency file, or workflow is changed by the daemon.
  6. Candidate FW tasks remain noncanonical proposals, require human source verification and ID reconciliation, and are never auto-appended to the framework backlog or auto-merged.
  7. The workflow uses least-privilege permissions, limits the external API credential to the collector step, treats retrieved content as untrusted data, and documents that dependency/web research does not constitute a full architecture or production-readiness assessment.
- **Evidence:** CAP-005; workflow run links covering clean, findings, unavailable, and filter outcomes; validated combined report; PR diff/path checks; and maintainer review/disposition.
- **State:** **In progress — owner direction (2026-10-11).** Workflow, collector, and capability contract are implemented locally. Hosted schedule, Tavily secret configuration, collector/filter scenario evidence, dependency scanner states, fixed-branch draft PR behavior, event-trigger limits, and append-only negative-case evidence remain unverified.

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
