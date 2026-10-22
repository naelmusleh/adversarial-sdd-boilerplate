---
id: FRAMEWORK-ADV-014
type: adversarial-review
title: FW-TASK-026 transactional gate runner review
status: approved
version: 0.2
created: 2026-10-22
updated: 2026-10-22
reviewed-artifact: FW-TASK-026
reviewed-version: f2ca403e4b0af68d439b58857c359615f69e810c
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
- **ADV-014-02 — CLOSED.** The paired hosted rehearsal evidence below demonstrates that the actual prerequisite-guard regression fails the required check and that failure of that same check blocks a ready, otherwise-mergeable PR under the observed active ruleset.
- **Follow-up disposition:** The reviewer accepts this route-coverage evidence for the narrow original finding. FW-TASK-026 remains in progress until hosted policy rehearsal and other required acceptance evidence are complete.

## Hosted policy observation and rehearsal — 2026-10-21

- **Policy observation:** The owner supplied GitHub Settings screenshots for the `main` branch rule. A read-only GitHub rulesets API lookup then independently returned active repository ruleset `main` (ID `25609658`) targeting `refs/heads/main`. It requires pull requests, strict/up-to-date status checks named `Metadata & Artifact Audit`, `Initializer Regression Gate`, and `TypeScript Static Code Analysis`; prohibits deletion and non-fast-forward updates; has no bypass actors; and reports `current_user_can_bypass: never`. The ruleset sets required approving reviews to `0`. The legacy branch-protection endpoint still returns HTTP 403, but the rulesets endpoint exposed the active policy directly.
- **Regression check:** Disposable rehearsal PR [#13](https://github.com/naelmusleh/adversarial-sdd-boilerplate/pull/13), head `9363c3416195bd40bdfa119f3a66a8a8d6294f67`, deliberately disabled the gate runner's prerequisite-completion guard. Local execution of the ten-gate route regression failed as intended. Hosted Verify Pipeline run [39712514713](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39712514713) completed with `Metadata & Artifact Audit` **failure** and the other two required checks **success**.
- **Required-check enforcement rehearsal:** Clean-based PR [#14](https://github.com/naelmusleh/adversarial-sdd-boilerplate/pull/14), head `a6b127810e9aec9d176c832758469b883193546b`, changed only one test to create an explicit, test-only failure sentinel. It was ready for review, based on `main` at `582f01a0f4fd3c126475a5e17c555f05fb718372`, and GitHub reported `mergeable: true` with no conflicts. Verify Pipeline run [39715440984](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39715440984) failed only the required `Metadata & Artifact Audit` context; `Initializer Regression Gate` and `TypeScript Static Code Analysis` passed. After the check completed, GitHub reported `mergeable_state: blocked` while the PR remained ready and mergeable. This isolates the active required-check rule as the merge blocker.
- **Rehearsal conclusion:** The actual prerequisite-guard regression on PR #13 caused the same required `Metadata & Artifact Audit` context to fail. PR #14 then demonstrated that failure of that exact required context blocks an otherwise mergeable, ready PR under the observed active ruleset. Together these runs satisfy the hosted invalid-transition merge-block rehearsal. Neither PR was merged; both were closed unmerged and both temporary remote/local branches were removed. The PR #14 sentinel was test-only and is not part of the implementation branch.
- **Final independent disposition (2026-10-22): APPROVED — no remaining technical blockers.** Reviewer `/root/fw021_review` reviewed exact implementation/evidence revision `f2ca403e4b0af68d439b58857c359615f69e810c` and accepted criterion 5: PR #13 tied the actual prerequisite-guard regression to the failing required `Metadata & Artifact Audit` check; clean, ready, otherwise mergeable PR #14 showed failure of that same required context produced `mergeable_state: blocked`. Both temporary PRs were closed unmerged. The reviewer also confirmed the exact-SHA run `39710983844` subsequently completed with all three jobs successful. The paired rehearsal and active ruleset satisfy the hosted policy acceptance criterion. Synthetic all-gates `not-applicable` records remain runner-plumbing evidence only and do not establish application PASS.

- **Closure:** ADV-014 is approved and closed for FW-TASK-026. The implementation and hosted enforcement evidence are limited to the stated contract version and observed `main` ruleset; no merge or deployment is claimed.
