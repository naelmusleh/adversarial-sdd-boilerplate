from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from scripts.artifacts import _latest_gate_runs, _published_checkpoint_problems, file_sha256, json_sha256, schema_definition_problems, validate_gate_run_records, validate_schema_value


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
        schema_v11 = json.loads((ROOT / "docs/framework/schemas/gate-run-v1.1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema_definition_problems(schema), [])
        self.assertEqual(schema_definition_problems(schema_v11), [])
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

    def test_dependency_free_draft_2020_12_subset_accepts_all_valid_gate_fixtures(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        for path in sorted((FIXTURES / "valid").glob("G-*.json")):
            with self.subTest(gate=path.stem):
                record = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(validate_schema_value(record, schema, schema), [])

    def test_dependency_free_draft_2020_12_subset_rejects_all_invalid_gate_fixtures(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        for path in sorted((FIXTURES / "invalid").glob("G-*.json")):
            with self.subTest(gate=path.stem):
                record = json.loads(path.read_text(encoding="utf-8"))
                errors = validate_schema_value(record, schema, schema)
                self.assertTrue(errors, f"invalid fixture unexpectedly passed: {path}")

    def test_schema_engine_rejects_unsupported_schema_keywords(self) -> None:
        self.assertTrue(schema_definition_problems({"type": "string", "unevaluatedProperties": False}))
        self.assertTrue(schema_definition_problems({"type": 17}))
        self.assertTrue(schema_definition_problems({"required": "gate_id"}))
        self.assertTrue(schema_definition_problems({"properties": {"x": "not-a-schema"}}))
        self.assertTrue(schema_definition_problems({"format": "invented-format"}))
        self.assertTrue(schema_definition_problems({"format": []}))

    def _validate_in_isolated_app(self, record: dict[str, object], schema: dict[str, object]) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "specification.md").write_text("Synthetic requirement: FIXTURE-REQ-001\n", encoding="utf-8")
            (root / "backlog.md").write_text("Synthetic task: FIXTURE-TASK-001\n", encoding="utf-8")
            (root / "decisions").mkdir()
            (root / "decisions/DECISION-LOG.md").write_text("Synthetic decision: FIXTURE-DECISION-001\n", encoding="utf-8")
            input_path = root / "docs/framework/examples/gate-contract-v1/inputs/FIXTURE-INPUT-001.md"
            input_path.parent.mkdir(parents=True)
            shutil.copy2(FIXTURES / "inputs/FIXTURE-INPUT-001.md", input_path)
            gate_runs = root / ".sdd/gate-runs"
            gate_runs.mkdir(parents=True)
            baseline = record.get("_baseline_record")
            if isinstance(baseline, dict):
                (gate_runs / f"{baseline['record_id']}.json").write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
            record_path = gate_runs / f"{record['record_id']}.json"
            record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
            return validate_gate_run_records(root, schema, "SYNTHETIC")

    def test_full_validator_accepts_all_ten_in_progress_fixtures_and_rejects_four_bypass_classes_per_gate(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        for path in sorted((FIXTURES / "valid").glob("G-*.json")):
            baseline = json.loads(path.read_text(encoding="utf-8"))
            baseline["application_id"] = "SYNTHETIC"
            with self.subTest(gate=path.stem, case="valid"):
                self.assertEqual(self._validate_in_isolated_app(baseline, schema), [])

            profile = PROFILE_BY_GATE[path.stem]
            missing = json.loads(json.dumps(baseline))
            required = schema["$defs"][profile]["required"][0]
            del missing["gate_data"][required]
            with self.subTest(gate=path.stem, case="missing-required-gate-artifact-field"):
                self.assertTrue(validate_schema_value(missing, schema, schema))

            stale = json.loads(json.dumps(baseline))
            stale["scope"]["artifact_refs"][0]["sha256"] = "sha256:" + "0" * 64
            with self.subTest(gate=path.stem, case="stale-artifact-identity"):
                self.assertTrue(any("digest is stale" in error for error in self._validate_in_isolated_app(stale, schema)))

            false_pass = json.loads(json.dumps(baseline))
            false_pass["gate_result"] = "passed"
            for criterion in false_pass["criteria_results"]:
                criterion["outcome"] = "pass"
            with self.subTest(gate=path.stem, case="false-pass-without-evidence"):
                self.assertTrue(self._validate_in_isolated_app(false_pass, schema))

            illegal = json.loads(json.dumps(baseline))
            illegal["record_version"] = 2
            illegal["supersedes_run_id"] = "MISSING-PRIOR-001"
            with self.subTest(gate=path.stem, case="unresolved-transition"):
                self.assertTrue(any("does not resolve" in error for error in self._validate_in_isolated_app(illegal, schema)))

    def test_v11_conditional_feasibility_requires_trigger_and_unknown_never_unblocks(self) -> None:
        schema = json.loads((ROOT / "docs/framework/schemas/gate-run-v1.1.schema.json").read_text(encoding="utf-8"))
        record = json.loads((FIXTURES / "valid/G-FEAS.json").read_text(encoding="utf-8"))
        record["application_id"] = "SYNTHETIC"
        record["contract_version"] = "1.1"
        dependency = record["gate_data"]["probes"][0]["task_dependencies"][0]
        dependency["state"] = "conditional"
        dependency["condition"] = "A privacy review returns an approved bounded scope."
        dependency["safe_work_boundary"] = "No provider integration is implemented."
        effect = record["dependency_effects"][0]
        effect.update({key: dependency[key] for key in ("state", "condition", "safe_work_boundary")})
        self.assertTrue(validate_schema_value(record, schema, schema))
        dependency["state_change_trigger"] = "Owner records the privacy decision; rerun G-FEAS before G-ARCH."
        effect["state_change_trigger"] = dependency["state_change_trigger"]
        self.assertEqual(validate_schema_value(record, schema, schema), [])
        self.assertEqual(self._validate_in_isolated_app(record, schema), [])

        dependency["state"] = "unblocked"
        effect["state"] = "unblocked"
        dependency.pop("state_change_trigger")
        self.assertTrue(any("cannot leave task" in error for error in self._validate_in_isolated_app(record, schema)))

    def test_constrained_feasibility_cannot_unblock_or_disagree_with_dependency_effect(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        record = json.loads((FIXTURES / "valid/G-FEAS.json").read_text(encoding="utf-8"))
        record["application_id"] = "SYNTHETIC"
        dependency = record["gate_data"]["probes"][0]["task_dependencies"][0]
        dependency.update({"state": "unblocked", "condition": "", "safe_work_boundary": ""})
        record["gate_data"]["probes"][0]["classification"] = "constrained"
        record["dependency_effects"][0].update(dependency)
        errors = self._validate_in_isolated_app(record, schema)
        self.assertTrue(any("cannot leave task" in error for error in errors), errors)
        dependency["state"] = "blocked"
        record["dependency_effects"][0]["state"] = "unblocked"
        errors = self._validate_in_isolated_app(record, schema)
        self.assertTrue(any("does not match its probe" in error for error in errors), errors)

    def test_ci_evidence_is_checked_against_this_record_source_commit(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        record = json.loads((FIXTURES / "valid/G-INTENT.json").read_text(encoding="utf-8"))
        record["application_id"] = "SYNTHETIC"
        commit = "a" * 40
        record["source_snapshot"].update({"commit_sha": commit, "revision_state": "clean-commit"})
        record["criteria_results"][0]["evidence_ids"] = ["EVIDENCE-CI-001"]
        record["evidence"] = [{
            "evidence_id": "EVIDENCE-CI-001", "type": "ci-run", "criterion_ids": ["GINT-01"],
            "observed_at": "2026-10-20T12:00:00Z", "observed_by": "synthetic CI",
            "source_revision": commit, "scope_ref": "fixture scope", "locator": "fixture run",
            "record_sha256": "sha256:" + "1" * 64, "limitations": ["synthetic"],
            "details": {"provider": "fixture", "run_id_or_url": "fixture-run-1", "commit_sha": commit,
                        "workflow_job": "verify", "conclusion": "success", "scope": "fixture"}
        }]
        self.assertEqual(validate_schema_value(record, schema, schema), [])
        self.assertEqual(self._validate_in_isolated_app(record, schema), [])
        record["evidence"][0]["details"]["commit_sha"] = "b" * 40
        self.assertTrue(any("commit_sha does not match" in error for error in self._validate_in_isolated_app(record, schema)))

    def test_g_impl_rejects_required_ci_evidence_with_failed_conclusion(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        record = json.loads((FIXTURES / "valid/G-IMPL.json").read_text(encoding="utf-8"))
        record["application_id"] = "SYNTHETIC"
        commit = record["source_snapshot"]["commit_sha"]
        check_id = "CI-CHECK-001"
        evidence_id = "CI-EVIDENCE-001"
        record["gate_data"]["required_checks"] = [{
            "check_id": check_id, "command_or_procedure": "python -m unittest", "tool_runtime_version": "Python 3.13",
            "source_revision": commit, "scope": "tests", "pass_condition": "exit code 0",
            "result": "passed", "evidence_id": evidence_id,
        }]
        record["gate_data"]["criterion_check_mappings"] = [{
            "criterion_id": row["criterion_id"], "check_ids": [check_id], "manual_method": None,
        } for row in record["criteria_results"]]
        record["criteria_results"] = [{**row, "outcome": "pass", "evidence_ids": [evidence_id]} for row in record["criteria_results"]]
        record["evidence"] = [{
            "evidence_id": evidence_id, "type": "ci-run", "criterion_ids": [row["criterion_id"] for row in record["criteria_results"]],
            "observed_at": "2026-10-20T12:00:00Z", "observed_by": "synthetic CI", "source_revision": commit,
            "scope_ref": "tests", "locator": "fixture-run", "record_sha256": "sha256:" + "1" * 64,
            "limitations": ["synthetic"], "details": {"provider": "fixture", "run_id_or_url": "fixture-run",
                "commit_sha": commit, "workflow_job": check_id, "conclusion": "failure", "scope": "tests"},
        }]
        record["change_control"].update({"commit_sha": commit, "branch_ref": "refs/heads/candidate",
            "remote": "fixture", "push_result": "pushed", "authorization_ref": "OWNER-DECISION-001",
            "ci_runs": [{"provider": "fixture", "run_id_or_url": "fixture-run", "commit_sha": commit,
                "check": check_id, "status": "passed", "scope": "tests"}]})
        record["authority"]["owner_decisions"] = [{"decision_id": "OWNER-DECISION-001", "decision_maker": "fixture-owner",
            "role": "synthetic owner", "decided_at": "2026-10-20T12:00:00Z",
            "choice": f"authorize-publish; commit_sha={commit}; branch_ref=refs/heads/candidate; remote=fixture",
            "affected_ids": ["FIXTURE-TASK-001"], "rationale": "synthetic", "revisit_condition": "synthetic"}]
        errors = self._validate_in_isolated_app(record, schema)
        self.assertTrue(any("CI evidence 'CI-EVIDENCE-001' with a non-success conclusion" in error for error in errors), errors)

    def test_published_checkpoint_requires_exact_owner_authorization_scope(self) -> None:
        commit = "a" * 40
        change = {"commit_sha": commit, "branch_ref": "refs/heads/candidate", "remote": "fixture",
                  "push_result": "pushed", "authorization_ref": "OWNER-DECISION-001"}
        authority = {"accountable_owner": {"identity": "fixture-owner"}, "owner_decisions": [{
            "decision_id": "OWNER-DECISION-001", "decision_maker": "fixture-owner",
            "choice": f"authorize-publish; commit_sha={commit}; branch_ref=refs/heads/candidate; remote=fixture",
            "affected_ids": ["TASK-001"],
        }]}
        self.assertEqual(_published_checkpoint_problems(change, commit, authority, ["TASK-001"], "G-IMPL"), [])
        authority["owner_decisions"][0]["choice"] = "authorize-publish"
        problems = _published_checkpoint_problems(change, commit, authority, ["TASK-001"], "G-IMPL")
        self.assertTrue(any("exact commit_sha, branch_ref, and remote fields" in problem for problem in problems), problems)

    def test_release_pass_requires_actual_artifact_reference_owner_and_successful_current_ci(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        record = json.loads((FIXTURES / "valid/G-RELEASE.json").read_text(encoding="utf-8"))
        record["application_id"] = "SYNTHETIC"
        commit = record["source_snapshot"]["commit_sha"]
        digest = file_sha256(FIXTURES / "inputs/FIXTURE-INPUT-001.md")
        record["gate_result"] = "passed"
        record["record_version"] = 2
        record["supersedes_run_id"] = "FIXTURE-RELEASE-VALID-001-BASE"
        baseline = json.loads(json.dumps(record))
        baseline.update({"record_id": "FIXTURE-RELEASE-VALID-001-BASE", "record_version": 1,
                         "gate_result": "in-progress", "supersedes_run_id": None,
                         "created_at": "2026-10-20T11:00:00Z"})
        isolated_validator = self._validate_in_isolated_app
        def validate_with_baseline(value: dict[str, object], schema_value: dict[str, object]) -> list[str]:
            original = value.pop("_baseline_record", None)
            try:
                result = isolated_validator(value, schema_value)
                if isinstance(original, dict):
                    with tempfile.TemporaryDirectory() as temporary:
                        root = Path(temporary)
                        (root / "specification.md").write_text("Synthetic requirement: FIXTURE-REQ-001\n", encoding="utf-8")
                        (root / "backlog.md").write_text("Synthetic task: FIXTURE-TASK-001\n", encoding="utf-8")
                        (root / "decisions").mkdir()
                        (root / "decisions/DECISION-LOG.md").write_text("Synthetic decision: FIXTURE-DECISION-001\n", encoding="utf-8")
                        input_path = root / "docs/framework/examples/gate-contract-v1/inputs/FIXTURE-INPUT-001.md"
                        input_path.parent.mkdir(parents=True)
                        shutil.copy2(FIXTURES / "inputs/FIXTURE-INPUT-001.md", input_path)
                        gate_runs = root / ".sdd/gate-runs"
                        gate_runs.mkdir(parents=True)
                        (gate_runs / f"{original['record_id']}.json").write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")
                        (gate_runs / f"{value['record_id']}.json").write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
                        result = validate_gate_run_records(root, schema_value, "SYNTHETIC")
                return result
            finally:
                if isinstance(original, dict):
                    value["_baseline_record"] = original
        self._validate_in_isolated_app = validate_with_baseline
        record["_baseline_record"] = baseline
        record["gate_data"].update({"tested_commit_sha": commit, "artifact_sha256": digest,
            "environment": "production", "required_check_evidence_ids": ["EVIDENCE-CI-001"],
            "security_accessibility_platform_evidence_ids": ["EVIDENCE-CI-001"],
            "owner_authorization_id": "FIXTURE-DECISION-001",
            "migration_backup_rollback_plan": (
                "Operator fixture-owner: if exact-SHA checks, artifact digest, or authorization fail, do not activate the candidate; "
                "retain the prior local artifact and state snapshot; restore the snapshot into an isolated temporary directory; "
                "verify its recorded SHA-256 and tenant-scoped read result; record the outcome before retrying."
            )})
        record["change_control"].update({
            "commit_sha": commit,
            "branch_ref": "refs/heads/release-candidate",
            "remote": "https://github.com/example/app",
            "push_result": "pushed",
            "authorization_ref": "FIXTURE-DECISION-001",
            "release_artifact_sha256": digest,
            "ci_runs": [{"provider": "fixture", "run_id_or_url": "fixture-run", "commit_sha": commit,
                         "check": "release-check", "status": "passed", "scope": "fixture"}],
        })
        for item in record["criteria_results"]:
            item["outcome"] = "pass"
        record["criteria_results"][0]["evidence_ids"] = ["EVIDENCE-ARTIFACT-001"]
        record["criteria_results"][1]["evidence_ids"] = ["EVIDENCE-CI-001"]
        record["criteria_results"][2]["evidence_ids"] = ["EVIDENCE-CI-001"]
        record["evidence"] = [
            {"evidence_id": "EVIDENCE-ARTIFACT-001", "type": "artifact-reference", "criterion_ids": ["GREL-01"],
             "observed_at": "2026-10-20T12:00:00Z", "observed_by": "fixture", "source_revision": commit,
             "scope_ref": "fixture scope", "locator": "docs/framework/examples/gate-contract-v1/inputs/FIXTURE-INPUT-001.md",
             "record_sha256": digest, "limitations": ["synthetic"], "details": {"artifact_id": "FIXTURE-INPUT-001",
             "version": "1.0", "path": "docs/framework/examples/gate-contract-v1/inputs/FIXTURE-INPUT-001.md", "sha256": digest}},
            {"evidence_id": "EVIDENCE-CI-001", "type": "ci-run", "criterion_ids": ["GREL-02", "GREL-03"],
             "observed_at": "2026-10-20T12:00:00Z", "observed_by": "fixture CI", "source_revision": commit,
             "scope_ref": "fixture scope", "locator": "fixture run", "record_sha256": "sha256:" + "1" * 64,
             "limitations": ["synthetic"], "details": {"provider": "fixture", "run_id_or_url": "fixture-run",
             "commit_sha": commit, "workflow_job": "release-check", "conclusion": "failure", "scope": "fixture"}}
        ]
        record["authority"]["owner_decisions"] = [{"decision_id": "FIXTURE-DECISION-001", "decision_maker": "different-owner",
            "role": "fixture", "decided_at": "2026-10-20T12:00:00Z", "choice": "approve", "affected_ids": ["FIXTURE-TASK-001"],
            "rationale": "synthetic", "revisit_condition": "synthetic"}]
        errors = self._validate_in_isolated_app(record, schema)
        self.assertTrue(any("accountable owner" in error for error in errors), errors)
        self.assertTrue(any("successful ci-run" in error for error in errors), errors)
        record["authority"]["owner_decisions"][0].update({"decision_maker": "fixture-owner",
            "choice": f"authorize-release: {digest}; environment: production", "revisit_condition": "release-window: 2026-10-20T11:00:00Z/2026-10-20T13:00:00Z"})
        record["evidence"][1]["details"]["conclusion"] = "success"
        errors = self._validate_in_isolated_app(record, schema)
        self.assertFalse(any("release-window" in error or "fall within the owner-authorized" in error for error in errors), errors)
        release_errors = [error for error in errors if "[G-RELEASE]:" in error and "required upstream gate" not in error]
        self.assertEqual(release_errors, [], release_errors)

        case = json.loads(json.dumps(record))
        attempt_details = case["evidence"][1]["details"]
        attempt_details.update({"provider": "github-actions", "run_id_or_url": "https://github.com/example/actions/runs/123"})
        case["change_control"]["ci_runs"][0].update({"provider": "github-actions", "run_id_or_url": attempt_details["run_id_or_url"]})
        errors = self._validate_in_isolated_app(case, schema)
        self.assertTrue(any("exact run attempt URL" in error for error in errors), errors)
        attempt_details["run_id_or_url"] += "/attempts/2"
        case["change_control"]["ci_runs"][0]["run_id_or_url"] = attempt_details["run_id_or_url"]
        errors = self._validate_in_isolated_app(case, schema)
        self.assertFalse(any("exact run attempt URL" in error for error in errors), errors)

        case = json.loads(json.dumps(record))
        case["change_control"]["authorization_ref"] = "MISSING-PUBLISH-AUTH-001"
        errors = self._validate_in_isolated_app(case, schema)
        self.assertTrue(any("authorization_ref must resolve to an owner decision" in error for error in errors), errors)
        case = json.loads(json.dumps(record))
        case["authority"]["owner_decisions"][0]["affected_ids"] = ["OTHER-TASK-001"]
        errors = self._validate_in_isolated_app(case, schema)
        self.assertTrue(any("publication authorization must identify at least one in-scope task" in error for error in errors), errors)

        case = json.loads(json.dumps(record))
        case["gate_data"]["artifact_sha256"] = "sha256:" + "0" * 64
        case["change_control"]["release_artifact_sha256"] = case["gate_data"]["artifact_sha256"]
        errors = self._validate_in_isolated_app(case, schema)
        self.assertTrue(any("artifact digest" in error or "artifact-reference evidence" in error for error in errors), errors)

        case = json.loads(json.dumps(record))
        case["gate_data"]["owner_authorization_id"] = "MISSING-OWNER-AUTH-001"
        errors = self._validate_in_isolated_app(case, schema)
        self.assertTrue(any("owner_authorization_id does not resolve" in error for error in errors), errors)

        case = json.loads(json.dumps(record))
        case["change_control"]["authorization_ref"] = "OTHER-OWNER-DECISION-001"
        errors = self._validate_in_isolated_app(case, schema)
        self.assertTrue(any("authorization_ref must match gate_data.owner_authorization_id" in error for error in errors), errors)

        case = json.loads(json.dumps(record))
        case["change_control"].update({"push_result": "failed", "remote": None, "branch_ref": None})
        errors = self._validate_in_isolated_app(case, schema)
        self.assertTrue(any("push_result must be 'pushed'" in error for error in errors), errors)

        case = json.loads(json.dumps(record))
        case["evidence"][1]["details"]["commit_sha"] = "b" * 40
        errors = self._validate_in_isolated_app(case, schema)
        self.assertTrue(any("commit_sha does not match" in error or "exact gate-run commit" in error for error in errors), errors)

        case = json.loads(json.dumps(record))
        case["evidence"][1]["details"]["conclusion"] = "cancelled"
        case["change_control"]["ci_runs"][0]["status"] = "cancelled"
        errors = self._validate_in_isolated_app(case, schema)
        self.assertTrue(any("successful ci-run" in error for error in errors), errors)

        case = json.loads(json.dumps(record))
        case["evidence"][1]["details"]["conclusion"] = "cancelled"
        case["change_control"]["ci_runs"][0]["status"] = "pending"
        errors = self._validate_in_isolated_app(case, schema)
        self.assertTrue(any("successful ci-run" in error for error in errors), errors)

        case = json.loads(json.dumps(record))
        case["evidence"] = [item for item in case["evidence"] if item["evidence_id"] != "EVIDENCE-ARTIFACT-001"]
        errors = self._validate_in_isolated_app(case, schema)
        self.assertTrue(any("artifact-reference evidence" in error for error in errors), errors)

        case = json.loads(json.dumps(record))
        case["gate_data"]["migration_backup_rollback_plan"] = ""
        errors = self._validate_in_isolated_app(case, schema)
        self.assertTrue(any("migration_backup_rollback_plan" in error for error in errors), errors)

        record["authority"]["owner_decisions"][0]["decided_at"] = "2026-10-20T12:30:00Z"
        errors = self._validate_in_isolated_app(record, schema)
        self.assertTrue(any("must be recorded no later" in error for error in errors), errors)
        record["authority"]["owner_decisions"][0]["decided_at"] = "2026-10-20T11:30:00Z"
        record["authority"]["owner_decisions"][0]["revisit_condition"] = "release-window: 2026-10-20T13:00:00Z/2026-10-20T14:00:00Z"
        errors = self._validate_in_isolated_app(record, schema)
        self.assertTrue(any("must fall within the owner-authorized release window" in error for error in errors), errors)

    def test_v11_evidence_scope_hash_is_bound_to_gate_run_scope(self) -> None:
        schema = json.loads((ROOT / "docs/framework/schemas/gate-run-v1.1.schema.json").read_text(encoding="utf-8"))
        record = json.loads((FIXTURES / "valid/G-INTENT.json").read_text(encoding="utf-8"))
        record["application_id"] = "SYNTHETIC"
        record["contract_version"] = "1.1"
        record["criteria_results"][0]["outcome"] = "pass"
        record["criteria_results"][0]["evidence_ids"] = ["EVIDENCE-001"]
        record["evidence"] = [{
            "evidence_id": "EVIDENCE-001", "type": "manual-observation", "criterion_ids": ["GINT-01"],
            "observed_at": "2026-10-20T12:00:00Z", "observed_by": "synthetic reviewer",
            "source_revision": "a" * 40, "scope_ref": "sha256:" + "0" * 64, "locator": "synthetic observation",
            "record_sha256": "sha256:" + "1" * 64, "limitations": ["synthetic fixture"],
            "details": {"observer": "synthetic reviewer", "procedure": "fixture", "observed_at": "2026-10-20T12:00:00Z", "scope": "fixture", "result": "observed", "limitations": ["synthetic"]},
        }]
        self.assertEqual(validate_schema_value(record, schema, schema), [])
        errors = self._validate_in_isolated_app(record, schema)
        self.assertTrue(any("scope_ref does not match" in error for error in errors), errors)
        record["evidence"][0]["scope_ref"] = json_sha256(record["scope"])
        record["evidence"][0]["details"]["scope"] = json_sha256(record["scope"])
        self.assertEqual(self._validate_in_isolated_app(record, schema), [])

    def test_gate_run_reader_rejects_duplicate_keys_malformed_oversized_and_traversal(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            runs = root / ".sdd/gate-runs"
            runs.mkdir(parents=True)

            record_path = runs / "BROKEN-RECORD-001.json"
            record_path.write_text('{"record_id":"A","record_id":"B"}', encoding="utf-8")
            errors = validate_gate_run_records(root, schema, "SYNTHETIC")
            self.assertTrue(any("duplicate JSON key" in error for error in errors))

            record_path.write_text("{", encoding="utf-8")
            errors = validate_gate_run_records(root, schema, "SYNTHETIC")
            self.assertTrue(any("invalid gate-run JSON" in error for error in errors))

            record_path.write_text(" " * (1_048_577), encoding="utf-8")
            errors = validate_gate_run_records(root, schema, "SYNTHETIC")
            self.assertTrue(any("byte limit" in error for error in errors))

            record_path.unlink()
            outside = root.parent / (root.name + "-outside-file.json")
            try:
                outside.write_text("{}", encoding="utf-8")
                record_path.symlink_to(outside)
                errors = validate_gate_run_records(root, schema, "SYNTHETIC")
                self.assertTrue(any("resolves outside" in error for error in errors))
            finally:
                outside.unlink(missing_ok=True)

    def test_gate_run_directory_symlink_escape_is_rejected(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            outside = root.parent / (root.name + "-outside")
            outside.mkdir()
            try:
                (root / ".sdd").mkdir()
                (root / ".sdd/gate-runs").symlink_to(outside, target_is_directory=True)
                errors = validate_gate_run_records(root, schema, "SYNTHETIC")
                self.assertTrue(any("resolves outside" in error for error in errors))
            finally:
                shutil.rmtree(outside)

    def test_downstream_pass_pins_latest_upstream_run_and_detects_stale_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            runs = root / ".sdd/gate-runs"
            runs.mkdir(parents=True)
            first = {
                "record_id": "SYNTHETIC-INTENT-001", "record_version": 1, "gate_id": "G-INTENT",
                "created_at": "2026-10-20T10:00:00Z", "supersedes_run_id": None, "gate_result": "in-progress",
            }
            first_path = runs / f"{first['record_id']}.json"
            first_path.write_text(json.dumps(first), encoding="utf-8")
            latest = {
                "record_id": "SYNTHETIC-INTENT-002", "record_version": 2, "gate_id": "G-INTENT",
                "created_at": "2026-10-20T11:00:00Z", "supersedes_run_id": first["record_id"], "gate_result": "passed",
            }
            latest_path = runs / f"{latest['record_id']}.json"
            latest_path.write_text(json.dumps(latest), encoding="utf-8")
            setup_first = {
                "record_id": "SYNTHETIC-SETUP-001", "record_version": 1, "gate_id": "G-SETUP",
                "created_at": "2026-10-20T12:00:00Z", "supersedes_run_id": None, "gate_result": "in-progress",
            }
            setup_first_path = runs / f"{setup_first['record_id']}.json"
            setup_first_path.write_text(json.dumps(setup_first), encoding="utf-8")
            setup_latest = {
                "record_id": "SYNTHETIC-SETUP-002", "record_version": 2, "gate_id": "G-SETUP",
                "created_at": "2026-10-20T13:00:00Z", "supersedes_run_id": setup_first["record_id"], "gate_result": "passed",
                "scope": {"artifact_refs": [{
                    "path": first_path.relative_to(root).as_posix(), "artifact_id": first["record_id"],
                    "version": "1", "sha256": file_sha256(first_path),
                }]},
            }
            setup_latest_path = runs / f"{setup_latest['record_id']}.json"
            setup_latest_path.write_text(json.dumps(setup_latest), encoding="utf-8")
            records = {
                item["record_id"]: (path, item)
                for item, path in ((first, first_path), (latest, latest_path), (setup_first, setup_first_path), (setup_latest, setup_latest_path))
            }
            _, errors = _latest_gate_runs(records)
            self.assertTrue(any("must pin current upstream run" in error for error in errors), errors)

            setup_latest["scope"]["artifact_refs"][0].update({
                "path": latest_path.relative_to(root).as_posix(), "artifact_id": latest["record_id"],
                "version": "2", "sha256": file_sha256(latest_path),
            })
            setup_latest_path.write_text(json.dumps(setup_latest), encoding="utf-8")
            _, errors = _latest_gate_runs(records)
            self.assertFalse(any("must pin current upstream run" in error for error in errors), errors)

    def test_superseded_downstream_history_does_not_block_a_valid_rebased_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            runs = root / ".sdd/gate-runs"
            runs.mkdir(parents=True)

            def add(record_id: str, gate_id: str, version: int, created_at: str, result: str, supersedes: str | None, refs: list[dict[str, str]] | None = None):
                record = {
                    "record_id": record_id,
                    "record_version": version,
                    "gate_id": gate_id,
                    "created_at": created_at,
                    "supersedes_run_id": supersedes,
                    "gate_result": result,
                    "scope": {"artifact_refs": refs or []},
                }
                path = runs / f"{record_id}.json"
                path.write_text(json.dumps(record), encoding="utf-8")
                return path, record

            records = {}
            intent1_path, intent1 = add("SYNTHETIC-INTENT-001", "G-INTENT", 1, "2026-10-20T10:00:00Z", "in-progress", None)
            records[intent1["record_id"]] = (intent1_path, intent1)
            intent2_path, intent2 = add("SYNTHETIC-INTENT-002", "G-INTENT", 2, "2026-10-20T11:00:00Z", "passed", intent1["record_id"])
            records[intent2["record_id"]] = (intent2_path, intent2)
            setup1_path, setup1 = add(
                "SYNTHETIC-SETUP-001", "G-SETUP", 1, "2026-10-20T12:00:00Z", "passed", None,
                [{"path": intent2_path.relative_to(root).as_posix(), "artifact_id": intent2["record_id"], "version": "2", "sha256": file_sha256(intent2_path)}],
            )
            records[setup1["record_id"]] = (setup1_path, setup1)
            intent3_path, intent3 = add("SYNTHETIC-INTENT-003", "G-INTENT", 3, "2026-10-20T13:00:00Z", "passed", intent2["record_id"])
            records[intent3["record_id"]] = (intent3_path, intent3)
            setup2_path, setup2 = add(
                "SYNTHETIC-SETUP-002", "G-SETUP", 2, "2026-10-20T14:00:00Z", "passed", setup1["record_id"],
                [{"path": intent3_path.relative_to(root).as_posix(), "artifact_id": intent3["record_id"], "version": "3", "sha256": file_sha256(intent3_path)}],
            )
            records[setup2["record_id"]] = (setup2_path, setup2)

            _, errors = _latest_gate_runs(records)
            self.assertFalse(any("current upstream run" in error or "upstream gate reference" in error for error in errors), errors)

    def test_archive_pinned_snapshot_requires_and_accepts_complete_digest_binding(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        record = json.loads((FIXTURES / "valid/G-INTENT.json").read_text(encoding="utf-8"))
        record["application_id"] = "SYNTHETIC"
        record["source_snapshot"]["commit_sha"] = None
        record["source_snapshot"]["revision_state"] = "archive-pinned"
        record["source_snapshot"]["uncommitted_reason"] = "Source archive has no Git metadata; exact input files are digest-pinned."
        for ref in record["source_snapshot"]["files"] + record["scope"]["artifact_refs"]:
            ref["source_revision"] = None
        self.assertEqual(self._validate_in_isolated_app(record, schema), [])

        record["source_snapshot"]["files"] = []
        errors = self._validate_in_isolated_app(record, schema)
        self.assertTrue(any("null commit_sha requires a digest-complete archive-pinned snapshot" in error for error in errors), errors)

    def test_gate_run_chronology_compares_normalized_timezone_offsets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            runs = root / ".sdd/gate-runs"
            runs.mkdir(parents=True)
            intent = {
                "record_id": "SYNTHETIC-INTENT-001", "record_version": 1, "gate_id": "G-INTENT",
                "created_at": "2026-10-20T10:00:00-05:00", "supersedes_run_id": None, "gate_result": "passed",
            }
            intent_path = runs / f"{intent['record_id']}.json"
            intent_path.write_text(json.dumps(intent), encoding="utf-8")
            setup = {
                "record_id": "SYNTHETIC-SETUP-001", "record_version": 1, "gate_id": "G-SETUP",
                "created_at": "2026-10-20T14:30:00Z", "supersedes_run_id": None, "gate_result": "passed",
                "scope": {"artifact_refs": [{
                    "path": intent_path.relative_to(root).as_posix(), "artifact_id": intent["record_id"],
                    "version": "1", "sha256": file_sha256(intent_path),
                }]},
            }
            setup_path = runs / f"{setup['record_id']}.json"
            setup_path.write_text(json.dumps(setup), encoding="utf-8")
            _, errors = _latest_gate_runs({
                intent["record_id"]: (intent_path, intent), setup["record_id"]: (setup_path, setup),
            })
            self.assertTrue(any("must be timezone-aware and later than upstream G-INTENT" in error for error in errors), errors)

            replacement = dict(intent)
            replacement.update({
                "record_id": "SYNTHETIC-INTENT-002", "record_version": 2,
                "created_at": "2026-10-20T14:30:00Z", "supersedes_run_id": intent["record_id"],
            })
            replacement_path = runs / f"{replacement['record_id']}.json"
            replacement_path.write_text(json.dumps(replacement), encoding="utf-8")
            _, errors = _latest_gate_runs({
                intent["record_id"]: (intent_path, intent), replacement["record_id"]: (replacement_path, replacement),
            })
            self.assertTrue(any("rerun created_at must be timezone-aware and later than superseded run" in error for error in errors), errors)

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
