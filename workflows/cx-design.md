---
id: WORKFLOW-CX-001
type: workflow
title: Platform-aware CX Design Workflow
status: active
version: 0.7
created: 2026-10-05
updated: 2026-10-20
related-artifacts: FRAMEWORK-002, GATE-CATALOG-001, TOOL-CATALOG-001, FRAMEWORK-GATE-CONTRACT-001
---

# WORKFLOW-CX-001 — Platform-aware CX Design Workflow v0.6

**Capability:** CX design and interaction contracts
## Purpose

Produce customer and operator experiences that explain decisions, expose meaningful user controls, and feel at home on each supported platform. Use official Material 3 and Apple Human Interface Guidelines as continuing references, not one-time inspiration.

## Required sources

- [Material Design 3](https://m3.material.io/), especially the relevant guidance on foundations, accessibility, content design, layout, components, tokens, color, and interaction states.
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines), especially relevant principles, platform-specific patterns, components, inputs, layout, and accessibility guidance.

These are evolving sources. Before each substantial CX design or design-system decision, consult the current official pages relevant to that task. Record the page title, direct URL, access date, applicable platform, and the decision or requirement it informed. Do not claim compliance based only on having consulted a landing page.

## Procedure

1. Read the governing PRD, CX contract, product decisions, research, and prior reviews. Identify actors, decision jobs, user-adjustable thresholds, product-owned rules, trust boundaries, and open dependencies.
2. Define the experience coverage before drawing screens. Inventory applicable **public/foundational, account/access, core-task, conversion, support/exception, and retention/return** journeys. Include marketing/discovery, onboarding, authentication and recovery, account/settings, primary task, search/navigation, data entry/editing, help, failure/empty/unsupported states, save/return, and account exit/data controls where they apply. Mark exclusions with a reason; do not add irrelevant template flows merely for checklist completeness.
3. Create a journey inventory that identifies each active journey, its actor, entry condition, exit condition, platform, source page, state branches, and traceable CX requirement. Separate active source journeys from integrated review copies, synthesis, archives, and visual explorations. Maintain one source map so an owner or implementer can tell which page is authoritative and where to begin review.
4. Define flow continuity, not only screen coverage. For every primary journey, specify its start, action, system response, decision/confirmation gate, success destination, back/cancel path, interrupted state, and recovery path. Show where guest access ends and identity is requested; state what survives authentication or interruption and keep unspecified persistence policy open.
5. Identify supported surfaces and input modes. If they are undecided, record that dependency and avoid assuming native iOS, Android, or web behavior.
6. Consult applicable official Material 3 and Apple HIG pages. For Android or Material-based interfaces, apply relevant Material patterns; for native Apple interfaces, apply the relevant Apple platform patterns. For other surfaces, use them as references where helpful and state what is adopted.
7. Translate guidance into observable requirements: what the user sees, can do, and understands, including accessibility, responsiveness/adaptivity, focus and input behavior, loading, empty, partial, error, unknown, unsupported, and insufficient-evidence states as applicable.
8. Keep domain meaning, evidence labels, calculations, uncertainty, and decision logic consistent across surfaces. Allow platform conventions for navigation, controls, input, layout, and system features to differ where that improves familiarity. Feature parity means equivalent decision tasks and information, not identical layouts.
9. Design for both decision comprehension and visual character. Establish the brand/design system before assembling screens. Explain why the visual hierarchy, typography, color, layout, imagery, and interaction style fit this product and audience; do not default to generic cards or a category template. Do not copy a component or visual style without validating platform, content, accessibility, and task fit.
10. Record design decisions and unresolved conflicts in CX artifacts. Link each meaningful requirement to its product rationale, source decision, and, where relevant, the official guideline that informed it. Flag guidance that conflicts with product needs or another platform for an explicit decision.
11. When more than one channel or platform is in scope, create the complete cross-surface matrix as part of the agent’s work; do not ask the owner to draft parity. Cover each shared capability across every surface, identify intentional platform differences, define equivalent decision outcomes and accessible information, and mark unsupported or undecided behavior with its requirement/decision ID. Keep one canonical matrix in or linked from the app repository's `design.md`. If an adopted design tool requires another path, produce it only as a generated adapter from the canonical matrix; never ask a person to maintain both copies independently. Record adapter generation/evidence or state that the canonical file was used directly.
12. Build an editable, linked Figma prototype from the accepted journey inventory and matrix. Provide a clear start-here frame, source map, named flows, and clickable primary/back/recovery paths. Include platform-specific screens and decision-critical states, representative long/empty/partial/unsupported cases, and annotations for sample data, unresolved policies, and assumptions. Every screen used as a review destination must make its status clear; a Figma link without a navigable flow is not sufficient.
13. Run the mandatory G-CX critique gate after journey coverage and design direction are coherent. Use Impeccable `critique` when the app's own constitution or tool decision selects it; otherwise use the tool-neutral procedure in GATE-CATALOG-001. Critique the complete active journey set and design target, and record the evaluator/method, scope, rendered evidence, findings, severity, and evidence. A partly fixed, intentionally open, or unverified finding keeps the gate failed. Resolve findings in the design, then rerun the full scope and record fix evidence. A residual finding may pass only through documented owner acceptance of scope, risk, mitigation, and revisit condition; a high score cannot override open findings or missing journey/platform evidence. For local markup, use a supported detector and browser evidence. For a Figma-only target, inspect rendered frames and prototype links; report markup detection/overlay as inapplicable instead of implying the Figma canvas was scanned.
14. If the app adopts Impeccable hooks, enable them for supported UI source files and record a benign proof of activation. Hooks can monitor only their supported code files; they do not observe Figma canvas/API edits, which require a separate visual review pass. The core framework does not require hooks.
15. Before handoff, check that every in-scope capability maps to a journey and every journey has a source, requirements, start/exit, state/error/recovery coverage, and intended surfaces. Confirm accessible behavior, adjustable thresholds versus product rules, visual status labels, Figma link validity, and prototype navigation. Verify G-CX passed after the latest design revision using the evaluator required by that app. Record unresolved owner decisions and evidence gaps; do not present a prototype as implementation approval. If a blocking/major critique finding remains without an authorized exception, stop the handoff and mark the CX review `revision-required`.

## Impeccable command routing and gates

Use Impeccable commands as purpose-specific adapters at the lifecycle point where their output can affect a decision. Do not run every command on every screen, treat a command recommendation as a pass, or substitute one gate for another. The current command definitions and prerequisites in the installed Impeccable references remain authoritative; this table records how this framework routes them when that integration is adopted. G-CX itself is mandatory and tool-neutral as defined in GATE-CATALOG-001.

| Lifecycle point / gate | Command | Use it for | Completion evidence |
| --- | --- | --- | --- |
| Product context setup | `init` | Capture durable product context in `PRODUCT.md` when a new application project lacks it; revisit only when core product context materially changes. | Reviewed `PRODUCT.md` with product, audience, goals, constraints, and explicit unknowns. |
| Feature discovery, before UI planning or implementation | `shape [feature]` | Discover the feature’s job, audience, evidence, scope, states, interaction, constraints, and open decisions; return a design brief before code. | Owner-confirmed brief or clearly recorded assumptions and unresolved decisions. |
| Ordinary new work | `craft [feature]` | Deprecated alias for ordinary new-work requests. Route to the current new-work workflow; do not make `craft` a required gate. | The applicable current workflow’s evidence, not invocation of the deprecated alias. |
| Existing implementation documentation | `document` | Generate or refresh `DESIGN.md` from an existing codebase when design documentation is absent or stale. It does not author a Figma prototype. | `DESIGN.md` grounded in inspected implementation. |
| Reusable system extraction | `extract [target]` | Pull proven reusable tokens and components from a target implementation into the design system. Use after patterns exist; do not infer a system from a one-off mock. | Extracted tokens/components mapped to actual source patterns and reviewed for reuse. |
| UX design approval gate | `critique [target]` when adopted; otherwise G-CX procedure | Critique the complete active journey set and design target after coverage and design direction are coherent, and again after findings are addressed. Use the evaluator recorded in the app's own contract. | Critique record with method/tool and scope, evidence, prioritized findings, dispositions, and a full rerun that verifies fixes; otherwise G-CX remains failed. |
| Implemented UI technical QA gate | `audit [target]` | Check web implementation quality including accessibility, performance, responsive behavior, and theming. Run against actual code / representative browser states. | Recorded technical findings and evidence; resolve required findings and rerun before release. |
| Implemented native technical QA gate | `audit.native [target]` | Check iOS/Android implementation on relevant simulator, emulator, or hardware, including platform conformance, accessibility, performance, and adaptivity. | Per-platform audit evidence; resolve required findings and rerun before release. |
| Evidence-led repair after critique/audit | `clarify [target]` | Fix confusing labels, UX copy, and error messages. | Updated copy checked in context and relevant states. |
| Evidence-led repair after critique/audit | `layout [target]` | Fix spacing, rhythm, grouping, canvas/screen organization, and visual hierarchy. | Before/after structural or rendered evidence; no unintended overlaps or regressions. |
| Evidence-led repair after critique/audit | `adapt [target]` | Adapt an interface to additional device sizes, breakpoints, or screen contexts. | Representative supported sizes checked; native work uses the native adaptation guidance. |
| Evidence-led repair after critique/audit | `harden [target]` | Close production edge cases such as errors, localization, long/missing data, and interrupted states. | Relevant edge-state behavior and copy verified. |
| Evidence-led repair after critique/audit | `onboard [target]` | Improve first-run, empty, and activation experiences. | First-use and return paths reviewed against activation intent. |
| Evidence-led repair after critique/audit | `optimize [target]` | Diagnose and fix implementation performance issues. Do not use it as a visual polish substitute. | Relevant runtime or profiling evidence shows the issue addressed. |
| Targeted visual refinement | `bolder [target]` | Give a safe or bland direction more distinct character when critique shows insufficient visual identity. | Revised design still fits the accepted brand and product direction; critique is rerun if materially changed. |
| Targeted visual refinement | `quieter [target]` | Reduce visual aggression or stimulation when critique shows competing emphasis or excess intensity. | Revised hierarchy and emphasis reviewed in context. |
| Targeted visual refinement | `distill [target]` | Remove unnecessary complexity when it obscures the primary task or decision. | Removed elements are not required by mapped requirements or states. |
| Targeted visual refinement | `colorize [target]` | Add strategic color when a monochromatic interface weakens meaning or hierarchy. | Semantic color use, contrast, and status meaning verified. |
| Targeted visual refinement | `typeset [target]` | Improve typography hierarchy, legibility, and font choices. | Hierarchy and text behavior checked across representative lengths and sizes. |
| Targeted visual refinement | `animate [target]` | Add purposeful motion when it improves feedback or continuity. | Motion has a task purpose, respects reduced-motion needs, and is checked on the target platform. |
| Targeted visual refinement | `delight [target]` | Add product-appropriate personality or memorable details after core clarity and completion are sound. | Detail supports the experience without obscuring task, evidence, or accessibility. |
| High-concept visual exploration | `overdrive [target]` | Explore an intentionally unconventional visual direction only when the brief calls for it; present the concept and trade-offs for owner selection before committing it. | Selected direction is explicit; resulting experience is critiqued and audited as applicable. |
| Final refinement before release review | `polish [target]` | Make a holistic finish pass after targeted fixes, preserving accepted behavior, content, and visual direction. | Complete path and relevant states reviewed; accidental churn removed; then rerun affected gates. |

### Gate sequence and target limitations

1. Establish product context with `init` when needed; use `shape [feature]` to settle the feature brief before designing or coding. `document` and `extract` are conditional documentation/system-maintenance actions, not prerequisites for every feature.
2. Build the journeys and implementation from the accepted requirements. Apply only targeted refinement commands whose findings apply; `craft` is deprecated and is never a required gate.
3. Run the selected evaluator's complete-scope critique as the mandatory UX/design gate. For any meaningful design change made to address findings, finish the targeted repair and relevant quality pass, then rerun critique against the complete affected journey set. An unresolved finding blocks sign-off unless the app's policy permits and records an explicit owner-accepted residual-risk exception.
4. Run `audit [target]` for implemented web code and `audit.native [target]` for implemented native code. These technical checks are separate from the UX critique. Resolve required findings and rerun the relevant audit; a design score cannot substitute for technical evidence.
5. If a target is Figma-only, inspect its rendered frames, prototype transitions, and canvas geometry directly. Impeccable’s code detector, markup overlay, and code-only performance checks do not scan or monitor Figma API edits. Apply the relevant design command’s method to the Figma work only where the command supports that target, and describe the actual inspection evidence rather than claiming a CLI run. Hook monitoring applies to supported UI source files, not Figma canvas edits.

## Record format

Add a short “Design guidance reviewed” section to each substantial CX artifact:

| Source/page | Accessed | Applies to | CX decision or requirement |
| --- | --- | --- | --- |
| Official page title and direct link | YYYY-MM-DD | Surface/platform or general | Specific design consequence; identify open questions |

If the platform is not yet selected, say so and identify decisions that depend on it. Do not describe an unselected pattern as a committed implementation requirement.

## Cross-surface design

For each application, use its approved platform and parity decisions. The agent prepares the requirements-to-journey matrix and routes only unresolved owner decisions for review; the owner is not asked to perform the analysis work. Before implementation, create an editable, linked prototype or equivalent reviewable experience artifact. Record which surfaces and capabilities are in scope, intentional differences, and unverified runtime or device behavior.
