---
id: FRAMEWORK-CX-003
type: framework-cx
title: FW-TASK-030 runner request and evidence interaction contract
status: draft
version: 0.2
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
| Request readiness | `DRAFT`, `READY`, `BLOCKED`, `UNSUPPORTED` | `READY` means all declared prerequisites are present and the request is awaiting authorization; it never means authorized or running. `BLOCKED` and `UNSUPPORTED` never launch. |
| Authorization | `NOT_AUTHORIZED`, `AUTHORIZED` | An accountable operator explicitly authorizes one synthetic invocation after reviewing the exact request summary. Authorization is separate from readiness and does not imply that a run started. |
| Execution | `NOT_STARTED`, `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED` | This axis preserves the terminal execution outcome permanently. `SUCCEEDED` means configured probe steps exited successfully, not that the gate or a general security claim passed. |
| Cleanup | `NOT_REQUIRED`, `PENDING`, `REQUIRED`, `CLEAN` | Cleanup state is independent of execution outcome. `REQUIRED` means absence is unverified or a resource remains; only observed absence permits `CLEAN`. Cleanup can never replace `FAILED` or `CANCELLED`. |
| Evidence | `INCOMPLETE`, `COMPLETE_BOUNDED`, `STALE`, `CONFLICTED` | Completeness binds source, workflow, policy, provider run, workload image, runtime identity, outcomes, and cleanup. Conflicting runner release metadata is explicitly `CONFLICTED` for reproducibility claims even when other bounded observations are usable. |
| Review | `NOT_REVIEWED`, `FINDINGS_OPEN`, `PASS_BOUNDED`, `BLOCKED` | Only an independent reviewer can recommend `PASS_BOUNDED`; a designated owner records the gate disposition. This never means complete host isolation or general runtime support. |

State update precedence is conservative: unsupported/missing prerequisites prevent `READY`; `READY` plus `NOT_AUTHORIZED` prevents `QUEUED`; any test failure prevents `SUCCEEDED`; uncertain cleanup sets cleanup to `REQUIRED` without changing the execution outcome; missing/mismatched evidence prevents `COMPLETE_BOUNDED`; open blocking findings prevent `PASS_BOUNDED`. If multiple defects exist, report all discovered blockers while preserving each axis independently.

## Product-appropriate interaction traces

These examples are conceptual and non-executable. They specify the desired observable interaction if the approved runner contract is later implemented; they do not claim the present workflow exposes all these reusable states.

### CX-030-A — Declare a request and check prerequisites (J-030-01)

1. Maintainer opens the FW-030 contract and sees its scope, supported-profile status, limitations, required policy fields, and explicit statement that no application secrets/source are allowed in this synthetic pilot.
2. Maintainer supplies/selects a versioned profile and policy reference; the interface summarizes command, image digest, identity, mounts, network, secrets, resource limits, timeout, audit, cancellation, and cleanup settings without echoing secret material.
3. A preflight summary binds the request to the exact source and workflow revision. Missing runtime/capability yields `UNSUPPORTED`; malformed or absent policy yields `BLOCKED`; neither presents a run button as actionable. `READY` explicitly means preflight passed but authorization has not been granted.
4. Only after reviewing that exact summary does an accountable operator authorize one run. The interface then shows `Authorization: AUTHORIZED` and makes the single-run dispatch action available. Reauthorization is required for a different source or policy revision.
5. To recover, maintainer edits a reviewed profile or provisions a supported environment, then repeats preflight. An unsupported result remains visible in history.

**Observable response contract:** `Preflight: UNSUPPORTED — rootless Podman is unavailable for profile X. Authorization: NOT_AUTHORIZED. Execution: NOT_STARTED. No workload was started. Select a separately reviewed supported profile or provision the declared prerequisite.` Do not display `READY` on partial capability checks or conflate ready with authorized.

### CX-030-B — Authorize and run synthetic checks (J-030-02)

1. Before authorization, the hosted workflow summary shows repository/ref, source SHA, workflow SHA, synthetic image digest, no-secret/no-app-source declaration, and bounded case list. The readiness and authorization indicators are separate.
2. An accountable operator authorizes one synthetic run against that exact summary. The provider shows queue/start progress and stable case-level pending/running results.
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
2. Cleanup reports container/network/temp-resource status on its own axis. If any resource is present or its absence cannot be verified, cleanup becomes `REQUIRED`, execution remains `CANCELLED` or `FAILED`, and new workload dispatch is withheld.
3. After the approved cleanup path verifies absence, cleanup transitions to `CLEAN`; the original execution result remains `CANCELLED` or `FAILED` and the complete cleanup history remains visible.
4. Persistent cleanup failure is escalated with exact resource identifiers and operator instructions; no blanket host-clean claim is shown.

### CX-030-F — Initialize a project without launching workloads (J-030-06)

1. Initializer validates inputs and reports files created or an actionable generation error.
2. It does not request runtime authorization, start a container, or imply later commands are sandboxed.
3. Runtime adapter prerequisites, if later documented, are informational and separate from file generation. A generation failure can be corrected and rerun without leaving an untracked workload.

## Full-scope critique checklist and finding register

The independent critique must walk all six traces and all four state axes, using the following dimensions: status visibility; real-world match; operator control; consistency across repository/CLI/Actions/review; error prevention; recognition of exact revision and evidence; flexibility without bypass; recovery; help; content clarity; trust calibration; and cross-surface handoff. Static text review cannot establish runtime accessibility, screen-reader behavior, provider UI rendering, or device behavior; route those to applicable implementation checks.

| Finding ID | Location / evidence | Severity | User/operator impact | Recommendation | Owner decision needed | Disposition / rerun evidence |
| --- | --- | --- | --- | --- | --- | --- |
| CX030-01 | v0.1 state table and CX-030-A preflight/authorization transition. | P2 | `READY` could be mistaken for permission to dispatch. | Separate readiness from one-run authorization and gate dispatch on both. | No. | Resolved in v0.2 with distinct `Request readiness` and `Authorization` axes; only READY + AUTHORIZED enables dispatch. Requires full-scope rerun. |
| CX030-02 | v0.1 Run axis and CX-030-E cleanup recovery. | P1 | Cleanup completion could overwrite a failed/cancelled execution outcome. | Separate terminal execution result from cleanup state and preserve both across recovery. | No. | Resolved in v0.2 with independent `Execution` and `Cleanup` axes; cleanup `CLEAN` does not change `FAILED`/`CANCELLED`. Requires full-scope rerun. |

## Gate evidence and next action

- **GCX-01:** Freeze this target, six journey IDs, P-01–P-06 applicability from FRAMEWORK-COVERAGE-003, artifact blob, source commit, and exclusions. No visual target exists.
- **GCX-02:** Durable review record must identify `manual tool-neutral review`, evaluator, date, exact source and artifact blobs, full trace/state scope, evidence locations, method limitations, and findings. See linked adversarial review disposition once complete.
- **GCX-03:** Resolve every blocking finding in a coherent revision and rerun the complete six-journey scope; retain stable IDs and fix evidence.
- **Required closeout:** Independent full-scope review, artifact validation, and exact-revision Verify Pipeline. CI does not replace the interaction critique.
- **Next gate if passed:** G-ARCH, which must still resolve architecture/trust/host boundary questions before implementation; no implementation is authorized by this artifact.
