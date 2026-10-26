---
id: FRAMEWORK-CONTRACT-032
type: framework-contract
title: FW-031 GitHub Actions run/job evidence contract
status: draft
version: 1.0
created: 2026-10-26
updated: 2026-10-26
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-ARCHITECTURE-006, FRAMEWORK-FEASIBILITY-014, FRAMEWORK-COVERAGE-005, FRAMEWORK-CX-005, DECISION-038
---

# FRAMEWORK-CONTRACT-032 — GitHub Actions run/job evidence v1

## Purpose and claim boundary

This version defines the wire shape and deterministic validation rules for a passive GitHub Actions run/job evidence record. The companion JSON Schema is `actions-run-job-evidence-v1.schema.json`. A valid record means only that the submitted structure and declared relationships conform to this contract. It does not authenticate a source, establish the truth or completeness of any value, prove timeout enforcement or workload termination, measure agent-internal activity, change a gate, or authorize work.

The implementation unit has no network or API access, collector, workflow or permission changes, timeout configuration, runtime integration, process control, host/profile adoption, or real measurements. All committed examples and test inputs are labeled as synthetic fixtures. Validation output is advisory and carries no gate result. The existing FRAMEWORK-CONTRACT-031 budget policy/result contract remains separate and unchanged.

## Record sections and semantics

| Section | Contract | Invariant |
| --- | --- | --- |
| `source` | Acquisition state, repository/workflow identity, source reference, observation time, optional response revision/digest | Intended to contain references and bounded identifiers only; the validator cannot detect secrets or authenticate a reference. No tokens, prompts, job logs, or user data belong here. Partial/denied/unavailable are not success. |
| `identity` | Run ID, Actions `run_attempt`, job ID/name, optional event; explicit completeness state | `run_attempt` means GitHub Actions rerun attempt only. Available means the run ID, attempt, job ID, and name are all present. Partial means some but not all are present. Unknown/unavailable means none are present. |
| `revisions` | Workflow, triggering, and executed revisions, each with state, SHA, and source | Roles remain distinct; no missing SHA is copied from another role. Available requires a 40- or 64-character lowercase hexadecimal SHA and source. |
| `timing` | Run and job start/completion points, each with state/value/source and a repeated identity binding | Every populated point has timezone-aware timestamp and source. Intervals must be ordered and bound to the same run/attempt/job. No intervals are combined across jobs. |
| `timeout` | Configuration state/minutes/revision/source separated from observed timeout state, host conclusion, and source | Configuration does not imply an observed timeout. Timeout outcome and host conclusion must agree when both are available. No threshold is selected here. |
| `cancellation` | Request state/time/source, host terminal state/source, and workload termination state/observation | A request or canceled host state never implies workload termination. `confirmed` requires an observation reference and a complete identity tuple; absence remains unknown/unavailable. |
| `measurements` | Named metric with measured/unknown/unavailable state, value/unit/source kind/source/scope/interval/reason | Measured requires complete direct provenance and exact identity-bound scope. Spend requires an authoritative meter; synthetic-only provenance is permitted only when the entire record is labeled `fixture_only`. Unknown/unavailable has no value or provenance and has a reason. Proxies such as elapsed time, step count, retry count, or public zero billing are rejected as evidence of tool calls, agent retries, nested agents, resources, or spend. |
| `limitations` | Bounded enum values for incomplete source and capability states | Limitations document uncertainty; they do not permit missing identity to be inferred or convert an unavailable source into an empty/successful result. |

A denied/unavailable retrieval may be represented with known repository/workflow context and an unknown/unavailable identity. A complete source requires a complete identity. Any evidence object that repeats run/attempt/job identifiers must match the record identity exactly. If identity is incomplete, dependent populated timing, timeout outcome, cancellation/workload observation, and measurements are invalid. Validation never fills fields or merges different source records. The validator is stateless and does not store, append, or preserve records; any later storage policy must define those behaviors separately.

## Deterministic validation

The validator accepts UTF-8 JSON text or bytes and returns a stable result containing contract/version, validation scope, valid boolean, and at most 32 path-based diagnostics. It rejects duplicate JSON keys, invalid UTF-8/JSON, non-finite numbers, inputs above 512 KiB, unsupported schema keywords, extra properties, unknown enums, and malformed schemas. It does not echo submitted values.

Cross-field checks enforce acquisition/identity state consistency; revision state/value/source consistency; timing identity binding and timestamp order; timeout configuration and outcome separation; cancellation/workload evidence separation; unique measurement names; metric provenance and non-proxy state semantics; and limitation consistency. `fixture_only=true` marks invented evidence and cannot be interpreted as observed source data. No deterministic validator can determine whether source references are authentic or whether claimed direct measurements actually occurred.

## Synthetic fixtures and verification map

The test suite uses clearly named synthetic fixtures only. Positive fixtures exercise complete identity binding, distinct revision roles, ordered run/job timing, configured versus observed timeout, cancellation versus terminal versus workload state, unknown/unavailable values, and a fully populated synthetic provenance shape. Negative fixtures cover malformed/duplicate JSON, unknown fields/enums, missing or contradictory identity, cross-run/job/attempt timing, reversed timestamps, SHA-role substitution, inconsistent timeout claims, cancellation treated as termination, missing direct provenance, proxy/synthetic evidence mislabeling, duplicate metrics, and denied/partial source inflation.

- FR-FW-041: source/identity tuple and revision roles bind; timing provenance cannot cross run/attempt/job boundaries.
- FR-FW-042: timeout configuration, timeout observation, host terminal result, cancellation request, and workload termination are distinct validated states.
- FR-FW-043: metrics require direct provenance; unknown/unavailable remains valueless; unsupported proxies are rejected.

## Deferred work and explicit non-adoption

No collection route, private Actions-read permission, workflow change, timeout value, cancellation experiment, metric source, spend meter, retention policy, or profile adoption is selected. API/network collection, runtime adapters, process control, real measurements, and enforcement claims require new owner-approved scopes. The contract is not wired into CI evidence or a gate runner; the GitHub Actions workflow does not change as part of this unit.
