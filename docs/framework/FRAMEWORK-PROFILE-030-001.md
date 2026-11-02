---
id: FRAMEWORK-PROFILE-030-001
type: framework-execution-profile
title: FW-030 bounded GitHub Actions Ubuntu 24.04 rootless Podman profile
status: in-review
version: 1.0
created: 2026-10-28
updated: 2026-10-28
related-artifacts: FRAMEWORK-ARCHITECTURE-004, FRAMEWORK-FEASIBILITY-011, FRAMEWORK-ADV-052, FRAMEWORK-CONTRACT-030, DECISION-043, FRAMEWORK-BACKLOG-001
---

# FRAMEWORK-PROFILE-030-001 — Bounded GitHub Actions profile

## Authority and claim boundary

DECISION-043 selects this profile only as the implementation target for FW030-IMPL-02 and accepts the residual risks below for this bounded unit. Selection does not establish general or production support. The only observed end-to-end evidence before implementation is one synthetic run, Verify Pipeline [40592505706](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40592505706), reviewed in FRAMEWORK-ADV-052.

The adapter must refuse other hosts, providers, architectures, runtime versions, profile revisions, or workload image digests. It must never fall back to host execution. This profile does not support local macOS/Docker, self-hosted runners, arbitrary OCI runtimes, application workloads, secrets, or workload network access.

## Exact observed profile

| Property | Required value |
| --- | --- |
| Provider | GitHub-hosted Actions runner |
| Operating system | Ubuntu 24.04, `ImageOS=ubuntu24`, Linux |
| Architecture | x86_64 / linux/amd64 |
| Container runtime | Rootless Podman 4.9.3 |
| OCI runtime | crun 1.14.1 |
| Workload image | `docker.io/library/alpine@sha256:dc92f017beea8e7f43263073d717f7bc011228c95d5312e440deb4d035bb4eec` |
| Profile identity | `github-actions.ubuntu-24.04.rootless-podman` revision `2026-10-28.1` |

### Known residual risks

- The runner log header `20261012.334.1` conflicts with environment value `ImageVersion=20261023.334.3`. Stable runner-image identity and reproducibility are not established. The adapter reports both values and does not silently choose one.
- Podman escalated SIGTERM to SIGKILL in two observed stop/cleanup cases. Graceful process-tree termination is not claimed.
- A container shares the host kernel. The profile is defense in depth, not complete host isolation or resistance to kernel/runtime compromise.
- Hosted artifact/log retention and secure deletion are unspecified. The synthetic report is run-log evidence only.

## Effective workload policy

The profile-specific synthetic pilot accepts only the exact pinned image, a shell workload script from one canonical temporary input directory, one read-only input bind, and one temporary output destination implemented as a bounded container tmpfs and copied out after completion. It enforces rootless execution, non-root UID/GID, dropped capabilities, no-new-privileges, read-only root filesystem, disabled workload networking, no host environment/secret injection, CPU/memory/PID/wall-time ceilings, and tmpfs capacity. The adapter inspects effective runtime configuration and refuses mismatches.

For the synthetic pilot only, proposed workload values are 1 CPU, 128 MiB memory, 32 processes, 16 MiB output tmpfs, and 30 seconds. These are test inputs, not universal or application defaults. Host-side network access is used anonymously only to retrieve the exact pinned public image; no registry credentials or workflow secrets are supplied.

## Evidence and recovery

The versioned InvocationResult remains the inner contract record and reports execution, cleanup, evidence, and review independently. The outer pilot report binds repository/revision and Actions run/attempt to the selected profile, records observed Podman/OCI/runner metadata and limitations, and emits no source, secrets, full environment, or unbounded output. It does not claim durable evidence. On timeout or cancellation, container removal and independent absence observation are attempted; unknown or failed cleanup remains visible and cannot be changed into a successful execution result.

## Re-evaluation triggers

A different OS release, architecture, Podman or crun version, runner image, workload image digest, mount/network/secret policy, or resource control requires a reviewed profile revision and fresh feasibility evidence. FW030-IMPL-02 does not authorize app integration or production use.
