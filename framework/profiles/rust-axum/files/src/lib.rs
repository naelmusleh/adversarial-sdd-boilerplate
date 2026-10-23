use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize, PartialEq, Eq)]
pub struct GalleryItemV1 {
    pub schema_version: String,
    pub item_id: String,
    pub content_type: String,
    pub byte_size: i64,
    pub state: String,
}

impl GalleryItemV1 {
    pub fn is_valid(&self) -> bool {
        self.schema_version == "1"
            && !self.item_id.is_empty()
            && !self.content_type.is_empty()
            && self.byte_size > 0
            && matches!(self.state.as_str(), "active" | "remove_requested")
    }

    pub fn is_visible_in_collection(&self) -> bool {
        self.state == "active"
    }
}

pub fn parse_gallery_item(input: &str) -> Result<GalleryItemV1, serde_json::Error> {
    let item: GalleryItemV1 = serde_json::from_str(input)?;
    if !item.is_valid() {
        return Err(<serde_json::Error as serde::de::Error>::custom(
            "payload does not satisfy the GalleryItemV1 contract",
        ));
    }
    Ok(item)
}
