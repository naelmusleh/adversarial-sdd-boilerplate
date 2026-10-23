---
id: FRAMEWORK-FEASIBILITY-009
type: feasibility-register
title: FW-TASK-028 risk-quality and traceability feasibility
status: draft
version: 1.0
created: 2026-10-23
updated: 2026-10-23
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-ADV-020, FRAMEWORK-ADV-021, DECISION-026, FRAMEWORK-EXERCISE-007
---

# FRAMEWORK-FEASIBILITY-009 — FW-TASK-028 risk-quality and traceability feasibility

## Scope and exclusions

This is a bounded G-FEAS plan for FR-FW-029–031 under DECISION-026. It examines whether three already exercised synthetic framework profiles—Next.js/TypeScript, FastAPI/Python, and Rust/Axum—can report useful coverage and mutation evidence, bind task criteria to changed paths and checks at an exact revision, and expose anti-gaming limits.

The work uses generated toy fixtures on a disposable, secret-free hosted runner. It does not set numeric thresholds, change the framework repository's current checks, classify a real product task, collect user/product data, approve an exception, adopt another gate contract, implement FW-TASK-028, or authorize FW-TASK-024 or other v2 tasks. Measurement availability and cost are feasibility inputs, not policy decisions.

## G-REQ and source baseline

G-REQ passed for exact scope revision `dc4c982effad35652802278d301b532c555c6388`; independent findings are in [FRAMEWORK-ADV-020](../adversarial-reviews/FRAMEWORK-ADV-020.md). The approved requirements and seven backlog criteria remain the scope. FW-TASK-013 already exercised the three synthetic profile toolchains on hosted runners; its exact limitations and run evidence remain in [FRAMEWORK-FEASIBILITY-008](FRAMEWORK-FEASIBILITY-008-fw013.md) and [FRAMEWORK-ADV-019](../adversarial-reviews/FRAMEWORK-ADV-019.md). These are reusable setup observations, not evidence for FW-028 policy or anti-gaming behavior.

## Dated technical observations

Official tool documentation indicates candidate measurement capabilities:
- Vitest documents V8 and Istanbul coverage providers and coverage collection/configuration. Coverage is execution evidence and does not establish assertion quality: [Vitest coverage guide](https://vitest.dev/guide/coverage.html).
- Coverage.py documents branch measurement through its `--branch` option: [Coverage.py documentation](https://coverage.readthedocs.io/en/latest/).
- LLVM `llvm-cov` exports line and branch coverage; the `cargo-llvm-cov` subcommand is a candidate Rust adapter: [LLVM coverage command guide](https://llvm.org/docs/CommandGuide/llvm-cov.html), [cargo-llvm-cov project](https://github.com/taiki-e/cargo-llvm-cov).
- StrykerJS documents TypeScript/JavaScript mutation testing support: [StrykerJS introduction](https://stryker-mutator.io/docs/stryker-js/introduction/).
- Mutmut is a Python mutation-testing candidate: [mutmut documentation](https://mutmut.readthedocs.io/en/latest/).
- cargo-mutants is a Rust mutation-testing candidate: [cargo-mutants documentation](https://mutants.rs/).

For a first reproducible probe, freeze these candidate pins as observed from official project documentation/registries on 2026-10-23: Node.js 22.23.3 and npm 12.1.0 (FW-013 hosted profile baseline), Vitest and @vitest/coverage-v8 5.0.5, Stryker core and Vitest runner 10.0.0, TypeScript 5.9.3; Python 3.13.2, pip 26.2.2, pytest 9.1.1, Coverage.py 7.16.2, mutmut 3.7.0; Rust/Cargo 1.97.0, cargo-llvm-cov 0.9.1, cargo-mutants 27.1.0. Pins and transitive lock digests are candidate experiment inputs, not ongoing recommendations. Sources: [Vitest 5 coverage package](https://www.npmjs.com/package/@vitest/coverage-v8), [Stryker core](https://www.npmjs.com/package/@stryker-mutator/core), [Stryker Vitest runner](https://www.npmjs.com/package/@stryker-mutator/vitest-runner), [Coverage.py 7.16.2](https://pypi.org/project/coverage/7.16.2/), [mutmut 3.7.0](https://pypi.org/project/mutmut/3.7.0/), [cargo-llvm-cov 0.9.1 release](https://github.com/taiki-e/cargo-llvm-cov/releases/tag/0.9.1), and [cargo-mutants 27.1.0](https://docs.rs/crate/cargo-mutants/27.1.0). These documents establish candidate capabilities, not compatibility with each other or directly comparable scores. Mutation operators, equivalent-mutant handling, generated-code treatment, test selection, runtime, and tool support can vary. The probes must retain exact toolchain/tool versions and classify unsupported or unavailable results explicitly.

## Applicability screen

Applicable: toolchain installation and runtime compatibility; coverage and mutation report semantics; test fixture integrity; exact commit/path/check metadata; authorization evidence for exceptions; runner cost and duration; registry egress and supply-chain exposure; reproducibility and artifact retention.

Not applicable to this synthetic probe: real product security classification, customer/privacy data, data rights, application deployment, provider costs, production service SLOs, photo/media behavior, release authorization, and operational support. No production threshold or user-data decision is made.

Security boundary: use a temporary GitHub-hosted VM, read-only permissions, no secrets, no persistent checkout credentials, no product data, no source/host mounts, and no privileged token in child processes. Package-registry/network egress during setup remains exposed and must be disclosed. If a safe read-only runner cannot execute a probe, mark it unavailable; do not weaken permissions or claim isolation.

## Frozen setup and deterministic fixture catalog

The probe generator and temporary workflow must be committed and reviewed before execution. Generate three isolated toy workspaces from one versioned fixture manifest; retain the generator and manifest SHA-256. Use an ephemeral `ubuntu-24.04` runner. Each profile is sequential, has a 15-minute soft budget and 20-minute hard timeout; the full job has a 60-minute hard timeout. Record unavailable/tool-install/timeout separately from a failed assertion. Resolve and retain exact lockfiles before the clean replay; no floating version tags or unpinned package installs are allowed.

| Profile | Exact setup and commands |
| --- | --- |
| Next.js/TypeScript | Node 22.23.3, npm 12.1.0; direct pins Vitest/@vitest/coverage-v8 5.0.5, @stryker-mutator/core/@stryker-mutator/vitest-runner 10.0.0, TypeScript 5.9.3. Generate package manifest and run `npm install --package-lock-only --ignore-scripts --no-audit --no-fund`; clean replay with `npm ci --ignore-scripts --no-audit --no-fund`; run `npm exec -- vitest run --coverage`, then `npm exec -- stryker run --concurrency 1 --reporters clear-text,json`. |
| FastAPI/Python | Python 3.13.2; create a clean venv, install pip 26.2.2, then install pytest 9.1.1, coverage 7.16.2, mutmut 3.7.0 from exact direct pins; capture `python -m pip freeze --all > requirements.lock`, create a second clean venv, install with `python -m pip install -r requirements.lock`, and run from the clean replay. Run `python -m coverage run --branch -m pytest -q`, `python -m coverage json -o coverage.json`, and `mutmut run`. |
| Rust/Axum | Rust/Cargo 1.97.0 edition 2024; exact Cargo dependencies from a retained lockfile. Create and retain Cargo.lock from exact direct dependencies, then clean replay with `cargo fetch --locked`. Install with `cargo install cargo-llvm-cov --locked --version 0.9.1` and `cargo install cargo-mutants --locked --version 27.1.0`. Run stable line/region coverage as `cargo llvm-cov --json --output-path target/coverage.json`; separately attempt `cargo llvm-cov --branch --json --output-path target/branch-coverage.json` and `cargo mutants --no-shuffle --timeout 30`. If branch mode, the tool, or exact pinned install is unsupported on the stable toolchain, record that metric unavailable; do not change toolchain or substitute an unpinned version. |

The identical hand-authored behavior fixture is `classify(n) = "positive" if n > 0 else "nonpositive"`. A coverage-only test invokes `classify(1)` without asserting its result; the assertion test checks both `classify(1) == "positive"` and `classify(0) == "nonpositive"`. The paired mutant changes only `n > 0` to `n >= 0`. Expected outcomes: the no-assertion test executes the positive branch and still exits successfully against the mutant; the assertion test fails against the mutant at `n=0`. Each profile must report source/branch outcomes where its tool supports them. This is a named toy mutant, not a comparable mutation score or proof of semantic quality.

The trace probe uses an explicit manifest fixture with this canonical shape: `repository`, `source_commit`, `task_id`, sorted complete `criterion_ids`, sorted `changed_paths`, sorted `required_checks`, `generated_paths` entries with declared treatment/rationale, and `exceptions`. The probe computes the Git changed-path set for the supplied base/head and compares exact commit, task/criteria completeness, path set, and the named check-result set. Expected diagnostic strings identify each bad field, for example `stale source_commit`, `missing criterion FR-FW-030/AC-5`, `unmapped changed path src/ui/card.tsx`, and `missing required check TypeScript Static Code Analysis`. It must not write to the fixture repo. A synthetic exception with only a free-text `approved_by` must be rejected. A positive exception is accepted only if the workflow can independently read a matching approval by an app-configured authorized identity against the same pull request/head commit; otherwise report authorization as unsupported and keep the path fail-closed.

The deterministic test commands select one fixture test in each generated workspace: TypeScript uses `npm exec -- vitest run tests/quality.test.ts`; Python uses `python -m pytest -q tests/test_quality.py`; Rust uses `cargo test --locked --test quality_fixture`. The harness switches only between checked-in/generated original and mutant copies, records each copy's SHA-256, runs all four pair combinations, and checks the required exit-code matrix. The mutation tools are not allowed to modify the canonical fixture tree; each tool gets a fresh disposable copy, and its report is considered only if it identifies the same comparator mutant and the relevant test outcome. Otherwise tool integration is unavailable while the native four-case experiment remains interpretable.

Anti-gaming fixtures and exact outcomes:

| Fixture | Input mutation | Required observable result |
| --- | --- | --- |
| Ineffective assertion | Replace the assertion test with a call-only test | Test exits 0 for original and mutant; report explains that execution/line coverage cannot establish assertion adequacy. |
| Omitted export | Each profile declares expected `classify` in a checked-in independent `expected_exports.json`; remove the public declaration/export from the module | A separate consumer contract test fails with a named missing-export diagnostic. TS checks module namespace keys; Python imports the named symbol; Rust compiles an integration test importing the expected public item. |
| Generated-file accounting | A generated fixture carries a marker and has an explicit path/policy entry with `include` or `exclude` plus rationale | Declared include/exclude appears in measured/unmeasured inventory exactly as configured; deleting its policy entry yields `unclassified generated path` and no silent exclusion. |
| Mixed-scope trace | Synthetic Git diff changes one task-mapped policy path plus an unrelated UI path | Trace check names the unmapped UI path; adding an authorized exception yields a pending/accepted exception result only if provider identity evidence validates. |
| Stale or incomplete trace | Change source SHA, remove one criteria ID, required check, or changed-path mapping | Each case rejects with the relevant missing/stale diagnostic. |

The fixture generator records SHA-256 for the generator, manifests, and complete input tree before execution; the harness compares the tree digest after all tests and mutation-tool runs. All test/mutant execution occurs in disposable generated directories. A mismatch is a hard stop and invalidates the probe. No workflow checkout token is persisted (`actions/checkout` uses `persist-credentials: false`); workflow permissions are `contents: read`; no token is passed to package, test, or mutation subprocesses. The runner has outbound registry access during setup; that risk is documented rather than described as network-isolated.

## Probe register

| Probe | Question and exact evidence | Classification rule | Requirements / dependency |
| --- | --- | --- | --- |
| FEAS-FW028-01 — coverage adapters | For each synthetic profile, can a clean target produce named line and branch/condition reports from pinned tools, identify measured source files and exclusions, and distinguish unavailable from zero or pass? Capture toolchain/tool versions, source and config digests, exact command/exit code, raw summary, excluded/generated paths, and repeated-run stability. | Supported only for exact profile/tool pins and report fields observed. A missing provider, unsupported metric, or missing report is unavailable/unsupported, never pass. No numeric threshold is evaluated. | FR-FW-029; FW-TASK-028 remains conditional on exact adapters and honest missing-metric behavior. |
| FEAS-FW028-02 — test-strength signals | In each profile, use a hand-authored original source file and a paired mutant source file differing only by `n > 0` versus `n >= 0`. Run the same profile-native test runner in four isolated cases: original+call-only, mutant+call-only, original+assertions, mutant+assertions. Required outcomes are pass, pass, pass, fail at the `n=0` assertion, respectively. Record the source digest and exact test command/exit code for every case. This controlled pair—not a general mutation-tool run—is the evidence that the call-only test can execute code yet miss the named behavior change. Run StrykerJS, mutmut, and cargo-mutants separately only to assess whether each tool can report a selected equivalent mutant on this tiny fixture; if it cannot select that mutant by identity and associate it with both test variants, classify that tool integration unavailable and do not infer the controlled-pair result from its general report. | Demonstrates only the named mutation operators and fixtures. Do not compare mutation percentages across languages or treat a killed mutant as proof of correctness. If tooling cannot run reproducibly within a declared pilot budget, record that limitation and an alternative evidence path. | FR-FW-029, FR-FW-031; critical-invariant evidence remains a per-app policy choice. |
| FEAS-FW028-03 — exact task/path/check trace | On a frozen synthetic Git revision, map one selected task ID and all its acceptance-criteria IDs to changed paths and required check IDs. Exercise a valid complete mapping, an unmapped changed path, missing criterion, missing required check, stale source revision, and an authorized exception record. Capture manifest/source digests, Git diff path set, check identity/conclusion, diagnostics, and whether any source bytes changed. | Mapping is deterministic and revision-bound; stale/missing/unmapped cases fail closed or require an explicit exception. The probe must identify an independently verifiable authorization source. A free-form author name or self-asserted JSON field is insufficient evidence of authority. | FR-FW-030; exception authority and record fields are an open design item, not presumed resolved. |
| FEAS-FW028-04 — anti-gaming and exclusions | Try deliberately misleading cases: high line coverage with ineffective/trivial assertions; omitted exported symbol; generated file counted or excluded without declaration; and unrelated mixed-scope file. Check whether policy/trace validators surface each case without editing or deleting source. | Report what deterministic checks actually detect. If a case requires human judgment (e.g. an export is intentionally obsolete or a test assertion is semantically weak), classify it as review-required; no static metric may claim to prove semantic test quality or product intent. | FR-FW-031 and FW-TASK-028 criteria 2, 4, 6, 7. |

## Candidate trace and exception evidence

The probe should test a versioned, machine-readable trace shape carrying: repository identity; exact source commit; selected task ID; the complete selected acceptance-criteria ID set; changed canonical paths; required check IDs/names and exact run conclusions; declared generated/excluded paths with rationale; and trace-manifest revision/digest.

An exception candidate binds one missing/unmapped element to the exact source revision, task and criteria, affected path/check, reason, scope, authenticated authorizer identity and role, review/run reference, creation time, and expiry or revisit condition. The application must declare permitted authorizer roles. G-FEAS must establish whether the chosen CI/review provider can independently verify the identity and approval at that revision. The reviewer flagged this as unresolved at G-REQ; no particular user, role, team, or exception is pre-approved.

## Run method and safety

1. Have the independent reviewer assess this exact plan and fixture design before execution.
2. Freeze plan, generator, and workflow revisions. Use only generated toy code in temporary workspaces.
3. Run the four probes on a disposable hosted Linux VM using exact setup pins and read-only workflow permissions; do not pass the repository token into package/test/mutation processes.
4. Retain only bounded summaries: exact commit, OS/architecture, versions, paths/digests, named outcomes, duration, and error classification. Do not upload full source or environment variables.
5. Delete the temporary workflow and generated files after evidence capture. Run the repository's existing Verify Pipeline on the final evidence commit.
6. Update every probe's per-task dependency state and request independent review of the observed results. Stop on any false authorization, source mutation, secret exposure, missing exact-revision binding, or runner-boundary violation.

## G-FEAS acceptance and boundary

G-FEAS may pass only if the frozen probes establish feasible, bounded profile-specific metrics; show why raw coverage alone can mislead; demonstrate the available strength/limits of mutation and contract evidence; verify deterministic trace mapping and stale/missing behavior; and either verify an independent authorization source for exceptions or explicitly keep exceptions blocked pending a future owner-authorized alternative. Any unsupported metric or unverified authorization path must be reported as such and cannot produce a PASS claim. No numeric threshold is selected here.

Even a G-FEAS PASS would authorize only architecture planning within DECISION-026. Implementation remains blocked pending subsequent gate evidence. The framework repository's current test/coverage policy is unchanged. FW-TASK-024 and all other proposed v2 work remain excluded.

## Initial status

Plan prepared 2026-10-23. First independent review blocked execution for missing exact pins/commands and underspecified omitted-export/generated-file fixtures. This revision adds pinned candidate toolchains, concrete commands, fixture contents and expected outcomes, frozen input/tree digests, source-mutation detection, permissions and timeouts. No FW-028 feasibility probe has run. The three FW-013 profile toolchains remain prior setup observations only. The second independent review found that the previous plan did not bind the named mutant to both test variants. This revision makes the four-case original/mutant matrix a standalone required test-runner probe and treats third-party mutation-tool reporting as separate, optional capability evidence. No probe has run. Because two consecutive independent-review rounds have now occurred, a further reviewer round requires the owner's explicit approval under the repository operating contract.
