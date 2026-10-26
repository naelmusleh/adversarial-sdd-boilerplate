---
id: FRAMEWORK-CONTRACT-030
type: framework-contract
title: FW-030 host-neutral request/result contract
status: draft
version: 1.0
created: 2026-10-25
updated: 2026-10-25
related-artifacts: FRAMEWORK-ARCHITECTURE-004, FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, DECISION-035
---

# FRAMEWORK-CONTRACT-030 — FW-030 contract v1

`request-v1.schema.json` and `result-v1.schema.json` define the versioned, host-neutral request/result wire shapes for FW030-IMPL-01. `scripts/fw030_contract.py` checks those schemas and cross-field invariants. The policy digest is SHA-256 over the policy object with its `sha256` member removed, encoded as UTF-8 canonical JSON with sorted keys and compact separators.

The preflight helper accepts only profile observations marked `synthetic_test_only: true`. Its `prerequisites_valid` state means that the request agrees with that supplied synthetic observation. It is not authorization to execute, proof of installed runtime/capability, a supported-host commitment, sandbox evidence, or a lifecycle-gate result. With no synthetic observation, the outcome is `unsupported`. This repository adopts no execution profile in this unit.

Results preserve separate request-readiness, authorization, execution, cleanup, evidence, and review axes. The result contract binds a supplied authorization reference to the exact request digest, enumerates expected cases and their outcomes, and carries bounded evidence references. Cross-field validation rejects execution without request-bound authorization, cases outside the expected set, and successful execution with missing or non-passing required cases. The validator itself always returns authorization `not_requested`, execution `not_started`, cleanup `not_applicable`, evidence `not_collected`, and review `not_performed`; it has no workload launcher and records no reviewer disposition. A structurally valid record is not proof that a referenced authorization or evidence object is authentic and is never a gate decision. Diagnostics contain stable codes and paths but never echo request values, including caller-supplied property names. Network and secrets are structurally limited to `disabled` in contract v1.

`fixtures/` is synthetic test material only. No fixture is an app, runtime probe, CI attestation, or gate evidence.
