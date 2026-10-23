---
id: FRAMEWORK-EXERCISE-007
type: framework-exercise
title: Multi-platform sample contract for profile composition
status: draft
version: 0.2
created: 2026-10-22
updated: 2026-10-22
related-artifacts: FRAMEWORK-SPEC-001, FRAMEWORK-BACKLOG-001, DECISION-LOG-001, DECISION-023, DECISION-024
---

# FRAMEWORK-EXERCISE-007 — Multi-platform sample contract for profile composition

## Purpose and status

This is a small framework fixture contract for FW-TASK-013. It helps test explicit platform applicability, stack-profile isolation, and a stable module interface. It is not an Infinite Gallery implementation plan or an app requirements amendment. The contract remains a draft and cannot unblock FW-TASK-013 until an independent review is recorded and the owner accepts this exact revision.

## Provenance and boundaries

| Statement | Provenance | Treatment |
|---|---|---|
| Infinite Gallery is for one owner, privately hosted, and browsed on phone and desktop browsers. | Owner-approved v0.6 scope, confirmed in this conversation. | Product source fact for the web lane only. The v0.6 source file is not in this framework checkout; this summary is not a byte-level reconciliation. |
| The gallery supports adding/removing pictures, playful looping browse behavior, and a collection target around 1,000 pictures. | Owner-approved requirements confirmed in this conversation. | Product source facts for the web lane only; the exercise does not re-specify detailed UX, provider, data model, or release behavior. |
| Native iOS and Android lanes. | Framework fixture choice authorized by DECISION-024. | Synthetic only. They exist to exercise platform applicability and do not add native apps, parity promises, or work to Infinite Gallery. |
| Three module assignments below. | Framework fixture choice authorized by DECISION-024 and derived from FW-TASK-013's approved stack list. | Synthetic examples only. They do not select an architecture, provider, or implementation stack for Infinite Gallery. |
| Real images, credentials, storage providers, deployments, and app runtime checks. | Outside this exercise. | Excluded. All payload values are synthetic metadata; no real photos or secrets are used. |

## Sample slice

The fictional slice is **register one image item, show its metadata in a collection, and request its removal**. The contract transfers metadata only; binary image bytes and storage behavior are outside the fixture. `remove_requested` is a logical collection state, not a claim of immediate physical purge or backup erasure. Product deletion and backup-retention behavior remain governed by the approved Infinite Gallery specification.

## Platform applicability

| Target | Status in this exercise | Applicable contract behavior | Explicitly not established |
|---|---|---|---|
| Responsive web, phone browser | Owner-approved product target; sample contract fixture | Register, list, and request removal through the shared metadata contract | Browser/device compatibility evidence, hosted behavior, auth/storage implementation, or gate PASS |
| Responsive web, desktop browser | Owner-approved product target; sample contract fixture | Same metadata contract and identifiers as phone browser | Desktop runtime evidence or independent quality claim |
| Native iOS | Synthetic fixture lane only | Demonstrate that the platform row points to the same stable interface and preserves artifact/requirement identity | Infinite Gallery native scope, Swift implementation, native checks, parity, or release |
| Native Android | Synthetic fixture lane only | Demonstrate that the platform row points to the same stable interface and preserves artifact/requirement identity | Infinite Gallery native scope, Kotlin implementation, native checks, parity, or release |

Native rows have no selected language/runtime profile and no executable native checks in this exercise. A consumer that requests such checks must report them as `unsupported` or `not_configured`; it must not silently skip them or mark them passed. This fixture therefore demonstrates applicability reporting, not native support.

## Synthetic module/profile mapping

| Module | Example profile | Sample responsibility | Version/prerequisite boundary | Unsupported or unverified here |
|---|---|---|---|---|
| Web client | `sample-next-ts@0.1`; Next.js 15 / TypeScript 5 | Validate and display metadata; send register/list/remove requests | Example versions follow the framework starter baseline; profile package and commands are not implemented by this exercise | Browser/device execution, actual app build, auth, upload transport, accessibility, and runtime checks |
| Metadata API | `sample-fastapi-py@0.1`; Python 3.10+ / FastAPI | Validate the versioned JSON contract and return collection state | Python minimum follows the framework's documented helper baseline; FastAPI version and executable profile are not selected here | Service execution, persistence, authorization, API security, and provider behavior |
| Metadata adapter | `sample-axum-rs@0.1`; Rust stable / Axum | Independently consume/produce the same versioned metadata envelope as a composition fixture | Rust toolchain pin, Axum version, and executable profile are intentionally unset pending FW-013's profile contract | Compilation, runtime, storage, image processing, and production use |
| Native clients | No language profile selected | Applicability-only fixture rows | No toolchain or prerequisites declared because no native code is in scope | All native execution and quality checks |

These are isolated examples, not three services that the Gallery must adopt. A profile that lacks declared versions or executable checks is not considered supported by this exercise. The eventual FW-013 profile contract must pin its own toolchain/prerequisites and report unavailable checks truthfully before claiming that profile support.

## Cross-module interface: `GalleryItemV1`

The interface represents metadata only. All modules use UTF-8 JSON and preserve the exact `item_id` across requests and responses. `schema_version` is the literal string `1`; producers MUST NOT add fields to version 1 that change existing field meaning. Consumers MUST ignore unknown optional fields and MUST reject an unsupported major schema version. A breaking field/type/meaning change requires `GalleryItemV2`. This fixture defines compatibility behavior for sample payloads only; it does not claim a deployed retention window or migration policy.

| Field | Type | Rule |
|---|---|---|
| `schema_version` | string | Required. Exactly `1` |
| `item_id` | string | Required. Non-empty synthetic opaque identifier; stable across modules |
| `content_type` | string | Required. Non-empty media-type label; this fixture does not define a product format allowlist or conversion guarantee |
| `byte_size` | integer | Required. Positive integer. This interface fixture does not resolve whether the product's “50 MB” limit is decimal or binary; the application contract must retain that decision explicitly. |
| `state` | string | Required. `active` or `remove_requested` |

All five fields are required in v1; no field is optional. A payload missing any field, with an invalid type/value, or using an unsupported `schema_version` is rejected. Unknown additional fields are ignored by v1 consumers and MUST NOT change known-field meaning. `remove_requested` is terminal for this interface version: the item MUST be omitted from collection-list results and clients MUST stop rendering it immediately. It MUST NOT transition back to `active`; restoring a picture requires registering a new item with a new `item_id`. This is active-gallery behavior only and makes no statement about physical storage deletion, backup retention, or erasure timing.

For a list operation, the response's `items` array contains only records whose `state` is `active`. A successful removal request returns the same item with state `remove_requested` for acknowledgement; clients remove it from the visible collection without waiting for physical purge.

### Valid example

```json
{
  "schema_version": "1",
  "item_id": "sample-item-0001",
  "content_type": "image/jpeg",
  "byte_size": 2048,
  "state": "active"
}
```

### Invalid examples

Missing required identifier:

```json
{
  "schema_version": "1",
  "content_type": "image/jpeg",
  "byte_size": 2048,
  "state": "active"
}
```

Out-of-range size:

```json
{
  "schema_version": "1",
  "item_id": "sample-item-0002",
  "content_type": "image/jpeg",
  "byte_size": 0,
  "state": "active"
}
```

The valid/invalid examples are contract examples only; they are not executed against any app or runtime in this exercise. A complete FW-013 implementation must supply executable schema fixtures and compatibility tests.

Expected collection result after removal: the removed `item_id` is absent from the returned `items` array. The acknowledgement record is not itself a list result.

## Adversarial review and disposition

| Risk | Current mitigation | Remaining evidence |
|---|---|---|
| Synthetic native targets leak into Gallery scope | Every native row is marked fixture-only and lists excluded claims | Independent review to confirm the boundary |
| Example stacks are mistaken for an app architecture | The mapping is labeled synthetic and says no app stack is selected | Independent review to confirm the boundary |
| Owner-confirmed facts are not reconciled to the original v0.6 file | Provenance row records that only conversation-confirmed summaries were available | Owner/reviewer to confirm the summary is faithful before acceptance |
| Unsupported checks could be misreported as passing | Native rows specify `unsupported` / `not_configured`; no runtime claim is made | FW-013 fixtures must verify actual reporting behavior |
| Version 1 compatibility is underspecified for deployed consumers | Compatibility applies to sample payloads only; no deployed retention or migration policy is claimed | FW-013 must define concrete compatibility policy before implementation |

### Independent review round 1 (2026-10-22)

Reviewer `/root/infinite_gallery_reviewer` assessed v0.1 against DECISION-024 and FW-TASK-032. Platform/provenance boundaries and synthetic profile assignments passed within their stated limits. The reviewer raised one major finding on AC-4: required/optional fields and `remove_requested` list/render behavior were ambiguous. The reviewer recommended marking every v1 field required, defining removal as immediately non-active/non-listable/non-renderable, and prohibiting reactivation. The author accepted the finding and applied those clarifications above. No stack, provider, native app, physical deletion, or backup-retention decision was added.

The review record and owner-acceptance state for this artifact are maintained in the FW-TASK-032 section of [FRAMEWORK-BACKLOG-001](FRAMEWORK-BACKLOG-001.md). This document alone does not assert G-REQ PASS or establish itself as an approved FW-TASK-013 prerequisite. Any acceptance must name the exact artifact revision and digest.
