---
id: FRAMEWORK-ADV-046
type: adversarial-review
title: FW-TASK-030 conmon timeout semantics review
status: approved
version: 0.1
created: 2026-10-26
updated: 2026-10-26
reviewed-artifact: .github/workflows/fw030-runtime-probe.yml
reviewed-version: 39bab5b13ae84b5bf30ebd0fa3976409eda30196
related-artifacts: FRAMEWORK-FEASIBILITY-011, FRAMEWORK-BACKLOG-001, FRAMEWORK-ADV-045, DECISION-034
---

# FRAMEWORK-ADV-046 — FW-TASK-030 conmon timeout semantics review

## Scope and method

Independent reviewer `/root/fw029_independent_review` inspected `.github/workflows/fw030-runtime-probe.yml` at exact revision `39bab5b13ae84b5bf30ebd0fa3976409eda30196`, workflow SHA-256 `d85e6bcbbac476c032d2e5af00e7542b8342dd339b92638654aa817606cea889`. Scope was limited to the version-specific timeout assertion, preservation of the timeout boundary checks, and any effect on other controls. The reviewer did not edit, execute, or dispatch the workflow.

## Review result — NEEDS-CHANGES

The timeout checks require a two-second configured timeout, nonempty start/finish timestamps, stopped/exited state, exit code `-1`, no OOM kill, Podman process exit `255`, elapsed time from two through ten seconds, and post-removal absence. These checks match the stated timeout boundary.

The version gate uses `conmon --version` from `PATH`, which does not prove it is the binary Podman selected through its configured conmon search path. Its prefix pattern also accepts versions such as `2.1.100`. Because the gate controls whether the version-specific `-1`/`255` result is accepted, bind the check to Podman's selected conmon path/version and require an exact version delimiter before relying on this interpretation. The reviewer confirmed the v2.1.10 source path sends SIGKILL while leaving the local exit status at `-1`; the diff is otherwise confined to the timeout block.

Verify Pipeline [40261728780](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40261728780) passed all three standard CI jobs on the exact candidate; optional probes were skipped on push. Per the owner checkpoint, no further correction or runtime retry was made after this review.
