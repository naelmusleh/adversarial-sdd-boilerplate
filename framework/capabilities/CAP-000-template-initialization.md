---
id: CAP-000
type: framework-capability
title: Template initialization and fresh-session bootstrap
status: active
version: 0.1
created: 2026-10-10
updated: 2026-10-10
related-artifacts: FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-SPEC-001, GATE-CATALOG-001, CAP-001, CAP-004
---

# CAP-000 — Template initialization and fresh-session bootstrap

## Purpose

Define how a human developer or incoming AI agent starts work from a fresh application repository without relying on ChatGPT Desktop, chat history, unstated memory, or an untracked setup ritual. The app repository is the durable source of truth. This contract is immutable for a given project session: changes to the bootstrap sequence require a recorded decision or reviewed change to this capability.

## Actors and authority

- **Application owner:** supplies or confirms intent, makes material product/security/provider decisions, grants access, and approves gates and release actions.
- **Lead agent:** reads the repository, reports state and risks, maintains artifacts, selects authorized work, implements routine tasks, and gathers evidence.
- **Independent reviewer:** assesses required adversarial, CX, architecture, and code-review gates without replacing the owner's decision authority.
- **Repository:** holds canonical requirements, design, backlog, decisions, reviews, code, configuration, and observed evidence.

An agent may infer ordinary reversible implementation details from approved contracts. It may not silently decide product behavior, data rights, auth policy, user-visible defaults, public exposure, credential handling, production access, or unresolved high-impact risks.

## Fresh-session bootstrap sequence

An incoming agent performs these steps in order before changing application behavior:

1. **Identify the checkout.** Confirm the current repository root, active branch, Git remotes, and working-tree status. Do not assume a directory or remote from chat context. Preserve existing user changes.
2. **Read the repository contract.** Read `README.md` and `AGENTS.md`, then `mission.md`, `constitution.md`, `specification.md`, `design.md`, and `backlog.md`. These are the minimum canonical project state. Read linked records that affect the requested task.
3. **Parse `/docs`.** Read `docs/framework/GATE-CATALOG-001.md` for gate entry/exit evidence; `docs/framework/TOOL-CATALOG-001.md` for available integrations and limitations; the matching `workflows/*.md`; and applicable files under `docs/templates/`. Do not load every unrelated artifact when the task has a bounded scope.
4. **Read the owner-controlled product and data contracts.** In `specification.md` and linked architecture/decision records, identify data classification, collection purpose, persistence, consent, access control, retention/deletion, migrations, backup/recovery, third-party providers, service-level expectations, and failure behavior. If these contracts are missing or contradictory, record a blocker; do not invent a database schema or authorization model.
5. **Read design constraints before UI work.** Read `design.md` and linked design-system records. Preserve approved tokens, typography, component semantics, responsive behavior, and surface parity. For Material surfaces, check the project’s Material 3 commitments; for Apple native surfaces, check the relevant Human Interface Guidelines. Keep platform conventions explicit. Do not replace approved app tokens with unapproved framework defaults.
6. **Establish objective state.** Run `python3 scripts/artifacts.py list` and `python3 scripts/artifacts.py validate`, inspect recent Git history, then locate the active gate record and task in `backlog.md`. Record command outputs or a clear reason when an environment lacks Python or Git metadata.
7. **Choose one authorized next action.** Confirm its prerequisite gates, task ID, requirement links, acceptance criteria, and verification plan. Work that depends on a failed/blocked gate must not start. Independent safe work may proceed only if it does not conceal, bypass, or prejudge the blocked decision.
8. **Execute and update durable state.** Implement the selected task, add or update focused tests and documentation when required by acceptance criteria, and update backlog progress with evidence. Keep code, migrations, design, decisions, and verification linked to stable artifact IDs.
9. **Verify and report.** Run the checks required by the task and active gate. Report exact observed results, files changed, failure output, unsupported checks, residual risks, and the next allowed action. Never equate a file's existence or a test plan with successful execution.

## Canonical state precedence

When sources disagree, use this order and stop on material contradictions:

1. Explicit current owner decision recorded in the app's decision log or decision record.
2. Approved `constitution.md` and `specification.md` for product invariants and required behavior.
3. Approved `design.md` and linked reviewed design evidence for experience behavior.
4. Passed gate records and linked verification evidence for demonstrated readiness.
5. Architecture, ADRs, backlog, and implementation records for approved technical realization.
6. `PRODUCT.md` or generated tool-specific documents only as synchronized derivatives.
7. Chat summaries, agent memory, generated notes, and unreviewed proposals are context only; they cannot silently supersede repository artifacts.

If two approved sources conflict, preserve the current state, create a decision-ready conflict record, and ask the owner only if the choice materially affects scope, experience, data, security, cost, legal exposure, or release.

## Gate mapping

| Lifecycle checkpoint | Required repository evidence | Bootstrap action |
| --- | --- | --- |
| G-INTENT | `mission.md`, evidence and explicit non-goals | Confirm user/problem/outcome and unresolved assumptions. |
| G-SETUP | repository identity, `AGENTS.md`, canonical files, owner/access map | Confirm source of truth, clean project boundary, and cold-start usability. |
| G-REQ | `constitution.md`, `specification.md`, `backlog.md`, independent review | Trace requirements, decisions, exclusions, outcomes, and testable criteria. |
| G-FEAS | feasibility register, evidence and owner/status | Validate provider/data rights, legal, security/privacy, platform, cost, and operating prerequisites. |
| G-COVERAGE | `design.md`, journey inventory, requirements map, supported-surface contract | Check all applicable actor, onboarding, core, recovery, account, support, and exit journeys; document justified exclusions. |
| G-CX | rendered prototype evidence, complete-scope critique, findings and rerun | Resolve and rerun every finding or stop; do not advance on score alone. |
| G-ARCH | architecture overview, data/trust contracts, reviewed ADRs, task-ready backlog | Validate schema, authorization, integrations, failure handling, operations, and deployment assumptions. |
| G-IMPL | selected task, code review, tests, build, linked verification record | Implement one approved task and record observed evidence. |
| G-RELEASE | release record, security/accessibility/platform evidence, rollback/support plan, owner authorization | Block production release unless all required evidence and explicit authorization exist. |
| G-OPERATE | monitoring, support, incident, user outcome, cost, and learning records | Assign operational responsibility and convert observed learning into linked decisions/backlog work. |

## Design-system safeguards

- `design.md` is the canonical SDD contract for experience and visual behavior.
- Material 3 and Apple HIG guide decisions only where they apply to the product's supported platform. Record selected patterns and justified deviations in the project design system.
- The framework starter's tokens/components are neutral scaffolding. They do not replace a product-specific reviewed brand kit.
- Generated design documents belong under `.impeccable/generated/`. Never create `DESIGN.md` beside canonical `design.md` on a case-insensitive filesystem.
- A Figma file, screenshot, or design critique cannot prove runtime integration, database authorization, native accessibility, or production readiness.

## Database and credential safeguards

- Treat the database contract as part of product requirements and architecture, not as an implementation detail inferred from a provider SDK.
- Keep privileged keys server-side. Never prefix service credentials with `NEXT_PUBLIC_`; never log secret values; never commit local environment files.
- Supabase browser access uses only its explicitly publishable key and relies on row-level security for authorization. A publishable key is not a substitute for RLS.
- Validate required runtime configuration at server initialization. Error messages may name missing variables but must not disclose their values.
- Any schema, RLS policy, migration, retention, deletion, backup, or recovery change must have linked acceptance and verification evidence.

## Stop conditions

Stop dependent work and record a blocker when the requested task requires a missing owner decision, a failed prerequisite gate, unavailable access, unclear data rights, contradictory canonical documents, untestable acceptance criteria, or a security/privacy contract that is not defined. Continue only independent work that cannot commit the project to the unresolved choice.

## Evidence of conformance

A session conforms when its work record identifies the repository root and baseline, canonical artifacts and gate read, active task and prerequisites, changed artifacts/code, actual checks/results, remaining risks, and permitted next action. Repository validation passing alone does not prove that the session followed this capability.

## References

- [FRAMEWORK-001](../../docs/constitution/FRAMEWORK-001.md)
- [FRAMEWORK-002](../../docs/constitution/FRAMEWORK-002.md)
- [FRAMEWORK-SPEC-001](../../docs/framework/FRAMEWORK-SPEC-001.md)
- [GATE-CATALOG-001](../../docs/framework/GATE-CATALOG-001.md)
- [CAP-001 Artifact Management](CAP-001-artifact-management.md)
- [CAP-004 App Repository Bootstrap](CAP-004-app-repository-bootstrap.md)
