from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs/framework/examples/gate-contract-v1"
SCHEMA_PATH = ROOT / "docs/framework/schemas/gate-run-v1.schema.json"
PROFILE_BY_GATE = {
    "G-INTENT": "g_intent",
    "G-SETUP": "g_setup",
    "G-REQ": "g_req",
    "G-FEAS": "g_feas",
    "G-COVERAGE": "g_coverage",
    "G-CX": "g_cx",
    "G-ARCH": "g_arch",
    "G-IMPL": "g_impl",
    "G-RELEASE": "g_release",
    "G-OPERATE": "g_operate",
}
PREFIX_BY_GATE = {
    "G-INTENT": "GINT", "G-SETUP": "GSET", "G-REQ": "GREQ",
    "G-FEAS": "GFEAS", "G-COVERAGE": "GCOV", "G-CX": "GCX",
    "G-ARCH": "GARCH", "G-IMPL": "GIMPL", "G-RELEASE": "GREL",
    "G-OPERATE": "GOP",
}


class GateContractFixtureTests(unittest.TestCase):
    def test_schema_and_ten_gate_fixtures_are_parseable_and_aligned(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["$defs"]["g_intent"]["type"], "object")
        self.assertEqual(len(PROFILE_BY_GATE), 10)
        traceability = (ROOT / "docs/framework/FRAMEWORK-GATE-TRACEABILITY-001.md").read_text(encoding="utf-8")

        for gate_id, profile_name in PROFILE_BY_GATE.items():
            valid = json.loads((FIXTURES / "valid" / f"{gate_id}.json").read_text(encoding="utf-8"))
            invalid = json.loads((FIXTURES / "invalid" / f"{gate_id}.json").read_text(encoding="utf-8"))
            self.assertEqual(valid["gate_id"], gate_id)
            self.assertEqual(valid["contract_version"], "1.0")
            self.assertEqual(valid["gate_result"], "in-progress")
            self.assertTrue(set(schema["required"]).issubset(valid))
            self.assertTrue(set(schema["$defs"][profile_name]["required"]).issubset(valid["gate_data"]))
            actual_criteria = {row["criterion_id"] for row in valid["criteria_results"]}
            matrix_criteria = set(re.findall(rf"\|\s*({PREFIX_BY_GATE[gate_id]}-[0-9]{{2}})\s*\|", traceability))
            self.assertEqual(actual_criteria, matrix_criteria)
            self.assertNotIn("gate_result", invalid)
            self.assertEqual(invalid["gate_id"], gate_id)

    def test_hash_drift_and_stale_revision_cases_are_real_fixture_mismatches(self) -> None:
        changed = json.loads((FIXTURES / "invalid/changed-file-hash.json").read_text(encoding="utf-8"))
        artifact = changed["scope"]["artifact_refs"][0]
        material = (ROOT / artifact["path"]).read_bytes()
        actual = "sha256:" + hashlib.sha256(material).hexdigest()
        self.assertNotEqual(artifact["sha256"], actual)

        stale = json.loads((FIXTURES / "invalid/stale-source-revision.json").read_text(encoding="utf-8"))
        stale_evidence = next(item for item in stale["evidence"] if item["evidence_id"] == "E-STALE")
        self.assertNotEqual(stale_evidence["source_revision"], stale["source_snapshot"]["commit_sha"])
        self.assertEqual(stale["gate_result"], "in-progress")


if __name__ == "__main__":
    unittest.main()
