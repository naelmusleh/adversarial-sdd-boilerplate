# Repository Operating Contract

This repository is the reusable Adversarial SDD application template. Each application created from it is a new repository with its own product documents, code, secrets, release records, and operational history.

## Session start

1. Read `README.md`, `mission.md`, `constitution.md`, `specification.md`, `design.md`, and `backlog.md` before implementation.
2. Read the matching workflow in `workflows/` and the applicable gate contract in `docs/framework/GATE-CATALOG-001.md`.
3. Run `python3 scripts/artifacts.py list` and `python3 scripts/artifacts.py validate`; inspect Git status and the current selected backlog item.
4. State the active gate, approved scope, selected task, acceptance evidence, and any blockers in your work record before making changes.
5. Do not implement through a failed or blocked gate. Ask the product owner only for decisions, permissions, unavailable evidence, or review that cannot be inferred.

## Source-of-truth rules

- `mission.md`, `constitution.md`, `specification.md`, `design.md`, and `backlog.md` are the canonical SDD product contracts.
- `PRODUCT.md` contains durable product context for compatible tools. It must not override the canonical SDD files.
- SDD `design.md` remains canonical. Generated design-tool output belongs under `.impeccable/generated/`; never create a case-only `DESIGN.md` beside `design.md` on a case-insensitive filesystem.
- `docs/` holds durable framework references and artifact templates. App-specific decisions, code, secrets, and release evidence remain in this repository after the template is initialized as an app.
- Preserve artifact IDs. Update the relevant document, decision record, gate record, and backlog state together when a decision or outcome changes.
- Distinguish owner decisions, observed facts, and agent inferences. Do not resolve open decisions silently.

## Implementation and evidence

- AI agents are expected to perform routine implementation, documentation, and verification work. The owner supplies intent, resolves material choices, and reviews/accepts results.
- Implement exactly one selected backlog task at a time. Link code and evidence to its requirement and acceptance criteria.
- Run the relevant checks, including `npm run typecheck`, `npm test`, `npm run test:coverage`, and `npm run build` when applicable. A required check that cannot run is reported as unverified, never as passed.
- Run `python3 scripts/artifacts.py validate` before proposing a change for review.
- Do not use production credentials or deploy without the specific authorization and release gate required by this repository.
- Report changed files, actual check output, unresolved risks, and the next permitted task.

## Framework invariants

- The lifecycle is finite: G-INTENT, G-SETUP, G-REQ, G-FEAS, G-COVERAGE, G-CX, G-ARCH, G-IMPL, G-RELEASE, and G-OPERATE.
- Gates require linked evidence. Scores and agent assertions do not pass gates.
- A failed or blocked gate stops dependent work. Resolve findings and rerun the affected complete scope or record an owner-approved residual risk where allowed.
- Web, Android, and iOS are considered independently wherever the product supports those surfaces. A web check does not prove native quality or feature parity.
- Material 3 and Apple Human Interface Guidelines are design references for the relevant surfaces, not substitutes for the product's approved design contract or accessibility evidence.
- Application-specific database contracts, authorization rules, migrations, retention, and recovery requirements must be written in `specification.md` and architecture records before implementation relies on them.
