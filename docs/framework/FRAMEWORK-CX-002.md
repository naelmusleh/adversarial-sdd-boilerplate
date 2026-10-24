---
id: FRAMEWORK-CX-002
type: framework-cx
title: FW-TASK-029 receipt verification interaction contract
status: draft
version: 0.4
created: 2026-10-24
updated: 2026-10-24
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-COVERAGE-002, FRAMEWORK-FEASIBILITY-010, FRAMEWORK-ADV-027, FRAMEWORK-ADV-028, FRAMEWORK-ADV-029, FRAMEWORK-ADV-030, FRAMEWORK-ADV-031, DECISION-027, GATE-CATALOG-001, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-CX-002 — FW-TASK-029 receipt verification interaction contract

## Gate work record

- **Gate:** G-CX — PASS within the bounded scope; see FRAMEWORK-ADV-031.
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
| CX-029-A — Prepare offline inputs | Reviewer selects receipt, bundle, policy, external expected policy digest and supplied root. Verifier reports each input's filename, digest match, and policy scope before starting signature checks. | `ready` only when every required local input is present and readable and both external pins match. Show repository/source/ref/workflow expected by policy. | Required local input not supplied or unsupported → `blocked`, naming the input and recovery action. An expected provider artifact cannot be retrieved or has expired → `unavailable`. A digest/pin comparison that runs and finds different bytes → `failed`, with expected/observed digest. No silent defaults or network fetch. |
| CX-029-B — Create receipt from hosted checks | Authorized operator starts the bounded workflow on the intended ref. Workflow resolves one run/attempt, identifies required provider checks, builds the bounded receipt, signs it, and uploads the receipt/bundle. | Show run URL/ID, source SHA/ref, workflow identity, required-check count and conclusion, signing outcome, artifact ID/name, and retention. Distinguish “receipt signed” from “offline verification pending.” | Provider run/check data cannot be queried → `unavailable`. A query returns ambiguous run/attempts, missing/duplicate/unexpected checks, wrong SHA/ref/workflow, or a non-success check conclusion → `failed` at the selection/policy-check stage. Signing or upload operation returns an error → `failed` at that operation; if the provider service cannot be reached, `unavailable`. No partial output is a complete receipt. Correct inputs and create a fresh run. |
| CX-029-C — Verify receipt locally | Reviewer invokes the documented read-only verifier with all explicit inputs. It verifies cryptographic issuer/signature and exact policy/receipt fields, then reports each stage separately. | `passed` is phrased “signature and configured provenance policy verified,” with source/run/policy digest. Explicitly say that tests, code semantics, gate approval and release authorization are not established. | Missing local argument/file or unsupported input before verification → `blocked`; verifier/tool cannot be obtained or started because a dependency is unavailable → `unavailable`; verification runs and rejects a supplied signature, identity, receipt, check, policy digest or evidence digest → `failed`. Preserve inputs; do not edit receipt/bundle. Correct policy through authorized path or obtain a new receipt; rerun all steps. |
| CX-029-D — Review evidence and decide next action | Reviewer follows provider links, confirms run/check identities, examines bounded receipt fields and the retention facts (one-day artifact retention; hosted-attestation retention/deletion unknown), then records a gate/review disposition. | Show the attempt status (`stale`, `unavailable`, `blocked`, `failed`, `in progress`, or `passed`) separately from reviewer disposition (`accepted`, `changes requested`, or `blocked`) and owner authorization. Identify the responsible role. | A previously produced receipt/result bound to a different selected source, workflow, contract, policy or trust revision → attempt `stale`. Required provider evidence that cannot be retrieved → `unavailable`. An absent owner decision or required review prerequisite → reviewer disposition `blocked`; it does not rewrite the attempt status. Present evidence that fails identity/provenance checks or makes an unsupported trust claim → attempt `failed` and disposition `changes requested`. Record retention facts without implying a guarantee. Retention uncertainty blocks only when the intended use requires an unproven retention/deletion guarantee. A proposed use as FW-TASK-020 replacement is out of scope and must be rejected. No gate/merge/release is implied by a valid signature. |

## Status rollup and recovery rules

- **Attempt status and review disposition are separate fields.** Attempt status is exactly one of `stale`, `unavailable`, `blocked`, `failed`, `in progress`, or `passed`. Reviewer disposition is exactly one of `accepted`, `changes requested`, or `blocked`; owner authorization is recorded separately. Never use a disposition as an attempt status.
- Assign attempt status by the primary condition at the earliest stage that prevents completion: `stale` only for an already-produced receipt/result whose bound source, workflow, contract, policy or trust revision differs from the currently selected scope; `unavailable` when an external verifier/provider record/artifact cannot be retrieved or a needed service/tool cannot be reached; `blocked` when a required local input or human prerequisite has not been supplied, or the supplied input is unsupported before the operation starts; `failed` when an executed operation or comparison rejects supplied data or returns an error; `in progress` while the attempt is incomplete without a known blocking outcome; and `passed` only when every bounded cryptographic and configured-policy step succeeds. If several conditions are found, report all of them but assign the status for the earliest stage that stops the attempt; do not let later downstream symptoms override it. A reviewer may separately mark `changes requested` after a passed verifier result if the interpretation or claim is unsupported. Never roll a verifier pass up to gate acceptance or authorization.
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
- **G-CX disposition:** FRAMEWORK-ADV-031 records independent PASS for GCX-01–03 on the complete v0.4 contract. Verify Pipeline [40133369128](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40133369128) passed all three required jobs on exact commit `25c2574f244405b44c408911d4792548320f3f78`, containing the reviewed v0.4 blob `c51eb817aeddb7d6505f57b83a2ab1ca954cb15d`.
- **Next action:** Proceed to G-ARCH planning only after its scope and evidence are opened under the applicable owner-approved scope. No implementation/provider selection/production trust-source choices, app adoption, or release are authorized.
- **Prohibited next work:** implementation/provider selection/production trust-source choices, app adoption, release, or changes to FW-TASK-020.


## Initial independent G-CX review and finding dispositions

The first full-scope independent critique returned **NEEDS-CHANGES** at source commit `644ed30f96794f6aec6ffda28539ba6e88c935de`, CX artifact blob `a9ab320a497acc8de21c26e821dbe188c826454e`. Findings and rationale are recorded in [FRAMEWORK-ADV-029](../adversarial-reviews/FRAMEWORK-ADV-029.md).

- **CX029-01 — P2 status taxonomy ambiguity — resolved in this revision.** The earlier traces could classify the same mismatch as either blocked or failed. The state rollup now defines deterministic precedence: stale prior results; unavailable evidence/tool; preflight-missing input as blocked; verifier rejection as failed; in-progress; then bounded passed. CX-A and CX-C align to that boundary.
- **CX029-02 — P2 retention uncertainty framed as a block — resolved in this revision.** The trace now states the observed one-day artifact retention and unknown hosted-attestation retention/deletion. Uncertainty alone does not block this bounded feasibility use; block only if a specific intended use requires a retention/deletion guarantee the evidence cannot establish.

The full affected-scope rerun was performed on v0.2. It resolved CX029-02 and clarified local-verifier handling for CX029-01, but found a new cross-trace status inconsistency, CX029-03. The exact result is recorded in [FRAMEWORK-ADV-030](../adversarial-reviews/FRAMEWORK-ADV-030.md). G-CX remains blocked until the owner authorizes another correction/review cycle under the repository's two-loop guard.


## G-CX review round 2 — owner checkpoint required

On FRAMEWORK-CX-002 v0.2 at exact commit `c229554f130243bd4ea445811ae541bd707e6b8d` (blob `fa6fc6ca7ddfbd850f068e730822a0657ce114c3`), the independent reviewer resolved CX029-02 and confirmed the local-verification part of CX029-01, but returned NEEDS-CHANGES for full-scope GCX-03 due to new finding CX029-03. CX-A classifies missing inputs as `blocked` while the rollup classifies unavailable evidence as `unavailable`; CX-B uses combined `failed`/`blocked` labels without a deterministic mapping; CX-D classifies stale source/policy and missing provider evidence as `blocked` instead of `stale`/`unavailable`. The reviewer requires a single state mapping per failure class across every trace, or explicit separation of interaction-layer status from reviewer disposition.

This was the second consecutive review/fix cycle. Per the repository operating guard, G-CX is **BLOCKED** pending an explicit owner checkpoint before any third correction/review cycle. This v0.3 record does not implement the CX029-03 correction and has not been independently reviewed.

## G-CX review round 3 — owner authorized and complete

The owner explicitly authorized one final correction and full-scope independent review after round 2. Version 0.4 resolves CX029-03 by defining attempt status separately from reviewer disposition, assigning every named failure in CX-029-A through CX-029-D one deterministic status, and using earliest blocking stage when multiple conditions occur. The independent reviewer passed GCX-01–03 for exact reviewed blob `c51eb817aeddb7d6505f57b83a2ab1ca954cb15d` at source commit `813019f11a0c8bf4f669926b1c9ff0cc4955dda3`; FRAMEWORK-ADV-031 records criterion-level evidence and all finding dispositions. Verify Pipeline [40133369128](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40133369128) passed all three required jobs on exact commit `25c2574f244405b44c408911d4792548320f3f78`, which contains the same reviewed contract blob. G-CX passes within the approved scope. The final owner-authorized review cycle is consumed; the next lifecycle gate is G-ARCH. No implementation/provider adoption/production trust-source selection/application integration/release/FW-TASK-020 substitution is authorized.
