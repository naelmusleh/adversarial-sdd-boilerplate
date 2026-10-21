---
id: CAP-004
type: framework-capability
title: App Repository Bootstrap
status: active
version: 0.6
created: 2026-10-08
updated: 2026-10-20
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001
---

# CAP-004 — App Repository Bootstrap

## Need

A new application needs its own repository and a useful SDD starting point without inheriting another application's content or accidentally claiming that decisions and gates are approved.

## User

The product owner and AI agents starting a new application project.

## Capability boundary

CAP-004 locally generates a documented app-repository starter from template-source files. By default it creates five canonical SDD artifacts plus README, AGENTS, `.gitignore`, a copied helper, a framework revision lock, G-REQ/G-ARCH manifest templates, and an app-local SDD validation workflow. An explicit option pre-seeds supporting lifecycle records. It substitutes a project name, ID prefix, date, framework repository URL, and exact framework commit; every generated artifact starts in `draft`. It refuses a non-empty target and does not create a GitHub repository, initialize Git, set permissions, choose application providers, or approve requirements, decisions, reviews, or release gates.

## Inputs and outputs

- **Inputs:** application name, unique artifact prefix, new/empty target directory, optional HTTPS framework repository URL, and the exact framework commit SHA when invoked from a source archive.
- **Default outputs:** five canonical SDD artifacts, README, AGENTS, `.gitignore`, the app-local artifact CLI, `.sdd/framework.lock.json`, G-REQ/G-ARCH manifest templates, a gate-record template, and the SDD Contract Validation workflow (14 files total).
- **Optional outputs:** `--include-lifecycle-records` adds decision, review/gate, feasibility/architecture (including the Step 2 architect handshake), verification/release, and operations starter records (26 files total).
- **Next action:** the owner gives the agent the app idea, intended user, available problem evidence, desired outcome, and constraints; the agent drafts `mission.md` and leads product discovery in the app repository.

## Safety and failure behavior

- Reject an invalid ID prefix, non-HTTPS framework URL, non-exact framework revision, symlink target, non-directory target, or target containing files.
- Validate all source templates and the local artifact helper exist before writing any output.
- The copied helper discovers the app's root canonical SDD files and artifact directories, excludes non-artifact project instructions and Impeccable outputs, and writes new artifacts only into app-owned directories.
- The framework lock records the immutable source revision and digests of the copied helper, both handoff templates, the gate-record template, and generated SDD validation workflow. Handoff validation checks frozen artifacts; changing these files requires a reviewed lock update.
- The generated workflow runs SDD validation only. The app must separately define stack-specific code checks and configure required status checks in repository settings before calling them merge-blocking or release controls.
- Keep canonical SDD `design.md` separate from Impeccable generated output; the generated app instructions require isolated staging for the `document` command.
- Do not embed requirements or owner-specific decisions from another application.
- An incomplete write reports the filesystem error; the operator inspects the target before retrying.

## Evidence and limits

Implementation: [`scripts/init_app_project.py`](../../scripts/init_app_project.py) and [`scripts/artifacts.py`](../../scripts/artifacts.py). The initializer has a lean default and an explicit full scaffold. The default now creates 14 files with five canonical SDD IDs; the optional full profile creates 26 files with 17 valid metadata IDs. Local regression tests cover both profiles, exact revision pinning, app-local validation, dry-run behavior, refusal to overwrite a non-empty target, and source archives with an explicitly supplied commit SHA. The generated SDD workflow does not run app code checks or configure GitHub branch protection. Existing application repositories still require a reviewed path-specific migration; this capability does not overwrite or migrate them automatically.

## References

- [App-project setup instructions](../../README.md#start-a-brand-new-application-from-scratch)
- [Framework v1 specification](../../docs/framework/FRAMEWORK-SPEC-001.md)
- [Framework v1 backlog](../../docs/framework/FRAMEWORK-BACKLOG-001.md)
- [FRAMEWORK-ADV-007 — Independent app starter profile review](../../docs/adversarial-reviews/FRAMEWORK-ADV-007.md)
