---
id: FRAMEWORK-EXERCISE-003
type: framework-exercise
title: Progressive application onboarding and bootstrap regression exercise
status: in-review
version: 1.1
created: 2026-10-21
updated: 2026-10-21
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, WORKFLOW-DISCOVERY-001, CAP-004
---

# FRAMEWORK-EXERCISE-003 — Progressive application onboarding

## Active FW-TASK-021 follow-up record

- **Active gate:** G-IMPL for the reusable discovery procedure, bootstrap evidence, and exercise.
- **Selected task/scope:** FW-TASK-021 only. Add explicit synthetic intake traces and provenance/unknown classification for minimal input, existing-repository inspection, repeat setup, and the owner review boundary; add deterministic assertions that keep those scripted cases aligned with the discovery policy. Do not implement FW-TASK-022 dependency discovery or claim real-owner usability.
- **Acceptance evidence:** Independent review at `b6177c3651aef9fec363a168b076644b865062f5` passed bootstrap/file-integrity and synthetic-evidence-boundary claims, but marked question-flow and owner-review evidence partial. Close what can be evidenced with a clearly labeled scripted exercise, preserve limits, run initializer regression tests and artifact validation, then obtain a fresh independent review.
- **Known blockers:** This remains framework-process evidence. It cannot establish human comprehension, observed AI behavior across runs, or real application gate approval.

## Purpose and evidence boundary

Exercise the FW-TASK-021 startup path against empty, partial, existing, changed, and unsafe target states. This is synthetic framework-process evidence. It is not customer research, owner approval of a product mission, a passed application gate, or proof of usability with real owners. Any simulated dialogue below is a test fixture, not an observed human or independent-model session.

## Frozen acceptance rubric

| Case | Starting condition / input | Required behavior | Evidence to retain |
|---|---|---|---|
| Empty new app, minimal intent | Empty sibling target; one-sentence app idea; no stack/provider decisions | Inspect empty target; request only the app identity/target needed by initializer; preserve unknowns; create draft artifacts only | Initializer output, generated file list, app validator result, post-run summary |
| Partial input and unknown answers | Owner knows user/problem but not platform, provider, region, or budget | Do not force answers unrelated to next safe step; classify each unknown and its impact/owner or later gate | Frozen synthetic prompt and expected question/unknown classification |
| Existing application repository | Non-empty source tree with repository instructions, code, manifests, and Git state | Inspect repository and SDD state before questions; do not run initializer; distinguish observed facts from assumptions; propose only scoped follow-up | Fixture file inventory, inspected facts/source references, expected next action |
| Repeat after context change | Existing accepted intent with one changed platform or outcome constraint | Reopen only impacted questions/decisions and dependent tasks; preserve unaffected accepted intent | Before/after decision matrix and synthetic continuation transcript |
| Invalid target | Non-empty or unsafe target passed to initializer | Fail before writing; preserve target bytes; report actionable error | Existing initializer negative test output and target digest comparison |
| Owner review boundary | Candidate starter generated, no owner approval recorded | Present captured intent, unknowns, decisions needed, generated files, current gate, and next action before Git/remote/publication; do not infer PASS | Expected owner-facing summary and gate-state assertion |

## Synthetic scenario fixture

**Owner input:** “I want a simple inventory tool for a small repair shop. Staff lose time finding parts. I have heard this from one shop owner, but I have not written down the interview. I do not know yet whether it needs a phone app, a web app, a provider, or a monthly budget. I want to explore the problem before choosing technology.”

**Provenance treatment:** The sentence and reported interview are owner statements. The interview itself is not supplied evidence and cannot be cited as an observed research artifact. The user, problem, and intended outcome remain provisional until the owner reviews the mission. Platform, provider, budget, retention, and regional requirements remain unknown; they do not block creating draft SDD files but block any dependent technical promise.

**Expected first response:** Ask for a project name/short ID prefix and a new empty target only if those are not already supplied, explain that unknowns can remain open, then create draft files. Do not ask the owner to select a database, cloud, model, app platform, pricing plan, legal policy, or CI provider before discovery shows why that choice is needed. After generation, report files created, provenance-labeled unknowns, owner decisions still needed, current gate as not approved/in-progress, and next action: review the draft mission and approve or revise it.

**Repeat scenario:** Owner later says, “We need barcode scanning on phones in the first release.” Reopen platform/device capability, camera permission, offline behavior, and related journey/feasibility questions. Preserve the stated repair-shop audience and part-finding problem unless new evidence contradicts them. Do not silently promote barcode scanning into an approved requirement; record it as a changed owner statement pending specification review.

## Scripted intake traces — synthetic, not observed conversations

These expected outputs make the tabletop reproducible for a reviewer. The labels below are fixture inputs and expected agent behavior; they are not transcripts from a human interview or proof that every model follows the workflow.
The corresponding machine-readable expectations live in [`tests/fixtures/fw021_discovery_scenarios.json`](../../tests/fixtures/fw021_discovery_scenarios.json); [`test_fw021_discovery_exercise.py`](../../tests/test_fw021_discovery_exercise.py) checks the question set, unknown routing, provenance, repeat-state handling, and review boundary. These assertions keep the fixture and written policy aligned; they do not execute an AI intake conversation.

### Empty target with minimal intent and unknown answers

**Fixture input:** The repair-shop inventory idea above. The operator has not supplied an app name, artifact prefix, or target path.

**Permitted setup questions:** “What should the project be called, what short artifact prefix should it use, and where is a new empty target directory?” The setup may proceed after those three bootstrap values are supplied. It does not ask the owner to choose a platform, provider, region, budget, license, or database just to create draft files.

| Intake item | Provenance / classification | Impact and resolver | Next action |
|---|---|---|---|
| Staff lose time finding parts; one shop owner reportedly mentioned the issue | Owner statement; interview notes were not supplied, so demand evidence remains unknown | Intent confidence is limited; owner may provide notes or authorize later research | Draft the mission with the interview explicitly labeled as an unverified report |
| A numeric time-saving target | Unknown; no baseline supplied | Needed before a measurable success target can be approved; owner or later baseline study resolves it | Leave target provisional and identify a measurement plan in discovery |
| Phone, web, or both | Owner decision, not a research fact | Blocks promising platform-specific behavior, not creation of draft SDD files | Keep platform open; revisit before platform-dependent requirement/design work |
| Provider, region, monthly budget, and data retention | Unknown; provider availability/pricing may need dated research after requirements identify a dependency | Blocks provider-specific and cost promises; owner decides choices, research/access resolves factual availability | No provider or external access is needed for bootstrap; carry these to relevant discovery/G-FEAS work |
| App name, artifact prefix, empty target | Blocking setup inputs only | Owner supplies these before initialization | Initialize draft artifacts after verifying the target is empty |

**Expected post-initialization review:** “Created the five canonical SDD drafts and starter support files in `<target>`. The repair-shop need and reported interview are owner statements; interview evidence and a success baseline are not supplied. Platform, provider, region, budget, and retention remain open and do not block this draft setup. No provider or remote was accessed. G-INTENT is not approved; please review `mission.md` and approve or revise it. No Git repository, remote, commit, publication, or gate PASS was created.”

### Existing application repository with inaccessible owner/product evidence

**Synthetic fixture inventory (observed within the fixture):** `README.md`, `AGENTS.md`, `pyproject.toml`, `src/inventory.py`, a CI workflow, Git branch `main`, no remote, and no canonical SDD documents. No credentials are read. There is no owner statement in this fixture about the intended change, and no external research was performed.

**Expected response:** Do not run the initializer or copy starter files over this repository. Report the inventory as observed facts. Treat “Python project” as a bounded inference from `pyproject.toml`, not an owner-selected stack. Mark product intent, user, permissions, and source-control destination unknown. Ask only what outcome/change the owner wants to pursue and whether a path-specific SDD bootstrap/migration is desired. Remote creation and credentials are not necessary for this inspection; if a remote is later requested, owner access/authorization is an external prerequisite. Any migration remains a separate reviewed action.

### Repeat setup after one changed constraint

| Item | Previously accepted/current state | New input | Expected disposition |
|---|---|---|---|
| Audience | Small repair-shop staff | No change | Preserve without asking again |
| Problem | Staff lose time finding parts | No change | Preserve; do not reopen absent contrary evidence |
| Barcode scanning | Not in agreed first-release scope | “We need barcode scanning on phones in the first release.” | Record as a new owner statement; ask whether offline scanning is required and which phone surfaces are in scope; mark acceptance pending |
| Camera permission, offline behavior, supported devices, accessibility | Not yet analyzed | Made relevant by barcode scanning | Reopen only these questions; assign feasibility research/owner decisions and affected requirement/task links when those IDs exist |
| Provider, region, and budget | Unknown and not currently blocking draft intent | No new evidence | Preserve as unknown; do not ask again unless the selected barcode approach makes them material |

**Expected next state:** Keep existing approved intent unchanged, mark the changed barcode scope as pending owner decision, and block only dependent platform/provider promises. Do not silently revise requirements or infer a gate transition from the conversation.

### Owner review and outward-action boundary

**Synthetic expected handoff:** Show the captured owner statements, observed files, researched claims (none in the minimal fixture), inferences, unresolved unknowns and their impacts, decisions requested, generated paths, current gate state, and next permitted action. Stop at “review the draft mission”; do not initialize Git, create a remote, commit, push, publish, or claim PASS before owner review/authorization. This demonstrates the specified handoff content and procedural boundary only; it does not claim an automated filesystem or Git sandbox prevents an agent from taking an outward action.

## Execution record

**Filesystem/bootstrap run — 2026-10-21:** At framework source revision `e0a5c25034c32d1787276138fc0d7773c5aaa586` using Python 3.13.2, the initializer created 25 files in an empty temporary target. The README's no-clobber template composition was exercised against the same copied framework folders; all files listed by `.sdd/framework.lock.json` retained their original SHA-256 digests. The complete composed app tree contained 106 files and its copied helper reported `Validated 23 artifact(s).` The five canonical app documents had the requested `REPAIR` identity, remained `draft`, and contained no `<APP>` or `TARJEM-` stale sample markers. A non-empty target returned exit code 2 and its sentinel file hash and directory contents were unchanged.

**Existing-repository fixture:** A synthetic source tree with README, AGENTS, `pyproject.toml`, `src/inventory.py`, CI workflow, Git branch `main`, and no remote was inventoried. The workflow directs the agent to inspect these facts and not invoke the initializer. This was fixture inspection, not an observed AI interview.

**Question-flow cases:** The synthetic expected outputs above are an inspectable scripted exercise for minimal/unknown input, existing-repository inspection, a single changed constraint, and the owner review boundary. They provide reviewable sample behavior, not observed conversations or proof of model conformance. No real owner interview or product G-INTENT/G-SETUP approval occurred. Keep all synthetic observations labeled as framework-process evidence.

**Framework checks — 2026-10-21:** `python3 -m unittest discover -s tests -v` passed all 85 tests; `python3 scripts/artifacts.py validate` reported 48 artifacts; `git diff --check` passed. These checks ran after the no-clobber correction and exercise record were committed at `e0a5c25034c32d1787276138fc0d7773c5aaa586` (the final exercise/checkpoint edits themselves are a follow-up evidence change).

**Earlier failed attempts:** Ordinary recursive template copying overwrote the generated locked gate template and was rejected by app validation. macOS `cp -Rn` then returned non-zero on the expected no-clobber collision. The documented Python-standard-library copier fixed both issues; the passing run above is after that correction.

## Limitations

- The progressive intake is an agent workflow, not a deterministic product-discovery oracle. The traces specify expected behavior but do not prove that a deployed model will follow it consistently; real-owner usability and product-gate evidence remain untested.
- The exercise does not establish owner comprehension, real-market demand, successful provider access, stack support, or product feasibility.
- Existing app migration remains separate from initialization. The initializer deliberately refuses non-empty targets.
- The recorded run checked the exact generated file inventory, draft status through validator behavior, named stale markers, and locked-file digests. It did not perform a general scan for every possible stale-history or credential-like string; do not claim comprehensive secret or historical-state detection.
