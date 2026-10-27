---
id: FRAMEWORK-ADV-065
type: adversarial-review
title: FW-TASK-031 passive Actions collector implementation review
status: approved
version: 0.1
created: 2026-10-27
updated: 2026-10-27
reviewed-artifact: FRAMEWORK-CONTRACT-032
reviewed-version: 1.0
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, DECISION-038, DECISION-039, FRAMEWORK-FEASIBILITY-014, FRAMEWORK-ARCHITECTURE-006, FRAMEWORK-CONTRACT-032
---

# FRAMEWORK-ADV-065 — FW031-IMPL-03 independent review

## Frozen target and reviewer

- **Gate:** G-IMPL for FW031-IMPL-03 under DECISION-039; task-wide acceptance remains incomplete.
- **Reviewer:** Independent read-only reviewer `/root/fw031_impl03_review`.
- **Review date:** 2026-10-27.
- **Final candidate:** `fa020dd799cd99e7973eb0008201526b0c66496a` on `codex/fw031-greq`.
- **Reviewed files:** `scripts/fw031_actions_collector.py`; `tests/test_fw031_actions_collector.py`; FRAMEWORK-CONTRACT-032 v1.0 and `actions-run-job-evidence-v1.schema.json`.
- **Method:** Exact-revision source and fixture review via GitHub connector; no edits or publication by reviewer.

## Review rounds and dispositions

Round 1 reviewed candidate `ae7556a7db2c04d9121fd0d1bdbb3b32c32eb67a` and returned NEEDS-CHANGES:

| Finding | Severity | Observation | Disposition |
| --- | --- | --- | --- |
| FW031-IMPL-03-REV-01 | P1 | Records built through injected synthetic transports were emitted with `fixture_only=false`, which could make the fixture appear observed. | Corrected: any injected transport automatically marks generated records `fixture_only=true`; the test asserts this and the evidence validator accepts the resulting record only as a fixture. |
| FW031-IMPL-03-REV-02 | P2 | GitHub REST run `path` combines the workflow file path and a ref suffix; the collector had stored the combined string as `workflow_path`. | Corrected: the collector separates the path component and keeps a full workflow ref unavailable unless a distinct field is actually returned. The source remains partial and states `workflow_ref-unavailable`. |

The independent full-scope rerun on exact candidate `fa020dd799cd99e7973eb0008201526b0c66496a` confirmed both findings resolved and returned PASS. No additional code-contract issue was reported.

## Review result and evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Read-only route and least privilege | PASS within code scope | Only HTTPS GET requests to exact `api.github.com`; API origin and repository identity are checked; redirects are rejected to prevent credential forwarding. A caller-supplied token is never logged or persisted. |
| Bounded retrieval and exact identity | PASS within fixture scope | Maximum five job pages of 100 rows; at most three retries; per-request timeout at most 30 seconds; exact repository, run, attempt-specific endpoint, and job ID binding; mismatched jobs are excluded and reported partial. |
| Redaction and data minimization | PASS within code scope | Token-shaped values in metadata are scrubbed; raw API bodies/errors are not emitted; only projected fields and a digest of returned response bytes are output. No logs, workflow artifacts, or persistent storage are retrieved. |
| Honest evidence states | PASS within contract scope | Unavailable workflow/executed revisions, timeout configuration, cancellation request, workload termination, and direct measurements remain unknown/unavailable; a successful host conclusion does not imply workload termination or budget compliance. |
| Synthetic behavior | PASS | Injected test transport outputs are fixture-only; focused suite passed 30 tests (10 collector and 20 contract tests). |
| Private-repository acquisition | NOT VERIFIED | No eligible private repository was available through the connected repository search, and no scoped token was supplied. Public/synthetic checks do not satisfy the private-access criterion. |

## Exact-revision hosted verification

Verify Pipeline push run [40508980927](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40508980927) and PR run [40508989590](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40508989590) passed Metadata & Artifact Audit, Initializer Regression Gate, and TypeScript Static Code Analysis at exact candidate `fa020dd799cd99e7973eb0008201526b0c66496a`. Optional FW-029 and FW-030 probes were skipped.

## Gate disposition and limits

- Independent code review: **PASS** for the bounded implementation and synthetic fixtures.
- G-IMPL: **IN PROGRESS**, because required private-repository access evidence is not available.
- No live API collection, private authorization, token scope, repository setting, timeout configuration, cancellation, workload termination, spend/resource measurement, gate mutation, or profile adoption is established by this review.
- Next action: the owner supplies the private repository identity and an Actions-read-only credential or enables an existing connection with that repository’s Actions-read permission. Then run the collector against one named run/attempt and record the exact output and limitations. Keep the token outside logs, files, and PR content.
