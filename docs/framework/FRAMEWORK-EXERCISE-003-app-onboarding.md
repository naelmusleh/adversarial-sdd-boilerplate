---
id: FRAMEWORK-EXERCISE-003
type: framework-exercise
title: Progressive application onboarding and bootstrap regression exercise
status: in-review
version: 1.0
created: 2026-10-21
updated: 2026-10-21
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, WORKFLOW-DISCOVERY-001, CAP-004
---

# FRAMEWORK-EXERCISE-003 — Progressive application onboarding

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

## Execution record

**Filesystem/bootstrap run — 2026-10-21:** At framework source revision `e0a5c25034c32d1787276138fc0d7773c5aaa586` using Python 3.13.2, the initializer created 25 files in an empty temporary target. The README's no-clobber template composition was exercised against the same copied framework folders; all files listed by `.sdd/framework.lock.json` retained their original SHA-256 digests. The complete composed app tree contained 106 files and its copied helper reported `Validated 23 artifact(s).` The five canonical app documents had the requested `REPAIR` identity, remained `draft`, and contained no `<APP>` or `TARJEM-` stale sample markers. A non-empty target returned exit code 2 and its sentinel file hash and directory contents were unchanged.

**Existing-repository fixture:** A synthetic source tree with README, AGENTS, `pyproject.toml`, `src/inventory.py`, CI workflow, Git branch `main`, and no remote was inventoried. The workflow directs the agent to inspect these facts and not invoke the initializer. This was fixture inspection, not an observed AI interview.

**Question-flow cases:** Minimal/unknown input, an existing accepted intent with one changed platform constraint, and the owner-facing pre-publication summary were walked against the frozen rubric as tabletop cases only. No real owner interview or independent model run occurred. Their outcomes remain unverified until an independent reviewer checks the dialogue burden and provenance behavior. Keep all synthetic observations labeled as framework-process evidence; they do not pass G-INTENT/G-SETUP for any real application.

**Framework checks — 2026-10-21:** `python3 -m unittest discover -s tests -v` passed all 85 tests; `python3 scripts/artifacts.py validate` reported 48 artifacts; `git diff --check` passed. These checks ran after the no-clobber correction and exercise record were committed at `e0a5c25034c32d1787276138fc0d7773c5aaa586` (the final exercise/checkpoint edits themselves are a follow-up evidence change).

**Earlier failed attempts:** Ordinary recursive template copying overwrote the generated locked gate template and was rejected by app validation. macOS `cp -Rn` then returned non-zero on the expected no-clobber collision. The documented Python-standard-library copier fixed both issues; the passing run above is after that correction.

## Limitations

- The progressive intake is an agent workflow, not a deterministic product-discovery oracle. Independent review must inspect its question burden, provenance handling, and tendency to invent facts.
- The exercise does not establish owner comprehension, real-market demand, successful provider access, stack support, or product feasibility.
- Existing app migration remains separate from initialization. The initializer deliberately refuses non-empty targets.
