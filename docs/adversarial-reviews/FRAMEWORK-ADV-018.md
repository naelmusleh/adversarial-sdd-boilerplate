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

The next review round will assess a single-keyed check declaration map, separate profile-selection and check-result schemas, an explicit readiness aggregation rule, strict duplicate-key parsing, and a pinned Draft 2020-12 semantic validator exercised against named positive/negative instances. This section is not evidence that those checks have run or passed.
