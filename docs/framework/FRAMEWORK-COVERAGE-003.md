---
id: FRAMEWORK-COVERAGE-003
type: coverage-matrix
title: FW-TASK-030 isolated execution adapter journeys and surfaces
status: draft
version: 0.1
created: 2026-10-26
updated: 2026-10-26
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-011, FRAMEWORK-ADV-047, DECISION-034, GATE-CATALOG-001, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-COVERAGE-003 — FW-TASK-030 isolated execution adapter journeys and surfaces

## Scope and evidence boundary

This is the G-COVERAGE journey/state inventory for the already approved FW-TASK-030 scope: FR-FW-035–037 and acceptance criteria AC-1–6 in FRAMEWORK-BACKLOG-001, approved by DECISION-034. The G-FEAS result is limited to one observed GitHub-hosted `ubuntu-24.04` runner using rootless Podman; FRAMEWORK-ADV-047 and FRAMEWORK-FEASIBILITY-011 preserve its exact run identities and image-version discrepancy.

The interaction under review is framework maintenance and synthetic feasibility evaluation. This artifact does not define an end-user application interface or declare a generally supported container runtime. A reusable versioned adapter contract, unsupported/missing-runtime execution behavior, and application integration remain later design/implementation work. The observed pilot workflow is evidence for coverage planning, not reusable adapter functionality.

## Actors and journey inventory

| Journey | Actor | Entry / preconditions | Main transitions and decision points | Success and failure exits | Recovery | Surface(s) | Requirements / acceptance mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J-030-01 Declare an execution request and policy | Framework adopter / maintainer | Approved task scope; a future versioned adapter/profile identifies host/runtime support, command allowlist, immutable image, identity, mounts, network, secret, resource, timeout, cancellation, cleanup, and audit policy. | Select profile → validate environment and required capabilities → accept or reject request before workload launch. Unknown profile, unsupported host, missing runtime, or unavailable capability must stop with a reason; no unsandboxed fallback. | Supported request is ready for an explicitly authorized synthetic invocation. Unsupported/incomplete request is rejected without launching work. | Correct the profile or environment under a new reviewed revision; keep the failed attempt visible. Current FW-030 feasibility workflow only observed architecture/rootless guards; a general adapter's missing-runtime behavior remains unimplemented/unverified. | P-01 repository/CLI; P-03 review | FR-FW-035; AC-1, AC-4 |
| J-030-02 Run the disposable synthetic pilot | Framework maintainer / authorized workflow operator; hosted runner executes | Exact reviewed workflow/source revision, passing required CI, approved one-run checkpoint, pinned synthetic image digest, no secrets or application source. | Dispatch → record runner/runtime identity → acquire pinned fixture → positive network control → run allowed and denied synthetic cases → inspect policy/boundaries → run timeout and resource tests → cleanup. | All required cases pass and bounded logs identify exact source/run/policy/runtime/image; any setup, policy, boundary, timeout, or cleanup mismatch fails the run. | Preserve the failed run and cleanup evidence; propose only a narrow, separately checkpointed correction and rerun after review and CI. | P-02 GitHub Actions; runner is an execution environment, not a user platform | FR-FW-036, FR-FW-037; AC-2, AC-3, AC-4, AC-6 |
| J-030-03 Review run evidence and disposition | Independent reviewer and owner | Completed provider run on the exact reviewed source; case logs and sanitized runtime identity; current threat model and feasibility limits. | Compare source/run/workflow/image/policy identities → inspect positive and negative outcomes → classify findings and image/runtime ambiguities → decide bounded feasibility disposition. | Reviewer recommends pass only for demonstrated scope or returns findings; owner accepts the bounded gate result or authorizes a new checkpoint. A CI green result alone is not a sandbox/security decision. | Correct evidence or claims under a new exact-revision review; preserve old outcomes and invalidate conclusions affected by revision changes. | P-03 pull-request/independent review; P-02 Actions run evidence | FR-FW-037; AC-4, AC-6 |
| J-030-04 Encounter an unsupported or unavailable runtime | Framework adopter / maintainer | Requested profile has unsupported OS/architecture, no runtime, no rootless mode, or a required capability is unavailable. | Profile resolution → fail-closed diagnostic → no workload start and no unsandboxed fallback. | Explicit unsupported/blocked state identifies missing prerequisite. | Provision a supported environment or select a separately reviewed profile; never relabel unsupported as passed. General missing-runtime/unavailable-capability behavior is a required contract/implementation case and was not exercised by the single supported-profile pilot. | P-01 repository/CLI; P-03 review | FR-FW-035; AC-1, AC-4 |
| J-030-05 Interrupt work and recover cleanup | Framework maintainer / hosted runner | Long-running synthetic container exists and bounded timeout/cancellation policy applies. | Request stop/cancellation → observe stop attempt and possible forced termination → remove container/network/temp files → verify absence → record cleanup disposition. | Work is stopped, resources are absent, and outcome is logged. Cleanup uncertainty/failure blocks completion. | Retry cleanup only through the approved cleanup path; retain failure evidence and require a new checkpoint if a new probe/correction is needed. The pilot observed stop escalation, removal refusal for a running container, forced cleanup, missing-target handling, and final absence. | P-02 GitHub Actions; P-03 review | FR-FW-036, FR-FW-037; AC-2, AC-3, AC-4 |
| J-030-06 Initialize an application repository | Framework adopter / maintainer | User runs the app initializer to generate project files; no runtime execution authorization is implied. | Validate inputs → write generated files transactionally → report paths → stop. The initializer does not start a container, run application code, or promise subsequent commands are sandboxed. | Generated project files are reported and initializer regression checks pass. | Repair file-generation errors and rerun the initializer check; runtime execution is a separate explicit workflow. | P-01 repository/CLI; P-03 review | FR-FW-035, FR-FW-037; AC-1, AC-5, AC-6 |

## Surface and applicability matrix

| Surface ID | Surface / platform | Applicability | In-scope user task and evidence | Exclusions / downstream effect |
| --- | --- | --- | --- | --- |
| P-01 | Framework repository, Markdown contracts, and local CLI/initializer | Applicable | Maintainers inspect/version the runner contract and threat model, run structural validation, and generate app files without starting workloads. | No end-user UI or local-host runtime support is claimed. A local machine without a verified runtime is unsupported for execution and cannot silently fall back. |
| P-02 | GitHub Actions hosted workflow and ephemeral `ubuntu-24.04` runner | Applicable only to the observed synthetic feasibility profile | The bounded pilot records exact workflow/source/run identities and exercises rootless Podman policy and synthetic boundary cases. | One observed run does not establish a permanent provider/runtime selection, broader runner-image reproducibility, application adoption, or production support. Image header/environment version mismatch remains unresolved. |
| P-03 | GitHub Actions run evidence and pull-request/independent-review surface | Applicable | Owner/reviewer checks exact revision, check results, bounded logs, risk limits, and evidence-linked gate disposition. | Status checks do not independently prove semantic correctness, branch protection, complete host isolation, or application security. |
| P-04 | Container/OCI runtime and host boundary | Execution environment, not a separate user-facing platform | The threat model locates the container inside the hosted runner VM; evidence describes tested filesystem, network, identity, capabilities, resource, timeout, and cleanup behavior. | No general Docker/Podman/OCI support, self-hosted runner support, kernel/runtime vulnerability resistance, or complete host boundary is declared. |
| P-05 | End-user web, Android, or iOS application UI | Not applicable | No end-user capability or app UI is part of DECISION-034. | No user-facing journey, mobile parity, or app-platform commitment is implied. Revisit only under separately approved product scope. |
| P-06 | Next.js, FastAPI, and Rust/Axum stack-profile lanes | Not applicable | These are unrelated synthetic language/profile adapters and are not the FW-TASK-030 host/runtime surfaces. | No stack compatibility is inferred from the hosted container pilot. |

## Failure-mode applicability and expected outcomes

| Category | Applicable | Expected outcome and recovery |
| --- | --- | --- |
| Empty | Yes | Missing task authorization, command, profile, pinned image, policy, source revision, or required evidence blocks launch or gate pass. Supply the missing versioned input and re-review; do not infer defaults that enable broader execution. |
| Malformed or corrupt | Yes | Invalid profile/policy, malformed image digest, corrupt fixture, or invalid run evidence fails closed with a specific diagnostic. Correct the source and create a new exact-revision result. |
| Unavailable | Yes | Missing runtime, unsupported host, unavailable rootless mode/capability, hosted runner outage, incomplete logs, or inaccessible evidence is `unsupported`, `unavailable`, or `blocked`, never passed. Missing-runtime behavior is not established by the observed profile and remains required for adapter implementation. |
| Unauthorized | Yes | An unapproved dispatch, secret request, app-source workload, unsupported repository/ref, or out-of-scope host cannot be treated as authorized evidence. Do not launch; obtain the relevant decision/checkpoint or narrow the request. |
| Degraded | Yes | Partial/skipped probes, conflicting runner image metadata, absent case output, failed cleanup, or a stale source/run association prevents a complete pass. Preserve observed values; reconcile or narrow claims and rerun only under a fresh approved cycle. |
| Abuse | Yes | Workload attempts parent/absolute paths, symlink traversal, subprocess escape, host/runtime socket access, network use, privilege/capability escalation, secret access, or resource exhaustion. Denied access and bounded resource outcomes must be observed; any unexpected success blocks the corresponding guarantee. |
| Recovery | Yes | Stop the workload, verify containers/network/temp files are absent, preserve failed evidence, then make a narrow revision and repeat independent review/CI before any new authorized run. A recovery attempt cannot rewrite or erase the original failure. |

## Requirement and acceptance traceability

| Trace ID | Requirements / acceptance | Covered by | Evidence basis / status |
| --- | --- | --- | --- |
| COV-030-01 | FR-FW-035; AC-1 | J-030-01, J-030-04, P-01, P-04 | Feasibility is PASS only for observed hosted candidate; reusable contract and missing-runtime/unavailable-capability fixtures remain future work. |
| COV-030-02 | FR-FW-036; AC-2 | J-030-02, J-030-05, P-02 | Synthetic policy, secret absence, timeout, resource, interruption, and cleanup outcomes passed in run 40263304567. |
| COV-030-03 | FR-FW-037; AC-3 | J-030-02, J-030-04, J-030-05, P-04 | Direct/child path and network probes, symlink, sockets, resource and cleanup checks passed for observed workflow. |
| COV-030-04 | AC-4 | J-030-02, J-030-03, P-02, P-03 | Evidence is exact-run bound and bounded; preserve unresolved runner image version disagreement and prohibit broader reproducibility claims. |
| COV-030-05 | AC-5 | J-030-06, P-01 | Runtime workflow did not execute the initializer; exact-revision Initializer Regression Gate passed. |
| COV-030-06 | AC-6 | J-030-03, J-030-04, P-03, P-04 | Threat model and ADV-047 limit claims to observed defense-in-depth controls; no complete host-isolation claim. |

## G-COVERAGE review preparation

| Criterion | Prepared evidence | Status |
| --- | --- | --- |
| GCOV-01 | Six journeys map each approved requirement and AC-1–6 to actors, preconditions, transitions, success/failure exits, recovery, and surfaces. | Prepared; independent review pending. |
| GCOV-02 | All seven required failure categories have explicit applicability, outcomes, and recovery. | Prepared; independent review pending. |
| GCOV-03 | Exact repository/CLI, hosted Actions, evidence/review, runtime environment, app UI, and unrelated stack surfaces are listed with applicability and rationale. | Prepared; independent review pending. |

## Evidence, exclusions, and next action

- **Evidence:** DECISION-034; FR-FW-035–037 and AC-1–6; FRAMEWORK-FEASIBILITY-011; FRAMEWORK-ADV-047; GATE-CATALOG-001; FRAMEWORK-GATE-CONTRACT-001 v1.0; WORKFLOW-CX-001.
- **Exclusions:** No end-user UI, mobile app, reusable adapter implementation, app integration, production runtime adoption, release/deployment, self-hosted runner, general OS/container support, or full host isolation.
- **Open interpretation:** Repository/CLI, GitHub Actions and pull-request review are treated as framework operation surfaces based on DECISION-034 and the approved non-product scope. The container is an execution environment, not a user platform. Independent review should flag a material scope conflict; do not convert this inference into an end-user/platform commitment.
- **Gate result:** G-COVERAGE in progress; no pass is asserted before independent review of this exact artifact and exact-revision Verify Pipeline.
- **Next action:** Independent review of GCOV-01–03 and the surface interpretation; if passed, prepare product-appropriate nonvisual G-CX evidence.
- **Prohibited next work:** Implementation, application adoption, production use, or a general runtime-support claim before downstream gates and explicit contracts.
