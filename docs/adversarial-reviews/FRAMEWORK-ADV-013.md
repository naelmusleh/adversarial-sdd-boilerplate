---
id: FRAMEWORK-ADV-013
type: adversarial-review
title: FW-TASK-020 separate-app ten-gate adversarial pilot
status: in-review
version: 1.0
created: 2026-10-21
updated: 2026-10-21
reviewed-artifact: FW-TASK-020
reviewed-version: framework revision 927fbdeee820d72ce5c008d2f81f88c02346239f
related-artifacts: FRAMEWORK-ADV-011, FRAMEWORK-ADV-012, FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-GATE-TRACEABILITY-001, FRAMEWORK-BACKLOG-001
---

# FRAMEWORK-ADV-013 — FW-TASK-020 separate-app adversarial pilot

## Scope and method

- **Purpose:** Exercise the approved ten-gate contract and app-local validator against a disposable, separate application repository using `FlagLite` only as a synthetic scenario label. No FlagLite evaluator, product requirements, services, customer data, secrets, release, or deployment were created.
- **Framework revision pinned by the pilot app:** `927fbdeee820d72ce5c008d2f81f88c02346239f` (`fix(framework): bind intent pass to owner-approved mission`). The app lock records this exact revision. The framework revision includes the G-COVERAGE platform/surface scope correction from `ee47a13792888c213b3848dc22290a7d10bad68b` and the G-INTENT mission-digest/owner-approval correction in `927fbde`.
- **Disposable app:** `/private/tmp/flaglite-fw020-pilot-v3`; initialized by `scripts/init_app_project.py`, local Git repository, no remote, and no `src/`, `services/`, or `apps/` product source directories. Synthetic fixture source baseline: `2c2efcdfc44d0cfc78fffec41b88c6b754450957`; ten in-progress gate-run records were committed at app revision `6278b103f8ef6f05245a97b019dbeda1f40dadff`.
- **Baseline result:** The pinned app-local validator accepted the 10 explicitly in-progress gate records and reported `Validated 18 artifact(s).` This is not a gate pass.
- **Harness:** `tests/test_fw020_separate_app_pilot.py` creates a new temporary app, pins the current framework revision, commits synthetic source/records in that app, then evaluates mutated copies with the app-local validator. It currently has 10 tests; fixture and mutation inputs are synthetic and the tests run against validator behavior, not a real product lifecycle. The focused harness passed 10 tests on framework revision `a62bbd539eaad919c6d54aaf34adbddf686d44bf`; its disposable app is removed at test teardown, so no app commit SHA is retained from that run.
- **Framework verification:** At revision `927fbde`, the hosted Verify Pipeline reported success for all three required checks. At revision `a62bbd539eaad919c6d54aaf34adbddf686d44bf`, local `python3 -m unittest discover -s tests -q` passed 72 tests, `python3 scripts/artifacts.py validate` reported 47 artifacts, and `git diff --check` passed. The hosted Verify Pipeline for exact revision `a62bbd539eaad919c6d54aaf34adbddf686d44bf` completed successfully: `Metadata & Artifact Audit`, `Initializer Regression Gate`, and `TypeScript Static Code Analysis` all concluded `success`.

## Adversarial cases and observed outcomes

| Attack / route | Expected outcome | Observed result and evidence | Boundary |
|---|---|---|---|
| Ten truthful `in-progress` records in an initialized app | Accept record structure without implying progress or PASS | Accepted; all ten records remained `in-progress`; app validator reported 18 artifacts | Structural baseline only |
| Free-text PASS with no criterion evidence, one attempt per gate | Reject each false PASS | All ten mutated records rejected by app validator | Does not prove semantic sufficiency of evidence a human supplies |
| Versioned invalid fixture, one per gate | Reject malformed or incomplete gate record | All ten invalid gate fixtures rejected after adapting identity and source revision to the disposable app | Most fixtures intentionally fail early on missing evidence/schema; this is not one uniquely isolated diagnostic per attack |
| Stale digest, stale source revision, cross-app identity, unsupported accepted-risk result | Reject stale/foreign/unsupported claim | All four mutations rejected | Digest/revision structural checks only |
| G-FEAS supported route | Permit an evidence-recorded supported dependency state | Synthetic supported route accepted | No technical feasibility research was performed; not real support evidence |
| G-FEAS scope reduction | Allow reduced scope to remove its now-out-of-scope dependency | Synthetic reduced-scope route accepted | No owner product decision is implied |
| G-FEAS unknown/blocked route | Keep dependent work blocked | Baseline unknown/blocked route accepted; changing unknown to unblocked rejected with `cannot leave task` | Structural dependency behavior only |
| G-FEAS conditional route | Allow explicitly bounded conditional work | Synthetic condition and safe-work boundary accepted | Does not assess whether the condition is adequate in a real project |
| G-FEAS owner risk decision on unknown dependency | Record risk without converting unknown to feasible/unblocked | Synthetic owner-risk record accepted while classification stayed unknown and dependency stayed blocked | Fixture owner identity/authority is not authenticated |
| G-COVERAGE platform substitution | Reject an Android row substituted for iOS scope | Rejected with `platform_applicability platform 'android' is outside scope.platforms`; out-of-scope journey requirement also rejected | Platform applicability judgment remains semantic |
| G-CX with no real render/capture | Keep interaction evidence explicitly unverified and gate in progress | Synthetic limitation record accepted only as `in-progress`; no rendered capture or PASS was claimed | No real user interaction or prototype was evaluated |
| G-INTENT real artifact-reference path in synthetic app | Accept only if current mission file digest is referenced and owner approval is bound to exact mission digest | Synthetic positive pass path accepted | Test owner is a fixture identity; this is not product-owner approval |
| G-INTENT forged manual observation, non-file locator, fabricated hash, no owner decision | Reject false PASS | Rejected with diagnostics requiring current `mission.md` artifact-reference evidence and accountable-owner approval bound to exact digest | Human identity remains procedural |
| G-SETUP, G-REQ, G-ARCH, G-IMPL, G-RELEASE, G-OPERATE fabricated gate-specific assertions | Reject evidence-free PASS attempts | All six mutated attempts rejected by the app-local validator | Some failures can be due to other required evidence/transition rules; no semantic claim follows |
| G-REQ reviewer labels self as independent | Reject unsupported/self-review PASS claim | Rejected by validator | Reviewer identity/context separation cannot be proven cryptographically by this schema |
| G-IMPL failed push | Reject publication/PASS when `push_result=failed` and remote/ref absent | Rejected | App had no actual remote; outage behavior is modeled, not a network outage experiment |
| Wrong platform, out-of-scope journey, invalid risk waiver, cross-app substitution | Reject invalid scope/authority | Rejected in separate app | No external identity provider was involved |

## Findings and dispositions

1. **G-COVERAGE allowed platform substitution.** The first disposable-app pilot accepted scope `ios` with applicability `android`. The validator now requires exact scope-to-applicability reconciliation and rejects missing, out-of-scope, or duplicate platform rows. Fix: `ee47a13792888c213b3848dc22290a7d10bad68b`; hosted checks passed, and the fresh pilot pinned to the later framework revision rejects the same substitution.
2. **G-INTENT accepted fabricated manual evidence.** The second pilot accepted a PASS supported only by a synthetic manual observation with a non-file locator and hash-shaped value. The validator now requires a current `mission.md` artifact-reference and exact-digest accountable-owner approval linked from every criterion. Fix: `927fbdeee820d72ce5c008d2f81f88c02346239f`; positive, forged, and mismatched paths are covered by framework tests, and the separate-app harness confirms the positive/forged boundary.
3. **Pilot initially lacked durable isolated-app regression coverage.** The result depended on temporary scripts and ephemeral app state. A committed harness now creates and validates a fresh disposable app in the framework test suite. It preserves no temporary app as a product artifact and makes the tested operations reproducible from the test suite.
4. **Explicit self-review overlap was not rejected.** An independent reviewer found that G-REQ/G-ARCH only required a reviewer marked `independent` with disclosure; an explicit `author_overlap: "same-agent"` was ignored. The validator now requires `author_overlap: "none"`, and the pilot asserts that explicit same-agent overlap is rejected. This is a declared field only; a dishonest reviewer can still misstate it, and identity remains unauthenticated.
5. **The initial harness overclaimed negative coverage.** The independent reviewer found that invalid-fixture cases removed upstream records and accepted any nonzero result, so failures could come from missing dependencies. The harness now preserves the ten baseline gate records and checks that each invalid fixture produces a diagnostic labeled with its intended gate; selected false-PASS/evidence attacks assert their diagnostic content. It still does not prove every negative case fails for its unique intended reason, and this matrix must be read with the existing focused regression tests.

## Limits and claims not established

- **Structural versus semantic:** The validator checks schema, IDs, references, source/digest relationships, transitions, scope relationships, and required evidence classes. A matching hash proves byte identity only; it does not prove that mission, feasibility, tenant isolation, test output, prototype critique, operations evidence, or user outcome is truthful or adequate.
- **Evidence provenance:** Repository-controlled CI can lie, tests can be malicious or shallow, and a local runner is not an immutable execution attestation. The harness demonstrates that specific forged or missing structures are rejected; it does not make all evidence truthful.
- **Independent review:** Review mode and reviewer metadata are procedural claims. The schema cannot authenticate identity, prove cognitive independence, or prevent collusion.
- **Platform / interaction:** No real UI exists in this Python-engine scenario. G-CX correctly remains unverified/in-progress; no visual quality, accessibility, cross-platform parity, or user research claim is made.
- **Remote / hosted app CI:** The disposable app intentionally has no remote and its generated app workflow was not run on a hosting provider. Push/CI outage and authorization behavior are only locally modeled. The framework repository hosted CI result is not the app's CI result.
- **Release / operation:** No artifact was released, no deployment occurred, and no backup/restore, tenant isolation runtime test, long-duration JSON growth, telemetry loss, or incident drill was run. No production-readiness claim is supported.
- **Repository controls:** Branch-protection settings remain unverified (the prior settings query returned HTTP 403); successful workflow runs do not establish merge protection.
- **Current acceptance gaps at report draft:** The independent pilot reviewer returned BLOCKED on the first review. The harness now addresses the upstream-deletion and generic-nonzero issues, but has not yet been independently reassessed. Only G-INTENT has a synthetic positive PASS path in the pilot; the other nine records remain explicitly in-progress. The G-FEAS route exercises accept in-progress dependency-state shapes, not feasibility PASS. No valid G-CX pass is appropriate because this disposable local-first engine has no rendered or product interaction. The criterion requiring valid pass fixtures “where permitted” therefore remains open for reviewer adjudication; the report must not represent the current matrix as complete. The exact hosted run for `a62bbd5` and final backlog state must also be recorded before approval.

## Pilot disposition

**Provisional: structurally useful, not yet independently accepted.** Two concrete false positives were found and fixed in bounded validator changes; the app was reinitialized at the resulting exact framework revision, and the regression harness exercises the relevant paths. FW-TASK-020 must remain in progress until independent review and final exact-commit verification are recorded. This pilot does not establish that the framework can build a production-grade application without semantic owner/reviewer judgment and real app-specific evidence.
