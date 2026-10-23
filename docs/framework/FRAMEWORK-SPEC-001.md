---
id: FRAMEWORK-SPEC-001
type: framework-specification
title: Adversarial SDD Framework v1 scope and behavior
status: draft
version: 0.17
created: 2026-10-07
updated: 2026-10-22
related-artifacts: MISSION-001, FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-BACKLOG-001, FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-GATE-TRACEABILITY-001, FRAMEWORK-EXERCISE-007, DECISION-024, DECISION-025
---

# FRAMEWORK-SPEC-001 — Adversarial SDD Framework v1 scope and behavior

## Purpose

Define the remaining work required to make the Adversarial SDD framework a usable, reusable operating system for taking a new application from idea through launch and learning. This specification governs the framework project and does not define or implement any application's product behavior.

The horizontal lifecycle slide is a presentation of the intended destination. This specification turns that destination into bounded requirements, work, gates, and completion evidence so a project can keep moving without repeatedly rediscovering what comes next.

## Product context and outcome

The framework is for a product owner who supplies goals, decisions, and acceptance feedback while AI agents perform the documentation, design preparation, implementation, verification, and operational documentation work. The reusable repository is the **template source**: its workflows, starter files, and local tools are used to create app-specific repositories. It is not a separate framework application or service. Each actual application has its own repository and delivery lifecycle; that repository becomes the source of truth for its requirements, design, code, release history, and operations.

The v1 outcome is that a project can start with a product idea, create and maintain a reviewable SDD package, pass explicit product/CX/technical gates, implement approved work in the application's repository, and produce evidence for release and ongoing operation. The process must identify owner decisions and external access requirements early, without making the owner the routine implementer.

## Approved bounded v2 increment

On 2026-10-21, the owner approved the bounded FW-TASK-026 scope and requirements FR-FW-019 through FR-FW-021, and the bounded FW-TASK-027 scope and requirements FR-FW-022 through FR-FW-024. On 2026-10-22, the owner approved the FW-TASK-013 scope and requirements FR-FW-025 through FR-FW-027 (DECISION-023), then authorized the separate bounded FW-TASK-032 task to define and review a small multi-platform sample contract (DECISION-024). FR-FW-028 records the traceability and acceptance conditions for that task. The owner accepted FRAMEWORK-EXERCISE-007 v0.2's exact digest for use as FW-TASK-013's prerequisite in DECISION-025. Its synthetic native lanes and stack assignments remain framework fixtures only, not Infinite Gallery product decisions. These approvals do not authorize FW-TASK-028, FW-TASK-024, other proposed v2 tasks, or adoption of a draft gate-contract version.

## Current baseline

- `FRAMEWORK-001` and `FRAMEWORK-002` establish principles, artifact conventions, and the build loop.
- `CAP-001` provides a small artifact CLI for listing, creating, and structurally validating Markdown artifacts in the framework checkout and a copied app-repository instance. It does not validate links, decision closure, gate evidence, or application readiness.
- `CAP-002` is active as a manual review capability. Its self-review exercise remains inconclusive for independence; an independent conformance review now passes for the documented workflow/template status distinction.
- A separate application project provides the proving context. Its PRD, CX contracts, prototype, and reviews remain in that app repository and are not framework requirements.
- The canonical app-project map, templates, and local initializer passed their original independent starter review; an app-root-aware artifact helper is now included and awaits independent rerun. The portable core uses Markdown, Git, and Python standard-library scripts; the tool catalog documents optional adapters. Lifecycle, engineering, feasibility, quality, release, and operations workflows passed bounded written review; a separate-app implementation and non-production staging pilot remain.

## Actors

| Actor | Responsibility |
| --- | --- |
| Product owner | Sets product intent, decides material open questions, reviews outcomes, accepts or rejects residual risks, and authorizes consequential external actions. |
| Lead agent/orchestrator | Maintains the lifecycle state, routes work to the correct workflow and tools, keeps artifacts traceable, reports blockers, and does not claim unsupported completion. |
| Specialist agents/tools | Produce or review bounded artifacts and implementation work under explicit inputs, constraints, and acceptance criteria. |
| Application operator | Owns production credentials, service access, release authorization, incident response decisions, and operational risk for the application. This may be the product owner or a delegate. |

## Scope

### In scope for the framework

- A canonical app-project artifact map and starter package for constitution, specification, design/CX contract, backlog, decision log, reviews, architecture, verification, release, and operations evidence.
- A lifecycle workflow from ideation through post-launch learning, including required inputs, outputs, roles, dependencies, gates, and return paths.
- Reusable workflows for discovery/requirements, adversarial review, CX design, feasibility/architecture, implementation, technical verification, release, and operations.
- Agent-led execution of approved implementation tasks with clear stop conditions for unresolved owner decisions, access requirements, or failed gates.
- Project and framework validation sufficient to find missing required metadata, broken artifact references, inconsistent IDs, unlinked requirements/tasks, and missing gate evidence where mechanically checkable.
- A bounded method for integrating available skills, plugins, connectors, and command-line tools without assuming a provider or claiming unavailable automation.
- A proving run that keeps application code in a separate application repository.

### Explicitly out of scope

- Building any application's code in this framework repository.
- Selecting a universal language, hosting provider, database, identity provider, analytics provider, or deployment architecture for every future app.
- Guaranteeing that any application is “world-class,” safe, compliant, or production-ready solely because it used the framework. Those claims require app-specific evidence and accountable release decisions.
- Requiring every possible journey, integration, test, design command, or document for every app. Applicability must be decided from product scope and recorded; irrelevant template items are excluded with rationale.
- Building a centralized hosted workflow/orchestration service in v1. The first target is a clear, repository-first workflow that agents can execute with available tools.
- Treating a Figma prototype as proof of runtime integrations, persistence, security, accessibility on devices, or service operations.

## Framework requirements

Requirement statements in the tables below use uppercase RFC 2119 keywords for machine-checkable obligation strength. The artifact validator checks stable IDs, table shape, non-empty acceptance-evidence cells, and keyword form only in the configured requirement tables. It does not determine whether a requirement is clear, feasible, complete, or correctly classified.

### Functional requirements

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| FR-FW-001 | The framework MUST expose one canonical lifecycle from idea through launch and post-launch learning, with stages that identify purpose, owner/agent responsibility, required inputs, durable outputs, dependencies, and transition criteria. | Lifecycle runbook and project template use the same stage and gate IDs; a new project can identify its next action from its recorded status. |
| FR-FW-002 | The framework MUST define one canonical SDD artifact map and explain how `constitution.md`, `specification.md`, `design.md`, `backlog.md`, decisions, reviews, and delivery records relate. Tool-specific files such as Impeccable `PRODUCT.md` and `DESIGN.md` MUST be mapped as canonical, derived, or disposable rather than competing authorities. | Template index names the source of truth for each content type; no required content has two independently edited canonical copies. |
| FR-FW-003 | The framework MUST preserve traceability from user goals and decisions through requirements, design/CX requirements, architecture, backlog items, code changes, verification, release, and operational learning. | A sample requirement can be followed through linked artifacts and evidence; automated checks report broken or missing links where feasible. |
| FR-FW-004 | The framework MUST specify reusable workflows for discovery and requirements, adversarial review, CX design, feasibility and architecture, implementation, verification, release, and operations. Each workflow MUST provide inputs, outputs, responsibilities, gates, failure paths, and completion criteria. | Workflow coverage matrix maps every lifecycle stage to an owned workflow and required artifacts; a tabletop walkthrough identifies no stage with an undefined handoff. |
| FR-FW-005 | The framework MUST treat applicable reviews as gates with explicit pass conditions, evidence, finding disposition, rerun requirements, and an owner-authorized residual-risk path. Scores alone MUST NOT pass a gate. | Gate templates and sample records show pass, fail, rerun, and accepted-risk states; failed gates prevent lifecycle advancement in the documented procedure. |
| FR-FW-006 | The framework MUST enable an AI agent to implement an explicitly approved backlog item in an application repository, preserve repository instructions and boundaries, report changed files, and record actual verification evidence. | A bounded application task is implemented from approved artifacts in a separate app repository, reviewed against acceptance criteria, and linked back to its source task. |
| FR-FW-007 | The framework MUST include release and operations procedures for app-specific readiness, deployment evidence, rollback/recovery, monitoring, support/incident handling, and learning back into the backlog. | A staging release rehearsal records readiness, deployment, health checks, rollback path, operator ownership, and post-release learning without assuming a production provider. |
| FR-FW-008 | The framework MUST distinguish framework requirements from application-specific decisions and identify external prerequisites such as accounts, permissions, secrets, legal review, provider access, and owner authorization before they block planned work. | Project readiness checklist links each external prerequisite to dependent requirements/tasks and shows owner, status, and consequence of delay. |
| FR-FW-009 | The framework MUST bound review and remediation loops. Each gate MUST define the review scope, required complete set, remediation batch, rerun condition, escalation path, and what is deferred to implementation or release validation. | Workflow records state a finite review scope and pass/blocked outcome; no “repeat until perfect” language is used as a completion rule. |
| FR-FW-010 | The framework MUST produce a clear project status and next-action summary from durable artifacts so the owner does not need to ask what is next or infer whether work has started, completed, or is blocked. | A project status report names current stage, active work, completed outputs, blocked dependencies, next authorized action, and evidence links. |
| FR-FW-011 | The framework MUST use tools and skills according to their actual capabilities and lifecycle fit, distinguishing available and tested integrations from optional, unavailable, or future capabilities. | Tool/skill catalog records purpose, stage, inputs, outputs, availability, limitations, and evidence of use; no workflow claims a hook or connector is active without project-level proof. |
| FR-FW-012 | The framework MUST preserve a product-specific app repository as the source of truth for that application's requirements, implementation, infrastructure, and operational records after handoff, with an explicit transfer/continuity procedure from framework proving work. | A new app repository can be initialized from the template; its source links, history, ownership, and unresolved decisions remain traceable after separation. |
| FR-FW-013 | The framework MUST provide an approved template-only distribution that a new user can fork/clone or download as a source archive and use locally by following the README. The distribution MUST exclude all app-specific material and private owner information, including prior application history. | After the owner approves the package and license, a clean fork/clone and ZIP download both support the documented local validation and app-initialization path; the public repository has clean history and contains only approved reusable framework materials. |
| FR-FW-014 | An initialized application MUST record the exact framework source revision and contract versions used to generate its local governance tools. The app's validator MUST check versioned G-REQ and G-ARCH handoff manifests against their frozen source artifacts and must reject a gate record claiming PASS when the required manifest is missing or invalid. | A generated app records a 40-character source commit, artifact/helper contract versions, and locked file digests; controlled valid and invalid handoff fixtures demonstrate that validation accepts matching frozen inputs and rejects drift, missing manifests, duplicate JSON keys, and unsupported contract versions. |
| FR-FW-015 | The implementation workflow MUST preserve completed authorized changes in Git as scoped, reviewable commits and MUST push them to the authorized feature branch or remote when the owner has granted standing or task-specific push authorization. It MUST inspect the staged diff, exclude unrelated/user changes, preserve review controls, and report commit and push evidence; failed required checks or absent authorization MUST NOT be presented as a completed, merge-ready change. | A workflow tabletop covers a clean change, unrelated pre-existing edits, failing checks, missing remote/authorization, and successful feature-branch publication; every case preserves ownership boundaries and accurately records commit, push, and check status. |
| FR-FW-016 | The framework MUST guide new and resumed application setup through a progressive, evidence-aware intake that inspects available repository state, distinguishes owner statements, observed facts, researched claims, inferences, and unknowns, asks only relevant unresolved questions, and creates a truthful next-action summary without fabricating decisions or gate outcomes. | Fresh-copy exercises cover minimal and partial input, unknown answers, an existing codebase, a repeat run after one context change, and an invalid target; outputs preserve source/provenance labels, avoid stale template state, validate successfully, and ask only for material owner decisions. |
| FR-FW-019 | An initialized application MUST expose a deterministic local gate-transition command that consumes its pinned, approved gate contract and validated gate-run records, reports permitted next actions, and rejects unauthorized or illegal transitions. A downstream transition MUST be rejected when a prerequisite is absent, failed, blocked, or stale under the contract's exact-revision rules. The command MUST NOT define a second policy source or infer PASS from model output. | Positive and negative fixtures cover all ten gates, prerequisite states, exact source/artifact revisions, authorization, reruns, and invalidation against the pinned contract version. |
| FR-FW-020 | Gate transitions MUST persist as append-only records through atomic, concurrency-safe updates. Stale-source and concurrent writers MUST fail or recover without partial/corrupt authoritative state. Any cache MUST be regenerable from validated gate records and MUST NOT become an authority. | Fault-injection and contention tests demonstrate complete old-or-new records, safe stale-run rejection, deterministic recovery, and cache reconstruction from canonical gate records. |
| FR-FW-021 | Adversarial review runs MUST freeze their inputs and record reviewer/mode, contract version, findings, dispositions, and rerun identity. Review output MUST remain advisory and separate from verified CI evidence, gate transition authority, and owner authorization. The core validator MUST require no provider credentials; optional review adapters MUST be explicitly configured and separately permissioned. | Review-run schema and tests verify frozen digests, identity/mode, findings/dispositions and reruns; negative cases prove review output alone cannot pass a gate, substitute trusted CI, or authorize an owner decision. |
| FR-FW-022 | A context projection MUST be generated only from a versioned policy keyed by gate and role. Missing or ambiguous required inputs MUST fail closed with actionable diagnostics; optional inputs and exclusions MUST be explicit. | Policy fixtures cover each supported gate/role, required/optional/forbidden paths, missing required paths, ambiguous matches, and deterministic refusal behavior. |
| FR-FW-023 | Each projection MUST record the exact source revision, policy and contract/profile revisions, included and excluded paths with reasons, and SHA-256 digests for included files. Generation and cleanup MUST reject symlink/path escapes, preserve canonical source artifacts, and recover safely from interrupted/concurrent runs. | Positive/negative fixtures verify path containment, symlink rejection, digests, manifest completeness, concurrent creation, interruption cleanup, and unchanged canonical files. |
| FR-FW-024 | A generated projection MUST identify itself as context minimization only. It MUST NOT claim access isolation unless a separately named OS/container sandbox has demonstrated denial of excluded-path reads for the supported host/runtime. | Manifest and CLI output default to `context-minimization-only`; fixtures reject unsupported isolation claims, while any future sandbox claim requires separately scoped host-specific denial evidence. |
| FR-FW-025 | The framework's governance core MUST define lifecycle, artifact, validator, and evidence contracts without requiring an application runtime or invoking stack-specific checks unless a profile is explicitly selected. | Core-only validation runs without application-stack dependencies or commands; selecting a profile is required before stack-specific checks run. |
| FR-FW-026 | Each supported application profile MUST be separately versioned and declare its language/runtime versions, prerequisites, source-layout assumptions, applicable and unsupported checks, and profile-owned dependencies; initializer composition MUST be explicit and MUST report missing prerequisites or unsupported checks without implying success. | Profile metadata and initializer fixtures cover Next.js/TypeScript, FastAPI/Python, and Rust/Axum independently, including clean-target generation, prerequisite failures, and truthful unsupported-check reporting. |
| FR-FW-027 | Cross-module governance interfaces MUST use versioned schemas and documented compatibility behavior; profile composition MUST preserve core artifact identity and MUST NOT leak another profile's dependencies or instructions. | Valid/invalid schema fixtures, compatibility cases, and deliberate dependency/instruction-leakage fixtures demonstrate isolated profile composition. |
| FR-FW-028 | The framework MUST provide a small, versioned multi-platform sample contract that identifies owner-approved source facts separately from synthetic platform/profile fixtures, defines platform and toolchain applicability, and specifies one stable cross-module interface without changing any real application's approved scope. | The sample contract includes a provenance map, explicit supported/fixture-only/excluded platform and profile matrix, a versioned interface with positive and negative examples, and independent review plus owner acceptance of the exact revision before FW-TASK-013 may consume it. |

### Non-functional requirements

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| NFR-FW-001 | The repository workflow MUST be understandable to an owner who is not acting as the primary software implementer. | A cold-start walkthrough explains the current stage and next decision/action without relying on chat history. |
| NFR-FW-002 | Framework tooling MUST prefer small, inspectable, repository-native artifacts and avoid duplicate registries unless a demonstrated need justifies them. | The source-of-truth map identifies canonical data; generated outputs can be recreated or are clearly marked. |
| NFR-FW-003 | Validation MUST fail clearly and explain the artifact or gate evidence that needs attention; it MUST NOT silently alter product decisions or mark a failed gate as passed. | Deliberately invalid sample artifacts produce actionable diagnostics and leave source files unchanged. |
| NFR-FW-004 | App-specific security, privacy, accessibility, reliability, cost, legal, and operational requirements MUST be identified according to context and verified at the appropriate design, implementation, or release stage. | The project template records applicability and the stage/evidence for each selected quality requirement. |
| NFR-FW-005 | The workflow MUST remain adaptable to different stacks and platforms while preserving invariant traceability, accountability, and quality gates. | The starter supports at least one web-first and one native-inclusive project profile without changing core artifact identity and gate semantics. |
| NFR-FW-006 | The framework's canonical procedures and local helper scripts MUST be usable from a local checkout without ChatGPT Desktop, a single AI provider, or a paid desktop runtime. | A cold-start contributor can follow the README from a clean fork/clone or source archive, validate the framework, initialize a separate app repository, and run that app repository's copied artifact helper using documented local prerequisites; provider integrations are labeled optional adapters. |

## Canonical artifact map proposal

This is the planned project-level model, not a claim that all documents already exist. `FRAMEWORK-001` remains the durable framework constitution; the application template may render a project-specific `constitution.md` based on the same separation of durable principles and product-specific constraints.

| App project artifact | Canonical responsibility | Framework source/template |
| --- | --- | --- |
| `constitution.md` | Product invariants, decision rights, quality principles, security/privacy/accessibility commitments, and explicit constraints. | Project template, informed by `FRAMEWORK-001`. |
| `specification.md` | Product context, actors, scope, requirements, domain/data contracts, integrations, quality needs, acceptance criteria, assumptions, and open decisions. | Specification template and discovery workflow. |
| `design.md` | Product experience/design contract, journeys, information architecture, design system, platform behavior, and links to approved visual artifacts. | CX/design workflow; explicitly mapped with Impeccable `PRODUCT.md` / `DESIGN.md`. |
| `backlog.md` | Ordered, traceable implementation work with dependencies and observable acceptance criteria. | Backlog template and implementation workflow. |
| `decisions/` | Owner or delegated decisions with options, rationale, impacts, and affected artifacts. | Decision template and decision workflow. |
| `reviews/` | Independent adversarial, CX, architecture, and quality-gate evidence with dispositions and reruns. | Review templates and gate procedures. |
| `architecture/` | App-specific technical design and ADRs after feasibility constraints are understood. | Architecture workflow and ADR template. |
| `delivery/` | Implementation, verification, release, deployment, rollback, and operational evidence. | Execution, verification, release, and operations workflows. |

The app repository is the source of truth after project setup. Framework templates and workflows are copied or generated into that repository; framework changes do not silently rewrite an active app's accepted requirements.

## Lifecycle and gates

The stages below preserve the slide's ten-step narrative while adding an early feasibility check and explicit evidence contracts. Work may run in parallel where dependencies permit; the stage order is a reader-friendly spine, not a prohibition on parallel research or risk discovery.

| Stage | Outcome | Gate ID / required evidence |
| --- | --- | --- |
| 1. Ideate and frame | User, problem, desired outcome, evidence, constraints, and exclusions are recorded. | **G-INTENT:** problem/intent brief and initial assumptions. |
| 2. Project setup | Dedicated app repository and artifact skeleton exist; owner and agent boundaries are clear. | **G-SETUP:** repository initialization evidence and source-of-truth map. |
| 3. Specify | Constitution, specification, backlog, decisions, and success measures are coherent and linked. | **G-REQ:** requirements/adversarial gate; open decisions and dependencies are visible. |
| 4. Feasibility and challenge | Data/provider, legal, security, platform, cost, and operational constraints are tested early; requirements are independently challenged. | **G-FEAS:** feasibility findings and adversarial review dispositions; scope changes return to specification. |
| 5. Experience design | Complete in-scope journeys, states, platform behavior, and design system are represented in linked reviewable design artifacts. | **G-COVERAGE:** CX coverage and design review readiness; exclusions have rationale. |
| 6. Design quality | Complete active journey set is critiqued and refined. | **G-CX:** mandatory complete-scope UX critique gate and rerun. Use Impeccable `critique` where the app adopts it; a tool-neutral review procedure remains available. Technical audits do not substitute for critique. |
| 7. Architecture and build readiness | App architecture, trust boundaries, data contracts, CI path, task sequencing, and operational requirements are implementation-ready. | **G-ARCH:** architecture/security readiness review; approved, actionable backlog. |
| 8. Implementation | AI agents execute approved tasks in the app repository and update evidence. | **G-IMPL:** acceptance criteria and appropriate automated/manual verification per task; code review. |
| 9. Verification and launch | App quality and release readiness are evidenced for supported web/native surfaces. | **G-RELEASE:** web/native technical audits as applicable, security/privacy checks, release checklist, deployment/rollback evidence, owner authorization. |
| 10. Operate and learn | Usage, incidents, support, cost, and outcomes are monitored and feed decisions/backlog. | **G-OPERATE:** operator ownership, monitoring/support evidence, incident/learning review, next prioritized work. |

### Gate loop limits

- A review scope must identify the active artifacts, screens, platforms, or code paths being assessed. “Complete” means complete for the approved scope, not every hypothetical future capability.
- Findings are grouped into a focused remediation batch. After fixes, rerun the same gate against the complete affected scope.
- If the rerun still fails, stop and produce a decision-ready report: unresolved findings, evidence, product/technical trade-offs, owner decision needed, and recommended next action. Do not keep making unbounded cosmetic iterations.
- A documented owner-accepted residual risk may satisfy only the gate's explicit exception policy; it does not rewrite facts, imply implementation verification, or close unrelated requirements.
- Figma-only checks cannot satisfy runtime, provider, native-device, deployment, or operational evidence requirements. These are routed to the stage where they can be tested.

## Framework validation model

The framework itself is validated at three distinct levels:

1. **Framework readiness:** all required templates, workflows, gates, and execution boundaries exist and agree with one another.
2. **Implementation pilot:** a bounded, approved capability is implemented in a separate application repository from the framework's artifacts with traceable code review and verification evidence.
3. **Lifecycle proof:** an application completes a release rehearsal and, when the owner authorizes it, a real launch/operations cycle. Until this evidence exists, describe the framework as launch-capable by design but not yet proven through a production lifecycle.

This distinction prevents framework completion from being confused with an app launch, while preventing a paper-only framework from being called proven.

## Open decision vectors

These do not block writing the plan. Resolve them only when the dependent work reaches the corresponding point; record any decision in the framework decision log.

| ID | Open question | Options / current recommendation | Impact and dependent work |
| --- | --- | --- | --- |
| D-FW-01 | Which agent environment is the v1 supported execution target? | **Resolved by the owner on 2026-10-08:** tool-neutral, local-first core; no ChatGPT Desktop or single-agent dependency. Codex is one reference adapter, not the framework runtime. | DECISION-017; portability requirement NFR-FW-006 and the local README/bootstrap instructions. |
| D-FW-02 | What level of repository/deployment autonomy may agents exercise? | Recommend agents implement, run checks, and prepare release changes; require owner authorization for production deploy, external messages, purchases, destructive data actions, or permissions escalation. | Determines execution, CI/CD, security, and release workflow stop conditions. |
| D-FW-03 | What constitutes a sufficient lifecycle proof for v1? | Recommend framework readiness plus one separate-repository implementation pilot and a staging release rehearsal; count a real production launch/operations cycle as the evidence for “framework proven to launch,” not as a prerequisite to start the first app. | Determines v1 status labels, pilot scope, and claims in README/slide. |
| D-FW-04 | Which app profiles must the initial template support? | Recommend one adaptable default profile with web/native applicability branches; add specialized profiles only when a real app needs them. | Affects template validation and NFR-FW-005. |
| D-FW-05 | How should the canonical SDD design contract coexist with Impeccable's generated `DESIGN.md` on case-insensitive filesystems? | **Resolved by the owner on 2026-10-08:** keep SDD `design.md` canonical and store Impeccable's generated output separately under `.impeccable/generated/`. Because the installed document workflow writes `DESIGN.md` at its project root, run it in an isolated staging copy/worktree and transfer the generated files only after review; never execute it in the canonical app root. | App template and Impeccable integration use this rule. The staging approach must be validated in an app pilot before claiming it works with the installed tooling. |
| D-FW-06 | What distribution package should fulfill the owner's public fork/download intent? | **Public local use and MIT License are settled** by DECISION-017 and DECISION-018. Publish one clean-history **template repository** containing only reusable workflows, starter files, and local tools; exclude all app-specific material. Review the package before publication. | The development source and its history are not the public package. Explicit package review and owner authorization to publish remain required. |

## Dependencies and risks

- An application proving context may have failed or open gates; its product-specific gate state remains in that app repository and must not be represented as framework evidence.
- App-specific provider, licensing, monetization, MVP, retention, launch-sequence, and authentication decisions remain in each app's own specification and decision records. The framework tracks these dependencies without deciding them.
- GitHub access, Figma access, application-provider accounts, secrets, and hosting permissions are environment prerequisites, not capabilities the framework can conjure. The existing remote's live visibility was not verified in this work session.
- ChatGPT Desktop, a specific AI provider, or plugin bundle is not a framework prerequisite. Public fork/download access and the MIT License are settled, but the current working repository and its history are not an approved public package; complete the clean package and owner review before claiming open access.
- A workflow may be clear but still lack an available integration or reliable automation. The tool catalog must preserve that distinction.
- Expanding every process idea into a separate tool can recreate the endless-loop problem. V1 should prioritize documented, repeatable agent execution and only automate checks with stable, objective acceptance criteria.

## V1 exit criteria

Framework v1 is **ready for application implementation** when:

1. The canonical app template and lifecycle map satisfy FR-FW-001 through FR-FW-005 and have an adversarial review with no unresolved blocking findings.
2. Every lifecycle stage has a usable workflow, gate, evidence record, owner-decision route, and bounded failure path.
3. CAP-002 is implemented or accurately renamed to show its actual manual/automated scope, and CAP-003 covers general AI engineering execution without app-specific assumptions.
4. Framework instructions can initialize or guide a separate app repository without duplicating canonical artifacts or leaking app code into this repository.
5. A bounded implementation pilot and staging release rehearsal satisfy D-FW-03, or the owner records a revised proof bar.
6. The current stage, completed work, blockers, and next action are discoverable from repository artifacts without relying on chat history.

The framework is **proven through launch** only after an owner-authorized application release and at least one documented operations/learning review. This is a later evidence milestone, not an unbounded condition for finishing the reusable framework package.

## References

- [MISSION-001](../missions/MISSION-001.md)
- [FRAMEWORK-001](../constitution/FRAMEWORK-001.md)
- [FRAMEWORK-002](../constitution/FRAMEWORK-002.md)
- [FRAMEWORK-BACKLOG-001](FRAMEWORK-BACKLOG-001.md)
- [DECISION-017](../decisions/DECISION-LOG-001.md#decision-017) — tool-neutral local-first framework requirement.
- [GATE-CATALOG-001](GATE-CATALOG-001.md)
- [FRAMEWORK-GATE-CONTRACT-001](FRAMEWORK-GATE-CONTRACT-001.md)
- [FRAMEWORK-GATE-TRACEABILITY-001](FRAMEWORK-GATE-TRACEABILITY-001.md)
- [TOOL-CATALOG-001](TOOL-CATALOG-001.md)
- [CAP-001](../../framework/capabilities/CAP-001-artifact-management.md)
- [CAP-002](../../framework/capabilities/CAP-002-adversarial-review.md)
