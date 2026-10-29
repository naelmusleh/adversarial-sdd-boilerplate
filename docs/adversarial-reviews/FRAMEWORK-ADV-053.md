---
id: FRAMEWORK-ADV-053
type: adversarial-review
title: FW030-IMPL-02 initial independent code review
status: complete
version: 1.1
created: 2026-10-28
updated: 2026-10-28
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
