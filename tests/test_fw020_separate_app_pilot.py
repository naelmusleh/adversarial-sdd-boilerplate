from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.artifacts import json_sha256


ROOT = Path(__file__).resolve().parents[1]
GATE_FIXTURES = ROOT / "docs/framework/examples/gate-contract-v1"
SYNTHETIC_EXCLUSION = "This synthetic governance pilot does not build or release FlagLite."
GATES = (
    "G-INTENT", "G-SETUP", "G-REQ", "G-FEAS", "G-COVERAGE",
    "G-CX", "G-ARCH", "G-IMPL", "G-RELEASE", "G-OPERATE",
)
INVALID_REQUIRED_GATE_DATA = {
    "G-INTENT": "non_goals",
    "G-SETUP": "cold_start_evidence_ids",
    "G-REQ": "review_evidence_ids",
    "G-FEAS": "probes",
    "G-COVERAGE": "journeys",
    "G-CX": "interaction_evidence_ids",
    "G-ARCH": "verification_contracts",
    "G-IMPL": "required_checks",
    "G-RELEASE": "owner_authorization_id",
    "G-OPERATE": "telemetry_gaps",
}


class SeparateAppAdversarialPilotTests(unittest.TestCase):
    """Run the app-local validator against a disposable initialized application."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="fw020-flaglite-")
        cls.app = Path(cls.temporary.name) / "flaglite"
        cls.framework_revision = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, text=True, capture_output=True
        ).stdout.strip()
        subprocess.run([
            "python3", str(ROOT / "scripts/init_app_project.py"),
            "--name", "FlagLite Governance Pilot (Synthetic)",
            "--prefix", "FLAGLITE", "--target", str(cls.app),
            "--include-lifecycle-records", "--framework-revision", cls.framework_revision,
        ], cwd=ROOT, check=True, text=True, capture_output=True)
        mission_path = cls.app / "mission.md"
        mission_text = mission_path.read_text(encoding="utf-8")
        mission_text = mission_text.replace(
            "## Owner and references",
            f"{SYNTHETIC_EXCLUSION}\n\n## Owner and references",
        )
        mission_path.write_text(mission_text, encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=cls.app, check=True)
        cls._git(cls.app, "add", ".")
        cls._git(cls.app, "commit", "-m", "chore: initialize synthetic FW020 app")

        (cls.app / "specification.md").write_text(
            (cls.app / "specification.md").read_text(encoding="utf-8")
            + "\n## Synthetic validator fixture IDs (not product requirements)\n"
            + "- FIXTURE-REQ-001: Disposable FW020 structural reference only.\n",
            encoding="utf-8",
        )
        (cls.app / "backlog.md").write_text(
            (cls.app / "backlog.md").read_text(encoding="utf-8")
            + "\n## Synthetic validator fixture tasks (not product work)\n"
            + "- FIXTURE-TASK-001: Disposable FW020 structural reference only.\n",
            encoding="utf-8",
        )
        input_target = cls.app / "docs/framework/examples/gate-contract-v1/inputs"
        shutil.copytree(GATE_FIXTURES / "inputs", input_target, dirs_exist_ok=True)
        cls.source_revision = cls._git(cls.app, "rev-parse", "HEAD").stdout.strip()
        cls._git(cls.app, "add", "specification.md", "backlog.md", "docs/framework/examples/gate-contract-v1/inputs")
        cls._git(cls.app, "commit", "-m", "test: add synthetic fixture references")
        cls.source_revision = cls._git(cls.app, "rev-parse", "HEAD").stdout.strip()

        runs = cls.app / ".sdd/gate-runs"
        runs.mkdir(parents=True)
        for source in sorted((GATE_FIXTURES / "valid").glob("G-*.json")):
            record = json.loads(source.read_text(encoding="utf-8"))
            gate_id = record["gate_id"]
            record["contract_version"] = "1.2"
            record["record_id"] = f"FLAGLITE-GATE-RUN-{gate_id[2:]}-001"
            record["application_id"] = "FLAGLITE"
            record["repository"]["url_or_path"] = str(cls.app)
            record["source_snapshot"]["commit_sha"] = cls.source_revision
            for ref in record["source_snapshot"].get("files", []):
                ref["source_revision"] = cls.source_revision
            for ref in record["scope"].get("artifact_refs", []):
                ref["source_revision"] = cls.source_revision
            if gate_id == "G-REQ":
                record["gate_data"]["decision_ids"] = ["FLAGLITE-DECISION-001"]
            if gate_id == "G-RELEASE":
                record["gate_data"]["release_window"] = "synthetic-window"
            (runs / f"{record['record_id']}.json").write_text(
                json.dumps(record, indent=2) + "\n", encoding="utf-8"
            )
        cls._git(cls.app, "add", ".sdd/gate-runs")
        cls._git(cls.app, "commit", "-m", "test: add ten in-progress gate fixtures")
        cls.app_revision = cls._git(cls.app, "rev-parse", "HEAD").stdout.strip()
        cls.baseline = Path(cls.temporary.name) / "baseline"
        shutil.copytree(cls.app, cls.baseline, ignore=shutil.ignore_patterns(".git"))
        evidence_path = os.environ.get("FW020_PILOT_EVIDENCE_PATH")
        if evidence_path:
            evidence = {
                "framework_revision": cls.framework_revision,
                "app_source_revision": cls.source_revision,
                "app_gate_records_revision": cls.app_revision,
                "gate_run_count": 10,
                "gate_results": {gate: "in-progress" for gate in GATES},
                "app_remote": None,
                "product_source_present": False,
                "synthetic_only": True,
            }
            Path(evidence_path).write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-c", "user.name=Synthetic Pilot", "-c", "user.email=pilot@example.invalid", *args],
            cwd=cwd, check=True, text=True, capture_output=True,
        )

    def _case(self, mutate=None) -> tuple[Path, subprocess.CompletedProcess[str]]:
        temporary = tempfile.TemporaryDirectory(prefix="fw020-case-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / "app"
        shutil.copytree(self.baseline, root)
        if mutate is not None:
            mutate(root)
        result = subprocess.run(
            ["python3", "scripts/artifacts.py", "validate"], cwd=root,
            text=True, capture_output=True,
        )
        return root, result

    @staticmethod
    def _record(root: Path, gate_id: str) -> tuple[Path, dict[str, object]]:
        path = root / ".sdd/gate-runs" / f"FLAGLITE-GATE-RUN-{gate_id[2:]}-001.json"
        return path, json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _save(path: Path, record: dict[str, object]) -> None:
        scope_ref = json_sha256(record.get("scope"))
        for evidence in record.get("evidence", []):
            if isinstance(evidence, dict):
                evidence["scope_ref"] = scope_ref
                details = evidence.get("details")
                if evidence.get("type") == "command-execution" and isinstance(details, dict):
                    details["scope"] = scope_ref
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def _attach_synthetic_observation(self, record: dict[str, object], evidence_id: str = "PILOT-OBSERVATION") -> None:
        criterion_ids = [item["criterion_id"] for item in record["criteria_results"]]
        for criterion in record["criteria_results"]:
            criterion["evidence_ids"] = [evidence_id]
        record["evidence"] = [{
            "evidence_id": evidence_id, "type": "manual-observation", "criterion_ids": criterion_ids,
            "observed_at": "2026-10-21T12:00:00Z", "observed_by": "synthetic pilot",
            "source_revision": self.source_revision, "scope_ref": "synthetic fixture scope",
            "locator": "synthetic-only://pilot-observation", "record_sha256": "sha256:" + "d" * 64,
            "limitations": ["synthetic structural fixture; not product evidence"],
            "details": {"observer": "synthetic pilot", "procedure": "schema and relationship exercise",
                        "observed_at": "2026-10-21T12:00:00Z", "scope": "synthetic fixture",
                        "result": "not product evidence", "limitations": ["synthetic only"]},
        }]

    def test_app_is_separate_disposable_pinned_and_has_ten_truthful_in_progress_gates(self) -> None:
        lock = json.loads((self.baseline / ".sdd/framework.lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["framework_revision"], self.framework_revision)
        self.assertRegex(self.app_revision, r"^[a-f0-9]{40}$")
        self.assertTrue((self.app / ".git").is_dir())
        self.assertEqual(self._git(self.app, "remote", "-v").stdout, "")
        self.assertFalse(any((self.app / folder).exists() for folder in ("src", "services", "apps")))
        runs = list((self.baseline / ".sdd/gate-runs").glob("*.json"))
        self.assertEqual(len(runs), 10)
        self.assertEqual({json.loads(path.read_text())["gate_result"] for path in runs}, {"in-progress"})
        _, result = self._case()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Validated", result.stdout)

    def test_each_gate_rejects_free_text_pass_without_criterion_evidence(self) -> None:
        for gate_id in GATES:
            def mutate(root: Path, gate_id=gate_id) -> None:
                path, record = self._record(root, gate_id)
                record["gate_result"] = "passed"
                for criterion in record["criteria_results"]:
                    criterion["outcome"] = "pass"
                self._save(path, record)

            with self.subTest(gate=gate_id):
                _, result = self._case(mutate)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                self.assertIn(f"$.criteria_results[0].evidence_ids: array has fewer than 1 items", output)
                self.assertIn(f"[{gate_id}]", output)

    def test_all_ten_invalid_gate_fixtures_fail_in_the_separate_app(self) -> None:
        invalid_dir = GATE_FIXTURES / "invalid"
        for source in sorted(invalid_dir.glob("G-*.json")):
            def mutate(root: Path, source=source) -> None:
                runs = root / ".sdd/gate-runs"
                record = json.loads(source.read_text(encoding="utf-8"))
                gate_id = record["gate_id"]
                record["contract_version"] = "1.2"
                record["gate_result"] = "in-progress"
                record["gate_data"].pop(INVALID_REQUIRED_GATE_DATA[gate_id], None)
                record["record_id"] = f"FLAGLITE-GATE-RUN-NEG-{gate_id[2:]}-001"
                record["application_id"] = "FLAGLITE"
                record["repository"]["url_or_path"] = str(root)
                record["source_snapshot"]["commit_sha"] = self.source_revision
                for ref in record["source_snapshot"].get("files", []):
                    ref["source_revision"] = self.source_revision
                for ref in record.get("scope", {}).get("artifact_refs", []):
                    ref["source_revision"] = self.source_revision
                scope_hash = json_sha256(record.get("scope"))
                for evidence in record.get("evidence", []):
                    if isinstance(evidence, dict):
                        evidence["scope_ref"] = scope_hash
                        details = evidence.get("details")
                        if evidence.get("type") == "command-execution" and isinstance(details, dict):
                            details["scope"] = scope_hash
                if gate_id == "G-REQ":
                    record["gate_data"]["decision_ids"] = ["FLAGLITE-DECISION-001"]
                if gate_id == "G-RELEASE":
                    record["gate_data"]["release_window"] = "synthetic-window"
                (runs / f"{record['record_id']}.json").write_text(json.dumps(record, indent=2) + "\n")

            with self.subTest(fixture=source.name):
                _, result = self._case(mutate)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                fixture = json.loads(source.read_text(encoding="utf-8"))
                gate_id = fixture["gate_id"]
                self.assertIn(f"[{gate_id}]", output)
                self.assertIn(
                    f"missing required property '{INVALID_REQUIRED_GATE_DATA[gate_id]}'",
                    output,
                )

    def test_stale_digest_revision_identity_waiver_and_cross_app_substitution_fail(self) -> None:
        cases = (
            ("digest", lambda d: d["scope"]["artifact_refs"][0].update(sha256="sha256:" + "0" * 64), "artifact digest is stale"),
            ("revision", lambda d: d["source_snapshot"].update(commit_sha="a" * 40), "source_snapshot file 'docs/framework/examples/gate-contract-v1/inputs/FIXTURE-INPUT-001.md' revision does not match commit_sha"),
            ("identity", lambda d: d.update(application_id="OTHER-APP"), "application_id does not match the app mission artifact identity 'FLAGLITE'"),
            ("waiver", lambda d: d.update(gate_result="passed-with-accepted-risk"), "$.accepted_risk: expected JSON type object"),
        )
        for label, change, expected in cases:
            def mutate(root: Path, change=change) -> None:
                path, record = self._record(root, "G-INTENT")
                change(record)
                self._save(path, record)
            with self.subTest(case=label):
                _, result = self._case(mutate)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                self.assertIn(expected, output)

    def test_invalid_accepted_risk_and_not_applicable_results_fail_closed(self) -> None:
        def empty_waiver(root: Path) -> None:
            path, record = self._record(root, "G-INTENT")
            record["gate_result"] = "passed-with-accepted-risk"
            record["accepted_risk"] = None
            self._save(path, record)

        _, result = self._case(empty_waiver)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("$.accepted_risk: expected JSON type object", output)

        def unsupported_not_applicable(root: Path) -> None:
            path, record = self._record(root, "G-CX")
            record["gate_result"] = "not-applicable"
            record["scope"]["exclusions"] = [{
                "item": "synthetic unavailable CX surface",
                "reason": "fixture only",
                "authority": "synthetic owner",
                "downstream_effect": "no product readiness claim",
            }]
            decision_id = "PILOT-UNAUTHORIZED-NA"
            record["authority"]["owner_decisions"] = [{
                "decision_id": decision_id,
                "decision_maker": "not-the-accountable-owner",
                "role": "synthetic fixture actor",
                "decided_at": "2026-10-21T12:00:00Z",
                "choice": "mark CX not applicable",
                "affected_ids": ["FLAGLITE-GATE-RUN-CX-001"],
                "rationale": "negative test",
                "revisit_condition": "fixture only",
            }]
            for criterion in record["criteria_results"]:
                criterion["outcome"] = "not-applicable"
                criterion["owner_decision_ids"] = [decision_id]
            self._save(path, record)

        _, result = self._case(unsupported_not_applicable)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("not-applicable decision 'PILOT-UNAUTHORIZED-NA' was not made by the accountable owner", output)

    def test_unknown_feasibility_cannot_unblock_and_coverage_cannot_substitute_platform(self) -> None:
        def unblocked(root: Path) -> None:
            path, record = self._record(root, "G-FEAS")
            record["gate_data"]["probes"][0]["task_dependencies"][0]["state"] = "unblocked"
            record["dependency_effects"][0]["state"] = "unblocked"
            self._save(path, record)
        _, result = self._case(unblocked)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("unknown feasibility probe 'FIXTURE-PROBE-001' cannot leave task 'FIXTURE-TASK-001' unconditionally unblocked", output)

        def substituted(root: Path) -> None:
            path, record = self._record(root, "G-COVERAGE")
            record["scope"]["platforms"] = ["ios"]
            record["gate_data"]["platform_applicability"][0]["platform"] = "android"
            self._save(path, record)
        _, result = self._case(substituted)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("G-COVERAGE platform_applicability platform 'android' is outside scope.platforms", output)

        def out_of_scope_journey(root: Path) -> None:
            path, record = self._record(root, "G-COVERAGE")
            record["gate_data"]["journeys"][0]["requirement_ids"] = ["OTHER-REQ-999"]
            self._save(path, record)
        _, result = self._case(out_of_scope_journey)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("journey 'FIXTURE-JOURNEY-001' references out-of-scope requirement 'OTHER-REQ-999'", output)

    def test_feasibility_dependency_conflicts_and_out_of_scope_tasks_fail_with_targeted_diagnostics(self) -> None:
        def conflicting_effect(root: Path) -> None:
            path, record = self._record(root, "G-FEAS")
            record["dependency_effects"][0]["state"] = "conditional"
            record["dependency_effects"][0]["condition"] = "owner approval"
            record["dependency_effects"][0]["safe_work_boundary"] = "no product work"
            record["dependency_effects"][0]["state_change_trigger"] = "new evidence"
            self._save(path, record)

        _, result = self._case(conflicting_effect)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("feasibility task 'FIXTURE-TASK-001' dependency_effect state does not match its probe", output)

        def out_of_scope_task(root: Path) -> None:
            path, record = self._record(root, "G-FEAS")
            record["gate_data"]["probes"][0]["task_dependencies"][0]["task_id"] = "OTHER-TASK-999"
            self._save(path, record)

        _, result = self._case(out_of_scope_task)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("feasibility dependency task 'OTHER-TASK-999' is not declared in scope.task_ids", output)

    def _synthetic_intent_pass(self, root: Path) -> tuple[dict[str, object], dict[str, object]]:
        base_path, base = self._record(root, "G-INTENT")
        record = json.loads(json.dumps(base))
        record.update({
            "record_id": "FLAGLITE-GATE-RUN-INTENT-002", "record_version": 2,
            "supersedes_run_id": base["record_id"], "created_at": "2026-10-21T13:00:00Z",
            "gate_result": "passed",
        })
        digest = "sha256:" + hashlib.sha256((root / "mission.md").read_bytes()).hexdigest()
        mission_ref = {
            "artifact_id": "FLAGLITE-MISSION-001", "version": "0.1", "path": "mission.md",
            "sha256": digest, "source_revision": self.source_revision,
        }
        record["scope"]["artifact_refs"].append(mission_ref)
        record["scope"]["exclusions"] = [{"item": SYNTHETIC_EXCLUSION, "reason": "synthetic-only pilot boundary",
            "authority": "fixture owner", "downstream_effect": "no product implementation or release"}]
        record["source_snapshot"]["files"].append(mission_ref)
        evidence_id = "EVIDENCE-MISSION-001"
        decision_id = "OWNER-INTENT-001"
        record["evidence"] = [{
            "evidence_id": evidence_id, "type": "artifact-reference",
            "criterion_ids": [item["criterion_id"] for item in record["criteria_results"]],
            "observed_at": "2026-10-21T12:30:00Z", "observed_by": "fixture-owner",
            "source_revision": self.source_revision, "scope_ref": "synthetic fixture",
            "locator": "mission.md", "record_sha256": digest,
            "limitations": ["synthetic only; not product evidence"],
            "details": {"artifact_id": "FLAGLITE-MISSION-001", "version": "0.1", "path": "mission.md", "sha256": digest},
        }]
        record["authority"]["owner_decisions"] = [{
            "decision_id": decision_id, "decision_maker": "fixture-owner", "role": "synthetic fixture owner",
            "decided_at": "2026-10-21T12:30:00Z",
            "choice": f"approve-intent: FLAGLITE-MISSION-001; digest={digest}",
            "affected_ids": ["FLAGLITE-MISSION-001"], "rationale": "synthetic pass-path test",
            "revisit_condition": "fixture only",
        }]
        for criterion in record["criteria_results"]:
            criterion.update({"outcome": "pass", "evidence_ids": [evidence_id], "owner_decision_ids": [decision_id]})
        return record, base

    @staticmethod
    def _refresh_mission_digest(root: Path, record: dict[str, object], exclusion: str) -> None:
        digest = "sha256:" + hashlib.sha256((root / "mission.md").read_bytes()).hexdigest()
        for section in (record["scope"]["artifact_refs"], record["source_snapshot"]["files"]):
            for ref in section:
                if ref.get("path") == "mission.md":
                    ref["sha256"] = digest
        for evidence in record["evidence"]:
            if evidence.get("type") == "artifact-reference" and evidence.get("details", {}).get("path") == "mission.md":
                evidence["record_sha256"] = digest
                evidence["details"]["sha256"] = digest
        for decision in record["authority"]["owner_decisions"]:
            decision["choice"] = f"approve-intent: FLAGLITE-MISSION-001; digest={digest}"
        record["scope"]["exclusions"] = [{"item": exclusion, "reason": "synthetic-only pilot boundary",
            "authority": "fixture owner", "downstream_effect": "no product implementation or release"}]

    def test_intent_synthetic_positive_pass_and_forged_manual_evidence_boundary(self) -> None:
        def positive(root: Path) -> None:
            record, _ = self._synthetic_intent_pass(root)
            self._save(root / ".sdd/gate-runs/FLAGLITE-GATE-RUN-INTENT-002.json", record)
        _, result = self._case(positive)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        def forged(root: Path) -> None:
            record, _ = self._synthetic_intent_pass(root)
            record["scope"]["artifact_refs"] = [ref for ref in record["scope"]["artifact_refs"] if ref["path"] != "mission.md"]
            record["source_snapshot"]["files"] = [ref for ref in record["source_snapshot"]["files"] if ref["path"] != "mission.md"]
            record["authority"]["owner_decisions"] = []
            evidence_id = "EVIDENCE-FORGED-001"
            record["evidence"] = [{
                "evidence_id": evidence_id, "type": "manual-observation",
                "criterion_ids": [item["criterion_id"] for item in record["criteria_results"]],
                "observed_at": "2026-10-21T12:30:00Z", "observed_by": "agent",
                "source_revision": self.source_revision, "scope_ref": "synthetic scope",
                "locator": "synthetic-only://missing-evidence", "record_sha256": "sha256:" + "a" * 64,
                "limitations": ["no mission evidence exists"],
                "details": {"observer": "agent", "procedure": "claim pass", "observed_at": "2026-10-21T12:30:00Z",
                            "scope": "synthetic", "result": "claimed pass", "limitations": ["no observation"]},
            }]
            for criterion in record["criteria_results"]:
                criterion.update({"evidence_ids": [evidence_id], "owner_decision_ids": []})
            (root / ".sdd/gate-runs/FLAGLITE-GATE-RUN-INTENT-002.json").write_text(json.dumps(record, indent=2) + "\n")
        _, result = self._case(forged)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("requires artifact-reference evidence for the current mission.md", output)
        self.assertIn("requires accountable-owner approval bound to mission ID and exact mission digest", output)

    def test_intent_pass_rejects_missing_or_unlinked_negative_boundaries(self) -> None:
        def missing_from_mission(root: Path) -> None:
            record, _ = self._synthetic_intent_pass(root)
            mission_path = root / "mission.md"
            mission_path.write_text(mission_path.read_text(encoding="utf-8").replace(SYNTHETIC_EXCLUSION, ""), encoding="utf-8")
            self._refresh_mission_digest(root, record, SYNTHETIC_EXCLUSION)
            self._save(root / ".sdd/gate-runs/FLAGLITE-GATE-RUN-INTENT-002.json", record)
        _, result = self._case(missing_from_mission)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("passed G-INTENT exclusion must be stated in the current mission.md", output)

        def no_exclusions(root: Path) -> None:
            record, _ = self._synthetic_intent_pass(root)
            record["scope"]["exclusions"] = []
            self._save(root / ".sdd/gate-runs/FLAGLITE-GATE-RUN-INTENT-002.json", record)
        _, result = self._case(no_exclusions)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("passed G-INTENT requires explicit negative-space scope.exclusions", output)

    def test_setup_pass_uses_observed_local_validation_and_latest_intent_pass(self) -> None:
        def setup_pass(root: Path) -> None:
            intent, _ = self._synthetic_intent_pass(root)
            intent_path = root / ".sdd/gate-runs/FLAGLITE-GATE-RUN-INTENT-002.json"
            self._save(intent_path, intent)

            output_dir = root / "docs/evidence/fw020-setup"
            output_dir.mkdir(parents=True)
            execution = subprocess.run(
                ["python3", "scripts/artifacts.py", "validate"], cwd=root,
                text=True, capture_output=True,
            )
            stdout_path = output_dir / "stdout.txt"
            stderr_path = output_dir / "stderr.txt"
            stdout_path.write_text(execution.stdout, encoding="utf-8")
            stderr_path.write_text(execution.stderr, encoding="utf-8")
            self.assertEqual(execution.returncode, 0, execution.stdout + execution.stderr)

            setup_path, setup = self._record(root, "G-SETUP")
            setup.update({"record_id": "FLAGLITE-GATE-RUN-SETUP-002", "record_version": 2,
                          "supersedes_run_id": setup["record_id"], "created_at": "2026-10-21T13:30:00Z",
                          "gate_result": "passed"})
            intent_bytes = intent_path.read_bytes()
            setup["scope"]["artifact_refs"].append({
                "artifact_id": intent["record_id"], "version": "2",
                "path": intent_path.relative_to(root).as_posix(),
                "sha256": "sha256:" + hashlib.sha256(intent_bytes).hexdigest(),
                "source_revision": self.source_revision,
            })
            evidence_id = "FLAGLITE-SETUP-OBSERVED-VALIDATION"
            criterion_ids = [item["criterion_id"] for item in setup["criteria_results"]]
            for criterion in setup["criteria_results"]:
                criterion.update({"outcome": "pass", "evidence_ids": [evidence_id],
                                  "rationale": "Synthetic pilot: observed app-local validator execution."})
            setup["gate_data"]["cold_start_evidence_ids"] = [evidence_id]
            setup["evidence"] = [{
                "evidence_id": evidence_id, "type": "command-execution", "criterion_ids": criterion_ids,
                "observed_at": "2026-10-21T13:20:00Z", "observed_by": "synthetic pilot runner",
                "source_revision": self.source_revision, "scope_ref": "initialized synthetic app baseline",
                "locator": stdout_path.relative_to(root).as_posix(),
                "record_sha256": "sha256:" + hashlib.sha256(stdout_path.read_bytes()).hexdigest(),
                "limitations": ["synthetic app setup only; no product readiness claim"],
                "details": {"command": "python3 scripts/artifacts.py validate", "exit_code": 0,
                            "stdout_ref": stdout_path.relative_to(root).as_posix(),
                            "stderr_ref": stderr_path.relative_to(root).as_posix(),
                            "runtime_versions": ["Python 3.13"],
                            "started_at": "2026-10-21T13:19:00Z", "completed_at": "2026-10-21T13:20:00Z",
                            "scope": "initialized synthetic app baseline"},
            }]
            self._save(root / ".sdd/gate-runs/FLAGLITE-GATE-RUN-SETUP-002.json", setup)

        _, result = self._case(setup_pass)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Validated", result.stdout)

        failed_root, _ = self._case(setup_pass)
        setup_path = failed_root / ".sdd/gate-runs/FLAGLITE-GATE-RUN-SETUP-002.json"
        setup = json.loads(setup_path.read_text(encoding="utf-8"))
        setup["evidence"][0]["details"]["exit_code"] = 1
        self._save(setup_path, setup)
        failed = subprocess.run(
            ["python3", "scripts/artifacts.py", "validate"], cwd=failed_root,
            text=True, capture_output=True,
        )
        output = failed.stdout + failed.stderr
        self.assertNotEqual(failed.returncode, 0, output)
        self.assertIn(
            "non-zero command evidence 'FLAGLITE-SETUP-OBSERVED-VALIDATION' cannot support a passing criterion",
            output,
        )

        missing_output_root, _ = self._case(setup_pass)
        output_path = missing_output_root / ".sdd/gate-runs/FLAGLITE-GATE-RUN-SETUP-002.json"
        setup = json.loads(output_path.read_text(encoding="utf-8"))
        setup["evidence"][0]["details"]["stdout_ref"] = None
        setup["evidence"][0]["details"]["stderr_ref"] = None
        self._save(output_path, setup)
        missing_output = subprocess.run(
            ["python3", "scripts/artifacts.py", "validate"], cwd=missing_output_root,
            text=True, capture_output=True,
        )
        output = missing_output.stdout + missing_output.stderr
        self.assertNotEqual(missing_output.returncode, 0, output)
        self.assertIn(
            "command evidence 'FLAGLITE-SETUP-OBSERVED-VALIDATION' requires durable stdout_ref or stderr_ref evidence",
            output,
        )

        missing_file_root, _ = self._case(setup_pass)
        setup_pass_path = missing_file_root / ".sdd/gate-runs/FLAGLITE-GATE-RUN-SETUP-002.json"
        evidence = json.loads(setup_pass_path.read_text(encoding="utf-8"))["evidence"][0]
        (missing_file_root / evidence["details"]["stdout_ref"]).unlink()
        missing_file = subprocess.run(
            ["python3", "scripts/artifacts.py", "validate"], cwd=missing_file_root,
            text=True, capture_output=True,
        )
        output = missing_file.stdout + missing_file.stderr
        self.assertNotEqual(missing_file.returncode, 0, output)
        self.assertIn(
            "command evidence 'FLAGLITE-SETUP-OBSERVED-VALIDATION' output reference is invalid",
            output,
        )

        stale_upstream_root, _ = self._case(setup_pass)
        upstream_path = stale_upstream_root / ".sdd/gate-runs/FLAGLITE-GATE-RUN-INTENT-002.json"
        upstream_path.write_text(upstream_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        stale_upstream = subprocess.run(
            ["python3", "scripts/artifacts.py", "validate"], cwd=stale_upstream_root,
            text=True, capture_output=True,
        )
        output = stale_upstream.stdout + stale_upstream.stderr
        self.assertNotEqual(stale_upstream.returncode, 0, output)
        self.assertIn("artifact digest is stale", output)

        altered_output_root, _ = self._case(setup_pass)
        altered_setup_path = altered_output_root / ".sdd/gate-runs/FLAGLITE-GATE-RUN-SETUP-002.json"
        altered_setup = json.loads(altered_setup_path.read_text(encoding="utf-8"))
        stdout_file = altered_output_root / altered_setup["evidence"][0]["details"]["stdout_ref"]
        stdout_file.write_text("replaced output; the original command result is no longer reproducible\n", encoding="utf-8")
        altered = subprocess.run(
            ["python3", "scripts/artifacts.py", "validate"], cwd=altered_output_root,
            text=True, capture_output=True,
        )
        output = altered.stdout + altered.stderr
        self.assertNotEqual(altered.returncode, 0, output)
        self.assertIn(
            "command evidence 'FLAGLITE-SETUP-OBSERVED-VALIDATION' record_sha256 does not match its durable stdout/stderr output",
            output,
        )

    def test_feasibility_supported_scope_reduced_blocked_conditional_and_owner_risk_routes(self) -> None:
        changes = {}
        def supported(d: dict[str, object]) -> None:
            probe = d["gate_data"]["probes"][0]
            probe.update({"classification": "supported", "observed_at": "2026-10-21T12:00:00Z", "confidence": "medium",
                          "status": "evidence-recorded", "source_or_plan": "synthetic evidence fixture only",
                          "limitations": ["synthetic route-shape only; no product feasibility claim"]})
            probe["task_dependencies"][0].update({"state": "unblocked", "condition": "", "safe_work_boundary": ""})
            d["dependency_effects"][0].update(probe["task_dependencies"][0])
        changes["supported route (synthetic only)"] = supported
        def scope_reduced(d: dict[str, object]) -> None:
            d["scope"]["requirement_ids"] = []
            d["gate_data"]["probes"][0]["requirement_ids"] = []
        changes["scope-reduced requirement"] = scope_reduced
        changes["unknown remains blocked"] = lambda d: None
        def conditional(d: dict[str, object]) -> None:
            probe = d["gate_data"]["probes"][0]
            probe["classification"] = "constrained"
            dependency = {"task_id": "FIXTURE-TASK-001", "state": "conditional",
                          "condition": "owner accepts documented limit", "safe_work_boundary": "no provider integration or rollout",
                          "state_change_trigger": "new provider evidence is recorded"}
            probe["task_dependencies"] = [dependency]
            d["dependency_effects"] = [dict(dependency)]
        changes["conditional safe work"] = conditional
        def risk(d: dict[str, object]) -> None:
            d["authority"]["owner_decisions"] = [{
                "decision_id": "FIXTURE-RISK-001", "decision_maker": "fixture-owner", "role": "synthetic owner",
                "decided_at": "2026-10-21T12:00:00Z", "choice": "accept residual uncertainty; dependent task stays blocked",
                "affected_ids": ["FIXTURE-TASK-001"], "rationale": "fixture only", "revisit_condition": "new evidence",
            }]
        changes["owner risk leaves unknown blocked"] = risk
        for name, change in changes.items():
            def mutate(root: Path, change=change) -> None:
                path, record = self._record(root, "G-FEAS")
                change(record["gate_data"].update({}) if False else record)
                if name == "supported route (synthetic only)":
                    self._attach_synthetic_observation(record, "FEAS-SYNTHETIC-SUPPORT-EVIDENCE")
                self._save(path, record)
            with self.subTest(route=name):
                root, result = self._case(mutate)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                _, record = self._record(root, "G-FEAS")
                self.assertEqual(record["gate_result"], "in-progress")
                if name == "supported route (synthetic only)":
                    self.assertTrue(record["evidence"])
                    self.assertTrue(all("FEAS-SYNTHETIC-SUPPORT-EVIDENCE" in item["evidence_ids"] for item in record["criteria_results"]))
                if name == "owner risk leaves unknown blocked":
                    self.assertEqual(record["gate_data"]["probes"][0]["classification"], "unknown")
                    self.assertEqual(record["gate_data"]["probes"][0]["task_dependencies"][0]["state"], "blocked")

    def test_product_interaction_without_capture_is_explicitly_unverified_in_progress(self) -> None:
        def mutate(root: Path) -> None:
            path, record = self._record(root, "G-CX")
            evidence_id = "EVIDENCE-UNVERIFIED-CX-001"
            record["gate_data"]["interaction_evidence_ids"] = [evidence_id]
            record["gate_data"]["limitations"] = ["No rendered or runtime capture exists; synthetic manual observation only."]
            for criterion in record["criteria_results"]:
                criterion["evidence_ids"] = [evidence_id]
            record["evidence"] = [{
                "evidence_id": evidence_id, "type": "manual-observation",
                "criterion_ids": [item["criterion_id"] for item in record["criteria_results"]],
                "observed_at": "2026-10-21T12:00:00Z", "observed_by": "synthetic fixture",
                "source_revision": self.source_revision, "scope_ref": "synthetic interaction",
                "locator": "synthetic-only://no-rendered-capture", "record_sha256": "sha256:" + "b" * 64,
                "limitations": ["not visual/runtime evidence"],
                "details": {"observer": "synthetic fixture", "procedure": "schema path exercise",
                            "observed_at": "2026-10-21T12:00:00Z", "scope": "synthetic only",
                            "result": "unverified", "limitations": ["no rendered or runtime capture"]},
            }]
            self._save(path, record)
        root, result = self._case(mutate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        _, record = self._record(root, "G-CX")
        self.assertEqual(record["gate_result"], "in-progress")
        self.assertTrue(any("no rendered" in item.lower() for item in record["gate_data"]["limitations"]))

        def fabricate_passing_critique(root: Path) -> None:
            mutate(root)
            path, record = self._record(root, "G-CX")
            record["gate_result"] = "passed"
            for criterion in record["criteria_results"]:
                criterion["outcome"] = "pass"
            self._save(path, record)

        _, claimed_pass = self._case(fabricate_passing_critique)
        output = claimed_pass.stdout + claimed_pass.stderr
        self.assertNotEqual(claimed_pass.returncode, 0, output)
        self.assertIn(
            "passed G-CX cannot rely on explicitly unverified interaction evidence",
            output,
        )

    def test_gcx_rejects_fabricated_non_image_capture_content(self) -> None:
        def mutate(root: Path) -> None:
            path, record = self._record(root, "G-CX")
            capture_path = root / "docs/evidence/fw020/fabricated-capture.txt"
            capture_path.parent.mkdir(parents=True, exist_ok=True)
            capture_bytes = b"This is fabricated screenshot text, not an image."
            capture_path.write_bytes(capture_bytes)
            evidence_id = "FABRICATED-CAPTURE-001"
            criteria = record["criteria_results"]
            for item in criteria:
                item.update({"outcome": "pass", "evidence_ids": [evidence_id]})
            record["gate_result"] = "passed"
            record["gate_data"]["interaction_evidence_ids"] = [evidence_id]
            record["evidence"] = [{
                "evidence_id": evidence_id,
                "type": "interaction-capture",
                "criterion_ids": [item["criterion_id"] for item in criteria],
                "observed_at": "2026-10-21T15:00:00Z",
                "observed_by": "synthetic fixture",
                "source_revision": self.source_revision,
                "scope_ref": "synthetic capture scope",
                "locator": capture_path.relative_to(root).as_posix(),
                "record_sha256": "sha256:" + hashlib.sha256(capture_bytes).hexdigest(),
                "limitations": ["synthetic adversarial input; not a rendered product capture"],
                "details": {
                    "target_ref": "synthetic-only://unavailable-product-screen",
                    "capture_method": "fabricated text file mislabeled as a screenshot",
                    "tool_version": "synthetic fixture",
                    "viewport_or_device": "synthetic fixture",
                    "runtime": "unavailable",
                    "captured_at": "2026-10-21T15:00:00Z",
                    "limitations": ["fabricated non-image content"],
                },
            }]
            self._save(path, record)

        _, result = self._case(mutate)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn(
            "interaction capture evidence 'FABRICATED-CAPTURE-001' must reference a PNG, JPEG, GIF, or WebP image",
            output,
        )

    def test_untestable_requirement_finding_blocks_greq_pass(self) -> None:
        def mutate(root: Path) -> None:
            path, record = self._record(root, "G-REQ")
            record["gate_result"] = "passed"
            finding_id = "GREQ-UNTESTABLE-001"
            evidence_id = "GREQ-REVIEW-UNTESTABLE"
            criteria = record["criteria_results"]
            for criterion in criteria:
                criterion.update({"outcome": "pass", "evidence_ids": [evidence_id]})
            record["gate_data"]["review_evidence_ids"] = [evidence_id]
            record["authority"]["reviewers"] = [{
                "identity": "synthetic-independent-reviewer",
                "role": "fixture reviewer",
                "mode": "independent",
                "result": "pass",
                "author_overlap": "none",
                "context_disclosure": "reviewed the frozen synthetic specification and backlog fixture",
                "limitations": ["synthetic reviewer identity; no product review claim"],
            }]
            record["evidence"] = [{
                "evidence_id": evidence_id,
                "type": "review-finding",
                "criterion_ids": [item["criterion_id"] for item in criteria],
                "observed_at": "2026-10-21T14:00:00Z",
                "observed_by": "synthetic-independent-reviewer",
                "source_revision": self.source_revision,
                "scope_ref": "synthetic requirement review",
                "locator": "synthetic-only://greq-untestable-review",
                "record_sha256": "sha256:" + "e" * 64,
                "limitations": ["fixture only; does not authenticate reviewer identity"],
                "details": {
                    "reviewer": "synthetic-independent-reviewer",
                    "mode": "independent",
                    "author_overlap": "none",
                    "context_disclosure": "reviewed the frozen synthetic specification and backlog fixture",
                    "finding_id": finding_id,
                    "severity": "major",
                    "location": "specification.md: FIXTURE-REQ-001",
                    "disposition": "open",
                },
            }]
            record["findings"] = [{
                "finding_id": finding_id,
                "severity": "major",
                "blocking": True,
                "location": "specification.md: FIXTURE-REQ-001",
                "impact": "The requirement has no observable acceptance outcome and cannot be verified.",
                "disposition": "open",
                "owner_decision_required": False,
                "evidence_ids": [evidence_id],
            }]
            self._save(path, record)

        _, result = self._case(mutate)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn(
            "passed gate retains unresolved blocking finding(s): GREQ-UNTESTABLE-001",
            output,
        )

    def test_gate_specific_evidence_bypasses_are_rejected(self) -> None:
        cases = (
            ("G-SETUP", lambda d: d["gate_data"].update({"cold_start_evidence_ids": ["MISSING-COLD-START"]}), "gate_data.cold_start_evidence_ids references unknown evidence ID"),
            ("G-REQ", lambda d: d["gate_data"].update({"review_evidence_ids": ["MISSING-REVIEW-EVIDENCE"]}), "gate_data.review_evidence_ids references unknown evidence ID"),
            ("G-OPERATE", lambda d: d["gate_data"].update({"runbook_evidence_ids": ["MISSING-RUNBOOK"]}), "gate_data.runbook_evidence_ids references unknown evidence ID"),
        )
        for gate_id, change, expected in cases:
            def mutate(root: Path, gate_id=gate_id, change=change) -> None:
                path, record = self._record(root, gate_id)
                self._attach_synthetic_observation(record)
                change(record)
                self._save(path, record)

            with self.subTest(gate=gate_id):
                _, result = self._case(mutate)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                self.assertIn(expected, output)

    def test_happy_path_only_architecture_prose_and_silent_operations_cannot_pass(self) -> None:
        cases = (
            ("G-COVERAGE", lambda d: [row.update(applicable=False) for row in d["gate_data"]["failure_mode_applicability"]],
             "passed G-COVERAGE requires at least one applicable failure-mode row"),
            ("G-ARCH", lambda d: d["gate_data"].update({"verification_contracts": []}),
             "passed G-ARCH requires at least one verified contract with linked evidence"),
            ("G-OPERATE", lambda d: d["gate_data"].update({"telemetry_gaps": [], "runbook_evidence_ids": ["PILOT-OBSERVATION"]}),
             "passed G-OPERATE requires an explicit telemetry_gaps declaration"),
            ("G-OPERATE", lambda d: d["gate_data"].update({"degradation_limits": []}),
             "$.gate_data.degradation_limits: array has fewer than 1 items"),
            ("G-OPERATE", lambda d: d["gate_data"].update({"degradation_limits": [
                {"condition": "state growth", "threshold": "", "response": "stop"}
            ]}),
             "$.gate_data.degradation_limits[0].threshold: string is shorter than 1 characters"),
        )
        for gate_id, change, expected in cases:
            def mutate(root: Path, gate_id=gate_id, change=change) -> None:
                path, record = self._record(root, gate_id)
                self._attach_synthetic_observation(record)
                record["gate_result"] = "passed"
                for item in record["criteria_results"]:
                    item["outcome"] = "pass"
                change(record)
                self._save(path, record)

            with self.subTest(gate=gate_id):
                _, result = self._case(mutate)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                self.assertIn(expected, output)

        def architecture_text_observation(root: Path) -> None:
            path, record = self._record(root, "G-ARCH")
            self._attach_synthetic_observation(record)
            record["gate_result"] = "passed"
            for item in record["criteria_results"]:
                item["outcome"] = "pass"
            record["gate_data"]["verification_contracts"] = [{
                "contract": "Tenant data is isolated in memory.",
                "method": "Reviewer states the contract is satisfied.",
                "evidence_id": "PILOT-OBSERVATION",
            }]
            self._save(path, record)

        _, result = self._case(architecture_text_observation)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("narrative observations cannot verify a data/security contract", output)

    def test_release_mismatched_artifact_hash_and_authorization_cannot_pass(self) -> None:
        def claimed_release(root: Path, mismatch: str) -> None:
            path, record = self._record(root, "G-RELEASE")
            self._attach_synthetic_observation(record)
            record["gate_result"] = "passed"
            for item in record["criteria_results"]:
                item["outcome"] = "pass"
            digest_a = "sha256:" + "a" * 64
            digest_b = "sha256:" + "b" * 64
            record["gate_data"].update({"tested_commit_sha": self.source_revision,
                "artifact_sha256": digest_a, "required_check_evidence_ids": ["PILOT-RELEASE-CI"],
                "security_accessibility_platform_evidence_ids": ["PILOT-RELEASE-CI"],
                "owner_authorization_id": "PILOT-OWNER-AUTH", "support_owner": "synthetic owner"})
            record["evidence"].append({
                "evidence_id": "PILOT-RELEASE-CI", "type": "ci-run",
                "criterion_ids": [item["criterion_id"] for item in record["criteria_results"]],
                "observed_at": "2026-10-21T13:30:00Z", "observed_by": "synthetic CI",
                "source_revision": self.source_revision, "scope_ref": "synthetic release",
                "locator": "synthetic-run", "record_sha256": "sha256:" + "e" * 64,
                "limitations": ["synthetic only"],
                "details": {"provider": "synthetic", "run_id_or_url": "synthetic-run",
                    "commit_sha": self.source_revision, "workflow_job": "verify", "conclusion": "success", "scope": "synthetic"},
            })
            record["change_control"].update({"commit_sha": self.source_revision,
                "branch_ref": "refs/heads/synthetic-release", "remote": "synthetic://no-remote",
                "push_result": "pushed", "release_artifact_sha256": digest_b,
                "authorization_ref": "PILOT-OWNER-AUTH" if mismatch == "artifact" else "OTHER-AUTH",
                "ci_runs": [{"provider": "synthetic", "run_id_or_url": "synthetic-run",
                    "commit_sha": self.source_revision, "check": "verify", "status": "passed", "scope": "synthetic"}]})
            self._save(path, record)

        for mismatch, expected in (
            ("artifact", "G-RELEASE artifact digest must match change_control.release_artifact_sha256"),
            ("authorization", "G-RELEASE publication authorization_ref must match gate_data.owner_authorization_id"),
        ):
            def mutate(root: Path, mismatch=mismatch) -> None:
                claimed_release(root, mismatch)
            with self.subTest(mismatch=mismatch):
                _, result = self._case(mutate)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                self.assertIn(expected, output)

    def test_textual_independent_review_claim_and_failed_push_do_not_pass(self) -> None:
        def self_review(root: Path) -> None:
            path, record = self._record(root, "G-REQ")
            record["gate_result"] = "passed"
            evidence_id = "SELF-REVIEW"
            criterion_ids = [item["criterion_id"] for item in record["criteria_results"]]
            for criterion in record["criteria_results"]:
                criterion.update({"outcome": "pass", "evidence_ids": [evidence_id]})
            record["gate_data"]["review_evidence_ids"] = ["SELF-REVIEW"]
            record["authority"]["reviewers"] = [{"identity": "same-agent", "role": "agent author", "mode": "independent",
                "result": "pass", "author_overlap": "same-agent", "context_disclosure": "same author reviewed own work", "limitations": ["synthetic"]}]
            record["evidence"] = [{"evidence_id": evidence_id, "type": "review-finding",
                "criterion_ids": criterion_ids,
                "observed_at": "2026-10-21T12:00:00Z", "observed_by": "same-agent", "source_revision": self.source_revision,
                "scope_ref": "synthetic", "locator": "self-review", "record_sha256": "sha256:" + "c" * 64,
                "limitations": ["synthetic only"], "details": {"reviewer": "same-agent", "mode": "independent",
                "author_overlap": "same-agent", "context_disclosure": "same author reviewed own work", "finding_id": "SELF-FINDING",
                "severity": "informational", "location": "synthetic fixture", "disposition": "not-applicable"}}]
            self._save(path, record)
        _, result = self._case(self_review)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("passed G-REQ requires an independent reviewer result, context disclosure, and author_overlap 'none'", output)

        def failed_push(root: Path) -> None:
            path, record = self._record(root, "G-IMPL")
            record["change_control"].update({"push_result": "failed", "remote": None, "branch_ref": None})
            self._save(path, record)
        root, result = self._case(failed_push)
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        _, record = self._record(root, "G-IMPL")
        self.assertEqual(record["change_control"]["push_result"], "failed")
        self.assertEqual(record["gate_result"], "in-progress")
        self.assertIsNone(record["change_control"]["remote"])
        self.assertIsNone(record["change_control"]["authorization_ref"])

        def missing_remote_claimed_pass(root: Path) -> None:
            path, record = self._record(root, "G-IMPL")
            record["gate_result"] = "passed"
            record["change_control"].update({"push_result": "not-applicable", "remote": None,
                                             "branch_ref": None, "authorization_ref": None})
            self._save(path, record)

        _, missing_remote = self._case(missing_remote_claimed_pass)
        output = missing_remote.stdout + missing_remote.stderr
        self.assertNotEqual(missing_remote.returncode, 0, output)
        self.assertIn("push_result must be 'pushed'; a missing or unavailable remote is a blocker", output)
        self.assertIn("published checkpoint requires non-empty change_control.remote", output)

    def test_skipped_unavailable_or_failed_required_check_cannot_support_impl_pass(self) -> None:
        for check_result in ("not-run", "skipped", "unavailable", "failed", "interrupted"):
            def mutate(root: Path, check_result=check_result) -> None:
                path, record = self._record(root, "G-IMPL")
                record["gate_result"] = "passed"
                record["gate_data"]["selected_task_id"] = "FIXTURE-TASK-001"
                record["gate_data"]["criterion_check_mappings"] = [
                    {"criterion_id": item["criterion_id"], "check_ids": ["PILOT-CHECK"], "manual_method": None}
                    for item in record["criteria_results"]
                ]
                record["gate_data"]["required_checks"] = [{
                    "check_id": "PILOT-CHECK", "command_or_procedure": "synthetic check",
                    "tool_runtime_version": "synthetic runtime", "source_revision": self.source_revision,
                    "scope": "synthetic fixture", "pass_condition": "success", "result": check_result,
                    "evidence_id": "MISSING-CHECK-EVIDENCE",
                }]
                record["gate_data"]["review_evidence_ids"] = ["MISSING-REVIEW"]
                for item in record["criteria_results"]:
                    item["outcome"] = "pass"
                    item["evidence_ids"] = ["MISSING-CHECK-EVIDENCE"]
                self._save(path, record)

            with self.subTest(check_result=check_result):
                _, result = self._case(mutate)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                self.assertIn("[G-IMPL]", output)
                if check_result in {"skipped", "unavailable", "interrupted"}:
                    expected = "$.gate_data.required_checks[0].result: value is not one of the allowed values"
                else:
                    expected = "$.gate_data.required_checks[0].result: value does not equal required constant 'passed'"
                self.assertIn(expected, output)

        def copied_terminal_output(root: Path) -> None:
            path, record = self._record(root, "G-IMPL")
            self._attach_synthetic_observation(record)
            record["gate_result"] = "passed"
            record["gate_data"]["selected_task_id"] = "FIXTURE-TASK-001"
            record["gate_data"]["review_evidence_ids"] = ["PILOT-OBSERVATION"]
            record["gate_data"]["criterion_check_mappings"] = [
                {"criterion_id": item["criterion_id"], "check_ids": ["PILOT-CHECK"], "manual_method": None}
                for item in record["criteria_results"]
            ]
            record["gate_data"]["required_checks"] = [{
                "check_id": "PILOT-CHECK", "command_or_procedure": "synthetic check",
                "tool_runtime_version": "synthetic runtime", "source_revision": self.source_revision,
                "scope": "synthetic fixture", "pass_condition": "success", "result": "passed",
                "evidence_id": "PILOT-OBSERVATION",
            }]
            record["gate_data"]["review_evidence_ids"] = ["PILOT-OBSERVATION"]
            for item in record["criteria_results"]:
                item.update({"outcome": "pass", "evidence_ids": ["PILOT-OBSERVATION"]})
            self._save(path, record)

        _, result = self._case(copied_terminal_output)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("evidence must be command-execution or ci-run", output)

    def test_structured_copied_terminal_output_cannot_support_lock_v4_gimpl_pass(self) -> None:
        def copied_but_well_shaped_command_evidence(root: Path) -> None:
            path, record = self._record(root, "G-IMPL")
            output_path = root / "docs/evidence/fw020-gimpl/copied-terminal-output.txt"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("Copied terminal text: all checks passed.\n", encoding="utf-8")
            output_ref = output_path.relative_to(root).as_posix()
            evidence_id = "PILOT-FORGED-COMMAND-OUTPUT"
            criterion_ids = [item["criterion_id"] for item in record["criteria_results"]]
            for item in record["criteria_results"]:
                item.update({"outcome": "pass", "evidence_ids": [evidence_id]})
            record["gate_result"] = "passed"
            record["gate_data"]["selected_task_id"] = "FIXTURE-TASK-001"
            record["gate_data"]["review_evidence_ids"] = [evidence_id]
            record["gate_data"]["criterion_check_mappings"] = [
                {"criterion_id": criterion_id, "check_ids": ["PILOT-COPIED-OUTPUT"], "manual_method": None}
                for criterion_id in criterion_ids
            ]
            record["gate_data"]["required_checks"] = [{
                "check_id": "PILOT-COPIED-OUTPUT", "command_or_procedure": "python3 -m unittest",
                "tool_runtime_version": "Python 3.13", "source_revision": self.source_revision,
                "scope": "synthetic copied-output fixture", "pass_condition": "exit_code == 0",
                "result": "passed", "evidence_id": evidence_id,
            }]
            record["evidence"] = [{
                "evidence_id": evidence_id, "type": "command-execution", "criterion_ids": criterion_ids,
                "observed_at": "2026-10-21T14:00:00Z", "observed_by": "synthetic fixture author",
                "source_revision": self.source_revision, "scope_ref": "synthetic copied-output fixture",
                "locator": output_ref,
                "record_sha256": "sha256:" + hashlib.sha256(output_path.read_bytes()).hexdigest(),
                "limitations": ["copied terminal text; no command was executed"],
                "details": {"command": "python3 -m unittest", "exit_code": 0,
                    "stdout_ref": output_ref, "stderr_ref": None, "runtime_versions": ["Python 3.13"],
                    "started_at": "2026-10-21T13:59:00Z", "completed_at": "2026-10-21T14:00:00Z",
                    "scope": "synthetic copied-output fixture"},
            }]
            self._save(path, record)

        _, result = self._case(copied_but_well_shaped_command_evidence)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("lock-v4 G-IMPL PASS requires an active trusted CI policy", output)


if __name__ == "__main__":
    unittest.main()
