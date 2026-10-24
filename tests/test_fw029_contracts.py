from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path
from typing import Any

from scripts.fw029_contracts import (
    MAX_BYTES,
    canonical_json_bytes,
    validate_policy,
    validate_receipt,
    validate_receipt_policy,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "framework" / "schemas" / "fw029" / "fixtures"
RECEIPT_PATH = FIXTURES / "receipt.valid.synthetic.json"
POLICY_PATH = FIXTURES / "policy.valid.synthetic.json"
CASES_PATH = FIXTURES / "semantic-cases.json"
TRUST_ROOT = b"synthetic FW029 test trust root"


def encode(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Fw029ContractsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        self.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        self.policy["issuer"]["trust_root_sha256"] = sha256(TRUST_ROOT)
        self.cases = {
            item["id"]: item
            for item in json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]
        }

    def evaluate(
        self,
        *,
        receipt: dict[str, Any] | None = None,
        policy: dict[str, Any] | None = None,
        expected_policy_sha256: str | None = "auto",
        trust_root_bytes: bytes | None = TRUST_ROOT,
        evidence_bytes: dict[str, bytes] | None = None,
        provider_check_ids: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        receipt_value = copy.deepcopy(self.receipt if receipt is None else receipt)
        policy_value = copy.deepcopy(self.policy if policy is None else policy)
        receipt_raw = encode(receipt_value)
        policy_raw = encode(policy_value)
        expected = (
            sha256(policy_raw)
            if expected_policy_sha256 == "auto"
            else expected_policy_sha256
        )
        return validate_receipt_policy(
            receipt_raw,
            policy_raw,
            expected_policy_sha256=expected,
            trust_root_bytes=trust_root_bytes,
            evidence_bytes=evidence_bytes,
            provider_check_ids=provider_check_ids,
        )

    def codes(self, outcome: dict[str, Any]) -> set[str]:
        return {item["code"] for item in outcome["diagnostics"]}

    def assert_case(self, outcome: dict[str, Any], case_id: str) -> None:
        case = self.cases[case_id]
        self.assertEqual(outcome["state"], case["expected_status"], outcome["diagnostics"])
        self.assertIn(case["expected_diagnostic"], self.codes(outcome))

    def test_valid_synthetic_schema_fixtures_are_contract_valid(self) -> None:
        self.assertEqual(validate_receipt(RECEIPT_PATH.read_bytes())["state"], "contract_valid")
        self.assertEqual(validate_policy(POLICY_PATH.read_bytes())["state"], "contract_valid")

    def test_invalid_required_field_fixtures_are_rejected(self) -> None:
        receipt = validate_receipt((FIXTURES / "receipt.missing-source.invalid.json").read_bytes())
        policy = validate_policy((FIXTURES / "policy.missing-trust-root.invalid.json").read_bytes())
        self.assertIn("receipt.schema_invalid", self.codes(receipt))
        self.assertIn("policy.schema_invalid", self.codes(policy))

    def test_duplicate_keys_invalid_utf8_and_nonstandard_numbers_fail_closed(self) -> None:
        duplicate = validate_receipt(b'{"schema_version":"1.0","schema_version":"1.0"}')
        invalid_utf8 = validate_receipt(b"\xff")
        nonstandard_number = validate_policy(b'{"policy_version":NaN}')
        self.assertIn("receipt.json_invalid", self.codes(duplicate))
        self.assertIn("receipt.json_invalid", self.codes(invalid_utf8))
        self.assertIn("policy.json_invalid", self.codes(nonstandard_number))

    def test_unknown_fields_and_invalid_formats_are_rejected(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["unreviewed_claim"] = True
        self.assertIn("receipt.schema_invalid", self.codes(validate_receipt(encode(receipt))))
        for value in (
            "not-a-date",
            "2026-10-24 18:00:00Z",
            "2026-10-24t18:00:00Z",
            "2026-10-24T18:00Z",
            "2026-10-24T18:00:00+0000",
            "2026-02-30T18:00:00Z",
        ):
            with self.subTest(issued_at=value):
                receipt = copy.deepcopy(self.receipt)
                receipt["issued_at"] = value
                self.assertIn("receipt.schema_invalid", self.codes(validate_receipt(encode(receipt))))

    def test_canonical_serialization_is_sorted_compact_utf8(self) -> None:
        self.assertEqual(
            canonical_json_bytes({"z": "café", "a": 1}),
            b'{"a":1,"z":"caf\xc3\xa9"}',
        )
        self.assertEqual(
            canonical_json_bytes({"a": 1, "z": "café"}),
            canonical_json_bytes({"z": "café", "a": 1}),
        )
        with self.assertRaises(ValueError):
            canonical_json_bytes({"not_finite": float("nan")})

    def test_receipt_and_policy_byte_limits_are_checked_before_parsing(self) -> None:
        receipt_raw = RECEIPT_PATH.read_bytes()
        policy_raw = POLICY_PATH.read_bytes()
        receipt_at_limit = validate_receipt(
            receipt_raw + b" " * (MAX_BYTES["receipt"] - len(receipt_raw))
        )
        policy_at_limit = validate_policy(
            policy_raw + b" " * (MAX_BYTES["policy"] - len(policy_raw))
        )
        self.assertEqual(receipt_at_limit["state"], "contract_valid")
        self.assertEqual(policy_at_limit["state"], "contract_valid")

        receipt = validate_receipt(b" " * (MAX_BYTES["receipt"] + 1))
        policy = validate_policy(b" " * (MAX_BYTES["policy"] + 1))
        self.assertIn("receipt.size_limit_exceeded", self.codes(receipt))
        self.assertIn("policy.size_limit_exceeded", self.codes(policy))
        self.assert_case(receipt, "FW029-SEM-24")
        self.assert_case(policy, "FW029-SEM-25")

    def test_array_limits_are_checked_before_schema_validation(self) -> None:
        receipt_at_limit = copy.deepcopy(self.receipt)
        receipt_at_limit["checks"] = [copy.deepcopy(self.receipt["checks"][0]) for _ in range(100)]
        receipt_at_limit["evidence"] = [copy.deepcopy(self.receipt["evidence"][0]) for _ in range(100)]
        self.assertEqual(validate_receipt(encode(receipt_at_limit))["state"], "contract_valid")

        policy_at_limit = copy.deepcopy(self.policy)
        policy_at_limit["required_checks"] = [
            copy.deepcopy(self.policy["required_checks"][0]) for _ in range(100)
        ]
        self.assertEqual(validate_policy(encode(policy_at_limit))["state"], "contract_valid")

        receipt = copy.deepcopy(self.receipt)
        receipt["checks"] = receipt["checks"] * 101
        self.assert_case(self.evaluate(receipt=receipt), "FW029-SEM-26")

        policy = copy.deepcopy(self.policy)
        policy["required_checks"] = policy["required_checks"] * 101
        self.assert_case(self.evaluate(policy=policy), "FW029-SEM-26")

    def test_policy_digest_must_be_separately_supplied_and_match_exact_bytes(self) -> None:
        missing = self.evaluate(expected_policy_sha256=None)
        mismatch = self.evaluate(expected_policy_sha256="0" * 64)
        self.assert_case(missing, "FW029-SEM-05")
        self.assert_case(mismatch, "FW029-SEM-06")

        raw = encode(self.policy)
        changed_bytes = validate_receipt_policy(
            encode(self.receipt),
            raw + b"\n",
            expected_policy_sha256=sha256(raw),
            trust_root_bytes=TRUST_ROOT,
        )
        self.assert_case(changed_bytes, "FW029-SEM-06")

    def test_trust_root_is_required_and_digest_bound(self) -> None:
        self.assert_case(self.evaluate(trust_root_bytes=None), "FW029-SEM-07")
        self.assert_case(self.evaluate(trust_root_bytes=b"different root"), "FW029-SEM-08")

    def test_provider_and_issuer_claims_are_compared_to_pinned_policy(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy["issuer"]["identity"] += "/untrusted"
        self.assert_case(self.evaluate(policy=policy), "FW029-SEM-09")

        receipt = copy.deepcopy(self.receipt)
        receipt["provider_run"]["provider"] = "other-ci"
        self.assert_case(self.evaluate(receipt=receipt), "FW029-SEM-30")

        receipt = copy.deepcopy(self.receipt)
        receipt["provider_run"]["run_id"] = "987654321"
        self.assert_case(self.evaluate(receipt=receipt), "FW029-SEM-31")

    def test_repository_source_workflow_contract_run_and_manifest_bindings(self) -> None:
        mutations = [
            ("repository", lambda r, p: r["repository"].update(owner="other-owner"), "FW029-SEM-13"),
            ("workflow", lambda r, p: r["workflow"].update(path=".github/workflows/other.yml"), "FW029-SEM-14"),
            ("contract", lambda r, p: r["gate_contract"].update(version="9.0"), "FW029-SEM-15"),
            ("run-attempt", lambda r, p: r["provider_run"].update(attempt=2), "FW029-SEM-16"),
            ("manifest", lambda r, p: r.update(required_check_manifest_sha256="1" * 64), "FW029-SEM-17"),
            ("source-sha", lambda r, p: r["source"].update(sha="b" * 40), "FW029-SEM-01"),
            ("source-ref", lambda r, p: r["source"].update(ref="refs/heads/other"), "FW029-SEM-29"),
        ]
        for name, mutate, case_id in mutations:
            with self.subTest(name=name):
                receipt = copy.deepcopy(self.receipt)
                policy = copy.deepcopy(self.policy)
                mutate(receipt, policy)
                self.assert_case(self.evaluate(receipt=receipt, policy=policy), case_id)

    def test_check_set_conclusion_identity_and_source_are_exact(self) -> None:
        missing = copy.deepcopy(self.receipt)
        missing["checks"] = []
        self.assert_case(self.evaluate(receipt=missing), "FW029-SEM-04")

        extra = copy.deepcopy(self.receipt)
        extra["checks"].append({
            **extra["checks"][0],
            "logical_id": "extra-check",
            "provider_check_id": "check-1002",
            "name": "Extra Check",
        })
        self.assert_case(self.evaluate(receipt=extra), "FW029-SEM-28")

        duplicate = copy.deepcopy(self.receipt)
        duplicate["checks"].append(copy.deepcopy(duplicate["checks"][0]))
        self.assert_case(self.evaluate(receipt=duplicate), "FW029-SEM-04")

        failed = copy.deepcopy(self.receipt)
        failed["checks"][0]["conclusion"] = "failure"
        self.assert_case(self.evaluate(receipt=failed), "FW029-SEM-18")

        wrong_source = copy.deepcopy(self.receipt)
        wrong_source["checks"][0]["head_sha"] = "b" * 40
        self.assert_case(self.evaluate(receipt=wrong_source), "FW029-SEM-20")

        wrong_provider_id = self.evaluate(provider_check_ids={"metadata-audit": "check-9999"})
        self.assert_case(wrong_provider_id, "FW029-SEM-19")

    def test_evidence_digest_checks_exact_supplied_bytes(self) -> None:
        outcome = self.evaluate(evidence_bytes={"gate-record": b"mutated evidence"})
        self.assert_case(outcome, "FW029-SEM-21")

    def test_unsupported_replay_policy_fails_closed(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy["verification_mode"] = "one-use"
        self.assert_case(self.evaluate(policy=policy), "FW029-SEM-22")

    def test_repeatable_contract_check_is_deterministic_and_read_only(self) -> None:
        receipt_before = copy.deepcopy(self.receipt)
        first = self.evaluate()
        second = self.evaluate()
        self.assertEqual(first, second)
        self.assertEqual(self.receipt, receipt_before)
        self.assertEqual(first["state"], "contract_valid")
        self.assertEqual(first["signature_status"], "not-verified")
        self.assertEqual(first["provider_authentication"], "not-performed")

    def test_missing_inputs_and_invalid_observation_containers_are_blocked(self) -> None:
        missing = validate_receipt_policy(
            None, encode(self.policy),
            expected_policy_sha256=sha256(encode(self.policy)),
            trust_root_bytes=TRUST_ROOT,
        )
        self.assertEqual(missing["state"], "blocked")
        self.assertIn("receipt.input_missing", self.codes(missing))

        invalid_evidence = self.evaluate(evidence_bytes={"gate-record": "not bytes"})
        self.assertEqual(invalid_evidence["state"], "blocked")
        self.assertIn("evidence.input_invalid", self.codes(invalid_evidence))

    def test_case_fixture_ids_are_stable_and_all_supported_cases_have_expectations(self) -> None:
        supported = {
            "FW029-SEM-01", "FW029-SEM-04", "FW029-SEM-05", "FW029-SEM-06",
            "FW029-SEM-07", "FW029-SEM-08", "FW029-SEM-09", "FW029-SEM-13",
            "FW029-SEM-14", "FW029-SEM-15", "FW029-SEM-16", "FW029-SEM-17",
            "FW029-SEM-18", "FW029-SEM-19", "FW029-SEM-20", "FW029-SEM-21",
            "FW029-SEM-22", "FW029-SEM-24", "FW029-SEM-25", "FW029-SEM-26",
            "FW029-SEM-28", "FW029-SEM-29", "FW029-SEM-30", "FW029-SEM-31",
        }
        self.assertTrue(supported <= self.cases.keys())
        deferred = {
            "FW029-SEM-02", "FW029-SEM-03", "FW029-SEM-10",
            "FW029-SEM-11", "FW029-SEM-12", "FW029-SEM-27",
        }
        self.assertTrue(deferred <= self.cases.keys())
        self.assertEqual(supported & deferred, set())


if __name__ == "__main__":
    unittest.main()
