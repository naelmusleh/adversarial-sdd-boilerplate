---
id: FRAMEWORK-CX-005
type: cx-contract
title: FW-TASK-031 slice B operator and reviewer interaction contract
status: draft
version: 0.2
created: 2026-10-26
updated: 2026-10-26
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-013, FRAMEWORK-FEASIBILITY-014, FRAMEWORK-COVERAGE-005, DECISION-038, WORKFLOW-CX-001, GATE-CATALOG-001, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-CX-005 — FW-TASK-031 slice B operator and reviewer interaction contract

## Scope and interaction target

This conceptual G-CX interaction contract covers FW-TASK-031 slice B and FR-FW-041–043 under DECISION-038. The target is the framework maintainer, an authorized Actions run operator, and an independent reviewer working with exact run/job evidence. It is a nonvisual interaction trace because the approved scope defines a governance/profile contract, not an end-user product UI.

The examples below use placeholder labels such as `<run-id>` and state names, not asserted live measurements. This contract does not define executable CLI commands or API routes and does not claim that current tooling emits the described records. GitHub Actions remains a candidate profile, not an adopted production host. Private job collection and timeout configuration remain conditional; exact workload termination is unverified and blocked pending a separately authorized synthetic workload test. Tool calls, agent-internal retries, nested-agent accounting, CPU/memory, and spend remain unknown unless a future source directly measures them with documented provenance and scope. No implementation, workflow/permission change, threshold, meter, application use, or deployment is authorized.

## Actors and authority boundaries

| Actor | Decision job | Authority boundary |
| --- | --- | --- |
| Framework maintainer | Inspect the versioned profile definition and determine whether requested evidence is complete and correctly scoped. | Cannot make unsupported measurements available or adopt the profile by documenting it. |
| Authorized run operator | Request retrieval or cancellation only through an authorized workflow/host procedure and record the result. | A request does not establish a host result or workload termination. No new permission is granted here. |
| Independent reviewer | Compare source identity, evidence provenance, state distinctions, and claims against FR-FW-041–043. | Review disposition is not profile adoption, owner authorization, or gate PASS by itself. |
| Repository owner / permission owner | Decide whether to grant future required access or approve a later implementation/profile decision. | This contract does not make that decision or alter repository settings. |

## Frozen journey and interaction traces

| Journey | Start and actor action | System response / decision point | Success and destination | Back, cancel, interruption, and recovery | Required information and limits |
| --- | --- | --- | --- | --- | --- |
| J-031B-01 Bind run/job and revisions | Maintainer selects one source record for a repository/workflow/run. | Present repository, workflow identity, run ID, `run_attempt`, job ID, source revision, and provenance for each field. Distinguish workflow revision, head/event revision, and executed revision when supplied. Reject missing or conflicting tuple members; never complete them from another run. | Reviewer sees a single well-bound record, or an explicit incomplete/unknown state with the missing fields identified. | If retrieval is interrupted, retain the exact source reference and partial record; restart only against the same selected run or begin a separately identified record. | `run_attempt` means Actions rerun only. No claim about model turns, agent iterations, commands, or tool calls. |
| J-031B-02 Interpret timestamps and reruns | Operator or reviewer opens a well-bound run/job evidence record. | Display each timestamp with source field, run/job scope, and observation meaning. Derive an interval only when inputs are compatible and provenance is present. Explain that overlapping jobs are not naively summed. | A source-backed interval is labeled by scope; missing/inconsistent times remain `unknown`/`unavailable`. | Preserve received timestamp values and errors; reacquire missing evidence only from the same run/job and authorized source. | Elapsed time is not a proxy for spend, resource use, agent retries, or tool-call count. |
| J-031B-03 Review configured timeout and job outcome | Maintainer compares the exact workflow revision with a job result. | Show a declared `timeout-minutes` value separately from job conclusion/timestamps. Ask whether the source actually reports a timeout outcome; configuration alone is not proof that a timeout fired or stopped a workload. | Configuration and observed outcome are shown as separate facts; absent evidence is `unknown`. | If the workflow source or outcome is unavailable, keep the distinction unresolved and request exact same-revision evidence. Never retrofit a later timeout into an earlier run. | No numeric threshold is selected. Current Verify Pipeline settings do not establish FW-031 timeout enforcement. |
| J-031B-04 Request cancellation and assess termination | Authorized operator records a cancellation request for an identified run/job. | Show request actor/time, host-reported terminal conclusion, and exact workload/process-tree observation as separate fields. A terminal Actions job status is not proof that every workload child process stopped. | The result may state `requested`, host `cancelled`/other terminal outcome, and workload termination `unknown` independently. A hard-stop claim requires a separately observed exact workload boundary. | If the request response or workload observation is lost, preserve the request and report `unknown`; route to the authorized operator. Retry only under the host procedure; retain each attempt. | No workload/cancellation test is performed or approved by this contract. No claim of process-tree control. |
| J-031B-05 Report metrics or unknown | Reviewer inspects a proposed metric value. | For each value show source, units, scope, interval, and provenance. If the source does not directly measure that metric, reject the proposed numeric value and show `unknown`/`unavailable` with reason. | Only directly measured, scoped values remain numeric. Tool calls, internal retries, nested agents, CPU/memory, and spend stay unknown/unavailable without direct evidence. | Preserve the attempted claim and diagnostic; request a future source decision or evidence without substituting another counter. | Steps, logs, elapsed time, run attempts, job counts, and public-run zero billing are forbidden proxies under FR-FW-043. |
| J-031B-06 Handle denied/degraded collection and review | Operator requests an authorized source read; reviewer checks the resulting evidence. | Present access-denied, API/service error, partial response, stale/mismatched revision, and empty response as distinct outcomes. Never turn denial or error into an empty result or numeric zero. | Complete exact-revision evidence proceeds to review; incomplete or unavailable evidence remains non-pass/unknown with the blocked claim and next action stated. | Preserve partial evidence and retrieval diagnostics; owner may decide whether to provide approved access or another exact source. Resume review only after binding new evidence to its source revision. | Private job collection may require Actions-read access; the current workflow permission set does not prove that access. No permission change is made here. |

## Interaction state model and invariant

| Axis | States and user-facing meaning |
| --- | --- |
| Evidence identity | `complete`, `missing`, `conflicting`, `unavailable`; complete means one internally consistent repository/workflow/run/attempt/job/source-revision binding. |
| Revision provenance | `workflow-revision`, `head-revision`, `executed-revision`, `unknown`; labels identify what each source value means. |
| Timing | `observed` with source/scope/interval, `partial`, `inconsistent`, `unavailable`; no inferred cross-record completion. |
| Timeout | `configured`, `observed-timeout`, `other-outcome`, `unknown`; configuration is not an observed stop. |
| Cancellation | `not-requested`, `requested`, `host-terminal`, `workload-termination-observed`, `failed`, `unknown`; each stage remains independently evidenced. |
| Measurement | `directly-measured`, `unknown`, `unavailable`, `rejected-proxy`; a number requires direct scoped provenance. |
| Authorization / access | `not-requested`, `pending`, `authorized`, `denied`, `expired`, `unknown`; these describe authority to retrieve or request an action only. |
| Retrieval / evidence | `not-started`, `complete`, `partial`, `degraded`, `unavailable`, `stale`, `conflicting`; these describe collection and source quality, independent of review. |
| Reviewer disposition | `not-reviewed`, `findings`, `pass-within-scope`, `inconclusive`; applies only to the exact evidence subset actually reviewed. |
| Owner / gate decision | `not-decided`, `pending`, `authorized`, `denied`, `in-progress`, `pass`, `blocked`; only the applicable accountable owner or gate record can set these states. They are not inferred from access, retrieval, or reviewer states. |

**Combination rules:** Access denial prevents a new retrieval attempt but does not erase already captured evidence. `partial`, `degraded`, `unavailable`, `stale`, or `conflicting` evidence can coexist with `findings` or `inconclusive` review for the available subset; it cannot support a reviewer PASS for a claim requiring the missing portion. Reviewer `pass-within-scope` is not an owner authorization or gate PASS. Owner authorization is separate from gate state; only the canonical gate record determines gate disposition. CI success establishes only its configured checks for the exact revision.

**Invariant:** Run identity binds the evidence; source-revision labels preserve provenance; configuration is distinct from runtime outcome; cancellation request is distinct from terminal host state and observed workload termination; missing measurements remain unknown; and neither a successful review nor CI run adopts a profile or enables implementation.

## Information hierarchy, diagnostics, and sample response

When presenting evidence, show (1) current result and next authorized action, (2) exact repository/workflow/run/attempt/job and source revisions, (3) timing/timeout/cancellation facts with source and scope, (4) direct measurements or explicit unknown/unavailable states, (5) missing, denied, partial, or degraded evidence, and (6) reviewer findings and any owner decision as separate records.

Illustrative, non-executable response:

```text
Evidence: partial — review cannot establish an FW-031 hard-stop result
Source: <repository>/<workflow> run <run-id>, attempt <attempt>, job <job-id>
Revisions: head=<sha>; workflow=<sha>; executed=<unknown>
Timing: job interval=<source-backed interval or unknown>
Timeout: configured=<value or unknown>; observed timeout=<unknown>
Cancellation: request=<state>; job conclusion=<state>; workload termination=unknown
Unavailable: tool calls, agent retries, nested agents, CPU/memory, spend
Next action: obtain authorized same-run evidence; do not claim process termination
```

Diagnostics must avoid echoing secrets, unrestricted logs, or application data. This example is a communication contract only; it does not represent a real run.

## Surface and applicability decisions

| Surface | Applicability | Interaction contract | Limits |
| --- | --- | --- | --- |
| Framework spec, workflow source, and evidence/gate records | Applicable | Define identity/provenance and record uncertainty, outcomes, and recovery. | Documentation does not implement collection or controls. |
| GitHub Actions run/job data and cancellation | Conditional candidate profile | May supply run/job identity, timestamps, configuration, cancellation request, and host terminal status if authorized and observed. | No permission change, adoption, timeout selection, or workload termination is established. |
| Pull request and independent review | Applicable | Inspect exact revision, review findings, CI results, blocked claims, and owner decisions separately. | Green CI is not measurement or runtime-control evidence. |
| End-user web, Android, or iOS interface | Not applicable: DECISION-038 defines a framework governance profile, with no product-facing journey. | No end-user interaction is designed. | No platform parity, rendered UI, accessibility, or product claim. |
| Other CI providers, local CLI, native execution | Not applicable to this bounded GitHub Actions slice. | No interaction path is specified. | No provider or runtime support is inferred. |
| Figma, Material Design 3, Apple HIG, visual audit | Not applicable to this nonvisual contract. | Reviewable interaction trace is the appropriate target. | No visual or accessibility evidence is claimed. |

## Method, limitations, and critique record

The interaction target is a conceptual text trace based on FRAMEWORK-COVERAGE-005 v0.1 and FRAMEWORK-FEASIBILITY-014 v0.1, using the tool-neutral G-CX procedure in WORKFLOW-CX-001 and GATE-CATALOG-001. No runtime, screenshot, browser/device capture, API invocation, or user test is represented. This static critique can assess completeness and clarity of required state communication only; it cannot prove implementation, runtime behavior, usability in practice, accessibility, latency, host permissions, workload termination, or measurement availability.

| Finding ID | Location | Severity / impact | Disposition / owner-decision need |
| --- | --- | --- | --- |
| CX031B-01 | §3, state model and combination rules | P2 — access, collection, review, and gate states were combined on one axis, obscuring coexisting states and decision authority. | Resolved in v0.2: split into four independent axes with explicit combination/precedence rules. Full six-journey and state-transition rerun required; no owner decision needed. |

**G-CX result:** Pending full-scope independent rerun for CX031B-01 and exact-revision Verify Pipeline. No unresolved finding is waived by this draft.

**Next gate:** G-ARCH after the interaction trace passes review and CI. Architecture must preserve conditional access/timeout and blocked workload termination; implementation still requires separate G-IMPL authorization.
