---
id: FRAMEWORK-ADV-032
type: adversarial-review
title: FW-TASK-029 G-ARCH review rounds 1 through 4
status: approved
version: 1.3
created: 2026-10-24
updated: 2026-10-24
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-ARCHITECTURE-003, FRAMEWORK-FEASIBILITY-010, FRAMEWORK-COVERAGE-002, FRAMEWORK-CX-002, FRAMEWORK-ADV-027, FRAMEWORK-ADV-028, FRAMEWORK-ADV-031, DECISION-027, DECISION-028
---

# FRAMEWORK-ADV-032 — FW-TASK-029 G-ARCH review rounds 1 through 4

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

## Round 3 — NEEDS-CHANGES (final owner-authorized cycle)

- **Source:** commit `8402aae63965ccab19e5ef8ed070a2af140e49a9`; architecture blob `d527290cf7e374eaaa01c1f47c5203a414507999`; semantic-case blob `62d47e34a12e8a794136501bede26431abcb445b`; isolated missing-trust-root fixture blob `f1f0906287cacd256ad2028069480c53de72547b`.
- **GARCH-01 — PASS.** Trust/data boundaries, failure and recovery behavior, privacy limits, retention uncertainty, and snapshot verification limits are explicit.
- **GARCH-02 — PASS with a downstream owner condition.** ADRs state alternatives, evidence, authority and blockers. ADR-05's proposed size ceilings require owner acceptance or revision before G-IMPL.
- **GARCH-03 — NEEDS-CHANGES.** ARCH029-04 is resolved: the negative policy fixture includes valid `source` and `provider_run` and omits only `issuer.trust_root_sha256`. ARCH029-05 is resolved: SEM-27 covers unsigned-receipt promotion, SEM-28 covers an extra required-check result, and SEM-29 covers top-level source-ref mismatch, all mapped to requirements.
- **ARCH029-06 (Major) — Provider/run identity case incomplete:** SEM-16 covers attempt/event/ref/URL mismatch but omits provider and run ID, although FR-FW-032 requires provider run identity binding. Add explicit provider/run-ID mismatch semantic coverage with expected diagnostic `receipt.run_mismatch`.
- The reviewer stated the correction itself requires no owner decision. The owner-authorized final review cycle is consumed, so a further correction and independent rerun requires a new owner checkpoint.
- **Exact-revision CI:** Verify Pipeline [40135758687](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40135758687) passed Metadata & Artifact Audit, TypeScript Static Code Analysis, and Initializer Regression Gate on the exact reviewed source commit. The optional FW-029 Synthetic Evidence Probe job was skipped.

## Round 4 — PASS (new owner-authorized bounded cycle)

The owner authorized correction and full-scope independent re-review limited to ARCH029-06. Reviewer `/root/fw029_independent_review` passed GARCH-01–03 at exact source commit `8326b77b10486e4140e9785cd44fcf31b78829e9`. FW029-SEM-30 tests receipt provider identity mismatch and FW029-SEM-31 tests receipt run-ID mismatch against the policy-pinned values; both expect `failed` with `receipt.run_mismatch` and map to FR-FW-032. ARCH029-06 is resolved; no new material findings or owner decision are needed for G-ARCH.

- **Reviewed blobs:** architecture `c62d3a35fbf1931131afba9ab57e00d9921e0a10`; semantic cases `9aa3eb42471e597f3539cc35dbbb6c8ae277ed7b`; receipt schema `76951d262a32bd1b9b385be3ecb6575277420f0f`; policy schema `535c1b4b1c097b147eec20cae22e27d5c310c20d`.
- **Exact-revision CI:** Verify Pipeline [40137156642](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40137156642) completed successfully on the exact reviewed source. Metadata & Artifact Audit, Initializer Regression Gate, and TypeScript Static Code Analysis all passed. The optional FW-029 Synthetic Evidence Probe was skipped.

## Gate status

**G-ARCH PASS** within the approved FW-TASK-029 / FR-FW-032–034 scope. ADR-05's proposed size ceilings still require owner acceptance or revision before G-IMPL. This review does not authorize implementation, provider adoption, production trust decisions, app adoption, or release.
