---
id: FRAMEWORK-ADV-040
type: adversarial-review
title: FW-TASK-030 temporary runtime workflow review
status: approved
version: 0.5
created: 2026-10-25
updated: 2026-10-25
reviewed-artifact: .github/workflows/fw030-runtime-probe.yml
reviewed-version: candidate at 7eee540696564326976a04cd6c5fc9e3dea00128
related-artifacts: FRAMEWORK-FEASIBILITY-011, FRAMEWORK-BACKLOG-001, FRAMEWORK-ADV-039, DECISION-034
---

# FRAMEWORK-ADV-040 — FW-TASK-030 temporary runtime workflow review

## Scope and method

Independent reviewer `/root/fw029_independent_review` inspected the exact workflow candidate at commit `7eee540696564326976a04cd6c5fc9e3dea00128` read-only. The workflow was not dispatched; no hosted workload ran. Review scope was false-pass resistance and truthful evidence for the bounded synthetic G-FEAS pilot, not runtime adoption, adapter implementation, complete host isolation, or release.

## Review round 1 — NEEDS-CHANGES

The reviewer found the permissions, caller/ref restriction, lack of checkout/secrets/actions/artifact upload, immutable image digest, rootless requirement, and claim boundaries sound. Four evidence gaps blocked execution:

1. **Network false positive:** The negative request targeted unroutable `192.0.2.1`; its failure did not show that the workload network was disabled. Add a reachable local synthetic endpoint and prove it responds from a network-enabled control client before testing that the identical endpoint is unreachable from the isolated workload and child process.
2. **Mount false positive:** The host input directory was mode `0700`, and container UID mapping was not established. Path and read-only failures could result from inability to traverse the mount. Make the synthetic fixture readable and first require a successful fixture read before negative path/write cases.
3. **Outcome misclassification:** Timeout, resource, and cleanup probes treated arbitrary nonzero command status as expected success. Require evidence the container started, then assert the specific expected timeout state/exit, explicit tmpfs exhaustion diagnostic, and running-container refusal message before cleanup. Check missing-target cleanup for a specific not-found diagnostic.
4. **Unverified policy/reporting:** The workflow reported one CPU without inspecting its configured value or the dropped-capability/no-new-privileges settings, and omitted required storage/network backend identities. Inspect those settings and emit the backend values, or narrow the claim.

The reviewer also requested labeling the command rejection as a probe-harness guard, not adapter evidence. The result `probe_guard_denied_command` is not evidence that a framework adapter exists.

## Follow-up on corrected candidate

At exact commit `9632a055a914f4b9e37aea9eb7561eaeac803807`, the independent reviewer confirmed that findings 1–4 above are corrected and that command rejection is labeled as harness-only evidence. The reviewer identified one remaining cleanup false-pass: the exit handler ignored container/network removal failures and did not verify the temporary directory was absent. A corrective patch now makes cleanup failures observable, checks all named containers and the network are absent, and verifies temporary-file removal. This candidate has not yet been reviewed.

## Third review — NEEDS-CHANGES

Owner authorized a third consecutive independent review. Reviewer `/root/fw029_independent_review` inspected the workflow at `cf2dbaee6983ba0981eba5dbb0db5b85a5628d7a` (same workflow blob at doc-only HEAD `5dced2007f8b4a924aafd0bb5fba146fbb8b16a5`). Earlier network, mount-readability, outcome-classification, and policy-reporting findings remain corrected. One cleanup false-pass remains: `podman container exists` and `podman network exists` checks treat every nonzero result as absence. Podman differentiates not-found (exit 1) from query/storage/backend errors (exit 125); the latter could therefore incorrectly produce `final_cleanup=PASS`. The reviewer requires accepting only documented presence/absence exit statuses and treating other statuses as cleanup failures. No workflow was dispatched or executed.

## Disposition

Do not dispatch the workflow. The third review returned NEEDS-CHANGES. Per the repository's limit on more than two consecutive adversarial loops, further correction/review work requires a new owner checkpoint. The task is recorded blocked in the backlog. No hosted probe ran, and no G-FEAS pass, runtime support, or isolation claim is established.

## Owner authorization and fourth review candidate

After the third review, the owner explicitly authorized one bounded correction and independent review cycle. The workflow now accepts only exit status 0 (resource present) or 1 (not found) from Podman container/network existence queries; all other statuses are recorded as cleanup failures. It repeats the same status classification after removal before claiming absence. Independent reviewer `/root/fw029_independent_review` reviewed exact workflow commit `bccc4764036c742770fea4ca87108ce3f57042b7` and returned PASS. The reviewer confirmed statuses are classified as 0=present, 1=not found, and all other results fail cleanup; post-removal status checks use the same rules; temporary directory removal is checked; and prior findings remain corrected. Verify Pipeline [40248535982](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40248535982) passed on the exact workflow commit. This approves the workflow for the already authorized disposable pilot only; it does not itself establish runtime support or isolation.
