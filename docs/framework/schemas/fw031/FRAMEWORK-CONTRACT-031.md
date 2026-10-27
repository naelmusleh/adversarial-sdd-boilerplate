---
id: FRAMEWORK-CONTRACT-031
type: framework-contract
title: FW-031 synthetic budget policy and result contract
status: active
version: 1.0
created: 2026-10-26
updated: 2026-10-26
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-ARCHITECTURE-005, DECISION-036, DECISION-037
---

# FRAMEWORK-CONTRACT-031 — FW-031 budget policy and result contract

## Scope and claim boundary

Contract version 1.0 defines JSON shapes and deterministic cross-record validation for per-run budget policies and result summaries. Its implementation unit accepts schemas, validation code, and synthetic fixtures only. Validation says that fields and declared relationships conform to this contract; it does not prove that a host observed a value, that a meter is authoritative, that a controller enforced a limit, that a process terminated, or that an actor is authorized. Fixtures contain invented values and are never application or pilot evidence.

The validator has no runtime, provider, meter, process-control, filesystem-mutation, gate-transition, or authorization integration. It emits validation diagnostics only. It cannot pass a task or lifecycle gate. Result records reject gate outcome fields, and exhausted runs cannot claim a completed execution.

## Policy schema

`budget-policy-v1.schema.json` identifies the policy and revision, its exact source revision, a SHA-256 digest of the canonical policy object with `policy_digest` omitted, run/nested-run scope, reset behavior, override availability, and an explicit list of limit definitions. Each limit states its kind, unit, scope, whether it is requested, measurement source identity, capability (`enforced`, `advisory`, or `unavailable`), start event, reset behavior, optional warning/exhaustion thresholds, threshold action, and behavior when measurement is unavailable. There are no implied limit values or reset defaults.

Version 1.0 permits only new-run resets and disables overrides. Manual/in-place reset and every override attempt fail validation until a later, separately approved contract selects an authority model. A requested but unavailable measurement must block the run or explicitly disable that limit; it cannot silently fall back to a proxy. A `run-tree` limit requires `aggregate-at-root` accounting, with exactly one aggregate owner at the root; per-run-exclusive samples cannot be summed implicitly. Spend remains bound to one run and cannot use `run-tree` scope until an explicit aggregate meter contract is defined.

## Result schema and invariants

`budget-result-v1.schema.json` binds a result to its policy ID/revision/digest and source revision. A run tree declares each run and parent; each observation has one accounting owner, a unique observation ID, and a unique per-owner/limit sequence. `per-run-exclusive` accounting assigns each event to one run and requires each requested per-run limit to be reported for every declared run. `aggregate-at-root` records aggregate observations only at the root and is mandatory for `run-tree` limits. Spend is reported separately and bound to one declared source run. Duplicate ownership keys, unknown runs/limits, mismatched units/sources, missing samples, or an accounting mode that differs from policy are invalid.

Warnings and exhaustion are checked against the latest observed value for each limit and accounting owner. Missing or unavailable requested measurements cannot produce `clear`; they remain `unknown`, or record `blocked` status and outcome when an enforced measurement's policy requires blocking. A reported spend amount is also compared with the matching declared spend limit thresholds; unknown spend is never treated as zero or compared. Reaching an exhaustion threshold requires `stop_state: exhausted` and forbids `execution_outcome: completed`. The checkpoint summary always carries preservation state, a last durable checkpoint reference when known, the remaining verification list, and the next authorized action. `confirmed` cancellation requires a termination observation reference; this is a structural requirement and not independent confirmation that termination occurred.

Spend is either `reported` with amount, currency, meter kind and identity, source run, time window, and provenance reference, or `unknown` with a bounded reason and all value/provenance fields null. Reported spend must structurally match a declared host/provider meter limit and run. This check does not establish the meter's authority or the truth of the report. Proxy counters are not accepted as spend. Missing, stale, mismatched, unavailable, unselected, or errored spend remains unknown.

## Validation interface

Run `python3 scripts/fw031_budget_contract.py policy <path>` to validate a policy, or `python3 scripts/fw031_budget_contract.py result --policy <policy-path> <result-path>` to validate a result against its policy. The Python functions `validate_budget_policy` and `validate_budget_result` accept UTF-8 JSON bytes or text. Both return a stable contract version, a boolean validity result, and bounded diagnostics without echoing input values. Invalid JSON, duplicate object keys, unknown versions, extra fields, oversize input, and cross-field inconsistencies fail closed.

The library and CLI are read-only. Result validity is structural evidence only; it is not a run completion, gate decision, enforcement observation, spend attestation, or authorization.
