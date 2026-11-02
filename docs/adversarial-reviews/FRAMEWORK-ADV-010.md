---
id: FRAMEWORK-ADV-010
type: adversarial-review
title: Independent blocking review of FW-TASK-018 first implementation
status: blocked
version: 1.0
created: 2026-10-20
updated: 2026-10-20
reviewed-artifact: FW-TASK-018
reviewed-version: initial implementation draft
related-artifacts: FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-GATE-TRACEABILITY-001, FRAMEWORK-BACKLOG-001
---

# FRAMEWORK-ADV-010 — FW-TASK-018 first implementation review

## Frozen scope and method

- **Gate/task:** G-IMPL / FW-TASK-018, fail-closed ten-gate validator and app initializer integration.
- **Frozen framework revision:** `d9e25383d55ed7d9c7e4d771fe5d3184c018f0fe` plus the then-current uncommitted FW-TASK-018 diff. The review was of that dirty tree, not a commit.
- **Method:** Read-only source review by `/root/sdd_governance`, assigned independently from implementation. The reviewer did not run tests or mutate files; identity separation remains a procedural claim.
- **Review result:** **BLOCK.** Do not accept the G-IMPL task or distribute v1.1 until blocking findings are fixed, affected checks rerun, and a new frozen review passes.

## Findings

| ID | Severity | Finding | Required disposition |
|---|---|---|---|
| ADV-018-01 | P1 | `ci-run` evidence read `source_commit` before assignment, permitting `UnboundLocalError` or reuse of a preceding record's commit. | Move source snapshot resolution before evidence processing; add a valid and mismatched CI evidence regression fixture. |
| ADV-018-02 | P1 | G-RELEASE compared user-supplied digest strings and merely resolved an owner decision ID; it did not bind the decision to the accountable owner, actual artifact bytes, environment, or release window. Release check evidence did not require successful conclusion/exact commit. | Resolve artifact digest to verified artifact-reference evidence, enforce accountable owner and exact authorization fields, and reject failed/mismatched CI evidence. Keep any provider/cryptographic limits explicit. |
| ADV-018-03 | P1 | App initializer pinned and distributed draft contract v1.1 before its amendment review passed. | Keep new app initialization on approved v1.0 until v1.1 is reviewed/approved; pin only the corresponding schema/template. |
| ADV-018-04 | P1 | G-IMPL check evidence could be unrelated to the declared check's scope, command/procedure, runtime, or pass condition. | Compare declared check metadata against linked execution/CI evidence and add mismatch fixtures. |
| ADV-018-05 | P1 | G-FEAS allowed constrained probe dependencies to be unblocked and did not reconcile probe task dependencies with the top-level `dependency_effects`. | Constrain unblocked state to supported feasibility; require exact task/state/effect correspondence and fixtures for mismatch and constrained bypass. |
| ADV-018-06 | P2 | Schema preflight checked unsupported keyword names but not malformed shapes of supported keywords, allowing runtime type errors for malformed schemas. | Validate supported keyword value types before evaluation; reject malformed schema definitions with deterministic diagnostics and fixtures. |

## Evidence boundary

The reviewer did not independently execute the local suite, artifact validator, initializer, hosted CI, or repository settings. The review does not assert the current state after this frozen revision. A new review must assess the repaired diff and its actual test outputs; this blocking report remains immutable history.
