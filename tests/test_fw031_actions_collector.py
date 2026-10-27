"""Synthetic transport tests for the passive Actions API collector."""
from __future__ import annotations

import json
import unittest
import urllib.request
from email.message import Message
from urllib.error import HTTPError
from io import BytesIO

from scripts.fw031_actions_collector import ActionsApi, CollectionError, _RejectRedirects
from scripts.fw031_actions_evidence import validate_actions_evidence


class Response:
    def __init__(self, body, status=200, headers=None):
        self.status = status
        self.headers = Message()
        for key, value in (headers or {}).items():
            self.headers[key] = value
        self._body = json.dumps(body).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        return self._body[:size]


def run_record(attempt=2):
    return {"id": 55, "run_attempt": attempt, "workflow_id": 9,
            "repository": {"id": 7, "full_name": "owner/repo"},
            "path": ".github/workflows/ci.yml@main", "event": "push", "status": "completed",
            "head_sha": "a" * 40, "run_started_at": "2026-10-27T10:00:00Z",
            "updated_at": "2026-10-27T10:01:00Z", "conclusion": "success"}


def job_record(run_id=55, name="tests"):
    return {"id": 88, "run_id": run_id, "name": name, "status": "completed",
            "conclusion": "success", "head_sha": "a" * 40,
            "started_at": "2026-10-27T10:00:10Z", "completed_at": "2026-10-27T10:00:50Z"}


class CollectorTests(unittest.TestCase):
    def test_collects_attempt_scoped_job_and_emits_valid_limited_record(self):
        responses = [Response(run_record(), headers={"ETag": '"run-v1"'}),
                     Response({"total_count": 1, "jobs": [job_record()]}, headers={"ETag": '"jobs-v1"'})]
        calls = []

        def opener(request, timeout):
            calls.append(request)
            return responses.pop(0)

        result = ActionsApi("secret-token", opener=opener, sleeper=lambda _: None).collect("owner/repo", 55, 2)
        self.assertEqual(result["collection_state"], "complete")
        self.assertEqual(result["records"][0]["identity"]["run_attempt"], 2)
        self.assertIn("/attempts/2/jobs?", calls[1].full_url)
        self.assertTrue(all(call.get_method() == "GET" for call in calls))
        self.assertNotIn("Authorization", result["records"][0]["source"])
        self.assertTrue(validate_actions_evidence(json.dumps(result["records"][0]))["valid"])
        self.assertEqual(result["records"][0]["cancellation"]["workload_state"], "unknown")
        self.assertEqual(result["records"][0]["measurements"][-1]["state"], "unknown")
        self.assertTrue(result["records"][0]["fixture_only"])
        self.assertEqual(result["records"][0]["source"]["workflow_path"], ".github/workflows/ci.yml")
        self.assertIsNone(result["records"][0]["source"]["workflow_ref"])
        self.assertEqual(result["records"][0]["source"]["acquisition_state"], "partial")
        self.assertIsNone(result["records"][0]["source"]["workflow_ref"])
        self.assertIn("workflow_ref-unavailable", result["limitations"])

    def test_attempt_endpoint_binding_is_used_when_job_payload_omits_attempt(self):
        responses = [Response(run_record(3)), Response({"total_count": 1, "jobs": [job_record()]})]
        result = ActionsApi(opener=lambda *_args, **_kwargs: responses.pop(0)).collect("owner/repo", 55, 3)
        self.assertEqual(result["records"][0]["identity"]["run_attempt"], 3)

    def test_mismatched_run_job_is_excluded_and_marks_partial(self):
        responses = [Response(run_record()), Response({"total_count": 1, "jobs": [job_record(run_id=56)]})]
        result = ActionsApi(opener=lambda *_args, **_kwargs: responses.pop(0)).collect("owner/repo", 55, 2)
        self.assertEqual(result["collection_state"], "partial")
        self.assertEqual(result["records"], [])

    def test_running_jobs_do_not_claim_run_completion_time_or_host_outcome(self):
        run = run_record()
        run["status"] = "in_progress"
        run["conclusion"] = None
        job = job_record()
        job["status"] = "in_progress"
        job["conclusion"] = None
        responses = [Response(run), Response({"total_count": 1, "jobs": [job]})]
        result = ActionsApi(opener=lambda *_args, **_kwargs: responses.pop(0)).collect("owner/repo", 55, 2)
        record = result["records"][0]
        self.assertEqual(record["timing"]["run"]["completed_at"]["state"], "unknown")
        self.assertEqual(record["timeout"]["host_conclusion"], "unknown")
        self.assertIsNone(record["timeout"]["observation_source"])
        self.assertTrue(validate_actions_evidence(json.dumps(record))["valid"])

    def test_returned_repository_must_match_requested_repository(self):
        response = run_record()
        response["repository"]["full_name"] = "other/repo"
        with self.assertRaises(CollectionError) as caught:
            ActionsApi(opener=lambda *_args, **_kwargs: Response(response)).collect("owner/repo", 55, 2)
        self.assertEqual(caught.exception.code, "repository-identity-mismatch")

    def test_pagination_limit_is_bounded_and_reported_partial(self):
        responses = [Response(run_record()), Response({"total_count": 101, "jobs": [job_record()]})]
        result = ActionsApi(max_pages=1, opener=lambda *_args, **_kwargs: responses.pop(0)).collect("owner/repo", 55, 2)
        self.assertEqual(result["pages_read"], 1)
        self.assertEqual(result["collection_state"], "partial")

    def test_retry_is_bounded_and_only_retries_transient_http_errors(self):
        count = [0]
        def opener(request, timeout):
            count[0] += 1
            if count[0] == 1:
                raise HTTPError(request.full_url, 503, "untrusted body", {}, BytesIO(b"secret"))
            return Response(run_record())
        api = ActionsApi(max_retries=1, opener=opener, sleeper=lambda _: None)
        payload, _, _ = api.get_json("/repos/owner/repo/actions/runs/55/attempts/2")
        self.assertEqual(payload["id"], 55)
        self.assertEqual(count[0], 2)

    def test_redirect_handler_refuses_cross_host_redirects(self):
        handler = _RejectRedirects()
        request = urllib.request.Request("https://api.github.com/path", headers={"Authorization": "Bearer secret"})
        self.assertIsNone(handler.redirect_request(request, None, 302, "Found", {}, "https://attacker.example/"))

    def test_token_and_server_error_body_never_escape(self):
        def opener(request, timeout):
            raise HTTPError(request.full_url, 403, "secret-token private body", {}, BytesIO(b"secret-token"))
        with self.assertRaises(CollectionError) as caught:
            ActionsApi("secret-token", max_retries=0, opener=opener).get_json("/private")
        self.assertEqual(caught.exception.code, "http-error")
        self.assertNotIn("secret-token", str(caught.exception))
        self.assertNotIn("private body", str(caught.exception))

    def test_invalid_origin_and_unbounded_settings_are_rejected(self):
        with self.assertRaises(ValueError):
            ActionsApi(base_url="http://api.github.com")
        with self.assertRaises(ValueError):
            ActionsApi(base_url="https://api.github.com.attacker.example")
        with self.assertRaises(ValueError):
            ActionsApi(base_url="https://api.github.com/unexpected/path")
        with self.assertRaises(ValueError):
            ActionsApi().collect("../repo", 1, 1)
        with self.assertRaises(ValueError):
            ActionsApi(max_pages=6)
        with self.assertRaises(ValueError):
            ActionsApi(max_retries=4)


if __name__ == "__main__":
    unittest.main()
