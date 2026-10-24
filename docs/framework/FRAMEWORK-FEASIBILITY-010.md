---
id: FRAMEWORK-FEASIBILITY-010
type: feasibility-register
title: FW-TASK-029 signed evidence receipt feasibility
status: draft
version: 0.2
created: 2026-10-24
updated: 2026-10-24
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-ADV-024, DECISION-027, DECISION-019, FRAMEWORK-CI-RELEASE-POLICY-001
---

# FRAMEWORK-FEASIBILITY-010 — FW-TASK-029 signed evidence receipt feasibility

## Scope and exclusions

This is a bounded G-FEAS plan for FR-FW-032–034 under DECISION-027. It will assess whether a compact receipt can bind exact repository/source identity, the required-check manifest, trusted workflow identity, hosted check results and evidence digests; whether a standalone verifier can validate the signed receipt with locally supplied trust material; and what issuer, key rotation, replay, privacy and claim limits remain.

The plan does not select or adopt a provider, signer, key-management mechanism, receipt format, or application integration. It does not change repository CI policy, use production credentials or product data, replace FW-TASK-020's app-hosted CI requirement, alter FW-TASK-028, or authorize implementation. Any hosted probe uses synthetic content, a temporary `workflow_dispatch` workflow, an ephemeral hosted runner, no repository secrets, and the minimum temporary permissions needed for the tested operation. The temporary workflow and generated data are removed after evidence capture. No claim about branch protection or trusted-branch enforcement is made.

## G-REQ source and frozen scope

DECISION-027 approved FW-TASK-029 and FR-FW-032–034. The independent reviewer passed G-REQ on corrected source revision `309e667a659fa285632cb0d6066f2fd337769ebf`; Verify Pipeline [40093307764](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40093307764) passed all three jobs on that revision. The G-REQ finding and disposition are in [FRAMEWORK-ADV-024](../adversarial-reviews/FRAMEWORK-ADV-024.md). The subsequent evidence-record commit is `66f3e6e243d843511779c8634b8abb162e0e3b0a` with Verify Pipeline [40093401070](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40093401070) passing all three jobs.

## Dated primary-source observations

Official GitHub documentation describes artifact attestations as signed claims that can include repository, organization, environment, commit SHA, triggering event, and workflow information. GitHub's `actions/attest` supports a custom predicate and requires `id-token: write`, `attestations: write`, and `artifact-metadata: write`; this permission surface must be isolated and justified. GitHub documentation recommends attestations for released artifacts and warns that an attestation does not guarantee an artifact is secure. It discourages signing individual source/document files or frequent test builds; a one-per-run governance receipt is not explicitly evaluated as a supported subject pattern, so the probe must treat fit as an open question. Sources: [GitHub artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations), [actions/attest](https://github.com/actions/attest), and [GitHub attestation setup](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations).

GitHub documents offline verification using the receipt/artifact bytes, a downloaded attestation bundle, and trusted-root material. The `gh attestation verify` interface supports repository and signer-workflow identity constraints, a custom trusted root, and JSON output for additional policy checks. For offline bundles, repository name alone cannot detect a rename or name reuse; the signing certificate's repository ID must also be compared with a separately trusted expected ID. GitHub's public repositories use Sigstore Public Good; private repositories use GitHub's Sigstore instance, which has no transparency log and only federates with GitHub Actions. The offline guide warns that previously exported root material can become stale after key rotation and cannot reveal later revocation. Sources: [offline verification](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline), [gh attestation verify](https://cli.github.com/manual/gh_attestation_verify), and [gh attestation trusted-root](https://cli.github.com/manual/gh_attestation_trusted-root).

Sigstore Cosign also supports keyless blob signing with a bundle containing the signature, certificate, and transparency-log inclusion proof, with issuer and signer identity checks. Its suitability for the repository's required workflow identity, private-repository trust path, receipt predicate, and offline policy remains to be compared rather than assumed. Source: [Sigstore Cosign verification](https://docs.sigstore.dev/cosign/verifying/verify/) and [blob signing](https://docs.sigstore.dev/cosign/signing/signing_with_blobs/).

## Applicability and risk screen

| Probe | Question and evidence | Classification rule | Requirement/dependency |
| --- | --- | --- | --- |
| FEAS-FW029-01 — receipt payload and policy binding | Can a deterministic synthetic receipt bind repository ID, source SHA/ref, contract/workflow revision and immutable signer identity, exact required-check manifest digest, provider run/attempt/event, provider check IDs/names/conclusions/head SHA, and digests for bounded evidence files? Record schema version, canonical bytes/digest, and positive/negative comparisons. | Supported only for fields observable from the selected provider and signed by the trusted identity. Provider-reported data and workflow-authored predicate data are distinguished; unverifiable fields remain unavailable. | FR-FW-032/033; DECISION-019 exact-check-manifest and trusted-workflow semantics. |
| FEAS-FW029-02 — hosted signing capability | On a temporary, `workflow_dispatch`-only hosted job, can a pinned candidate action sign a small synthetic receipt without secrets, using ephemeral workflow identity, and make a verifiable bundle available? Record exact action commit, workflow digest, run/attempt, required permissions, subject digest, signer identity, repository ID, and clean-up. | Demonstrates only the candidate mechanism and current repository environment. Permission escalation, unsupported repo visibility, or inability to attest a receipt is an explicit constraint; no provider is selected by the probe. | FR-FW-032/033; G-ARCH must later select any mechanism. |
| FEAS-FW029-03 — offline verifier and trust freshness | Can verification run outside the originating CI job using only receipt bytes, bundle, pinned policy, and supplied trust material? Verify signer workflow identity, issuer, repository ID, source SHA, manifest digest and check set; also document how trust material is obtained, aged, rotated, revoked, or refreshed. | Offline support passes only if the signed bundle validates from local inputs and policy checks pass. This is not an OS/network isolation test. Missing/stale trust inputs or unknown revocation remain visible limitations and cannot be called current trust. | FR-FW-033; G-ARCH decides supported trust update/revocation policy. |
| FEAS-FW029-04 — adversarial integrity and substitution | Mutate one field/byte at a time: receipt bytes, repo ID, source SHA, workflow/signer identity, workflow revision, manifest digest, run attempt, provider check ID/name/conclusion/head SHA, evidence digest, and trust root. Include missing check and unsigned receipt cases. | Each mismatch must fail with a named reason; signature success alone is insufficient. Predicate claims are trusted only when signer identity is trusted and the configured policy validates every required field. | FR-FW-033; acceptance criteria 1–3. |
| FEAS-FW029-05 — privacy, retention and reuse | Inspect generated receipt/bundle fields and transfer path; determine which data is retained by provider APIs and what is needed for an offline verifier. Test that no raw source, diff, secret, personal data, or unrestricted logs are included. | Only bounded identifiers, conclusions, digests and links are retained. Record provider retention/deletion controls as known/unknown; do not assume attestation deletion is equivalent to deleting all copies. | FR-FW-034; acceptance criteria 4–6. |

## Frozen probe method and safety

1. Independently review this plan and temporary-workflow design before execution.
2. Pin every external action by immutable commit SHA. For the initial GitHub-hosted candidate probe, use `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` and `actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6`; these are probe pins only, not provider selection or adoption. Add no other third-party actions unless their exact immutable SHAs are recorded in this plan before execution. Record the hosted runner image and `gh` version observed during the run. Use a toy receipt with no app/user data and a synthetic required-check manifest. The workflow may read exact hosted check records only with temporary read permission and must not execute code from an untrusted pull request.
3. Keep `contents: read` for checkout; grant `checks: read` only if needed to query required checks. The signing job alone may receive `id-token: write`, `attestations: write`, and `artifact-metadata: write`. Do not request repository administration, deployment, package, or secret access.
4. Capture only bounded outputs: exact source/action/workflow SHA, provider run/check identities, receipt and bundle digests, trust-root source/date/digest, verifier command/result, diagnostic codes, permissions, duration, and known retention/rotation limits. Never upload environment dumps, ID tokens, secrets, source trees, or full logs.
5. Verify with locally supplied receipt, bundle, root and policy inputs outside the signing workflow. Test tampered inputs. Describe this as offline verification capability only; do not claim the host had network access denied.
6. Delete the temporary workflow and fixture files, preserve the bounded result record, and run the existing Verify Pipeline on the final evidence commit. Re-review the exact final evidence and update dependent task states.

## G-FEAS pass boundary

G-FEAS may pass only if at least one candidate can produce and independently verify a receipt bound to the exact source, required-check manifest, trusted workflow identity, provider check evidence and artifact digests; negative substitution/tamper cases fail; and privacy/permission limits are bounded. If no candidate meets those conditions, record the blocker and stop. A pass establishes feasibility only for the observed repository visibility, GitHub-hosted runner, candidate pins and trust-root snapshot. It does not choose a provider/key strategy, establish root freshness or revocation, prove repository branch protection, prove test adequacy or authorize production adoption.

## Status

Plan prepared 2026-10-24 after G-REQ PASS. No signing probe has run. Independent review of the exact plan and temporary workflow remains required before execution.
