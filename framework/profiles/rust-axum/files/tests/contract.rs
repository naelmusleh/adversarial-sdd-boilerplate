use fw013_rust_axum_profile::{parse_gallery_item, GalleryItemV1};

const VALID: &str = r#"{"schema_version":"1","item_id":"sample-item-0001","content_type":"image/jpeg","byte_size":2048,"state":"active"}"#;

#[test]
fn accepts_valid_example_and_preserves_identity() {
    let item = parse_gallery_item(VALID).expect("valid fixture");
    assert!(item.is_valid());
    assert_eq!(item.item_id, "sample-item-0001");
}

#[test]
fn rejects_missing_fields_zero_size_and_unsupported_major() {
    assert!(parse_gallery_item(r#"{"schema_version":"1","content_type":"image/jpeg","byte_size":2048,"state":"active"}"#).is_err());
    let zero = GalleryItemV1 { byte_size: 0, ..parse_gallery_item(VALID).unwrap() };
    assert!(!zero.is_valid());
    let major = GalleryItemV1 { schema_version: "2".to_owned(), ..parse_gallery_item(VALID).unwrap() };
    assert!(!major.is_valid());
}

#[test]
fn ignores_unknown_optional_fields_and_hides_removed_items() {
    let extended = VALID.trim_end_matches('}').to_owned() + ",\"optional_future\":true}";
    assert!(parse_gallery_item(&extended).unwrap().is_valid());
    let removed = GalleryItemV1 { state: "remove_requested".to_owned(), ..parse_gallery_item(VALID).unwrap() };
    assert!(!removed.is_visible_in_collection());
}
