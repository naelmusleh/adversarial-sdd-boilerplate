---
id: FRAMEWORK-001
type: framework-constitution
title: Adversarial SDD principles and quality bar
status: active
version: 1.2
created: 2026-10-05
updated: 2026-10-10
---

# FRAMEWORK-001 — Principles and quality bar

## Purpose

This constitution defines durable principles for the reusable Adversarial SDD template. The process makes AI-led software delivery understandable, challengeable, and traceable while keeping human attention focused on decisions that need human judgment.

## Principles

1. **Artifacts are the durable record.** Chat is a collaboration surface, not the project archive. Durable requirements, decisions, reviews, plans, and delivery evidence live in repository artifacts with stable IDs and version history.
2. **Work from explicit intent.** Agents receive a clear mission, relevant requirements, constraints, and acceptance criteria. They distinguish facts, owner decisions, and inferences. Unresolved choices are recorded rather than silently guessed.
3. **Challenge before commitment.** Important requirements and designs receive an independent adversarial review. Reviews look for missing cases, contradictions, abuse, operational failure, accessibility gaps, and disconfirming evidence. A review does not make product decisions for the owner.
4. **AI does the implementation work.** The lifecycle enables agents to produce specifications, code, documentation, and verification evidence. The owner contributes goals, material product choices, acceptance, and authorization; routine implementation is not delegated back to the owner.
5. **Human accountability stays clear.** Agents report changes and evidence. The owner remains the authority for product acceptance and unresolved product decisions. High-impact choices are explicit and reviewable.
6. **Traceability is continuous.** Stable IDs connect missions, requirements, decisions, reviews, specifications, work items, changes, and evaluations. Completion claims point to evidence.
7. **Build only what the next step needs.** Use real work to expose process gaps, then build the smallest reusable capability that removes a demonstrated gap.
8. **Quality includes operation.** Specifications consider security, privacy, accessibility, reliability, observability, cost, maintainability, and recovery where relevant.
9. **Quality reviews are gates.** Required reviews govern lifecycle transitions. Resolve findings and rerun before advancing, or record an owner-approved residual risk where the gate permits it. A score is never a pass.
10. **Keep project boundaries explicit.** The template owns reusable process and starter material. Each application repository owns that app's product requirements, code, infrastructure, secrets, data, release history, and operations evidence.

## Quality bar

Before work is marked complete, record the artifact IDs and criteria addressed, changes and links, actual verification and its result (or why it could not run), limitations, unresolved decisions, and follow-up work. Never claim a check passed without observing it. Never present a proposal or inference as an accepted owner decision.

## Changes to this constitution

Propose changes as a decision or reviewable change. Explain motivation and affected artifacts. Keep this file focused on durable principles; put operational procedure in workflow documents.
