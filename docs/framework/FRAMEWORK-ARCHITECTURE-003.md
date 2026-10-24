---
id: FRAMEWORK-ARCHITECTURE-003
type: framework-architecture
title: FW-TASK-029 signed CI evidence receipt architecture
status: draft
version: 0.6
created: 2026-10-24
updated: 2026-10-24
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, DECISION-027, DECISION-028, FRAMEWORK-FEASIBILITY-010, FRAMEWORK-COVERAGE-002, FRAMEWORK-CX-002, FRAMEWORK-ADV-027, FRAMEWORK-ADV-028, FRAMEWORK-ADV-031, FRAMEWORK-ADV-032, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-ARCHITECTURE-003 — FW-TASK-029 signed CI evidence receipt architecture

## Gate work record

- **Gate:** G-ARCH — PASS within the approved FW-TASK-029 / FR-FW-032–034 scope, confirmed by exact-revision CI and independent review.
- **Task and requirements:** FW-TASK-029, FR-FW-032–034, under DECISION-027 and the bounded G-ARCH authorization DECISION-028.
- **Accepted inputs:** G-REQ PASS for FRAMEWORK-SPEC-001/DECISION-027; bounded G-FEAS PASS in FRAMEWORK-FEASIBILITY-010; G-COVERAGE PASS in FRAMEWORK-COVERAGE-002; G-CX PASS in FRAMEWORK-CX-002 and FRAMEWORK-ADV-031.
- **Architecture scope:** Receipt and verification data boundaries, hosted signing workflow boundary, local verification flow, privacy/retention, operational failures, candidate contracts and fixtures, owner decisions, and task-ready implementation decomposition.
- **Exclusions:** No signing provider/key mechanism is selected or adopted. No production trust-root or policy-digest source, trust freshness/revocation window, artifact retention guarantee, or one-use/replay authorization rule is decided. No production credential, application adoption, framework CI-policy change, FW-TASK-020 replacement, or implementation is authorized.
- **Review/verification plan:** Validate document/artifact links and JSON syntax, have the independent reviewer inspect schema/fixture conformance and the requirement-to-case map, run `git diff --check`, run exact-revision Verify Pipeline, then request independent GARCH-01–03 review. The local artifact-validation command was not run in this chat per the repository's execution instruction; the exact-revision Verify Pipeline runs it. Machine-readable schemas define shape only; identity equality, signature validity, policy pinning and provider claims require semantic verification at G-IMPL.

## Architecture summary

The candidate flow has four trust-separated stages: (1) a hosted workflow selects one exact completed source run and gathers the configured required-check records; (2) a preparation job builds a small deterministic receipt containing bounded identifiers, conclusions, links and digests; (3) a separate hosted identity signs the receipt bytes and emits a detached attestation bundle; and (4) a standalone verifier checks that bundle against a caller-supplied trust snapshot and an explicitly pinned verification policy. A successful signature verifies issuer and signed-byte integrity under the supplied trust inputs. It does not approve a lifecycle gate, prove test quality, or authorize release.

GitHub Actions and its attestation service are the only observed hosted candidate in FRAMEWORK-FEASIBILITY-010. The disposable probe separated receipt preparation from an OIDC-backed signing job, used read-only metadata permissions for preparation, and retained the synthetic receipt artifact for one day. This is feasibility evidence, not provider selection, production adoption or a guarantee about the hosted attestation's retention. No other provider is claimed as supported.

The verification policy and its expected SHA-256 must be supplied through a channel independent of the policy file being verified. The policy binds the expected repository, exact source SHA/ref, provider/run/attempt/event/ref, workflow identity/revision, gate-contract revision, required-check manifest digest, required check set, issuer identity and trust-root digest. Because source and run identity vary, the expected policy digest is per verification scope and must still arrive through an independent trusted channel. The verifier fails closed when any required input is absent or any supplied value differs. An externally supplied trust-root snapshot permits repeatable offline verification only against that snapshot; it does not establish that the snapshot is current or unrevoked.

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
- `fixtures/semantic-cases.json` records cross-record, trust, size and repeatability outcomes that JSON Schema cannot prove. Implementation must turn each case into a deterministic verifier assertion with the named diagnostic.
- V1 proposes at most 100 checks and 100 evidence references per receipt, at most 100 required checks per policy, 262,144 serialized UTF-8 bytes per receipt, and 65,536 bytes per policy. These are conservative contract ceilings for compact metadata, not targets or a claim about provider limits. The byte ceilings require an explicit pre-parse implementation check; exceeding any ceiling fails with the mapped diagnostic. An app needing a higher ceiling must revise the versioned contract before implementation rather than silently override it.

Canonical JSON serialization is UTF-8, sorted by key, with no insignificant whitespace and duplicate object keys rejected. Sign the exact canonical receipt bytes. The verifier must check the signature over those bytes before trusting receipt claims, then compare all receipt identities/checks to the separately pinned policy and supplied provider evidence. JSON Schema validates shape, not canonicalization, signer identity or equality across records.

### Required semantic invariants

1. Repository ID/host, source SHA/ref, workflow identity/revision, contract ID/revision/digest, provider run/attempt/event/ref, and required-check-manifest digest match the pinned per-run policy. Each required check head SHA must match the policy-pinned source SHA.
2. The receipt check set is exactly the policy's required logical-check set: no missing, duplicate, extra or substituted check; each provider result identifies the same repository and source SHA and has the configured success conclusion.
3. Every evidence digest is computed from the exact retained bytes. A digest without retrievable evidence is a provenance reference only; it does not prove that the bytes were tested.
4. Issuer identity is verified from the supplied trust root and checked against the pinned expected workflow identity. A repository/workflow string inside the receipt is not identity proof.
5. A policy byte or trust-root byte change fails its external digest comparison. The expected policy digest and expected root digest cannot be sourced from the same untrusted bundle alone.
6. Reverification is repeatable and read-only. This v1 receipt is provenance evidence and cannot authorize an action, so the approved scope defines no prohibited replay and no replay-prevention mechanism. This maps FR-FW-033's conditional “disallowed replay” negative case: the verifier accepts a repeated read-only check under `read-only-repeatable`; it rejects an unsupported one-use/replay policy as unsupported. If a future consumer makes a receipt an authorization token or forbids repeated verification, that consumer needs a separate owner-approved policy and test contract. Snapshot verification also establishes neither freshness nor revocation.
7. Attempt results use the CX-002 vocabulary. Missing required local input is `blocked`; an unavailable external provider/tool is `unavailable`; an executed cryptographic or policy mismatch is `failed`; an already-produced result bound to superseded selected inputs is `stale`. Reviewer disposition and owner authorization remain separate.

Structural schemas and synthetic valid/invalid fixtures are present. Cross-record semantic cases are listed but are not executable until G-IMPL. No claim is made that a schema alone verifies any cryptographic or provider fact.

## Integration, recovery and operations

| Failure | Attempt result | Recovery |
| --- | --- | --- |
| Receipt, bundle, policy, expected digest or trust root not supplied locally | `blocked` | Obtain the named input through its authorized channel; do not use a receipt-supplied default. |
| Provider API, verifier dependency or artifact cannot be obtained | `unavailable` | Restore access or retrieve the bounded artifact; do not downgrade to an unsigned/local PASS. |
| Multiple matching runs, incorrect SHA/ref/workflow, missing/duplicate/failed required check | `failed` | Correct workflow/policy configuration and create a new source-bound run/receipt. Preserve the failed result. |
| Receipt signature, policy digest or root digest mismatch | `failed` | Obtain original bytes and current owner-controlled policy/trust material; never rewrite the receipt. |
| Receipt/policy exceeds the v1 byte or array ceiling | `failed` | Reduce the bounded metadata set or revise the versioned contract through review; never truncate signed or policy bytes silently. |
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

**Options:** snapshot verification with explicit “freshness unknown”; bounded-age policy; or online revalidation against current provider state. For replay, the relevant options are repeatable provenance verification versus a separately defined action-authorization token with consumption/nonce state. **Evidence:** the positive offline check was repeated read-only against a supplied trust-root snapshot; trust freshness/revocation and hosted attestation retention remain unverified. **Bounded interpretation of FR-FW-033:** its negative case applies to a policy that actually prohibits replay. The only v1 mode is `read-only-repeatable`; verifying the same receipt again is allowed and cannot authorize an action. A policy requesting one-use or replay prevention is unsupported and fails closed. Thus no prohibited replay exists in the approved receipt-verification scope and no replay mechanism is selected. **Authority:** an owner must approve a separate contract before any consumer uses a receipt as an authorization token or prohibits repeated verification. **Impact:** no authorization or freshness claim is supported here; such consumers remain blocked pending that decision and review.

### ADR-FW029-ARCH-04 — Treat retention as split across artifact and attestation stores

**Options:** rely on short-lived hosted artifacts and rerun on expiry; require an owner-managed archive with explicit access/retention controls; or select a provider with a reviewed retention/deletion contract. **Evidence:** synthetic artifact retention was configured for one day; hosted-attestation deletion/retention semantics were unknown. **Decision:** no retention guarantee or provider lifecycle is selected. **Authority:** owner must set a retention target and select its storage/control owner before any use that requires durable audit or deletion guarantees. **Impact:** present evidence supports acquisition and local verification while available, not long-term availability or complete deletion.

### ADR-FW029-ARCH-05 — Bound v1 receipt and policy inputs

**Options:** leave input size to runtime defaults; bind count/byte limits in the versioned contract; or derive ceilings from a versioned required-check manifest and separately configured evidence quota. **Evidence:** feasibility exercised a small three-check workflow and a metadata-only receipt; it did not measure large manifests. **Proposed v1 ceilings:** 100 required/check entries, 100 evidence references, 262,144 serialized receipt bytes and 65,536 serialized policy bytes. The array ceilings align the policy and receipt and exceed the observed workflow size; byte caps bound parser and storage work. They are contract limits, not measured provider guarantees. **Authority:** these ceilings are proposed for owner review at G-ARCH acceptance; any app that cannot fit must not override them locally and requires a versioned contract revision. **Impact:** implementation must reject over-limit bytes before parsing and over-limit arrays during schema validation, with deterministic diagnostics; no truncation is allowed.

## Task-ready implementation decomposition (not authorized)

| Proposed unit | Scope and acceptance evidence | Dependencies / blocking owner choices |
| --- | --- | --- |
| FW029-IMPL-01 — Strict receipt and policy contracts | Implement schema/semantic validation, canonical serialization, duplicate-key rejection, pre-parse byte ceilings, array ceilings and precise diagnostics. Map every acceptance invariant below to a positive/negative assertion. | G-ARCH PASS and separate G-IMPL authorization. Provider-neutral core; no provider selection required for pure parser fixtures. |
| FW029-IMPL-02 — Hosted receipt and signing adapter | Resolve one exact provider run/attempt; verify required checks and source identity; emit deterministic receipt and detached signed bundle; keep metadata and signing jobs separated; no secrets in test code; pin actions/workflow identity. | G-ARCH PASS, G-IMPL authorization, and owner selection of provider/signer. Do not run signing from untrusted PR-controlled workflow code. |
| FW029-IMPL-03 — Standalone verifier | Verify signed bytes, issuer against supplied root, external policy/root digests, exact receipt/provider/check identity and evidence digests; repeat read-only; fail closed; produce bounded output. | G-ARCH PASS, G-IMPL authorization, and owner-approved trust-input distribution. Snapshot-only output must state freshness limits. |
| FW029-IMPL-04 — Operator handling and evidence claims | Document retrieval, offline verification, expiry/unavailability, secure local retention, privacy limits, recovery and separate gate/release decisions; privacy review plus independent adversarial provenance review. | G-ARCH PASS, G-IMPL authorization, and retention/operations decision for any durability promise. |

### Requirement-to-semantic-case handoff

| Requirement / acceptance invariant | Cases and expected assertion | Planned unit |
| --- | --- | --- |
| FR-FW-032: versioned payload binds source/repository/workflow/contract/run/manifest/check/evidence/issuer identities | SEM-01, 02, 04, 12–21, and 29–31 reject mismatch, ambiguity, missing/duplicate checks, signature changes, evidence changes, top-level source-ref mismatch, provider mismatch, and run-ID mismatch with the named diagnostic. The policy schema carries the exact per-run source and provider-run identity. Positive shape is `receipt.valid.synthetic.json`; missing source is rejected by its schema fixture. | FW029-IMPL-01; provider cross-checks also FW029-IMPL-02. |
| FR-FW-033: signature, issuer and external trust inputs are checked fail-closed | SEM-05–09 and SEM-12/27 reject missing/mismatched policy/root pins, untrusted issuer/signature, and unsigned-receipt promotion. | FW029-IMPL-01 / 03. |
| FR-FW-033: exact required check set, successful conclusions, identity and source | SEM-03–04, 17–20, and 28 reject unavailable, ambiguous, missing, duplicate, extra, failed, substituted, or wrong-source check results. The pinned per-run policy binds source SHA/ref and provider run/attempt/event/ref. | FW029-IMPL-01 / 02 / 03. |
| FR-FW-033: stale scope and conditional replay semantics | SEM-10 returns stale for superseded scope; SEM-22 rejects unsupported one-use/replay policy; SEM-23 confirms repeated read-only verification passes. No action authorization or consumption is implemented. | FW029-IMPL-01 / 03; any future action-token behavior needs a separate owner-approved scope. |
| FR-FW-033: supplied evidence digest and bounded inputs | SEM-21 rejects evidence-byte mismatch; SEM-24–26 reject byte/array ceilings before acceptance. | FW029-IMPL-01 / 03. |
| FR-FW-034: privacy-minimized receipt and strict claims | Schema excludes unbounded free-form fields and raw source/log fields; SEM-11 labels freshness unknown. Privacy/content review and no-production-claim review are required for FW029-IMPL-04. | FW029-IMPL-01 / 04. |

Semantic cases are a frozen implementation handoff, not execution evidence. G-IMPL must execute every listed case and compare the actual diagnostic/status with the expected value. If a requirement/acceptance criterion changes, the map and case IDs must be reviewed with the contract.

No unit is a product backlog commitment until G-ARCH is accepted and the owner separately authorizes a G-IMPL scope. FW-TASK-020 remains independent and its app-hosted run cannot be replaced.

## G-ARCH acceptance mapping and evidence status

| Criterion | Evidence in this artifact | Status before independent review |
| --- | --- | --- |
| GARCH-01 — Boundaries, identities, data, integration/failure, security/privacy, deployment/operations/recovery | System context and trust-boundary table; lifecycle, retention, failure and recovery contracts; snapshot freshness limits. | PASS on final review revision `8326b77b10486e4140e9785cd44fcf31b78829e9`. |
| GARCH-02 — Material ADRs, authority, alternatives, constraints, linked task scope and checks | Five ADRs state options, evidence, decision authority and downstream blockers; four proposed implementation units map to FR-FW-032–034. | PASS; ADR-05 size ceilings require owner acceptance or revision before G-IMPL. |
| GARCH-03 — Structural contracts, invariant checks and frozen handoff | Versioned JSON Schemas, synthetic valid/invalid fixtures, bounded input ceilings, requirement-to-semantic-case matrix and frozen semantic case IDs. | PASS: SEM-30/31 cover provider and run-ID mismatch against pinned policy, and FR-FW-032 maps both. |

G-ARCH passes within the approved FW-TASK-029 scope. ARCH029-04/05 were resolved in the prior review cycle and ARCH029-06 is resolved by SEM-30/31. Exact-revision Verify Pipeline [40137156642](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40137156642) passed all three required jobs, and the independent reviewer passed GARCH-01–03 at source commit `8326b77b10486e4140e9785cd44fcf31b78829e9`. ADR-05 size ceilings remain proposed and require owner acceptance or revision before G-IMPL. No G-IMPL, provider adoption, production trust decisions or release is authorized.

## Independent G-ARCH review history

- **Round 1 — NEEDS-CHANGES:** Reviewer `/root/fw029_independent_review` reviewed commit `805251ca5dfaea729997c7cdeb6f3c2533e991e5` (architecture blob `6f076fd05618f88c790aab86ae792916a6eace7c`). Findings ARCH029-01 (replay condition not reconciled), ARCH029-02 (acceptance criteria lacked semantic case mapping), and ARCH029-03 (input arrays/bytes unbounded) were recorded. The reviewer found no separate owner decision required to map repeatable read-only verification; any future action authorization remains a separate owner-approved scope.
- **Round 2 — NEEDS-CHANGES:** Reviewer `/root/fw029_independent_review` reviewed commit `a37ea6989d7090a4cf897ed82f87934cac8d2b4c` (architecture blob `cefd5b503d1d268f233696896d9d78edd142e895`). GARCH-01 and GARCH-02 passed; GARCH-03 remained blocked by ARCH029-04 (the invalid policy fixture also omitted newly required `source` and `provider_run`, so it did not isolate the trust-root failure) and ARCH029-05 (no explicit negatives for unsigned-receipt promotion, an extra check, or top-level `source.ref` mismatch). Review report: [FRAMEWORK-ADV-032](../adversarial-reviews/FRAMEWORK-ADV-032.md). The owner authorized one final bounded correction and full-scope re-review; a subsequent checkpoint explicitly authorized a new cycle limited to ARCH029-06.

- **Round 3 — NEEDS-CHANGES:** Reviewer `/root/fw029_independent_review` reviewed source commit `8402aae63965ccab19e5ef8ed070a2af140e49a9`, architecture blob `d527290cf7e374eaaa01c1f47c5203a414507999`, semantic-case blob `62d47e34a12e8a794136501bede26431abcb445b`, and isolated missing-trust-root fixture blob `f1f0906287cacd256ad2028069480c53de72547b`. GARCH-01 passed; GARCH-02 passed subject to ADR-05 size-ceiling owner acceptance or revision before G-IMPL; GARCH-03 needs changes. ARCH029-04 and ARCH029-05 are resolved. **ARCH029-06 (Major):** semantic case FW029-SEM-16 covers run attempt/event/ref/URL mismatch but omits provider and run-ID mismatch, despite FR-FW-032 binding provider run identity. Add explicit deterministic mismatch coverage with `receipt.run_mismatch`. The reviewer stated no owner decision is needed for the content change; however, this final owner-authorized review cycle is consumed under the repository's review-loop limit, so another correction plus independent review requires a new owner checkpoint. Review report: [FRAMEWORK-ADV-032](../adversarial-reviews/FRAMEWORK-ADV-032.md). Verify Pipeline [40135758687](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40135758687) passed all three required checks on the exact reviewed source commit; the synthetic evidence probe job was skipped. G-IMPL remains unauthorized.

- **Round 4 — PASS:** Following the owner's bounded authorization, separate semantic cases FW029-SEM-30/31 cover provider and run-ID mismatch against the pinned policy and both expect `failed` / `receipt.run_mismatch`. Reviewer `/root/fw029_independent_review` passed GARCH-01–03 at exact source commit `8326b77b10486e4140e9785cd44fcf31b78829e9`. Verify Pipeline [40137156642](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40137156642) passed all three required jobs on that exact commit; the optional synthetic evidence probe was skipped. ARCH029-06 is resolved. No provider, trust, replay, retention, or implementation decision changed.
