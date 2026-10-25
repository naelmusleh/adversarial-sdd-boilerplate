---
id: FRAMEWORK-ADV-036
type: adversarial-review
title: FW-TASK-029 FW029-IMPL-04 operator guide review
status: in-review
version: 0.2
created: 2026-10-25
updated: 2026-10-25
reviewed-artifact: FW-TASK-029 / FW029-IMPL-04 operator handling and evidence claims
reviewed-version: FRAMEWORK-ARCHITECTURE-003 v0.8
related-artifacts: FRAMEWORK-ARCHITECTURE-003, FRAMEWORK-IMPL-003, FRAMEWORK-OPERATIONS-001, FRAMEWORK-BACKLOG-001, DECISION-032
---

# FRAMEWORK-ADV-036 — FW029-IMPL-04 operator guide review

## Scope and method

Independent reviewer `/root/fw029_independent_review` reviewed the operator guide and linked decision/backlog/verifier-guide changes read-only at exact commit `bdb84750c462090d0e99910a6b7c75dc1888d72c`. Scope: FW029-IMPL-04 operator retrieval, offline verification, expiry/unavailability handling, local privacy and retention claims, recovery, and separation of provenance verification from gate/release decisions. The reviewer did not edit files or run tests.

## Review round 1 — NEEDS-CHANGES

The reviewer found two P2 documentation issues:

- **FW029-IMPL04-01 — Bundle digest omitted from reproducibility record.** The guide asked operators to record four input digests, but the verifier JSON reports only the receipt, policy and trusted-root digests. The per-use record also omitted the detached bundle digest. **Resolution:** the guide now directs operators to compute and record the bundle SHA-256 separately and lists all four input digests.
- **FW029-IMPL04-02 — Outcome states collapsed.** The guide described every non-passing result as failed, obscuring distinct `blocked`, `unavailable`, and `failed` states. **Resolution:** the guide now preserves exact state and diagnostic, defines those three outcomes, and describes other outcomes as “did not pass.”

The reviewer otherwise confirmed the artifact name and retention configuration against the pilot workflow and found the trust, privacy, recovery, and gate/release limits accurately stated. The first corrected candidate was `ced85ad06ed1db29b34cb15a083112f36a78e2ad`.

## Review round 2 — NEEDS-CHANGES

**Exact revision:** `ced85ad06ed1db29b34cb15a083112f36a78e2ad`.

- **FW029-IMPL04-03 — State descriptions incomplete.** `blocked` also covers an invalid separately supplied policy digest; `unavailable` also covers a verifier timeout after the CLI starts. **Resolution:** candidate `e2faea49850e3999fa4f869c7ed3388d15baaf2b` describes both cases and preserves the exact attempt state and diagnostic.

The candidate awaits an owner checkpoint before a third review, under the repository's adversarial-loop guard. No hosted checks have been verified for the corrected candidate.
