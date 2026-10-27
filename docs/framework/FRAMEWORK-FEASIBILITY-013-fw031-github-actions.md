---
id: FRAMEWORK-FEASIBILITY-013
type: feasibility-register
title: FW-TASK-031 GitHub Actions hosted-runner capability probe
status: approved
version: 0.2
created: 2026-10-26
updated: 2026-10-26
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-012, FRAMEWORK-ARCHITECTURE-005, FRAMEWORK-CONTRACT-031, DECISION-036, DECISION-037
---

# FRAMEWORK-FEASIBILITY-013 — FW-TASK-031 GitHub Actions hosted-runner capability probe

## Scope and boundaries

This is a bounded, read-only capability probe requested by the owner after FW031-IMPL-01. It evaluates GitHub-hosted Actions as a possible execution profile for FR-FW-038–040. It does not select or adopt GitHub Actions, implement an adapter, change workflow configuration, set a budget threshold, exercise real cancellation, query private billing data, or authorize application use, credentials, merge, or deployment. It makes no claim that the observed CI jobs were agent executions.

The probe examined workflow and job metadata, logs, and timing for the successful Verify Pipeline run [40328119676](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40328119676), whose head was `ca0e8a40871a3e23ba4cafee1cf7ec377dc6fb6f`. The repository was public at observation time. Evidence was observed on 2026-10-26 and is specific to this run and the repository workflow at that commit.

## Observed run evidence

- The workflow declares three required parallel jobs with `runs-on: ubuntu-latest`; no job or step `timeout-minutes` is set in the current Verify Pipeline. The run started at 13:09:13Z and completed at 13:09:50Z (`run_duration_ms: 37000`).
- GitHub's job API returned job start/end timestamps and temporary runner names for each required job. Their observed durations were 32 seconds (Metadata & Artifact Audit), 8 seconds (Initializer Regression Gate), and 27 seconds (TypeScript Static Code Analysis). These are job wall-clock durations from one short CI run, not a general agent budget measurement.
- The Metadata & Artifact Audit log identified hosted image `ubuntu-24.04`, image version `20261012.334.1`, Ubuntu `24.04.5`, and runner version `2.338.0`. This is time-bound image evidence, not a stable runner pin or proof about later runs.
- The run timing API returned `run_duration_ms: 37000`, but `billable.UBUNTU.total_ms` and all job `duration_ms` values were zero for this public repository run. GitHub documents standard hosted-runner use in public repositories as free. This output therefore provides no monetary spend measurement.

## Capability findings

| Capability | Finding for this candidate | Classification and safe boundary |
| --- | --- | --- |
| Workflow/run identity | GitHub contexts define repository-scoped `run_id`, `run_number`, and `run_attempt`; the job API exposes workflow job IDs. | **Supported at workflow/job level.** A workflow rerun attempt is identifiable; these IDs do not identify internal agent/tool invocations or prove nested-work ownership. |
| Elapsed wall time | The run and job API expose start/completion times. Workflow syntax supports a per-job timeout; the documented default is 360 minutes and the maximum is 360. | **Available at workflow/job level; not configured as a short budget in the observed workflow.** Timestamps can support elapsed-time reporting for one run/job, but not per-agent aggregation without explicit instrumentation. |
| Retry/iteration counts | `run_attempt` distinguishes GitHub workflow reruns. | **Partial.** It does not count an agent's internal retries, model turns, or command retries. Those remain unknown absent coordinator instrumentation. |
| Tool invocations | The workflow and observed run expose no Codex/MCP tool-call counter. | **Unavailable in the current profile.** Do not substitute steps, API requests, or log lines as tool-call counts. |
| CPU/memory/resource use | The observed run API and workflow contain no per-run CPU or memory measurements. No sampling instrumentation was exercised. | **Unknown.** Do not claim a resource ceiling or use local process samples as whole-run enforcement without a separate scoped probe. |
| Nested-run accounting | The observed run has independent job IDs; the workflow API can list referenced reusable workflows. Neither represents child-agent parent IDs or assigns child tool usage to one root owner. | **Unavailable for agent-tree accounting in the current profile.** Root aggregation and double-count prevention need an explicit coordinator and tested lineage contract. |
| Cancellation and stop | GitHub documents job/step timeouts and workflow cancellation. During cancellation, the runner sends interrupt signals, then termination signals, and kills the step process tree if it still runs; server-side cancellation can take up to five minutes, and job conditions can allow jobs to continue. | **Documented workflow/step control; not tested here for an agent process tree.** A cancellation request alone is not observed termination. The current Verify Pipeline has no short timeout configured. |
| Monetary spend | This public run had zero billable milliseconds. GitHub-hosted standard runner use is free in public repositories. The per-run usage endpoint is documented as closing down; private-repository usage reports runner time, not a per-agent monetary amount. | **Unavailable for numeric spend in this candidate.** Keep spend `unknown`; do not infer dollars from elapsed time, tools, retries, or runner minutes. |

## Feasibility result and next dependency

GitHub Actions provides a plausible boundary for workflow/job IDs, rerun attempts, elapsed timestamps, configurable job timeouts, and host-level cancellation. The current framework workflow does not capture a complete FW-031 capability record, configure a short time budget, count agent tool calls or internal retries, establish child-agent accounting, or measure monetary spend. A workflow-level timebox could be explored as a narrow advisory/control profile, but this probe does not adopt that profile or establish that it satisfies FW-TASK-031.

**Result:** Evidence narrows several previous unknowns for workflow/job-level timing and cancellation surfaces. Tool calls and nested agent accounting remain unavailable in the current profile; resource metrics and termination for a future agent workload remain unknown; spend remains unknown. Slices B–D in FRAMEWORK-ARCHITECTURE-005 stay held. No threshold, budget policy, controller, or host profile is selected.

**Independent review:** Reviewer `/root/fw029_independent_review` found no actionable findings at exact published candidate `934ee58f629af667341532eb6b95c8e1724e657e` on `codex/fw031-greq`. The reviewer confirmed that the claims stay at workflow/job level and do not transfer prior FW-029/FW-030 results into adoption evidence.

**Next dependency:** Before implementation of advisory accounting, the owner must select whether the intended profile is limited to GitHub workflow/job level and define which counters may be treated as supported, advisory, or unavailable. Any process-tree enforcement or monetary spend remains separately blocked on a tested controller or authoritative meter.

## Sources

- Repository workflow: [Verify Pipeline at the observed revision](https://github.com/naelmusleh/adversarial-sdd-boilerplate/blob/ca0e8a40871a3e23ba4cafee1cf7ec377dc6fb6f/.github/workflows/verify-pipeline.yml).
- Observed job metadata: [run 40328119676](https://api.github.com/repos/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40328119676/jobs); [run timing response](https://api.github.com/repos/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40328119676/timing).
- GitHub Actions [contexts reference](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts) for run IDs/attempts and runner context; [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) for timeout limits; [workflow cancellation reference](https://docs.github.com/en/enterprise-cloud@latest/actions/reference/workflows-and-actions/workflow-cancellation) for cancellation behavior.
- GitHub [workflow run usage API](https://docs.github.com/en/rest/actions/workflow-runs#get-workflow-run-usage) for per-run timing/billable fields and its endpoint closing-down notice; [billing and usage](https://docs.github.com/en/actions/concepts/billing-and-usage) for public and private runner billing behavior.
