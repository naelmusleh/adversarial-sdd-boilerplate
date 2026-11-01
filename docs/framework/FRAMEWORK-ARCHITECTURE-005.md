---
id: FRAMEWORK-ARCHITECTURE-005
type: framework-architecture
title: FW-TASK-033 founder-facing orchestrator and role-capability architecture
status: draft
version: 0.1
created: 2026-11-01
updated: 2026-11-01
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-012, FRAMEWORK-COVERAGE-004, FRAMEWORK-CX-004, DECISION-057, DECISION-058, FRAMEWORK-ADV-063
---

# FRAMEWORK-ARCHITECTURE-005 — FW-TASK-033 founder-facing orchestrator and role-capability architecture

## Gate and scope

- **Gate:** G-ARCH for FW-TASK-033 and FR-FW-041–045 only.
- **Inputs:** FRAMEWORK-FEASIBILITY-012; FRAMEWORK-COVERAGE-004; FRAMEWORK-CX-004; DECISION-057/058; the pinned one-man-startup roster at commit `0a47eac13eaf63511903a5c25933325210bdc101`.
- **Target:** A repository-native, provider-neutral coordination contract; a catalog of role capabilities; and traceable handoff/status guidance.
- **Exclusions:** Hosted orchestration, provider-specific dispatch, runtime execution guarantees, one executable agent per catalog item, app-specific activation, gate-contract changes, application implementation, automatic posting/spending/deployment, and production recovery actions.
- **Implementation boundary:** This architecture authorizes no implementation. A later G-IMPL decision is required for the documented role catalog/workflow/template changes. Any executable orchestration or adapter needs a separate scope and feasibility review.

## Decision summary

Model roles as **capabilities with contracts**, not as a promise of separate always-running agents. The default is one lead orchestrator plus the current work agent; the orchestrator engages the smallest justified specialist set. Sequential role-bounded work in one agent is allowed unless independence, expertise, or useful parallelism requires a distinct actor. Independent review remains distinct from implementation; QA remains a distinct outcome even where one individual performs both activities on a low-risk task.

Use current canonical artifacts for project state. The orchestrator reads them and reports; it does not create an alternate task/gate registry or author authoritative gate transitions. Optional app role profiles may state which capabilities are available and the app-specific triggers, but absence of a specialist never means that a required safeguard passed.

## Full source-role crosswalk

The source is the 26-entry `docs/TEAM.md` pinned in DECISION-057. “Covered” means the framework already names the responsibility in a role/workflow/gate; it does not mean a dedicated agent or automation exists.

| Source role | Framework disposition | Activation / boundary |
| --- | --- | --- |
| orchestrator | Existing role; strengthen its operating contract | Always the owner-facing coordinator when used; reads canonical artifacts, routes work, reports evidence; never approves or passes gates. |
| setup | Existing onboarding responsibility; no standing agent required | New/resumed app setup or material context change; progressive intake only. |
| researcher | Existing discovery capability; optional specialist | Material user, competitor, market, or provider uncertainty; evidence informs owner choice, not automatic requirements. |
| feasibility | Existing G-FEAS specialist capability | A material assumption could change scope, cost, legality, platform, provider, or operations. |
| architect | Existing G-ARCH responsibility | New product, significant feature, or material data/integration/trust/operation boundary. Keep output proportional. |
| agentic-workflow | Conditional specialist capability | The application itself includes AI behavior/workflows requiring guardrails, evaluations, or AI-specific cost treatment; excluded for development-only AI use. |
| platform-architect | Conditional platform specialty | Selected platform has material architecture differences or platform-specific obligations. |
| product-designer | Existing CX/design capability | User-facing journey or interaction changes; follow approved MVP scope. |
| platform-designer | Conditional design specialty | Selected platforms require meaningful divergent interaction/design contracts. |
| web-dev | Stack-selected implementation specialty | Only when the app selects web and the task changes web code. |
| android-dev | Platform-selected implementation specialty | Only when Android is an approved app surface and the task affects it. |
| ios-dev | Platform-selected implementation specialty | Only when iOS is an approved app surface and the task affects it. |
| desktop-dev | Platform-selected implementation specialty | Only when desktop is an approved app surface and the task affects it. |
| backend-dev | Stack-selected implementation specialty | Only when server/data/integration work is in approved scope. |
| debugger | Focused troubleshooting mode, not a standing role | Hard or repeated defect with reproducible evidence; ordinary bugs remain with implementation. |
| reviewer | Existing independent review responsibility | Required by the applicable gate/repository policy; implementer cannot claim independent review. |
| qa | Existing acceptance/verification responsibility | Verify approved acceptance and release outcomes; QA result is separate from review and release authorization. |
| rollback | Operational capability/runbook, not an autonomous agent | Prepare or carry out recovery only under the app's explicit operator authorization and evidence. |
| security | Conditional specialist plus existing gate checks | Sensitive data, identity, permissions, integrations, exposure, or material threat; no blanket security certification. |
| legal | Conditional issue-spotting capability | Jurisdiction, privacy, IP, terms, regulated activity, or other legal question; qualified counsel makes legal judgments. |
| dashboard | Product/operations reporting capability, not an agent | Only if an owner/operator has a defined need for service, usage, or cost visibility. |
| devops | Conditional release/operations specialty | Environment, deployment, monitoring, or reliability work warrants it; small pilots may use documented simple procedures. |
| growth | Optional business capability; may precede build for a market bet | Defined acquisition, retention, positioning, pricing, or demand question; owner approves spend and business claims. |
| social-media | Optional communications capability | Defined audience and communications goal; may draft, never publish/contact without applicable authorization. |
| explainer-writer | Optional product education capability | User research or support indicates a need for educational content; factual claims remain sourced and owner-approved. |
| optimizer | Periodic evidence-based improvement capability | Observed cost, delay, or waste supports a bounded proposal; recommendation only, no perpetual optimization queue. |

## Candidate role contracts

These are architecture-level contracts for the next-version catalog. They define the assignment boundary, not runnable agent prompts or an assertion that the framework has each specialist available.

| Role/capability | Purpose and trigger | Inputs → deliverable | Limit, escalation, and handoff |
| --- | --- | --- | --- |
| Orchestrator | Coordinate every active project interaction; invoked on owner request or lifecycle handoff. | Canonical project records → status/next-action summary and bounded role assignments. | Cannot decide product scope, pass/transition gates, self-review, or authorize release; missing/conflicting records go to owner; handoffs reference canonical tasks. |
| Setup | Establish or refresh project context when starting/resuming an app. | Owner intent and existing repository → source map, initial decisions/unknowns, next step. | Progressive intake; no premature stack/legal/provider questionnaire; material choices return to owner; handoff to discovery. |
| Researcher | Reduce a material user/market/competitor/provider unknown. | Bounded question and trusted-source policy → dated findings, provenance, limits, options. | External content is untrusted; no fabricated user evidence or silent requirement creation; handoff to owner decision or feasibility. |
| Feasibility | Test assumptions whose failure could change commitment. | Requirement and claim, evidence plan → supported/unsupported/unknown/constrained result and dependency state. | No “agent believes feasible”; cannot accept risk for owner; high-impact unknowns return to owner, architecture after disposition. |
| Architect | Define a proportionate system contract for new product/material boundary changes. | Approved requirements, design, feasibility → boundaries, ADRs, task-ready implementation plan. | No provider/stack decision without authority; no speculative scale design; unresolved material tradeoffs return to owner; handoff to implementation readiness. |
| Agentic-workflow specialist | Design AI behavior inside the product where present. | AI-specific product goals, data, risks → interaction contract, guardrails, evaluation plan, cost assumptions. | Not triggered by AI-assisted coding alone; cannot claim model safety or quality without evidence; escalate data/authorization risk to security/owner. |
| Platform architect | Resolve material architecture differences for an approved platform. | Selected platform and shared architecture → platform-specific constraints and contract delta. | No undeclared platform commitment; unsupported capability remains unsupported; handoff to shared architect and platform implementation. |
| Product designer | Shape approved user journeys and interaction behavior. | Requirements, user evidence, platform scope → design/CX contract and prototype evidence when useful. | No scope invention; MVP focus; critical ambiguity returns to owner; handoff to CX review and implementation. |
| Platform designer | Specify meaningful platform-specific interaction differences. | Shared design plus selected platform contract → bounded platform design delta. | No parity promise without evidence; omit if no material difference; handoff to product designer/relevant platform implementer. |
| Web developer | Implement an approved web task. | App instructions, task, code context → scoped change and observed verification. | Exact task only, no secrets or release action; blockers return to owner/orchestrator; handoff to reviewer/QA. |
| Android developer | Implement approved Android work when Android is in scope. | Android task, platform contract, source → scoped Android change and device/test evidence. | No Android support claim without app decision and evidence; unsupported platform blocks only dependent work; handoff to reviewer/QA. |
| iOS developer | Implement approved iOS work when iOS is in scope. | iOS task, platform contract, source → scoped iOS change and device/test evidence. | No iOS support claim without app decision and evidence; unsupported platform blocks only dependent work; handoff to reviewer/QA. |
| Desktop developer | Implement approved desktop work when desktop is in scope. | Desktop task, platform contract, source → scoped desktop change and verification. | No desktop support claim without selection/evidence; blockers stay visible; handoff to reviewer/QA. |
| Backend developer | Implement approved server, data, or integration work. | API/data contract, architecture, task → scoped server change and tests/evidence. | No implicit data-retention/auth/provider choice; security/data risk escalates to owner/security; handoff to reviewer/QA. |
| Debugger | Diagnose a difficult or repeated defect. | Reproduction, logs, failing test, relevant source → evidenced root-cause hypothesis and focused fix/test plan. | Must not guess from symptoms or broaden task; if cause remains unknown, report next diagnostic; handoff to task owner/implementer. |
| Independent reviewer | Independently challenge a frozen artifact/change where policy requires it. | Exact revision, criteria, evidence → findings, severity, disposition request. | Must disclose author/context overlap; never edits or passes gate by itself; findings go to author, gate decision to authorized owner. |
| QA | Verify approved acceptance and release criteria. | Requirements, changed revision, test environment → observed pass/fail/not-run evidence. | No new scope or gate waiver; distinguish from code review and CI; failure returns to implementer/owner, release decision to authorized operator. |
| Rollback/recovery | Prepare or assist safe restoration when release/runbook requires it. | Incident/release identity, runbook, authorization → bounded recovery action/evidence or safe stop. | Not autonomous; requires app policy authorization, data integrity and recovery checks; escalate uncertainty to operator; handoff to incident/operations record. |
| Security | Analyze material threat, identity, data exposure, or dependency risk. | Threat/data flow and task context → bounded threat findings and controls/evidence needs. | Cannot certify product security globally; unavailable expertise stays visible; escalates unresolved risk to owner and G-ARCH/release. |
| Legal support | Identify legal questions and prepare review material. | Jurisdictions, data/use/claims context → issue list and questions for qualified counsel. | No legal advice, compliance certification, or legal position; escalate to counsel/owner; handoff to feasibility/decision record. |
| Dashboard/operations reporting | Provide a defined operator view when evidence shows it is needed. | Operator questions and available telemetry → minimal report/dashboard requirements. | Not a universal agent or app feature; no unsupported health/cost claims; missing telemetry reported as unknown; handoff to operator/product backlog. |
| DevOps | Plan/implement authorized environments, delivery, monitoring, and operational controls. | Approved deployment/operations contract → environment/release/runbook evidence. | No provider/production credential use or deployment without authorization; escalates missing controls to operator/owner; handoff to release gate. |
| Growth | Address a defined market, acquisition, retention, positioning, or pricing question. | Owner-approved business objective and evidence → bounded experiment/options/metrics. | No unapproved spend, public claim, or product commitment; uncertainty/falsifier returned to owner; handoff to product decision. |
| Social media/communications | Prepare audience-specific product communications. | Approved audience, claims, voice, channel → draft content and publication checklist. | Draft only by default; posting/contact requires authorization; uncertain claims return to owner; handoff to owner for approval. |
| Explainer writer | Help users understand a proven product task or concept. | Approved product behavior and sourced claims → concise educational copy/script. | No advice or unsupported claims; unclear behavior returns to product owner; handoff to design/content review. |
| Optimizer | Investigate observed process cost, delay, or waste. | Measured baseline and bounded goal → recommendation with expected measure and rollback/revisit. | Proposal only; no automatic workflow change or endless optimization; owner selects; handoff to backlog. |

## Proposed role-capability record

The future role catalog should use one stable entry per capability, with this logical shape:

| Field | Purpose |
| --- | --- |
| `role_id`, `name`, `version`, `classification` | Stable identity; classification is existing, specialist, operational/product responsibility, or excluded. |
| `purpose` | Outcome the role is responsible for supporting. |
| `activate_when[]`, `do_not_activate_when[]` | Positive trigger and explicit non-trigger, linked to requirement/task/gate context. |
| `required_inputs[]` | Canonical artifact paths/IDs and exact revisions needed to work safely. |
| `deliverable` | Reviewable output, evidence location, and expected format. |
| `decision_limits[]`, `escalate_when[]` | Authority boundary and condition that returns a decision to owner/operator/qualified professional. |
| `handoff` | Next responsible actor, task/requirement links, and state/evidence references. |
| `execution_mode` | `same-agent-sequential`, `separate-agent-when-justified`, or `external-qualified-review`; not a runtime promise. |

Per-app availability/activation belongs in that app's existing project context or role configuration, not in a second global status ledger. If the framework has no configured role catalog adapter, Markdown contracts remain authoritative and the orchestrator applies them procedurally.

## Orchestration sequence and state boundaries

1. Read app instructions and canonical mission/specification/backlog/decision/gate records. Report missing or conflicting records as such.
2. Identify the approved task and next action allowed by the adopted lifecycle contract. If no eligible task exists, ask for only the material owner input and continue independent safe work if possible.
3. Match task triggers to available role capabilities; record why a material role is activated or omitted. The number of role entries does not determine complexity or gate status.
4. Create a bounded handoff referencing exact source artifacts/revisions, task/requirement IDs, question, deliverable, authority limits, and evidence location.
5. Reconcile role outputs against requirements and observed evidence. Preserve unknown, unavailable, stale, conflicted, failed, and blocked distinctions; do not average them into a green summary.
6. Update only the canonical task/decision/evidence records permitted by the selected workflow. Gate transition, risk acceptance, release, and external actions remain with their separately authorized authority.
7. Report goal, active work/gate, verified completion, blocker/owner action, and next permitted action in plain language.

Status report format is a projection from canonical records, not separately persisted authoritative state. Handoffs may be artifacts, but they reference the backlog and evidence rather than shadowing their status.

## Trust, failure, and operating considerations

- External research and specialist outputs are untrusted inputs. They may inform a recommendation but cannot alter role permissions, paths, gate rules, or owner decisions.
- Missing expertise/tool access is `unavailable` or `unknown`; a substitute role cannot impersonate qualified legal/security review.
- If role selection is ambiguous, use the lowest-risk capability set that satisfies the accepted task and ask the owner only if the choice materially changes scope, cost, authority, or promise.
- Reviewer independence is based on actual authorship/context and required policy, not the label assigned to a role. A same-agent sequential review cannot satisfy an independent-review requirement.
- Growth, legal, social, dashboard, and optimizer roles do not automatically run during MVP mode. A market validation bet may use research/growth/feasibility before build when the owner selected that outcome.

## Implementation-sized follow-up (not authorized here)

After separate G-IMPL approval, the minimal documentation-only slice would update the lifecycle/engineering workflows with the orchestration sequence, add an optional role-catalog template and concise role contracts, and add founder-facing status/handoff examples. It would not create agent runtime code. Automated dispatch, provider adapters, and app-specific role activation remain separate tasks requiring evidence and authorization.

## G-ARCH exit criteria

The architecture is ready only when the full crosswalk covers the pinned 26-role roster; each capability has triggers, inputs, output, limits, escalation, and handoff; the orchestrator's state/authority boundary is unambiguous; MVP and post-MVP routing are demonstrated; duplicate artifacts/gates are excluded; and an independent architecture review plus exact-revision CI pass.
