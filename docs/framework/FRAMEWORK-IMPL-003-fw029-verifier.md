---
id: FRAMEWORK-IMPL-003
type: framework-implementation-guide
title: FW-TASK-029 offline receipt verifier
status: draft
version: 1.0
created: 2026-10-25
updated: 2026-10-25
related-artifacts: FRAMEWORK-ARCHITECTURE-003, FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, DECISION-031
---

# FW029-IMPL-03 — Offline receipt verifier

`scripts/fw029_verifier.py` verifies the repository's bounded GitHub Actions / Sigstore receipt format. It requires four caller-provided inputs: the exact receipt bytes, detached attestation bundle, verification policy, and Sigstore `trusted_root.jsonl` snapshot. The expected policy SHA-256 is a separate caller argument; it must come from a channel independent of the policy file and bundle. The policy itself pins the root digest.

The verifier invokes the installed GitHub CLI with a local bundle and custom root, then checks the exact receipt subject digest, SLSA predicate, signer workflow, OIDC issuer, repository ID, source revision/ref, workflow identity and run invocation. For v1 it supports exactly one evidence item, `github-check-set`; its bytes are reconstructed using the canonical serialization of the receipt's check records and compared with the declared digest. Other evidence IDs fail closed.

Example invocation (replace paths and the digest with reviewed values):

```sh
python3 scripts/fw029_verifier.py \
  --receipt receipt.json \
  --bundle attestation-bundle.jsonl \
  --policy verification-policy.json \
  --policy-sha256 <independently-supplied-64-character-policy-digest> \
  --trusted-root trusted_root.jsonl
```

The command is read-only and emits one bounded JSON result. A `passed` result means the receipt and provenance verify against the exact caller-supplied policy and root snapshot. It always reports `freshness: unknown`, `revocation_status: not-established`, and `authorization: false`. It does not fetch current repository state, prove branch protection, establish test quality, pass a lifecycle gate, or authorize merge/release. GitHub CLI local-bundle verification binds certificate repository names as they were at signing; the verifier additionally checks the signed certificate's repository ID but does not establish whether GitHub has since renamed or reassigned the repository. See the [GitHub CLI verification documentation](https://cli.github.com/manual/gh_attestation_verify).

The root snapshot is caller-supplied trust material. A passing snapshot check does not mean it is current. Production trust distribution, root rotation, freshness/revocation policy, retention and operator recovery remain outside this implementation unit.
