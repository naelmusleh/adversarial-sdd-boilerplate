# Adversarial SDD — application template

**A local-first, AI-first starter for taking an application from intent to operation through ten evidence-based gates.**

This repository is the reusable boilerplate. Each product created from it lives in a separate app repository that contains that product's requirements, design, code, decisions, release history, and operational evidence. The framework is a set of files, tools, and repeatable procedures; it is not a hosted service and does not require ChatGPT Desktop.

```text
┌──────────────────────────────────────────────┐
│ Adversarial SDD template repository           │
│ lifecycle · gates · templates · local tools    │
└───────────────────────┬──────────────────────┘
                        │ initialize once; evolve in app repo
                        ▼
┌──────────────────────────────────────────────┐
│ One application repository                    │
│ mission · constitution · specification         │
│ design · backlog · code · evidence · operation │
└──────────────────────────────────────────────┘
```

The template starts with a neutral Next.js 15, React 19, TypeScript 5, and Supabase-ready application shell. Those technologies are a starter choice, not a requirement imposed on every application. Change the stack only through an app-specific decision backed by requirements and feasibility evidence.

## What is in this repository

```text
adversarial-sdd-boilerplate/
├── README.md                         # this operator manual
├── AGENTS.md                         # fresh-session engineering contract
├── .github/workflows/                # CI checks and weekly governance proposal
│   ├── verify-pipeline.yml            # artifact, initializer, TypeScript, test, coverage gates
│   └── weekly-architecture-audit.yml  # dependency and research audit with draft PR
├── package.json                      # pinned Next / React / test toolchain
├── vitest.config.ts                  # jsdom and strict coverage thresholds
├── instrumentation.ts                # server boot environment guard
├── .env.example                      # variable names, no credentials
├── src/
│   ├── app/                           # neutral Next.js App Router shell
│   └── core/env.ts                    # fail-fast runtime configuration
├── docs/
│   ├── constitution/                  # reusable framework principles
│   ├── framework/                     # scope, backlog, gates, tool catalog
│   └── templates/app-project/         # canonical app SDD starter files
├── framework/capabilities/            # CAP-000 through CAP-005 contracts
├── scripts/
│   ├── artifacts.py                   # list, create, validate SDD records
│   ├── init_app_project.py            # generate a fresh app repository
│   └── architecture_research.py       # bounded web research and audit report compiler
├── workflows/                         # product lifecycle operating steps
└── tests/                              # starter tests and coverage support
```

Framework artifacts describe reusable process. Generated application artifacts describe one application's product. The initializer does not copy a sample app's requirements or decisions into a new project.

## Repository automation

The [Verify Pipeline](.github/workflows/verify-pipeline.yml) runs independent artifact, initializer, TypeScript, Vitest, and coverage checks for pushes and pull requests targeting `main`. It provides G-RELEASE evidence. GitHub repository protection must separately require those checks and restrict direct updates or bypasses before the evidence becomes a merge block; a successful workflow alone does not protect the branch.

The [Weekly Architecture Audit](.github/workflows/weekly-architecture-audit.yml) runs Sunday at 00:00 UTC and can be started manually from `main`. It audits the committed npm lockfile and runs three public engineering research sweeps. It combines vulnerability metrics, source links, screening outcomes, and any qualified FW task drafts into a new validated report, then opens or updates a draft PR on `automation/weekly-architecture-audit`. Configure the repository Actions secret `TAVILY_API_KEY` for the research sweeps; missing credentials or incomplete research produce a visible non-zero workflow result. The daemon never edits `/src`, the canonical backlog, dependencies, or existing records. A maintainer reviews source claims and accepts any candidate task through a separate change. GitHub may place checks triggered by a PR created with the default Actions token into an approval-required state; a maintainer must approve that run or manually dispatch Verify Pipeline against the PR branch before merge. The combined report is operational evidence, not a complete architecture or production-readiness review. See [CAP-005](framework/capabilities/CAP-005-platform-governance-daemon.md) for permissions, boundaries, and evidence requirements.

## Requirements

- Git 2.40 or newer.
- Python 3.10 or newer for the artifact helper and app initializer.
- Node.js 22.12 or newer and npm 10.9 or newer for the bundled Next.js/Vitest stack.
- A Supabase project only when the new app is ready to run its server. The template does not provision a database or create credentials.
- A GitHub account/repository only if the owner chooses GitHub as the app's remote. Local use is supported.

The bundled Next.js starter is pinned to `15.5.27`, the 15.x backport selected when this starter was prepared. The template does not assert that this remains the newest patch release; update it through a reviewed dependency change. [Next.js 15.5 release notes](https://nextjs.org/blog/next-15-5) · [Next.js 15 package versions](https://www.npmjs.com/package/next?activeTab=versions).

## Start a brand-new application from scratch

The following steps produce a new local app directory. They do not create a GitHub repository, publish code, accept terms, provision a database, choose a provider, or deploy an application.

### 1. Obtain the template

Clone the repository or download its ZIP from GitHub and extract it. Then open a terminal in the extracted `adversarial-sdd-boilerplate` directory.

```sh
git clone https://github.com/naelmusleh/adversarial-sdd-boilerplate.git
cd adversarial-sdd-boilerplate
```

For a downloaded ZIP, change into the extracted directory instead. No `.git` metadata is required to use the templates and local scripts.

### 2. Check the template before using it

```sh
python3 scripts/artifacts.py list
python3 scripts/artifacts.py validate
npm install
npm run typecheck
npm test
npm run test:coverage
```

The coverage command fails unless the included source reaches 100% statements, branches, functions, and lines. New source added to `src/` joins the coverage scope. This is a deliberate quality gate: do not weaken thresholds to make a failing change appear green.

### 3. Generate the app's SDD workspace

Run the initializer from the template directory and choose the app name, a short stable ID prefix, and a new sibling folder:

```sh
python3 scripts/init_app_project.py \
  --name "Example App" \
  --prefix EXAMPLE \
  --target ../example-app
```

The initializer refuses a non-empty target. By default it creates the five canonical app SDD documents, an app README, app-specific `AGENTS.md`, `.gitignore`, and a copy of the dependency-free artifact helper. It never overwrites existing work. Add `--include-lifecycle-records` only if the team wants the optional supporting record templates preseeded; otherwise create records when their gate requires them.

### 4. Add the selected runtime and lifecycle files to the app repository

The initializer creates the app's SDD files and framework helper. Every app also needs the reusable lifecycle contracts. The web runtime below is an optional starter: use it when the app has chosen the bundled Next.js stack. If the app chooses another stack or native clients, retain the SDD/framework files and replace or extend the runtime according to the app's approved architecture. Record that stack and platform decision in the app repository before implementation. Set `TARGET` to the same path passed to `--target`:

```sh
TARGET=../example-app
mkdir -p "$TARGET/tests" "$TARGET/docs" "$TARGET/framework"
cp -R docs/framework "$TARGET/docs/"
cp -R docs/constitution "$TARGET/docs/"
cp -R docs/templates "$TARGET/docs/"
cp -R workflows "$TARGET/"
cp -R framework/capabilities "$TARGET/framework/"
```

For the bundled Next.js web starter, add its runtime files as well:

```sh
TARGET=../example-app
cp package.json package-lock.json vitest.config.ts tsconfig.json next.config.ts next-env.d.ts instrumentation.ts .env.example "$TARGET/"
cp -R src "$TARGET/"
cp tests/setup.ts tests/server-only.ts "$TARGET/tests/"
cat >> "$TARGET/.gitignore" <<'EOF'
node_modules/
.next/
coverage/
dist/
.env
.env.*
!.env.example
EOF
```

These commands add the same reusable lifecycle/gate contracts and neutral app shell to the newly created app directory. They do not copy product requirements from another app. Inspect the output before proceeding; the initializer refuses non-empty targets, and the copy commands above target only the just-generated directory.

Initialize Git in the app directory and create its first commit only after reviewing the generated files. If using GitHub, create a new repository for this app and add it as the app repository's remote; do not reuse the template remote.

The app's repository is its source of truth after setup. Later changes to this template do not automatically overwrite the app's accepted product artifacts.

### 5. Complete the initial product contracts

In the new app repo:

1. Give the agent the app idea, intended user, observed problem evidence, desired outcome, constraints, and any supplied source material. The agent drafts `mission.md`, labeling evidence, assumptions, non-goals, and unknowns.
2. Have the agent lead product discovery and draft `constitution.md`, `specification.md`, and `backlog.md`, with linked decisions and testable acceptance outcomes.
3. Review material scope and risk decisions returned by the agent; record owner decisions in the app repository.
4. Have the agent define the full active journey set, platform behavior, design system, content, states, errors, accessibility, and prototype links in `design.md`.
5. Run required adversarial and CX reviews. Keep findings in review artifacts separate from the documents being reviewed.

Do not start implementation of dependent features while a blocking requirement, feasibility, coverage, CX, or architecture gate is failed or blocked.

### 6. Configure local runtime values when needed

Copy `.env.example` to `.env.local` in the app repo and set `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` from the app's Supabase project. The server boot guard prints `APP_INITIALIZATION_FAILED` and stops when either is absent or malformed. Never commit `.env.local`, put privileged keys behind a `NEXT_PUBLIC_` name, or rely on a publishable key without correct row-level security (RLS) policies. Keep `SUPABASE_SECRET_KEY` unset until an approved server-only feature needs it.

The template does not decide the app's schema, RLS policy, retention, deletion, backup, or recovery contract. Define and review these in the app's specification and architecture records before relying on the database in product behavior.

### 7. Choose and record tools for this app

The core lifecycle works with Markdown, Git, Python, and a human or any capable AI agent. ChatGPT Desktop, Codex, Figma, Impeccable, Supabase, and GitHub are integrations, not implicit product approvals. Record actual tool access and limitations in the app repository. Tool access never substitutes for a gate's evidence.

## The ten lifecycle gates

Each stage consumes durable files in the app repository and records an explicit gate outcome. New records are created when the work reaches the corresponding checkpoint; empty records are not evidence. Full contracts and allowed outcomes are in [GATE-CATALOG-001](docs/framework/GATE-CATALOG-001.md). The orchestrator and next-action rules are in [the lifecycle workflow](workflows/lifecycle.md).

| # | Gate and transition | Durable inputs and outputs in the app repository | Pass evidence |
| ---: | --- | --- | --- |
| 01 | **G-INTENT · Idea → project setup** | `mission.md`; evidence, assumptions, constraints, exclusions, and success signals. | Owner confirms the project is sufficiently framed; uncertainties stay visible. |
| 02 | **G-SETUP · Setup → specification** | App repository and remote (if chosen), `README.md`, `AGENTS.md`, five canonical SDD docs, local artifact helper, owner/access map. | A cold-start agent can locate the source of truth and next action; app boundary and permissions are clear. |
| 03 | **G-REQ · Requirements → feasibility/design** | `constitution.md`, `specification.md`, `backlog.md`, linked decisions, independent adversarial review under `reviews/`. | Requirement links, exclusions, and testable outcomes are coherent; blocking findings are resolved or explicitly accepted where allowed. |
| 04 | **G-FEAS · Assumptions → committed scope** | `architecture/feasibility-register.md`, evidence probes, owner/status, provider/data/legal/security/platform/cost/operations decisions. | Blocking dependencies are evidenced, mitigated, or removed from promises; scope matches proven feasibility. |
| 05 | **G-COVERAGE · Journeys → design critique** | `design.md`, complete journey/state inventory, requirement-to-journey map, platform matrix, prototype and exclusions. | Every applicable lifecycle and product journey is covered to reviewable depth across supported surfaces. |
| 06 | **G-CX · Design → architecture/build readiness** | Rendered design/prototype evidence, complete-scope critique, findings, fix dispositions, full affected-scope rerun under `reviews/`. | All findings have evidence-backed fixes and rerun results, or an authorized residual-risk acceptance where permitted. |
| 07 | **G-ARCH · Architecture → implementation** | `architecture/architecture.md`, `architecture/ADR-###.md`, data/trust contracts, reviewed backlog tasks, threat and operations assumptions. | High-impact risks and interfaces are understood; every task has acceptance and verification paths. |
| 08 | **G-IMPL · Task → integration/release candidate** | Code and migrations, focused tests, review record, CI results, `delivery/verification/`, updated `backlog.md`. | Selected task criteria and required checks pass with observed evidence; code review and open risks are recorded. |
| 09 | **G-RELEASE · Candidate → production** | `delivery/releases/` release record, web/native/security/accessibility checks, secrets/environment readiness, rollback and support plan. | Required app-specific evidence passes and the owner authorizes that specific production release. |
| 10 | **G-OPERATE · Operation → next learning cycle** | `operations/RUNBOOK.md`, health/usage/cost/support/incident records, user outcome, retrospective, linked backlog/decision updates. | An accountable operator is active; incidents and learning are captured and prioritized. |

**Transition rule:** a later gate never clears an earlier failed gate. Record `not ready`, `in progress`, `passed`, `failed`, `blocked`, or a permitted owner-accepted risk in a gate record; include the exact artifact versions, scope, platform, evidence, findings, decision authority, and next permitted action. The evidence determines the status, not elapsed time or a visual score.

### How the canonical files evolve

```text
G-INTENT       mission.md
G-SETUP        repository + README.md + AGENTS.md + canonical SDD files
G-REQ          constitution.md + specification.md + backlog.md + review record
G-FEAS         feasibility register + evidence + decisions
G-COVERAGE     design.md + journey inventory + platform matrix
G-CX           rendered prototype + critique + findings + rerun record
G-ARCH         architecture + ADRs + verified data/security contracts
G-IMPL         code + tests + review + observed verification record
G-RELEASE      release record + owner authorization + rollback plan
G-OPERATE      runbook + incidents + user outcomes + learning records
```

After each checkpoint, the agent updates the affected canonical file and backlog status in the app repository; the template repository is not used as a shared app work log.

## Design and engineering quality

- **Design:** mobile-first where user behavior warrants it; maintain feature and accessibility parity across supported web, Android, and iOS clients. Use Material 3 and Apple Human Interface Guidelines as platform references when applicable. Product-specific tokens and components belong in the app's reviewed `design.md`/brand kit.
- **Requirements:** cover foundational account/access, first-run, core actions, search/navigation, account settings, error/recovery, help/support, and exit flows when applicable; record why any category is out of scope.
- **Quality:** match verification to the target. Figma critique does not establish code quality. A web audit does not establish iOS or Android behavior. Release claims require runtime, security, accessibility, rollback, and operational evidence appropriate to the app.
- **Database:** define entities and ownership, authorization/RLS, migrations, validation, retention/deletion, backup, and failure behavior before implementation uses persistent data.
- **AI-first execution:** agents do routine artifact, code, and verification work. The owner is asked for material choices, access, legal/security authorization, unresolved risks, and product acceptance.

## Local artifact commands

The helper uses Python's standard library and operates relative to the repository containing it:

```sh
python3 scripts/artifacts.py list
python3 scripts/artifacts.py validate
python3 scripts/artifacts.py new ADR ADR-001 "Choose the event retention policy"
```

Validation checks artifact metadata, IDs, status vocabulary, and filename/ID consistency. It does not establish requirement completeness, cross-reference validity, gate passage, security, or production readiness. See [CAP-001](framework/capabilities/CAP-001-artifact-management.md).

## Current package status

This package is the separated boilerplate repository and is available from the owner's private GitHub account for application work. It contains no application-specific product requirements, prototype exports, or application worktree history. The repository remains private; public release is deferred until the owner has used the template to launch a couple of applications and separately authorizes a visibility change. The MIT license permits reuse, but it does not make this private repository public. Application work belongs in its own repository.

## References

- [Framework scope and exit criteria](docs/framework/FRAMEWORK-SPEC-001.md)
- [Current framework backlog](docs/framework/FRAMEWORK-BACKLOG-001.md)
- [Gate evidence contracts](docs/framework/GATE-CATALOG-001.md)
- [Tool and skill routing](docs/framework/TOOL-CATALOG-001.md)
- [Fresh-session bootstrap contract](framework/capabilities/CAP-000-template-initialization.md)
- [App-project starter contract](framework/capabilities/CAP-004-app-repository-bootstrap.md)
- [MIT License](LICENSE)
