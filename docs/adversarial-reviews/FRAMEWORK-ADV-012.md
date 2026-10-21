---
id: FRAMEWORK-ADV-012
type: adversarial-review
title: FW-TASK-019 CI, revision, and release evidence rehearsal
status: approved
version: 1.0
created: 2026-10-21
updated: 2026-10-21
reviewed-artifact: FW-TASK-019
reviewed-version: implementation at 8bb496736acdbf69b95310f4a23b411e30b45fde
related-artifacts: FRAMEWORK-ADV-011, FRAMEWORK-BACKLOG-001, FRAMEWORK-CI-RELEASE-POLICY-001, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-ADV-012 — FW-TASK-019 CI and release evidence review

## Frozen scope and method

- **Task/gates:** FW-TASK-019; G-IMPL CI and exact-source evidence, plus a bounded G-RELEASE control rehearsal. No application deployment, production release, or repository-setting mutation was authorized or performed.
- **Reviewed implementation revision:** `8bb496736acdbf69b95310f4a23b411e30b45fde` on `codex/v2-backlog-roadmap`.
- **Hosted positive run:** GitHub Actions push run [39533369435, attempt 1](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39533369435/attempts/1), against the exact revision above; completed successfully. `Initializer Regression Gate`, `TypeScript Static Code Analysis`, and `Metadata & Artifact Audit` all concluded `success`.
- **Hosted negative observation:** The preceding push run [39533199767, attempt 1](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39533199767/attempts/1), against `15e00f0eec064fabc73aacd1c82d2ee254c10582`, failed the metadata job because a local-runner unit test assumed `runner_os == local` while executing on hosted Linux. The test now removes inherited provider/runner metadata when simulating a local run; the follow-up exact-commit hosted run passed. This was a test isolation defect, not a product check failure.
- **Local evidence before the follow-up push:** `python3 -m unittest discover -s tests -q` — 59 passed; `python3 scripts/artifacts.py validate` — 45 artifacts validated; `git diff --check` — passed. The implementation checkpoint also recorded 30 TypeScript tests, configured 100% statement/branch/function/line coverage, typecheck, and production build passing. These local results are distinct from the hosted run.
- **Review method:** A bounded read-only review of implementation, policy, fixtures, tests, backlog, and CI results. Reviewer did not edit files or execute checks. Reviewer separation is procedural and does not prove identity or independent organizational control.
- **Independent final review:** `/root/review_fw019` accepted criterion 5 as a synthetic control rehearsal for this framework-only task. The reviewer confirmed that the case matrix and fixtures cover the required decision boundary and response semantics; no actual app release, deployment, or user-data restore is claimed or required for FW019.

## Rehearsal coverage and results

The retained unit/fixture suite exercises the decision boundary for successful and failing checks, stale source SHA, artifact digest mismatch, absent or mismatched owner authorization, unavailable remote publication, interrupted/cancelled workflow, missing rollback evidence, and an authorization reference mismatch. Runner tests cover command failure, stale provider SHA, invalid manifest rejection before execution, persistent workspace mutation stopping later commands, timeout cleanup of a background child, and successful provenance/output capture. These are deterministic local simulations of release-control decisions; they are not an actual application artifact release, deployment, or restore of user data.

| Scenario | Evidence and expected result |
|---|---|
| Exact-revision positive CI | `test_success_record_binds_runner_attempt_sha_event_and_output_digests`; hosted run `39533369435`, attempt 1, SHA `8bb496736acdbf69b95310f4a23b411e30b45fde`; all three required checks succeeded. |
| Required-check failure / cancelled run | `test_g_impl_rejects_required_ci_evidence_with_failed_conclusion` and release scenario in `test_release_pass_requires_actual_artifact_reference_owner_and_successful_current_ci`; expected/observed result: reject G-IMPL/G-RELEASE PASS. |
| Interrupted or pending run / partial evidence | Release test models an interrupted run as `pending` with cancelled conclusion; it must not satisfy successful CI evidence. Removing artifact-reference evidence models unavailable artifact upload and must reject release PASS. Neither fixture invokes an actual interrupted GitHub job. |
| Stale source or workflow attempt | `test_ci_evidence_is_checked_against_this_record_source_commit` and release test's wrong-SHA / missing-attempt-URL cases; expected/observed result: reject and rerun against exact candidate. |
| Changed artifact / missing authorization | Release test changes the artifact digest, removes owner authorization, mismatches `authorization_ref`, changes affected task, or violates the release window; expected/observed result: reject and require a rebuilt/re-authorized candidate. |
| Missing or unavailable remote | Release test sets `push_result=failed`, `remote=null`, and branch ref null; expected/observed result: reject publication. This models unavailable publication state without probing a real network remote. |
| Rollback and recovery response | Release test now includes an explicit synthetic local-first recovery procedure naming the operator, stop/retain-current behavior, restore target, digest check, tenant-scoped read check, and recorded outcome. An empty plan is rejected. This is a validator-level text fixture; no filesystem restore drill or machine parsing of plan steps occurred. |
| Runner integrity / execution | `tests/test_ci_checks.py`: invalid manifest is rejected before execution, persistent source mutation stops remaining checks, and timeout terminates a background process group. |
| Repository merge protection | **Unverified.** The connected GitHub integration received HTTP 403 for branch-protection settings; workflow success is not merge protection. |

## Adversarial findings and limits

1. **Environment-sensitive tests can falsify the pipeline signal.** The first hosted run caught a test that only passed in a local environment. The test now sanitizes inherited provider metadata for its local simulation, and hosted rerun passed; future runner metadata changes still need tests that distinguish simulated from real provider execution explicitly.
2. **Provenance is not proof of test honesty.** The runner captures source/run metadata and output digests, validates before execution, detects persistent workspace changes, and kills timed-out POSIX child processes. Repository-controlled checks can still lie, exfiltrate data where runner networking permits, or mutate and restore files; the recorded digest is not cryptographic attestation that checks evaluated immutable source bytes.
3. **The release-control rehearsal is synthetic.** It verifies validator behavior with deterministic fixtures and modeled responses; it does not build and retain a real app artifact, obtain a real owner authorization, deploy to a non-production target, or exercise restoration of user data. The local-first recovery-plan fixture is text-only: the validator checks presence, not that each plan step is complete or executable. It cannot justify application release readiness.
4. **Hosted workflow success is narrower than repository governance.** Branch-protection settings could not be read, so direct-push restrictions, required-check enforcement, review requirements, and bypass restrictions remain unverified and must not be claimed active.
5. **The first failed run is retained as failure evidence.** The passing rerun does not erase it; the resolution is the test isolation change and successful exact-revision rerun.

## Review disposition

**Independent review disposition: PASS for the bounded FW-TASK-019 framework implementation and synthetic control rehearsal.** The local rehearsal demonstrates validator decisions and modeled responses; the rollback plan is textually present but not machine-parsed or actually executed. The hosted positive run cited above is for the earlier implementation commit; this final review-record/test delta still requires its own exact-commit hosted run before FW-TASK-019 can be closed. This record establishes neither production-release authorization nor production readiness. Branch protection remains explicitly unverified.
