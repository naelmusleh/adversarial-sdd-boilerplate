---
id: FRAMEWORK-FEASIBILITY-011
type: feasibility-register
title: FW-TASK-030 isolated execution adapter feasibility
status: draft
version: 0.5
created: 2026-10-25
updated: 2026-10-25
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-ADV-038, FRAMEWORK-ADV-039, FRAMEWORK-ADV-040, DECISION-034, WORKFLOW-FEASIBILITY-001
---

# FRAMEWORK-FEASIBILITY-011 — FW-TASK-030 isolated execution adapter feasibility

## Scope and exclusions

This is a G-FEAS evaluation under DECISION-034 for FR-FW-035–037. It evaluates whether a disposable hosted Linux runner can execute a synthetic command under a rootless container policy with explicit filesystem, network, identity, resource, timeout, interruption, cleanup, and audit behavior.

It does not adopt a runtime for applications, implement the reusable adapter, execute private application code or user data, use secrets, deploy, alter repository protection, or claim complete host isolation. Any passing result is specific to the exact observed runner image, runtime, image digest, workflow revision, and cases. A new environment or material configuration change requires a new evaluation.

## G-REQ and work checkpoint

DECISION-034 approved the requirements scope only. G-REQ passed at `25896b1c376331dee781d04ef0e17ab712287da4` after independent review in [FRAMEWORK-ADV-038](../adversarial-reviews/FRAMEWORK-ADV-038.md). Verify Pipeline run [40246570924](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40246570924) passed on that exact SHA. Artifact validation passed for 90 artifacts. G-FEAS is active; no implementation is authorized.

## Candidate screen

| Candidate | Observation | Classification | Boundary / dependency |
| --- | --- | --- | --- |
| Local macOS Docker Desktop | macOS arm64 and Docker CLI are present. The configured `desktop-linux` Docker socket was inaccessible in the normal shell and the daemon was not running when inspected with elevated read-only access. Podman CLI was not found. | Unknown / currently unavailable | Do not start the user's local daemon or treat the client binary as proof of an executable runtime. Revisit only if the owner provides an available local engine and approves its use. |
| Self-hosted GitHub runner | Not tested; requires a maintained host and runner lifecycle. | Constrained; not selected for the pilot | GitHub warns self-hosted runners do not have the same ephemeral-clean-VM guarantee and may be persistently compromised by untrusted workflow code. Exclude from the first pilot. |
| GitHub-hosted Ubuntu 24.04 + rootless Podman | Official runner image inventory lists Podman 4.9.3. No execution behavior has yet been observed in this repository's hosted run. A disposable candidate probe pins the linux/amd64 Alpine workload manifest to `sha256:dc92f017beea8e7f43263073d717f7bc011228c95d5312e440deb4d035bb4eec`. | Candidate; unverified | Use exact runner and Podman versions observed during a disposable CI probe. Runner images move; results do not establish a permanent support promise. |

Sources: [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use), [GitHub runner image inventory](https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md), Docker's official [rootless mode documentation](https://docs.docker.com/engine/security/rootless/), and the Docker Official Image [Alpine manifest details](https://github.com/docker-library/repo-info/blob/master/repos/alpine/tag-details.md). Source observations retrieved 2026-10-25. Rootless execution is a mitigation, not complete separation; the pinned workload image digest fixes the linux/amd64 Alpine image bytes used by this probe.

## Threat model

The synthetic workload is treated as adversarial code that may attempt to escape its intended filesystem view, follow symlinks, spawn subprocesses, access host/runtime sockets, use network, exhaust CPU/memory/process/time limits, or ignore graceful cancellation. The pilot protects a disposable hosted runner from accidental or malicious access by that workload within the measured controls. It does not assume protection against a kernel or container-runtime vulnerability, compromise of the hosted runner control plane, malicious workflow/action changes, denial of service to GitHub, or access to secrets that the workflow grants. Therefore the pilot grants no repository secrets, sets workflow token permissions to `contents: read` only if checkout is needed (otherwise `permissions: {}`), and must not execute arbitrary repository/application source.

The local host boundary remains the GitHub-hosted runner VM. The container boundary is defense in depth inside that VM. Evidence must not claim that rootless Podman prevents all host access or provides a stronger boundary than the negative tests establish.

## Probe matrix

| ID | Question / method | Required result for supported pilot profile | Dependencies |
| --- | --- | --- | --- |
| FEAS-FW030-01 | Does a fresh GitHub-hosted Ubuntu 24.04 job have a usable rootless Podman runtime? Record runner image, kernel, Podman, storage/network backends, and rootless identity. | Run a harmless synthetic command as non-root; otherwise classify unsupported and do not fall back to Docker's rootful daemon. | FR-FW-035; hosted runner availability. |
| FEAS-FW030-02 | Can the invocation constrain command, immutable image digest, user, mounts, network, resource/time ceilings, cleanup, and secret/environment propagation? | Positive allowlisted command succeeds; denied command/network fails; read-only/isolated mount behavior is observed; resource/time limit and container removal are evidenced. The workflow defines no secrets, uses no secret context, and injects a synthetic host-only environment sentinel; the container must not receive it. Image reference is pinned by digest. | FR-FW-036; exact image digest and action pins must be frozen before execution. No real credentials are used. |
| FEAS-FW030-03 | Do direct and subprocess adversarial path probes escape the container's intended mount? | Parent/absolute path and symlink probes cannot read a synthetic host sentinel or unmounted runner path. A child process launched inside the container repeats the sentinel and denied-network probes and must not gain access. Runtime socket/host mount is absent. A failed case blocks the corresponding claim. | FR-FW-037; test only synthetic sentinels and no sensitive host files. |
| FEAS-FW030-04 | Are cancellation and failure cleanup observable? | A bounded long-running synthetic process receives cancellation; workflow cleanup confirms the disposable container is removed, or documents a clear cleanup failure. | FR-FW-036; hosted runner cancellation semantics. |
| FEAS-FW030-05 | Does generated evidence remain bounded and secret-free? | Record exact commit, run, runner/runtime/image/policy identities, commands, exit codes, case outcomes, and bounded logs; no tokens, environment dumps, source, or unrestricted logs. | FR-FW-036/037; no secret permissions. |

## Planned procedure and current limits

1. Independently review this plan and the temporary workflow before execution. Pin all third-party actions by immutable commit SHA. Pin the workload image by digest; a mutable tag is not acceptable.
2. Use one temporary, branch-restricted GitHub Actions workflow on an ephemeral `ubuntu-24.04` hosted runner. The workflow must use no repository secrets and must never invoke the repository's product/test code. Keep permissions minimal; do not grant OIDC, attestations, packages, deployment, or repository write access.
3. Use rootless Podman only. Set network to none for the workload, mount only a fresh synthetic fixture directory with explicit read/write mode, drop capabilities, prohibit privilege escalation, set process/memory/CPU/time limits, and ensure cleanup with a bounded `finally` step. Never mount the Docker/Podman socket or host root.
4. Execute the positive and negative matrix against exact frozen inputs. Save only bounded result codes, identities/digests, and sanitized output. Do not make G-FEAS pass on plan review or package availability alone.
5. Remove temporary workflow/fixture files after the run; run artifact validation and the exact-revision Verify Pipeline on the evidence record. Independently review the final record before deciding G-FEAS.

Current state: plan review round 1 at exact commit `e7351e841eaaeed1a65b28ed95e2278fcec007be` returned NEEDS-CHANGES for explicit secret non-inheritance and a child-process boundary attempt. Both corrections in v0.2 were independently re-reviewed at exact commit `a70e989a47c54a69643ccee8e6a56e18c55d293d` and passed; see [FRAMEWORK-ADV-039](../adversarial-reviews/FRAMEWORK-ADV-039.md). This PASS establishes plan readiness only. Workflow review round 1 at `7eee540696564326976a04cd6c5fc9e3dea00128` found false-pass risks in network reachability, mounted-input accessibility, timeout/resource/cleanup outcome classification, and observed policy/backend reporting. The corrected candidate at `9632a055a914f4b9e37aea9eb7561eaeac803807` addressed those issues but its independent follow-up identified an ignored cleanup failure and missing temporary-directory absence check. FRAMEWORK-ADV-040 records both rounds. A cleanup correction is now prepared; no hosted workload has run. The corrected exact revision requires a further independent review before dispatch, subject to the repository's owner checkpoint. No supported-host/isolation claim is established.

**G-FEAS correction work record (2026-10-25):** Active gate: G-FEAS. Exact base: `7eee540696564326976a04cd6c5fc9e3dea00128` on `codex/fw030-greq`; CI passed on that revision and the optional runtime probe was skipped. Independent reviewer `/root/fw029_independent_review` returned NEEDS-CHANGES before any probe execution (FRAMEWORK-ADV-040): the network target was unroutable; the mounted fixture had no successful-read control; nonzero status alone could misclassify setup errors as expected timeout/resource/cleanup outcomes; and the workflow claimed but did not inspect CPU, capabilities, privilege-escalation, storage backend, and network backend controls. Corrective workflow edits add a local reachable server/client control before the `--network=none` workload, world-readable synthetic fixture plus positive read, exact expected runtime outcomes with start/state checks, inspect assertions for configured CPU/capability/no-new-privileges policy, and runtime backend identity. `python3 scripts/artifacts.py list` completed; `validate` passed for 93 artifacts; YAML parsing and extracted-shell syntax checks passed. This record describes correction intent, not observed runtime behavior. The workflow remains undispatched pending independent review of the corrected exact revision.

**G-FEAS cleanup correction checkpoint (2026-10-25):** Independent follow-up review of exact commit `9632a055a914f4b9e37aea9eb7561eaeac803807` confirmed the prior network, mount, expected-outcome, and policy-reporting corrections, but found the exit trap could ignore container/network deletion failures and did not verify the temporary directory was removed. The trap now reports cleanup failure, verifies named containers/network absence, and verifies temporary-file deletion; this correction has not yet been reviewed or run. No G-FEAS PASS is claimed. The workflow remains undispatched pending the repository-required owner checkpoint before a further consecutive adversarial review.

## G-FEAS disposition

Pending. G-FEAS can pass only for a bounded named runner/runtime profile after the positive and negative pilot evidence is complete, independent review finds no blocking issue, the limitations are explicit, and downstream dependency states are updated. Otherwise record the specific blocker and keep G-ARCH/G-IMPL blocked.
