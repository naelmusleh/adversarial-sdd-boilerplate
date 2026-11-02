from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from scripts.quality_profiles import (
    diagnose_change_scope,
    evaluate_profile,
    parse_json,
    validate_profile,
    validate_profile_revision,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "framework" / "schemas" / "fw028" / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class FrameworkQualityProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = load_fixture("quality-profile.valid.json")

    def test_valid_profile_fixture_passes_structural_and_cross_field_validation(self) -> None:
        self.assertEqual(validate_profile(self.profile), [])

    def test_missing_rationale_fixture_reports_its_exact_rule_and_path(self) -> None:
        diagnostics = validate_profile(load_fixture("quality-profile.missing-rationale.invalid.json"))
        match = [item for item in diagnostics if item["code"] == "PROFILE-FIELD-MISSING"]
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0]["rule_id"], "QUAL-COVERAGE")
        self.assertEqual(match[0]["path"], "$.metric_rules[0].rationale")

    def test_root_path_is_rejected_as_changed_path(self) -> None:
        result = evaluate_profile(
            self.profile,
            changed_paths=["."],
            declared_task_risk_tier="low",
            measurements={"line-coverage": 90},
        )
        self.assertEqual(result["state"], "blocked")
        self.assertIn("TASK-PATH-INVALID", [item["code"] for item in result["diagnostics"]])

    def test_sensitive_path_risk_floor_cannot_be_lowered_by_task_label(self) -> None:
        result = evaluate_profile(
            self.profile,
            changed_paths=["src/auth/guard.py"],
            declared_task_risk_tier="low",
            measurements={"line-coverage": 90},
        )
        self.assertEqual(result["effective_risk_tier"], "critical")
        self.assertEqual(result["state"], "blocked")
        self.assertIn("RISK-FLOOR-DOWNGRADE", [item["code"] for item in result["diagnostics"]])
        self.assertEqual(result["metrics"][0]["state"], "pass")

    def test_mixed_scope_uses_strictest_matching_floor(self) -> None:
        result = evaluate_profile(
            self.profile,
            changed_paths=["src/ui/card.py", "src/auth/guard.py"],
            declared_task_risk_tier="critical",
            measurements={"line-coverage": 90},
        )
        self.assertEqual(result["effective_risk_tier"], "critical")
        self.assertEqual(result["state"], "pass")

    def test_criterion_tag_floor_escalates_risk_and_rejects_lower_task_label(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["escalation_floors"].append(
            {"match_kind": "criterion-tag", "match": "security-boundary", "minimum_tier": "high"}
        )
        result = evaluate_profile(
            profile,
            changed_paths=["src/domain/rule.py"],
            criterion_tags=["security-boundary"],
            declared_task_risk_tier="low",
            measurements={"line-coverage": 90},
        )
        self.assertEqual(result["effective_risk_tier"], "high")
        self.assertIn("RISK-FLOOR-DOWNGRADE", [item["code"] for item in result["diagnostics"]])

    def test_required_unsupported_metric_is_nonpassing_even_with_a_value(self) -> None:
        profile = copy.deepcopy(self.profile)
        rule = profile["metric_rules"][0]
        rule["availability"] = "unavailable"
        rule.pop("threshold")
        rule["unavailable_reason"] = "This adapter does not measure this metric."
        result = evaluate_profile(
            profile,
            changed_paths=["src/domain/rule.py"],
            declared_task_risk_tier="high",
            measurements={"line-coverage": 100},
        )
        self.assertEqual(result["state"], "blocked")
        self.assertEqual(result["metrics"][0]["state"], "unavailable")
        self.assertIn("REQUIRED-METRIC-UNAVAILABLE", [item["code"] for item in result["diagnostics"]])

    def test_task_level_threshold_override_is_rejected(self) -> None:
        result = evaluate_profile(
            self.profile,
            changed_paths=["src/domain/rule.py"],
            declared_task_risk_tier="high",
            measurements={"line-coverage": 100},
            task_overrides={"thresholds": {"line-coverage": 10}},
        )
        self.assertEqual(result["state"], "blocked")
        self.assertIn("TASK-OVERRIDE-UNSUPPORTED", [item["code"] for item in result["diagnostics"]])

    def test_failed_metric_threshold_returns_failure_with_rule_path(self) -> None:
        result = evaluate_profile(
            self.profile,
            changed_paths=["src/domain/rule.py"],
            declared_task_risk_tier="high",
            measurements={"line-coverage": 50},
        )
        self.assertEqual(result["state"], "fail")
        diagnostic = next(item for item in result["diagnostics"] if item["code"] == "METRIC-THRESHOLD-FAILED")
        self.assertEqual(diagnostic["rule_id"], "QUAL-COVERAGE")
        self.assertEqual(diagnostic["path"], "measurements.line-coverage.value")

    def test_threshold_policy_change_requires_new_reviewed_exact_revision(self) -> None:
        previous = json.dumps(self.profile, sort_keys=True).encode("utf-8")
        candidate_profile = copy.deepcopy(self.profile)
        candidate_profile["profile_version"] = "1.1.0"
        candidate_profile["supersedes"] = "sample@1.0.0"
        candidate_profile["metric_rules"][0]["threshold"]["value"] = 70
        candidate = json.dumps(candidate_profile, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(candidate).hexdigest()

        missing_review = validate_profile_revision(
            previous, candidate, review_ref=None, reviewed_profile_sha256=None
        )
        self.assertIn("PROFILE-REVISION-REVIEW-REQUIRED", [item["code"] for item in missing_review])

        accepted = validate_profile_revision(
            previous, candidate, review_ref="review:APP-REVIEW-004", reviewed_profile_sha256=digest
        )
        self.assertEqual(accepted, [])

    def test_threshold_revision_rejects_wrong_digest_or_unadvanced_version(self) -> None:
        previous = json.dumps(self.profile, sort_keys=True).encode("utf-8")
        candidate_profile = copy.deepcopy(self.profile)
        candidate_profile["profile_version"] = "1.0.0"
        candidate_profile["supersedes"] = "sample@1.0.0"
        candidate_profile["metric_rules"][0]["threshold"]["value"] = 70
        candidate = json.dumps(candidate_profile, sort_keys=True).encode("utf-8")

        diagnostics = validate_profile_revision(
            previous, candidate, review_ref="review:APP-REVIEW-004",
            reviewed_profile_sha256="0" * 64,
        )
        codes = [item["code"] for item in diagnostics]
        self.assertIn("PROFILE-REVISION-NOT-ADVANCED", codes)
        self.assertIn("PROFILE-REVISION-DIGEST-MISMATCH", codes)

    def test_malformed_types_return_diagnostics_without_crashing(self) -> None:
        malformed = copy.deepcopy(self.profile)
        malformed["risk_dimensions"] = [[]]
        malformed["metric_rules"][0]["availability"] = []
        malformed["metric_rules"][0]["risk_tier"] = {}
        malformed["path_rules"][0]["classification"] = []
        malformed["escalation_floors"][0]["minimum_tier"] = {}
        diagnostics = validate_profile(malformed)
        self.assertTrue(diagnostics)
        self.assertIn("PROFILE-AVAILABILITY-INVALID", [item["code"] for item in diagnostics])

    def test_optional_metric_failure_does_not_block_required_quality_result(self) -> None:
        profile = copy.deepcopy(self.profile)
        optional = copy.deepcopy(profile["metric_rules"][0])
        optional["rule_id"] = "QUAL-OPTIONAL"
        optional["metric_id"] = "optional-score"
        optional["required"] = False
        optional["threshold"]["value"] = 90
        profile["metric_rules"].append(optional)
        result = evaluate_profile(
            profile,
            changed_paths=["src/domain/rule.py"],
            declared_task_risk_tier="high",
            measurements={"line-coverage": 90, "optional-score": 20},
        )
        self.assertEqual(result["state"], "pass")
        self.assertIn("OPTIONAL-METRIC-THRESHOLD-FAILED", [item["code"] for item in result["diagnostics"]])

    def test_duplicate_json_keys_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            parse_json('{"schema_version":"1","schema_version":"2"}', label="profile fixture")

    def test_scope_diagnostics_keep_generated_exports_and_unrelated_paths_visible(self) -> None:
        diagnostics = diagnose_change_scope(
            changed_paths=["src/domain/rule.py", "src/generated/client.py", "docs/notes.md"],
            task_paths=["src/domain/rule.py", "src/generated/client.py"],
            measured_paths=["src/domain/rule.py"],
            generated_paths=["src/generated/client.py"],
            exported_symbols={"src/domain/rule.py": ["authorize"]},
            traced_symbols={"src/domain/rule.py": []},
        )
        codes = [item["code"] for item in diagnostics]
        self.assertIn("CHANGED-PATH-UNMEASURED", codes)
        self.assertIn("GENERATED-PATH-REVIEW", codes)
        self.assertIn("EXPORTED-SYMBOL-UNTRACED", codes)
        self.assertIn("UNRELATED-CHANGE-PATH", codes)
        self.assertIn("MIXED-SCOPE-CHANGE", codes)

    def test_scope_diagnostics_reject_noncanonical_paths_without_crashing(self) -> None:
        diagnostics = diagnose_change_scope(
            changed_paths=["../outside.py", "src/domain/rule.py"],
            task_paths="src/domain/rule.py",
            measured_paths=["src/domain/rule.py"],
        )
        codes = [item["code"] for item in diagnostics]
        self.assertIn("SCOPE-PATH-INVALID", codes)
        self.assertIn("SCOPE-PATHS-INVALID", codes)

    def test_scope_diagnostics_do_not_mutate_source_bytes(self) -> None:
        source_path = Path(self.id().replace(".", "_") + "_source.py")
        source = b"def authorize(user): return user.is_allowed\n"
        try:
            source_path.write_bytes(source)
            before = hashlib.sha256(source_path.read_bytes()).hexdigest()
            diagnose_change_scope(
                changed_paths=["src/domain/rule.py"],
                task_paths=[],
                measured_paths=[],
                exported_symbols={"src/domain/rule.py": ["authorize"]},
            )
            self.assertEqual(hashlib.sha256(source_path.read_bytes()).hexdigest(), before)
        finally:
            source_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
