---
id: FRAMEWORK-COVERAGE-002
type: framework-coverage
title: FW-TASK-029 signed receipt journey and surface coverage
status: draft
version: 0.1
created: 2026-10-24
updated: 2026-10-24
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-010, FRAMEWORK-ADV-027, DECISION-027, GATE-CATALOG-001, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-COVERAGE-002 — FW-TASK-029 signed receipt journey and surface coverage

## Gate work record

- **Gate:** G-COVERAGE — in progress; no pass is asserted.
- **Task:** FW-TASK-029, Produce verifiable signed CI evidence receipts.
- **Approved requirements:** FR-FW-032–034 under DECISION-027.
- **Prerequisites:** G-REQ passed for the approved task scope; G-FEAS passed for bounded feasibility only in FRAMEWORK-FEASIBILITY-010 and FRAMEWORK-ADV-027.
- **Source baseline:** `codex/v2-backlog-roadmap`, coverage artifact commit `cd0a0ba949a1815b6af781488cd7df8bc0c788b2` (content blob `b7fdf60a8da517935512941eba50a76dd772fea6`); remote CI and review use later commits containing this same exact blob.
- **Boundary:** Journey/state coverage and surface applicability only. No provider adoption, signing-key/trust architecture choice, application integration, implementation, policy threshold, production readiness, FW-TASK-020 substitution, or other v2 task is included.
- **Scope interpretation for review:** The feature is a governance workflow over local repository files, GitHub-hosted workflow/check results and artifacts, and repository pull-request review. These surfaces are inferred from DECISION-027, the FW-029 feasibility record, and the framework's local-first mission; no end-user web product or native mobile client is declared. Independent review should flag if this interpretation requires an owner decision.

## Capability and roles

The proposed capability produces bounded, signed provenance evidence for a particular hosted run and lets a reviewer verify that evidence outside the originating CI job against explicit policy and trust inputs. It helps a reviewer answer who issued a receipt, what exact run/checks and evidence digests it names, and whether the receipt matches the supplied verification policy. A receipt does not approve a gate, authorize a merge/release, establish check adequacy, or prove the underlying source is safe.

- **Framework/app owner:** approves the task scope and, in any later adoption, the trusted policy source and trust lifecycle. Those production choices remain for G-ARCH.
- **Maintainer or authorized CI operator:** runs the bounded hosted workflow and retains only the receipt/bundle artifacts needed for review.
- **CI workflow identity:** observes the exact source run and check records and signs the bounded receipt under the tested hosted identity.
- **Developer or agent:** supplies no privileged secret or local signature; may retrieve the receipt and bundle and run the documented verifier.
- **Independent reviewer / gate owner:** inspects identity, exact-revision binding, diagnostics, privacy limits, and whether the claim is within the evidence boundary. A valid signature alone is not a gate decision.

This is a planned journey inventory, not evidence of a production receipt service or application UI.

## Journey and state inventory

| Journey | Requirement IDs | Actor | Preconditions and start | Main transitions | Success exit | Failure exits | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J-029-01 — Prepare a trusted verification input set | FR-FW-033 | Reviewer or authorized operator | Receipt, bundle, policy, and trusted-root files are available from their recorded sources; expected policy/root digests are obtained through a separately trusted channel. | Confirm file identity and digests → select exact repository/source/ref/workflow policy → provide explicit trust inputs → start read-only verification. | Inputs are complete and match the expected external pins; verifier can proceed without fetching trust data. | Missing/unsupported root, missing external digest, altered policy/root bytes, stale or unknown trust state, or ambiguous source. | Stop; obtain trust material and expected digest through an authorized protected source; document freshness limits. Production protected storage and rotation are deferred to G-ARCH. Do not infer current revocation status from a snapshot. |
| J-029-02 — Produce a hosted evidence receipt | FR-FW-032, FR-FW-034 | Authorized CI workflow; operator observes | Approved exact source revision/ref and workflow definition are available; required checks have completed for the same source; bounded synthetic or otherwise explicitly authorized evidence is in scope. | Resolve one exact workflow run and attempt → query provider check records → match repository, source SHA/ref, event, workflow and signer identity → build canonical bounded payload → attest payload → retain receipt and bundle. | Receipt and signed bundle refer to one exact run, required-check manifest, check identities/conclusions, source and evidence digests; retained content is bounded. | Missing/ambiguous run or attempt; duplicate/missing/unexpected check; stale or wrong source/ref/workflow; check failure; signing unavailable; artifact retention failure; unexpected sensitive content. | Fail closed and retain a bounded diagnostic; fix the relevant input/workflow and rerun on a new exact revision. Do not reuse a partial receipt or claim signing success as offline verification. |
| J-029-03 — Verify receipt offline and repeatably | FR-FW-033 | Reviewer, developer or agent | Receipt, bundle, pinned policy, externally expected policy digest, and supplied trust root are present locally; verifier version and invocation are documented. | Parse and validate policy digest → constrain repository/source/workflow identity → verify signature and issuer against supplied trust material → compare receipt fields and required check set → verify evidence digests → report result and limits. | Exact bytes and all configured identities match; verifier reports provenance/integrity only. Repeating this read-only verification does not consume or authorize the receipt. | Altered receipt/bundle/signature; unknown issuer; wrong repository, source, workflow, contract, manifest, check or evidence digest; absent/mismatched trust/policy pin; unsupported replay semantics. | Reject with a specific diagnostic; acquire a fresh authorized evidence set or correct policy through its owner and rerun. Never edit a receipt to make it pass. A passed repeatable verification is not approval to perform another action. |
| J-029-04 — Review claim limits, privacy and gate disposition | FR-FW-034, FR-FW-032, FR-FW-033 | Gate reviewer and accountable owner | Verification output and linked provider evidence are available; exact revision and policy are identified. | Inspect receipt fields and digests → compare the verified claim to provider evidence and gate criteria → check data minimization and known retention → distinguish provenance from semantic/release claims → record accept/request-changes/blocked decision. | Reviewer can trace the receipt to exact evidence and accurately state both what the signature establishes and what remains unknown. | Receipt includes source/secrets/PII/unrestricted logs; provider retention is misstated; signature is treated as test-quality proof, gate approval, merge/release authorization, or replacement for FW-TASK-020. | Stop the overbroad claim; remove or quarantine inappropriate payload through an authorized process, document retention uncertainty, correct the claim, and reassess the exact scope. |

### Requirement and task-criterion coverage

| Requirement / acceptance criterion | Covered journeys | Observable state or evidence |
| --- | --- | --- |
| FR-FW-032 | J-029-02, J-029-03 | Versioned deterministic payload binds repository, source, workflow/contract revisions, provider run/attempt/event/ref, required-check manifest and identities, evidence digests, and issuer to the observed provider evidence and configured policy. |
| FR-FW-033 | J-029-01, J-029-03 | Offline verifier requires explicit trust and policy inputs; missing/unsupported inputs fail closed; exact identity and evidence mismatches return diagnostics; local unsigned content remains untrusted. |
| FR-FW-034 | J-029-02, J-029-04 | Retained fields are bounded; no raw source/diff/secret/personal data/unrestricted logs; documentation preserves claim limits and FW-TASK-020's independent app-hosted requirement. |
| FW-TASK-029 AC-1 | J-029-02, J-029-03 | Valid receipt accepted only when signature, issuer, repository, commit, workflow/contract, attempt, manifest, signer, required checks and evidence digests match policy. |
| FW-TASK-029 AC-2 | J-029-03 | Named negative mutations fail; repeat verification behavior is explicit. Prohibited replay is rejected only where policy supports that rule; this experiment allows repeatable read-only provenance checks. |
| FW-TASK-029 AC-3 | J-029-03 | A local unsigned receipt cannot be promoted by editing fields or copying terminal output. |
| FW-TASK-029 AC-4 | J-029-02, J-029-04 | Privacy review checks bounded receipt fields and transparent artifact/attestation retention limits. |
| FW-TASK-029 AC-5 | J-029-01, J-029-03 | Verification runs outside the originating CI job using explicitly supplied trust material; missing trust fails closed. |
| FW-TASK-029 AC-6 | J-029-04 | Provenance/integrity claims remain separate from test adequacy, semantics, reviewer independence, release authorization and production outcome; FW-TASK-020 remains required. |

## Surface and applicability matrix

| Surface | Applicability | Rationale and boundary |
| --- | --- | --- |
| Local repository / command-line verifier | Applicable | Policy, receipt and trust inputs are assembled and checked locally. This demonstrates the tested verifier environment only; it does not prove OS sandboxing, network denial, general portability, or a production trust source. |
| GitHub Actions hosted workflow | Applicable | The bounded probe observes one exact hosted run and signs a synthetic receipt using the tested workflow identity and permissions. This is not a permanent provider selection or app adoption. |
| GitHub Checks / workflow-run evidence | Applicable | Exact provider run/attempt/check identities, names, app, conclusions, source SHA/ref/event are inputs to receipt construction; branch protection remains a separate observed setting and is not established here. |
| Hosted artifact download/retention | Applicable | Receipt and bundle must be retrieved together for offline verification. Artifact retention was observed as one day; hosted attestation deletion/retention semantics remain unknown. |
| Pull-request review / gate-record review | Applicable | Owner/reviewer evaluates the evidence boundary, residual risks, and whether downstream claims are authorized. A cryptographic pass does not itself pass a product gate. |
| Public or end-user web application UI | Not applicable | No end-user product interface is part of DECISION-027 or FW-TASK-029; no such platform promise is made. Revisit only under separately approved scope. |
| Android/iOS native application UI | Not applicable | No native client or mobile user flow is in the approved framework capability. Local or hosted workflow surfaces do not imply native support. |
| Next.js, FastAPI, Rust/Axum profile lanes | Not applicable to this task | These are unrelated synthetic adapters from FW-TASK-013/028, not consumer platforms for signed receipts. No stack adapter compatibility is asserted. |

The surface interpretation above is a reasoned inference from the approved local-first framework mission and DECISION-027. It changes no product/platform requirement. Independent review should assess whether a separate owner decision is needed; if the reviewer finds the inference materially alters approved scope, stop before G-CX and request that decision.

## Required failure-mode applicability

| Category | Applicable | Expected state and rationale |
| --- | --- | --- |
| Empty | Yes | Missing receipt, bundle, policy pin, trust root, required check, or evidence digest cannot produce verification success. |
| Malformed or corrupt | Yes | Invalid serialization, truncated/altered bundle, malformed signature, corrupt receipt, or invalid trust-root structure fails with a diagnostic. |
| Unavailable | Yes | Missing verifier capability, provider/API outage, expired artifact, unavailable trust material or unknown retention/revocation state is unavailable/blocked, never pass. |
| Unauthorized | Yes | Wrong repository/ref/workflow/issuer or unsupported source cannot be accepted by policy; receipt has no authority to approve or deploy. |
| Degraded | Yes | Partial provider checks, incomplete bundle, ambiguous retry, or one-day artifact expiry prevents a complete verification claim. |
| Abuse | Yes | Receipt/policy/check substitution, invalid signatures, trust-root changes, replay-policy confusion, or claims that overstate semantics are rejected or flagged. Repeatable read-only verification is explicitly allowed and is not an authorization replay. |
| Recovery | Yes | After correcting the trust input, policy or source/workflow, obtain a new bounded evidence set and reverify; preserve the old failed attempt and do not mutate evidence to pass. |

## G-COVERAGE criterion preparation

| Criterion | Prepared evidence | Current status |
| --- | --- | --- |
| GCOV-01 | Four journeys map FR-FW-032–034 and all six task acceptance criteria to actors, preconditions, transitions, success/failure exits and recovery. | PASS; see the exact review and CI disposition below. |
| GCOV-02 | All seven required failure categories are explicitly applicable with expected fail-closed or blocked outcomes and recovery. | PASS; see the exact review and CI disposition below. |
| GCOV-03 | Every declared workflow/review surface is in the matrix; end-user web/mobile and unrelated stack adapters are excluded with rationale and downstream effect. | Prepared; independent review pending; scope inference submitted for review. |

## Evidence, exclusions and next action

- **Evidence refs:** DECISION-027; FR-FW-032–034 and FW-TASK-029 AC-1–6; FRAMEWORK-FEASIBILITY-010 v2.2; FRAMEWORK-ADV-027; FRAMEWORK-ADV-028; GATE-CATALOG-001; approved FRAMEWORK-GATE-CONTRACT-001 v1.0.
- **Known feasibility limits carried forward:** tested repo visibility/runner/action pins and supplied trust snapshot only; no current root freshness/revocation proof; hosted attestation retention/deletion unknown; production policy-digest trust source deferred to G-ARCH.
- **Exclusions:** provider adoption, production trust lifecycle/architecture, app integration, source changes, end-user UI, release/merge authorization, FW-TASK-020 replacement, and all unrelated v2 tasks.
- **Gate result:** G-COVERAGE PASS for the approved bounded FW-TASK-029 scope, recorded below.
- **Next action:** Proceed to product-appropriate nonvisual G-CX evidence for receipt creation, offline verification, and review journeys. No owner scope decision was required by the independent coverage review.
- **Prohibited next work:** implementation, provider adoption, production trust-source selection, app integration, branch-protection changes, or deployment.


## Independent G-COVERAGE disposition (2026-10-24)

**G-COVERAGE: PASS** for the approved bounded FW-TASK-029 scope. Independent reviewer `/root/fw029_independent_review` passed GCOV-01, GCOV-02, and GCOV-03 on the exact coverage artifact blob `b7fdf60a8da517935512941eba50a76dd772fea6`, present at remote review commit `ac2efd31870a10a2589b6cfb8f6ce577ea1ce5bb`. The reviewer confirmed four complete journeys map all requirements and six acceptance criteria; all seven required failure categories are addressed; and the local verifier, hosted workflow/checks/artifacts, and pull-request review surfaces follow DECISION-027. End-user web/mobile surfaces and unrelated profile lanes are properly excluded. No owner decision is needed. The review and criterion rationale are recorded in [FRAMEWORK-ADV-028](../adversarial-reviews/FRAMEWORK-ADV-028.md).

Verify Pipeline [40120164557](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40120164557) passed all three required jobs on exact commit `e1bab3677b28ea18d9de8931faaec284ed4e9343`, which contains the reviewed coverage blob. The earlier run [40120004006](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40120004006) is excluded because an incomplete transferred backlog lacked its front matter and caused the Python job to fail; the backlog was restored from the intact prior revision before the successful run.

G-COVERAGE clears journey and surface coverage only. It does not authorize implementation, provider adoption, production trust-source decisions, or replacement of FW-TASK-020. The next permitted gate is G-CX.
