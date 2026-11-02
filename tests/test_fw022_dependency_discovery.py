from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / "workflows/product-discovery.md").read_text(encoding="utf-8")
FEASIBILITY = (ROOT / "workflows/feasibility-architecture.md").read_text(encoding="utf-8")
EXERCISE = (ROOT / "docs/framework/FRAMEWORK-EXERCISE-004-pre-spec-dependency-discovery.md").read_text(encoding="utf-8")
FIXTURE = json.loads((ROOT / "tests/fixtures/fw022_dependency_scenarios.json").read_text(encoding="utf-8"))
ALLOWED_CLASSIFICATIONS = {"supported", "unsupported", "unknown", "constrained", "not-applicable"}
ALLOWED_TASK_STATES = {"blocked", "unblocked", "conditional"}


class DependencyDiscoveryContractTests(unittest.TestCase):
    """Exercise routing examples without network or credentials."""

    def test_pre_spec_workflow_defines_narrow_evidence_and_no_early_gate_pass(self) -> None:
        self.assertIn("## Early dependency screen — before specification lock", WORKFLOW)
        self.assertIn("The pre-spec screen alone can never satisfy G-FEAS", FEASIBILITY)
        self.assertIn("not a formal feasibility assessment", WORKFLOW)
        self.assertEqual(FIXTURE["scope"], "pre-specification dependency screening only")
        self.assertEqual(FIXTURE["formal_g_feas_result"], "not-run")
        self.assertIn("This is a process example, not a formal G-FEAS run", EXERCISE)

    def test_documented_capability_is_supported_without_claiming_project_access(self) -> None:
        probes = self.scenario("documented-capability-with-access-open")["probes"]
        capability = self.probe(probes, "DEP-PLACE-CAPABILITY")
        access = self.probe(probes, "DEP-PLACE-ACCESS")
        self.assertEqual(capability["classification"], "supported")
        self.assertTrue(any(item["kind"] == "primary-provider-documentation" and item["url"].startswith("https://") for item in capability["evidence"]))
        self.assertIn("does not prove", capability["evidence"][0]["limits"].lower())
        self.assertEqual(capability["downstream_tasks"][0]["state"], "unblocked")
        self.assertEqual(access["classification"], "unknown")
        self.assertEqual(access["downstream_tasks"][0]["state"], "blocked")
        self.assertIn("not assessed", access["confidence"])
        self.assertEqual(access["observation"]["status"], "not checked")
        self.assertEqual(access["observation"]["date"], "2026-10-21")
        self.assertFalse(access["credential_value_read"])

    def test_unavailable_endpoint_blocks_only_its_dependent_task(self) -> None:
        probe = self.scenario("provider-endpoint-unavailable")["probes"][0]
        self.assertEqual(probe["classification"], "unsupported")
        self.assertEqual(probe["evidence"][0]["kind"], "synthetic-provider-probe-fixture")
        self.assertEqual(probe["downstream_tasks"][0]["state"], "blocked")
        self.assertIn("manual inventory work can continue", probe["downstream_effect"])
        self.assertIn("Synthetic response only", probe["evidence"][0]["limits"])

    def test_missing_credentials_remain_unknown_and_preserve_independent_work(self) -> None:
        probe = self.scenario("missing-credentials-or-permission")["probes"][0]
        self.assertEqual(probe["classification"], "unknown")
        self.assertFalse(probe["credential_value_read"])
        states = {task["task_id"]: task["state"] for task in probe["downstream_tasks"]}
        self.assertEqual(states["APP-TASK-INVENTORY-INTEGRATION"], "blocked")
        unaffected = {task["task_id"]: task["state"] for task in probe["unaffected_tasks"]}
        self.assertEqual(unaffected["APP-TASK-INVENTORY-MOCK-UX"], "unblocked")
        self.assertIn("not establish that the provider or API is unavailable", probe["evidence"][0]["limits"])

    def test_cost_constraint_requires_condition_boundary_and_owner_trigger(self) -> None:
        probe = self.scenario("cost-constrained-provider")["probes"][0]
        self.assertEqual(probe["classification"], "constrained")
        self.assertTrue(probe["evidence"][0]["url"].startswith("https://"))
        task = probe["downstream_tasks"][0]
        self.assertEqual(task["state"], "conditional")
        self.assertTrue(task["condition"] and task["safe_work_boundary"] and task["state_change_trigger"])
        self.assertIn("Mock-only design remains allowed", probe["downstream_effect"])

    def test_not_applicable_requires_owner_scope_evidence_and_states_its_effect(self) -> None:
        probe = self.scenario("explicitly-not-applicable-dependency")["probes"][0]
        self.assertEqual(probe["classification"], "not-applicable")
        self.assertEqual(probe["evidence"][0]["kind"], "synthetic-owner-decision")
        self.assertEqual(probe["evidence"][0]["decision_id"], "DECISION-SYNTH-WEB-ONLY")
        self.assertEqual(probe["downstream_tasks"], [])
        self.assertEqual(probe["unaffected_tasks"][0]["state"], "unblocked")
        self.assertIn("reopen if native ios enters scope", probe["downstream_effect"].lower())

    def test_all_probes_have_classification_links_owner_and_next_action(self) -> None:
        seen = set()
        for scenario in FIXTURE["scenarios"]:
            for probe in scenario["probes"]:
                self.assertNotIn(probe["probe_id"], seen)
                seen.add(probe["probe_id"])
                self.assertIn(probe["classification"], ALLOWED_CLASSIFICATIONS)
                self.assertTrue(probe["confidence"])
                self.assertTrue(probe["claim"] and probe["requirement_anchors"] and probe["owner"] and probe["next_action"] and probe["downstream_effect"])
                self.assertIsInstance(probe["requirement_ids"], list)
                for task in probe.get("downstream_tasks", []) + probe.get("unaffected_tasks", []):
                    self.assertIn(task["state"], ALLOWED_TASK_STATES)
                    self.assertTrue(task["task_id"] and task.get("reason", task.get("condition")))
                    if task["state"] == "conditional":
                        self.assertTrue(task["condition"] and task["safe_work_boundary"] and task["state_change_trigger"])
                if probe["classification"] in {"unsupported", "unknown", "constrained"}:
                    self.assertFalse(any(task["state"] == "unblocked" for task in probe.get("downstream_tasks", [])))

    def scenario(self, scenario_id: str) -> dict:
        matches = [item for item in FIXTURE["scenarios"] if item["id"] == scenario_id]
        self.assertEqual(len(matches), 1, f"expected one scenario {scenario_id}")
        return matches[0]

    def probe(self, probes: list[dict], probe_id: str) -> dict:
        matches = [item for item in probes if item["probe_id"] == probe_id]
        self.assertEqual(len(matches), 1, f"expected one probe {probe_id}")
        return matches[0]


if __name__ == "__main__":
    unittest.main()
