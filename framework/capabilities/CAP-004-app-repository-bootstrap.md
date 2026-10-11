---
id: CAP-004
type: framework-capability
title: App Repository Bootstrap
status: active
version: 0.5
created: 2026-10-08
updated: 2026-10-11
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001
---

# CAP-004 — App Repository Bootstrap

## Need

A new application needs its own repository and a useful SDD starting point without inheriting another application's content or accidentally claiming that decisions and gates are approved.

## User

The product owner and AI agents starting a new application project.

## Capability boundary

CAP-004 locally generates a documented app-repository starter from template-source files. By default it creates five canonical SDD artifacts plus README, AGENTS, `.gitignore`, and a copied helper; an explicit option pre-seeds supporting lifecycle records. It substitutes a project name, ID prefix, date, and template source URL; every generated artifact starts in `draft`. It refuses a non-empty target and does not create a GitHub repository, initialize Git, set permissions, choose application providers, or approve requirements, decisions, reviews, or release gates.

## Inputs and outputs

- **Inputs:** application name, unique artifact prefix, new/empty target directory, and optional HTTPS framework repository URL.
- **Default outputs:** five canonical SDD artifacts (`mission.md`, `constitution.md`, `specification.md`, `design.md`, `backlog.md`), README, AGENTS, `.gitignore`, and an app-root-aware copy of the dependency-free artifact CLI (nine files total).
- **Optional outputs:** `--include-lifecycle-records` adds decision, review/gate, feasibility/architecture, verification/release, and operations starter records (20 files total).
- **Next action:** the owner gives the agent the app idea, intended user, available problem evidence, desired outcome, and constraints; the agent drafts `mission.md` and leads product discovery in the app repository.

## Safety and failure behavior

- Reject an invalid ID prefix, non-HTTPS framework URL, symlink target, non-directory target, or target containing files.
- Validate all source templates and the local artifact helper exist before writing any output.
- The copied helper discovers the app's root canonical SDD files and artifact directories, excludes non-artifact project instructions and Impeccable outputs, and writes new artifacts only into app-owned directories.
- Keep canonical SDD `design.md` separate from Impeccable generated output; the generated app instructions require isolated staging for the `document` command.
- Do not embed requirements or owner-specific decisions from another application.
- An incomplete write reports the filesystem error; the operator inspects the target before retrying.

## Evidence and limits

Implementation: [`scripts/init_app_project.py`](../../scripts/init_app_project.py) and [`scripts/artifacts.py`](../../scripts/artifacts.py). The initializer has a lean default and an explicit full scaffold. The former 21-file output included an unnecessary empty Impeccable directory; the optional full profile is now 20 files with 16 valid metadata IDs in `draft`, while the default is nine files with five canonical SDD IDs. Local regression tests cover both profiles, helper validation, dry-run behavior, refusal to overwrite a non-empty target, and downloaded-source use without `.git`. Independent review FRAMEWORK-ADV-007 passed the profile split and generated README corrections. The FW-TASK-008 cold-start checklist records fresh app initialization, app-local artifact discovery/validation, next-action clarity, and current template-link fixes. This capability does not create a GitHub repository, initialize Git, or provide a starter migration/update mechanism. A starter refresh must be reviewed and manually applied to avoid overwriting application-owned artifacts.

## References

- [App-project setup instructions](../../README.md#start-a-brand-new-application-from-scratch)
- [Framework v1 specification](../../docs/framework/FRAMEWORK-SPEC-001.md)
- [Framework v1 backlog](../../docs/framework/FRAMEWORK-BACKLOG-001.md)
- [FRAMEWORK-ADV-007 — Independent app starter profile review](../../docs/adversarial-reviews/FRAMEWORK-ADV-007.md)
