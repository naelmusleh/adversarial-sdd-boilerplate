from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any

from scripts.fw029_contracts import canonical_json_bytes
from scripts.fw029_verifier import MAX_TOOL_OUTPUT, VerificationError, verify_files


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs/framework/schemas/fw029/fixtures"
SIGNER = "sample-owner/sample-repo/.github/workflows/signer.yml@refs/heads/sample"
SIGNER_URI = "https://github.com/" + SIGNER


def _sample_inputs() -> tuple[dict[str, Any], dict[str, Any], bytes]:
    receipt = json.loads((FIXTURES / "receipt.valid.synthetic.json").read_bytes())
    policy = json.loads((FIXTURES / "policy.valid.synthetic.json").read_bytes())
    receipt["repository"].update(host="github.com", owner="sample-owner", name="sample-repo", id="123456789")
    receipt["source"] = {"sha": "a" * 40, "ref": "refs/heads/sample"}
    receipt["workflow"] = {
        "path": ".github/workflows/verify-pipeline.yml",
        "revision_sha": "a" * 40,
        "identity": "sample-owner/sample-repo/.github/workflows/verify-pipeline.yml@refs/heads/sample",
    }
    receipt["issuer"] = {"provider": "github-actions-sigstore", "identity": SIGNER}
    receipt["provider_run"].update(provider="github-actions", run_id="100", attempt=1, event="push", ref="refs/heads/sample")
    receipt["evidence"] = [{"evidence_id": "github-check-set", "sha256": "0" * 64, "reference": "https://github.com/sample-owner/sample-repo/actions/runs/100"}]
    receipt["evidence"][0]["sha256"] = hashlib.sha256(canonical_json_bytes(receipt["checks"])).hexdigest()

    policy["repository"] = copy.deepcopy(receipt["repository"])
    policy["source"] = copy.deepcopy(receipt["source"])
    policy["gate_contract"] = copy.deepcopy(receipt["gate_contract"])
    policy["workflow"] = copy.deepcopy(receipt["workflow"])
    policy["provider_run"] = {key: receipt["provider_run"][key] for key in ("provider", "run_id", "attempt", "event", "ref")}
    policy["required_check_manifest_sha256"] = receipt["required_check_manifest_sha256"]
    policy["required_checks"] = [{"logical_id": item["logical_id"], "name": item["name"]} for item in receipt["checks"]]
    policy["issuer"] = {"provider": "github-actions-sigstore", "identity": SIGNER, "trust_root_sha256": ""}
    root = b'{"synthetic_test_root":true}\n'
    policy["issuer"]["trust_root_sha256"] = hashlib.sha256(root).hexdigest()
    return receipt, policy, root


def _verified_output(receipt: dict[str, Any]) -> bytes:
    receipt_bytes = canonical_json_bytes(receipt)
    repo = "https://github.com/sample-owner/sample-repo"
    source_sha = receipt["source"]["sha"]
    source_ref = receipt["source"]["ref"]
    workflow_path = receipt["workflow"]["path"]
    workflow_identity = receipt["workflow"]["identity"]
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": "receipt.json", "digest": {"sha256": hashlib.sha256(receipt_bytes).hexdigest()}}],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "externalParameters": {"workflow": {"repository": repo, "path": workflow_path, "ref": source_ref}},
                "internalParameters": {"github": {"repository_id": "123456789", "runner_environment": "github-hosted"}},
                "resolvedDependencies": [{"uri": f"git+{repo}@{source_ref}", "digest": {"gitCommit": source_sha}}],
            },
            "runDetails": {
                "builder": {"id": SIGNER_URI},
                "metadata": {"invocationId": repo + "/actions/runs/200/attempts/1"},
            },
        },
    }
    certificate = {
        "issuer": "https://token.actions.githubusercontent.com",
        "subjectAlternativeName": SIGNER_URI,
        "buildSignerURI": SIGNER_URI,
        "sourceRepositoryURI": repo,
        "sourceRepositoryIdentifier": "123456789",
        "sourceRepositoryDigest": source_sha,
        "sourceRepositoryRef": source_ref,
        "githubWorkflowRepository": "sample-owner/sample-repo",
        "githubWorkflowSHA": source_sha,
        "buildSignerDigest": source_sha,
        "githubWorkflowRef": "refs/heads/sample",
        "githubWorkflowTrigger": "workflow_dispatch",
        "buildTrigger": "workflow_dispatch",
        "buildConfigURI": f"{repo}/{workflow_path}@{source_ref}",
    }
    output = [{"verificationResult": {
        "statement": statement,
        "signature": {"certificate": certificate},
        "verifiedTimestamps": [{"type": "Tlog", "timestamp": "2026-10-25T00:00:00Z"}],
    }}]
    return json.dumps(output).encode()


class VerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.receipt, self.policy, self.root = _sample_inputs()
        self.receipt_path = self.directory / "receipt.json"
        self.bundle_path = self.directory / "bundle.jsonl"
        self.policy_path = self.directory / "policy.json"
        self.root_path = self.directory / "trusted_root.jsonl"
        self.receipt_path.write_bytes(canonical_json_bytes(self.receipt))
        self.bundle_path.write_text('{"synthetic":true}\n', encoding="utf-8")
        self.policy_path.write_bytes(canonical_json_bytes(self.policy))
        self.root_path.write_bytes(self.root)
        self.policy_digest = hashlib.sha256(self.policy_path.read_bytes()).hexdigest()
        self.output = _verified_output(self.receipt)

    def runner(self, output: bytes | None = None):
        calls = []

        def run(command, **kwargs):
            calls.append((command, kwargs))
            return CompletedProcess(command, 0, self.output if output is None else output, b"")

        return run, calls

    def verify(self, runner):
        return verify_files(
            receipt_path=self.receipt_path,
            bundle_path=self.bundle_path,
            policy_path=self.policy_path,
            expected_policy_sha256=self.policy_digest,
            trust_root_path=self.root_path,
            runner=runner,
        )

    def test_pinned_synthetic_fixture_passes_without_authorizing_action(self) -> None:
        runner, calls = self.runner()
        result = self.verify(runner)
        self.assertEqual(result["state"], "passed")
        self.assertEqual(result["freshness"], "unknown")
        self.assertFalse(result["authorization"])
        self.assertEqual(len(calls), 1)
        self.assertIn("--custom-trusted-root", calls[0][0])
        self.assertIn("--bundle", calls[0][0])

    def test_repeat_verification_is_read_only_and_deterministic(self) -> None:
        runner, _ = self.runner()
        self.assertEqual(self.verify(runner), self.verify(runner))

    def test_changed_expected_policy_digest_fails_before_cli(self) -> None:
        runner, calls = self.runner()
        with self.assertRaises(VerificationError) as error:
            verify_files(
                receipt_path=self.receipt_path, bundle_path=self.bundle_path,
                policy_path=self.policy_path, expected_policy_sha256="f" * 64,
                trust_root_path=self.root_path, runner=runner,
            )
        self.assertEqual(error.exception.code, "policy.digest_mismatch")
        self.assertEqual(calls, [])

    def test_changed_subject_digest_is_rejected(self) -> None:
        result = json.loads(self.output)
        result[0]["verificationResult"]["statement"]["subject"][0]["digest"]["sha256"] = "f" * 64
        runner, calls = self.runner(json.dumps(result).encode())
        with self.assertRaises(VerificationError) as error:
            self.verify(runner)
        self.assertEqual(error.exception.code, "attestation.provenance_mismatch")
        self.assertEqual(len(calls), 1)

    def test_changed_trusted_root_fails_before_signature_verification(self) -> None:
        self.root_path.write_bytes(self.root + b"tamper")
        runner, calls = self.runner()
        with self.assertRaises(VerificationError) as error:
            self.verify(runner)
        self.assertEqual(error.exception.code, "trust_root.digest_mismatch")
        self.assertEqual(calls, [])

    def test_signer_identity_mutation_is_rejected(self) -> None:
        result = json.loads(self.output)
        result[0]["verificationResult"]["signature"]["certificate"]["subjectAlternativeName"] = "https://attacker.example/signer"
        runner, _ = self.runner(json.dumps(result).encode())
        with self.assertRaises(VerificationError) as error:
            self.verify(runner)
        self.assertEqual(error.exception.code, "attestation.provenance_mismatch")

    def test_gh_signature_rejection_fails_closed(self) -> None:
        def rejected(command, **kwargs):
            return CompletedProcess(command, 1, b"", b"signature invalid")

        with self.assertRaises(VerificationError) as error:
            self.verify(rejected)
        self.assertEqual(error.exception.code, "attestation.signature_invalid")

    def test_repository_identity_mutation_is_rejected(self) -> None:
        result = json.loads(self.output)
        result[0]["verificationResult"]["signature"]["certificate"]["sourceRepositoryIdentifier"] = "999"
        runner, _ = self.runner(json.dumps(result).encode())
        with self.assertRaises(VerificationError):
            self.verify(runner)

    def test_unlisted_evidence_type_fails_closed(self) -> None:
        self.receipt["evidence"].append({"evidence_id": "other", "sha256": "0" * 64, "reference": "https://example.test/evidence"})
        self.receipt_path.write_bytes(canonical_json_bytes(self.receipt))
        runner, calls = self.runner()
        with self.assertRaises(VerificationError) as error:
            self.verify(runner)
        self.assertEqual(error.exception.code, "evidence.unsupported")
        self.assertEqual(calls, [])

    def test_noncanonical_signed_receipt_fails_before_signature_verification(self) -> None:
        self.receipt_path.write_text(json.dumps(self.receipt, indent=2), encoding="utf-8")
        runner, calls = self.runner()
        with self.assertRaises(VerificationError) as error:
            self.verify(runner)
        self.assertEqual(error.exception.code, "receipt.canonicalization_mismatch")
        self.assertEqual(calls, [])

    def test_oversized_bundle_fails_at_bounded_read(self) -> None:
        self.bundle_path.write_bytes(b"x" * (MAX_TOOL_OUTPUT + 4096))
        runner, calls = self.runner()
        with self.assertRaises(VerificationError) as error:
            self.verify(runner)
        self.assertEqual(error.exception.code, "bundle.size_invalid")
        self.assertEqual(calls, [])

    def test_cli_consumes_snapshots_if_original_paths_change(self) -> None:
        original_receipt = self.receipt_path.read_bytes()
        original_bundle = self.bundle_path.read_bytes()
        original_root = self.root_path.read_bytes()
        calls = []

        def replace_inputs_then_verify(command, **kwargs):
            calls.append(command)
            self.receipt_path.write_bytes(b"replaced receipt")
            self.bundle_path.write_bytes(b"replaced bundle")
            self.root_path.write_bytes(b"replaced root")
            receipt_snapshot = Path(command[3])
            bundle_snapshot = Path(command[command.index("--bundle") + 1])
            root_snapshot = Path(command[command.index("--custom-trusted-root") + 1])
            self.assertEqual(receipt_snapshot.read_bytes(), original_receipt)
            self.assertEqual(bundle_snapshot.read_bytes(), original_bundle)
            self.assertEqual(root_snapshot.read_bytes(), original_root)
            return CompletedProcess(command, 0, self.output, b"")

        result = self.verify(replace_inputs_then_verify)
        self.assertEqual(result["state"], "passed")
        self.assertEqual(len(calls), 1)

    def test_untrusted_gh_result_is_not_passed(self) -> None:
        runner, _ = self.runner(b"not-json")
        with self.assertRaises(VerificationError) as error:
            self.verify(runner)
        self.assertEqual(error.exception.code, "attestation.json_invalid")


if __name__ == "__main__":
    unittest.main()
