---
id: TOOL-CATALOG-001
type: framework-tool-catalog
title: Framework skill, plugin, and tool routing
status: draft
version: 0.3
created: 2026-10-07
updated: 2026-10-08
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, WORKFLOW-LIFECYCLE-001, DECISION-017
---

# TOOL-CATALOG-001 — Framework skill, plugin, and tool routing

## Purpose and freshness

This catalog lists integration adapters observed in the reference Codex workspace as of 2026-10-07. It is not a prerequisite list. The core framework is Markdown, Git, and Python standard-library scripts; it can be followed by a human or any AI agent from a local checkout without ChatGPT Desktop or a paid desktop runtime. The catalog is an environment-specific snapshot, not a guarantee that every app repository, host, plan, permission, plugin version, or external account has access. At each app project, verify availability, configuration, access, and version before relying on an adapter.

## Routing table

| Capability | Lifecycle use | What it can contribute | Limits and required proof |
| --- | --- | --- | --- |
| **App starter initializer (`scripts/init_app_project.py`)** | Project setup after the owner selects an app name, artifact prefix, and repository target. | Generates a separate app SDD tree, agent instructions, status README, an app-root-aware copy of `scripts/artifacts.py`, and links to current framework workflows; starts artifacts in draft and refuses non-empty targets. | Local file creation only. It does not create GitHub repositories, initialize Git, set permissions, select app technology/providers, or pass gates. Review the generated files and verify repository access separately. |
| **SDD Product Architect skill** | Requirements/specification and CX matrix preparation. | Drafts constitution/specification/backlog from supplied requirements; can derive interaction contracts/matrices. | Its default save instructions assume shared Space storage. In this repository-first process, save only to the explicitly selected app repository; do not let tool output establish an alternate source of truth. Review all decisions and links. |
| **Product Design plugin/skill** | Discovery research, flow audit, design alternatives, prototype/exploration, and UX assessment when useful. | Adds product-design research, screenshot-based journey audits, ideation, and visual implementation methods. | It is not the canonical requirements repository or a replacement for Figma when the project selects Figma as review surface. Record exact evidence and distinguish generated exploration from accepted design. |
| **Impeccable skill/commands** | Optional adapter for product context, feature shaping, UX critique, targeted refinement, and implemented web/native audits. | `init`, `shape`, `critique`, `audit`, `audit.native`, `polish`, and relevant focused commands such as `bolder`, `adapt`, `harden`, `onboard`, and `clarify`. | G-CX is mandatory for every app; Impeccable `critique` is required when that app selects it. Other app projects may use the tool-neutral G-CX procedure. Scores do not pass gates. `audit`/`audit.native` require implemented targets. Hooks are optional, must be configured and proven active, and do not monitor Figma API edits. `document` writes `DESIGN.md` at project root in the installed version; follow the collision-safe staging procedure in D-FW-05. |
| **Figma skills and connector** | Create/update/read design files, variables/components, prototype pages/flows, and inspect rendered evidence. | Figma file operations and design-to-code context when the project uses Figma. | File visibility/permission and the available connector methods must be checked in the actual task. Figma screens do not prove runtime behavior, service integrations, device accessibility, or shipped parity. |
| **Codex repository agent / shell tools** | Documentation, code changes, local checks, review preparation, and repository workflows. | Inspect and edit project files, run project-prescribed commands, preserve Git diff evidence. | Availability is local to a host/worktree; branch, credentials, network, and sandbox access vary. A command's presence does not mean its external action is authorized. |
| **GitHub connection / `gh` CLI** | Repository initialization, versioned collaboration, pull requests, CI records, and review. | GitHub repository and change-management operations when authenticated and permitted. | Verify account, organization/repository authorization, scopes, remote, and operation-specific permission at setup. Never expose token values. CI/deployment behavior is app-specific. |
| **`execute-sdd-coder` skill** | Possible implementation aid only when its target app explicitly adopts its contract. | Implements one selected backlog task and updates its milestone under its specified path assumptions. | The installed skill requires an exact activation phrase, assumes `.codex-specs/` files, and contains finance/database-specific rules. It is not the generic CAP-003 workflow; do not use it as the default for unrelated apps. |
| **Provider-specific CI, hosting, identity, data, analytics, support tools** | App architecture, verification, release, and operations. | Concrete app-dependent implementation and production evidence. | None is selected globally. Choose from app requirements and feasibility evidence; verify entitlements, contracts, security, cost, and access in that app. |

## Lifecycle routing

1. Use the app starter initializer only after selecting a new/empty app-repository target; review the generated artifacts and establish owner/access details.
2. Use the SDD Product Architect to draft or refine artifacts only after recording canonical app paths and open decisions.
3. Use research/Product Design where evidence or experience exploration benefits; save conclusions and accepted decisions in canonical app artifacts.
4. For CX, run mandatory G-CX using the app's selected evaluator. Use Figma if selected and Product Design audit where useful. If Impeccable is adopted, run its `critique` gate; otherwise follow GATE-CATALOG-001's tool-neutral critique procedure. Apply `bolder`, `adapt`, `harden`, `onboard`, `clarify`, or other Impeccable commands only when findings warrant them; rerun the full affected gate.
5. Use architecture/implementation agents against approved app-repository tasks; preserve project instructions and use CAP-003 as the generic contract.
6. Use app-selected CI/device/security/operations tooling for real runtime proof; record unavailable checks rather than substituting design-time evidence.

## App project tool verification record

Before depending on a capability, an app project records:

- Tool/skill name and installed version/host.
- Account/repository/project connection and required permission (without secret material).
- Exact supported target/scope and incompatible or unverified behavior.
- Hook/configuration location and a benign proof of activation, when hooks are in scope.
- Owner for renewing access or replacing the tool if unavailable.

Recheck this list when the host, plugin version, project scope, account, or target platform changes.

## References

- [Framework specification](FRAMEWORK-SPEC-001.md)
- [Framework backlog](FRAMEWORK-BACKLOG-001.md)
- [Application lifecycle workflow](../../workflows/lifecycle.md)
- [AI engineering execution workflow](../../workflows/ai-engineering-execution.md)
- [CX design workflow](../../workflows/cx-design.md)
- [D-FW-05](FRAMEWORK-SPEC-001.md#d-fw-05)
