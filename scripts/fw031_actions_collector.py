"""Passively collect bounded GitHub Actions run/job evidence; never mutate a run or gate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from urllib.request import HTTPRedirectHandler, build_opener
from datetime import datetime, timezone
from typing import Any, Callable

_API = "https://api.github.com"
_PAGE_SIZE = 100
_MAX_PAGES = 5
_MAX_RETRIES = 3
_RETRYABLE = {429, 500, 502, 503, 504}
_SHA = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
class _RejectRedirects(HTTPRedirectHandler):
    """Never forward a caller credential to a redirect target."""

    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


_DEFAULT_OPENER = build_opener(_RejectRedirects()).open
_SECRET_PATTERNS = (
    re.compile(r"(?i)\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"(?i)\bBearer\s+\S+"),
)


class CollectionError(Exception):
    """Safe, value-free acquisition failure."""

    def __init__(self, code: str, status: int | None = None):
        super().__init__(code)
        self.code = code
        self.status = status


class ActionsApi:
    """Read-only, bounded GitHub Actions REST client with injectable transport."""

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = _API,
        max_pages: int = _MAX_PAGES,
        max_retries: int = _MAX_RETRIES,
        timeout: float = 10.0,
        opener: Callable[..., Any] | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if not 1 <= max_pages <= _MAX_PAGES or not 0 <= max_retries <= _MAX_RETRIES:
            raise ValueError("collection bounds exceed the reviewed maximum")
        if not 0 < timeout <= 30:
            raise ValueError("request timeout must be between 0 and 30 seconds")
        parsed_base = urllib.parse.urlsplit(base_url)
        if (parsed_base.scheme != "https" or parsed_base.netloc != "api.github.com"
                or parsed_base.username or parsed_base.password or parsed_base.path not in {"", "/"}
                or parsed_base.query or parsed_base.fragment):
            raise ValueError("only the GitHub API HTTPS origin is supported")
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._max_pages = max_pages
        self._max_retries = max_retries
        self._timeout = timeout
        self._opener = opener or _DEFAULT_OPENER
        # Any injected transport is a test seam; it can never produce observed evidence.
        self._fixture_only = opener is not None
        self._sleep = sleeper

    def get_json(self, path: str, query: dict[str, str] | None = None) -> tuple[dict[str, Any], bytes, str | None]:
        url = self._base_url + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self._token:
            headers["Authorization"] = "Bearer " + self._token
        request = urllib.request.Request(url, headers=headers, method="GET")
        for attempt in range(self._max_retries + 1):
            try:
                with self._opener(request, timeout=self._timeout) as response:
                    status = getattr(response, "status", 200)
                    if status < 200 or status >= 300:
                        raise CollectionError("http-error", status)
                    raw = response.read(2 * 1024 * 1024 + 1)
                    if len(raw) > 2 * 1024 * 1024:
                        raise CollectionError("response-too-large")
                    try:
                        value = json.loads(raw.decode("utf-8"))
                    except (UnicodeError, json.JSONDecodeError):
                        raise CollectionError("invalid-json") from None
                    if not isinstance(value, dict):
                        raise CollectionError("invalid-response-shape")
                    etag = response.headers.get("ETag") if getattr(response, "headers", None) else None
                    return value, raw, _safe_text(etag, self._token, 255) if etag else None
            except urllib.error.HTTPError as exc:
                if exc.code not in _RETRYABLE or attempt >= self._max_retries:
                    raise CollectionError("http-error", exc.code) from None
                self._sleep(_retry_delay(exc.headers.get("Retry-After") if exc.headers else None))
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                status = getattr(exc, "code", None)
                if status is not None and status not in _RETRYABLE:
                    raise CollectionError("http-error", status) from None
                if attempt >= self._max_retries:
                    raise CollectionError("network-unavailable", status) from None
                self._sleep(0.25 * (attempt + 1))
        raise CollectionError("network-unavailable")

    def collect(self, repository: str, run_id: int, run_attempt: int) -> dict[str, Any]:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) or any(
            segment in {".", ".."} for segment in repository.split("/")
        ):
            raise ValueError("repository must be owner/name")
        if run_id < 1 or run_attempt < 1:
            raise ValueError("run and attempt identifiers must be positive")
        repo = urllib.parse.quote(repository, safe="/")
        root = f"/repos/{repo}"
        run_path = f"{root}/actions/runs/{run_id}/attempts/{run_attempt}"
        run, run_bytes, run_etag = self.get_json(run_path)
        if run.get("id") != run_id or run.get("run_attempt") != run_attempt:
            raise CollectionError("run-identity-mismatch")
        run_repository = run.get("repository") if isinstance(run.get("repository"), dict) else {}
        run_repository_name = run_repository.get("full_name")
        if not isinstance(run_repository_name, str) or run_repository_name.casefold() != repository.casefold():
            raise CollectionError("repository-identity-mismatch")
        jobs: list[dict[str, Any]] = []
        page_digests: list[bytes] = [run_bytes]
        etags = [run_etag] if run_etag else []
        total: int | None = None
        pages_read = 0
        partial = False
        for page in range(1, self._max_pages + 1):
            query = {"per_page": str(_PAGE_SIZE), "page": str(page)}
            try:
                payload, raw, etag = self.get_json(f"{root}/actions/runs/{run_id}/attempts/{run_attempt}/jobs", query)
            except CollectionError:
                if page == 1:
                    raise
                partial = True
                break
            page_digests.append(raw)
            if etag:
                etags.append(etag)
            pages_read += 1
            rows = payload.get("jobs")
            if not isinstance(rows, list) or any(not isinstance(item, dict) for item in rows):
                raise CollectionError("invalid-jobs-shape")
            if total is None:
                total_value = payload.get("total_count")
                total = total_value if isinstance(total_value, int) and total_value >= 0 else None
            page_source = f"{self._base_url}{root}/actions/runs/{run_id}/attempts/{run_attempt}/jobs?per_page={_PAGE_SIZE}&page={page}"
            for item in rows:
                # The attempt-specific endpoint is authoritative; job objects omit run_attempt.
                if item.get("run_id") != run_id or (item.get("run_attempt") is not None and item.get("run_attempt") != run_attempt):
                    partial = True
                    continue
                item = dict(item)
                item["_collector_source_url"] = page_source
                jobs.append(item)
            if not rows or len(rows) < _PAGE_SIZE or (total is not None and len(jobs) >= total):
                break
        else:
            partial = total is None or len(jobs) < total
        if total is not None and len(jobs) < total:
            partial = True
        digest = "sha256:" + hashlib.sha256(b"\n".join(page_digests)).hexdigest()
        response_revision = ",".join(etags)[:255] or None
        observed_at = _now()
        repository_id = run_repository.get("id")
        repository_name = run_repository_name
        workflow_id = run.get("workflow_id") if isinstance(run.get("workflow_id"), int) else None
        raw_workflow_path = run.get("path") if isinstance(run.get("path"), str) else None
        # REST `path` is encoded as `<workflow-path>@<ref>`. Preserve the path
        # component; the ref suffix is not a fully qualified workflow_ref.
        workflow_path = raw_workflow_path.rsplit("@", 1)[0] if raw_workflow_path and "@" in raw_workflow_path else raw_workflow_path
        workflow_ref = run.get("workflow_ref") if isinstance(run.get("workflow_ref"), str) else None
        source_ref = _API + run_path
        source_state = "complete" if all(x is not None for x in (repository_id, repository_name, workflow_id, workflow_path, workflow_ref)) and not partial else "partial"
        records = [
            _project_record(
                run, job, repository_id, repository_name, workflow_id, workflow_path,
                workflow_ref, source_ref, observed_at, response_revision, digest,
                source_state,
                self._token, self._fixture_only,
            )
            for job in jobs
        ]
        return {
            "contract": "FRAMEWORK-CONTRACT-032",
            "schema_version": "1.0",
            "collection_state": "partial" if partial else "complete",
            "repository": repository,
            "run_id": run_id,
            "run_attempt": run_attempt,
            "pages_read": pages_read,
            "records": records,
            "limitations": ["workflow_ref-unavailable"] if workflow_ref is None else [],
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _retry_delay(raw: str | None) -> float:
    try:
        return min(2.0, max(0.0, float(raw))) if raw is not None else 0.25
    except (TypeError, ValueError):
        return 0.25


def _safe_text(value: Any, token: str | None, maximum: int) -> str | None:
    if not isinstance(value, str):
        return None
    result = value
    if token:
        result = result.replace(token, "[REDACTED]")
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    result = "".join(ch for ch in result if ch >= " " and ch != "\x7f")
    return result[:maximum] or None


def _revision(value: Any, source: str, token: str | None) -> dict[str, Any]:
    if isinstance(value, str) and _SHA.fullmatch(value):
        return {"state": "available", "value": value, "source": source}
    return {"state": "unknown", "value": None, "source": None}


def _point(value: Any, source: str, token: str | None) -> dict[str, Any]:
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is not None and parsed.utcoffset() is not None:
                return {"state": "available", "value": value, "source": source}
        except ValueError:
            pass
    return {"state": "unknown", "value": None, "source": None}


def _project_record(
    run: dict[str, Any], job: dict[str, Any], repository_id: Any, repository_name: str,
    workflow_id: Any, workflow_path: Any, workflow_ref: Any, source_ref: str,
    observed_at: str, response_revision: str | None, response_digest: str,
    acquisition_state: str, token: str | None, fixture_only: bool,
) -> dict[str, Any]:
    run_id, attempt, job_id = run["id"], run["run_attempt"], job.get("id")
    job_name = _safe_text(job.get("name"), token, 255)
    if not isinstance(job_id, int) or job_id < 1 or not job_name:
        raise CollectionError("job-identity-incomplete")
    run_source = source_ref
    job_source = _safe_text(job.get("_collector_source_url"), token, 2048) or source_ref
    run_finished_at = run.get("updated_at") if run.get("status") == "completed" else None
    run_timing = _interval(run_id, attempt, None, run.get("run_started_at"), run_finished_at, run_source, token)
    job_timing = _interval(run_id, attempt, job_id, job.get("started_at"), job.get("completed_at"), job_source, token)
    conclusion = job.get("conclusion")
    valid_conclusions = {"success", "failure", "cancelled", "skipped", "timed_out", "action_required"}
    host_conclusion = conclusion if conclusion in valid_conclusions else ("unknown" if job.get("status") != "completed" else "unknown")
    observed_timeout = "timed-out" if conclusion == "timed_out" else ("not-timed-out" if job.get("status") == "completed" and conclusion in valid_conclusions else "unknown")
    terminal = {"success": "completed", "failure": "failure", "cancelled": "cancelled", "timed_out": "timed_out"}.get(conclusion, "unknown")
    revisions = {
        "workflow": {"state": "unknown", "value": None, "source": None},
        "triggering": _revision(run.get("head_sha"), run_source, token),
        "executed": {"state": "unknown", "value": None, "source": None},
    }
    metrics = [
        {"name": name, "state": "unknown", "binding": {"run_id": run_id, "run_attempt": attempt, "job_id": job_id},
         "value": None, "unit": None, "source_kind": None, "source": None, "scope": None, "interval": None,
         "reason": "not-instrumented"}
        for name in ("tool_calls", "internal_retries", "nested_agents", "cpu_time", "memory_peak", "spend")
    ]
    limitations = ["metrics-unknown", "workload-termination-unobserved"]
    if acquisition_state != "complete":
        limitations.append("source-partial")
    if any(item["state"] != "available" for item in revisions.values()):
        limitations.append("revision-unknown")
    if any(point["state"] != "available" for interval in (run_timing, job_timing) for point in (interval["started_at"], interval["completed_at"])):
        limitations.append("timing-unknown")
    if observed_timeout == "unknown":
        limitations.append("timeout-unknown")
    # No API field proves which timeout value was configured in workflow source.
    limitations.append("timeout-unknown")
    if terminal == "unknown":
        limitations.append("cancellation-unknown")
    # Cancellation requests and workload termination cannot be inferred from run/job responses.
    limitations.append("cancellation-unknown")
    return {
        "contract": "FRAMEWORK-CONTRACT-032", "schema_version": "1.0",
        "profile": "github-actions-run-job", "fixture_only": fixture_only,
        "source": {
            "acquisition_state": acquisition_state,
            "repository_id": repository_id if isinstance(repository_id, int) and repository_id > 0 else None,
            "repository_name": _safe_text(repository_name, token, 255),
            "workflow_id": workflow_id if isinstance(workflow_id, int) and workflow_id > 0 else None,
            "workflow_path": _safe_text(workflow_path, token, 1024),
            "workflow_ref": _safe_text(workflow_ref, token, 1024), "source_ref": source_ref,
            "observed_at": observed_at, "response_revision": response_revision,
            "response_digest": response_digest,
        },
        "identity": {"state": "available", "run_id": run_id, "run_attempt": attempt,
                     "job_id": job_id, "job_name": job_name, "event_name": _safe_text(run.get("event"), token, 128)},
        "revisions": revisions, "timing": {"run": run_timing, "job": job_timing},
        "timeout": {"configuration_state": "unknown", "minutes": None, "configuration_revision": None,
                    "configuration_source": None, "observed_state": observed_timeout,
                    "host_conclusion": host_conclusion,
                    "observation_source": job_source if host_conclusion not in {"unknown", "unavailable"} else None},
        "cancellation": {"request_state": "unknown", "requested_at": None, "request_source": None,
                         "host_terminal_state": terminal, "terminal_source": job_source if terminal != "unknown" else None,
                         "workload_state": "unknown", "workload_observation": None},
        "measurements": metrics, "limitations": sorted(set(limitations)),
    }


def _interval(run_id: int, attempt: int, job_id: int | None, started: Any, completed: Any, source: str, token: str | None) -> dict[str, Any]:
    return {"run_id": run_id, "run_attempt": attempt, "job_id": job_id,
            "started_at": _point(started, source, token), "completed_at": _point(completed, source, token)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", help="owner/name")
    parser.add_argument("run_id", type=int)
    parser.add_argument("run_attempt", type=int)
    parser.add_argument("--max-pages", type=int, default=_MAX_PAGES)
    args = parser.parse_args(argv)
    token = os.environ.get("GITHUB_TOKEN") or None
    try:
        result = ActionsApi(token, max_pages=args.max_pages).collect(args.repository, args.run_id, args.run_attempt)
    except (CollectionError, ValueError) as exc:
        code = exc.code if isinstance(exc, CollectionError) else "invalid-request"
        status = exc.status if isinstance(exc, CollectionError) else None
        # Do not echo URLs, server bodies, request headers, or credential-bearing exceptions.
        print(json.dumps({"collection_state": "denied" if status in {401, 403, 404} else "unavailable",
                          "error": code, "http_status": status}, sort_keys=True, separators=(",", ":")))
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["collection_state"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
