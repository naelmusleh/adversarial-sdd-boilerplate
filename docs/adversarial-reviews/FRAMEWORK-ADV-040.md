---
id: FRAMEWORK-ADV-040
type: adversarial-review
title: FW-TASK-030 temporary runtime workflow review
status: revision-required
version: 0.2
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

## Disposition

Do not dispatch either reviewed candidate. The latest correction is pending an exact-revision independent review. This review remains `revision-required`; no hosted probe ran, and no G-FEAS pass, runtime support, or isolation claim is established.
