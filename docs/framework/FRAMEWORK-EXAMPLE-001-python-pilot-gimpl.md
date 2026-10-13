---
id: FRAMEWORK-EXAMPLE-001
type: framework-verification-example
title: Python pilot verification matrix and G-IMPL example
status: active
version: 0.1
created: 2026-10-11
updated: 2026-10-11
related-artifacts: FRAMEWORK-BACKLOG-001, FRAMEWORK-PILOT-001, GATE-CATALOG-001, WORKFLOW-QUALITY-001
---

# FRAMEWORK-EXAMPLE-001 — Python pilot verification matrix and G-IMPL example

## Purpose and scope

This example supplies project-filled verification evidence for FW-TASK-006. It uses only the synthetic Framework Pilot Reading Queue's approved `APP-TASK-003` local Python ping slice. It does not represent the unimplemented queue task, a real customer product, a general Python coverage policy, or a web/native application.

The full pilot verification plan maps the broader queue requirements to planned methods. Those checks are not treated as executed by this example: APP-TASK-001 queue behavior remains outside the selected, completed ping slice.

The example is transcribed from the pilot repository's `PILOT-VERIFICATION-001` v1.3, `PILOT-VERIFY-002` v1.1, `PILOT-GATE-PING-IMPL-001` v1.1, and `PILOT-PING-REVIEW-001` v1.4, summarized in [FRAMEWORK-PILOT-001](FRAMEWORK-PILOT-001.md). The pilot repository was separately validated during this work: `python3 scripts/artifacts.py validate` reported 35 artifacts validated. The recorded test and coverage commands below were not re-executed for this example.

The pilot source was an uncommitted working tree on top of commit `61b196ec126d2bfb46614994fe627830d1b17bce`. That commit is the release rehearsal's baseline, not a source revision containing the ping implementation. The test record correctly identifies its target as a local uncommitted working tree; no source commit SHA was recorded. Do not cite the baseline SHA as the tested implementation revision.

## Project-filled verification plan excerpt

### Target and applicability

| Surface | Applicability | In-scope behavior | Verification method and observed environment | Evidence | Limits and exclusion reason |
| --- | --- | --- | --- | --- | --- |
| Local terminal on the development host | In scope | `python3 -m scripts.ping --ping` emits one JSON status object; invalid invocation is rejected; diagnostic does not access queue data. | Unit/integration suite under Python 3.13.2 on the recorded local macOS host; unsupported-version subprocess diagnostic under Python 3.9.6. | `PILOT-VERIFY-002`; `PILOT-GATE-PING-IMPL-001`; release behavior in `PILOT-RELEASE-PING-001`. | Evidence is limited to the recorded host and interpreter invocations. It does not prove all supported Python versions or operating systems. |
| Web | Out of scope | No web client, browser UI, or web service is part of APP-TASK-003. | Not applicable; no browser or web audit was run. | Scope declaration in `PILOT-MISSION-001` and `PILOT-VERIFICATION-001`. | This is a terminal-only slice. The exclusion does not waive web checks for an app that supports web. |
| iOS | Out of scope | No iOS client is part of APP-TASK-003. | Not applicable; no simulator/device build, VoiceOver audit, or native test was run. | Scope declaration in `PILOT-MISSION-001` and `PILOT-VERIFICATION-001`. | This is not evidence of iOS quality or parity. |
| Android | Out of scope | No Android client is part of APP-TASK-003. | Not applicable; no emulator/device build, TalkBack audit, or native test was run. | Scope declaration in `PILOT-MISSION-001` and `PILOT-VERIFICATION-001`. | This is not evidence of Android quality or parity. |

### Required-check matrix

The check IDs below are assigned by this framework example to demonstrate criterion-to-check traceability. The source pilot artifacts did not assign these IDs.

| Required check ID | Criterion / risk | Required check and procedure | Tool/runtime and scope | Pass condition | Recorded result and evidence | Limit |
| --- | --- | --- | --- | --- | --- | --- |
| PING-UNIT-001 | APP-TASK-003 AC-1: JSON contract, UTC timestamp, default checks, stdout, and exit semantics. | `python3.13 -m unittest discover -s tests -v` | Python 3.13.2; 12 tests cover `src/core/ping.py`, `scripts/ping.py`, and CLI behavior. | Tests assert one valid JSON object, boolean `success`, UTC `Z` timestamp, stable check names, stdout-only serialization, and exit code 0 after valid diagnostic output. | **Passed: 12 tests.** `PILOT-VERIFY-002` v1.1; outcome mapped in `PILOT-GATE-PING-IMPL-001` v1.1. | The separate Python 3.9.6 run is an unsupported-runtime diagnostic, not support certification for Python 3.9. |
| PING-FAILURE-001 | APP-TASK-003 AC-2 and AC-3: default runtime checks and failure paths remain deterministic and safe. | Same unittest suite, including supported/unsupported versions, zero checks, successful probes, exceptions, empty/non-string results, continuation after a failed probe, help, malformed options, and module entry point. | Python 3.13.2 test process; the suite launches the recorded Python 3.9.6 compatibility diagnostic. | Failure results contain the exception class only, do not retry or leak exception messages/tracebacks, and preserve the documented JSON/exit-code distinction. | **Passed** per `PILOT-VERIFY-002` v1.1 and `PILOT-GATE-PING-IMPL-001` v1.1; historical design/review finding R-10 and its resolution are in `PILOT-PING-REVIEW-001` v1.4. | The example reports the source record's observation; the suite was not rerun while this framework example was written. |
| PING-COVERAGE-001 | APP-TASK-003 AC-4: measured code coverage is complete for the declared source set. | `PYTHONPATH=/private/tmp/fw-task-009-coverage python3.13 -m coverage erase`; `PYTHONPATH=/private/tmp/fw-task-009-coverage python3.13 -m coverage run -m unittest discover -s tests -v`; `PYTHONPATH=/private/tmp/fw-task-009-coverage python3.13 -m coverage report --fail-under=100`; `PYTHONPATH=/private/tmp/fw-task-009-coverage python3.13 -m coverage json -o /private/tmp/fw-task-009-coverage/coverage.json`; `python3.13 scripts/check_ping_function_coverage.py /private/tmp/fw-task-009-coverage/coverage.json` | coverage.py 7.16.2 installed outside the application runtime; exact production scope: `src/core/ping.py` and `scripts/ping.py`. | 100% statements, branches, and lines for these two modules; separate AST function-entry check observes every top-level production function. | **Passed:** 50/50 statements, 14/14 branches, 100% line coverage, and function-entry metric 4/4. `PILOT-VERIFY-002` v1.1. | coverage.py does not natively report function coverage. “4/4” is the pilot's AST-based function-entry metric, not a function coverage percentage from coverage.py. This is not a repository-wide or universal threshold. |
| PING-CLI-001 | APP-TASK-003 AC-4 and recorded review invariant: help and invalid invocation communicate behavior. | Assertions in `tests/test_ping.py` through the unittest suite; recorded `python3.13 -m scripts.ping --help` observation. | Python 3.13.2; CLI module and test entry points. | Help explains that process exit 0 reports successful JSON emission while the JSON `success` field reports environment health; malformed invocation exits nonzero. | **Passed** per `PILOT-VERIFY-002` v1.1 and `PILOT-GATE-PING-IMPL-001` v1.1. | Does not assess usability with representative users. |
| PING-RELEASE-001 | APP-TASK-003 AC-5: local release behavior is reversible. | Separate, non-production detached-worktree rehearsal. See `PILOT-RELEASE-PING-001` and `PILOT-GATE-PING-RELEASE-001`. | Python 3.13.2 healthy path and Python 3.9.6 unsupported-runtime diagnostic. | Candidate emits the expected JSON in both cases; rollback/rehearsal cleanup is confined to disposable state. | **Passed in the separate G-RELEASE record**, not counted as a G-IMPL test. The rehearsal reports matching source-worktree porcelain status snapshots. | It did not record a full source-file checksum comparison and is not a production deployment or rollback. |

The pilot recorded local commands and no CI enforcement evidence for this task. Do not infer that these checks were required or enforced on a hosted pull request. A future app must define its own required checks, environment, revision, enforcement, and evidence locations in its verification plan.

## Completed sample G-IMPL record

### Gate identity and scope

- **Gate ID and transition:** G-IMPL, approved task to verified implementation.
- **Project:** Synthetic Framework Pilot Reading Queue, local repository `adversarial-sdd-pilot`.
- **Task and requirement:** APP-TASK-003; FR-PILOT-007 and NFR-PILOT-006.
- **Evidence date:** 2026-10-11, as recorded in the pilot artifacts.
- **Tested source revision:** local uncommitted working tree; no commit SHA was assigned to the tested ping source. Baseline `61b196ec126d2bfb46614994fe627830d1b17bce` is the separate rehearsal baseline only.
- **Source evidence artifact versions:** `PILOT-VERIFICATION-001` v1.3; `PILOT-VERIFY-002` v1.1; `PILOT-GATE-PING-IMPL-001` v1.1; `PILOT-PING-REVIEW-001` v1.4.
- **Reviewer:** independent code reviewer recorded in `PILOT-PING-REVIEW-001`; reviewer identity is not reproduced in this framework example.
- **Included paths:** `src/core/ping.py`, `scripts/ping.py`, their tests, coverage configuration, and the function-entry checker.
- **Excluded scope:** APP-TASK-001 queue functionality, Web, iOS, Android, cloud hosting, production deployment, and production operations.
- **Required-check source:** the pilot's approved task contract and `PILOT-VERIFICATION-001`; the template itself does not make its own checks universal requirements.

### Criteria and evidence

| Criterion | Evidence recorded by the pilot | Outcome |
| --- | --- | --- |
| JSON schema, UTC timestamp, default runtime checks, stdout, and exit behavior match the approved contract. | `PING-UNIT-001`; 12-test suite and command results in `PILOT-VERIFY-002` v1.1. | Pass — recorded in `PILOT-GATE-PING-IMPL-001` v1.1. |
| Probe exceptions and invalid results are handled safely and deterministically. | `PING-FAILURE-001`; safe class-only exception handling and continuation cases in `PILOT-VERIFY-002` v1.1. | Pass — recorded in `PILOT-GATE-PING-IMPL-001` v1.1. |
| Unsupported Python runtime includes `UnsupportedPythonVersion` and retains valid-JSON exit-0 behavior. | `PING-FAILURE-001`; Python 3.9.6 subprocess evidence in `PILOT-VERIFY-002` v1.1; review finding R-10 disposition in `PILOT-PING-REVIEW-001` v1.4. | Pass — recorded in `PILOT-GATE-PING-IMPL-001` v1.1. |
| Help text explains exit/health semantics and malformed invocation exits nonzero. | `PING-CLI-001`; CLI assertions and recorded help output in `PILOT-VERIFY-002` v1.1. | Pass — recorded in `PILOT-GATE-PING-IMPL-001` v1.1. |
| Statement, branch, and line coverage meet the task's scoped 100% acceptance threshold. | `PING-COVERAGE-001`; coverage.py 7.16.2 report: 50/50 statements, 14/14 branches, and 100% lines for the two named modules. | Pass — scoped to APP-TASK-003 source only. |
| Every top-level synchronous production function is entered by the test suite. | `PING-COVERAGE-001`; separate AST checker result: `_python_version`, `_python_implementation`, `build_status`, and `main` entered, 4/4. | Pass — pilot-defined function-entry metric; not native coverage.py function coverage. |
| Implementation review finds no unresolved blocker in the selected slice. | Final independent review in `PILOT-PING-REVIEW-001` v1.4; resolved finding R-10 and review rerun evidence. | Pass — recorded by independent reviewer in `PILOT-GATE-PING-IMPL-001` v1.1. |

### Gate outcome and boundaries

**Recorded outcome: PASS for APP-TASK-003 only**, as approved in `PILOT-GATE-PING-IMPL-001`. The example cites the pilot's record; it does not rerun the tests, create a new independent review, or grant a new gate approval.

The pilot's G-RELEASE rehearsal is a separate gate. Web, iOS, and Android remain out of scope and untested. The result does not verify queue functionality, validate a real product problem, establish cross-version or cross-operating-system support, prove accessibility or security beyond the recorded checks, demonstrate CI enforcement, or establish production readiness.

### Failure handling demonstrated

The independent review found a mismatch in the unsupported-runtime failure schema (R-10). The implementation and assertions were revised, and the independent reviewer reran the 12-test suite plus the recorded coverage and function-entry checks. The finding's disposition and rerun are preserved in `PILOT-PING-REVIEW-001`; the original issue is not hidden by the final pass status.

## Reuse rule

Copy the matrix structure, not the pilot's platform statuses, test commands, metrics, or coverage threshold. Each app must derive applicability and required checks from its approved requirements, architecture, task scope, and quality policy. Mark out-of-scope surfaces with explicit rationale; do not mark them passed. A G-IMPL record must identify the exact tested revision and distinguish committed code from an uncommitted working tree.
