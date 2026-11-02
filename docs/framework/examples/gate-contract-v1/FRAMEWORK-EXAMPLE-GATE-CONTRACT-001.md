---
id: FRAMEWORK-EXAMPLE-GATE-CONTRACT-001
type: framework-contract-example-set
title: Synthetic gate-run contract fixtures
status: draft
version: 1.0
created: 2026-10-20
updated: 2026-10-20
related-artifacts: FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-GATE-TRACEABILITY-001
---

# Synthetic gate-run fixtures — contract v1.0

These files are structural fixtures only. They do not represent a real application, observed execution, reviewer, owner decision, or gate approval. The ten files in `valid/` are schema-shaped `in-progress` records with every criterion left `not-checked`; they intentionally do not assert a gate pass. The ten gate-specific files in `invalid/` omit the required `gate_result` property and must be rejected by a Draft 2020-12 validator.

Two additional `invalid/` fixtures exercise relational checks that JSON Schema shape alone cannot establish:

- `changed-file-hash.json` has a digest that does not match `inputs/FIXTURE-INPUT-001.md`; the FW-TASK-018 validator must reject the mismatch.
- `stale-source-revision.json` has evidence from a source revision different from the run snapshot; the FW-TASK-018 validator must reject stale evidence.

No fixture is an application artifact or product evidence. Contract v1.0 requires every gate criterion exactly once and performs semantic/result consistency checks beyond JSON Schema. Those relational checks are assigned to FW-TASK-018; the fixtures remain its positive and negative oracle set.
