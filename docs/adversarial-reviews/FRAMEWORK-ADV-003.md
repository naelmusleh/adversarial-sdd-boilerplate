---
id: FRAMEWORK-ADV-003
type: adversarial-review
title: Independent review of app-project starter implementation
status: approved
version: 0.1
created: 2026-10-08
updated: 2026-10-08
reviewed-artifact: CAP-004
reviewed-version: 0.1
related-artifacts: CAP-004, FRAMEWORK-001, FRAMEWORK-002
---

# FRAMEWORK-ADV-003 — Independent review of app-project starter

## Review request

- **Gate / lifecycle transition:** Assess whether CAP-004's starter implementation safely and accurately bootstraps a separate app repository without false approval claims or broken artifact traceability.
- **Review scope:** CAP-004; `scripts/init_app_project.py`; `docs/templates/app-project/README.md`; every app-project template; generated fresh-repository behavior documented in CAP-004. Focus on generated ID validity and collisions, overwrite/path safety, status/approval claims, canonical `design.md` versus Impeccable output, workflow handoffs, and consistency between documentation and code.
- **Explicit exclusions:** Framework-wide design beyond the starter handoff, application-specific requirements, external GitHub operations, and production deployment behavior.
- **Questions to answer:** Does generated output have valid traceable IDs, avoid overwriting existing user data, preserve canonical source-of-truth boundaries, and report its capabilities and limits truthfully?
- **Approval authority:** Framework owner under FRAMEWORK-001. This independent review does not accept residual risk on the owner's behalf.
- **Evidence cutoff:** 2026-10-08, America/New_York.
- **Source revision:** Base commit `0d85b6105cda0e58d9faf7bf336ade3143182c71`; all reviewed targets were uncommitted working-tree files. Current rerun fingerprints: CAP-004 `88646fafbb3efb2332e90656ef6ff478ad9ff6e5e4087a855f00c7ab0cbeab31`; initializer `0dc3de6af209ca94d329c68a5c174b567a12c59497795950c35c0fa0de8d2fe2`; starter README `832e868f66f0f255c648b0b8a0e85b16bae72f3f5fef4d6898fab0a0c7019f1f`; design template `3aa1585d93e5deefa821b94ead55775bfe4c59bb7f974c5260c17d77f1081931`. These hashes identify the observed current files; Git history will preserve them only after commit.

## Review method

- **Critic / verifier:** Independent reviewer agent, separate from the CAP-004 author and its revisions.
- **Reviewer mode:** `independent` for the initial and follow-up reviews; no authoring or target-editing work was performed by this reviewer.
- **Independence explanation:** The reviewer examined the implementation and generated behavior separately from the author. The author made two fixes during the review, which were rerun independently and recorded below.
- **Reviser:** CAP-004 author.
- **Sources inspected:** CAP-004; `scripts/init_app_project.py`; `docs/templates/app-project/README.md`; all 16 `*.template` files in `docs/templates/app-project/`; generated fresh-repository sample; FRAMEWORK-001 and FRAMEWORK-002; lifecycle, discovery, CX-design, gate-catalog, and tool-catalog handoff material as needed.
- **Limits:** The GitHub repository-creation and permission flow is explicitly outside this local initializer's capability. No external GitHub operation was run. Current working-tree targets are uncommitted.

## Finding register

### FRAMEWORK-ADV-003/FINDING-001 — Generated design artifact referenced a matrix ID that did not exist

- **Severity:** Major
- **Target location:** `docs/templates/app-project/design.md.template`, front matter `related-artifacts` and CX matrix instructions.
- **Initial evidence:** The initial template listed `<APP>-CX-MATRIX-001` in `related-artifacts`, but the initializer generated no CX matrix artifact. A fresh sample contained 16 unique artifact IDs and no `<APP>-CX-MATRIX-001`; scanning every generated `related-artifacts` field found that ID dangling. The README said the detailed matrix had one canonical location in or directly linked from `design.md` and prohibited a second hand-edited copy.
- **Inference:** A new project would begin with a broken traceability link and ambiguous expectations about whether a separate matrix artifact should exist.
- **Impact / failure mode:** Agents and owners could waste effort searching for a missing artifact or create a second matrix that drifts from the canonical experience contract.
- **Recommendation / options:** Remove the nonexistent ID when the matrix is inline; if the matrix is split out, require creating and linking an artifact with a stable ID.
- **Owner decision required:** No. FRAMEWORK-002 requires stable IDs and links; the template can state the inline default.
- **Initial disposition:** unresolved.

### FRAMEWORK-ADV-003/FINDING-002 — Initial empty-target check allowed a concurrent file to be overwritten

- **Severity:** Major
- **Target location:** `scripts/init_app_project.py`, output file creation loop.
- **Initial evidence:** The initial implementation checked whether the target was empty and later used `Path.write_text`, which replaces an existing file. A deterministic simulation created `mission.md` after the emptiness check but before the write loop; the initializer returned success and replaced `CONCURRENT USER CONTENT`.
- **Inference:** Another process or user action during initialization could lose data despite the documented refusal to overwrite.
- **Impact / failure mode:** Existing user-authored content could be destroyed by a race between validation and file creation.
- **Recommendation / options:** Create each output with exclusive-create semantics and stop with an error if a path appears after the initial check.
- **Owner decision required:** No. Preserving data is required by the documented safety boundary.
- **Initial disposition:** unresolved.

## Disposition and revision

| Finding | Disposition | Rationale / decision evidence | Change made or follow-up | Target revision/link | Owner and revisit trigger if deferred/risk |
| --- | --- | --- | --- | --- | --- |
| FRAMEWORK-ADV-003/FINDING-001 | `resolved` | Current fresh output has no dangling related-artifact IDs; inline matrix is the default. | Removed the nonexistent matrix ID and clarified that a separately stored matrix must receive a stable ID and be linked. | `docs/templates/app-project/design.md.template`, current hash in source revision | N/A |
| FRAMEWORK-ADV-003/FINDING-002 | `resolved` | Deterministic rerun confirms a concurrent file is preserved and initialization stops. | Changed output file creation to exclusive mode (`open("x")`) and reports the collision as an initialization error. | `scripts/init_app_project.py`, current hash in source revision | N/A |

No owner residual-risk approval used for this review.

## Rerun and verification

- **Rerun date:** 2026-10-08.
- **Verifier and reviewer mode:** Independent reviewer agent; no target authoring or revision overlap.
- **Scope:** Full original scope rerun against current CAP-004, initializer, README, all app-project templates, and generated sample. Rechecked IDs/links, collision and path behavior, approval/status claims, `design.md`/Impeccable separation, and handoff claims.
- **Target revision:** Current uncommitted CAP-004 v0.1 and initializer/template working tree, identified by the fingerprints above.
- **Prior finding checks:**

| Finding | Rerun state | Evidence confirming resolution or explaining remaining risk |
| --- | --- | --- |
| FRAMEWORK-ADV-003/FINDING-001 | verified-resolved | A new invocation generated 20 files and 16 unique metadata IDs. A scan of all generated `related-artifacts` values found no missing IDs. The current design template keeps the matrix inline by default and requires a stable ID and link only if split out. |
| FRAMEWORK-ADV-003/FINDING-002 | verified-resolved | Repeated the deterministic race simulation by inserting `mission.md` after the empty-target preflight. The current initializer stopped with exit 1 on `File exists`; the sentinel content remained unchanged. |

- **New findings:** None in the rerun scope.
- **Exact checks run:**
  - `python3 scripts/artifacts.py validate` — **PASS**, `Validated 30 artifact(s).` before adding this review record.
  - Fresh subprocess invocation of `scripts/init_app_project.py --name "Review App" --prefix RVW --target <temporary-directory>` — **PASS**, created 20 files; 16 metadata IDs were unique; every generated artifact's related IDs resolved to generated metadata IDs.
  - Deterministic concurrent-file injection against the current initializer — initializer exited 1 with an `Errno 17 File exists` error and preserved the preexisting sentinel file.
  - Current generated design README/template inspection — **PASS** for the canonical boundary: `design.md` is the experience contract; the Impeccable `document` command must run in isolated staging, and its generated `DESIGN.md` is stored as reviewed, non-authoritative output. The matrix is canonical inline or linked, not a second manually maintained copy.
  - Inspected all 16 app-project templates and the generated README/AGENTS handoff links. Generated records are forced to lifecycle `draft`; the README says the starter does not approve decisions or gates; the initializer separately states that it does not create GitHub repositories or initialize Git. The tool catalog identifies repository creation/permissions as separate work.
- **Post-record integrity checks:** After creating this review record, `python3 scripts/artifacts.py validate` — **PASS**, `Validated 31 artifact(s).`; focused relative-link resolution across the reviewed Markdown references and this record — **PASS**, 11 local links checked, none broken; `git diff --check -- docs/adversarial-reviews/FRAMEWORK-ADV-003.md` — **PASS**, no output.
- **Verification limits:** The exclusive-create test establishes no clobbering for a colliding generated file. It does not make the multi-file initialization transactional; an unrelated filesystem error can leave a partial target, which CAP-004 tells the operator to inspect before retrying. This is documented behavior, not a new finding in the requested scope.

## Final gate result

- **Result:** **PASS**.
- **Why this result follows the criteria:** Both initial Major findings were corrected and independently verified across the full requested scope. The current generated artifact IDs and local related-artifact references are valid; the concurrent-file collision does not overwrite user content; the generated records make no false approval claims; and canonical `design.md` remains distinct from reviewed Impeccable output. No unresolved Blocking or Major findings remain. The implementation's GitHub boundary and possible partial output on unrelated filesystem failure are explicitly disclosed.
- **Approval:** No owner residual-risk acceptance used. This result is the independent review gate evidence, not a product-owner decision or deployment authorization.
- **Next action / owner:** Framework owner may use CAP-004 after preserving the reviewed working-tree versions in Git. No owner decision is needed to resolve these findings.

## References

- [CAP-004 — App Repository Bootstrap](../../framework/capabilities/CAP-004-app-repository-bootstrap.md)
- [App-project starter guide](../templates/app-project/README.md)
- [FRAMEWORK-001](../constitution/FRAMEWORK-001.md) and [FRAMEWORK-002](../constitution/FRAMEWORK-002.md)
- [Framework v1 lifecycle workflow](../../workflows/lifecycle.md)
- [Framework gate catalog](../framework/GATE-CATALOG-001.md) and [tool/skill catalog](../framework/TOOL-CATALOG-001.md)
