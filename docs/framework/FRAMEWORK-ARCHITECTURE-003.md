---
id: FRAMEWORK-ARCHITECTURE-003
type: framework-architecture
title: FW-TASK-029 signed CI evidence receipt architecture
status: draft
version: 0.1
created: 2026-10-24
updated: 2026-10-24
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, DECISION-027, DECISION-028, FRAMEWORK-FEASIBILITY-010, FRAMEWORK-COVERAGE-002, FRAMEWORK-CX-002, FRAMEWORK-ADV-027, FRAMEWORK-ADV-028, FRAMEWORK-ADV-031, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-ARCHITECTURE-003 — FW-TASK-029 signed CI evidence receipt architecture

## Gate work record

- **Gate:** G-ARCH — in progress; no pass is asserted.
- **Task and requirements:** FW-TASK-029, FR-FW-032–034, under DECISION-027 and the bounded G-ARCH authorization DECISION-028.
- **Accepted inputs:** G-REQ PASS for FRAMEWORK-SPEC-001/DECISION-027; bounded G-FEAS PASS in FRAMEWORK-FEASIBILITY-010; G-COVERAGE PASS in FRAMEWORK-COVERAGE-002; G-CX PASS in FRAMEWORK-CX-002 and FRAMEWORK-ADV-031.
- **Architecture scope:** Receipt and verification data boundaries, hosted signing workflow boundary, local verification flow, privacy/retention, operational failures, candidate contracts and fixtures, owner decisions, and task-ready implementation decomposition.
- **Exclusions:** No signing provider/key mechanism is selected or adopted. No production trust-root or policy-digest source, trust freshness/revocation window, artifact retention guarantee, or one-use/replay authorization rule is decided. No production credential, application adoption, framework CI-policy change, FW-TASK-020 replacement, or implementation is authorized.
- **Review/verification plan:** Validate document/artifact links, JSON syntax, schemas and fixtures structurally, run `python3 scripts/artifacts.py validate` and `git diff --check`, run exact-revision Verify Pipeline, then request independent GARCH-01–03 review. Machine-readable schemas define shape only; identity equality, signature validity, policy pinning and provider claims require semantic verification at G-IMPL.

## Architecture summary

The candidate flow has four trust-separated stages: (1) a hosted workflow selects one exact completed source run and gathers the configured required-check records; (2) a preparation job builds a small deterministic receipt containing bounded identifiers, conclusions, links and digests; (3) a separate hosted identity signs the receipt bytes and emits a detached attestation bundle; and (4) a standalone verifier checks that bundle against a caller-supplied trust snapshot and an explicitly pinned verification policy. A successful signature verifies issuer and signed-byte integrity under the supplied trust inputs. It does not approve a lifecycle gate, prove test quality, or authorize release.

GitHub Actions and its attestation service are the only observed hosted candidate in FRAMEWORK-FEASIBILITY-010. The disposable probe separated receipt preparation from an OIDC-backed signing job, used read-only metadata permissions for preparation, and retained the synthetic receipt artifact for one day. This is feasibility evidence, not provider selection, production adoption or a guarantee about the hosted attestation's retention. No other provider is claimed as supported.

The verification policy and its expected SHA-256 must be supplied through a channel independent of the policy file being verified. The policy binds the expected repository, workflow identity/revision, gate-contract revision, required-check manifest digest, issuer identity and trust-root digest. The verifier fails closed when any required input is absent or any supplied value differs. An externally supplied trust-root snapshot permits repeatable offline verification only against that snapshot; it does not establish that the snapshot is current or unrevoked.

## System context and trust boundaries

| Component / actor | Data and authority | Boundary and failure behavior |
| --- | --- | --- |
| Source workflow and required checks | Exact repository ID, commit, ref, workflow/contract revision and check conclusions for one provider run/attempt | A green workflow reports only its observed checks. Code from an untrusted pull request is executable input. Signing permissions must not be exposed to test, build, package or pull-request-controlled steps. |
| Receipt preparation job | Read-only provider metadata and the versioned required-check manifest; emits canonical receipt bytes | Must identify exactly one run/attempt and compare repository, SHA, workflow, manifest and every required check. Missing provider response is unavailable; ambiguous or mismatched returned records fail. It receives no secrets and cannot sign. |
| Signing job | One exact receipt subject digest; ephemeral hosted workload identity | Separate job with only the permissions required for the selected signer. It must not check out or execute source code. It signs the prepared receipt bytes, not arbitrary source or logs. This permission model remains a candidate pending provider choice and security review. |
| Artifact/provider storage | Receipt, detached signature/attestation bundle and bounded provider URL | The tested receipt artifact retention was one day; hosted-attestation retention/deletion remains unknown. Expired provider links are unavailable evidence. An independently preserved valid bundle can still be verified against supplied trust material. No durability or deletion SLA is asserted. |
| Verification policy and trust-root supplier | Expected policy digest, policy bytes, trusted issuer constraints and trust-root snapshot/digest | Policy digest and trust root must arrive through an independently trusted channel. If the digest is stored beside the mutable policy without a separate anchor, it provides no protection against changing both. The production source/rotation process is an owner decision. |
| Local verifier / reviewer | Receipt, bundle, policy, expected policy digest, trust root and expected trust-root digest | Read-only and repeatable. It never consumes a receipt, silently downloads trust material, edits signed bytes, or converts its result to a gate decision. Missing local inputs block start; unavailable tools/provider records are unavailable; executed mismatches fail; old results are stale against a changed selected scope. |
| Gate/owner decision | Verified receipt and separate semantic/review evidence | A valid signature is one provenance input only. Gate acceptance, merge protection, semantic review and release authorization remain separate records and authorities. |

### Data minimization and retention

Receipt fields are limited to identifiers, exact revisions, workflow/run/check names and IDs, conclusions, bounded evidence references/digests, issuer identity and issue time. They exclude source text, diffs, personal data, credentials, environment values and unrestricted command logs. Diagnostic output is bounded and redacted. The test artifact's one-day retention is an observed setting; provider-attestation retention/deletion is unknown. A later implementation must tell the operator how to save the receipt and bundle before the test artifact expires and must not claim that deleting one artifact deletes the hosted attestation.

## Contract artifacts

The schemas and fixtures in `schemas/fw029/` are proposed v1 architecture contracts. The fixtures use synthetic identities and are not receipt evidence.

- `receipt-v1.schema.json` defines the deterministic signed payload's required fields and bounded shapes.
- `verification-policy-v1.schema.json` defines caller-selected expected repository, workflow, contract, manifest, issuer, check set and trust-root digest. Its bytes are pinned by a separately supplied expected SHA-256.
- `fixtures/receipt.valid.synthetic.json` and `fixtures/policy.valid.synthetic.json` illustrate shape only.
- `fixtures/receipt.missing-source.invalid.json` and `fixtures/policy.missing-trust-root.invalid.json` exercise required-field rejection.
- `fixtures/semantic-cases.json` records cross-record and trust outcomes that JSON Schema cannot prove. Implementation must turn each case into a deterministic verifier assertion with the named diagnostic.

Canonical JSON serialization is UTF-8, sorted by key, with no insignificant whitespace and duplicate object keys rejected. Sign the exact canonical receipt bytes. The verifier must check the signature over those bytes before trusting receipt claims, then compare all receipt identities/checks to the separately pinned policy and supplied provider evidence. JSON Schema validates shape, not canonicalization, signer identity or equality across records.

### Required semantic invariants

1. Repository ID/host, source SHA/ref, workflow identity/revision, contract ID/revision/digest, provider run/attempt/event/ref, and required-check-manifest digest match the pinned policy and observed provider record.
2. The receipt check set is exactly the policy's required logical-check set: no missing, duplicate, extra or substituted check; each provider result identifies the same repository and source SHA and has the configured success conclusion.
3. Every evidence digest is computed from the exact retained bytes. A digest without retrievable evidence is a provenance reference only; it does not prove that the bytes were tested.
4. Issuer identity is verified from the supplied trust root and checked against the pinned expected workflow identity. A repository/workflow string inside the receipt is not identity proof.
5. A policy byte or trust-root byte change fails its external digest comparison. The expected policy digest and expected root digest cannot be sourced from the same untrusted bundle alone.
6. Reverification is repeatable and read-only. It establishes neither freshness/revocation nor one-use authorization. A gate consumer that needs current provider state or age limits requires a separate reviewed decision and evidence path.
7. Attempt results use the CX-002 vocabulary. Missing required local input is `blocked`; an unavailable external provider/tool is `unavailable`; an executed cryptographic or policy mismatch is `failed`; an already-produced result bound to superseded selected inputs is `stale`. Reviewer disposition and owner authorization remain separate.

Structural schemas and synthetic valid/invalid fixtures are present. Cross-record semantic cases are listed but are not executable until G-IMPL. No claim is made that a schema alone verifies any cryptographic or provider fact.

## Integration, recovery and operations

| Failure | Attempt result | Recovery |
| --- | --- | --- |
| Receipt, bundle, policy, expected digest or trust root not supplied locally | `blocked` | Obtain the named input through its authorized channel; do not use a receipt-supplied default. |
| Provider API, verifier dependency or artifact cannot be obtained | `unavailable` | Restore access or retrieve the bounded artifact; do not downgrade to an unsigned/local PASS. |
| Multiple matching runs, incorrect SHA/ref/workflow, missing/duplicate/failed required check | `failed` | Correct workflow/policy configuration and create a new source-bound run/receipt. Preserve the failed result. |
| Receipt signature, policy digest or root digest mismatch | `failed` | Obtain original bytes and current owner-controlled policy/trust material; never rewrite the receipt. |
| Existing receipt or result is evaluated against a different selected contract/policy/source/trust revision | `stale` | Produce a new result bound to selected revisions. Keep the old result historical. |
| Hosted artifact expires while no local copy exists | `unavailable` | Rerun the relevant workflow or obtain a separately retained exact bundle; do not claim that an expired link proves invalidity. |
| Policy/root snapshot is valid but age/revocation state is unknown | `passed` only for verification against the supplied snapshot, with freshness explicitly unknown | For uses requiring current trust, stop and obtain an owner-approved freshness/revocation design. No “currently trusted” label is allowed. |

The verifier is not a production monitor or gate runner. It makes no network call in the bounded offline path. If an eventual verifier needs online provider state to satisfy an owner-approved freshness policy, that is a distinct mode with separately declared data, permissions, timeouts, failure outcomes and evidence. No automatic retry loop or mutating recovery is designed.

## ADRs and open owner decisions

### ADR-FW029-ARCH-01 — Preserve provider choice as an adapter decision

**Options:** adopt the tested GitHub Actions/attestation candidate for the first implementation; design a provider-neutral interface and defer adapters; or compare another provider before implementation. **Evidence:** FRAMEWORK-FEASIBILITY-010 demonstrates only the GitHub candidate and supplied trust-root snapshot. **Proposed boundary:** retain one explicit provider adapter contract and report unsupported providers honestly. The architecture does not adopt a provider. **Authority:** owner must select provider/key mechanism before a provider-specific implementation task is authorized. **Impact:** FW029-IMPL-02 remains conditional until that decision and a reviewed exact workflow identity are recorded.

### ADR-FW029-ARCH-02 — Require an independent trust anchor for policy and root bytes

**Options:** owner-supplied digest/root via an independent controlled channel; an organization-controlled protected setting or signed policy release; or a live trust-service refresh with pinned bootstrap/root rotation. A digest stored only alongside a mutable policy is insufficient. **Evidence:** the feasibility probe rejected policy/root mutations when supplied expected digests were pinned independently; it did not establish a production source. **Decision:** no production trust source is selected. **Authority:** owner must select and document the source, access/rotation owner, and recovery route before production use. **Impact:** FW029-IMPL-03 may test explicit caller-supplied trust inputs only; any product/gate integration requiring durable trust is blocked.

### ADR-FW029-ARCH-03 — Do not infer freshness, revocation or one-use behavior

**Options:** snapshot verification with explicit “freshness unknown”; bounded-age policy; or online revalidation against current provider state. **Evidence:** the positive offline check used a supplied trust-root snapshot; trust freshness/revocation and hosted attestation retention remain unverified. Verification was repeatable and read-only. **Proposed bounded behavior:** snapshot-only results say “verified against supplied trust snapshot,” not “currently trusted”; no receipt is consumed. **Authority:** owner must choose a stronger policy if a future consumer needs current authorization or replay prevention. **Impact:** production use that needs such a guarantee is blocked pending a separate reviewed contract. 

### ADR-FW029-ARCH-04 — Treat retention as split across artifact and attestation stores

**Options:** rely on short-lived hosted artifacts and rerun on expiry; require an owner-managed archive with explicit access/retention controls; or select a provider with a reviewed retention/deletion contract. **Evidence:** synthetic artifact retention was configured for one day; hosted-attestation deletion/retention semantics were unknown. **Decision:** no retention guarantee or provider lifecycle is selected. **Authority:** owner must set a retention target and select its storage/control owner before any use that requires durable audit or deletion guarantees. **Impact:** present evidence supports acquisition and local verification while available, not long-term availability or complete deletion.

## Task-ready implementation decomposition (not authorized)

| Proposed unit | Scope and acceptance evidence | Dependencies / blocking owner choices |
| --- | --- | --- |
| FW029-IMPL-01 — Strict receipt and policy contracts | Implement schema/semantic validation, canonical serialization, duplicate-key rejection and precise diagnostics. Add positive/negative tests for every shape and semantic case. | G-ARCH PASS and separate G-IMPL authorization. Provider-neutral core; no provider selection required for pure parser fixtures. |
| FW029-IMPL-02 — Hosted receipt and signing adapter | Resolve one exact provider run/attempt; verify required checks and source identity; emit deterministic receipt and detached signed bundle; keep metadata and signing jobs separated; no secrets in test code; pin actions/workflow identity. | G-ARCH PASS, G-IMPL authorization, and owner selection of provider/signer. Do not run signing from untrusted PR-controlled workflow code. |
| FW029-IMPL-03 — Standalone verifier | Verify signed bytes, issuer against supplied root, external policy/root digests, exact receipt/provider/check identity and evidence digests; repeat read-only; fail closed; produce bounded output. | G-ARCH PASS, G-IMPL authorization, and owner-approved trust-input distribution. Snapshot-only output must state freshness limits. |
| FW029-IMPL-04 — Operator handling and evidence claims | Document retrieval, offline verification, expiry/unavailability, secure local retention, privacy limits, recovery and separate gate/release decisions; privacy review plus independent adversarial provenance review. | G-ARCH PASS, G-IMPL authorization, and retention/operations decision for any durability promise. |

No unit is a product backlog commitment until G-ARCH is accepted and the owner separately authorizes a G-IMPL scope. FW-TASK-020 remains independent and its app-hosted run cannot be replaced.

## G-ARCH acceptance mapping and evidence status

| Criterion | Evidence in this artifact | Status before independent review |
| --- | --- | --- |
| GARCH-01 — Boundaries, identities, data, integration/failure, security/privacy, deployment/operations/recovery | System context and trust-boundary table; lifecycle, retention, failure and recovery contracts; snapshot freshness limits. | Prepared; reviewer to assess completeness and safe boundaries. |
| GARCH-02 — Material ADRs, authority, alternatives, constraints, linked task scope and checks | Four ADRs state options, evidence, decision authority and downstream blockers; four proposed implementation units map to FR-FW-032–034. | Prepared; provider/trust/retention choices deliberately remain owner-controlled. |
| GARCH-03 — Structural contracts, invariant checks and frozen handoff | Versioned JSON Schemas, synthetic valid/invalid fixtures and semantic case index; artifact validation; exact-revision CI and review evidence to be added. | Schema/fixture structures prepared; semantic verifier execution is correctly deferred to G-IMPL. |

The architecture remains draft until the exact revision passes Verify Pipeline and an independent reviewer passes GARCH-01–03. Unresolved owner decisions are visible conditions on dependent tasks, not implicit approval. G-IMPL, provider adoption, production trust decisions and release remain unauthorized.
