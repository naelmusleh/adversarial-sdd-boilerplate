---
id: FRAMEWORK-ADV-018
type: adversarial-review
title: FW-TASK-013 G-ARCH review
status: draft
version: 0.1
created: 2026-10-23
updated: 2026-10-23
related-artifacts: FRAMEWORK-ARCHITECTURE-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-SPEC-001, FRAMEWORK-FEASIBILITY-008, FRAMEWORK-EXERCISE-007, FRAMEWORK-ADV-017, FRAMEWORK-GATE-CONTRACT-001, DECISION-LOG-001
---

# FRAMEWORK-ADV-018 — FW-TASK-013 G-ARCH review

## Review round 1 — blocked on GARCH-03

Reviewer: `/root/infinite_gallery_reviewer`, acting as the separately assigned read-only reviewer. The reviewer made no edits and ran no tests. Nine supplied hashes were checked and matched:

| Frozen input | SHA-256 |
|---|---|
| `docs/framework/FRAMEWORK-ARCHITECTURE-001-fw013.md` | `1aa3a7b2a9341ee09874f6e03e37820f20ca4a7a62db0623e253af153cab644b` |
| `docs/framework/schemas/profile-manifest-v1.schema.json` | `5733c26a68f29fd944647e078e01f62730d57b4fa7e148ee83b7f478c8beb131` |
| `docs/framework/FRAMEWORK-BACKLOG-001.md` | `86da79c6d6c4c6e6cda293f2a4b907722177cebbfe38062a5e74f3bdcd8cbfcd` |
| `docs/framework/FRAMEWORK-SPEC-001.md` | `e85d4b676bc90a530de91b454f1394d4d76484f29fbbd736eef564c68ec1a07a` |
| `docs/framework/FRAMEWORK-GATE-CONTRACT-001.md` | `46fd2116c87adaa395df79e62ce76a7d5994d2d03e9631a1b3af73a6fdf07b5a` |
| `docs/decisions/DECISION-LOG-001.md` | `dab97947121b2fe62134890ac8e4c388078531c5a88c2887519fbe2b052af59a` |
| `docs/framework/FRAMEWORK-EXERCISE-007-multiplatform-sample-contract.md` | `2bb91ef415110b336eb653c9ffaf9b1c1822d65ccad94b7710407ecd5357c17b` |
| `docs/framework/FRAMEWORK-FEASIBILITY-008-fw013.md` | `389c0682418847889ca936d2b08359db7aa1f5c44569af1637b241766965a0af` |
| `docs/adversarial-reviews/FRAMEWORK-ADV-017.md` | `d729ccbf8a699d3334e325f4ca6db2fa3373b42c18a56c9ab46e56d793edd1f9` |

### Criterion results

| Criterion | Result | Finding |
|---|---|---|
| GARCH-01 — boundaries, ownership, data flows, trust, security/privacy, failure/recovery, operations | PASS | The framework-only boundary and controls are explicit. No Infinite Gallery stack, provider, storage, native, or implementation choice leaked into the design. |
| GARCH-02 — ADRs and task-ready work | PASS | ADR-01–03 identify alternatives, evidence, authority/constraints, and trade-offs; six work packages state scope, acceptance, dependencies, and verification while remaining inside FW-TASK-013. |
| GARCH-03 — critical contracts, structural checks, frozen inputs | BLOCK | Two major contract gaps remain. |

### Findings

1. **Major — check IDs can be ambiguous.** The profile schema used arrays with `uniqueItems`, which rejects only identical objects. It permitted duplicate `check_id` values with different commands and the same ID in both applicable and unsupported lists. Use a unique-keyed object or an executable invariant; provide positive/negative cases. The exact prior schema sections were `checks` at lines 60–69 and 87–105.
2. **Major — output-manifest and semantic verification gap.** The architecture described an emitted provenance/check manifest but supplied only the profile declaration schema. It also deferred semantic Draft 2020-12 checks until G-IMPL; JSON parsing and required-field assertions did not execute keywords, references, or rejection behavior. Define a separate output contract, distinct check states/aggregation, and semantic validation against positive/negative fixtures, including duplicate-key rejection.

The reviewer concluded that no additional owner scope or product decision is needed for these bounded corrections. G-ARCH remains blocked on GARCH-03; implementation remains blocked.

## Corrective work in progress

## Review round 2 — blocked on GARCH-03

Reviewer: `/root/infinite_gallery_reviewer`, acting as the separately assigned read-only reviewer. The reviewer confirmed all nine supplied frozen input hashes matched and did not run the checker. Criterion result: GARCH-01 PASS, GARCH-02 PASS, GARCH-03 BLOCK.

| Frozen input | SHA-256 |
|---|---|
| `docs/framework/FRAMEWORK-SPEC-001.md` | `e85d4b676bc90a530de91b454f1394d4d76484f29fbbd736eef564c68ec1a07a` |
| `docs/framework/FRAMEWORK-BACKLOG-001.md` | `e193888b54c2506da8ea8da57a0e414b5077fe663c1f175326d7efeafa16ae0f` |
| `docs/framework/FRAMEWORK-FEASIBILITY-008-fw013.md` | `cc4fe2631f4ffe5cd225741ce657499db63356d5ad0829cedce89551ad068be0` |
| `docs/framework/FRAMEWORK-ARCHITECTURE-001-fw013.md` | `081ef1997b76cccfc83486d83186d8dcbb236c11d12323dbdd5eca865d990b79` |
| `docs/framework/schemas/profile-manifest-v1.schema.json` | `9857f98234bcbc0fe996775635b3b71336a2e754df4ffefd09807154903868a3` |
| `docs/framework/schemas/profile-selection-manifest-v1.schema.json` | `01735a71fbbf45d03d3e826b32acd027425b29bbcce6376efb8359552bb6afc4` |
| `docs/framework/schemas/profile-check-result-v1.schema.json` | `6af5f1e55f3310a16a54dd0e2e119c40493fdaee7ee620fca79001e79aef8f86` |
| `experiments/fw013/validate_architecture_contracts.py` | `6a828e7b5bb7d2e208f95a58fefc79bb6550342a8f892309d7740f9f7fc21414` |
| `docs/adversarial-reviews/FRAMEWORK-ADV-018.md` | `4ff9dc58b0204f1dd24ccfe8b542eb8938d87470ada247ac4c71e10a53b6a397` |

The original duplicate check-ID and missing output-schema findings are resolved. Three new major cross-record gaps remain:

1. **Selected profile version was not compared to the digested profile declaration.** The checker must compare both the selected version and manifest digest and reject a mismatched version fixture.
2. **Generated-file ownership reconciliation was incomplete.** The checker must validate the exact selected-profile path inventory against each profile declaration and core-owned paths against a separately versioned authoritative core-file inventory, including mismatch fixtures.
3. **Core-only readiness bypassed consistency checks.** The checker must validate result/profile bindings and exact core inventory before returning core-only; negative fixtures must reject residual profile-owned outputs and mismatched result selections.

No owner decision is needed for these bounded contract corrections. G-ARCH-03 remains blocked and implementation is not authorized by this review. The next frozen review will assess a versioned core-file inventory schema, the selection-to-core digest, selected profile version equality, exact generated path ownership sets, and core-only consistency fixtures under Draft 2020-12 validation. The prior hosted checker and Verify Pipeline results do not cover these new corrections.

The first hosted rerun of the corrective verifier, run [39892246981](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39892246981) on commit `7e99c037633ab69a5d312f65911b785363c770d1`, validated all four Draft 2020-12 schemas and reached the cross-record fixtures, then failed because the synthetic profile fixture declared `tsconfig.json` without including it in the selection inventory. This is a fixture inconsistency, not a product or profile execution result. The fixture is being corrected and the hosted verifier must pass before another independent review request.

## Review round 3 — blocked on GARCH-03

Reviewer: `/root/infinite_gallery_reviewer`, read-only. All ten supplied frozen hashes matched. The reviewer passed GARCH-01/02 and blocked GARCH-03 on the need to demonstrate correct multi-profile check-declaration validation with positive and negative fixtures. The reviewer reported that the cross-record validator compared a profile-check map at an overly broad level; the correction must prove that a valid selection containing two independently declared profiles is accepted and that a mismatch in one profile is rejected without conflating profile declarations.

| Frozen input | SHA-256 |
|---|---|
| `docs/framework/FRAMEWORK-SPEC-001.md` | `e85d4b676bc90a530de91b454f1394d4d76484f29fbbd736eef564c68ec1a07a` |
| `docs/framework/FRAMEWORK-BACKLOG-001.md` | `60ec254a5013db4bd51f363515fcca4566a6618e0ce292bcb76b023ce053196a` |
| `docs/framework/FRAMEWORK-FEASIBILITY-008-fw013.md` | `c8ef168b765f1055286e99fae8a0f9117f2a0402348403067676c799711bc5f9` |
| `docs/framework/FRAMEWORK-ARCHITECTURE-001-fw013.md` | `081707d74c8601fb9aa3120da05a01a0d9adbe9810d4d54ccb4ce75f5feeb965` |
| `docs/framework/schemas/core-file-manifest-v1.schema.json` | `bd6112370043048c71b53df9fb1da457df4facca4618b3ece4df35efa2cdb9ef` |
| `docs/framework/schemas/profile-manifest-v1.schema.json` | `9857f98234bcbc0fe996775635b3b71336a2e754df4ffefd09807154903868a3` |
| `docs/framework/schemas/profile-selection-manifest-v1.schema.json` | `b13713cfc667ee64f4f467c46f2298f63decab2eb0e416e04cdbfdec9155e5ae` |
| `docs/framework/schemas/profile-check-result-v1.schema.json` | `6af5f1e55f3310a16a54dd0e2e119c40493fdaee7ee620fca79001e79aef8f86` |
| `experiments/fw013/validate_architecture_contracts.py` | `9c497cbec125718836fb27869604c221565ef19d0e0c4f7e47ac22d0b65e2118` |
| `docs/adversarial-reviews/FRAMEWORK-ADV-018.md` | `0f637c6728f72bd4064d2d37c81dba8ed2fe02032b950f5cca0a079ba3bba70f` |

The hosted contract job [39892392326](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39892392326) and Verify Pipeline [39892392312](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39892392312) both passed on the exact reviewed commit `a20d1021b8c8ca67d0acfbdd0ae6ef57f8d8f67b`. The round-3 finding remains open until the multi-profile fixtures are run successfully and a fresh independent review accepts them.

On inspection of the frozen checker source, the comparison at the cited lines already used a profile-keyed lookup (`selection["profile_checks"].get(profile_id)`); however, no multi-profile fixture exercised that path. The finding is therefore treated as an unproven behavior/evidence gap, not silently dismissed. The correction checkpoint makes the per-profile lookup explicit and adds a valid two-profile aggregation fixture plus a negative mismatch fixture for the second profile. Hosted execution and fresh independent review remain required.
