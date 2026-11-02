# Synthetic Next.js / TypeScript profile

This isolated module exists only to exercise FW-013 profile composition and the accepted `GalleryItemV1` compatibility fixture. It does not implement Infinite Gallery or select a stack for that product.

profile-instructions: nextjs-typescript

- Profile: `nextjs-typescript@1.0.0`
- Runtime: Node.js `>=22.12.0`; npm `>=10.9.0`
- Language: TypeScript `5.9.3`
- Source layout: `src/`; tests: `tests/`
- Checks: `npm --prefix profiles/nextjs-typescript run typecheck` and `npm --prefix profiles/nextjs-typescript test`
- Browser and device checks: unsupported by this fixture.

Install dependencies in this module before running its checks. Initialization records declared checks as `not-run`; it does not install dependencies or execute profile code.
