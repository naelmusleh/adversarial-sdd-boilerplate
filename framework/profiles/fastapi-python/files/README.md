# Synthetic FastAPI / Python profile

This isolated module exists only to exercise FW-013 profile composition and the accepted `GalleryItemV1` compatibility fixture. It does not implement Infinite Gallery or select a stack for that product.

profile-instructions: fastapi-python

- Profile: `fastapi-python@1.0.0`
- Runtime: CPython `>=3.10`
- Source layout: `src/`; tests: `tests/`
- Direct pins: FastAPI `0.157.0`, pytest `9.1.1`, HTTPX `0.28.1`
- Checks: compile source and run the named compatibility tests.
- Persistence and storage checks: unsupported by this fixture.

Install this module's requirements before running its tests. Initialization records checks as `not-run`; it does not install dependencies or execute profile code.
