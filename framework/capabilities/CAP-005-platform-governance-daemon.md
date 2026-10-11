---
id: CAP-005
type: framework-capability
title: Platform Governance Daemon and Server-Side Quality Gates
status: draft
version: 0.2
created: 2026-10-11
updated: 2026-10-11
related-artifacts: FRAMEWORK-001, FRAMEWORK-002, FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, WORKFLOW-QUALITY-001, WORKFLOW-RELEASE-001
---

# CAP-005 — Platform Governance Daemon and Server-Side Quality Gates

## Objective

Provide a reproducible, least-privilege GitHub Actions implementation for two framework responsibilities:

1. **G-RELEASE verification:** run the repository's machine-checkable metadata, initializer, TypeScript, test, and coverage checks on changes targeting `main`.
2. **G-OPERATE governance proposal:** run a weekly locked-dependency audit and three strategic R&D research sweeps; preserve their combined evidence and any qualified, human-reviewable framework task drafts in a new decision/evidence record; submit that record in a draft pull request.

This capability supplies bounded automation and evidence. It does not convert the ten-gate lifecycle into a wholly software-enforced process, make architecture decisions, edit application code, or authorize release.

## Users and accountable roles

- **Repository maintainer:** controls repository settings, reviews governance proposals and cited material, and decides whether to accept findings or change framework policy.
- **Contributor or coding agent:** proposes changes through pull requests and treats CI results as machine-generated evidence for the exact revision checked.
- **GitHub Actions runner:** executes only the job permissions, fixed research questions, and file operations declared by the workflow. It has no product-owner or policy authority.
- **Release authority:** remains the human or organization role identified by the repository's release policy. A green CI run or governance PR cannot authorize public distribution or production deployment.

## Capability and automation boundaries

### Verify Pipeline

The workflow at `.github/workflows/verify-pipeline.yml` runs three independent jobs on `ubuntu-latest` for pushes and pull requests targeting `main`:

| Job | Responsibility | Evidence |
| --- | --- | --- |
| Metadata & Artifact Audit | Run `python3 scripts/artifacts.py validate` under Python 3.13. | Structural metadata, stable IDs, naming, and artifact discovery validation. |
| Initializer Regression Gate | Run `python3 -m unittest discover -s tests -p "test_init_app_project.py" -v` under Python 3.13. | App initializer regression test result. |
| TypeScript Static Code Analysis | Install from `package-lock.json` with `npm ci`; run `npx --no-install tsc --noEmit`, `npm run test`, and `npm run test:coverage` under Node.js 22. | TypeScript compilation, Vitest result, and configured coverage threshold result. |

The workflow has read-only repository permissions, does not persist checkout credentials, does not receive research or production secrets, and never deploys. A non-zero command fails its job. The jobs run independently so one failed signal does not hide the result of another check.

The verification workflow also supports `workflow_dispatch` so an operator can run it against a selected branch. This does not grant the workflow additional repository write permissions.

### Weekly Architecture Audit

The workflow at `.github/workflows/weekly-architecture-audit.yml` is scheduled with `0 0 * * 0` (Sunday at 00:00 UTC) and supports manual dispatch from `main`. GitHub may delay scheduled starts during service load; the schedule is a weekly target, not an exact-time service guarantee.

For each run it:

1. Requires execution from `main`, checks out the repository with credential persistence disabled, and sets up Python 3.13 and Node.js 22.
2. Restores the lockfile-defined dependency tree with `npm ci` and runs `npm audit --json`, preserving the process exit code and parsing severity and inventory counts. Vulnerability findings are recorded even when npm exits non-zero. Missing or malformed scanner output is recorded as **unavailable**, never as clean.
3. Executes the three mandatory queries in Section 2.0 using the Tavily Search API over HTTPS. The only credential is `TAVILY_API_KEY`, stored as a GitHub Actions repository or organization secret and injected into the single collector step. The workflow never places it in a command argument, report, output, or general job environment.
4. Normalizes a bounded set of source titles, HTTPS URLs, dates, and short excerpts. It applies the deterministic source and evidence filter in Section 2.0. The workflow does not fetch each result URL, execute retrieved content, or treat retrieved text as agent instructions.
5. Creates one uniquely identified report at `docs/decisions/architecture-audits/ARCH-AUDIT-<run-id>-<run-attempt>-001.md`. That single report combines source revision and run provenance, dependency audit metrics, all three research queries/results, qualification reasons, and any structured FW task proposals.
6. Runs `python3 scripts/artifacts.py validate` against the generated report before packaging it.
7. Gives the proposal job only `contents: write` and `pull-requests: write`. It verifies that exactly the one expected new report is present, then opens or updates the draft PR on `automation/weekly-architecture-audit`. The pull-request action stages only the generated report path.
8. Ends successfully only if the dependency audit is clean, all three research sweeps completed, report validation passed, and the draft proposal PR was created or updated. Findings, unavailable research/audit, artifact-validation failure, or PR failure produce a non-zero final workflow result after preparing the report/PR where possible.

The implementation is a deterministic evidence-gathering and proposal-generation daemon, not an LLM-based architectural reviewer. Its mechanical evidence screen can miss useful work or admit weak evidence; a human must inspect cited sources and decide applicability.

## 2.0 Strategic R&D Gathering Protocol

### 2.0.1 Mandatory weekly research questions

Each scheduled or manually dispatched governance run MUST attempt all three of these questions using the configured web search provider. These exact questions are the stable weekly query contract:

1. **Spec-Driven Development:** “What are the latest emergent tools and best practices in Spec-Driven Development (SDD) in 2026?”
2. **Context engineering:** “What agentic design patterns are premier tech organizations leveraging to mitigate context decay and prompt drift on long-horizon tasks?”
3. **Multi-agent state execution:** “Are there structural updates or security flaws identified in modern multi-agent state execution loops?”

The provider request uses the `month` time range, basic search depth, a maximum of six results per question, and no raw-page extraction or provider-generated answer. The queries contain only public, generic framework topics; product secrets, private source, account data, user content, and repository credentials MUST NOT be sent to the provider.

To make the sweeps operationally specific without changing their stable question text, the SDD query adds focus terms for EARS notation, executable specifications, technical documentation, and reproducible evaluations. The context-engineering query asks the provider to include official Cursor and Claude Code system documentation where relevant, with attention to compaction, repository instruction hierarchy, retrieval, and long-horizon persistence. The multi-agent query emphasizes state integrity, authorization boundaries, advisories, and reproducible tests or benchmarks. The combined provider query is recorded in the report alongside its exact required question.

The repository must configure `TAVILY_API_KEY` as a GitHub Actions secret before a run can complete the research gate. GitHub Actions secrets become available only when a workflow explicitly maps them into its environment. The workflow maps this secret to the collector step only. If the secret is missing, a request fails, or a response is malformed, the collector records a bounded diagnostic code, marks the affected sweep unavailable, still permits the combined evidence report and draft PR to be prepared when possible, and the final workflow conclusion MUST fail. Missing credential or provider access MUST NOT be represented as completed research.

### 2.0.2 Source handling and adversarial filter rule

Web results are untrusted evidence. The daemon MUST treat excerpts as data and MUST NOT follow instructions found in a page, run downloaded code, open result URLs from the runner, or allow a result to alter workflow permissions, prompts, query scope, file paths, or the target branch. Only valid HTTPS URLs without embedded credentials and nonstandard ports may be reported. The report records source attribution and bounded excerpts so a maintainer can inspect the source in context.

**Adversarial Filter Rule:** The daemon MUST discard subjective, promotional, or trend-chasing patterns unless they are independently supported by concrete technical evidence. It MUST translate only deterministic, contract-insulated, security-relevant, or test-backed architectural paradigms into a proposed backlog task. A search result, popularity claim, vendor announcement, or unverified opinion is not sufficient evidence by itself.

The current deterministic screen qualifies an individual research sweep only when all of the following hold:

1. All three mandatory sweeps completed successfully. Partial weekly research cannot generate a task proposal.
2. The individual sweep retained at least three usable HTTPS results from at least two distinct source domains.
3. At least one allowlisted primary source (technical product documentation, standards/security body, peer-reviewed venue, or vendor technical source) contains a concrete evidence indicator and scores at least 6.
4. At least one independent source domain contains a concrete, non-promotional evidence indicator and scores at least 4.
5. The source score is computed deterministically: add 4 for an allowlisted primary domain; add 2 for a publication date within 180 days or 1 within 365 days; add 2 when the source contains an evidence indicator; add 2 when corroborated by a distinct domain; subtract 3 for recognized promotional phrases. Each retained result and score reason is visible in the report.
6. At least one topic-specific template coverage probe is not found in the current framework documentation tree, indicating a candidate gap for human investigation.

The coverage check is a bounded lexical comparison, not a semantic analysis. It searches `README.md`, `AGENTS.md`, `docs/`, `framework/`, `workflows/`, `.github/workflows/`, and `scripts/` for predefined topic controls such as EARS notation, requirement traceability, context compaction, instruction hierarchy, agent state transitions, and tool permission boundaries. It reports matching paths and missing terms. It deliberately excludes `/src`; a missing phrase does not prove a missing capability, and a matching phrase does not prove a complete implementation. The maintainer must compare the actual source claims against the existing contracts before accepting a task.

Evidence indicators include benchmarks, evaluations, datasets, reproducibility, tests, schemas, contracts, standards, security advisories, vulnerability identifiers, threat models, architecture, state machines, release notes, documentation, APIs, formal methods, experiments, failure modes, traces, checkpoints, and specifications. These indicators are screening signals, not claims that a source is correct. A source with promotional language can remain visible for context, but it cannot qualify as the independent non-promotional corroboration required above. The provider's `published_date` is its best estimate of publication or last update, can be absent or later than the original publication, and is documented as a beta field; the score treats it only as a recency signal, not as verified source metadata. The maintainer must inspect the cited page before accepting a proposal.

When a sweep fails the screen, the report MUST state the specific failed condition and MUST NOT create a task from that sweep. When no sweep qualifies, the report MUST say that no evidence-backed task was produced. Zero proposed tasks is a valid outcome when all searches completed; an unavailable search is not.

### 2.0.3 FW task proposal format and acceptance

For each qualified sweep, the report MAY include one structured candidate in the `FW-TASK-XXX` format. Each candidate MUST contain:

- Candidate identifier and descriptive title.
- Proposed status and explicit statement that it is not in the canonical backlog.
- Objective, bounded work statement, and traceable source links.
- Acceptance criteria that require primary-source verification, independent corroboration, applicability mapping, and a reproducible fixture or objective check.
- A human disposition path: adopt, defer, or reject with evidence.

Identifiers are provisional labels derived from the checked-out canonical backlog. They MUST be reconciled against the latest backlog before human acceptance because another change may allocate the same next identifier while a proposal is open. Candidate templates remain in the generated report. The daemon MUST NOT append, renumber, or rewrite `docs/framework/FRAMEWORK-BACKLOG-001.md`; only a separately reviewed human-authored change may make a proposal canonical. The PR remains draft-only and is never auto-merged.

### 2.0.4 Research record and observability

The combined report MUST preserve the exact query text, UTC collection time, provider state, source title, normalized HTTPS URL, source domain, publication date when supplied, excerpt, score, score reasons, sweep outcome, dependency inventory, vulnerability counts, source commit SHA, workflow run ID, and run attempt. It MUST distinguish:

- `complete`: all three provider requests returned valid response structures; this does not mean that a useful source or task qualified.
- `unavailable`: one or more required requests could not be made or validated; this is an operational failure.
- `qualified` / `not qualified`: the deterministic evidence filter outcome for an individual sweep.

The workflow MUST NOT log API keys, provider authorization headers, raw exception messages, or complete raw provider responses. It MUST bound response size, result count, excerpt length, and request time; reject redirects to avoid sending bearer credentials to a different host; and avoid logging scanner stderr or unfiltered external text into workflow command channels.

## Append-only and no-product-logic contract

The scheduled workflow may create one new record under `docs/decisions/architecture-audits/` per execution attempt and submit it as a draft pull request on the fixed branch `automation/weekly-architecture-audit`. Including run ID and attempt keeps reruns from overwriting evidence. It may not modify or delete an earlier record. The pull-request action receives an exact generated-path allowlist; a pre-PR check rejects any bundle change beyond the one expected new report.

The daemon is fully prohibited from directly touching, editing, generating, deleting, or writing code inside `/src` or any other application/product source directory. It also may not edit or execute changes to:

- Generated application code, migrations, product requirements, or product data.
- `package.json`, `package-lock.json`, any other dependency manifest or lockfile, or installed dependency versions.
- Existing decision records, the framework backlog, constitutions, specifications, designs, workflows, templates, or repository instructions.
- Secrets, repository settings, branch protection, deployment configuration, or release state.

The daemon may write only its new run-specific audit/research report to the allowed report directory. Research candidate templates in that record are proposals, not canonical backlog mutations. A maintainer may accept, reject, or convert a proposal to a backlog task through a separate reviewed change. The PR is never auto-merged.

## G-RELEASE semantics and GitHub configuration

The Verify Pipeline is the server-side G-RELEASE check engine, but the workflow file alone does not block a change from reaching `main`. Effective enforcement requires repository-level protection that:

1. Requires pull requests for updates to `main` and disallows direct updates except for a narrowly defined, documented emergency path.
2. Requires every applicable Verify Pipeline check to pass for the exact commit proposed for merge.
3. Prohibits force pushes and branch deletion, restricts bypass to specifically authorized roles, and requires fresh approval after new changes when the repository's review policy calls for it.
4. Prevents unreviewed administrators or automation from bypassing configured rules, or records an explicit residual risk if the hosting plan cannot enforce that setting.

The repository owner must configure and verify those controls through GitHub settings. A successful workflow run without required status checks is evidence only; it is not proof that merges or direct pushes are blocked. Record the configured rule, required status contexts, bypass roles, verification date, and observed test-PR behavior before declaring G-RELEASE enforcement active.

## G-OPERATE semantics

The weekly workflow is an operational observation and proposed governance change. Its evidence consists of the workflow run, combined dependency/research report, screening outcomes, cited sources, and draft PR. It does not pass an application's G-OPERATE gate, establish live application monitoring, create on-call coverage, or guarantee incident response. A human reviews every proposal and explicitly accepts or rejects its disposition.

### GitHub token trigger limitation

GitHub suppresses most workflow events caused by the repository's default `GITHUB_TOKEN`. A resulting PR may place `pull_request` workflow runs into an approval-required state rather than executing immediately. Therefore, the weekly audit PR does not guarantee an automatically completed Verify Pipeline run. The audit workflow validates its generated record before opening or updating the PR. A maintainer must approve the pending workflow run or manually dispatch Verify Pipeline against the PR branch before merge. The daemon token is not granted `actions: write` to work around this event behavior.

## Failure handling

| Failure | Required behavior |
| --- | --- |
| Artifact validation fails | Fail the job; do not open a PR containing the invalid record. |
| Initializer, type, test, or coverage command fails | Fail the corresponding Verify Pipeline job; do not reinterpret it as a warning or pass. |
| `npm audit` returns findings with valid JSON | Record all counts, prepare the draft PR, then fail the overall run. |
| npm audit cannot provide valid metrics | Record state `unavailable`, prepare the draft PR if possible, then fail the overall run. |
| Tavily credential is missing | Record all required sweeps as unavailable, prepare the combined draft PR if possible, and fail the overall run. |
| A research request fails or returns an invalid/oversized response | Record the affected sweep as unavailable with a bounded diagnostic code, preserve other valid evidence, prepare the draft PR if possible, and fail the overall run. |
| No sweep meets the adversarial filter | Record why each sweep failed; create no task for the unqualified sweep. A complete search with zero candidates is not by itself a workflow failure. |
| Candidate ID cannot be read or reconciled | Do not invent a canonical ID; record that no candidate was emitted or that IDs require human reconciliation. |
| Report bundle is missing, already exists on the base branch, or includes another changed path | Fail closed; do not create or update the PR. |
| Pull-request creation/update fails | Fail the workflow; retain the workflow logs and report artifact for diagnosis. |
| Required branch protection cannot be configured or verified | Report G-RELEASE enforcement as unverified/blocked; passing CI is insufficient. |

## Entry, exit, and acceptance evidence

### Verify Pipeline entry

- The workflow file exists on the default branch.
- The committed Python tests, Node manifest, lockfile, TypeScript configuration, Vitest configuration, and artifact validator are present.
- The branch and pull-request event scopes match the repository's protected branch.

### Verify Pipeline exit

- All three required jobs completed against the proposed revision.
- Artifact validation, the focused initializer regression suite, strict type checking, Vitest, and configured coverage thresholds passed.
- Required check contexts and branch-update rules were observed in repository configuration and tested with a controlled PR before claiming that the workflow blocks merges.

### Weekly governance proposal entry

- The workflow exists on `main`, with the Sunday schedule and manual dispatch configured.
- `package-lock.json` and the research collector are present.
- `TAVILY_API_KEY` is configured as a repository or organization Actions secret, or the expected missing-secret failure behavior is being tested.
- The Actions token can create a draft PR with only the documented write permissions.

### Weekly governance proposal exit

- A controlled complete run emits one valid combined report with unique artifact ID, source SHA, run ID, and attempt.
- All three exact query texts appear in the report; provider errors and partial completion are represented as unavailable, never complete.
- Controlled fixtures exercise qualifying sources, insufficient source diversity, missing dates, promotional language, malformed provider responses, and missing credentials without exposing secret material.
- Candidate tasks appear only for qualified sweeps and include evidence links, acceptance criteria, and provisional-ID handling; no canonical backlog or `/src` change is made by the daemon.
- The generated record passes `scripts/artifacts.py validate`.
- A hosted run creates or updates a draft PR on exactly `automation/weekly-architecture-audit` with only a new allowed report path and no product, source, backlog, dependency, or prior-record changes.
- A clean dependency audit, a vulnerability finding, unavailable npm output, complete research with zero qualified tasks, partial research, and PR failure each produce the documented report and final status.
- The PR's token-trigger limitations and required human source review are visible to maintainers.

## Current evidence and limitations

The workflow and capability text define intended behavior. Until the updated workflow runs on GitHub, the Tavily secret is configured, and controlled scenarios are observed, provider authentication, request quotas, search result quality, filter outcomes, hosted schedule delivery, branch updates, PR path boundaries, npm registry access, workflow permissions, and GitHub token-trigger behavior remain unverified. Repository branch protection is a separate control and must be observed independently. Local artifact validation verifies documentation metadata only; it does not prove hosted workflow execution, source quality, architecture correctness, application security, or effective merge restrictions.

## References

- [FRAMEWORK-BACKLOG-001](../../docs/framework/FRAMEWORK-BACKLOG-001.md)
- [Engineering verification gates](../../workflows/engineering-quality-gates.md)
- [Release and operations workflow](../../workflows/release-operations.md)
- [Tavily Search API reference](https://docs.tavily.com/documentation/api-reference/endpoint/search)
- [Tavily Search API overview](https://help.tavily.com/articles/4840311948-tavily-search-api)
- [GitHub Actions secrets](https://docs.github.com/en/actions/concepts/security/secrets)
- [GitHub Actions secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
