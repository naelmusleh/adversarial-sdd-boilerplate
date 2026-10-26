from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.fw030_contract import preflight_request, validate_request, validate_result


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs/framework/schemas/fw030/fixtures"


class Fw030ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = json.loads((FIXTURES / "request.valid.synthetic.json").read_text(encoding="utf-8"))
        self.cases = json.loads((FIXTURES / "preflight-cases.json").read_text(encoding="utf-8"))

    def test_valid_synthetic_request_and_result_contract(self) -> None:
        request_raw = json.dumps(self.request, separators=(",", ":"))
        self.assertTrue(validate_request(request_raw)["valid"])
        result_fixture = (FIXTURES / "result.valid.synthetic.json").read_bytes()
        self.assertTrue(validate_result(result_fixture)["valid"])
        result = preflight_request(request_raw, self.cases["profile_observation"])
        self.assertEqual(result["readiness_status"], "prerequisites_valid")
        self.assertTrue(validate_result(json.dumps(result))["valid"])
        self.assertEqual(result["states"], {
            "request_readiness": "prerequisites_valid",
            "authorization": "not_requested",
            "execution": "not_started",
            "cleanup": "not_applicable",
            "evidence": "not_collected",
            "review": "not_performed",
        })

    def test_synthetic_preflight_cases_are_fail_closed(self) -> None:
        base = self.cases["profile_observation"]
        for case in self.cases["cases"]:
            with self.subTest(case=case["id"]):
                observation = {**base, **case["observation_changes"]}
                result = preflight_request(self.request_json(), observation)
                self.assertEqual(result["readiness_status"], case["expected_status"])
                self.assertEqual(result["states"]["execution"], "not_started")
                self.assertEqual(result["states"]["authorization"], "not_requested")
                codes = {diagnostic["code"] for diagnostic in result["diagnostics"]}
                if case["expected_diagnostic"] is None:
                    self.assertEqual(codes, set())
                else:
                    self.assertIn(case["expected_diagnostic"], codes)
                self.assertTrue(validate_result(json.dumps(result))["valid"])

    def test_unadopted_or_mismatched_profile_is_not_treated_as_supported(self) -> None:
        no_observation = preflight_request(self.request_json())
        mismatched = copy.deepcopy(self.cases["profile_observation"])
        mismatched["profile_revision"] = "other-revision"
        mismatch_result = preflight_request(self.request_json(), mismatched)
        self.assertEqual(no_observation["readiness_status"], "unsupported")
        self.assertEqual(mismatch_result["readiness_status"], "unsupported")
        self.assertEqual(mismatch_result["diagnostics"][0]["code"], "fw030.profile.identity_mismatch")

    def test_malformed_synthetic_observation_fails_closed(self) -> None:
        for mutation in (
            lambda value: value.update(available_capabilities="runtime.rootless"),
            lambda value: value.update(unreviewed_claim=True),
        ):
            malformed = copy.deepcopy(self.cases["profile_observation"])
            mutation(malformed)
            result = preflight_request(self.request_json(), malformed)
            self.assertEqual(result["readiness_status"], "unsupported")
            self.assertEqual(result["diagnostics"][0]["code"], "fw030.profile.observation_invalid")
            self.assertEqual(result["states"]["execution"], "not_started")

    def test_invalid_versions_extra_fields_and_semantic_inconsistencies_reject(self) -> None:
        for mutate in (
            lambda value: value.update(schema_version="2.0"),
            lambda value: value.update(unreviewed_claim=True),
            lambda value: value["execution_context"].update(provider_context={}),
            lambda value: value["workload"].update(argv=["/bin/other"]),
            lambda value: value["policy"].update(secrets="enabled"),
        ):
            request = copy.deepcopy(self.request)
            mutate(request)
            self.assertFalse(validate_request(json.dumps(request))["valid"])

        stale_digest = copy.deepcopy(self.request)
        stale_digest["policy"]["limits"]["memory_mb"] += 1
        outcome = validate_request(json.dumps(stale_digest))
        self.assertIn("fw030.request.policy_digest_mismatch", {item["code"] for item in outcome["diagnostics"]})

        invalid_id = copy.deepcopy(self.request)
        invalid_id["invocation_id"] = "not-a-uuid"
        result = preflight_request(json.dumps(invalid_id), self.cases["profile_observation"])
        self.assertEqual(result["readiness_status"], "invalid")
        self.assertTrue(validate_result(json.dumps(result))["valid"])

    def test_malformed_json_duplicate_keys_and_parser_errors_do_not_echo_input(self) -> None:
        duplicate = validate_request('{"token-secret-value":"private","token-secret-value":"private"}')
        malformed = validate_request('{"token-secret-value":"private",}')
        self.assertFalse(duplicate["valid"])
        self.assertFalse(malformed["valid"])
        for result in (duplicate, malformed):
            rendered = json.dumps(result)
            self.assertNotIn("private", rendered)
            self.assertNotIn("token-secret-value", rendered)

    def test_invalid_result_state_relationships_reject(self) -> None:
        result = preflight_request(self.request_json(), self.cases["profile_observation"])
        result["readiness_status"] = "blocked"
        self.assertFalse(validate_result(json.dumps(result))["valid"])

    def test_validator_does_not_start_a_process(self) -> None:
        with patch.object(subprocess, "Popen", side_effect=AssertionError("process launch attempted")) as popen:
            with patch.object(subprocess, "run", side_effect=AssertionError("process launch attempted")) as run:
                result = preflight_request(self.request_json(), self.cases["profile_observation"])
        self.assertEqual(result["states"]["execution"], "not_started")
        popen.assert_not_called()
        run.assert_not_called()

    def request_json(self) -> str:
        return json.dumps(self.request, separators=(",", ":"))


if __name__ == "__main__":
    unittest.main()
