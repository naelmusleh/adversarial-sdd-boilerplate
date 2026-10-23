# Synthetic Rust / Axum profile

This isolated module exists only to exercise FW-013 profile composition and the accepted `GalleryItemV1` compatibility fixture. It does not implement Infinite Gallery or select a stack for that product.

profile-instructions: rust-axum

- Profile: `rust-axum@1.0.0`
- Toolchain: Rust `1.97.0` (rustc and cargo)
- Source layout: `src/`; tests: `tests/`
- Direct pins: Axum `0.8.9`, serde `1.0.228`, serde_json `1.0.145`
- Checks: `cargo check --manifest-path profiles/rust-axum/Cargo.toml` and `cargo test --manifest-path profiles/rust-axum/Cargo.toml`
- Persistence and storage checks: unsupported by this fixture.

Cargo resolves packages when the user runs the declared checks. Initialization records checks as `not-run`; it does not access a registry or execute profile code.
