#!/usr/bin/env python3
"""Offline, fail-closed verifier for FW-TASK-029 GitHub/Sigstore receipts.

The verifier checks a caller-pinned policy and trust-root snapshot, asks the
installed GitHub CLI to verify the detached Sigstore bundle, then applies
additional exact-receipt and GitHub provenance checks. Success is provenance
verification only; it is never gate or release authorization.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.fw029_contracts import canonical_json_bytes, validate_receipt_policy

MAX_TOOL_OUTPUT = 2_097_152
MAX_INPUT = 262_144
OIDC_ISSUER = "https://token.actions.githubusercontent.com"
PREDICATE_TYPE = "https://slsa.dev/provenance/v1"
REPOSITORY_URI_PREFIX = "https://github.com/"


class VerificationError(ValueError):
    def __init__(self, code: str, message: str, state: str = "failed") -> None:
        super().__init__(message)
        self.code = code
        self.state = state


def _fail(code: str, message: str, state: str = "failed") -> VerificationError:
    return VerificationError(code, message, state)


def _read(path: str | Path, label: str, limit: int = MAX_INPUT) -> bytes:
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise _fail(f"{label}.input_missing", f"cannot read {label} input", "blocked") from exc
    if not data or len(data) > limit:
        raise _fail(f"{label}.size_invalid", f"{label} input is empty or exceeds {limit} bytes")
    return data


def _parse_json(raw: bytes, label: str) -> Any:
    try:
        def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate object key")
                result[key] = value
            return result

        return json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=unique_pairs)
    except (UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise _fail(f"{label}.json_invalid", f"{label} output is not valid UTF-8 JSON") from exc


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise _fail("attestation.output_invalid", f"verified attestation is missing {label}")
    return value


def _same(actual: Any, expected: str, label: str) -> None:
    if not isinstance(actual, str) or not hmac.compare_digest(actual, expected):
        raise _fail("attestation.provenance_mismatch", f"verified attestation {label} does not match pinned receipt and policy")


def _repository(policy: dict[str, Any]) -> tuple[str, str, str]:
    repo = policy["repository"]
    if repo["host"] != "github.com":
        raise _fail("policy.provider_unsupported", "only github.com GitHub artifact attestations are supported")
    name = f"{repo['owner']}/{repo['name']}"
    uri = f"{REPOSITORY_URI_PREFIX}{name}"
    return name, uri, repo["id"]


def _run_gh(
    receipt_path: str | Path,
    bundle_path: str | Path,
    root_path: str | Path,
    policy: dict[str, Any],
    runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    repo_name, _, _ = _repository(policy)
    receipt = policy["source"]
    workflow = policy["workflow"]
    issuer = policy["issuer"]["identity"]
    if "@" not in issuer:
        raise _fail("policy.issuer_invalid", "issuer identity must pin a workflow ref")
    command = [
        "gh", "attestation", "verify", str(receipt_path),
        "--bundle", str(bundle_path),
        "--repo", repo_name,
        "--cert-identity", f"{REPOSITORY_URI_PREFIX}{issuer}",
        "--cert-oidc-issuer", OIDC_ISSUER,
        "--source-digest", receipt["sha"],
        "--source-ref", receipt["ref"],
        "--custom-trusted-root", str(root_path),
        "--format", "json",
    ]
    try:
        result = runner(command, check=False, capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _fail("verifier.unavailable", "GitHub CLI could not complete bounded verification", "unavailable") from exc
    if len(result.stdout) > MAX_TOOL_OUTPUT or len(result.stderr) > MAX_TOOL_OUTPUT:
        raise _fail("verifier.output_unbounded", "GitHub CLI output exceeded the configured bound")
    if result.returncode != 0:
        raise _fail("attestation.signature_invalid", "GitHub CLI rejected the signature, trust root, or signer policy")
    output = _parse_json(result.stdout, "attestation")
    if not isinstance(output, list) or len(output) != 1 or not isinstance(output[0], dict):
        raise _fail("attestation.output_invalid", "expected exactly one verified attestation")
    verification = output[0].get("verificationResult")
    if not isinstance(verification, dict):
        raise _fail("attestation.output_invalid", "verified attestation result is missing")
    return verification


def _check_provenance(verification: dict[str, Any], receipt: dict[str, Any], receipt_bytes: bytes, policy: dict[str, Any]) -> int:
    statement = verification.get("statement")
    if not isinstance(statement, dict):
        raise _fail("attestation.statement_missing", "signed in-toto statement is missing")
    if statement.get("_type") != "https://in-toto.io/Statement/v1" or statement.get("predicateType") != PREDICATE_TYPE:
        raise _fail("attestation.statement_unsupported", "statement or predicate type is unsupported")
    subjects = statement.get("subject")
    expected_receipt_sha = hashlib.sha256(receipt_bytes).hexdigest()
    if not isinstance(subjects, list) or len(subjects) != 1 or not isinstance(subjects[0], dict):
        raise _fail("attestation.subject_mismatch", "attestation must bind exactly one receipt subject")
    subject = subjects[0]
    _same(subject.get("digest", {}).get("sha256") if isinstance(subject.get("digest"), dict) else None, expected_receipt_sha, "receipt subject digest")
    if subject.get("name") != "receipt.json":
        raise _fail("attestation.subject_mismatch", "attestation subject name is not receipt.json")

    repo_name, repo_uri, repo_id = _repository(policy)
    source = receipt["source"]
    source_workflow = policy["workflow"]
    issuer_identity = policy["issuer"]["identity"]
    issuer_uri = f"{REPOSITORY_URI_PREFIX}{issuer_identity}"
    predicate = statement.get("predicate")
    if not isinstance(predicate, dict):
        raise _fail("attestation.predicate_missing", "SLSA provenance predicate is missing")
    build = predicate.get("buildDefinition")
    details = predicate.get("runDetails")
    if not isinstance(build, dict) or not isinstance(details, dict):
        raise _fail("attestation.predicate_invalid", "SLSA build definition or run details are missing")
    external = build.get("externalParameters")
    workflow_claim = external.get("workflow") if isinstance(external, dict) else None
    if not isinstance(workflow_claim, dict):
        raise _fail("attestation.predicate_invalid", "SLSA workflow parameters are missing")
    _same(workflow_claim.get("repository"), repo_uri, "source workflow repository")
    _same(workflow_claim.get("path"), source_workflow["path"], "source workflow path")
    _same(workflow_claim.get("ref"), source["ref"], "source workflow ref")

    builder = details.get("builder")
    _same(builder.get("id") if isinstance(builder, dict) else None, issuer_uri, "reusable signer workflow")
    metadata = details.get("metadata")
    invocation = metadata.get("invocationId") if isinstance(metadata, dict) else None
    invocation_match = re.fullmatch(re.escape(repo_uri) + r"/actions/runs/[1-9][0-9]*/attempts/[1-9][0-9]*", invocation) if isinstance(invocation, str) else None
    if not invocation_match:
        raise _fail("attestation.invocation_invalid", "signer invocation ID is not a bounded run/attempt URI for the pinned repository")

    internal = build.get("internalParameters")
    github = internal.get("github") if isinstance(internal, dict) else None
    _same(github.get("repository_id") if isinstance(github, dict) else None, repo_id, "attested repository ID")
    if not isinstance(github, dict) or github.get("runner_environment") != "github-hosted":
        raise _fail("attestation.runner_untrusted", "attestation was not produced on a GitHub-hosted runner")

    dependencies = build.get("resolvedDependencies")
    expected_dependency_uri = f"git+{repo_uri}@{source['ref']}"
    matching = []
    if isinstance(dependencies, list):
        for dependency in dependencies:
            if not isinstance(dependency, dict) or not isinstance(dependency.get("digest"), dict):
                continue
            if dependency.get("uri") == expected_dependency_uri and dependency["digest"].get("gitCommit") == source["sha"]:
                matching.append(dependency)
    if len(matching) != 1:
        raise _fail("attestation.source_dependency_mismatch", "SLSA resolved dependency does not uniquely bind the exact source SHA and ref")

    certificate = verification.get("signature", {}).get("certificate") if isinstance(verification.get("signature"), dict) else None
    if not isinstance(certificate, dict):
        raise _fail("attestation.certificate_missing", "verified signing certificate claims are missing")
    for key, expected, label in (
        ("issuer", OIDC_ISSUER, "OIDC issuer"),
        ("subjectAlternativeName", issuer_uri, "signer SAN"),
        ("buildSignerURI", issuer_uri, "certificate signer workflow"),
        ("sourceRepositoryURI", repo_uri, "source repository URI"),
        ("sourceRepositoryIdentifier", repo_id, "source repository ID"),
        ("sourceRepositoryDigest", source["sha"], "source revision"),
        ("sourceRepositoryRef", source["ref"], "source ref"),
        ("githubWorkflowRepository", repo_name, "signer repository"),
        ("githubWorkflowSHA", source_workflow["revision_sha"], "signer workflow revision"),
        ("buildSignerDigest", source_workflow["revision_sha"], "signer workflow digest"),
        ("githubWorkflowRef", issuer_identity.rsplit("@", 1)[1], "signer workflow ref"),
        ("buildConfigURI", f"{repo_uri}/{source_workflow['path']}@{source['ref']}", "caller workflow identity"),
    ):
        _same(certificate.get(key), expected, label)
    if certificate.get("githubWorkflowTrigger") != "workflow_dispatch" or certificate.get("buildTrigger") != "workflow_dispatch":
        raise _fail("attestation.trigger_unsupported", "pilot signer must be invoked through workflow_dispatch")
    if certificate.get("runnerEnvironment") != "github-hosted":
        raise _fail("attestation.runner_untrusted", "signing certificate does not identify a GitHub-hosted runner")

    timestamps = verification.get("verifiedTimestamps")
    if not isinstance(timestamps, list) or not timestamps:
        raise _fail("attestation.timestamp_missing", "no verified transparency or timestamp evidence was returned")
    return len(timestamps)


def verify_files(
    *, receipt_path: str | Path, bundle_path: str | Path, policy_path: str | Path,
    expected_policy_sha256: str, trust_root_path: str | Path,
    runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    receipt_bytes = _read(receipt_path, "receipt")
    policy_bytes = _read(policy_path, "policy", 65_536)
    root_bytes = _read(trust_root_path, "trust_root", MAX_INPUT)
    bundle_bytes = _read(bundle_path, "bundle", MAX_TOOL_OUTPUT)
    if not isinstance(expected_policy_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_policy_sha256):
        raise _fail("policy.expected_digest_invalid", "separately supplied policy digest must be lowercase SHA-256", "blocked")
    policy = _parse_json(policy_bytes, "policy")
    receipt = _parse_json(receipt_bytes, "receipt")
    if not isinstance(policy, dict) or not isinstance(receipt, dict):
        raise _fail("input.shape_invalid", "receipt and policy roots must be JSON objects")
    evidence = receipt.get("evidence")
    if (
        not isinstance(evidence, list)
        or len(evidence) != 1
        or not isinstance(evidence[0], dict)
        or evidence[0].get("evidence_id") != "github-check-set"
    ):
        raise _fail("evidence.unsupported", "this verifier supports exactly the github-check-set evidence record")
    try:
        bundle = bundle_bytes.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise _fail("bundle.json_invalid", "attestation bundle must be UTF-8 JSONL") from exc
    if not bundle.strip() or len(bundle.splitlines()) > 10:
        raise _fail("bundle.size_invalid", "attestation bundle must contain between 1 and 10 bounded JSONL lines")

    evidence_bytes = {"github-check-set": canonical_json_bytes(receipt.get("checks"))}
    policy_result = validate_receipt_policy(
        receipt_bytes, policy_bytes,
        expected_policy_sha256=expected_policy_sha256,
        trust_root_bytes=root_bytes,
        evidence_bytes=evidence_bytes,
    )
    if policy_result.get("state") != "contract_valid":
        diagnostics = policy_result.get("diagnostics", [])
        first = diagnostics[0] if diagnostics else {"code": "policy.invalid", "message": "receipt or policy failed validation"}
        state = policy_result.get("state", "failed")
        raise _fail(first.get("code", "policy.invalid"), first.get("message", "receipt or policy failed validation"), state)
    if not hmac.compare_digest(hashlib.sha256(root_bytes).hexdigest(), policy["issuer"]["trust_root_sha256"]):
        raise _fail("trust_root.digest_mismatch", "trust-root bytes do not match policy pin")
    verification = _run_gh(receipt_path, bundle_path, trust_root_path, policy, runner)
    timestamp_count = _check_provenance(verification, receipt, receipt_bytes, policy)
    return {
        "state": "passed",
        "signature_status": "cryptographically-verified",
        "provider_authentication": "github-sigstore-attestation-verified",
        "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        "policy_sha256": hashlib.sha256(policy_bytes).hexdigest(),
        "trust_root_sha256": hashlib.sha256(root_bytes).hexdigest(),
        "verified_timestamp_count": timestamp_count,
        "freshness": "unknown",
        "revocation_status": "not-established",
        "authorization": False,
        "diagnostics": [],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--policy-sha256", required=True, help="independently supplied digest of exact policy bytes")
    parser.add_argument("--trusted-root", required=True, help="caller-supplied GitHub trusted_root.jsonl snapshot")
    args = parser.parse_args(argv)
    try:
        result = verify_files(
            receipt_path=args.receipt, bundle_path=args.bundle,
            policy_path=args.policy, expected_policy_sha256=args.policy_sha256,
            trust_root_path=args.trusted_root,
        )
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except VerificationError as exc:
        result = {
            "state": exc.state,
            "signature_status": "not-verified",
            "provider_authentication": "not-verified",
            "freshness": "unknown",
            "authorization": False,
            "diagnostics": [{"code": exc.code, "message": str(exc)}],
        }
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 1


if __name__ == "__main__":
    sys.exit(main())
