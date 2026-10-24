---
id: FRAMEWORK-ADV-032
type: adversarial-review
title: FW-TASK-029 G-ARCH review rounds 1 and 2
status: blocked
version: 1.0
created: 2026-10-24
updated: 2026-10-24
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-ARCHITECTURE-003, FRAMEWORK-FEASIBILITY-010, FRAMEWORK-COVERAGE-002, FRAMEWORK-CX-002, FRAMEWORK-ADV-027, FRAMEWORK-ADV-028, FRAMEWORK-ADV-031, DECISION-027, DECISION-028
---

# FRAMEWORK-ADV-032 — FW-TASK-029 G-ARCH review rounds 1 and 2

## Review scope and independence

Independent reviewer `/root/fw029_independent_review` performed two read-only full-scope G-ARCH reviews for FW-TASK-029 under DECISION-027/028, covering FR-FW-032–034 and GARCH-01–03. Reviewer identity and cognitive independence remain procedural assertions. No files were edited and no workflow was run by the reviewer. Exact-revision Verify Pipeline evidence is recorded separately.

## Round 1 — NEEDS-CHANGES

- **Source:** commit `805251ca5dfaea729997c7cdeb6f3c2533e991e5`; architecture blob `6f076fd05618f88c790aab86ae792916a6eace7c`.
- **GARCH-01:** Boundaries and operational limits mostly clear; findings below required correction.
- **GARCH-02:** ADRs and proposed units were coherent, but the replay acceptance condition needed explicit mapping.
- **GARCH-03:** Structural handoff was incomplete.

Findings:

- **ARCH029-01 (P2) — Replay semantics:** FR-FW-033 conditionally requires rejecting replay where prohibited, while v1 allowed repeatable read-only verification and deferred action authorization. The architecture did not explicitly map that conditional criterion.
- **ARCH029-02 (P2) — Requirement-to-case map:** Semantic cases omitted important source, repository, workflow, contract, run, manifest, check, signature and evidence mismatch negatives, and lacked criterion-to-test mapping.
- **ARCH029-03 (P2) — Input bounds:** Check/evidence arrays and total receipt/policy byte sizes were unbounded despite the bounded-payload claim.

## Round 2 — NEEDS-CHANGES

- **Source:** commit `a37ea6989d7090a4cf897ed82f87934cac8d2b4c`; architecture blob `cefd5b503d1d268f233696896d9d78edd142e895`.
- **Receipt schema:** `76951d262a32bd1b9b385be3ecb6575277420f0f`.
- **Policy schema:** `535c1b4b1c097b147eec20cae22e27d5c310c20d`.
- **Valid receipt:** `46eb29ec49913832e46dc16e13f9d45c72b68230`.
- **Invalid receipt:** `ef06b191477e8b45f5fda18ce32b45c0d014f7a3`.
- **Valid policy:** `a84808dbdf8a41604b06b9404ed308fdb2953167`.
- **Invalid policy:** `4c9bd276d69185f17d0be1d104a44f19706296cc`.
- **Semantic cases:** `2d50422eb2f0d80c37df433779cec6d3c1efd2fb`.

Criterion disposition:

- **GARCH-01 — PASS.** Trust boundaries, privacy minimization, least privilege, retention limits, recovery, freshness/revocation limits and claim boundaries are explicit.
- **GARCH-02 — PASS with decisions gated.** ADRs and implementation units identify options, evidence, authority, dependencies and unauthorized work. No additional replay-policy decision is required in the bounded scope. The owner must accept or revise the proposed size ceilings in ADR-05 before implementation.
- **GARCH-03 — NEEDS-CHANGES.** Two findings remain.

Findings:

- **ARCH029-04 (P2) — Invalid fixture does not isolate trust-root omission:** The policy invalid fixture omits `source` and `provider_run` in addition to `issuer.trust_root_sha256`, although the updated policy schema requires all three. Update it with valid source/run fields or add a dedicated isolated fixture.
- **ARCH029-05 (P2) — Acceptance-case gaps:** The requirement-to-case map lacks explicit semantic negatives for an unsigned receipt being promoted, an extra required-check result without a missing replacement, and top-level `receipt.source.ref` differing from the pinned policy.

The reviewer parsed all seven JSON documents and performed a limited structural/fixture check. Valid fixtures conformed to checked schema constraints; the invalid policy failed for three missing fields, so it did not isolate the intended error. This was not complete JSON Schema 2020-12 conformance or semantic verifier execution. Review evidence is limited to artifacts at the exact source commit above.

## Gate status and required checkpoint

**G-ARCH is BLOCKED at GARCH-03.** ARCH029-01–03 are addressed in round 2; ARCH029-04/05 remain unresolved. No owner choice is needed to correct these two findings. However, the repository's operating guard limits consecutive adversarial review/fix loops to two. The owner must explicitly authorize a third, final bounded correction and full-scope independent review before that work begins.

The proposed checkpoint scope is limited to correcting the isolated invalid policy fixture and adding explicit semantic cases/mappings for unsigned-receipt rejection, extra-check rejection, and source-ref mismatch. It excludes changing FR-FW-032–034, provider or key selection, production trust anchoring, replay/authorization design, trust freshness/revocation, retention guarantees, implementation, app adoption, and release. Exact-revision Verify Pipeline and full-scope GARCH-01–03 review would follow if authorized. Implementation remains unauthorized.
