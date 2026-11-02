from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

from scripts import architecture_research as research


class ArchitectureResearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "docs/framework").mkdir(parents=True)
        (self.root / "docs/framework/FRAMEWORK-BACKLOG-001.md").write_text(
            "# Framework backlog\n\n### FW-TASK-014 — Governance audit\n",
            encoding="utf-8",
        )
        (self.root / "README.md").write_text("Framework test fixture\n", encoding="utf-8")
        self.backlog_path = self.root / "docs/framework/FRAMEWORK-BACKLOG-001.md"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    @staticmethod
    def audit_payload(total: int = 0) -> dict[str, object]:
        severities = {name: 0 for name in ("info", "low", "moderate", "high", "critical", "total")}
        severities["total"] = total
        if total:
            severities["high"] = total
        return {
            "metadata": {
                "vulnerabilities": severities,
                "dependencies": {name: 4 for name in ("prod", "dev", "optional", "peer", "total")},
            }
        }

    @staticmethod
    def valid_result(domain: str, *, primary: bool) -> dict[str, object]:
        return {
            "title": f"Technical implementation evidence from {domain}",
            "url": f"https://{domain}/engineering/evidence",
            "domain": domain,
            "published_date": "2026-10-01",
            "snippet": "Technical documentation records a reproducible test, schema, and architecture evaluation.",
            "relevance_score": 0.9,
            "primary_source_domain": primary,
            "evidence_terms": ["test", "schema", "evaluation"],
            "hype_terms": [],
        }

    def eligible_research_payload(self) -> dict[str, object]:
        sweeps = []
        for definition in research.SWEEPS:
            sweeps.append(
                {
                    "key": definition["key"],
                    "query": definition["query"],
                    "provider_query": f"{definition['query']} {definition['search_scope']}",
                    "status": "complete",
                    "error_code": None,
                    "results": [
                        self.valid_result("docs.github.com", primary=True),
                        self.valid_result("independent.example.org", primary=False),
                        self.valid_result("standards.example.net", primary=False),
                    ],
                }
            )
        return {
            "schema_version": 1,
            "provider": "Tavily Search API",
            "collected_at": "2026-10-13T12:00:00Z",
            "status": "complete",
            "sweeps": sweeps,
        }

    def write_render_inputs(
        self,
        *,
        audit: object | None = None,
        research_payload: object | None = None,
        audit_exit_code: int = 0,
    ) -> tuple[Path, Path, Path]:
        audit_path = self.root / "audit.json"
        research_path = self.root / "research.json"
        report_path = self.root / "docs/decisions/architecture-audits/ARCH-AUDIT-123-1-001.md"
        audit_path.write_text(json.dumps(self.audit_payload() if audit is None else audit), encoding="utf-8")
        research_path.write_text(
            json.dumps(self.eligible_research_payload() if research_payload is None else research_payload),
            encoding="utf-8",
        )
        return audit_path, research_path, report_path

    def render(self, *, audit: object | None = None, research_payload: object | None = None, audit_exit_code: int = 0):
        audit_path, research_path, report_path = self.write_render_inputs(
            audit=audit,
            research_payload=research_payload,
            audit_exit_code=audit_exit_code,
        )
        fixed_now = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)
        with patch.object(research, "utc_now", return_value=fixed_now):
            metadata = research.render_report(
                audit_path=audit_path,
                audit_exit_code=audit_exit_code,
                research_path=research_path,
                report_path=report_path,
                backlog_path=self.backlog_path,
                run_id="123",
                run_attempt="1",
                source_sha="a" * 40,
            )
        return metadata, report_path.read_text(encoding="utf-8"), report_path

    def test_missing_api_key_records_all_sweeps_unavailable_without_network_calls(self) -> None:
        output_path = self.root / "research.json"
        with patch.dict(os.environ, {}, clear=True), patch.object(research, "request_search") as request:
            result = research.collect(output_path)

        self.assertEqual(result, 0)
        request.assert_not_called()
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "unavailable")
        self.assertEqual([sweep["status"] for sweep in payload["sweeps"]], ["unavailable"] * 3)
        self.assertEqual({sweep["error_code"] for sweep in payload["sweeps"]}, {"missing_api_key"})
        self.assertNotIn("TAVILY_API_KEY", output_path.read_text(encoding="utf-8"))

    def test_collection_attempts_each_fixed_query_and_marks_partial_result_unavailable(self) -> None:
        output_path = self.root / "research.json"
        mocked_results = [([self.valid_result("example.org", primary=False)]) for _ in range(2)]
        side_effect = [
            ("complete", mocked_results[0], None),
            ("complete", mocked_results[1], None),
            ("invalid_response", [], "unexpected_response_shape"),
        ]
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}), patch.object(
            research, "request_search", side_effect=side_effect
        ) as request:
            self.assertEqual(research.collect(output_path), 0)

        self.assertEqual(request.call_count, 3)
        self.assertEqual([call.args[0] for call in request.call_args_list], [item["query"] for item in research.SWEEPS])
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "unavailable")
        self.assertEqual([sweep["status"] for sweep in payload["sweeps"]], ["complete", "complete", "invalid_response"])
        self.assertEqual(payload["sweeps"][2]["error_code"], "unexpected_response_shape")
        self.assertNotIn("test-key", output_path.read_text(encoding="utf-8"))

    def test_request_search_rejects_malformed_provider_response(self) -> None:
        response = Mock()
        response.read.return_value = b'{"unexpected": []}'
        context = Mock()
        context.__enter__ = Mock(return_value=response)
        context.__exit__ = Mock(return_value=False)
        opener = Mock()
        opener.open.return_value = context

        with patch.object(research.urllib.request, "build_opener", return_value=opener):
            status, results, error_code = research.request_search("fixed query", "fixed scope", "test-key")

        self.assertEqual((status, results, error_code), ("invalid_response", [], "unexpected_response_shape"))

    def test_report_distinguishes_clean_audit_and_finding_audit(self) -> None:
        clean, clean_report, _ = self.render()
        self.assertEqual(clean["audit_state"], "clean")
        self.assertIn("Result: **CLEAN**", clean_report)

        finding, finding_report, _ = self.render(audit=self.audit_payload(total=2), audit_exit_code=1)
        self.assertEqual(finding["audit_state"], "findings")
        self.assertEqual(finding["vulnerability_total"], 2)
        self.assertIn("Result: **FINDINGS**", finding_report)

    def test_invalid_audit_payload_is_unavailable_and_never_reported_as_zero_findings(self) -> None:
        metadata, report, _ = self.render(audit={"metadata": {}}, audit_exit_code=1)

        self.assertEqual(metadata["audit_state"], "unavailable")
        self.assertIn("Result: **UNAVAILABLE**", report)
        self.assertIn("missing or invalid", report)

    def test_partial_research_does_not_create_candidate_tasks(self) -> None:
        payload = self.eligible_research_payload()
        payload["status"] = "unavailable"
        payload["sweeps"][2]["status"] = "unavailable"
        payload["sweeps"][2]["error_code"] = "http_503"

        metadata, report, _ = self.render(research_payload=payload)

        self.assertEqual(metadata["research_state"], "unavailable")
        self.assertEqual(metadata["candidate_count"], 0)
        self.assertIn("No candidate task is generated from partial research", report)

    def test_complete_research_with_unqualified_sources_creates_no_candidate(self) -> None:
        payload = self.eligible_research_payload()
        for sweep in payload["sweeps"]:
            sweep["results"] = [
                {
                    "title": "A revolutionary future",
                    "url": "https://example.org/post",
                    "domain": "example.org",
                    "published_date": None,
                    "snippet": "A game-changing idea with no reproducible test or technical evidence.",
                    "relevance_score": 0.9,
                    "primary_source_domain": False,
                    "evidence_terms": [],
                    "hype_terms": ["revolutionary", "game-changing"],
                }
            ]

        metadata, report, _ = self.render(research_payload=payload)

        self.assertEqual(metadata["research_state"], "complete")
        self.assertEqual(metadata["candidate_count"], 0)
        self.assertIn("No research sweep met the deterministic source, evidence, and corroboration requirements", report)
        self.assertIn("fewer than three usable results or fewer than two distinct source domains", report)

    def test_qualified_sweeps_create_only_provisional_report_candidates(self) -> None:
        original_backlog = self.backlog_path.read_bytes()

        metadata, report, _ = self.render()

        self.assertEqual(metadata["research_state"], "complete")
        self.assertEqual(metadata["candidate_count"], 3)
        self.assertIn("FW-TASK-015", report)
        self.assertIn("provisional proposal label", report)
        self.assertEqual(self.backlog_path.read_bytes(), original_backlog)

    def test_covered_template_probes_prevent_candidate_creation(self) -> None:
        coverage_terms = sorted(
            {
                term
                for definition in research.SWEEPS
                for probe in definition["coverage_probes"]
                for term in probe["terms"]
            }
        )
        (self.root / "docs/coverage.md").write_text(" ".join(coverage_terms), encoding="utf-8")

        metadata, report, _ = self.render()

        self.assertEqual(metadata["candidate_count"], 0)
        self.assertIn("all predefined template coverage probes were found", report)

    def test_template_coverage_inventory_excludes_application_source(self) -> None:
        source = self.root / "src"
        source.mkdir()
        (source / "secret-contract.md").write_text("EARS requirement-to-journey", encoding="utf-8")
        inventory = research.template_inventory(self.root)

        self.assertFalse(any(path.startswith("src/") for path, _ in inventory))
        self.assertFalse(any(path == "scripts/architecture_research.py" for path, _ in inventory))
        comparison = research.compare_template_tree(research.SWEEPS[0], inventory)
        self.assertEqual(comparison["probes"][0]["state"], "not_found")

    def test_normalizer_rejects_non_https_credentials_and_hype_is_penalized(self) -> None:
        normalized = research.normalize_results(
            [
                {"url": "http://example.org/a", "title": "HTTP", "content": "documentation test"},
                {"url": "https://user:pass@example.org/a", "title": "Auth", "content": "documentation test"},
                {
                    "url": "https://docs.github.com/guide",
                    "title": "Revolutionary system",
                    "content": "A game-changing architecture evaluation test.",
                    "published_date": "2026-10-01",
                    "score": 0.8,
                },
            ]
        )

        self.assertEqual(len(normalized), 1)
        self.assertEqual(normalized[0]["domain"], "docs.github.com")
        self.assertEqual(normalized[0]["hype_terms"], ["revolutionary", "game-changing"])
        score, reasons = research.score_result(normalized[0], corroborated=False, today=date(2026, 10, 13))
        self.assertEqual(score, 5)
        self.assertIn("promotional or hype language penalty", reasons)


if __name__ == "__main__":
    unittest.main()
