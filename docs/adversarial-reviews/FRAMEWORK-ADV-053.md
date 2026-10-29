---
id: FRAMEWORK-ADV-053
type: adversarial-review
title: FW030-IMPL-02 initial independent code review
status: in-review
version: 1.4
created: 2026-10-28
updated: 2026-10-29
related-artifacts: FRAMEWORK-ARCHITECTURE-004, FRAMEWORK-PROFILE-030-001, FRAMEWORK-CONTRACT-030, FRAMEWORK-BACKLOG-001, DECISION-043
---

# FRAMEWORK-ADV-053 — FW030-IMPL-02 initial review

## Review record

- **Gate/task:** G-IMPL; FW-TASK-030 / FW030-IMPL-02 only.
- **Evaluator:** independent read-only reviewer `/root/fw030_impl02_review`.
- **Review date:** 2026-10-28.
- **Reviewed candidate:** `e8527d898a18c6527efbf996fdef59bbdee19fc9`, branch `codex/fw030-impl02`.
- **Scope:** profile identity and refusal behavior; request/source/run and supplied authorization binding; no-secret/no-workload-network/mount/resource controls; bounded results; terminal-state and cleanup behavior; workflow permissions/triggers; alignment with FRAMEWORK-ARCHITECTURE-004 and DECISION-043.
- **Verdict:** NEEDS-CHANGES. This is the first review checkpoint, not a G-IMPL pass.

## Findings and disposition

| Finding | Severity | Reviewer finding | Correction and disposition |
| --- | --- | --- | --- |
| FW030-IMPL02-01 | P1 | The candidate checked that a bind ended in `:/input:ro` but did not require the exact request-declared source. The effective image, argv, and working directory were not all compared against the request. This could make runtime observations weaker than the contract claim. | Corrected in adapter commit `670357454a95ed847f3864e32f1656a189c756a9`: compare exact HostConfig and effective bind source/destination/mode, image, command, working directory, rootfs, network, identity, resources, and relevant privilege settings. Negative exact-source test is included in `03feeec3eb893d6d5427c4fb0a597f9fe8031465`. Pending independent re-review. |
| FW030-IMPL02-02 | P2 | Malformed case-result JSON or non-string case fields could raise an uncaught parsing/type error instead of producing a normalized failed result while preserving cleanup. | Corrected in adapter commit `670357454a95ed847f3864e32f1656a189c756a9`: strict duplicate-key parser, field type/outcome checks, bounded diagnostics, and failure normalization. The malformed-output-and-cleanup fixture is in `03feeec3eb893d6d5427c4fb0a597f9fe8031465`. Pending independent re-review. |
| FW030-IMPL02-03 | P1 | A second independent review at exact candidate `3d18aebede357426ca3338f67c71d499bbd5d5c1` found `_run` copied the complete Actions environment into host-side Podman processes, despite the adapter's no-secret boundary. | Corrected in adapter commit `f1892a9957e0711d8b05f951e0929e2c225bd629` by removing environment merging and retaining only explicit PATH, HOME, locale, XDG runtime, and TMPDIR variables. Tests now assert that synthetic secret and provider run identifiers are excluded in `70100425dc30b6d6fb1be83f73981ab5a6dca8db`. Pending independent re-review. |
| Context mismatch | Not a finding | The reviewer’s local snapshot did not contain DECISION-043 or the latest `verify-pipeline.yml` update and therefore could not verify owner scope or the new pilot call. The remote review branch contains DECISION-043 and gates the reusable pilot to manual dispatch on `codex/fw030-impl02`; its checkout permission is `contents: read` only and credentials are not persisted. | Reconciled against the remote `codex/fw030-impl02` branch. No implementation change is needed for this observation. |

## Review constraints and residual risks

The reviewer did not run tests. The profile remains bounded to one observed GitHub-hosted Ubuntu 24.04 / rootless Podman candidate and the fixed pinned synthetic image. The runner-image metadata mismatch and observed SIGTERM-to-SIGKILL escalation remain explicitly accepted residual risks under DECISION-043. The review establishes no profile support beyond this candidate, no complete host isolation, no graceful termination, no application integration, and no production readiness. A separate full review of the corrected exact candidate and exact-revision CI are still required before G-IMPL disposition.


A second independent review of the corrected environment boundary is required on the current exact PR head. The previous exact-review miss was fixed before any synthetic adapter pilot was dispatched; no runtime pilot has yet run against this adapter implementation.


## Superseded exact-revision CI

Verify Pipeline run [40797321974](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40797321974) failed the Python job on superseded source `3d18aebede357426ca3338f67c71d499bbd5d5c1`; it is not evidence for the corrected candidate. The failures were (a) review artifact status `complete`, which is not an allowed artifact status; (b) three adapter fixtures whose UID/GID did not match the request; and (c) the now-recorded full-environment leak. The review artifact is now `in-review`, the fixtures use the requested non-root identity, and the host subprocess environment is allowlisted. A fresh exact-head Verify Pipeline run is required.


## Fresh-cycle finding on exact candidate `3336a38b11cdce4b51f46156f9f1d1350d68e01a`

Independent reviewer `/root/fw030_option_fix_review` identified that `_verify_container` accepts extra options alongside the required tmpfs flags and filters effective mounts down to bind entries, so it neither rejects contradictory extras nor detects an unexpected `/output` user mount. Podman 4.9's inspect contract omits tmpfs entries from the user-mount list; a corrected candidate must report configured tmpfs strictly and observe the effective tmpfs from inside the synthetic workload's mount table. Verdict for this candidate: NEEDS-CHANGES; no retry is authorized on it. The owner has separately authorized one new correction/review/CI/retry cycle in DECISION-044.


## Cycle-3 retry disposition (2026-10-29)

After the cycle-3 corrected adapter review passed, a one-time trigger workflow was independently reviewed at `8701f2f256230add2fe9e75e1fbc8ab2c9163d02`; exact adapter and workflow Verify Pipeline runs `40874914344`, `40874924272`, `40875188008`, and `40875194970` passed their required jobs. The authorized synthetic retry [40875354469](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40875354469) ran on source `a1d7b4364ec7ea8a90577b28ac760c4c3d5901c9`, reached container inspection, then returned `fw030.adapter.mount_observation_mismatch` before case results. Cleanup was reported `complete`. The trigger workflow and marker were removed immediately after the run. The single retry under DECISION-044 is consumed; no FW030-IMPL-02 pass is claimed. DECISION-046 is a separate owner checkpoint for one bounded sanitized bind-observation correction/review/CI/retry cycle.



## Cycle-4 bind-observation disposition (2026-10-29)

Under DECISION-046, candidate `73154a4887907265ae53a927e79afb983b74e38b` received NEEDS-CHANGES: the code allowed `rprivate` before the diagnostic had observed it. The corrected diagnostic-only candidate `db1719555e3c356f1bfe23b415ae97ee31fa4048` passed independent read-only review; it kept the policy strict to `ro` while emitting bounded summaries without host paths. Its Verify Pipeline [40884972685](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40884972685) passed all three required jobs. Temporary diagnostic workflow commit `6b23427089f300243906d1c2aeb971672282e8b3` passed independent review and exact Verify Pipeline [40885371281](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40885371281); the one-marker workflow was removed after use.

Diagnostic run [40885552547](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40885552547) on source `cf17a9709a328d21996d7129a730e573714eba1c` produced no cases and cleanup complete. The sanitized report observed one HostConfig bind, source match true, destination `/input`, options `ro,rprivate`; one effective `bind`, source match true, destination `/input`, read-only true. Verify Pipeline [40885561837](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40885561837) passed all required checks. The report's allowlisted token summary did not explain why validation rejected the binding.

The evidence-bounded correction candidate `e50b262cc5a6f9197572b811bef74d0ed3fde451` was independently reviewed PASS and its focused adapter suite passed (19 tests); Verify Pipeline [40885994850](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40885994850) passed all three required jobs. It accepted only option sets `ro` or `ro,rprivate`, with exact effective source/destination/read-only checks and negative cases.

The single DECISION-046 retry [40886378843](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40886378843), on trigger source `27a2089488af90f04d69a41207208ea0e483672d`, again failed at `mount_observation_mismatch`, produced no cases, and reported cleanup complete. Its sanitized output repeated the expected source, `/input`, `ro,rprivate`, and effective read-only bind observations. Therefore FW030-IMPL-02 remains blocked. DECISION-046 is exhausted. DECISION-047 authorizes only a fresh bounded diagnostic cycle to identify the remaining rejection without exposing paths or raw arbitrary option values; no further policy changes or retry are permitted until that checkpoint's evidence, independent review, and exact CI requirements are met. No profile expansion, app data/secrets, production, merge, or deployment is claimed.


## Cycle-5 diagnostic and correction (2026-10-29)

The bounded diagnostic run [40887400236](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40887400236) on source `6abd542885371b9014f4f175adf6d1e9b2153870` failed before cases with cleanup complete. It observed exactly one HostConfig bind with the expected source and `/input`; bounded options were `ro`, `rprivate`, and `rbind`. The effective mount was one bind from the expected source to `/input`, with read-only true. This identifies `rbind` as the remaining rejected token. The official [Podman 4.9.3 manual](https://docs.podman.io/en/v4.9.3/markdown/podman-run.1.html) documents recursive bind behavior. The correction candidate allows only `ro,rprivate,rbind`, after a fail-closed host mountinfo preflight verifies there are no nested mounts beneath the generated synthetic input. It preserves exact declared source/destination checks and requires the effective mount to remain read-only. Independent review and exact-revision Verify Pipeline are pending; the one authorized synthetic retry has not run.


### Cycle-5 correction review finding

Independent read-only review of exact candidate `355a429d80861e19b9122e7c67a5a32fc3ad454b` returned NEEDS-CHANGES. Finding: `_has_nested_mounts` treated empty mountinfo as no nested mount and did not require the `-` separator after the mandatory mount fields. The correction rejects empty/blank records, requires the separator at or after field 7 with a complete filesystem tuple, and adds empty and misplaced-separator fixtures. The exact-candidate Verify Pipeline passed all required checks, but the candidate is not accepted; no retry was dispatched. A new exact review and Verify Pipeline are required.


A second independent review of `7c6fc50ea3dcb29cfa2c1d214f44f9ae2107b58b` returned NEEDS-CHANGES. It identified that mountinfo parsing accepted trailing fields beyond the defined filesystem tuple and that the blank-line fixture contained a literal `\\n`. The next correction requires exactly three fields after the separator and tests true blank input, extra trailing data, and a valid optional-field record. No retry was dispatched.


### Cycle-5 correction disposition

Corrected candidate `bd85f9d6220e834b99171375837c372f759cbf79` passed independent read-only review. The reviewer confirmed that preflight rejects empty and blank mountinfo, locates the separator after the six mandatory fields, requires exactly three post-separator filesystem fields, and covers valid optional fields, nested mounts, malformed records, and trailing data. Exact Verify Pipeline run [40888950113](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40888950113) passed Metadata & Artifact Audit, Initializer Regression Gate, and TypeScript Static Code Analysis; optional pilot jobs were skipped on push. The focused mountinfo fixture passed locally. The single authorized synthetic retry remains pending a separately reviewed temporary trigger workflow and its exact-revision CI. No workload result or FW030-IMPL-02 pass is claimed.


### Cycle-5 retry workflow checkpoint

Temporary trigger workflow commit `80d54c11fdbad6f52fe7e9b6e809578406726087` passed independent read-only review. The reviewer confirmed the workflow triggers only on the dedicated marker path on `codex/fw030-impl02`, has no top-level permissions or secrets, gives its sole reusable-pilot job `contents: read`, and has no marker present in that commit. Exact Verify Pipeline [40889191310](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40889191310) passed all three required jobs; optional synthetic jobs were skipped. DECISION-047’s one retry is now authorized for dispatch by adding the dedicated marker. The workflow and marker must be removed after the run; no merge/deploy is in scope.
