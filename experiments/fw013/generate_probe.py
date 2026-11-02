"""Generate disposable, synthetic FW-013 feasibility probe projects."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: generate_probe.py <empty-directory-under-RUNNER_TEMP>")

    runner_temp_value = os.environ.get("RUNNER_TEMP")
    if not runner_temp_value:
        raise SystemExit("RUNNER_TEMP is required; local /tmp is not an approved boundary")

    runner_temp = Path(runner_temp_value).resolve(strict=True)
    target = Path(sys.argv[1]).resolve()
    if target == runner_temp or runner_temp not in target.parents:
        raise SystemExit("target must be a child of RUNNER_TEMP")
    if target.exists():
        raise SystemExit("target already exists; refusing to overwrite")

    valid = {
        "schema_version": "1",
        "item_id": "sample-item-0001",
        "content_type": "image/jpeg",
        "byte_size": 2048,
        "state": "active",
    }
    missing_id = {key: value for key, value in valid.items() if key != "item_id"}
    invalid_size = {**valid, "byte_size": 0}
    invalid_major = {**valid, "schema_version": "2"}
    unknown_optional = {**valid, "future_label": "ignored-by-v1"}
    removed = {**valid, "state": "remove_requested"}

    files: dict[str, str] = {
        "fixtures/valid.json": json.dumps(valid, indent=2) + "\n",
        "fixtures/missing-id.json": json.dumps(missing_id, indent=2) + "\n",
        "fixtures/zero-size.json": json.dumps(invalid_size, indent=2) + "\n",
        "fixtures/unsupported-major.json": json.dumps(invalid_major, indent=2) + "\n",
        "fixtures/unknown-optional.json": json.dumps(unknown_optional, indent=2) + "\n",
        "fixtures/remove-requested.json": json.dumps(removed, indent=2) + "\n",
        "web/fixtures/valid.json": json.dumps(valid, indent=2) + "\n",
        "web/package.json": json.dumps(
            {
                "name": "fw013-next-profile-probe",
                "private": True,
                "scripts": {"build": "next build", "typecheck": "tsc --noEmit", "test": "vitest run"},
                "dependencies": {
                    "next": "15.5.27",
                    "react": "19.2.8",
                    "react-dom": "19.2.8",
                },
                "devDependencies": {
                    "@types/node": "22.18.0",
                    "@types/react": "19.2.0",
                    "@types/react-dom": "19.2.0",
                    "typescript": "5.9.3",
                    "vitest": "5.0.0",
                },
            },
            indent=2,
        )
        + "\n",
        "web/tsconfig.json": json.dumps(
            {
                "compilerOptions": {
                    "target": "ES2017",
                    "lib": ["dom", "dom.iterable", "esnext"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "strict": True,
                    "noEmit": True,
                    "esModuleInterop": True,
                    "module": "esnext",
                    "moduleResolution": "bundler",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "jsx": "preserve",
                    "incremental": True,
                    "plugins": [{"name": "next"}],
                },
                "include": ["next-env.d.ts", ".next/types/**/*.ts", "**/*.ts", "**/*.tsx"],
                "exclude": ["node_modules"],
            },
            indent=2,
        )
        + "\n",
        "web/app/layout.tsx": (
            "import type { ReactNode } from 'react';\n"
            "export default function RootLayout({ children }: { children: ReactNode }) {\n"
            "  return <html lang=\"en\"><body>{children}</body></html>;\n"
            "}\n"
        ),
        "web/app/page.tsx": (
            "import item from '../fixtures/valid.json';\n"
            "export default function Page() {\n"
            "  return <main><h1>Framework profile probe</h1><p>{item.item_id}</p></main>;\n"
            "}\n"
        ),
        "web/gallery-item.ts": (
            "export type GalleryItem = { schema_version: '1'; item_id: string; content_type: string; byte_size: number; state: 'active' | 'remove_requested' };\n"
            "export function isGalleryItem(value: unknown): value is GalleryItem {\n"
            "  if (!value || typeof value !== 'object') return false;\n"
            "  const item = value as Record<string, unknown>;\n"
            "  return item.schema_version === '1' && typeof item.item_id === 'string' && item.item_id.length > 0 && typeof item.content_type === 'string' && item.content_type.length > 0 && Number.isInteger(item.byte_size) && Number(item.byte_size) > 0 && (item.state === 'active' || item.state === 'remove_requested');\n"
            "}\n"
        ),
        "web/gallery-item.test.ts": (
            "import { readFileSync } from 'node:fs';\n"
            "import { resolve } from 'node:path';\n"
            "import { describe, expect, it } from 'vitest';\n"
            "import { isGalleryItem } from './gallery-item';\n"
            "const fixture = (name: string): unknown => JSON.parse(readFileSync(resolve('../fixtures', name), 'utf8'));\n"
            "describe('GalleryItemV1 fixture outcomes', () => {\n"
            "  it.each([['valid.json', true], ['remove-requested.json', true], ['unknown-optional.json', true], ['missing-id.json', false], ['zero-size.json', false], ['unsupported-major.json', false]])('%s => %s', (name, accepted) => {\n"
            "    expect(isGalleryItem(fixture(name as string))).toBe(accepted);\n"
            "  });\n"
            "});\n"
        ),
        "api/requirements.in": "fastapi==0.157.0\npytest==9.1.1\nhttpx==0.28.1\n",
        "api/main.py": (
            "from typing import Literal\n"
            "from fastapi import FastAPI\n"
            "from pydantic import BaseModel, ConfigDict, Field\n"
            "\n"
            "class GalleryItem(BaseModel):\n"
            "    model_config = ConfigDict(extra='ignore', strict=True)\n"
            "    schema_version: Literal['1']\n"
            "    item_id: str = Field(min_length=1)\n"
            "    content_type: str = Field(min_length=1)\n"
            "    byte_size: int = Field(gt=0)\n"
            "    state: Literal['active', 'remove_requested']\n"
            "\n"
            "app = FastAPI()\n"
            "@app.post('/items', response_model=GalleryItem)\n"
            "def register_item(item: GalleryItem) -> GalleryItem:\n"
            "    return item\n"
        ),
        "api/test_main.py": (
            "import json\n"
            "from pathlib import Path\n"
            "from fastapi.testclient import TestClient\n"
            "from main import app\n"
            "\n"
            "FIXTURES = Path(__file__).parents[1] / 'fixtures'\n"
            "client = TestClient(app)\n"
            "def payload(name):\n"
            "    return json.loads((FIXTURES / name).read_text())\n"
            "def test_valid_preserves_identity():\n"
            "    response = client.post('/items', json=payload('valid.json'))\n"
            "    assert response.status_code == 200\n"
            "    assert response.json()['item_id'] == 'sample-item-0001'\n"
            "import pytest\n"
            "@pytest.mark.parametrize(('name', 'status'), [('valid.json', 200), ('remove-requested.json', 200), ('unknown-optional.json', 200), ('missing-id.json', 422), ('zero-size.json', 422), ('unsupported-major.json', 422)], ids=['valid.json', 'remove-requested.json', 'unknown-optional.json', 'missing-id.json', 'zero-size.json', 'unsupported-major.json'])\n"
            "def test_named_fixture_outcome(name, status):\n"
            "    assert client.post('/items', json=payload(name)).status_code == status\n"
            "def test_unknown_optional_is_ignored():\n"
            "    response = client.post('/items', json=payload('unknown-optional.json'))\n"
            "    assert response.status_code == 200\n"
            "    assert 'future_label' not in response.json()\n"
            "def test_remove_request_is_acknowledged_as_terminal_state():\n"
            "    response = client.post('/items', json=payload('remove-requested.json'))\n"
            "    assert response.status_code == 200\n"
            "    assert response.json()['state'] == 'remove_requested'\n"
        ),
        "rust/rust-toolchain.toml": '[toolchain]\nchannel = "1.97.0"\nprofile = "minimal"\n',
        "rust/Cargo.toml": (
            "[package]\nname = \"fw013-axum-probe\"\nversion = \"0.1.0\"\nedition = \"2024\"\n\n"
            "[dependencies]\naxum = \"=0.8.9\"\nserde = { version = \"=1.0.228\", features = [\"derive\"] }\n"
            "serde_json = \"=1.0.145\"\n"
        ),
        "rust/src/main.rs": (
            "use axum::{routing::post, Json, Router};\n"
            "use serde::{Deserialize, Serialize};\n"
            "\n"
            "#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]\n"
            "struct GalleryItem {\n"
            "    schema_version: String, item_id: String, content_type: String,\n"
            "    byte_size: u64, state: String,\n"
            "}\n"
            "impl GalleryItem {\n"
            "    fn valid(&self) -> bool { self.schema_version == \"1\" && !self.item_id.is_empty() && !self.content_type.is_empty() && self.byte_size > 0 && matches!(self.state.as_str(), \"active\" | \"remove_requested\") }\n"
            "}\n"
            "async fn register(Json(item): Json<GalleryItem>) -> Json<GalleryItem> { Json(item) }\n"
            "fn app() -> Router { Router::new().route(\"/items\", post(register)) }\n"
            "fn main() { let _router = app(); }\n"
            "\n"
            "#[cfg(test)]\n"
            "mod tests {\n"
            "    use super::*;\n"
            "    const VALID: &str = include_str!(\"../../fixtures/valid.json\");\n"
            "    const MISSING: &str = include_str!(\"../../fixtures/missing-id.json\");\n"
            "    const ZERO: &str = include_str!(\"../../fixtures/zero-size.json\");\n"
            "    const MAJOR: &str = include_str!(\"../../fixtures/unsupported-major.json\");\n"
            "    const UNKNOWN: &str = include_str!(\"../../fixtures/unknown-optional.json\");\n"
            "    const REMOVED: &str = include_str!(\"../../fixtures/remove-requested.json\");\n"
            "    #[test] fn fixture_valid_json_accept() { let item: GalleryItem = serde_json::from_str(VALID).unwrap(); assert!(item.valid(), \"valid.json\"); assert_eq!(item.item_id, \"sample-item-0001\"); }\n"
            "    #[test] fn fixture_remove_requested_json_accept() { let item: GalleryItem = serde_json::from_str(REMOVED).unwrap(); assert!(item.valid(), \"remove-requested.json\"); assert_eq!(item.state, \"remove_requested\"); }\n"
            "    #[test] fn fixture_unknown_optional_json_accept() { let item: GalleryItem = serde_json::from_str(UNKNOWN).unwrap(); assert!(item.valid(), \"unknown-optional.json\"); }\n"
            "    #[test] fn fixture_missing_id_json_reject() { assert!(serde_json::from_str::<GalleryItem>(MISSING).is_err(), \"missing-id.json\"); }\n"
            "    #[test] fn fixture_zero_size_json_reject() { let item: GalleryItem = serde_json::from_str(ZERO).unwrap(); assert!(!item.valid(), \"zero-size.json\"); }\n"
            "    #[test] fn fixture_unsupported_major_json_reject() { let item: GalleryItem = serde_json::from_str(MAJOR).unwrap(); assert!(!item.valid(), \"unsupported-major.json\"); }\n"
            "}\n"
        ),
    }

    for relative, contents in files.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")

    print(f"Generated {len(files)} synthetic probe inputs under {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
