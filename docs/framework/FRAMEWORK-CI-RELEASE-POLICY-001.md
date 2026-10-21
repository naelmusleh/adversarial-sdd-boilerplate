---
id: FRAMEWORK-CI-RELEASE-POLICY-001
type: framework-operating-policy
title: App check, CI provenance, and release evidence policy
status: draft
version: 1.0
created: 2026-10-20
updated: 2026-10-20
related-artifacts: FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-ADV-011
---

# FRAMEWORK-CI-RELEASE-POLICY-001 — app checks and release evidence

## Authority and limits

This policy governs the generated app workflow and the framework Verify Pipeline. It supplements the approved gate contract v1.0 and does not enable the draft v1.1 amendment. An app workflow can run checks and retain provenance, but only hosting-provider repository settings can require those checks before merge. The framework owner or app owner must record repository protection as `observed` with provider evidence or `unverified`; workflow YAML is never proof of protection.

## App-owned required-check manifest

New app initializations use framework lock version 3 and receive:

- `.sdd/required-checks.json`: app-owned, editable policy data. It begins `unconfigured` with no checks; this is honest for an ideation-stage app and cannot support a passing G-IMPL gate.
- `.sdd/schemas/required-checks-v1.schema.json`: framework schema copied and digest-locked.
- `.sdd/required-checks.json.template`: starter example copied and digest-locked.
- `scripts/ci_checks.py`: digest-locked runner for required CI checks.

An active check entry names a stable `check_id`, `task_ids`, task acceptance criteria, platforms, source paths, execution mode (`ci` or `manual`), exact command/procedure, pass condition, and evidence location. CI entries require a runtime-probe command; its observed output is recorded. The generated runner currently executes shell checks on GitHub's Ubuntu runner, so checks that need another platform require a separately recorded workflow/procedure rather than an assumed cross-platform result. A required check tied to a task must appear in that task's G-IMPL evidence. The gate validator compares check ID, command, scope, and pass condition to the app manifest. It does not yet resolve each manifest task/criterion against the canonical backlog/specification or prove semantic completeness of that mapping; reviewers must verify those references. Manual checks remain owner/reviewer evidence and are not silently treated as CI passes.

All required CI entries run on each push and pull request. The runner executes only from a clean checkout, stops if a command changes tracked or untracked non-ignored checkout state, terminates the command process group on timeout, uses a 10-minute per-command timeout, records stdout/stderr digests and exit codes outside the checkout, and fails if any required command or runtime probe fails. Ignored workspace mutations are not detected. Because check commands run from repository-controlled configuration in a writable hosted workspace, the runner cannot prove a malicious command did not transiently alter source and then restore it before the post-check inspection; this is a provenance limitation, not proof that the check evaluated unmodified bytes. Stronger assurance requires an immutable/read-only execution sandbox. Unconfigured apps produce an explicit empty report; a green empty run does not satisfy a later G-IMPL gate. Scope paths and evidence locations must be relative and cannot traverse outside the repository.

## CI provenance record

Each workflow attempt records provider/repository, workflow identity and revision, job, run ID and attempt URL, event and ref, pull-request head/base SHA when applicable, exact checked-out SHA, runner OS/architecture and available runner-image metadata, manifest digest, check commands and runtime observations, task/criterion/platform/path scope, pass condition, individual outcomes, and output digests. The runner compares checked-out `HEAD` with the provider event SHA; a mismatch fails. On pull requests, the tested SHA is the provider's merge ref commit, while the report separately records the PR head and base SHAs. Gate evidence for GitHub Actions must retain the exact attempt URL, including `/attempts/<attempt>`; a base run URL without the attempt is not accepted.

The generated workflow uploads the evidence report and outputs as a run-attempt artifact, including after a required check fails where artifact storage remains available. The standard retention is 90 days; gate records must copy/link the required durable evidence into the app's approved evidence store before relying on it beyond that retention. A failed, cancelled, skipped, missing, or SHA-mismatched required check is non-pass. A GitHub run URL includes the run attempt and must be linked with the exact tested SHA.

The evidence report is a provenance and output-integrity record, not a cryptographic attestation or proof that a command's claims are semantically true. Tests and scripts can print misleading output. Code review and independent gate review remain required. The hosted runner has outbound network access; read-only repository permissions and no injected secrets reduce impact but do not prevent malicious pull-request code from disclosing checked-out source or causing external side effects. Repository owners must account for that provider constraint when enabling this workflow on private repositories; the generated template does not claim network isolation.

## Workflow security boundary

- Generated workflows have `contents: read`; checkout credentials are not persisted. They do not deploy, publish releases, change repository settings, or receive app secrets.
- Pull-request code and its manifest commands are untrusted executable input. They run without privileged secrets. Do not add deployment credentials or trusted release tokens to these jobs.
- The runner filters environment variable names that indicate tokens, secrets, passwords, credentials, and private keys before invoking manifest commands. The workflow itself does not inject secrets; logs and evidence must still be reviewed for accidental sensitive output.
- Provider approval requirements and event suppression must be handled explicitly. A missing or approval-pending follow-on run is `pending`/`unverified`, never a pass. Do not use a privileged `pull_request_target` workaround to run untrusted code with secrets.
- The framework Verify Pipeline uses read-only repository permissions and no deployment credentials. It runs for feature-branch pushes and pull requests as well as manual dispatch. The required check set remains a repository-settings decision.

## Commit, push, merge, and release are separate states

For each change, record the local commit SHA and explicit staged scope, authorized branch/ref, remote push outcome, exact CI run attempt and result, review/merge outcome, release artifact digest, target environment, owner authorization, and deployment outcome as separate facts. A local commit is not a push; a push is not CI success; CI success is not a merge; merge is not release or deployment. A passing G-IMPL/G-RELEASE publication checkpoint requires `change_control.authorization_ref` to resolve to an owner decision in the same gate record, made by its accountable owner, with an explicit commit/push/publication/release authorization choice and at least one affected in-scope task. G-IMPL's decision choice must use `authorize-commit`, `authorize-push`, or `authorize-publish` followed by exact `commit_sha`, `branch_ref`, and `remote` key/value fields; G-RELEASE's publication authorization reference must be the same decision as its artifact/environment release approval. Missing remote, credentials, owner authorization, or required checks is a blocker. Never force-push, bypass protections, or claim a state that was not observed.

G-RELEASE links the artifact-reference evidence whose current bytes match the recorded digest, the tested source SHA, successful exact-SHA CI evidence, the accountable owner's authorization for that digest/environment/release window, support ownership, and rollback/recovery plan. A digest binds bytes, not publisher identity or build provenance by itself. The rehearsal must show that changed bytes, SHA, environment, window, or owner authorization invalidate the release decision.

## Bounded G-RELEASE control rehearsal

Exercise these cases with synthetic data and no production credentials or deployment:

| Case | Required disposition |
|---|---|
| Required checks pass on the exact tested revision; artifact digest and owner authorization match. | Eligible for a non-production readiness PASS only if all other G-RELEASE criteria and authority evidence pass. |
| Required command fails or the provider run is cancelled/skipped. | Block; preserve failure evidence; no release PASS. |
| Evidence names a stale/mismatched source SHA or workflow attempt. | Reject as stale; rerun on the exact candidate. |
| Artifact bytes change after authorization or the digest differs from tested artifact evidence. | Reject; rebuild/reverify and obtain new authorization. |
| Owner authorization is missing, post-dated, outside the release window, or names another environment. | Block; no inferred or reusable approval. |
| Remote is absent/unavailable or push authorization is absent. | Record commit separately; push state is blocked/unverified; do not claim publication or CI on remote. |
| Workflow is interrupted, approval-pending, or evidence artifact upload is unavailable. | Record pending/unavailable; no pass based on partial output. |
| Rollback/recovery procedure is missing, unexercised where required, or inapplicable to local/offline state. | Block release; assign an operator and run a non-production recovery rehearsal. |

This rehearsal is synthetic control evidence. It does not establish application deployment readiness, active repository protection, archive authenticity, production recovery, or production quality.
