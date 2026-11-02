---
id: FRAMEWORK-ADV-036
type: adversarial-review
title: FW-TASK-029 FW029-IMPL-04 operator guide review
status: approved
version: 0.5
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

## Owner-authorized review round 3 — NEEDS-CHANGES

**Exact revision:** `44331824784ee1ec7023a02fa2d311d346bc2248`.

- **FW029-IMPL04-04 — CLI usage error conflated with verifier state.** Omitting required `--policy-sha256` exits through argument parsing before JSON is emitted; a malformed supplied digest returns the verifier's `blocked` state. **Resolution:** candidate `6d29dc4f06722e8de822cf24791f0a7f46e5d85a` distinguishes omitted-argument usage errors from malformed supplied digests and the verifier's `blocked`, `unavailable`, and `failed` states.

## Owner-authorized review round 4 — NEEDS-CHANGES

**Exact revision:** `9af459f582f5d23d1411d63570cf8b96c7aa797f`.

- **FW029-IMPL04-05 — Failure-output fields overstated.** Failure JSON omits `revocation_status`, although successful JSON includes `not-established`; the guide incorrectly said every result contains that field. **Resolution:** candidate `50ff55cc52c26e21ced7fa03603f737a25c5c10f` states which fields occur in each output and that a failed attempt has not established revocation status.

The reviewer otherwise confirmed the prior corrections and found the remaining guide and checkpoint claims aligned with the architecture, verifier, and pilot workflow.

## Owner-authorized review round 5 — PASS

**Exact revision:** `e13cfd4869dc52efd967506a56b90e3a37bddc72`.

The reviewer confirmed the omitted-argument CLI error is distinguished from a malformed supplied digest, bundle SHA-256 capture is explicit, and success/failure JSON claims match the verifier implementation. The artifact name, configured one-day artifact retention, and unknown hosted-attestation lifecycle remain accurately bounded. No material mismatch or new finding remains.

Verify Pipeline [40212807109](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40212807109) passed the exact candidate: Metadata & Artifact Audit, TypeScript Static Code Analysis, and Initializer Regression Gate succeeded. The optional FW-029 Synthetic Evidence Probe was skipped on the push event as configured.

**Independent verdict: PASS for FW029-IMPL-04 within the bounded documentation scope.** This does not select a durable-retention policy or storage owner, establish deletion guarantees or current trust, authorize a gate/release, or complete FW-TASK-029 as a whole.
