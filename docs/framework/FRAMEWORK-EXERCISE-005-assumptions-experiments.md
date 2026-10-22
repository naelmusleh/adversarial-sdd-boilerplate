---
id: FRAMEWORK-EXERCISE-005
type: framework-exercise
title: Assumption expiry and experiment evidence lifecycle
status: draft
version: 0.1
created: 2026-10-22
updated: 2026-10-22
related-artifacts: FRAMEWORK-BACKLOG-001, WORKFLOW-DISCOVERY-001, DECISION-LOG-001, ARTIFACT-CONTRACT-001
---

# FRAMEWORK-EXERCISE-005 — Assumption and experiment lifecycle

## Boundary

This synthetic exercise demonstrates record shape and routing only. It is not customer research, a provider test, an owner decision, a gate result, or evidence that a product outcome occurred. Synthetic examples MUST NOT be treated as real-world observations.

## Lifecycle example

`SAMPLE-ASM-001` records the synthetic claim “users will complete a five-step setup.” It is labeled an inference with low confidence, impact if wrong, an owner, due/review dates, links to `SAMPLE-FR-001` and `SAMPLE-TASK-001`, and separate confirmation/disproof methods. Its status history starts at `open`; each status event has a date and reason so reopening cannot masquerade as a new record. Its dependent setup task is conditional; the unrelated help-content task remains unblocked.

`SAMPLE-EXP-001` proposes a test of that assumption and records a prediction and an explicit falsifier (“fewer than four of five eligible participants complete without assistance”), method, sample/data limits, privacy handling, read date, and decision rule. Its attached synthetic evidence exercises only schema routing; it is not an outcome, does not complete the experiment, and cannot confirm real user demand. The validator rejects any attempt to use that synthetic evidence as a completed result.

In the expiry case, an open assumption whose due date is past produces an error. In the disproved case, the record must include a disposition, affected requirements/tasks are held for reevaluation, and only independent work stays unblocked. A decision record must identify the evidence and experiment it considered; that record still requires the authorized owner to choose and cannot itself grant a gate transition.

## Reproducibility

Run `python3 -m unittest tests.test_assumption_experiments -v` for the positive and negative matrix. Run `python3 scripts/artifacts.py assumptions validate PATH --today YYYY-MM-DD` to validate a project bundle deterministically. The validator checks structure, canonical trace links when invoked inside an app repository, expiry, lifecycle fields, and synthetic evidence boundaries; human reviewers still judge source truth, materiality, and decision authority.
