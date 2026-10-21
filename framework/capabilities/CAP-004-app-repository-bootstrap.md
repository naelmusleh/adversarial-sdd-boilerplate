---
id: CAP-004
type: framework-capability
title: App Repository Bootstrap
status: active
version: 0.7
created: 2026-10-08
updated: 2026-10-21
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
- **Default outputs:** five canonical SDD artifacts, README, AGENTS, `.gitignore`, app-local artifact/CI helpers, framework lock and trust/check manifests, handoff and gate-run templates/schemas, and the SDD Contract Validation workflow (25 files total).
- **Optional outputs:** `--include-lifecycle-records` adds decision, review/gate, feasibility/architecture (including the architect handshake), verification/release, and operations starter records (37 files total).
- **Next action:** the agent first inspects the new app repository and labels observed facts, owner statements, researched claims, inferences, and unknowns. The owner may start with a short product idea and mark missing details unknown; the agent drafts `mission.md`, asks only material unresolved questions, and continues unaffected discovery. A new-app initializer is never run against an existing/non-empty app repository; existing repositories are inspected and migrated only through a separate reviewed task.

## Safety and failure behavior

- Reject an invalid ID prefix, non-HTTPS framework URL, non-exact framework revision, symlink target, non-directory target, or target containing files.
- Validate all source templates and the local artifact helper exist before writing any output.
- The copied helper discovers the app's root canonical SDD files and artifact directories, excludes non-artifact project instructions and Impeccable outputs, and writes new artifacts only into app-owned directories.
- The framework lock records the immutable source revision and digests of the copied helper, both handoff templates, the gate-record template, and generated SDD validation workflow. Handoff validation checks frozen artifacts; changing these files requires a reviewed lock update.
- The README's framework-template composition uses no-clobber copying so shared templates do not overwrite initializer-rendered, lock-digested app files. Revalidate the app after composing the framework folders.
- The generated workflow runs SDD validation only. The app must separately define stack-specific code checks and configure required status checks in repository settings before calling them merge-blocking or release controls.
- Keep canonical SDD `design.md` separate from Impeccable generated output; the generated app instructions require isolated staging for the `document` command.
- Do not embed requirements or owner-specific decisions from another application.
- Do not require a fixed intake questionnaire or force a stack, provider, platform, region, budget, or license choice before evidence and product scope require it. Detailed system/provider feasibility is recorded in the app's canonical requirements/decision records and later G-FEAS evidence, not in a duplicate setup tracker.
- On resumed setup, inspect current canonical artifacts and repository state; ask only about changed context or newly relevant unresolved decisions. Preserve unaffected accepted decisions and never infer a gate PASS from generated files, validation success, or a prior conversation.
- An incomplete write reports the filesystem error; the operator inspects the target before retrying.

## Evidence and limits

Implementation: [`scripts/init_app_project.py`](../../scripts/init_app_project.py) and [`scripts/artifacts.py`](../../scripts/artifacts.py). The initializer has a lean default and an explicit full scaffold. The default creates 25 files with five canonical SDD artifacts and locked governance support; the optional full profile creates 37 files with supporting lifecycle records. Local regression tests cover both profiles, exact revision pinning, app-local validation, dry-run behavior, refusal to overwrite a non-empty target, and source archives with an explicitly supplied commit SHA. Product discovery instructions provide progressive intake and repository preflight; they are agent procedures, not a filesystem sandbox or an automatic proof of truth. The generated SDD workflow does not run app code checks or configure GitHub branch protection. Existing application repositories still require a reviewed path-specific migration; this capability does not overwrite or migrate them automatically.

## References

- [App-project setup instructions](../../README.md#start-a-brand-new-application-from-scratch)
- [Framework v1 specification](../../docs/framework/FRAMEWORK-SPEC-001.md)
- [Framework v1 backlog](../../docs/framework/FRAMEWORK-BACKLOG-001.md)
- [FRAMEWORK-ADV-007 — Independent app starter profile review](../../docs/adversarial-reviews/FRAMEWORK-ADV-007.md)
