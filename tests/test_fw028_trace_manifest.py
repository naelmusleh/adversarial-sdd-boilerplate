from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.trace_manifest import validate_trace_manifest


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "framework" / "schemas" / "fw028" / "fixtures"
PROFILE_PATH = FIXTURES / "quality-profile.valid.json"
MANIFEST_PATH = FIXTURES / "trace-manifest.valid.json"
RESULT_PATH = FIXTURES / "measurement-result.valid.json"
SHA = "a" * 40
REPOSITORY = "https://github.com/example/sample"
CHECK_ID = "CI-UNIT"


class TraceManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile_raw = PROFILE_PATH.read_bytes()
        self.profile = json.loads(self.profile_raw)
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.manifest["declared_risk_tier"] = "low"
        self.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.manifest_raw = json.dumps(self.manifest, sort_keys=True, separators=(",", ":")).encode()
        self.manifest["profile"]["sha256"] = hashlib.sha256(self.profile_raw).hexdigest()
        self.manifest_raw = json.dumps(self.manifest, sort_keys=True, separators=(",", ":")).encode()
        self.result.update({
            "repository": REPOSITORY,
            "source_sha": SHA,
            "profile_sha256": hashlib.sha256(self.profile_raw).hexdigest(),
            "manifest_sha256": hashlib.sha256(self.manifest_raw).hexdigest(),
        })
        self.result["provider_checks"][0].update({
            "repository": REPOSITORY,
            "head_sha": SHA,
            "required_check_id": CHECK_ID,
            "provider": "github-actions",
            "check_name": "Unit Tests",
        })
        self.policy = [{
            "check_id": CHECK_ID,
            "execution": "ci",
            "required": True,
            "task_ids": ["APP-TASK-001"],
            "acceptance_criteria": ["AC-1"],
            "provider": "github-actions",
            "name": "Unit Tests",
        }]

    def evaluate(self, *, manifest: dict | None = None, result: dict | None = None,
                 paths: list[str] | None = None, profile_raw: bytes | None = None) -> dict:
        manifest_value = self.manifest if manifest is None else manifest
        raw = json.dumps(manifest_value, sort_keys=True, separators=(",", ":")).encode()
        value_result = copy.deepcopy(self.result if result is None else result)
        value_result["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            changed = paths if paths is not None else ["src/domain/rule.py"]
            return validate_trace_manifest(
                raw,
                expected_repository=REPOSITORY,
                expected_source_sha=SHA,
                expected_task_id="APP-TASK-001",
                expected_criterion_ids=["AC-1"],
                observed_changed_paths=changed,
                profile_raw=self.profile_raw if profile_raw is None else profile_raw,
                required_check_policy=self.policy,
                measurement_result=value_result,
                checkout_root=directory,
            )

    def codes(self, outcome: dict) -> set[str]:
        return {item["code"] for item in outcome["diagnostics"]}

    def test_valid_exact_revision_trace_passes(self) -> None:
        result = self.evaluate()
        self.assertEqual(result["state"], "pass", result["diagnostics"])

    def test_missing_changed_path_mapping_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["path_criteria"] = []
        self.assertIn("TRACE-PATH-CRITERIA-INVALID", self.codes(self.evaluate(manifest=manifest)))

    def test_unknown_criterion_and_unmapped_path_fail(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["criterion_ids"] = ["AC-UNKNOWN"]
        manifest["path_criteria"] = [{"path": "src/domain/rule.py", "criterion_ids": ["AC-UNKNOWN"]}]
        codes = self.codes(self.evaluate(manifest=manifest))
        self.assertIn("TRACE-CRITERIA-MISMATCH", codes)

    def test_path_inventory_mismatch_fails(self) -> None:
        self.assertIn("TRACE-PATH-INVENTORY-MISMATCH", self.codes(self.evaluate(paths=["src/other.py"])))

    def test_noncanonical_and_root_paths_fail(self) -> None:
        for path in ("../outside.py", ".", "src//x.py", "C:/x.py", "src\\x.py"):
            with self.subTest(path=path):
                manifest = copy.deepcopy(self.manifest)
                manifest["changed_paths"] = [path]
                manifest["path_criteria"] = [{"path": path, "criterion_ids": ["AC-1"]}]
                self.assertIn("TRACE-PATH-NONCANONICAL", self.codes(self.evaluate(manifest=manifest, paths=[path])))

    def test_symlink_component_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root.parent / (root.name + "-outside")
            outside.mkdir()
            try:
                (root / "link").symlink_to(outside, target_is_directory=True)
                manifest = copy.deepcopy(self.manifest)
                manifest["changed_paths"] = ["link/secret.py"]
                manifest["path_criteria"] = [{"path": "link/secret.py", "criterion_ids": ["AC-1"]}]
                raw = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
                result = copy.deepcopy(self.result)
                result["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
                outcome = validate_trace_manifest(
                    raw, expected_repository=REPOSITORY, expected_source_sha=SHA,
                    expected_task_id="APP-TASK-001", expected_criterion_ids=["AC-1"],
                    observed_changed_paths=["link/secret.py"], profile_raw=self.profile_raw,
                    required_check_policy=self.policy, measurement_result=result, checkout_root=root,
                )
                self.assertIn("PATH-SYMLINK-ESCAPE", self.codes(outcome))
            finally:
                outside.rmdir()

    def test_profile_exact_bytes_are_digest_bound(self) -> None:
        changed_profile = self.profile_raw + b" "
        self.assertIn("TRACE-PROFILE-DIGEST-MISMATCH", self.codes(self.evaluate(profile_raw=changed_profile)))

    def test_wrong_repository_and_source_revision_fail(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["source_sha"] = "b" * 40
        manifest["repository"] = "https://github.com/other/repo"
        codes = self.codes(self.evaluate(manifest=manifest))
        self.assertIn("TRACE-SOURCE-SHA-MISMATCH", codes)
        self.assertIn("TRACE-REPOSITORY-MISMATCH", codes)

    def test_positive_exception_is_rejected_even_with_textual_authority(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["exceptions"] = [{
            "path": "src/domain/rule.py", "criterion_id": "AC-1",
            "reason": "approved", "authority_ref": "owner-approved",
        }]
        self.assertIn("TRACE-EXCEPTION-AUTHORITY-UNSUPPORTED", self.codes(self.evaluate(manifest=manifest)))

    def test_missing_failed_pending_or_wrong_name_provider_check_fails_closed(self) -> None:
        for mode in ("missing", "failed", "pending", "wrong-name", "wrong-sha"):
            with self.subTest(mode=mode):
                result = copy.deepcopy(self.result)
                if mode == "missing":
                    result["provider_checks"] = []
                elif mode == "failed":
                    result["provider_checks"][0]["conclusion"] = "failure"
                elif mode == "pending":
                    result["provider_checks"][0]["conclusion"] = "in_progress"
                elif mode == "wrong-name":
                    result["provider_checks"][0]["check_name"] = "Different Check"
                else:
                    result["provider_checks"][0]["head_sha"] = "b" * 40
                self.assertNotEqual(self.evaluate(result=result)["state"], "pass")

    def test_malformed_inputs_fail_without_crashing(self) -> None:
        for manifest_raw in (b"[]", b"{"):
            with self.subTest(manifest=manifest_raw):
                outcome = validate_trace_manifest(
                    manifest_raw, expected_repository=REPOSITORY, expected_source_sha=SHA,
                    expected_task_id="APP-TASK-001", expected_criterion_ids=["AC-1"],
                    observed_changed_paths=["src/domain/rule.py"], profile_raw=self.profile_raw,
                    required_check_policy=self.policy, measurement_result=self.result,
                    checkout_root=tempfile.gettempdir(),
                )
                self.assertEqual(outcome["state"], "blocked")
        result = copy.deepcopy(self.result)
        result["provider_checks"] = [{"required_check_id": []}]
        self.assertIn("TRACE-PROVIDER-CHECK-UNKNOWN", self.codes(self.evaluate(result=result)))

    def test_unhashable_path_values_fail_without_crashing(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["changed_paths"] = [["nested", "value"]]
        manifest["path_criteria"] = [{"path": ["nested"], "criterion_ids": ["AC-1"]}]
        outcome = self.evaluate(manifest=manifest, paths=[["nested", "value"]])
        self.assertEqual(outcome["state"], "blocked")
        self.assertIn("TRACE-PATH-NONCANONICAL", self.codes(outcome))

    def test_malformed_required_policy_scope_cannot_be_omitted_from_trace(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy[0]["task_ids"] = "APP-TASK-001"
        manifest = copy.deepcopy(self.manifest)
        manifest["required_checks"] = []
        result = copy.deepcopy(self.result)
        result["provider_checks"] = []
        raw = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        result["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            outcome = validate_trace_manifest(
                raw, expected_repository=REPOSITORY, expected_source_sha=SHA,
                expected_task_id="APP-TASK-001", expected_criterion_ids=["AC-1"],
                observed_changed_paths=["src/domain/rule.py"], profile_raw=self.profile_raw,
                required_check_policy=policy, measurement_result=result, checkout_root=directory,
            )
        self.assertEqual(outcome["state"], "blocked")
        self.assertIn("TRACE-CHECK-POLICY-INVALID", self.codes(outcome))

    def test_manifest_required_check_set_must_match_policy(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["required_checks"] = []
        self.assertIn("TRACE-CHECK-POLICY-MISMATCH", self.codes(self.evaluate(manifest=manifest)))

    def test_duplicate_and_unknown_provider_checks_fail(self) -> None:
        duplicate = copy.deepcopy(self.result)
        duplicate["provider_checks"].append(copy.deepcopy(duplicate["provider_checks"][0]))
        self.assertIn("TRACE-CHECK-RESULT-CARDINALITY", self.codes(self.evaluate(result=duplicate)))

        unknown = copy.deepcopy(self.result)
        unknown["provider_checks"][0]["required_check_id"] = "CI-UNKNOWN"
        self.assertIn("TRACE-PROVIDER-CHECK-UNKNOWN", self.codes(self.evaluate(result=unknown)))


if __name__ == "__main__":
    unittest.main()
