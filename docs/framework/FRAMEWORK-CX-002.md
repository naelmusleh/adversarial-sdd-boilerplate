---
id: FRAMEWORK-CX-002
type: framework-cx
title: FW-TASK-029 receipt verification interaction contract
status: draft
version: 0.1
created: 2026-10-24
updated: 2026-10-24
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-COVERAGE-002, FRAMEWORK-FEASIBILITY-010, FRAMEWORK-ADV-027, FRAMEWORK-ADV-028, DECISION-027, GATE-CATALOG-001, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-CX-002 — FW-TASK-029 receipt verification interaction contract

## Gate work record

- **Gate:** G-CX — in progress; no pass is asserted.
- **Task:** FW-TASK-029, within DECISION-027 and FR-FW-032–034 only.
- **Prerequisites:** G-REQ and bounded G-FEAS passed; G-COVERAGE passed for FRAMEWORK-COVERAGE-002.
- **Target:** A nonvisual governance workflow spanning a local verifier, a bounded hosted CI workflow, provider check/artifact records, and pull-request/gate review. There is no end-user interface, mobile surface, or production service in this scope.
- **Review method:** Manual tool-neutral critique of every covered journey and state using explicit interaction traces below. There is no rendered prototype or GUI to capture; none is claimed. The review evaluates status visibility, user control, consistency, error prevention, recognition, recovery, content clarity, trust calibration, and cross-surface handoff.
- **Source checkpoint:** coverage commit `cd0a0ba949a1815b6af781488cd7df8bc0c788b2`, coverage blob `b7fdf60a8da517935512941eba50a76dd772fea6`; this interaction artifact requires its own exact-revision CI and independent review.
- **Boundary:** Interaction semantics and critique evidence only. No implementation, provider adoption, production trust-source or rotation choice, threshold, app integration, merge/release authorization, or FW-TASK-020 replacement.

## Interaction principles and state vocabulary

1. Show a clear state before an operator acts: `ready`, `in progress`, `passed`, `failed`, `blocked`, `unavailable`, or `stale`. A `passed` state always names what was verified and against which exact policy/source revision.
2. Keep provenance, policy matching, cryptographic verification, and gate/owner decisions as distinct steps and outcomes. Do not collapse a verified signature into “gate approved.”
3. Fail closed on missing or mismatched inputs. Explain the mismatched identity or missing item, point to the evidence location, and state the next safe recovery action. Never recommend editing signed evidence to repair it.
4. Preserve exact run, source, policy and trust-material identity across local/hosted/review handoffs. A changed source or policy requires a new result; old results remain historical.
5. Repeatable offline verification is read-only. State that rechecking does not consume or authorize the receipt. Do not introduce an arbitrary one-use or freshness claim unsupported by the current policy.
6. State privacy and retention facts plainly: only bounded identifiers/digests are expected; the test artifact is retained one day; hosted-attestation deletion and freshness/revocation are unknown. Do not claim deletion or current trust without evidence.

## Full-scope interaction traces

| Trace | User action and system response | Visible status / trust signal | Failure and recovery behavior |
| --- | --- | --- | --- |
| CX-029-A — Prepare offline inputs | Reviewer selects receipt, bundle, policy, external expected policy digest and supplied root. Verifier reports each input's filename, digest match, and policy scope before starting signature checks. | `ready` only when every required file is present and both external pins match. Show repository/source/ref/workflow expected by policy. | Missing file, unsupported format, or digest mismatch → `blocked` with exact input name and expected-vs-observed digest; advise obtaining inputs/pins from authorized source. No silent defaults or network fetch. |
| CX-029-B — Create receipt from hosted checks | Authorized operator starts the bounded workflow on the intended ref. Workflow resolves one run/attempt, identifies required provider checks, builds the bounded receipt, signs it, and uploads the receipt/bundle. | Show run URL/ID, source SHA/ref, workflow identity, required-check count and conclusion, signing outcome, artifact ID/name, and retention. Distinguish “receipt signed” from “offline verification pending.” | Ambiguous run/attempt, missing/duplicate/unexpected check, wrong SHA/ref/workflow, non-success conclusion, signer failure, or upload failure → `failed`/`blocked` with the failed stage and bounded diagnostic; no partial output is treated as a complete receipt. Correct inputs and create a fresh run. |
| CX-029-C — Verify receipt locally | Reviewer invokes the documented read-only verifier with all explicit inputs. It verifies cryptographic issuer/signature and exact policy/receipt fields, then reports each stage separately. | `passed` is phrased “signature and configured provenance policy verified,” with source/run/policy digest. Explicitly say that tests, code semantics, gate approval and release authorization are not established. | Any mismatch → `failed` with named rule, expected and observed identity where safe, and evidence location. Preserve inputs; do not edit receipt/bundle. Correct policy through authorized path or obtain a new receipt; rerun all steps. |
| CX-029-D — Review evidence and decide next action | Reviewer follows provider links, confirms run/check identities, examines bounded receipt fields and known retention, then records a gate/review disposition. | Separate labels for cryptographic verification, provider check success, reviewer disposition and owner authorization. Indicate whether review is `accepted`, `changes requested`, or `blocked`; identify the responsible role. | Stale source/policy, missing provider evidence, retention uncertainty, overclaimed trust or a proposed use as FW-TASK-020 replacement → `blocked` or request changes. Reopen at the affected upstream step; no gate/merge/release is implied by a valid signature. |

## Status rollup and recovery rules

- Overall status is `blocked` if a required identity, trust input, policy pin, run/check or evidence item is missing, unsupported, stale or mismatched.
- Overall status is `failed` if verification runs and rejects a signature, receipt field, check result, policy digest or evidence digest.
- Overall status is `in progress` while hosted receipt creation, local verification, or human review remains incomplete.
- Overall status is `passed` only for the bounded cryptographic and configured-policy verification step; it never rolls up to gate acceptance or authorization by itself.
- Preserve the failed run/receipt as historical evidence. Recovery creates a fresh source-bound run or corrected owner-controlled policy and a new verification result. Never rewrite receipt bytes or relabel a failed result.
- Read-only verification may be repeated. Repetition does not change receipt state, grant authority, or establish freshness/revocation.

## Tool-neutral critique record (prepared for independent review)

| UX heuristic | Evidence inspected | Initial finding / disposition |
| --- | --- | --- |
| Status visibility and trust calibration | Four interaction traces; outcome vocabulary; separate signature/check/gate states. | No conflation in the contract. Reviewer should challenge whether “passed” is sufficiently scoped and visible across local and CI handoffs. |
| User control and error prevention | Explicit input selection, no defaults, fail-closed mismatch handling, no receipt mutation. | Safe recovery preserves evidence. No automatic retry loop or privileged action is specified. |
| Consistency and recognition | Shared status labels, stable source/run/policy identities across traces. | Same identities are repeated at each handoff; reviewer should identify any drift or ambiguous labels. |
| Error recovery and help | Named failed stage, diagnostic, evidence location, responsible role and fresh-run recovery. | Recovery route is bounded and avoids editing signed data. |
| Content clarity and cognitive load | Separate cryptographic, provider, reviewer and owner outcomes; bounded privacy and retention claims. | Claims are intentionally narrow; reviewer should flag jargon without an understandable status or actionable next step. |
| Cross-surface behavior | Hosted creation → artifact retrieval → local verification → PR/gate review. | Handoff explicitly carries receipt, bundle, source/run, policy and root digests. Artifact expiration or missing provider link blocks rather than silently downgrades. |
| Accessibility / rendered UI | No visual product surface or screen exists in scope. | Not applicable to this nonvisual CLI/CI/review contract; this does not establish accessibility for any future interface. |

## Evidence, limitations and next action

- **Covered journeys:** J-029-01 through J-029-04 in FRAMEWORK-COVERAGE-002; all requirements, task criteria, failure categories and applicable surfaces are included.
- **Evidence refs:** DECISION-027; FRAMEWORK-COVERAGE-002; FRAMEWORK-FEASIBILITY-010; FRAMEWORK-ADV-027/028; GATE-CATALOG-001; contract v1.0.
- **G-CX-01/02/03:** Prepared for independent review across all four traces; no visual prototype, runtime behavior, accessibility test, or product UI evidence is claimed.
- **Next action:** Independent critique of this complete interaction contract, followed by exact-commit Verify Pipeline and recorded findings/disposition.
- **Prohibited next work:** implementation/provider selection/production trust-source choices, app adoption, release, or changes to FW-TASK-020.
