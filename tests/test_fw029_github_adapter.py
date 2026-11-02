from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path
from typing import Any

from scripts.fw029_github_adapter import (
    ALLOWED_REF,
    EXPECTED_EVENT,
    EXPECTED_REPOSITORY_ID,
    REPOSITORY,
    SKIPPED_CALLER_JOB,
    VERIFY_WORKFLOW,
    AdapterError,
    build_check_records,
    build_receipt,
    load_required_checks,
    resolve_run,
)


ROOT = Path(__file__).resolve().parents[1]
FW029 = ROOT / "docs" / "framework" / "schemas" / "fw029"
MANIFEST = FW029 / "github-actions-required-checks.v1.json"
CASES = FW029 / "fixtures" / "semantic-cases.json"
SOURCE_SHA = "a" * 40
CONTRACT = b"---\nversion: 1.2\n---\nsynthetic contract bytes\n"
REPOSITORY_RECORD = {"full_name": REPOSITORY, "id": EXPECTED_REPOSITORY_ID}


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sample_run() -> dict[str, Any]:
    return {
        "id": 987654321,
        "run_attempt": 1,
        "check_suite_id": 123456789,
        "head_sha": SOURCE_SHA,
        "head_branch": ALLOWED_REF.removeprefix("refs/heads/"),
        "event": EXPECTED_EVENT,
        "path": VERIFY_WORKFLOW,
        "status": "completed",
        "conclusion": "success",
        "html_url": "https://github.com/naelmusleh/adversarial-sdd-boilerplate/actions/runs/987654321",
        "updated_at": "2026-10-25T15:30:00Z",
    }


def sample_jobs() -> tuple[dict[str, Any], dict[int, dict[str, Any]]]:
    required, _ = load_required_checks(MANIFEST.read_bytes())
    run = sample_run()
    jobs = []
    checks: dict[int, dict[str, Any]] = {}
    for index, item in enumerate(required, start=1001):
        jobs.append({
            "id": index,
            "name": item["name"],
            "run_id": run["id"],
            "run_attempt": run["run_attempt"],
            "head_sha": SOURCE_SHA,
            "status": "completed",
            "conclusion": "success",
        })
        checks[index] = {
            "id": index,
            "name": item["name"],
            "head_sha": SOURCE_SHA,
            "status": "completed",
            "conclusion": "success",
            "app": {"id": 15368, "slug": "github-actions"},
            "check_suite": {"id": run["check_suite_id"]},
        }
    jobs.append({
        "id": 9876,
        "name": SKIPPED_CALLER_JOB,
        "run_id": run["id"],
        "run_attempt": run["run_attempt"],
        "head_sha": SOURCE_SHA,
        "status": "completed",
        "conclusion": "skipped",
    })
    return {"total_count": len(jobs), "jobs": jobs}, checks


class Fw029GithubAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.required_checks, _ = load_required_checks(MANIFEST.read_bytes())
        self.run = sample_run()
        self.jobs_response, self.checks = sample_jobs()
        self.cases = {item["id"]: item for item in json.loads(CASES.read_text())["cases"]}

    def assert_adapter_error(self, callback: Any, case_id: str) -> AdapterError:
        with self.assertRaises(AdapterError) as context:
            callback()
        error = context.exception
        case = self.cases[case_id]
        self.assertEqual(error.state, case["expected_status"], str(error))
        self.assertEqual(error.code, case["expected_diagnostic"], str(error))
        return error

    def records(self, jobs: dict[str, Any] | None = None, checks: dict[int, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        return build_check_records(
            copy.deepcopy(self.jobs_response if jobs is None else jobs),
            run=copy.deepcopy(self.run),
            source_sha=SOURCE_SHA,
            required_checks=copy.deepcopy(self.required_checks),
            check_lookup=lambda check_id: copy.deepcopy((self.checks if checks is None else checks).get(check_id)),
        )

    def receipt(self, *, run: dict[str, Any] | None = None, repository: dict[str, Any] | None = None, records: list[dict[str, Any]] | None = None) -> tuple[dict[str, Any], bytes]:
        return build_receipt(
            repository=copy.deepcopy(REPOSITORY_RECORD if repository is None else repository),
            run=copy.deepcopy(self.run if run is None else run),
            check_records=copy.deepcopy(self.records() if records is None else records),
            required_manifest_bytes=MANIFEST.read_bytes(),
            source_sha=SOURCE_SHA,
            source_ref=ALLOWED_REF,
            contract_bytes=CONTRACT,
        )

    def test_observed_provider_records_produce_schema_valid_canonical_receipt(self) -> None:
        receipt, encoded = self.receipt()
        self.assertEqual(encoded, canonical(receipt))
        self.assertEqual(receipt["schema_version"], "1.0")
        self.assertEqual(receipt["repository"]["id"], str(EXPECTED_REPOSITORY_ID))
        self.assertEqual(receipt["source"], {"sha": SOURCE_SHA, "ref": ALLOWED_REF})
        self.assertEqual(receipt["provider_run"]["run_id"], str(self.run["id"]))
        self.assertEqual(receipt["provider_run"]["attempt"], self.run["run_attempt"])
        self.assertEqual(
            receipt["required_check_manifest_sha256"],
            hashlib.sha256(canonical(json.loads(MANIFEST.read_bytes()))).hexdigest(),
        )
        self.assertEqual(receipt["checks"], self.records())
        self.assertEqual(receipt["issuer"]["identity"], f"{REPOSITORY}/.github/workflows/fw029-evidence-probe.yml@{ALLOWED_REF}")

    def test_run_resolution_rejects_missing_ambiguous_and_mismatched_runs(self) -> None:
        duplicated = {"total_count": 2, "workflow_runs": [self.run, copy.deepcopy(self.run)]}
        self.assert_adapter_error(
            lambda: resolve_run(duplicated, source_sha=SOURCE_SHA, expected_ref=ALLOWED_REF),
            "FW029-SEM-02",
        )
        wrong_workflow = copy.deepcopy(self.run)
        wrong_workflow["path"] = ".github/workflows/untrusted.yml"
        self.assert_adapter_error(
            lambda: resolve_run(
                {"total_count": 1, "workflow_runs": [wrong_workflow]},
                source_sha=SOURCE_SHA,
                expected_ref=ALLOWED_REF,
            ),
            "FW029-SEM-14",
        )
        wrong_ref = copy.deepcopy(self.run)
        wrong_ref["head_branch"] = "refs/heads/other"
        with self.assertRaises(AdapterError) as context:
            resolve_run({"total_count": 1, "workflow_runs": [wrong_ref]}, source_sha=SOURCE_SHA, expected_ref=ALLOWED_REF)
        self.assertEqual(context.exception.code, "receipt.run_mismatch")

    def test_run_and_check_pages_fail_closed_when_incomplete_or_unbounded(self) -> None:
        truncated = {"total_count": 2, "workflow_runs": [self.run]}
        with self.assertRaisesRegex(AdapterError, "incomplete or unbounded"):
            resolve_run(truncated, source_sha=SOURCE_SHA, expected_ref=ALLOWED_REF)
        jobs, _ = sample_jobs()
        jobs["total_count"] = 101
        jobs["jobs"] = jobs["jobs"] * 25 + jobs["jobs"][:1]
        with self.assertRaisesRegex(AdapterError, "incomplete or unbounded"):
            self.records(jobs=jobs)

    def test_required_check_omission_duplicate_and_extra_are_rejected(self) -> None:
        missing = copy.deepcopy(self.jobs_response)
        missing["jobs"] = [j for j in missing["jobs"] if j["name"] != self.required_checks[0]["name"]]
        missing["total_count"] -= 1
        self.assert_adapter_error(lambda: self.records(jobs=missing), "FW029-SEM-04")

        duplicate = copy.deepcopy(self.jobs_response)
        duplicate["jobs"].append(copy.deepcopy(duplicate["jobs"][0]))
        duplicate["total_count"] += 1
        self.assert_adapter_error(lambda: self.records(jobs=duplicate), "FW029-SEM-04")

        extra = copy.deepcopy(self.jobs_response)
        extra["jobs"].append({**extra["jobs"][0], "id": 9999, "name": "Unexpected Check"})
        extra["total_count"] += 1
        self.assert_adapter_error(lambda: self.records(jobs=extra), "FW029-SEM-28")

    def test_missing_provider_check_data_is_unavailable(self) -> None:
        def missing_check(_: int) -> Any:
            raise AdapterError("http.failure", "synthetic unavailable response", "unavailable")
        self.assert_adapter_error(
            lambda: build_check_records(
                self.jobs_response,
                run=self.run,
                source_sha=SOURCE_SHA,
                required_checks=self.required_checks,
                check_lookup=missing_check,
            ),
            "FW029-SEM-03",
        )

    def test_check_failure_identity_and_source_mismatches_have_stable_diagnostics(self) -> None:
        failed = copy.deepcopy(self.jobs_response)
        failed_job = next(j for j in failed["jobs"] if j["name"] == self.required_checks[0]["name"])
        failed_job["conclusion"] = "failure"
        self.assert_adapter_error(lambda: self.records(jobs=failed), "FW029-SEM-18")

        wrong_identity = copy.deepcopy(self.checks)
        check_id = next(iter(wrong_identity))
        wrong_identity[check_id]["name"] = "Substituted Check"
        self.assert_adapter_error(
            lambda: self.records(checks=wrong_identity),
            "FW029-SEM-19",
        )

        wrong_source = copy.deepcopy(self.checks)
        wrong_source[check_id]["head_sha"] = "b" * 40
        self.assert_adapter_error(
            lambda: self.records(checks=wrong_source),
            "FW029-SEM-20",
        )

    def test_provider_app_and_check_suite_are_bound(self) -> None:
        for field, change in (
            ("app", {"id": 1, "slug": "other"}),
            ("check_suite", {"id": 1}),
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.checks)
                first = next(iter(changed))
                changed[first][field] = change
                with self.assertRaises(AdapterError) as context:
                    self.records(checks=changed)
                self.assertEqual(context.exception.code, "receipt.check_identity_mismatch")

    def test_repository_and_run_identity_mismatches_are_rejected(self) -> None:
        wrong_repo = {**REPOSITORY_RECORD, "id": EXPECTED_REPOSITORY_ID + 1}
        self.assert_adapter_error(
            lambda: self.receipt(repository=wrong_repo),
            "FW029-SEM-13",
        )
        for field, value in (
            ("run_attempt", 0),
            ("event", "workflow_dispatch"),
            ("head_branch", "other"),
            ("html_url", "file:///tmp/not-a-run"),
        ):
            with self.subTest(field=field):
                run = copy.deepcopy(self.run)
                run[field] = value
                self.assert_adapter_error(lambda: self.receipt(run=run), "FW029-SEM-16")

    def test_wrong_signer_caller_is_rejected_before_provider_lookup(self) -> None:
        from scripts.fw029_github_adapter import prepare_receipt
        self.assert_adapter_error(
            lambda: prepare_receipt(
                repository=REPOSITORY,
                source_sha=SOURCE_SHA,
                source_ref=ALLOWED_REF,
                event="workflow_dispatch",
                caller_workflow_ref=f"{REPOSITORY}/.github/workflows/other.yml@{ALLOWED_REF}",
            ),
            "FW029-SEM-14",
        )

    def test_wrong_check_set_supplied_to_receipt_builder_is_rejected(self) -> None:
        altered = self.records()
        altered[0]["logical_id"] = "unconfigured-check"
        self.assert_adapter_error(
            lambda: self.receipt(records=altered),
            "FW029-SEM-04",
        )

    def test_check_output_contains_only_bounded_schema_fields(self) -> None:
        records = self.records()
        self.assertEqual(
            set(records[0]),
            {"logical_id", "provider_check_id", "name", "conclusion", "head_sha"},
        )
        self.assertNotIn("output", records[0])
        self.assertNotIn("logs", records[0])

    def test_manifest_rejects_duplicate_keys_and_duplicate_check_identity(self) -> None:
        with self.assertRaises(AdapterError) as context:
            load_required_checks(b'{"schema_version":"1.0","schema_version":"1.0","required_checks":[]}')
        self.assertEqual(context.exception.code, "manifest.invalid")

        duplicate = {
            "schema_version": "1.0",
            "required_checks": [
                {"logical_id": "same", "name": "Same"},
                {"logical_id": "same", "name": "Same"},
            ],
        }
        with self.assertRaises(AdapterError):
            load_required_checks(canonical(duplicate))

    def test_architecture_semantic_case_ids_are_present(self) -> None:
        needed = {
            "FW029-SEM-02", "FW029-SEM-03", "FW029-SEM-04",
            "FW029-SEM-13", "FW029-SEM-14", "FW029-SEM-16",
            "FW029-SEM-18", "FW029-SEM-19", "FW029-SEM-20",
            "FW029-SEM-28", "FW029-SEM-30", "FW029-SEM-31",
        }
        self.assertTrue(needed <= self.cases.keys())


if __name__ == "__main__":
    unittest.main()
