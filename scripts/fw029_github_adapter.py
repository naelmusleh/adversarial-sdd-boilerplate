#!/usr/bin/env python3
"""Build a bounded FW-TASK-029 v1 receipt from observed GitHub Actions data.

This pilot adapter is deliberately scoped to the selected repository, ref and
workflow. It does not verify a signature, establish current trust, or authorize
a gate. Signing is performed only by the separately permissioned workflow job.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Mapping

from scripts.fw029_contracts import canonical_json_bytes, validate_receipt

REPOSITORY = "naelmusleh/adversarial-sdd-boilerplate"
ALLOWED_REF = "refs/heads/codex/v2-backlog-roadmap"
VERIFY_WORKFLOW = ".github/workflows/verify-pipeline.yml"
SIGNER_WORKFLOW = ".github/workflows/fw029-evidence-probe.yml"
EXPECTED_EVENT = "push"
EXPECTED_APP_ID = 15368
EXPECTED_REPOSITORY_ID = 1413825865
EXPECTED_APP_SLUG = "github-actions"
SKIPPED_CALLER_JOB = "FW-029 Synthetic Evidence Probe"
REQUIRED_CHECKS_PATH = Path("docs/framework/schemas/fw029/github-actions-required-checks.v1.json")
CONTRACT_PATH = Path("docs/framework/FRAMEWORK-GATE-CONTRACT-001.md")
MAX_PROVIDER_ITEMS = 100
MAX_PROVIDER_RESPONSE_BYTES = 1_048_576


class AdapterError(ValueError):
    """A fail-closed diagnostic for provider data or policy mismatch."""

    def __init__(self, code: str, message: str, state: str = "failed") -> None:
        super().__init__(message)
        self.code = code
        self.state = state


def _diag(code: str, message: str, state: str = "failed") -> AdapterError:
    return AdapterError(code, message, state)


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def load_required_checks(raw: bytes) -> tuple[list[dict[str, str]], bytes]:
    """Validate the bounded check manifest and return checks plus canonical bytes."""
    if not isinstance(raw, bytes) or not 0 < len(raw) <= 65_536:
        raise _diag("manifest.invalid", "required-check manifest is missing or out of bounds")
    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise _diag("manifest.invalid", "required-check manifest is invalid JSON") from exc
    if not isinstance(value, dict) or set(value) != {"schema_version", "required_checks"}:
        raise _diag("manifest.invalid", "required-check manifest has an invalid shape")
    checks = value.get("required_checks")
    if value.get("schema_version") != "1.0" or not isinstance(checks, list) or not 1 <= len(checks) <= 100:
        raise _diag("manifest.invalid", "required-check manifest version or count is invalid")
    logical_ids: set[str] = set()
    names: set[str] = set()
    normalized: list[dict[str, str]] = []
    for item in checks:
        if not isinstance(item, dict) or set(item) != {"logical_id", "name"}:
            raise _diag("manifest.invalid", "each required check needs only logical_id and name")
        logical_id, name = item.get("logical_id"), item.get("name")
        if (
            not isinstance(logical_id, str) or not logical_id.strip()
            or not isinstance(name, str) or not name.strip()
            or len(logical_id) > 255 or len(name) > 512
            or logical_id in logical_ids or name in names
        ):
            raise _diag("manifest.invalid", "required check identities must be unique and bounded")
        logical_ids.add(logical_id)
        names.add(name)
        normalized.append({"logical_id": logical_id, "name": name})
    normalized.sort(key=lambda item: item["logical_id"])
    if normalized != checks:
        raise _diag("manifest.invalid", "required checks must be sorted by logical_id")
    return normalized, canonical_json_bytes(value)


def _bounded_collection(response: Any, key: str, label: str) -> list[dict[str, Any]]:
    if not isinstance(response, dict):
        raise _diag(f"provider.{label}_invalid", f"{label} response must be an object")
    items = response.get(key)
    total = response.get("total_count")
    if (
        not isinstance(items, list)
        or not isinstance(total, int)
        or isinstance(total, bool)
        or total != len(items)
        or len(items) > MAX_PROVIDER_ITEMS
        or not all(isinstance(item, dict) for item in items)
    ):
        raise _diag(f"provider.{label}_invalid", f"{label} response is incomplete or unbounded")
    return items


def resolve_run(
    response: Any,
    *,
    source_sha: str,
    expected_ref: str,
    expected_event: str = EXPECTED_EVENT,
    workflow_path: str = VERIFY_WORKFLOW,
) -> dict[str, Any]:
    """Resolve exactly one successful provider run for the exact source and workflow."""
    runs = _bounded_collection(response, "workflow_runs", "runs")
    if response.get("total_count") == 0:
        raise _diag("provider.run_missing", "no matching Verify Pipeline run was returned")
    if not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        raise _diag("provider.source_mismatch", "source SHA must be a 40-character lowercase Git SHA")
    branch = expected_ref.removeprefix("refs/heads/")
    source_candidates = [
        run for run in runs
        if run.get("head_sha") == source_sha
        and run.get("head_branch") == branch
        and run.get("event") == expected_event
    ]
    if not source_candidates:
        raise _diag("receipt.run_mismatch", "provider run does not match source, ref and event")
    candidates = [
        run for run in source_candidates
        if isinstance(run.get("path"), str)
        and run.get("path", "").split("@", 1)[0] == workflow_path
    ]
    if not candidates:
        raise _diag("receipt.workflow_mismatch", "provider workflow path does not match the approved Verify Pipeline")
    if len(candidates) > 1:
        raise _diag("provider.run_ambiguous", "multiple matching provider runs were returned")
    run = candidates[0]
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        raise _diag("receipt.run_mismatch", "exact Verify Pipeline run is not completed successfully")
    if (
        not isinstance(run.get("id"), int) or isinstance(run.get("id"), bool) or run["id"] < 1
        or not isinstance(run.get("run_attempt"), int)
        or isinstance(run.get("run_attempt"), bool) or run["run_attempt"] < 1
        or not isinstance(run.get("check_suite_id"), int)
        or isinstance(run.get("check_suite_id"), bool) or run["check_suite_id"] < 1
        or run.get("head_sha") != source_sha
        or run.get("head_branch") != branch
        or run.get("event") != expected_event
        or not isinstance(run.get("path"), str)
        or run.get("path", "").split("@", 1)[0] != workflow_path
        or not isinstance(run.get("html_url"), str)
        or not run["html_url"].startswith("https://")
        or not isinstance(run.get("updated_at"), str)
    ):
        raise _diag("receipt.run_mismatch", "provider run identity fields are invalid or inconsistent")
    return run


def build_check_records(
    jobs_response: Any,
    *,
    run: Mapping[str, Any],
    source_sha: str,
    required_checks: list[dict[str, str]],
    check_lookup: Callable[[int], Any],
) -> list[dict[str, Any]]:
    """Match exact job and Check Run records to one provider run attempt."""
    jobs = _bounded_collection(jobs_response, "jobs", "checks")
    expected_names = {item["name"] for item in required_checks}
    names: dict[str, list[dict[str, Any]]] = {}
    skipped = []
    for job in jobs:
        name = job.get("name")
        if name == SKIPPED_CALLER_JOB:
            skipped.append(job)
        elif name in expected_names:
            names.setdefault(name, []).append(job)
        else:
            raise _diag("receipt.check_set_mismatch", "provider run has an unexpected check job")
    if (
        len(skipped) != 1
        or skipped[0].get("status") != "completed"
        or skipped[0].get("conclusion") != "skipped"
    ):
        raise _diag("receipt.check_set_mismatch", "known caller job must occur once and be skipped")
    if set(names) != expected_names or any(len(items) != 1 for items in names.values()):
        raise _diag("receipt.check_set_mismatch", "required provider check set is missing or duplicated")

    records: list[dict[str, Any]] = []
    for required in required_checks:
        name = required["name"]
        job = names[name][0]
        if (
            job.get("run_id") != run["id"]
            or job.get("run_attempt") != run["run_attempt"]
            or job.get("head_sha") != source_sha
            or job.get("status") != "completed"
            or job.get("conclusion") != "success"
            or not isinstance(job.get("id"), int)
            or isinstance(job.get("id"), bool)
            or job["id"] < 1
        ):
            if job.get("head_sha") != source_sha:
                raise _diag("receipt.check_source_mismatch", f"{name} targets a different source SHA")
            if job.get("conclusion") != "success" or job.get("status") != "completed":
                raise _diag("receipt.check_failed", f"{name} did not complete successfully")
            raise _diag("receipt.check_identity_mismatch", f"{name} does not belong to the exact run attempt")
        try:
            check = check_lookup(job["id"])
        except AdapterError as exc:
            raise _diag("provider.checks_unavailable", f"{name} Check Run could not be retrieved", "unavailable") from exc
        if not isinstance(check, dict):
            raise _diag("provider.checks_unavailable", f"{name} Check Run could not be retrieved", "unavailable")
        app = check.get("app")
        suite = check.get("check_suite")
        if not isinstance(app, dict) or not isinstance(suite, dict):
            raise _diag("receipt.check_identity_mismatch", f"{name} Check Run app or suite metadata is missing")
        if check.get("head_sha") != source_sha:
            raise _diag("receipt.check_source_mismatch", f"{name} Check Run targets a different source SHA")
        if check.get("status") != "completed" or check.get("conclusion") != "success":
            raise _diag("receipt.check_failed", f"{name} Check Run did not complete successfully")
        if (
            check.get("id") != job["id"]
            or app.get("id") != EXPECTED_APP_ID
            or app.get("slug") != EXPECTED_APP_SLUG
            or suite.get("id") != run["check_suite_id"]
            or check.get("name") != name
        ):
            raise _diag("receipt.check_identity_mismatch", f"{name} Check Run identity, suite or app mismatch")
        records.append({
            "logical_id": required["logical_id"],
            "provider_check_id": str(check["id"]),
            "name": name,
            "conclusion": "success",
            "head_sha": source_sha,
        })
    return records


def build_receipt(
    *,
    repository: Mapping[str, Any],
    run: Mapping[str, Any],
    check_records: list[dict[str, Any]],
    required_manifest_bytes: bytes,
    source_sha: str,
    source_ref: str,
    contract_bytes: bytes,
) -> tuple[dict[str, Any], bytes]:
    """Produce canonical schema-v1 receipt bytes from already-observed provider facts."""
    checks, manifest_canonical = load_required_checks(required_manifest_bytes)
    if (
        not isinstance(repository, Mapping)
        or repository.get("full_name") != REPOSITORY
        or repository.get("id") != EXPECTED_REPOSITORY_ID
    ):
        raise _diag("receipt.repository_mismatch", "provider repository identity differs from the pinned pilot repository")
    parts = REPOSITORY.split("/", 1)
    repo_id = repository.get("id")
    expected_pairs = [(item["logical_id"], item["name"]) for item in checks]
    actual_pairs = [(item.get("logical_id"), item.get("name")) for item in check_records if isinstance(item, dict)]
    if (
        not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", source_sha)
        or run.get("head_sha") != source_sha
    ):
        raise _diag("receipt.source_mismatch", "provider run source SHA differs from the dispatched source")
    if (
        source_ref != ALLOWED_REF
        or run.get("head_branch") != source_ref.removeprefix("refs/heads/")
        or run.get("event") != EXPECTED_EVENT
    ):
        raise _diag("receipt.run_mismatch", "provider run attempt, event or ref differs from the approved source")
    if not isinstance(run.get("path"), str) or run.get("path", "").split("@", 1)[0] != VERIFY_WORKFLOW:
        raise _diag("receipt.workflow_mismatch", "provider workflow identity differs from the approved path")
    if (
        len(check_records) != len(checks)
        or actual_pairs != expected_pairs
    ):
        raise _diag("receipt.check_set_mismatch", "provider check set differs from the approved manifest")
    if any(
        not isinstance(item, dict)
        or item.get("conclusion") != "success"
        or item.get("head_sha") != source_sha
        for item in check_records
    ):
        raise _diag("receipt.check_source_mismatch", "one or more provider checks differ from the exact source SHA")
    if not isinstance(run.get("id"), int) or isinstance(run.get("id"), bool) or run["id"] < 1:
        raise _diag("receipt.run_mismatch", "provider run ID is invalid")
    if not isinstance(run.get("run_attempt"), int) or isinstance(run.get("run_attempt"), bool) or run["run_attempt"] < 1:
        raise _diag("receipt.run_mismatch", "provider run attempt is invalid")
    expected_run_url = f"https://github.com/{REPOSITORY}/actions/runs/{run['id']}"
    if run.get("html_url") != expected_run_url:
        raise _diag("receipt.run_mismatch", "provider run URL is invalid or points at another run")
    if not isinstance(run.get("updated_at"), str):
        raise _diag("receipt.run_mismatch", "provider run update timestamp is missing")
    if not isinstance(contract_bytes, bytes) or not contract_bytes:
        raise _diag("contract.input_missing", "exact gate contract bytes are required")
    try:
        front_matter = contract_bytes.split(b"---", 2)[1].decode("utf-8", errors="strict")
    except (IndexError, UnicodeError) as exc:
        raise _diag("contract.invalid", "gate contract front matter is invalid") from exc
    match = re.search(r"^version:\s*([0-9]+\.[0-9]+)\s*$", front_matter, re.MULTILINE)
    if not match or match.group(1) != "1.2":
        raise _diag("contract.version_unsupported", "pilot adapter requires gate contract version 1.2")
    contract_digest = hashlib.sha256(contract_bytes).hexdigest()
    owner, name = parts
    workflow_identity = f"{REPOSITORY}/{VERIFY_WORKFLOW}@{source_ref}"
    issuer_identity = f"{REPOSITORY}/{SIGNER_WORKFLOW}@{source_ref}"
    checks_digest = hashlib.sha256(canonical_json_bytes(check_records)).hexdigest()
    receipt = {
        "schema_version": "1.0",
        "repository": {
            "host": "github.com",
            "owner": owner,
            "name": name,
            "id": str(repo_id),
        },
        "source": {"sha": source_sha, "ref": source_ref},
        "gate_contract": {
            "id": "FRAMEWORK-GATE-CONTRACT-001",
            "version": match.group(1),
            "sha256": contract_digest,
        },
        "workflow": {
            "path": VERIFY_WORKFLOW,
            "revision_sha": source_sha,
            "identity": workflow_identity,
        },
        "provider_run": {
            "provider": "github-actions",
            "run_id": str(run["id"]),
            "attempt": run["run_attempt"],
            "event": EXPECTED_EVENT,
            "ref": source_ref,
            "url": run["html_url"],
        },
        "required_check_manifest_sha256": hashlib.sha256(manifest_canonical).hexdigest(),
        "checks": check_records,
        "evidence": [{
            "evidence_id": "github-check-set",
            "sha256": checks_digest,
            "reference": run["html_url"],
        }],
        "issuer": {"provider": "github-actions-sigstore", "identity": issuer_identity},
        # Provider run updated_at is stable across repeated reads and is the
        # provenance observation time; it is not a freshness guarantee.
        "issued_at": run["updated_at"],
    }
    encoded = canonical_json_bytes(receipt)
    outcome = validate_receipt(encoded)
    if outcome.get("state") != "contract_valid":
        codes = ",".join(item.get("code", "unknown") for item in outcome.get("diagnostics", []))
        raise _diag("receipt.schema_invalid", f"generated receipt failed FW029 v1 schema validation ({codes})")
    return receipt, encoded


def _api(endpoint: str) -> Any:
    if not isinstance(endpoint, str) or not endpoint.startswith("repos/"):
        raise _diag("provider.endpoint_invalid", "provider endpoint is invalid")
    try:
        result = subprocess.run(
            ["gh", "api", "-H", "Accept: application/vnd.github+json", endpoint],
            check=False,
            capture_output=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _diag("provider.unavailable", "GitHub API request failed or timed out") from exc
    if result.returncode != 0 or len(result.stdout) > MAX_PROVIDER_RESPONSE_BYTES:
        raise _diag("provider.unavailable", "GitHub API request failed or exceeded the response bound")
    try:
        return json.loads(result.stdout.decode("utf-8", errors="strict"), object_pairs_hook=_no_duplicates, parse_constant=_reject_constant)
    except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise _diag("provider.response_invalid", "GitHub API response was not valid bounded JSON") from exc


def prepare_receipt(*, repository: str, source_sha: str, source_ref: str, event: str, caller_workflow_ref: str) -> bytes:
    if repository != REPOSITORY or source_ref != ALLOWED_REF or event != "workflow_dispatch":
        raise _diag("provider.scope_rejected", "receipt preparation is restricted to the authorized repository/ref/manual dispatch")
    expected_caller = f"{REPOSITORY}/{VERIFY_WORKFLOW}@{ALLOWED_REF}"
    if caller_workflow_ref != expected_caller:
        raise _diag("receipt.workflow_mismatch", "workflow was not called by the authorized Verify Pipeline identity")
    if not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        raise _diag("provider.source_mismatch", "dispatched source SHA is invalid")

    api = lambda endpoint: _api(endpoint)
    runs_response = api(
        f"repos/{REPOSITORY}/actions/workflows/verify-pipeline.yml/runs"
        f"?head_sha={source_sha}&event={EXPECTED_EVENT}&per_page={MAX_PROVIDER_ITEMS}"
    )
    run = resolve_run(runs_response, source_sha=source_sha, expected_ref=ALLOWED_REF)
    jobs_response = api(
        f"repos/{REPOSITORY}/actions/runs/{run['id']}/attempts/{run['run_attempt']}/jobs"
        f"?per_page={MAX_PROVIDER_ITEMS}"
    )
    required_raw = REQUIRED_CHECKS_PATH.read_bytes()
    required_checks, _ = load_required_checks(required_raw)
    def lookup_check(check_id: int) -> Any:
        try:
            return api(f"repos/{REPOSITORY}/check-runs/{check_id}")
        except AdapterError as exc:
            raise _diag("provider.checks_unavailable", "provider Check Run data could not be retrieved", "unavailable") from exc

    check_records = build_check_records(
        jobs_response,
        run=run,
        source_sha=source_sha,
        required_checks=required_checks,
        check_lookup=lookup_check,
    )
    repository_response = api(f"repos/{REPOSITORY}")
    contract_bytes = CONTRACT_PATH.read_bytes()
    _, receipt_bytes = build_receipt(
        repository=repository_response,
        run=run,
        check_records=check_records,
        required_manifest_bytes=required_raw,
        source_sha=source_sha,
        source_ref=ALLOWED_REF,
        contract_bytes=contract_bytes,
    )
    return receipt_bytes


def main() -> int:
    try:
        receipt = prepare_receipt(
            repository=os.environ.get("GH_REPOSITORY", ""),
            source_sha=os.environ.get("GH_SHA", ""),
            source_ref=os.environ.get("GH_REF", ""),
            event=os.environ.get("GH_EVENT", ""),
            caller_workflow_ref=os.environ.get("GH_CALLER_WORKFLOW_REF", ""),
        )
        target = Path("receipt.json")
        temporary = Path(".receipt.json.tmp")
        if target.exists() or target.is_symlink() or temporary.exists() or temporary.is_symlink():
            raise _diag("receipt.output_exists", "receipt output path already exists")
        temporary.write_bytes(receipt)
        temporary.replace(target)
        print(f"Prepared schema-valid canonical receipt ({len(receipt)} bytes) for the exact provider run.")
        return 0
    except (AdapterError, OSError) as exc:
        code = exc.code if isinstance(exc, AdapterError) else "receipt.output_error"
        print(f"{code}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
