from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXERCISE = (ROOT / "docs/framework/FRAMEWORK-EXERCISE-003-app-onboarding.md").read_text(encoding="utf-8")
WORKFLOW = (ROOT / "workflows/product-discovery.md").read_text(encoding="utf-8")
FIXTURE = json.loads((ROOT / "tests/fixtures/fw021_discovery_scenarios.json").read_text(encoding="utf-8"))


class DiscoveryExerciseContractTests(unittest.TestCase):
    """Keep the synthetic onboarding examples aligned with the written policy."""

    def test_minimal_intake_preserves_unknowns_without_premature_stack_questions(self) -> None:
        scenario = self.scenario("minimal-intake")
        self.assertEqual(scenario["setup_questions"], ["project_name", "artifact_prefix", "empty_target"])
        self.assertEqual(
            set(scenario["questions_not_needed_for_bootstrap"]),
            {"platform", "provider", "region", "budget", "license", "database"},
        )
        self.assertFalse(scenario["bootstrap_creates_remote_or_gate_pass"])
        self.assertTrue(all(item["blocks"] and item["resolver"] and item["next_action"] for item in scenario["unknowns"]))
        self.assertIn("Do not make the owner fill a fixed questionnaire", WORKFLOW)
        self.assertIn("### Empty target with minimal intent and unknown answers", EXERCISE)

    def test_existing_repository_trace_separates_observations_inferences_and_unknowns(self) -> None:
        scenario = self.scenario("existing-repository")
        self.assertIn("pyproject.toml", scenario["observed_facts"])
        self.assertEqual(scenario["owner_statements"], [])
        self.assertEqual(scenario["researched_claims"], [])
        self.assertEqual(scenario["inferences"], ["Python project based on pyproject.toml"])
        self.assertFalse(scenario["credentials_read"])
        self.assertFalse(scenario["initializer_allowed"])
        self.assertIn("### Existing application repository with inaccessible owner/product evidence", EXERCISE)

    def test_repeat_setup_only_reopens_questions_affected_by_the_change(self) -> None:
        scenario = self.scenario("repeat-changed-constraint")
        self.assertIn("audience", " ".join(scenario["preserve"]))
        self.assertIn("problem", " ".join(scenario["preserve"]))
        self.assertIn("unknown provider", scenario["preserve"])
        self.assertIn("camera permission", scenario["reopen"])
        self.assertTrue(scenario["do_not_silently_approve_requirement"])
        self.assertTrue(scenario["block_only_dependent_promises"])
        self.assertIn("### Repeat setup after one changed constraint", EXERCISE)

    def test_owner_handoff_lists_review_fields_and_disclaims_technical_enforcement(self) -> None:
        scenario = self.scenario("owner-review-boundary")
        self.assertEqual(scenario["outward_actions_before_owner_review"], [])
        self.assertEqual(
            set(scenario["requires_owner_review_before"]),
            {"git init", "remote creation", "commit", "push", "publication"},
        )
        self.assertFalse(scenario["technical_sandbox_claim"])
        self.assertFalse(scenario["gate_pass_claim"])
        self.assertTrue({"owner statements", "observed files", "unknowns and impacts"}.issubset(scenario["handoff_fields"]))
        self.assertIn("### Owner review and outward-action boundary", EXERCISE)

    def test_examples_remain_synthetic_process_evidence(self) -> None:
        self.assertIn("not observed conversations", EXERCISE)
        self.assertIn("No real owner interview", EXERCISE)
        self.assertIn("No real owner interview or product G-INTENT/G-SETUP approval occurred", EXERCISE)

    def scenario(self, scenario_id: str) -> dict:
        matching = [item for item in FIXTURE["scenarios"] if item["id"] == scenario_id]
        self.assertEqual(len(matching), 1, f"expected one fixture for {scenario_id}")
        self.assertIn("synthetic", FIXTURE["evidence_boundary"])
        return matching[0]


if __name__ == "__main__":
    unittest.main()
