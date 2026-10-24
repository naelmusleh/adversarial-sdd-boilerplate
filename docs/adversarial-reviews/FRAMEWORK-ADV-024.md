---
id: FRAMEWORK-ADV-024
type: adversarial-review
title: FW-TASK-029 requirements scope review
status: in-review
version: 1.0
created: 2026-10-24
updated: 2026-10-24
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, DECISION-027, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-ADV-024 — FW-TASK-029 requirements scope review

## Review scope and evidence

Reviewer: `/root/infinite_gallery_reviewer`, separately assigned and read-only. Scope: FW-TASK-029 G-REQ and FR-FW-032–034, including receipt-to-policy binding, trust boundaries, offline verification, privacy, claim limits, and consistency with DECISION-019 and FW-TASK-020.

Initial frozen revision reviewed: `8835e5f9bc7b5cfe02b32b98214ee21e1088ae74`.

## Review round 1

**Verdict: BLOCK.** Scope and privacy boundaries were adequate, and deferring provider/key-mechanism selection to G-FEAS/G-ARCH was appropriate. The reviewer identified one major requirement gap:

### FINDING-001 — Major: exact manifest and trusted workflow identity not bound

FR-FW-032 listed individual check identities and workflow revisions, but did not require the receipt to bind the exact approved required-check manifest digest and trusted workflow identity. AC-1's phrase “declared policy” did not say which policy bytes or workflow identity must be checked. A receipt could therefore attest to an arbitrary list of checks without showing that it came from the policy required by DECISION-019.

**Required correction:** Add the exact required-check manifest digest and trusted workflow identity to the receipt contract, and require the offline verifier to validate both against configured policy. Do not select a provider or signing mechanism as part of this correction.

## Corrective review

The requirements and AC-1 were amended to include the manifest digest and trusted workflow identity. Exact corrected revision and Verify Pipeline result will be recorded after publication. Independent re-review is pending; G-REQ remains blocked until the finding is resolved at the exact reviewed revision.
