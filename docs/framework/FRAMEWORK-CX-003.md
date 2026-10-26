---
id: FRAMEWORK-CX-003
type: framework-cx
title: FW-TASK-030 runner request and evidence interaction contract
status: draft
version: 0.1
created: 2026-10-26
updated: 2026-10-26
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-COVERAGE-003, FRAMEWORK-FEASIBILITY-011, FRAMEWORK-ADV-047, FRAMEWORK-ADV-048, DECISION-034, GATE-CATALOG-001, FRAMEWORK-GATE-CONTRACT-001, WORKFLOW-CX-001
---

# FRAMEWORK-CX-003 — FW-TASK-030 runner request and evidence interaction contract

## Gate work record and boundary

- **Gate:** G-CX, active; no pass is claimed before complete-scope independent critique and exact-revision Verify Pipeline.
- **Task/scope:** FW-TASK-030 within DECISION-034 and FR-FW-035–037 only; G-COVERAGE passed for FRAMEWORK-COVERAGE-003.
- **Target:** Product-appropriate nonvisual interaction contract for framework maintainers/adopters using repository documentation/CLI, a hosted synthetic feasibility workflow, run evidence, and independent review.
- **Source scope:** Six journeys J-030-01–06 and surfaces P-01–06 in FRAMEWORK-COVERAGE-003. The conceptual interface below is not an implemented CLI or reusable adapter API.
- **Known feasibility:** One synthetic run on GitHub-hosted Ubuntu 24.04/rootless Podman passed within the limits in FRAMEWORK-ADV-047 and FRAMEWORK-ADV-048. Runner image release metadata remains inconsistent. This does not make a reusable runner profile or general runtime support available.
- **Method:** Manual tool-neutral critique of every journey and state in this artifact. There is no end-user GUI or native UI to render; no Figma prototype, accessibility conformance, device behavior, or runtime behavior is claimed. No Material 3 or Apple HIG visual pattern applies to this CLI/hosted-workflow target; accessible text output and documented keyboard/provider behavior remain implementation verification obligations.
- **Exclusions:** End-user app UI, Android/iOS app flows, unrelated stack profiles, production use, application adoption, general runtime support, full host isolation, deployment, and implementation.

## Interaction principles and state model

1. Show scope and authority before execution: requested task, source revision, profile, exact synthetic workload, and whether authorization is present.
2. Treat unknown, unsupported, missing, stale, or conflicting prerequisites as blocking. Never imply that a blocked request ran or silently offer an unsandboxed alternative.
3. Keep execution outcome, evidence completeness, and reviewer disposition separate. A passing process exit does not alone pass a governance gate.
4. Keep user-facing output free of secret values and sensitive environment contents. Identify evidence by stable run/source/policy/image references and bounded case names.
5. Preserve failed run evidence and cleanup results; recovery does not erase or replace the original attempt.
6. Explain the next safe action at every blocked or failed state; do not invite an operator to bypass a restriction.

| Axis | Allowed values | Meaning |
| --- | --- | --- |
| Request | `DRAFT`, `READY`, `BLOCKED`, `UNSUPPORTED`, `AUTHORIZED` | `READY` means all declared prerequisites are present; only an explicitly authorized synthetic invocation may transition to `AUTHORIZED`. `BLOCKED` and `UNSUPPORTED` never launch. |
| Run | `NOT_STARTED`, `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED`, `CLEANUP_REQUIRED`, `CLEANED` | `SUCCEEDED` means configured probe steps exited successfully, not that the gate or a general security claim passed. Any failed or interrupted cleanup remains `CLEANUP_REQUIRED` until absence is observed. |
| Evidence | `INCOMPLETE`, `COMPLETE_BOUNDED`, `STALE`, `CONFLICTED` | Completeness binds source, workflow, policy, provider run, workload image, runtime identity, outcomes, and cleanup. Conflicting runner release metadata is explicitly `CONFLICTED` for reproducibility claims even when other bounded observations are usable. |
| Review | `NOT_REVIEWED`, `FINDINGS_OPEN`, `PASS_BOUNDED`, `BLOCKED` | Only an independent reviewer can recommend `PASS_BOUNDED`; a designated owner records the gate disposition. This never means complete host isolation or general runtime support. |

State update precedence is conservative: unsupported/missing prerequisites prevent `READY`; lack of authorization prevents `QUEUED`; any test failure or uncertain cleanup prevents `SUCCEEDED`; missing/mismatched evidence prevents `COMPLETE_BOUNDED`; open blocking findings prevent `PASS_BOUNDED`. If multiple defects exist, report all discovered blockers while preserving the earliest lifecycle state that prevents the next action.

## Product-appropriate interaction traces

These examples are conceptual and non-executable. They specify the desired observable interaction if the approved runner contract is later implemented; they do not claim the present workflow exposes all these reusable states.

### CX-030-A — Declare a request and check prerequisites (J-030-01)

1. Maintainer opens the FW-030 contract and sees its scope, supported-profile status, limitations, required policy fields, and explicit statement that no application secrets/source are allowed in this synthetic pilot.
2. Maintainer supplies/selects a versioned profile and policy reference; the interface summarizes command, image digest, identity, mounts, network, secrets, resource limits, timeout, audit, cancellation, and cleanup settings without echoing secret material.
3. A preflight summary binds the request to the exact source and workflow revision. Missing runtime/capability yields `UNSUPPORTED`; malformed or absent policy yields `BLOCKED`; neither presents a run button as actionable.
4. To recover, maintainer edits a reviewed profile or provisions a supported environment, then repeats preflight. An unsupported result remains visible in history.

**Observable response contract:** `Request: BLOCKED — rootless Podman is unavailable for profile X. No workload was started. Select a separately reviewed supported profile or provision the declared prerequisite.` Do not display `Ready` on partial capability checks.

### CX-030-B — Authorize and run synthetic checks (J-030-02)

1. Before dispatch, the hosted workflow summary shows repository/ref, source SHA, workflow SHA, run attempt, synthetic image digest, no-secret/no-app-source declaration, and bounded case list.
2. The authorized operator confirms one synthetic run. The provider shows queue/start progress and stable case-level pending/running results.
3. The workflow presents each positive control, negative boundary probe, resource/timeout probe, and cleanup result as `PASS`, `FAIL`, `NOT RUN`, or `UNKNOWN`, with a concise reason and evidence locator.
4. Any setup/assertion failure marks the run `FAILED`; skipped or unknown required probes do not roll up to success. A successful run is labeled `Synthetic probe succeeded for this run`, never `host is secure` or `adapter supported`.
5. Recovery preserves the failing run ID and its cleanup result. Any correction uses a new reviewed revision and a new authorized run.

### CX-030-C — Review evidence and decide a bounded gate result (J-030-03)

1. Reviewer starts from an evidence index mapping each case to source/workflow SHA, provider run/attempt, image digest, observed host/runtime identities, policy observations, exit state, and cleanup verification.
2. Missing, stale, or mismatched references are visibly `INCOMPLETE`, `STALE`, or `CONFLICTED`; the reviewer can open bounded logs for a case without an unrestricted environment dump.
3. The reviewer compares observed results with approved requirements and threat-model exclusions. For the known runner header/environment version conflict, the screen/record keeps both values and flags reproducibility as unresolved.
4. The independent reviewer records findings, criteria, evidence, and a bounded recommendation. The accountable owner separately records gate disposition. A green CI badge is shown as CI status only, separate from feasibility/security review.

### CX-030-D — Unsupported or unavailable environment (J-030-04)

1. Preflight identifies the exact unavailable prerequisite and whether it is profile incompatibility, runtime absence, permission failure, or provider outage.
2. Request state becomes `UNSUPPORTED` or `BLOCKED`; output states that no workload ran and no unsandboxed fallback occurred.
3. The operator receives a safe recovery route: select a separately reviewed profile, restore a missing prerequisite, or wait/retry after provider recovery. The old attempt remains linkable and cannot be converted to a pass by changing its label.

### CX-030-E — Interrupt and recover cleanup (J-030-05)

1. Operator requests cancellation; progress indicates stop requested and then whether graceful stop or forced termination was observed.
2. Cleanup reports container/network/temp-resource status independently. If any resource is present or its absence cannot be verified, state is `CLEANUP_REQUIRED`, run is not successful, and new workload dispatch is withheld.
3. After the approved cleanup path verifies absence, the record transitions to `CLEANED` while retaining the original `CANCELLED` or `FAILED` result and cleanup history.
4. Persistent cleanup failure is escalated with exact resource identifiers and operator instructions; no blanket host-clean claim is shown.

### CX-030-F — Initialize a project without launching workloads (J-030-06)

1. Initializer validates inputs and reports files created or an actionable generation error.
2. It does not request runtime authorization, start a container, or imply later commands are sandboxed.
3. Runtime adapter prerequisites, if later documented, are informational and separate from file generation. A generation failure can be corrected and rerun without leaving an untracked workload.

## Full-scope critique checklist and finding register

The independent critique must walk all six traces and all four state axes, using the following dimensions: status visibility; real-world match; operator control; consistency across repository/CLI/Actions/review; error prevention; recognition of exact revision and evidence; flexibility without bypass; recovery; help; content clarity; trust calibration; and cross-surface handoff. Static text review cannot establish runtime accessibility, screen-reader behavior, provider UI rendering, or device behavior; route those to applicable implementation checks.

| Finding ID | Location / evidence | Severity | User/operator impact | Recommendation | Owner decision needed | Disposition / rerun evidence |
| --- | --- | --- | --- | --- | --- | --- |
| None recorded before independent critique. | Full artifact, all CX-030-A–F traces and state axes. | — | — | Record stable IDs for each actionable issue; do not convert scores into passes. | No owner risk acceptance presumed. | Pending full-scope independent critique. |

## Gate evidence and next action

- **GCX-01:** Freeze this target, six journey IDs, P-01–P-06 applicability from FRAMEWORK-COVERAGE-003, artifact blob, source commit, and exclusions. No visual target exists.
- **GCX-02:** Record `manual tool-neutral review`, reviewer, date, exact source and artifact blobs, full trace/state scope, evidence locations, method limitations, and findings.
- **GCX-03:** Resolve every blocking finding in a coherent revision and rerun the complete six-journey scope; retain stable IDs and fix evidence.
- **Required closeout:** Independent full-scope review, artifact validation, and exact-revision Verify Pipeline. CI does not replace the interaction critique.
- **Next gate if passed:** G-ARCH, which must still resolve architecture/trust/host boundary questions before implementation; no implementation is authorized by this artifact.
