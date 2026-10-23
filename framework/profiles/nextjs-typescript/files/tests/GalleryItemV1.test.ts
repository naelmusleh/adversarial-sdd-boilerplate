import { describe, expect, it } from "vitest";
import { isGalleryItemV1, isVisibleInCollection } from "../src/GalleryItemV1";

const valid = { schema_version: "1", item_id: "sample-item-0001", content_type: "image/jpeg", byte_size: 2048, state: "active" } as const;

describe("synthetic GalleryItemV1 compatibility fixture", () => {
  it("accepts the valid example and preserves its identifier", () => {
    expect(isGalleryItemV1(valid)).toBe(true);
    if (isGalleryItemV1(valid)) expect(valid.item_id).toBe("sample-item-0001");
  });
  it("rejects missing identifiers, zero sizes, and unsupported majors", () => {
    expect(isGalleryItemV1({ ...valid, item_id: undefined })).toBe(false);
    expect(isGalleryItemV1({ ...valid, byte_size: 0 })).toBe(false);
    expect(isGalleryItemV1({ ...valid, schema_version: "2" })).toBe(false);
  });
  it("ignores unknown optional fields and hides removal requests", () => {
    expect(isGalleryItemV1({ ...valid, optional_future: true })).toBe(true);
    expect(isVisibleInCollection({ ...valid, state: "remove_requested" })).toBe(false);
  });
});
