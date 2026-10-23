Warning: truncated output (original token count: 5055)
Total output lines: 158

---
id: FRAMEWORK-ARCHITECTURE-002
type: framework-architecture
title: FW-TASK-028 risk-scaled quality and traceability architecture
status: draft
version: 0.2
created: 2026-10-23
updated: 2026-10-23
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, FRAMEWORK-FEASIBILITY-009, FRAMEWORK-COVERAGE-001, FRAMEWORK-CX-001, FRAMEWORK-ADV-020, FRAMEWORK-ADV-021, DECISION-026, GATE-CATALOG-001, FRAMEWORK-GATE-CONTRACT-001
---

# FRAMEWORK-ARCHITECTURE-002 — FW-TASK-028 risk-scaled quality and traceability

## G-ARCH work record

- **Gate:** G-ARCH — in progress; no pass is asserted.
- **Task and requirements:** FW-TASK-028; FR-FW-029, FR-FW-030, FR-FW-031; seven acceptance criteria in FRAMEWORK-BACKLOG-001.
- **Approved boundary:** DECISION-026 and the G-REQ record in FRAMEWORK-BACKLOG-001. Covers app-owned quality profiles, deterministic task/criterion/path/check traceability, and anti-gaming diagnostics. It does not change framework repository checks or thresholds. FW-TASK-024, signed receipts, sandboxing, agent budgets, draft gate-contract adoption, app implementation, and other v2 work are excluded.
- **Upstream gates:** Bounded G-FEAS passed in FRAMEWORK-FEASIBILITY-009; G-COVERAGE passed in FRAMEWORK-COVERAGE-001; G-CX passed in FRAMEWORK-CX-001. These are planning evidence, not implemented capability.
- **Target:** Local-first repository contracts and deterministic diagnostics, with hosted CI enforcement against an exact source revision. GitHub Actions check-run lookup is the only provider path exercised; other providers remain unsupported until separately evidenced.
- **Review method:** Independent tool-neutral GARCH-01–03 review after this exact artifact revision and Verify Pipeline result are available. No executable schema or integration test is claimed by this design.

## Boundaries, actors, and authority

| Actor/component | Responsibility | Boundary |
| --- | --- | --- |
| App owner | Owns risk classification, policy scope, thresholds, exclusions, rationale, and any future exception-authority decision | No numeric default is supplied by the framework. This task configures no exception approver. |
| Contributor/agent | Selects approved task, proposes mappings, runs diagnostics, resolves findings | Cannot lower an accepted threshold, misclassify a sensitive path to avoid escalation, or self-authorize an exception. |
| Local evaluator | Parses policy and trace inputs; checks structure, paths and mappings; may run diagnostics | Advisory only; cannot authenticate hosted checks, guarantee merge protection, or mutate source. |
| Stack adapter | Runs supported coverage/mutation/property/contract checks and emits normalized results | Adapter output is untrusted. Synthetic FW-013 lanes do not establish production stack support. |
| Hosted CI evaluator | Repeats validation against event SHA, queries provider check metadata when permitted, emits bounded report | Read-only permissions, no secrets passed to test/package tools, no auto-edits. Workflow success alone is not branch protection. |
| Reviewer | Inspects mappings, policy, results, limitations, findings and authority | Human review remains necessary for semantic intent and policy adequacy. |

Out of boundary: product runtime/deployment, user data, hosted orchestration, host sandboxing, code deletion/rewrite, and framework repository policy settings.

## Components and data flow

1. **App-owned profile:** A versioned app artifact declares risk dimensions, metric rules, exact scope, thresholds, exclusions, unavailable metrics, evidence strength, and rationale. It is accepted through the app's review process; no framework threshold is silently inherited.
2. **Trace manifest:** A versioned record binds repository identity and full source SHA to task ID, the complete acceptance-criterion set, canonical changed paths, criterion/path pairs, selected profile digest, and required provider/check identities. Positive exceptions are rejected while no independently verifiable authorization contract exists.
3. **Preflight evaluator:** A deterministic core checks version, unique IDs, required fields, repository/profile/source binding, normalized canonical paths, complete criterion/path mapping, generated files, and check declarations. It emits diagnostics and never edits source.
4. **Risk resolver:** Combine app policy with task/criterion declarations and changed-path inventory. Apply the strictest applicable supported class. A lower task label cannot override a sensitive path or criterion. Unknown, conflicting, mixed-scope, or unclassified generated paths either escalate or block; they never silently lower evidence requirements.
5. **Measurement adapters:** Run declared checks and normalize tool/version, invocation, source SHA, metric/value or unavailable reason, included/excluded scope, exit status and bounded evidence reference. Tool output alone is not a pass.
6. **Provider adapter:** Bind required checks to provider, repository, immutable run/check ID, conclusion and matching head SHA. A local success string, copied output, check name alone, or a run from another SHA cannot satisfy the requirement. GitHub is the only feasibility-proven adapter.
7. **Review summary:** Link each criterion to paths and checks; display per-metric scope, rationale, result, limitations and next action. PASS requires every applicable required condition to be current and satisfied. FAIL, STALE, IN_PROGRESS, BLOCKED, UNAVAILABLE and unsupported states remain distinct. No metric proves semantic correctness.
8. **Evidence lifecycle:** Bind results to exact source, policy, profile, adapter and evaluator revisions. A changed input invalidates dependent evidence; reruns append linked records rather than relabeling old results.

## Versioned contract drafts

The schemas and fixture cases under `docs/framework/schemas/fw028/` are architecture artifacts, not production validators. JSON Schema checks field shape and domain; cross-record invariants require semantic validation in later implementation.

### Quality profile

Schema: `docs/framework/schemas/fw028/quality-profile-v1.schema.json`. It types profile identity/version, owner reference, adapter, dimensions, risk tiers, metric rules, path scope, escalation floors, and supersession. Fixtures: `fixtures/quality-profile.valid.json` and `fixtures/quality-profile.missing-rationale.invalid.json`.

Invariants: thresholds are typed and justified by linked app policy/decision; exclusions cannot hide a path required by a stricter rule; unavailable metrics cannot satisfy mandatory conditions; task-level overrides cannot weaken accepted policy; lowering a threshold requires a reviewed new profile version; exact accepted profile bytes are digest-bound.

### Trace manifest

Schema: `docs/framework/schemas/fw028/trace-manifest-v1.schema.json`. It types repository/source identity, task and criterion IDs, canonical paths, criterion/path links, required checks, profile digest, and exception references. Fixtures: `fixtures/trace-manifest.valid.json` and `fixtures/trace-manifest.missing-path-link.invalid.json`.

Invariants: repository/source/profile revisions match the evaluated checkout; every in-scope changed path and required criterion is mapped; each pair is checked for correctness rather than accepting only complete sets; traversal, ambiguous normalization, aliases and symlink escape are rejected; generated paths are explicit. Exceptions require exact paths/criteria, reason and independently verifiable authority; until that authority contract is approved, every positive exception is rejected. Check names or local outcome strings are insufficient.

### Normalized measurement/check result

Schema: `docs/framework/schemas/fw028/measurement-result-v1.schema.json`. It types repository/source and policy bindings, adapter/tool invocation, metrics, unavailable reasons, provider check-run evidence, overall state, evidence reference, and timestamp. Fixtures: `fixtures/measurement-result.valid.json` and `fixtures/measurement-result.unavailable-claimed-pass.invalid.json`.

Invariants: missing, failed, skipped, pending, stale, unsupported or unauthenticated evidence never becomes PASS; percentages from different tools/stacks are not compared as equivalent; a green aggregate cannot hide missing checks or weak-assertion findings. `fixtures/cases.json` records expected schema and semantic outcomes. The semantic validator must reject missing path/criterion pairs, profile digest mismatch, risk-floor downgrade, or a required unavailable metric paired with overall pass; JSON Schema alone cannot establish these cross-record facts.

## Data, security, privacy, and operations

- Keep app policy and trace records in each app repository. The template stores only generic contracts and synthetic fixtures.
- CI permissions are read-only and limited to source/provider metadata. Do not pass tokens, checkout credentials, deployment secrets or private product data to test, build, mutation or third-party tools.
- Pull-request code is untrusted executable input. Use the established disposable hosted runner and read-only CI boundary; this is not a container or OS sandbox and does not prove denial of runner-level access.
- Resolve paths against a frozen repository root; reject traversal and symlink escape. Compare source inventory before and after measurements; any source change invalidates the result.
- Provider identities bind to repository and head SHA, but do not prove branch protection or reviewer identity. Retain bounded diagnostics and redact secrets.
- Existing CI timeout bounds remain in force. FW-TASK-030 budget monitoring is excluded. The evaluator does not operate or monitor product services.

| Failure | Result | Recovery |
| --- | --- | --- |
| Missing/invalid policy, task, criterion or mapping | Named failure; no PASS | Correct versioned input and evaluate new SHA. |
| Conflicting or downgraded risk labels | Strictest rule or blocked | Owner reviews the classification…55 tokens truncated…A details | Await or rerun for exact current SHA. |
| Self-asserted or wrongly scoped exception | Reject | Resolve mapping; future authority requires separate owner-approved contract. |
| Tool error, timeout or malformed output | Failed/unavailable with bounded diagnostic | Diagnose and retry under existing CI controls; no automatic retry loop. |
| Source/policy changes during run | Stale/invalidated | Recompute on clean checkout at new revision. |
| High coverage with surviving boundary mutant | Weak assertion evidence; critical condition fails | Strengthen behavior assertions or owner-review policy change; do not lower policy to mask it. |

## Architecture decisions and alternatives

### ADR-FW028-ARCH-01 — App-owned versioned risk policy
**Decision:** Each app owns its risk profile, thresholds, scope, exclusions and rationale. No framework default is applied to app behavior. **Alternatives:** a universal threshold ignores stack-specific metric availability; per-task agent-selected thresholds enable silent weakening. A reviewed app-owned policy preserves owner authority and auditability. **Authority/evidence:** DECISION-026, FR-FW-029/031, bounded profile observations in FRAMEWORK-FEASIBILITY-009. No numeric value is selected here.

### ADR-FW028-ARCH-02 — Trace manifest and provider adapter
**Decision:** Bind full task/criteria/path mappings in a versioned manifest; use provider APIs for exact-SHA check identity where evidenced. **Alternatives:** AST inference cannot establish semantic intent or non-code criteria; local check names/outcome text are replayable. **Authority/evidence:** DECISION-026, FR-FW-030, exact-SHA GitHub probe [39974646889](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/39974646889). Other providers are unsupported pending evidence.

### ADR-FW028-ARCH-03 — Exceptions fail closed
**Decision:** Accept none until a separate owner-approved model verifies authority, scope and validity. **Alternatives:** free-text approver names are spoofable; treating exceptions as exclusions hides changed paths. **Authority/evidence:** DECISION-026 and bounded G-FEAS disposition in FRAMEWORK-FEASIBILITY-009.

### ADR-FW028-ARCH-04 — Diagnostics never rewrite source
**Decision:** Emit findings only; never delete or rewrite code based on AST/path findings. **Alternative:** automated edit/delete is destructive and cannot infer intent. **Authority/evidence:** FR-FW-030, AC-6, and source-digest observations in FRAMEWORK-FEASIBILITY-009.

## Invariants and later verification design

These checks are required for a later implementation; this document does not claim they already run:

1. Valid profile/trace/result fixtures and explicit unavailable cases across at least two adapters.
2. Reject unknown/duplicate criteria, missing/swapped pairs, stale SHA, repository/profile mismatch, traversal, path aliases, symlink escape, undeclared generated paths and source mutation during a run.
3. Show that sensitive path/criterion risk cannot be downgraded by a low-risk task label; mixed scope uses the strictest rule.
4. Reject task-level threshold lowering; reviewed policy changes require new version and rationale.
5. Accept only provider check identity/conclusion matching repository and exact SHA; reject wrong, absent, failed, skipped, pending or unverified checks. Do not infer branch protection.
6. Reject free-text, wrong-scope, expired, missing-authority, and all positive exceptions while authorization remains unavailable.
7. Pair weak assertion/call-only and boundary-mutant fixtures; cover generated files, omitted exports and unrelated changes without misleading quality claims.
8. Before/after source digest proves diagnostic non-mutation only, not a sandbox guarantee.
9. Preserve revision bindings and append-only correction links.

## Acceptance trace and task-ready decomposition

| Backlog criterion | Component and planned evidence |
| --- | --- |
| AC-1 profile metrics, thresholds, exclusions, limits, unavailable state | Profile contract plus valid, malformed and unsupported fixtures |
| AC-2 critical changes get stronger checks; classification cannot evade escalation | Risk resolver plus mixed-scope and downgrade negatives |
| AC-3 scoped rationale, diagnostics, reviewed threshold changes | Owner decision link, immutable profile version, override negatives |
| AC-4 intended checks on at least two profiles | Adapter contract and cross-profile fixtures; synthetic evidence does not mean permanent support |
| AC-5 exact task/criteria/path/check links and exception boundary | Trace manifest and provider binding; matching and mismatch cases; exceptions currently fail closed |
| AC-6 no source rewrite | Diagnostic-only evaluator and before/after digest case |
| AC-7 anti-gaming defenses | Controlled original/mutant pair plus weak-assertion, generated, export and unrelated-change cases |

Task-ready implementation units, all dependent on G-ARCH PASS and a separately recorded G-IMPL authorization:

| Unit | Scope and acceptance criteria | Dependencies | Required checks and evidence |
| --- | --- | --- | --- |
| **FW028-IMPL-01 — Profile contract and risk policy** | Implement profile schema and semantic validation. Pass only when required fields/rationale are complete, mandatory unsupported metrics stay non-passing, sensitive-path/criterion floors cannot be lowered by task labels, and threshold reduction requires a reviewed profile revision. Diagnostics name the rule/path. | G-ARCH PASS; G-IMPL authorization; FR-FW-029/031 and current framework check policy. | `FW028-PROFILE-SCHEMA`: valid/invalid fixtures; `FW028-RISK-SEMANTICS`: downgrade, mixed-scope, unavailable-metric and threshold-override cases; exact-SHA Verify Pipeline; independent review. |
| **FW028-IMPL-02 — Exact-revision trace and provider binding** | Implement trace schema and relational validator. Pass only when repository, source SHA, profile digest, task, each criterion, changed path and path/criterion pair are checked; canonical-path attacks fail; only matching provider/check/run/head-SHA evidence satisfies a required check; positive exceptions remain rejected. | FW028-IMPL-01; G-ARCH PASS; G-IMPL authorization; FW-TASK-019 trust semantics and current CI/release policy. | `FW028-TRACE-SCHEMA`: valid/malformed fixtures; `FW028-TRACE-SEMANTICS`: missing/swapped mapping, wrong repository/SHA/profile digest, traversal/symlink, absent/failed/pending check and self-asserted exception; synthetic exact-SHA provider probe; exact-SHA Verify Pipeline; independent review. |
| **FW028-IMPL-03 — Anti-gaming diagnostics** | Add deterministic quality fixtures and bounded diagnostics. Pass only when call-only high coverage differs from assertion evidence, assertion fixtures reject the named boundary mutant, generated/omitted exports and unrelated/mixed-scope paths remain visible, diagnostics do not mutate source, and at least two adapters report truthful outcomes. | FW028-IMPL-01/-02; G-ARCH PASS; G-IMPL authorization; frozen fixture catalog. | `FW028-QUALITY-MATRIX`: original/mutant × weak/asserting tests; `FW028-SCOPE-NEGATIVES`: generated/export/unrelated cases; `FW028-NONMUTATION`: before/after digest; exact-SHA CI and independent review. |

These are proposed acceptance identifiers, not existing workflow jobs. Unsupported providers/metrics remain explicitly unavailable.

All units must revalidate against approved FRAMEWORK-GATE-CONTRACT-001 v1.0 and current app-check/CI policy. The decomposition does not authorize implementation, choose thresholds, authorize exceptions, or alter framework checks.

## Independent critique record

- **Reviewer/evaluator:** Independent reviewer `/root/infinite_gallery_reviewer`; full-scope tool-neutral G-ARCH review round 1.
- **Frozen inputs:** FRAMEWORK-CX-001 v0.3; FRAMEWORK-COVERAGE-001 v0.2; FRAMEWORK-FEASIBILITY-009 v1.5; approved FW-TASK-028 scope and DECISION-026.
- **Scope:** GARCH-01–03; boundaries, identities, data flows, privacy/security, failure/recovery, provider/profile claims, contract invariants, ADR authority/alternatives, verification plan, backlog handoff, exclusions.
- **Limitations:** No code, executable schema, threat-model exercise, production integration, app deployment, branch setting inspection, or real exception authority is established.
- **Round 1 result:** BLOCK at exact commit `198ca0dc6e057694dda7a4401f790fa4926ac893`; Verify Pipeline [40015129630](https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/40015129630) passed all three jobs on that SHA.
- **FRAMEWORK-ARCHITECTURE-002/FINDING-001 — Major, task-ready decomposition:** FW028-IMPL-01–03 lacked unit-level criteria, dependencies and checks. **Disposition:** accepted; v0.2 supplies a scope/dependency/check matrix.
- **FRAMEWORK-ARCHITECTURE-002/FINDING-002 — Major, critical contract verification:** Profile, trace and result contracts lacked typed schemas and positive/negative fixtures; relational invariants were underspecified. **Disposition:** accepted; v0.2 adds three Draft 2020-12 schemas, paired fixtures, semantic diagnostic cases, and explicit limits on schema-only claims.
- **Owner decisions:** Reviewer found none needed; corrections remain within DECISION-026.
- **Findings/disposition:** Both findings are addressed in this revision; full-scope independent rerun is pending.
- **Gate result:** In progress; round-1 BLOCK remains immutable historical evidence.

## Exclusions and next action

This design does not choose numeric thresholds, select real app stacks/providers, implement validators/adapters, set repository protection, accept exceptions, or authorize FW-TASK-024 or other v2 work.

**Next action:** Commit v0.2 with schemas, fixtures, and finding dispositions; pass Verify Pipeline on that exact revision; then request full-scope independent G-ARCH rerun. G-IMPL remains unauthorized until G-ARCH passes and implementation is separately authorized under the applicable gate contract.
