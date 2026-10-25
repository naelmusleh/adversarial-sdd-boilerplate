---
id: FRAMEWORK-OPERATIONS-001
type: framework-operations-guide
title: FW-TASK-029 receipt retrieval and operator handling
status: draft
version: 1.0
created: 2026-10-25
updated: 2026-10-25
related-artifacts: FRAMEWORK-ARCHITECTURE-003, FRAMEWORK-IMPL-003, FRAMEWORK-CX-002, FRAMEWORK-BACKLOG-001, DECISION-027, DECISION-030, DECISION-031, DECISION-032
---

# FW029-IMPL-04 — Receipt retrieval and operator handling

This guide covers the bounded GitHub Actions/Sigstore pilot in this repository. A receipt verification result establishes only that the supplied receipt bytes and provenance match the supplied policy and trust-root snapshot under the verifier's checks. It is evidence for a reviewer to consider; it is not a lifecycle-gate result, branch-protection observation, merge decision, or release authorization.

## Before retrieval

Record the repository, source commit, ref, Verify Pipeline run ID and attempt, workflow path, required-check manifest revision, and artifact expiry shown by GitHub. Confirm that the run and each required check refer to the same source commit and that the checks succeeded. Do not substitute a rerun, a newer run, or a similarly named artifact. The pilot signing path is limited to the approved `workflow_dispatch` invocation on `refs/heads/codex/v2-backlog-roadmap`.

Download the `fw029-receipt-and-bundle-<run-id>-<attempt>` artifact from that exact run using an authenticated GitHub session. Keep the downloaded archive intact until its GitHub artifact identity, digest when exposed, name, run, and expiry have been recorded. Extract it into a newly created private local directory with access limited to the operator. Reject unexpected files, links, or paths; do not extract over an existing directory. The expected payload is the receipt and detached Sigstore bundle.

On macOS or Linux, a private temporary directory can be created with:

```sh
umask 077
workdir=$(mktemp -d "${TMPDIR:-/tmp}/fw029-verify.XXXXXX")
chmod 700 "$workdir"
```

Inspect the archive member list before extraction. Extract only the expected regular files beneath this new directory; reject absolute paths, `..` path components, symlinks, and unexpected entries. Keep the working directory private while verifying. If the machine or filesystem is shared or not approved for the repository's data classification, do not use it for this evidence.

The current pilot configures workflow artifact retention to one day. This is a configured pilot value, not a promise that GitHub will retain the artifact for a full day in every circumstance. The hosted attestation has separate provider lifecycle semantics that have not been established. If the artifact has expired or cannot be retrieved, stop and record it as unavailable. Do not recreate a receipt from logs or reuse a receipt from a different run. If a fresh exact-run receipt is needed, an authorized operator must initiate a new eligible run; the new run is distinct evidence and must be reviewed on its own.

## Prepare exact verification inputs

The verifier needs four files: receipt, detached bundle, policy, and a caller-supplied `trusted_root.jsonl` snapshot. It also needs the expected policy SHA-256 from a channel independent of the policy file and bundle. Use the policy and trust root selected for the exact repository, source ref, workflow and provider run. Obtain their expected digests through the approved channel for the bounded review. The repository's synthetic policy fixtures are test data and must not be substituted for a run-specific policy.

Check that the trust-root digest matches the root digest pinned in the policy. A matching digest proves byte identity with that pin; it does not prove that the root is current or that the pin source is trustworthy. If either expected digest is missing, arrives through the same untrusted source as the file, or does not match, stop and obtain the input through its owner. Do not refresh or replace a root during a verification attempt.

Before running the verifier, use a current GitHub CLI installation and record its version. Run from a trusted checkout containing the reviewed verifier revision. The verifier reads bounded inputs, snapshots the validated bytes for the local GitHub CLI verification, and does not intentionally update repository or provider state. Use the paths and independently obtained policy digest in the following invocation:

```sh
gh version
python3 scripts/fw029_verifier.py \
  --receipt /private/path/receipt.json \
  --bundle /private/path/attestation-bundle.jsonl \
  --policy /private/path/verification-policy.json \
  --policy-sha256 <independently-supplied-policy-sha256> \
  --trusted-root /private/path/trusted_root.jsonl
```

Keep the JSON output with the run identity and the four input digests. A zero exit status and `state: passed` mean only that the bounded verification succeeded against those exact supplied bytes. A nonzero exit or any other state is a failed verification; retain the diagnostic and do not repair or edit signed inputs in place. Re-run only after an authorized source supplies corrected inputs or a distinct fresh run.

## Interpret limits and recover

Every result reports `freshness: unknown`, `revocation_status: not-established`, and `authorization: false`. These are substantive limits, not warnings an operator can clear. A passing result does not establish current branch protection, test adequacy, semantic correctness, a gate PASS, approval to merge, or approval to release. The verifier does not fetch current repository state. The pilot does not establish an application trust-root distribution or rotation process, durable evidence archive, secure-erasure method, provider-side deletion, or hosted-attestation retention period.

Use these recovery actions:

| Condition | Operator action |
| --- | --- |
| Artifact expired, missing, or download unavailable | Record the run and artifact as unavailable. If fresh evidence is needed, request or initiate a separately authorized eligible run and start again with its exact run ID/attempt. |
| Policy or trust-root pin absent or mismatched | Stop. Ask the owner of the policy/trust channel to provide the exact approved bytes and independently communicated digest. Do not guess, fetch an arbitrary root, or weaken the policy. |
| Verifier reports signature, identity, source, check-set, or evidence-digest mismatch | Preserve the bounded diagnostic and inputs for review in the approved restricted location. Treat the evidence as rejected; investigate the source run or workflow and produce a new exact-run evidence set if authorized. |
| Local GitHub CLI is missing, outdated, or cannot verify the local bundle | Stop and restore a supported current GitHub CLI through the machine's managed software process. Do not bypass signature verification or silently switch verification tools. |
| Sensitive or unexpected content is present | Stop further distribution. Restrict access and follow the repository's incident/data-handling process; do not upload the material to an issue, chat, or public artifact. |
| A lifecycle gate or release decision is pending | Send the verification result, exact source/run identity, check evidence, limits, and applicable gate criteria to the authorized gate owner. The owner records the gate decision separately. Release authorization follows its own approved gate. |

## Local handling and privacy

Treat the receipt, bundle, policy, root snapshot, digests, and verifier output as integrity-sensitive project evidence. Store them only in an access-controlled location approved for the repository's classification. Avoid shared folders, public issue attachments, broad chat uploads, source control, and unnecessary duplicate copies. Do not place credentials, raw logs, source contents, or unrelated user data in these files. The receipt is designed to carry bounded metadata, but repository names, refs, commit IDs, workflow/check names and signer identity can still reveal private project activity.

This guide does not select a local storage provider, define a retention period, or guarantee deletion. For temporary review with no approved archive, remove the private working directory after the review record is stored in its approved location. This is ordinary file removal, not secure erasure; local snapshots, backups, or filesystem recovery may retain copies. For retained evidence, follow the owner-approved retention period and the storage system's documented deletion process, and record the outcome. Do not claim secure erasure or provider-side deletion without evidence. Until a storage owner and retention target are approved, this pilot supports temporary local review only, not durable audit retention.

## Review record

For each use, record the exact verifier revision, run ID/attempt, source SHA/ref, policy and trust-root digests, receipt digest, CLI version, result state, diagnostics, operator, review date, and the separate gate/release decision or its pending owner. Do not copy a `passed` result into a gate record as PASS without the gate owner reviewing all required evidence against that gate's contract.

The pilot's configured one-day artifact expiry and one observed retrieval do not establish a service-level retention guarantee. Trust freshness, revocation status, long-term availability, policy/root distribution and rotation, secure erasure, gate approval and release authorization remain unproven or out of scope.
