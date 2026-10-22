---
id: FRAMEWORK-ADV-014
type: adversarial-review
title: FW-TASK-026 transactional gate runner review
status: in-review
version: 0.1
created: 2026-10-22
updated: 2026-10-22
reviewed-artifact: FW-TASK-026
reviewed-version: a6e90a65057e87f27b1a7a61b963b09893c3495c
related-artifacts: GATE-RUNNER-001, FRAMEWORK-SPEC-001, FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-BACKLOG-001, DECISION-LOG-001
---

# FRAMEWORK-ADV-014 — FW-TASK-026 transactional gate runner review

## Review scope and basis

- **Reviewed revision:** `a6e90a65057e87f27b1a7a61b963b09893c3495c` on `codex/v2-backlog-roadmap`.
- **Reviewer:** `/root/fw021_review`, read-only review independent of the implementation edits.
- **Scope:** FR-FW-019 through FR-FW-021 and the FW-TASK-026 acceptance criteria. This report evaluates local source and test evidence; it does not certify hosted repository controls.
- **Disposition:** **BLOCK — FW-TASK-026 remains in progress.** The local implementation checkpoint is useful and its identified security fixes are verified, but two acceptance requirements remain unproven.

## Findings

| ID | Severity | Finding | Evidence and disposition |
|---|---|---|---|
| ADV-014-01 | Major | Positive append/transition paths are not demonstrated for G-SETUP through G-OPERATE. | `tests/test_gate_runner.py::test_candidate_validation_routes_every_gate_fixture` accepts G-INTENT only; every downstream candidate is rejected because its prerequisite run is absent. The transition plan enumerates legal/illegal result combinations but is not an end-to-end accepted record route. Keep acceptance criterion 2 open; do not manufacture PASS evidence. |
| ADV-014-02 | Major | Hosted policy rehearsal is unavailable. | Verify Pipeline code checks are running for the reviewed SHA, but branch-protection read returned GitHub API 403 `Resource not accessible by integration`. A passing workflow run alone cannot establish that repository rules prevent merging invalid transition evidence. Keep acceptance criterion 5 open and do not claim protection. |

## Closed findings

- The local interprocess lock rejects a symlinked lock path and tests that an external target remains untouched.
- Atomic record publication rejects symlinked/out-of-repository record paths, refuses overwrite, cleans interrupted staging, and tests lock contention and failure cleanup.
- Candidate source snapshots must match current HEAD and a clean worktree, or digest-pin archive inputs; stale source tests reject mismatch.
- Append commands catch `ValueError` and report controlled errors; malformed lock version types fail closed.
- Advisory review records are schema-bounded, bind frozen input digests, and cannot claim gate, CI, or owner-authorization authority.

## Verification and limits

At this revision, local checks passed: 15 focused gate-runner tests, 130 Python governance/initializer tests, 51 framework artifacts, TypeScript typecheck, 30 Vitest tests, 100% configured statements/branches/functions/lines, production build, and `git diff --check`. These results establish the tested local behavior only. Hosted Verify Pipeline run [39710112306](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39710112306), attempt 1, event `push`, against the exact reviewed SHA completed successfully with all three jobs passing. No branch-protection or ruleset state was observable through the connected GitHub integration; the branch-protection read returned HTTP 403 `Resource not accessible by integration`.

The runner currently consumes only gate-contract v1.0, an explicitly approved contract version. It rejects draft v1.1/v1.2 and does not migrate existing app locks. Filesystem locks coordinate cooperating writers only; direct writes and hook bypass remain outside their control. Review metadata does not authenticate reviewer identity or cognitive independence.

## Follow-up review — revision `591847987a15dff30c4b6501b4296648995252ae`

- **Reviewer:** `/root/fw021_review`, read-only follow-up against the exact revision above.
- **ADV-014-01 — CLOSED for runner-plumbing route coverage.** `tests/test_gate_runner.py::test_all_ten_gate_routes_accept_isolated_synthetic_not_applicable_records` builds and validates an accepted chain through all ten gates, pins exact upstream run IDs/versions/digests, and verifies that each downstream candidate is rejected while its immediate prerequisite is `in-progress`. Each fixture is explicitly synthetic `not-applicable` with a fixture-owner decision. This demonstrates positive/negative runner plumbing only; it does not establish application applicability, application evidence, or a PASS route.
- **ADV-014-02 — OPEN.** Hosted branch-protection/ruleset state and the invalid-transition merge-blocking rehearsal remain unverified. The connected GitHub integration previously returned HTTP 403 when reading branch protection. A passing pipeline does not establish merge enforcement.
- **Follow-up disposition:** The reviewer accepts this route-coverage evidence for the narrow original finding. FW-TASK-026 remains in progress until hosted policy rehearsal and other required acceptance evidence are complete.

## Required follow-up

1. Have a repository administrator/maintainer expose or configure the required hosted rules, then rehearse that an invalid transition check blocks merge and record the observed settings and exact run.
2. After the hosted-policy evidence is available, obtain a fresh independent review against the exact final revision and update this report and the FW-TASK-026 milestone. Until then, FW-TASK-026 remains in progress.
