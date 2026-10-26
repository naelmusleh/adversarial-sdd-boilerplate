---
id: FRAMEWORK-ARCHITECTURE-004
type: framework-architecture
title: FW-TASK-030 optional isolated command runner architecture
status: approved
version: 1.0
created: 2026-10-26
updated: 2026-10-26
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, DECISION-034, FRAMEWORK-FEASIBILITY-011, FRAMEWORK-COVERAGE-003, FRAMEWORK-CX-003, FRAMEWORK-ADV-047, FRAMEWORK-ADV-048, FRAMEWORK-ADV-049, FRAMEWORK-ADV-050, FRAMEWORK-GATE-CONTRACT-001, WORKFLOW-FEASIBILITY-001
---

# FRAMEWORK-ARCHITECTURE-004 — FW-TASK-030 optional isolated command runner architecture

## Gate work record

- **Gate:** G-ARCH, active. G-REQ, bounded G-FEAS, G-COVERAGE, and G-CX passed for the FW-TASK-030 scope under DECISION-034.
- **Task/requirements:** FW-TASK-030; FR-FW-035–037 and AC-1–6 only.
- **Inputs:** FRAMEWORK-FEASIBILITY-011 and FRAMEWORK-ADV-047 (one hosted synthetic run); FRAMEWORK-COVERAGE-003/ADV-048; FRAMEWORK-CX-003/ADV-049; DECISION-034.
- **Target:** A stack-neutral optional adapter contract, a policy/configuration and result model, bounded evidence flow, failure/recovery semantics, and task-ready implementation plan.
- **Non-adoption boundary:** GitHub-hosted Ubuntu 24.04 with rootless Podman is only the observed feasibility candidate. No supported production profile, provider, release, or app-specific runtime is adopted. The runner-image version mismatch remains unresolved. The local macOS/Docker profile is unverified. Architecture may describe these candidates and alternatives but cannot label them supported.
- **Implementation dependency:** Runtime-backed implementation remains blocked until the owner selects a concrete profile and accepts its residual risks. A pure contract/schema/validation unit may be separately proposed only if it does not imply runtime support; it is not authorized by this G-ARCH record.
- **Exclusions:** FW-TASK-031, application integration, app source/data/secrets, production use, deploy/release, unsandboxed fallback, unrestricted host mounts, self-hosted runner support, general OCI/Docker/Podman support, kernel/runtime compromise resistance, and complete host isolation.
- **Review plan:** Independent architecture/security review against GARCH-01–03, artifact validation, `git diff --check`, and exact-revision Verify Pipeline. Any named profile or high-impact control remains a candidate until the owner decides and required evidence exists.

## Architecture decision summary

The framework will expose an **optional request contract** that an orchestrator must submit to an explicitly selected adapter. A resolver validates the request against a versioned profile and policy before a workload can start. The adapter either returns a structured unsupported/blocked result without execution or invokes the exact allowlisted workload with declared identity, image, mounts, network, secrets, resource, time, audit, cancellation, and cleanup controls. The result separates execution outcome from cleanup state and carries bounded provenance. A reviewer evaluates that evidence against the named profile's threat model; neither a successful command nor green CI alone authorizes a lifecycle gate.

At present, the architecture has no adopted runtime adapter. The hosted Podman pilot demonstrates feasibility for one run and profile snapshot only. It is evidence for candidate trade-offs, not a default, support commitment, implementation, or production deployment decision.

## System context and responsibilities

| Component / actor | Responsibility and authority | Boundary and failure behavior |
| --- | --- | --- |
| Framework adopter / task owner | Authors an explicit request and policy reference; approves whether execution is allowed for their task. | Cannot make an unsupported profile run by adding a fallback. Missing or unauthorized configuration blocks before workload launch. |
| Request resolver / policy validator (proposed) | Resolves profile and policy revisions; validates required fields, image/runtime identity, command allowlist, mounts, network, secret policy, limits, and declared capability requirements. | Pure validation only; no host command execution. Unknown schema/profile/capability is `unsupported` or `blocked`; no implicit defaults that grant access. |
| Adapter interface (proposed) | Receives a validated immutable request and returns a normalized invocation result plus bounded evidence references. | Versioned, optional, capability-specific. Adapter errors remain distinct from workload failures. No adapter is a valid configured state; request fails closed. |
| Host adapter/runtime (not adopted) | Executes the exact command in a named rootless container or equivalent OS sandbox under the accepted profile. | Runtime, kernel, daemon/control socket, host mounts, and provider runner remain separate trust boundaries. If enforcement cannot be observed, the corresponding guarantee is unavailable. |
| Evidence collector (proposed) | Records source/request/profile/policy/runtime/image identities, case outcomes, exit state, and cleanup observations without secret values or unrestricted environment capture. | Bounded and redacted. Missing/mismatched fields make evidence incomplete; provider retention and durability are not promised. |
| Initializer | Generates project files and reports file outcomes. | Must not call the adapter, start a container, request runtime authorization, or imply later commands are sandboxed. |
| Independent reviewer / owner | Reviewer checks exact evidence and threat claims; accountable owner records gate disposition and residual-risk decisions. | Reviewer recommendation, CI result, signature, and score cannot substitute for owner authority or each other. |

### Trust boundaries and data flow

1. **Policy authoring boundary:** Request/policy bytes are versioned in the repository. Secret values are referenced only through a future profile-approved secret mechanism; default is no secrets. Do not place values in source, command arguments, image layers, logs, or evidence.
2. **Orchestrator-to-adapter boundary:** The request binds a schema version, exact source SHA, profile ID/revision, policy digest, command argv, image/runtime identity, mounts, network, secret references/disabled state, limits, timeout, cancellation, and evidence mode. It is immutable for the run. Any request change requires a new digest and authorization.
3. **Adapter-to-runtime boundary:** The adapter invokes only the explicitly named runtime and exact allowlisted command. Runtime absence, permission errors, or missing required capabilities return before launch. The adapter must never execute the command on the host as a fallback.
4. **Workload-to-host boundary:** Workload code is untrusted. A container shares the host kernel and depends on runtime configuration. Namespaces, rootless identity, capabilities, read-only mounts, network controls, and resource limits are defense-in-depth controls; none imply protection from kernel/runtime compromise unless that threat is explicitly tested and accepted.
5. **Runtime-to-evidence boundary:** Collector records allowlisted observations, stable identifiers, bounded diagnostics and digests. It excludes secret values, full process environments, source contents, and unbounded logs. Run metadata and logs may contain provider-controlled values and are treated as untrusted data.
6. **Evidence-to-gate boundary:** Exact-revision CI, runtime observations, independent review, and owner decision remain distinct. The evidence identifies one profile/run and cannot be generalized across OS versions, provider image releases, architectures, runtimes, or workloads.

### Data and state ownership

| Data | Authority / owner | Lifetime and protection |
| --- | --- | --- |
| Profile contract and capability declarations | Framework maintainers propose; owner approves support claims | Versioned source artifact; changing profile identity or guarantees requires review and new evidence. |
| Invocation policy and authorization | Application/task owner for the specific invocation | Immutable digest for a run; no secrets by default; not persisted in logs beyond bounded non-secret fields. |
| Runtime resources | Adapter owns resources it creates; host/provider remains responsible for underlying runner | Unique per-run names; cleanup attempts run on normal, failed, timed-out, and cancelled paths; uncertain absence blocks subsequent work and remains visible. |
| Invocation record | Adapter/collector produce execution and cleanup observations; provider may host execution status; reviewer assesses meaning in a separate review artifact | Exact source/invocation/profile/policy binding, bounded fields, redaction, and provider-retention caveat. No durable evidence promise until separately specified. |
| Review record | Independent reviewer evaluates exact invocation evidence; authorized owner records gate decision separately | Never authored by the adapter. Findings and disposition bind to exact source/artifact/evidence digests; reviewer role does not grant gate-owner authority. |
| Gate disposition and risk acceptance | Authorized owner, informed by independent review | Durable governance record; never inferred from adapter result or CI badge. |

## Proposed versioned contract

The wire representation should be JSON or another deterministic, schema-validated format with explicit major version and a canonical digest. Concrete field names remain subject to independent review. Minimum logical request shape:

| Field group | Required content | Fail-closed rule |
| --- | --- | --- |
| Contract identity | Contract major/minor, profile ID and exact profile revision | Unknown incompatible major/profile blocks; minor-version compatibility must be explicit. |
| Invocation identity | Unique invocation ID, execution-context kind, repository identity and exact source identity (commit plus content digest when the tree differs), policy digest | Missing/ambiguous invocation ID, unverifiable source identity, or policy mismatch blocks launch or makes evidence incomplete. |
| Provider context | For hosted/provider execution: provider, workflow, job, run and attempt IDs, event/ref, and run URL when available. For local execution: explicit `context_kind: local` and an explicit absence reason instead of fabricated provider fields. | Provider fields are conditional on execution context. If provider context is selected, missing required provider identifiers makes provenance incomplete. Empty strings or guessed IDs are never used to satisfy the schema. This is a contract shape only; local support is not thereby adopted. |
| Workload | Immutable image reference/digest, exact argv array, working directory, allowed command identity | Mutable tags, shell-string ambiguity, unlisted command, or image mismatch blocks. |
| Identity and filesystem | Numeric execution UID/GID; explicit input/output mounts and modes; ephemeral workspace | Root identity, undeclared host path, runtime socket, broad parent mount, writable source/input, or path escape blocks. |
| Network and secrets | Network disabled by default; secret injection disabled by default; narrowly named exceptions only when owner-authorized | Unknown network mode or secret-bearing env/log exposure blocks. Secret exception requires separate documented scope and implementation control. |
| Resource/time | CPU, memory, process, disk/tmpfs and wall-clock limits; cancellation policy | Missing or unenforced limit required by profile blocks; timeout/cancel does not imply cleanup. |
| Audit/cleanup | Bounded case set, identifiers, redaction policy, teardown requirements | Missing cleanup result or unbounded/sensitive diagnostic prevents evidence completeness and gate pass. |

The adapter emits an `InvocationResult` containing request/preflight status, a reference to supplied authorization (never an authorization decision), execution outcome, cleanup status, evidence completeness/freshness, case results, and bounded evidence references. It cannot create or grant authorization and never emits reviewer disposition. An independent reviewer creates a separate `ReviewRecord` bound to the exact invocation/result digests; the accountable owner creates or updates the separate gate disposition. A read-only report may project request readiness, authorization, execution, cleanup, evidence, and review as separate axes, but must preserve each source and authority. The invocation record preserves terminal execution outcome through cleanup and cannot roll up to successful execution when a required case is failed, skipped, unknown, stale, or mismatched. These are conceptual contracts, not implemented interfaces/schemas.

## Failure, timeout, cancellation, and recovery

| Failure | Required observable result | Recovery and gate consequence |
| --- | --- | --- |
| Empty, malformed, unknown, or incompatible profile/policy | Block/unsupported before execution, with field/category and no secret echo | Correct a reviewed revision; no run is created. |
| Unsupported host, missing runtime, unavailable capability | `UNSUPPORTED` or `BLOCKED`; state explicitly no workload started and no unsandboxed fallback | Provision or select a separately reviewed profile; this remains unimplemented until adapter work. |
| Provider/runtime setup failure | `FAILED` execution or `NOT_STARTED` as observed; adapter-level error separated from workload exit; cleanup independently tracked | Preserve evidence and resource identifiers; retry only as a new authorized run after diagnosis. |
| Workload timeout or cancellation | Execution `FAILED` or `CANCELLED`; timeout/stop event and timestamps recorded | Stop then forced termination only under explicit policy; cleanup remains `REQUIRED` until absence observed. |
| Cleanup failure or uncertain absence | Cleanup `REQUIRED`; original execution result unchanged; block new invocation on the same resource namespace | Approved cleanup/recovery procedure, independent absence verification, retain failure evidence. |
| Boundary-control violation | Named case `FAIL`; exact observed access and affected guarantee recorded | Narrow the guarantee or redesign profile; cannot waive with prose or CI success. |
| Evidence missing, stale, conflicting, or sensitive | Evidence `INCOMPLETE`, `STALE`, or `CONFLICTED`; no gate pass | Correct collector or preserve allowed evidence; never synthesize missing results or replace original run. |
| Initializer error | File-generation diagnostic only; no runtime side effects | Repair/retry initializer; runtime execution remains a separate workflow. |

## Security, privacy, and operational controls

- Deny by default: no network and no secret values; only a concrete owner-approved policy may introduce an exception.
- Use a pinned workload image digest and declared runtime identity; record runtime version and effective configuration. Pinning one image does not pin the host runner image.
- Pass argv as structured arguments; avoid shell interpolation. Allow only reviewed executable/arguments. Workload and repository content are untrusted.
- Mount only named inputs read-only and one explicit output destination writable. Never mount repository parent directories, home directories, credentials, runtime sockets, or host control paths.
- Run non-root under the profile's numeric identity; drop all unnecessary capabilities; prohibit privilege escalation; require rootless execution when that is the adopted profile's prerequisite.
- Apply and observe CPU, memory, process-count, disk/tmpfs, and wall-time limits. A declared limit that cannot be verified is not claimed as enforced.
- Use unique per-run resources; trap normal signals; attempt cleanup on all exits; verify absence independently. Preserve both the run outcome and cleanup outcome.
- Emit bounded, structured evidence with stable references and sanitized diagnostics. Do not capture entire environments, source content, tokens, unbounded command output, or secret-bearing config.
- Treat runner logs, Actions outputs, artifacts, and provider metadata as untrusted and potentially short-lived. Retention, deletion, and durability remain unspecified unless a separate decision/evidence establishes them.
- Separate CI status, adapter status, independent reviewer recommendation, and owner gate decision in all reporting.

## Alternatives and architecture records

| ADR | Decision area | Alternatives and evidence | Proposed disposition / authority | Downstream consequence |
| --- | --- | --- | --- | --- |
| ADR-FW030-01 | Adapter abstraction | A: host-neutral optional interface with explicit profile capability declaration. B: bake one provider/runtime directly into the lifecycle runner. | Recommend A to satisfy FR-FW-035 and avoid universal runtime assumptions. Within approved requirements; independent review required. | Adapter implementations become separate, profile-specific tasks; absent adapter fails closed. |
| ADR-FW030-02 | Initial runtime profile | A: GitHub-hosted Ubuntu 24.04/rootless Podman pilot candidate (one observed run; runner image metadata mismatch). B: local Podman/Docker (local engine was inaccessible). C: another OS-native sandbox (not evaluated). | No adoption now. Owner must select a candidate after G-ARCH and decide whether to authorize its implementation. Feasibility evidence alone is not adoption. | Runtime-backed implementation is blocked; follow-up profile evaluation/adoption task remains conditional. |
| ADR-FW030-03 | Request and evidence state model | A: one flat status field. B: separate readiness, authorization, execution, cleanup, evidence, and review axes. | Recommend B; required to preserve authorization and failed execution through recovery, and approved by G-CX contract. | Every adapter/result schema and UI/CLI surface must preserve all axes. |
| ADR-FW030-04 | Unsupported behavior | A: transparent unsandboxed fallback. B: fail closed with reason and safe recovery. | B is required by FR-FW-035; A is prohibited. No owner exception path is proposed. | Unsupported/missing prerequisites stop before workload launch. |
| ADR-FW030-05 | Initializer integration | A: start a container during project initialization. B: initializer remains file generation; a separate authorized runner entrypoint executes workloads. | B is required by FR-FW-037. | Initializer regression check remains a separate mandatory acceptance check. |

## Quality, verification, and operations

- **Supported surfaces:** framework repository and CLI; profile-specific hosted or local execution only after explicit owner adoption; CI and pull-request review for source/check evidence. No user-facing web/native app is in scope.
- **Required task verification:** artifact/schema validation; deterministic positive and negative request fixtures; profile-specific integration tests on the adopted environment; positive controls and boundary denial probes; timeout, resource exhaustion, cancellation, cleanup failure/recovery; initializer regression; no-secret audit; exact-run evidence binding; independent security review.
- **Observability:** per-run source/profile/policy/image/runtime IDs, case outcome, exit status, start/finish, cancellation/timeout, and cleanup state. Avoid telemetry of workload contents. Provider retention remains unknown; report if evidence is ephemeral.
- **Support/incident:** framework maintainer owns contract changes; app/task owner authorizes use and any secret/network exception; runner/operator owns resource cleanup within the execution host. A suspected boundary escape blocks profile use and requires preserving evidence and owner security review.
- **Rollback:** disable/remove the selected profile or adapter and leave all executions blocked/unsupported. Never revert to host execution as a recovery path.

## Requirement-to-architecture mapping

| Requirement / acceptance | Architecture coverage | Evidence still required in G-IMPL |
| --- | --- | --- |
| FR-FW-035 / AC-1: versioned optional host-neutral contract; explicit supported/unsupported; fail closed | Versioned contract, profile capability declaration, alternatives ADR-01/02, unsupported behavior ADR-04 | Schema and fixtures for supported profile, unsupported host, missing runtime, unavailable capability; verify no launch/fallback. |
| FR-FW-036 / AC-2, AC-4: least privilege; exact identities/policy/audit; disposable pilot | Minimum policy fields, trust boundaries, redaction and evidence model, failure/cleanup rules | Profile-specific enforcement tests for identity/mount/network/secrets/resources/time and bounded exact-run evidence. |
| FR-FW-037 / AC-3, AC-5, AC-6: adversarial cases; initializer boundary; bounded claims | Trust-boundary/threat exclusions, failure table, ADR-05, separate reviewer/owner authority | Adversarial profile tests, initializer regression, independent security review against exact implementation and evidence. |

## Task-ready backlog decomposition

| Proposed unit | Scope | Dependency/state | Acceptance evidence |
| --- | --- | --- | --- |
| FW030-IMPL-01 | Versioned host-neutral request/result contract, schema validator, and deterministic synthetic fixtures; no runtime support claim | Conditional on G-ARCH PASS and an explicit owner implementation authorization; can be platform-neutral | Validate allowed schema versions and reject unsupported/missing/malformed profiles, policy and capabilities before any command launch; include separate state axes and redaction. |
| FW030-IMPL-02 | One profile-specific adapter implementation and enforcement suite | **Blocked** until owner selects/adopts a host/runtime profile and accepts its residual risk; no implicit default | Exact command/image/runtime identity; deny-by-default network/secrets; identity/mount/resource/time policy; positive and negative controls; cleanup/cancellation; independent security review. |
| FW030-IMPL-03 | Bounded evidence collector and CLI/reporting adapter | Conditional on FW030-IMPL-01; profile-specific fields depend on FW030-IMPL-02 | Exact source/request/profile/policy/run binding; bounded redacted output; stale/incomplete/conflicted states; no gate pass from CI alone. |
| FW030-IMPL-04 | Initializer non-execution regression and docs integration | Can proceed only after separate G-IMPL authorization for a selected unit | Regression proves initializer generates files only and starts no workload; commands remain separate and explicit. |

Each unit remains a proposal until G-ARCH passes and the owner authorizes a G-IMPL scope. Do not split or start units just because the architecture lists them. FW030-IMPL-02 cannot proceed before its profile choice. If the owner elects not to adopt a profile, close the runtime adapter portion as not adopted rather than claiming generic support.

## G-ARCH review preparation

| Criterion | Prepared evidence | Status |
| --- | --- | --- |
| GARCH-01 — boundaries, identities, data, integration/failure, security/privacy, operations/recovery | Context/trust boundaries; data ownership; contract; failure/recovery; security and operational controls | PASS — FRAMEWORK-ADV-050 |
| GARCH-02 — ADRs, authority, alternatives, constraints, linked task scope/checks | Five ADRs identify alternatives, decision authority, consequences; implementation units map to requirements and dependencies | PASS — FRAMEWORK-ADV-050 |
| GARCH-03 — coherent handoff and no invented decisions | Runtime adoption is explicitly open and blocks runtime-backed implementation; no support/provider choice is inferred | PASS — FRAMEWORK-ADV-050 |

## G-ARCH finding register

| Finding ID | Location / issue | Severity | Disposition |
| --- | --- | --- | --- |
| ARCH030-01 | v0.1 provenance required workflow/job/run fields despite the host-neutral/local context. | P2 | Resolved in v0.2. Independent GARCH-02 review confirmed mandatory neutral invocation identity, conditional provider workflow/run context, and explicit local absence semantics (FRAMEWORK-ADV-050). |
| ARCH030-02 | v0.1 adapter result mixed reviewer disposition with adapter-produced evidence. | P2 | Resolved in v0.2. Independent GARCH-02 review confirmed separate adapter `InvocationResult`, independent `ReviewRecord`, and owner gate disposition (FRAMEWORK-ADV-050). |

## Next action and limits

G-ARCH passes for the approved scope based on independent review in FRAMEWORK-ADV-050 of exact artifact blob `371e58eca446c075d46a2d22944215406c24e2fa` at source `020f4ef3185cb3a418f744e4b8f2521df8e78ec8` and exact-revision Verify Pipeline run `40265528089`. ARCH030-01/02 are resolved. No runtime profile, provider, implementation, app adoption, production use, or deployment is selected or authorized here.
