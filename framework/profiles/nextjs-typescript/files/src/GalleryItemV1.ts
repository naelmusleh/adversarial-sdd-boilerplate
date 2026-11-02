export type GalleryItemV1 = {
  schema_version: "1";
  item_id: string;
  content_type: string;
  byte_size: number;
  state: "active" | "remove_requested";
};

export function isGalleryItemV1(value: unknown): value is GalleryItemV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return false;
  const item = value as Record<string, unknown>;
  return item.schema_version === "1"
    && typeof item.item_id === "string" && item.item_id.length > 0
    && typeof item.content_type === "string" && item.content_type.length > 0
    && typeof item.byte_size === "number" && Number.isInteger(item.byte_size) && item.byte_size > 0
    && (item.state === "active" || item.state === "remove_requested");
}

export function isVisibleInCollection(item: GalleryItemV1): boolean {
  return item.state === "active";
}
