#!/usr/bin/env python3
"""Collect and render bounded weekly architecture-governance research.

The collector sends only the fixed, public research questions to Tavily. Search
results are treated as untrusted evidence: they are never executed, followed as
instructions, or fetched directly. The renderer applies deterministic evidence
rules and writes a human-review report; it does not edit the framework backlog
or application source.
"""

from __future__ import annotations

import argparse
from email.utils import parsedate_to_datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


API_URL = "https://api.tavily.com/search"
MAX_RESPONSE_BYTES = 1_048_576
MAX_RESULT_COUNT = 6
MAX_TITLE_LENGTH = 240
MAX_SNIPPET_LENGTH = 700
MAX_URL_LENGTH = 2_048
MAX_TEMPLATE_FILES = 400
MAX_TEMPLATE_FILE_BYTES = 512_000
REQUEST_TIMEOUT_SECONDS = 30
MAX_ATTEMPTS = 3

SWEEPS = (
    {
        "key": "sdd",
        "query": "What are the latest emergent tools and best practices in Spec-Driven Development (SDD) in 2026?",
        "search_scope": "Prioritize EARS requirements notation, executable specification tooling, current technical documentation, and reproducible evaluations.",
        "task_title": "Evaluate evidence-backed SDD practices for template applicability",
        "task_objective": "Determine whether a documented, reproducible SDD practice should be adopted by this template.",
        "task_work": (
            "Inspect the cited primary material and independent corroboration; map the proposed practice to the existing "
            "SDD artifacts and gates; identify compatibility, maintenance, and security costs; build a focused positive and "
            "negative fixture for any proposed machine-checkable contract."
        ),
        "coverage_probes": (
            {"name": "EARS requirements notation", "terms": ("ears",)},
            {"name": "explicit requirement-to-acceptance traceability", "terms": ("requirement-to-journey", "traceability", "traceable")},
            {"name": "testable acceptance criteria", "terms": ("acceptance criteria", "testable outcome")},
        ),
    },
    {
        "key": "context-engineering",
        "query": "What agentic design patterns are premier tech organizations leveraging to mitigate context decay and prompt drift on long-horizon tasks?",
        "search_scope": "Include official Cursor and Claude Code system structures or documentation where relevant; focus on context compaction, repository instruction hierarchy, retrieval, and long-horizon persistence.",
        "task_title": "Evaluate long-horizon agent context-control patterns",
        "task_objective": "Assess whether a source-backed context-management control reduces drift or recovery failures in long-running work.",
        "task_work": (
            "Inspect primary technical documentation or reproducible evaluation evidence and an independent corroborating source; "
            "map the control to this repository's session-start, artifact, and gate contracts; define observable failure and recovery "
            "signals; prototype a bounded fixture before recommending adoption."
        ),
        "coverage_probes": (
            {"name": "session continuity and handoff", "terms": ("session start", "handoff")},
            {"name": "context compaction and retrieval", "terms": ("compaction", "retrieval")},
            {"name": "prompt or instruction drift controls", "terms": ("prompt drift", "instruction hierarchy")},
        ),
    },
    {
        "key": "multi-agent-state",
        "query": "Are there structural updates or security flaws identified in modern multi-agent state execution loops?",
        "search_scope": "Focus on state integrity, authorization boundaries, orchestration security advisories, and reproducible tests or benchmarks.",
        "task_title": "Assess multi-agent state execution security controls",
        "task_objective": "Determine whether a documented security or state-integrity control warrants a framework change.",
        "task_work": (
            "Inspect primary advisories, specifications, technical documentation, or reproducible tests and independent corroboration; "
            "map the threat to agent identity, state transitions, tool permissions, and durable artifacts; propose a minimal adversarial "
            "fixture with an explicit expected rejection or recovery outcome."
        ),
        "coverage_probes": (
            {"name": "agent state transition integrity", "terms": ("state transition", "state machine")},
            {"name": "agent tool permission boundaries", "terms": ("least privilege", "tool permissions", "tool permission")},
            {"name": "multi-agent execution coordination", "terms": ("multi-agent", "agent orchestration")},
        ),
    },
)

PRIMARY_DOMAINS = (
    "anthropic.com",
    "arxiv.org",
    "aclanthology.org",
    "cursor.com",
    "github.blog",
    "docs.github.com",
    "openai.com",
    "developers.openai.com",
    "platform.openai.com",
    "nist.gov",
    "owasp.org",
    "mitre.org",
    "usenix.org",
    "acm.org",
    "ieee.org",
    "ietf.org",
)

EVIDENCE_TERMS = (
    "benchmark",
    "evaluation",
    "dataset",
    "reproduc",
    "test",
    "schema",
    "contract",
    "standard",
    "security",
    "cve-",
    "vulnerability",
    "threat model",
    "architecture",
    "state machine",
    "release notes",
    "documentation",
    "api",
    "formal",
    "experiment",
    "ablation",
    "failure mode",
    "trace",
    "checkpoint",
    "specification",
)

HYPE_TERMS = (
    "revolutionary",
    "game-changing",
    "game changer",
    "world's first",
    "world’s first",
    "unprecedented",
    "ultimate",
    "magic",
    "10x",
    "100x",
)


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Do not forward a bearer token to an API-provided redirect destination."""

    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def safe_text(value: Any, limit: int) -> str:
    if not isinstance(value, str):
        return ""
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace("|", "¦").replace("`", "ʼ")
    value = value.replace("[", "（").replace("]", "）")
    value = value.replace("<", "‹").replace(">", "›")
    value = value.replace("\\", "／")
    return value[:limit]


def safe_source_url(value: Any) -> tuple[str, str] | None:
    if not isinstance(value, str) or not value or len(value) > MAX_URL_LENGTH:
        return None
    try:
        parsed = urllib.parse.urlsplit(value)
        if parsed.scheme.lower() != "https" or not parsed.hostname:
            return None
        if parsed.username is not None or parsed.password is not None:
            return None
        if parsed.port not in (None, 443):
            return None
        hostname = parsed.hostname.encode("idna").decode("ascii").lower().rstrip(".")
    except (UnicodeError, ValueError):
        return None
    normalized = urllib.parse.urlunsplit(("https", hostname + (f":{parsed.port}" if parsed.port else ""), parsed.path, parsed.query, ""))
    normalized = urllib.parse.quote(normalized, safe=":/?#@!$&'()*+,;=%")
    return normalized, hostname


def is_primary_domain(hostname: str) -> bool:
    return any(hostname == domain or hostname.endswith("." + domain) for domain in PRIMARY_DOMAINS)


def published_date(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip()
    try:
        return date.fromisoformat(candidate[:10]).isoformat()
    except ValueError:
        try:
            return parsedate_to_datetime(candidate).date().isoformat()
        except (TypeError, ValueError, OverflowError):
            return None


def request_search(query: str, search_scope: str, api_key: str) -> tuple[str, list[dict[str, Any]], str | None]:
    payload = json.dumps(
        {
            "query": f"{query} {search_scope}",
            "topic": "general",
            "search_depth": "basic",
            "chunks_per_source": 1,
            "time_range": "month",
            "max_results": MAX_RESULT_COUNT,
            "include_published_date": True,
            "filter_by_published_date": False,
            "include_answer": False,
            "include_raw_content": False,
        },
        separators=(",", ":"),
    ).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "adversarial-sdd-weekly-governance/1.0",
        },
        method="POST",
    )
    opener = urllib.request.build_opener(NoRedirectHandler)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with opener.open(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                return "invalid_response", [], "response_too_large"
            decoded = json.loads(raw.decode("utf-8"))
            if not isinstance(decoded, dict) or not isinstance(decoded.get("results"), list):
                return "invalid_response", [], "unexpected_response_shape"
            return "complete", normalize_results(decoded["results"]), None
        except urllib.error.HTTPError as error:
            status = int(error.code)
            if status in (429, 500, 502, 503, 504) and attempt < MAX_ATTEMPTS:
                delay_header = error.headers.get("Retry-After", "") if error.headers else ""
                try:
                    delay = min(max(int(delay_header), 1), 4)
                except (TypeError, ValueError):
                    delay = min(2**(attempt - 1), 4)
                time.sleep(delay)
                continue
            return "unavailable", [], f"http_{status}"
        except (TimeoutError, urllib.error.URLError):
            if attempt < MAX_ATTEMPTS:
                time.sleep(min(2**(attempt - 1), 4))
                continue
            return "unavailable", [], "network_or_timeout_error"
        except (UnicodeDecodeError, json.JSONDecodeError):
            return "invalid_response", [], "invalid_json"
        except OSError:
            if attempt < MAX_ATTEMPTS:
                time.sleep(min(2**(attempt - 1), 4))
                continue
            return "unavailable", [], "transport_error"
    return "unavailable", [], "retry_limit_reached"


def normalize_results(results: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for result in results[:MAX_RESULT_COUNT]:
        if not isinstance(result, dict):
            continue
        safe_url = safe_source_url(result.get("url"))
        if safe_url is None:
            continue
        url, domain = safe_url
        title = safe_text(result.get("title"), MAX_TITLE_LENGTH)
        snippet = safe_text(result.get("content"), MAX_SNIPPET_LENGTH)
        if not title or not snippet:
            continue
        combined = f"{title} {snippet}".lower()
        evidence = [term for term in EVIDENCE_TERMS if term in combined]
        hype = [term for term in HYPE_TERMS if term in combined]
        score_value = result.get("score")
        try:
            relevance_score = round(float(score_value), 4)
        except (TypeError, ValueError):
            relevance_score = None
        if relevance_score is not None and not 0 <= relevance_score <= 1:
            relevance_score = None
        normalized.append(
            {
                "title": title,
                "url": url,
                "domain": domain,
                "published_date": published_date(result.get("published_date")),
                "snippet": snippet,
                "relevance_score": relevance_score,
                "primary_source_domain": is_primary_domain(domain),
                "evidence_terms": evidence,
                "hype_terms": hype,
            }
        )
    return normalized


def collect(output_path: Path) -> int:
    api_key = os.environ.get("TAVILY_API_KEY", "").strip()
    credential_error = bool(api_key) and (len(api_key) > 4_096 or any(ord(character) < 33 or ord(character) > 126 for character in api_key))
    collected_at = utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")
    sweeps: list[dict[str, Any]] = []

    for sweep in SWEEPS:
        if credential_error:
            status, results, error_code = "unavailable", [], "invalid_api_key_configuration"
        elif not api_key:
            status, results, error_code = "unavailable", [], "missing_api_key"
        else:
            status, results, error_code = request_search(sweep["query"], sweep["search_scope"], api_key)
        sweeps.append(
            {
                "key": sweep["key"],
                "query": sweep["query"],
                "search_scope": sweep["search_scope"],
                "provider_query": f"{sweep['query']} {sweep['search_scope']}",
                "status": status,
                "error_code": error_code,
                "results": results,
            }
        )

    state = "complete" if all(sweep["status"] == "complete" for sweep in sweeps) else "unavailable"
    output = {
        "schema_version": 1,
        "provider": "Tavily Search API",
        "collected_at": collected_at,
        "time_range": "month",
        "status": state,
        "sweeps": sweeps,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Research collection state: {state}; completed sweeps: {sum(s['status'] == 'complete' for s in sweeps)}/3")
    return 0


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def score_result(result: dict[str, Any], corroborated: bool, today: date) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    if result.get("primary_source_domain"):
        score += 4
        reasons.append("primary technical, standards, security, or vendor source")
    source_date = result.get("published_date")
    if source_date:
        try:
            age_days = (today - date.fromisoformat(source_date)).days
            if 0 <= age_days <= 180:
                score += 2
                reasons.append("dated within 180 days")
            elif 181 <= age_days <= 365:
                score += 1
                reasons.append("dated within 365 days")
        except ValueError:
            pass
    if result.get("evidence_terms"):
        score += 2
        reasons.append("contains a concrete technical evidence indicator")
    if corroborated:
        score += 2
        reasons.append("corroborated by a distinct source domain")
    hype = result.get("hype_terms") or []
    if hype:
        score -= 3
        reasons.append("promotional or hype language penalty")
    return score, reasons


def template_inventory(repository_root: Path) -> list[tuple[str, str]]:
    allowed_roots = ("docs", "framework", "workflows", "scripts", ".github/workflows")
    allowed_root_files = ("AGENTS.md", "README.md")
    candidate_paths: set[Path] = {repository_root / name for name in allowed_root_files}
    for relative_root in allowed_roots:
        directory = repository_root / relative_root
        if directory.is_dir():
            candidate_paths.update(directory.rglob("*"))

    inventory: list[tuple[str, str]] = []
    for path in sorted(candidate_paths, key=lambda item: item.as_posix()):
        if len(inventory) >= MAX_TEMPLATE_FILES:
            break
        if not path.is_file() or path.is_symlink():
            continue
        if path.suffix.lower() not in {".md", ".py", ".yml", ".yaml", ".json", ".toml"}:
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if len(raw) > MAX_TEMPLATE_FILE_BYTES:
            continue
        try:
            relative = path.relative_to(repository_root).as_posix()
        except ValueError:
            continue
        if relative.startswith("src/") or relative == "scripts/architecture_research.py":
            continue
        inventory.append((relative, raw.decode("utf-8", errors="replace").lower()))
    return inventory


def compare_template_tree(sweep_definition: dict[str, Any], inventory: list[tuple[str, str]]) -> dict[str, Any]:
    probes: list[dict[str, Any]] = []
    for probe in sweep_definition["coverage_probes"]:
        matches = [
            path
            for path, content in inventory
            if any(term in content for term in probe["terms"])
        ]
        probes.append(
            {
                "name": probe["name"],
                "state": "found" if matches else "not_found",
                "matched_paths": matches[:8],
                "match_count": len(matches),
            }
        )
    return {
        "probes": probes,
        "missing_controls": [probe["name"] for probe in probes if probe["state"] == "not_found"],
    }


def evaluate_sweep(
    sweep: dict[str, Any],
    today: date,
    tree_comparison: dict[str, Any],
) -> dict[str, Any]:
    results = sweep.get("results", []) if isinstance(sweep.get("results"), list) else []
    domains = {result.get("domain") for result in results if result.get("domain")}
    for result in results:
        result["score"], result["score_reasons"] = score_result(result, len(domains) >= 2, today)
    primary_evidence = any(
        result.get("primary_source_domain") and result.get("evidence_terms") and result.get("score", 0) >= 6
        for result in results
    )
    primary_domains = {
        result.get("domain")
        for result in results
        if result.get("primary_source_domain") and result.get("evidence_terms") and result.get("score", 0) >= 6
    }
    independent_evidence = any(
        result.get("domain") not in primary_domains
        and result.get("evidence_terms")
        and not result.get("hype_terms")
        and result.get("score", 0) >= 4
        for result in results
    )
    template_gap = bool(tree_comparison.get("missing_controls"))
    enough_sources = len(results) >= 3 and len(domains) >= 2
    eligible = bool(
        sweep.get("status") == "complete"
        and enough_sources
        and primary_evidence
        and independent_evidence
        and template_gap
    )
    if sweep.get("status") != "complete":
        reason = f"sweep unavailable ({sweep.get('error_code') or 'unknown error'})"
    elif not enough_sources:
        reason = "fewer than three usable results or fewer than two distinct source domains"
    elif not primary_evidence:
        reason = "no primary source with concrete evidence met the score threshold"
    elif not independent_evidence:
        reason = "no independent source with concrete, non-promotional evidence met the threshold"
    elif not template_gap:
        reason = "all predefined template coverage probes were found; no candidate gap was detected"
    else:
        reason = "passed source diversity, primary evidence, corroboration, score, and template-gap checks"
    return {
        "eligible": eligible,
        "reason": reason,
        "source_domains": sorted(domains),
        "tree_comparison": tree_comparison,
    }


def next_candidate_number(backlog_path: Path) -> int | None:
    try:
        backlog = backlog_path.read_text(encoding="utf-8")
    except OSError:
        return None
    identifiers = [int(match) for match in re.findall(r"\bFW-TASK-(\d{3})\b", backlog)]
    return max(identifiers, default=0) + 1


def markdown_cell(value: str) -> str:
    return value.replace("|", "¦").replace("\n", " ")


def render_report(
    audit_path: Path,
    audit_exit_code: int,
    research_path: Path,
    report_path: Path,
    backlog_path: Path,
    run_id: str,
    run_attempt: str,
    source_sha: str,
) -> dict[str, Any]:
    audit_payload = load_json(audit_path)
    research_payload = load_json(research_path)
    audit_metadata = audit_payload.get("metadata", {}) if isinstance(audit_payload, dict) else {}
    raw_vulnerabilities = audit_metadata.get("vulnerabilities") if isinstance(audit_metadata, dict) else None
    raw_dependencies = audit_metadata.get("dependencies") if isinstance(audit_metadata, dict) else None
    severity_names = ("info", "low", "moderate", "high", "critical", "total")
    dependency_names = ("prod", "dev", "optional", "peer", "total")
    try:
        if not isinstance(raw_vulnerabilities, dict) or not isinstance(raw_dependencies, dict):
            raise ValueError("npm audit summary objects are absent")
        if not all(type(raw_vulnerabilities.get(name)) is int and raw_vulnerabilities[name] >= 0 for name in severity_names):
            raise ValueError("npm audit vulnerability counts are malformed")
        if not all(type(raw_dependencies.get(name)) is int and raw_dependencies[name] >= 0 for name in dependency_names):
            raise ValueError("npm audit dependency counts are malformed")
        vulnerabilities = {name: raw_vulnerabilities[name] for name in severity_names}
        dependencies = {name: raw_dependencies[name] for name in dependency_names}
        audit_valid = True
    except (TypeError, ValueError, AttributeError):
        vulnerabilities = {name: 0 for name in severity_names}
        dependencies = {name: 0 for name in dependency_names}
        audit_valid = False
    if audit_valid and vulnerabilities["total"] == 0 and audit_exit_code == 0:
        audit_state = "clean"
    elif audit_valid and vulnerabilities["total"] > 0:
        audit_state = "findings"
    else:
        audit_state = "unavailable"

    now = utc_now()
    report_date = now.date().isoformat()
    artifact_id = f"ARCH-AUDIT-{run_id}-{run_attempt}-001"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if not isinstance(research_payload, dict) or research_payload.get("schema_version") != 1:
        research_payload = {"status": "unavailable", "provider": "Tavily Search API", "collected_at": None, "sweeps": []}
    raw_sweeps = research_payload.get("sweeps", [])
    sweep_map = {sweep.get("key"): sweep for sweep in raw_sweeps if isinstance(sweep, dict)} if isinstance(raw_sweeps, list) else {}
    evaluations: dict[str, dict[str, Any]] = {}
    repository_root = backlog_path.resolve().parents[2]
    inventory = template_inventory(repository_root)
    for definition in SWEEPS:
        sweep = sweep_map.get(definition["key"], {"key": definition["key"], "query": definition["query"], "status": "unavailable", "error_code": "missing_sweep", "results": []})
        if not isinstance(sweep.get("results"), list):
            sweep["results"] = []
        comparison = compare_template_tree(definition, inventory)
        evaluations[definition["key"]] = evaluate_sweep(sweep, now.date(), comparison)

    research_state = "complete" if research_payload.get("status") == "complete" and all(
        sweep_map.get(definition["key"], {}).get("status") == "complete" for definition in SWEEPS
    ) else "unavailable"

    candidate_start = next_candidate_number(backlog_path)
    candidates: list[dict[str, Any]] = []
    if research_state == "complete" and candidate_start is not None:
        for definition in SWEEPS:
            evaluation = evaluations[definition["key"]]
            if evaluation["eligible"]:
                candidates.append(
                    {
                        "id": f"FW-TASK-{candidate_start + len(candidates):03d}",
                        "definition": definition,
                        "evaluation": evaluation,
                        "sweep": sweep_map[definition["key"]],
                    }
                )

    def counts_table(values: dict[str, int]) -> str:
        return "\n".join(f"| {name} | {value} |" for name, value in values.items())

    def sources_for(sweep: dict[str, Any]) -> str:
        results = sweep.get("results", [])
        if not results:
            code = sweep.get("error_code") or "no_usable_results"
            return f"No usable sources were retained. Sweep state: `{sweep.get('status', 'unavailable')}`; diagnostic code: `{code}`."
        lines: list[str] = []
        for result in results:
            score = result.get("score", 0)
            reasons = "; ".join(result.get("score_reasons", [])) or "no qualifying evidence indicators"
            pubdate = result.get("published_date") or "publication date not supplied"
            relevance = result.get("relevance_score")
            relevance_label = relevance if relevance is not None else "not supplied"
            primary_label = "primary-source domain" if result.get("primary_source_domain") else "independent source"
            lines.append(
                f"- [{result['title']}](<{result['url']}>) — `{result['domain']}`; {primary_label}; provider relevance: {relevance_label}; date: {pubdate}; "
                f"score: {score}; {markdown_cell(reasons)}.\n  - Search excerpt (untrusted): {result['snippet']}"
            )
        return "\n".join(lines)

    sections: list[str] = []
    for definition in SWEEPS:
        sweep = sweep_map.get(definition["key"], {"status": "unavailable", "error_code": "missing_sweep", "results": []})
        if not isinstance(sweep.get("results"), list):
            sweep["results"] = []
        evaluation = evaluations[definition["key"]]
        result_count = len(sweep["results"])
        coverage_rows = []
        for probe in evaluation["tree_comparison"]["probes"]:
            match_text = ", ".join(f"`{path}`" for path in probe["matched_paths"]) or "no lexical match"
            coverage_rows.append(f"  - {probe['name']}: **{probe['state'].replace('_', ' ')}**; {match_text}")
        sections.append(
            f"### {definition['key']} research sweep\n\n"
            f"- Required query: “{definition['query']}”\n"
            f"- Search focus: {definition['search_scope']}\n"
            f"- Provider query sent: “{safe_text(sweep.get('provider_query', definition['query'] + ' ' + definition['search_scope']), 600)}”\n"
            f"- Result: **{sweep.get('status', 'unavailable').upper()}**\n"
            f"- Usable results: `{result_count}`\n"
            f"- Distinct source domains: `{len(evaluation['source_domains'])}`\n"
            f"- Adversarial filter: **{'QUALIFIED FOR A TASK DRAFT' if evaluation['eligible'] else 'NO TASK DRAFT'}** — {evaluation['reason']}.\n\n"
            "- Template-tree coverage probes (lexical only; no semantic adoption claim):\n"
            f"{chr(10).join(coverage_rows)}\n\n"
            f"{sources_for(sweep)}"
        )

    if candidates:
        task_sections = []
        for candidate in candidates:
            definition = candidate["definition"]
            task_sections.append(
                f"### {candidate['id']} — {definition['task_title']}\n\n"
                "- **Status:** Proposed; human review required; not yet part of the canonical backlog.\n"
                f"- **Objective:** {definition['task_objective']}\n"
                f"- **Evidence:** Research sweep `{definition['key']}`; see the linked sources above and the source revision in this record.\n"
                f"- **Work:** {definition['task_work']}\n"
                "- **Acceptance criteria:**\n"
                "  1. Verify the primary source and independently corroborating evidence; record exact URLs, dates, and any material limitations.\n"
                "  2. Map the claimed control or practice to an existing framework requirement, capability, workflow, or explicit gap.\n"
                "  3. Define a reproducible positive and negative fixture or other objective verification appropriate to the claim.\n"
                "  4. Preserve least privilege, repository boundaries, existing gate contracts, and human decision authority.\n"
                "  5. Record an explicit adopt, defer, or reject decision with evidence; do not promote an unsupported trend.\n"
                f"- **Source report:** `{artifact_id}`.\n"
                f"- **ID handling:** `{candidate['id']}` is a provisional proposal label allocated from the checked-out backlog snapshot. Reconcile it against the current canonical backlog before accepting the task."
            )
        proposals_section = "\n\n".join(task_sections)
    elif research_state != "complete":
        proposals_section = "The mandatory research set is incomplete or unavailable. No candidate task is generated from partial research."
    elif candidate_start is None:
        proposals_section = "The required framework backlog could not be read, so no candidate identifier was allocated and no task draft was generated."
    else:
        proposals_section = "No research sweep met the deterministic source, evidence, and corroboration requirements. No task draft was generated."

    content = f"""---
id: {artifact_id}
type: architecture-audit
title: Weekly dependency and strategic R&D audit {report_date} run {run_id}
status: draft
version: 0.2
created: {report_date}
updated: {report_date}
related-artifacts: FRAMEWORK-BACKLOG-001, CAP-005
---

# {artifact_id} — Weekly dependency and strategic R&D audit

## Scope and provenance

- Audit time (UTC): {now.strftime('%Y-%m-%dT%H:%M:%SZ')}
- Source revision: `{source_sha}`
- Workflow run: `{run_id}`, attempt `{run_attempt}`
- This record combines the locked npm dependency audit with three time-bounded engineering research sweeps.
- The research provider is Tavily Search API. Its API credential is supplied as a GitHub Actions secret to the collection step only; no credential or provider response headers are stored in this record.
- The workflow reads search result titles, HTTPS URLs, publication dates, and bounded excerpts. Search excerpts are untrusted external data and are never interpreted as instructions, executed, or fetched directly by this workflow.
- A provider-reported publication date is an estimated publish or last-updated date, can be absent or later than the original publication, and is used only as a recency signal; it is not verified source metadata.

## Locked dependency audit

- Scanner: `npm audit --json`
- Input: committed `package-lock.json`, restored with `npm ci`
- Result: **{audit_state.upper()}**
- npm audit process exit code: `{audit_exit_code}`

| Dependency class | Count |
| --- | ---: |
{counts_table(dependencies)}

| Vulnerability severity | Count |
| --- | ---: |
{counts_table(vulnerabilities)}

{('The scanner reported one or more vulnerabilities. This record proposes human triage and does not update dependencies.' if audit_state == 'findings' else 'The scan output was missing or invalid. Treat this state as unavailable, never as clean.' if audit_state == 'unavailable' else 'The scanner completed and reported no known vulnerabilities within this lockfile audit scope.')}

## Strategic R&D research

- Research result: **{research_state.upper()}**
- Collection time (UTC): `{research_payload.get('collected_at') or 'unavailable'}`
- Freshness window requested from the provider: latest month
- Completed required sweeps: `{sum(sweep_map.get(definition['key'], {}).get('status') == 'complete' for definition in SWEEPS)}/3`
- Candidate task drafts: `{len(candidates)}`
- The report uses deterministic screening rules. It does not claim semantic understanding or an AI-generated architectural judgment.

### Adversarial filter and scoring contract

A sweep qualifies for a candidate task only when all required sweeps completed, its individual sweep contains at least three usable HTTPS sources across at least two distinct domains, at least one allowlisted primary technical/standards/security/vendor source with a concrete evidence indicator and score of at least 6, at least one independent domain with a concrete non-promotional evidence indicator and score of at least 4, and at least one predefined topic-specific template-coverage probe is not found. Scores add 4 for an allowlisted primary domain, 2 for a source date within 180 days (1 within 365 days), 2 for a concrete evidence indicator, and 2 for distinct-domain corroboration; a recognized promotional phrase subtracts 3. The tree comparison searches only the framework's README/AGENTS, documentation, capabilities, workflows, CI workflows, and helper scripts. It reports matched paths and missing lexical markers; it excludes `/src` and does not claim semantic understanding. This mechanical screen is conservative and explainable, not a substitute for human source review. It can miss relevant work or admit weak sources; maintainers must check evidence before accepting a proposal.

Evidence indicators include benchmark, evaluation, dataset, reproducibility, test, schema, contract, standard, security/advisory, vulnerability, threat model, architecture, state machine, release notes, documentation, API, formal method, experiment, failure mode, trace, checkpoint, or specification. Promotional language reduces the source score. Search results do not become findings solely because the provider returned them.

{chr(10).join(sections)}

## Traceable candidate backlog templates

{proposals_section}

Candidate tasks in this report are recommendations only. The daemon does not append them to `docs/framework/FRAMEWORK-BACKLOG-001.md`; maintainers must verify source claims, reconcile candidate identifiers, accept or reject the proposal, and make any canonical backlog change through a separate reviewed action.

## Proposed operator action

Review this combined record and the linked workflow run. Triage dependency findings in an independently reviewed change. For each research proposal, open the primary and corroborating sources, verify dates and claims, assess applicability and maintenance/security costs, and accept, defer, or reject it explicitly. If either scanner or one of the mandatory research sweeps is unavailable, restore that service and rerun before treating this week's governance observation as complete.

## Decision and safety status

This is a draft evidence and proposal record awaiting human review. It is not a complete security assessment, a full architecture review, an accepted backlog change, or a production-readiness claim. The workflow does not modify `/src`, application or product logic, manifests, lockfiles, prior records, backlog policy, deployment settings, or repository settings, and it never auto-merges.
"""
    with report_path.open("w", encoding="utf-8", newline="\n") as report_file:
        report_file.write(content)
    return {
        "artifact_id": artifact_id,
        "audit_state": audit_state,
        "research_state": research_state,
        "candidate_count": len(candidates),
        "vulnerability_total": vulnerabilities["total"],
        "report_path": report_path.as_posix(),
        "report_date": report_date,
    }


def render_command(args: argparse.Namespace) -> int:
    metadata = render_report(
        audit_path=Path(args.audit_json),
        audit_exit_code=args.audit_exit_code,
        research_path=Path(args.research_json),
        report_path=Path(args.report_path),
        backlog_path=Path(args.backlog_path),
        run_id=args.run_id,
        run_attempt=args.run_attempt,
        source_sha=args.source_sha,
    )
    result_path = Path(args.outputs_json)
    result_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Compiled combined governance report {metadata['artifact_id']} ({metadata['audit_state']}; research {metadata['research_state']}; {metadata['candidate_count']} task drafts).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    collect_parser = subparsers.add_parser("collect", help="run the three fixed Tavily research queries")
    collect_parser.add_argument("--output", required=True, help="path for bounded, normalized research JSON")
    render_parser = subparsers.add_parser("render", help="combine npm audit and research evidence into one report")
    render_parser.add_argument("--audit-json", required=True)
    render_parser.add_argument("--audit-exit-code", required=True, type=int)
    render_parser.add_argument("--research-json", required=True)
    render_parser.add_argument("--report-path", required=True)
    render_parser.add_argument("--backlog-path", default="docs/framework/FRAMEWORK-BACKLOG-001.md")
    render_parser.add_argument("--run-id", required=True)
    render_parser.add_argument("--run-attempt", required=True)
    render_parser.add_argument("--source-sha", required=True)
    render_parser.add_argument("--outputs-json", required=True)
    args = parser.parse_args()
    if args.command == "collect":
        return collect(Path(args.output))
    return render_command(args)


if __name__ == "__main__":
    sys.exit(main())
