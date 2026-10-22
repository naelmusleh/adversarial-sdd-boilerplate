---
id: GATE-RUNNER-001
type: framework-capability
title: Transactional lifecycle gate runner
status: in-review
version: 0.1
created: 2026-10-21
updated: 2026-10-21
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-GATE-CONTRACT-001, FRAMEWORK-BACKLOG-001, WORKFLOW-ADV-001
---

# GATE-RUNNER-001 — Transactional lifecycle gate runner

## Purpose and boundary

The app-local `scripts/artifacts.py` command supports a deterministic plan view and prevalidated append for immutable gate-run records. It currently accepts only approved gate-contract v1.0, consuming the app lock's exact version and existing validator/schema. It fails closed for pinned v1.1/v1.2 because those amendments remain drafts; this task does not approve or adopt them. It does not infer gate results, fabricate evidence, or turn advisory review into gate authority. It does not add or alter gate-contract semantics. The plan is a derived view of `GATE_ORDER`, `GATE_RESULT_TRANSITIONS`, and the pinned contract; there is no second editable transition registry.

The runner is available in initialized apps that copied a framework snapshot containing this helper and pin approved contract v1.0. Newer app snapshots that pin draft v1.2 do not become eligible just by copying the helper. Existing app snapshots are not silently upgraded.

## Commands

```text
python3 scripts/artifacts.py gate --root APP_ROOT plan --json
python3 scripts/artifacts.py gate --root APP_ROOT append --record candidate-gate-run.json
python3 scripts/artifacts.py review --root APP_ROOT validate --record candidate-review-run.json
python3 scripts/artifacts.py review --root APP_ROOT append --record candidate-review-run.json
python3 scripts/artifacts.py review schema
python3 scripts/artifacts.py staged-check --root APP_ROOT
```

The plan emits each gate/result transition as legal or illegal, its prior-gate prerequisites, actor boundary, invalidation rule, and next action. The runner validates a candidate record in memory alongside current immutable runs before publishing it. Candidate records must reference every exact current upstream run by ID, version, and digest; absent, failed, blocked, or stale prerequisites reject the append. Existing evidence and owner-decision checks remain in the pinned validator.

Append takes a repository-local interprocess lock, writes and syncs a same-filesystem temporary file, then uses create-only hard-link publication. A duplicate ID is never overwritten. A failed publication removes its temporary file. The canonical JSON records are authoritative; no cache is created. Lock timeout and I/O errors fail closed. A crash before publication may leave a hidden temporary file, which is not a gate record; remove it only after confirming no runner is active.

## Advisory review runs

Review JSON lives in `.sdd/review-runs/<record_id>.json`, separately from `.sdd/gate-runs/`. `review schema` prints its machine-readable schema. A record binds reviewer identity and mode, context disclosure and author overlap, the exact pinned gate contract, target IDs, frozen input paths and SHA-256 digests, findings, dispositions, and optional `rerun_of`. Every review result is the literal `advisory`; the schema denies additional fields, and its authority boundary explicitly denies gate authority, CI evidence status, and owner authorization. Changing a frozen input makes validation fail until a new review run is prepared against the changed bytes and linked as a rerun.

The core review-record validator has no provider calls or credentials. No provider adapter is included. A review record can inform a human decision but cannot satisfy a CI check, change owner authority, or pass a gate by itself.

## Local staged-path guard

`staged-check` rejects modifications, deletions, and renames under `.sdd/gate-runs/` and `.sdd/review-runs/`; it permits only new `.json` records. It can be called from a repository's local pre-commit hook. The hook is advisory defense against accidental staged rewrites: it cannot stop arbitrary file writes, bypass, hook removal, or direct tool/API access. Hosted required checks and branch rules must enforce merge eligibility. CI validates newly added records and the entire repository state.

## Security and verification limits

The interprocess lock coordinates cooperating runner instances on the local filesystem. It cannot prevent an editor, arbitrary program, hook bypass, or direct filesystem writer from changing files. Create-only atomic publication protects a single record from partial visibility and accidental replacement; it is not a tamper-proof ledger. Git history, required hosted checks, protected-branch settings, reviewer identity, and repository policy remain separate controls and must be observed independently.

No hosted required-check rehearsal or branch-protection claim is made by local tests. The Verify Pipeline is necessary evidence for proposed code but does not by itself prove repository settings prevent bypass or unreviewed direct updates.
