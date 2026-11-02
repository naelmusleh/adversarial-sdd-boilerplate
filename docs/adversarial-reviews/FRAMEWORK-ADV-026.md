---
id: FRAMEWORK-ADV-026
type: adversarial-review
title: FW-TASK-029 hosted probe execution halt
status: blocked
version: 1.0
created: 2026-10-24
updated: 2026-10-24
related-artifacts: FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-010, FRAMEWORK-ADV-025, DECISION-027
---

# FRAMEWORK-ADV-026 — FW-TASK-029 hosted probe execution halt

## Observed execution evidence

- The corrected path/ref workflow at `7331e36aa9bcc99048b23a4d94c973e2802eace2` passed independent review and all three required Verify Pipeline checks. Hosted run `40097282253` failed closed because the source push contained the explicitly skipped reusable-workflow caller job in addition to the three configured required checks. No receipt or signature was created.
- The exact skipped-caller correction at `feb96b2b285b8693a2561cff03960694b7128893` passed independent review and all three required Verify Pipeline checks. Hosted run `40097474831` successfully prepared and signed the synthetic receipt. GitHub and Rekor record attestation `59408103` for the synthetic receipt. The signing job then failed while locating the downloaded bundle: the Linux GitHub CLI emits `sha256:<digest>.jsonl`, while the script searched only for `sha256-<digest>.jsonl`. The bounded receipt/bundle output artifact was not completed, and offline verification did not run.
- Local uncommitted correction in FEASIBILITY-010 v1.5 and `.github/workflows/fw029-evidence-probe.yml` accepts colon or dash digest separators, validates the exact digest filename shape, requires a single bounded regular file, and rejects symlinks. It has not received independent review or hosted CI.

## Adversarial disposition

This record reports observed execution facts and the process halt; it is not an independent security PASS. After the owner's resumption, two review/fix cycles have occurred. The repository `AGENTS.md` circuit breaker requires stopping before a third review/fix cycle, recording findings, and marking the backlog item BLOCKED for manual owner gating.

## Required owner gate

FW-TASK-029 G-FEAS is **BLOCKED**. Do not request another reviewer, push the v1.5 correction, or dispatch another hosted run until the owner explicitly directs resumption after this halt. If resumed, independently review the exact v1.5 diff, run exact-revision CI, then retry the bounded hosted workflow and complete offline bundle verification before claiming feasibility. No provider choice, product implementation, or app adoption is authorized by this record.

## Owner resumption and re-review checkpoint

The owner explicitly resumed FW-TASK-029 after this halt on 2026-10-24. The task is active at G-FEAS while its corrected workflow is reviewed. The independent reviewer blocked the first local filename correction because it did not require a regular, nonempty bundle and because the backlog still stated that owner resumption was pending. The workflow now requires exactly one digest-shaped regular file, rejects symlinks, and enforces a nonzero size no greater than 4 MiB. FEASIBILITY-010 v1.7 and FRAMEWORK-BACKLOG-001 v4.64 record the resumed state and reviewer findings. This is a new, narrower review checkpoint; the prior circuit-breaker history remains preserved. No hosted retry is permitted until this exact correction passes independent review and exact-revision CI.
