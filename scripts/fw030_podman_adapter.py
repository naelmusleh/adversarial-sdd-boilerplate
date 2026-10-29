"""Bounded GitHub-hosted Ubuntu 24.04/rootless Podman adapter for FW-030.

This adapter supports one explicitly selected profile snapshot only. It is not
an OS isolation boundary and does not accept secrets, network access, arbitrary
host paths, or an unsandboxed fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from scripts.fw030_contract import validate_request, validate_result


PROFILE_ID = "github-actions.ubuntu-24.04.rootless-podman"
PROFILE_REVISION = "2026-10-28.1"
PODMAN_VERSION = "4.9.3"
PINNED_IMAGE = "docker.io/library/alpine@sha256:dc92f017beea8e7f43263073d717f7bc011228c95d5312e440deb4d035bb4eec"
CAPABILITIES = {"runtime.rootless", "filesystem.readonly-input", "network.disabled", "secrets.disabled", "resources.limits", "evidence.bounded"}
MAX_REQUEST_BYTES = 256 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class AdapterError(Exception):
    def __init__(self, code: str, message: str, readiness: str = "blocked") -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.readiness = readiness


class AdapterCancelled(Exception):
    pass


Runner = Callable[[Sequence[str], int], subprocess.CompletedProcess[str]]


def _run(argv: Sequence[str], timeout: int, env: Mapping[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run a host-side Podman command without a shell and discard inherited secrets."""
    base = os.environ
    safe_env = {
        "PATH": base.get("PATH", "/usr/bin:/bin"),
        "HOME": base.get("HOME", "/tmp"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }
    for name in ("XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS", "TMPDIR", "CONTAINERS_CONF", "CONTAINERS_STORAGE_CONF"):
        if base.get(name):
            safe_env[name] = base[name]
    if env:
        safe_env.update(env)
    try:
        return subprocess.run(list(argv), shell=False, check=False, capture_output=True,
                              text=True, timeout=timeout, env=safe_env, start_new_session=True)
    except subprocess.TimeoutExpired as exc:
        raise AdapterError("fw030.adapter.host_command_timeout", "host runtime command exceeded its bounded timeout") from exc
    except OSError as exc:
        raise AdapterError("fw030.adapter.runtime_unavailable", "the required host runtime command could not be started", "unsupported") from exc


def _json_without_duplicates(raw: bytes) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result
    return json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid constant")))


def _diag(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _result(request: Mapping[str, Any] | None, request_bytes: bytes, readiness: str,
            auth: Mapping[str, str] | None = None, execution: str = "not_started",
            cleanup: str = "not_applicable", evidence: str = "not_collected",
            cases: list[dict[str, str]] | None = None, diagnostics: list[dict[str, str]] | None = None) -> dict[str, Any]:
    valid_id = request.get("invocation_id") if request else None
    expected = request["policy"]["evidence"]["case_ids"] if request and readiness != "invalid" else []
    output = {
        "schema_version": "1.0",
        "invocation_id": valid_id if isinstance(valid_id, str) else "00000000-0000-4000-8000-000000000000",
        "request_sha256": hashlib.sha256(request_bytes).hexdigest() if request_bytes else None,
        "readiness_status": readiness,
        "authorization_reference": dict(auth) if auth else None,
        "expected_case_ids": expected,
        "case_results": cases or [],
        "evidence_references": [],
        "states": {
            "request_readiness": readiness,
            "authorization": "authorized" if auth else "not_requested",
            "execution": execution,
            "cleanup": cleanup,
            "evidence": evidence,
            "review": "not_performed",
        },
        "diagnostics": (diagnostics or [])[:32],
    }
    checked = validate_result(json.dumps(output, separators=(",", ":")))
    if not checked["valid"]:
        output["readiness_status"] = "invalid"
        output["states"].update(request_readiness="invalid", authorization="not_requested",
                                execution="not_started", cleanup="not_applicable", evidence="not_collected")
        output["authorization_reference"] = None
        output["case_results"] = []
        output["diagnostics"] = [_diag("fw030.adapter.internal_contract_error", "$", "the generated invocation result did not satisfy the versioned result contract")]
    return output


def _host_facts(env: Mapping[str, str]) -> dict[str, str]:
    try:
        release: dict[str, str] = {}
        for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
            key, sep, value = line.partition("=")
            if sep and key in {"ID", "VERSION_ID", "PRETTY_NAME"}:
                release[key] = value.strip().strip('"')
    except OSError as exc:
        raise AdapterError("fw030.adapter.host_unavailable", "host identity could not be verified", "unsupported") from exc
    if env.get("GITHUB_ACTIONS", "").lower() != "true" or env.get("RUNNER_OS") != "Linux" or env.get("ImageOS") != "ubuntu24":
        raise AdapterError("fw030.adapter.profile_unsupported", "this adapter supports only the selected GitHub-hosted Ubuntu 24.04 profile", "unsupported")
    if release.get("ID") != "ubuntu" or release.get("VERSION_ID") != "24.04" or platform.machine() != "x86_64":
        raise AdapterError("fw030.adapter.host_unsupported", "the observed operating system or architecture does not match the selected profile", "unsupported")
    if env.get("GITHUB_REPOSITORY") is None or env.get("GITHUB_SHA") is None or env.get("GITHUB_RUN_ID") is None:
        raise AdapterError("fw030.adapter.provider_context_missing", "required GitHub Actions run identity is unavailable", "unsupported")
    return {"os": release.get("PRETTY_NAME", "Ubuntu 24.04"), "architecture": platform.machine(),
            "image_header": env.get("ImageVersion", "not-reported"), "image_env": env.get("ImageOS", "not-reported")}


def _check_request(raw: bytes, env: Mapping[str, str]) -> tuple[dict[str, Any], str]:
    if not raw or len(raw) > MAX_REQUEST_BYTES:
        raise AdapterError("fw030.adapter.request_size", "request is empty or exceeds the bounded size")
    verdict = validate_request(raw)
    if not verdict["valid"]:
        raise AdapterError("fw030.adapter.request_invalid", "request does not satisfy FRAMEWORK-CONTRACT-030")
    try:
        request = _json_without_duplicates(raw)
    except (UnicodeError, json.JSONDecodeError, ValueError):
        raise AdapterError("fw030.adapter.request_invalid", "request is not strict UTF-8 JSON")
    if request["profile"] != {"id": PROFILE_ID, "revision": PROFILE_REVISION}:
        raise AdapterError("fw030.adapter.profile_mismatch", "request names a profile other than the explicitly selected adapter profile", "unsupported")
    if request["execution_context"]["kind"] != "hosted":
        raise AdapterError("fw030.adapter.context_unsupported", "this adapter supports hosted GitHub Actions context only", "unsupported")
    context = request["execution_context"]["provider_context"]
    expected_pairs = {
        "provider": "GitHub Actions", "run_id": env.get("GITHUB_RUN_ID"),
        "attempt": int(env.get("GITHUB_RUN_ATTEMPT", "0")), "event": env.get("GITHUB_EVENT_NAME"),
        "ref": env.get("GITHUB_REF"),
    }
    if any(context.get(key) != value for key, value in expected_pairs.items()):
        raise AdapterError("fw030.adapter.run_identity_mismatch", "request provider metadata does not match the active workflow run")
    if request["source"]["repository"] != env.get("GITHUB_REPOSITORY") or request["source"]["revision"] != env.get("GITHUB_SHA"):
        raise AdapterError("fw030.adapter.source_mismatch", "request source identity does not match the checked out repository revision")
    policy = request["policy"]
    if policy["network"] != "disabled" or policy["secrets"] != "disabled":
        raise AdapterError("fw030.adapter.policy_unsupported", "selected profile accepts no network and no secrets")
    if request["workload"]["image"] != PINNED_IMAGE:
        raise AdapterError("fw030.adapter.image_unsupported", "workload image is outside the selected pinned image")
    if request["workload"]["executable"] not in {"sh", "/bin/sh"} or request["workload"]["argv"][0] != request["workload"]["executable"]:
        raise AdapterError("fw030.adapter.command_unsupported", "selected profile pilot permits only the declared shell entrypoint")
    if not request["required_capabilities"] or set(request["required_capabilities"]) - CAPABILITIES:
        raise AdapterError("fw030.adapter.capability_unsupported", "request requires a capability outside the selected profile")
    return request, hashlib.sha256(raw).hexdigest()


def _safe_paths(request: Mapping[str, Any], env: Mapping[str, str]) -> tuple[Path, Path, Path]:
    root_text = env.get("FW030_PILOT_ROOT", "")
    runner_temp = env.get("RUNNER_TEMP", "")
    if not root_text or not runner_temp:
        raise AdapterError("fw030.adapter.temp_unavailable", "dedicated temporary workspace is unavailable")
    root = Path(root_text)
    temp = Path(runner_temp).resolve(strict=True)
    if root.is_symlink() or root.resolve(strict=True) != root.absolute() or root.parent.resolve(strict=True) != temp:
        raise AdapterError("fw030.adapter.path_invalid", "dedicated workspace is not a direct canonical child of runner temporary storage")
    input_dir = root / "input"
    output_dir = root / "output"
    if not input_dir.is_dir() or not output_dir.is_dir() or input_dir.is_symlink() or output_dir.is_symlink():
        raise AdapterError("fw030.adapter.path_invalid", "input and output directories must be ordinary directories")
    mounts = request["policy"]["mounts"]
    if len(mounts) != 2:
        raise AdapterError("fw030.adapter.mount_policy", "pilot profile requires exactly one input and one output declaration")
    expected = {"input": (str(input_dir), "/input", "read_only"), "output": (str(output_dir), "/output", "write_only")}
    for mount in mounts:
        wanted = expected.get(mount["kind"])
        if wanted is None or (mount["source"], mount["target"], mount["mode"]) != wanted:
            raise AdapterError("fw030.adapter.mount_policy", "mount declaration differs from the fixed pilot boundary")
    workload = request["workload"]
    if workload["working_directory"] != "/input" or workload["argv"] != [workload["executable"], "-eu", "/input/workload.sh"]:
        raise AdapterError("fw030.adapter.command_policy", "pilot permits only the fixed synthetic workload entrypoint")
    script = input_dir / "workload.sh"
    if not script.is_file() or script.is_symlink() or not (input_dir / "fixture.txt").is_file():
        raise AdapterError("fw030.adapter.fixture_missing", "synthetic pilot inputs are incomplete")
    return root, input_dir, output_dir


def _profile_observation(runner: Runner, timeout: int) -> dict[str, Any]:
    version = runner(["podman", "--version"], timeout)
    if version.returncode != 0 or version.stdout.strip() != f"podman version {PODMAN_VERSION}":
        raise AdapterError("fw030.adapter.runtime_version", "rootless Podman version does not match the observed profile", "unsupported")
    info = runner(["podman", "info", "--format", "json"], timeout)
    if info.returncode != 0:
        raise AdapterError("fw030.adapter.runtime_unavailable", "rootless Podman inspection failed", "unsupported")
    try:
        value = json.loads(info.stdout)
        host = value["host"]
        rootless = host["security"]["rootless"]
        runtime = host["ociRuntime"]["name"]
        runtime_version = host["ociRuntime"]["version"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise AdapterError("fw030.adapter.runtime_observation_invalid", "Podman returned incomplete runtime identity", "unsupported")
    if rootless is not True:
        raise AdapterError("fw030.adapter.runtime_not_rootless", "Podman is not operating rootless", "unsupported")
    return {"podman": PODMAN_VERSION, "oci_runtime": str(runtime), "oci_runtime_version": str(runtime_version)}


def _verify_container(inspect: Any, request: Mapping[str, Any]) -> None:
    if not isinstance(inspect, list) or len(inspect) != 1 or not isinstance(inspect[0], dict):
        raise AdapterError("fw030.adapter.inspect_invalid", "runtime inspection did not return one expected container")
    item = inspect[0]
    config = item.get("Config", {})
    host = item.get("HostConfig", {})
    limits = request["policy"]["limits"]
    cpu_nano = limits["cpu_millis"] * 1_000_000
    expected_tmpfs = f"rw,noexec,nosuid,size={limits['disk_mb']}m,rprivate,nodev"
    tmpfs = host.get("Tmpfs", {}).get("/output", "")
    if (host.get("NetworkMode") != "none" or host.get("ReadonlyRootfs") is not True
            or host.get("Memory") != limits["memory_mb"] * 1024 * 1024
            or host.get("NanoCpus") != cpu_nano or host.get("PidsLimit") != limits["process_count"]
            or config.get("User") != f"{request['policy']['uid']}:{request['policy']['gid']}"
            or "ALL" not in host.get("CapDrop", [])
            or not any("no-new-privileges" in item for item in host.get("SecurityOpt", []))
            or tmpfs != expected_tmpfs):
        raise AdapterError("fw030.adapter.policy_mismatch", "observed container configuration does not match the requested controls")
    mounts = host.get("Binds", [])
    if len(mounts) != 1 or not mounts[0].endswith(":/input:ro"):
        raise AdapterError("fw030.adapter.mount_observation_mismatch", "observed input binding is not the declared read-only input")


def run_request(raw: bytes, authorization: Mapping[str, str] | None,
                env: Mapping[str, str] | None = None, runner: Runner | None = None) -> dict[str, Any]:
    """Execute one fixed-profile request; caller supplies, but cannot create, authorization."""
    active_env = dict(os.environ if env is None else env)
    request: dict[str, Any] | None = None
    auth: dict[str, str] | None = None
    request_digest = ""
    execution, cleanup, readiness = "not_started", "not_applicable", "blocked"
    cases: list[dict[str, str]] = []
    diagnostics: list[dict[str, str]] = []
    container_name = ""
    run = runner or (lambda argv, timeout: _run(argv, timeout))
    try:
        host = _host_facts(active_env)
        request, request_digest = _check_request(raw, active_env)
        root, input_dir, output_dir = _safe_paths(request, active_env)
        timeout = request["policy"]["limits"]["wall_seconds"]
        runtime = _profile_observation(run, min(timeout, 30))
        readiness = "prerequisites_valid"
        if not isinstance(authorization, Mapping) or set(authorization) != {"record_id", "record_sha256", "authorized_request_sha256"}:
            raise AdapterError("fw030.adapter.authorization_missing", "caller did not supply the required request-bound authorization reference")
        if (not isinstance(authorization.get("record_id"), str) or not authorization["record_id"]
                or not _DIGEST.fullmatch(str(authorization.get("record_sha256", "")))
                or authorization.get("authorized_request_sha256") != request_digest):
            raise AdapterError("fw030.adapter.authorization_invalid", "supplied authorization reference does not bind the exact request")
        auth = dict(authorization)
        invocation = request["invocation_id"].replace("-", "")[:16]
        container_name = f"fw030-{invocation}"
        output_dir_empty = not any(output_dir.iterdir())
        if not output_dir_empty:
            raise AdapterError("fw030.adapter.output_not_empty", "output destination must be empty before invocation")
        limit = request["policy"]["limits"]
        command = [
            "podman", "run", "--pull=never", "--name", container_name, "--network=none", "--read-only",
            "--user", f"{request['policy']['uid']}:{request['policy']['gid']}", "--cap-drop=all",
            "--security-opt=no-new-privileges", f"--memory={limit['memory_mb']}m",
            f"--cpus={limit['cpu_millis'] / 1000:.3f}", f"--pids-limit={limit['process_count']}",
            f"--timeout={timeout}", f"--tmpfs=/output:rw,noexec,nosuid,size={limit['disk_mb']}m",
            "--volume", f"{input_dir}:/input:ro", request["workload"]["image"],
            *request["workload"]["argv"],
        ]
        # Host/image identities are retained only as sanitized identifiers; no env is passed to the workload.
        _ = (host, runtime)
        execution, cleanup = "running", "required"
        ran = run(command, timeout + 10)
        if ran.returncode == 0:
            inspect = run(["podman", "inspect", container_name], 15)
            if inspect.returncode != 0:
                raise AdapterError("fw030.adapter.inspect_failed", "container policy inspection failed")
            try:
                _verify_container(json.loads(inspect.stdout), request)
            except (json.JSONDecodeError, TypeError):
                raise AdapterError("fw030.adapter.inspect_invalid", "container policy inspection was not valid JSON")
            copied = run(["podman", "cp", f"{container_name}:/output/cases.json", str(output_dir / "cases.json")], 15)
            if copied.returncode != 0:
                raise AdapterError("fw030.adapter.output_missing", "bounded case result could not be retrieved")
            result_path = output_dir / "cases.json"
            if result_path.is_symlink() or not result_path.is_file() or result_path.stat().st_size > min(MAX_OUTPUT_BYTES, request["policy"]["evidence"]["max_output_bytes"]):
                raise AdapterError("fw030.adapter.output_invalid", "case result is not a bounded ordinary file")
            parsed = _json_without_duplicates(result_path.read_bytes())
            if not isinstance(parsed, list) or any(not isinstance(item, dict) or set(item) != {"case_id", "outcome"} for item in parsed):
                raise AdapterError("fw030.adapter.cases_invalid", "case results do not match the bounded output contract")
            cases = [{"case_id": item["case_id"], "outcome": item["outcome"]} for item in parsed]
            expected = request["policy"]["evidence"]["case_ids"]
            if sorted(item["case_id"] for item in cases) != sorted(expected) or any(item["outcome"] != "passed" for item in cases):
                raise AdapterError("fw030.adapter.case_failure", "one or more required synthetic boundary cases failed")
            execution = "succeeded"
        else:
            execution = "failed"
            diagnostics.append(_diag("fw030.adapter.workload_failed", "$.states.execution", "workload returned a non-zero status or exceeded its runtime limit"))
    except AdapterCancelled:
        execution = "cancelled"
        diagnostics.append(_diag("fw030.adapter.cancelled", "$.states.execution", "adapter received a cancellation signal"))
    except AdapterError as exc:
        if execution == "running":
            execution = "failed"
            cleanup = "required"
        diagnostics.append(_diag(exc.code, "$", exc.message))
        if readiness != "prerequisites_valid":
            readiness = exc.readiness
    finally:
        if container_name:
            try:
                exists = run(["podman", "container", "exists", container_name], 15)
                if exists.returncode == 0:
                    removed = run(["podman", "rm", "--force", container_name], 20)
                    verify = run(["podman", "container", "exists", container_name], 15)
                    if removed.returncode != 0 or verify.returncode != 1:
                        cleanup = "failed"
                        execution = "failed" if execution == "running" else execution
                        diagnostics.append(_diag("fw030.adapter.cleanup_failed", "$.states.cleanup", "container removal or independent absence verification failed"))
                    else:
                        cleanup = "complete"
                elif exists.returncode == 1:
                    cleanup = "complete"
                else:
                    cleanup = "unknown"
                    diagnostics.append(_diag("fw030.adapter.cleanup_unknown", "$.states.cleanup", "runtime could not determine whether the container remains"))
            except AdapterError:
                cleanup = "unknown"
                diagnostics.append(_diag("fw030.adapter.cleanup_unknown", "$.states.cleanup", "cleanup command failed; resource absence is not established"))
    return _result(request, raw, readiness, auth, execution, cleanup,
                   "incomplete" if execution in {"succeeded", "failed", "cancelled"} else "not_collected",
                   cases, diagnostics)


def _pilot_request(env: Mapping[str, str], root: Path) -> tuple[bytes, dict[str, str]]:
    source_tree = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], check=True, capture_output=True, text=True).stdout.strip()
    policy: dict[str, Any] = {
        "uid": 1000, "gid": 1000,
        "mounts": [
            {"kind": "input", "source": str(root / "input"), "target": "/input", "mode": "read_only"},
            {"kind": "output", "source": str(root / "output"), "target": "/output", "mode": "write_only"},
        ],
        "network": "disabled", "secrets": "disabled",
        "limits": {"cpu_millis": 1000, "memory_mb": 128, "process_count": 32, "disk_mb": 16, "wall_seconds": 30},
        "cancellation": "terminate_then_kill_within_wall_limit",
        "evidence": {"mode": "allowlisted_redacted", "max_output_bytes": 4096,
                     "case_ids": ["INPUT_READONLY", "HOST_PATH_DENIED", "NETWORK_DISABLED", "OUTPUT_BOUNDED"]},
    }
    canonical_policy = json.dumps(policy, sort_keys=True, separators=(",", ":")).encode("utf-8")
    policy["sha256"] = hashlib.sha256(canonical_policy).hexdigest()
    request = {
        "schema_version": "1.0", "invocation_id": str(uuid.uuid4()),
        "source": {"repository": env["GITHUB_REPOSITORY"], "revision": env["GITHUB_SHA"],
                   "tree_sha256": hashlib.sha256(source_tree.encode()).hexdigest()},
        "execution_context": {"kind": "hosted", "provider_context": {
            "provider": "GitHub Actions", "workflow": env["GITHUB_WORKFLOW"], "job": env["GITHUB_JOB"],
            "run_id": env["GITHUB_RUN_ID"], "attempt": int(env["GITHUB_RUN_ATTEMPT"]),
            "event": env["GITHUB_EVENT_NAME"], "ref": env["GITHUB_REF"],
            "url": f"{env.get('GITHUB_SERVER_URL', 'https://github.com')}/{env['GITHUB_REPOSITORY']}/actions/runs/{env['GITHUB_RUN_ID']}",
        }},
        "profile": {"id": PROFILE_ID, "revision": PROFILE_REVISION},
        "workload": {"image": PINNED_IMAGE, "argv": ["sh", "-eu", "/input/workload.sh"],
                     "executable": "sh", "working_directory": "/input"},
        "policy": policy,
        "required_capabilities": ["runtime.rootless", "filesystem.readonly-input", "network.disabled", "secrets.disabled", "resources.limits", "evidence.bounded"],
    }
    raw = json.dumps(request, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    # Pilot-only reference. It is a fixture for the owner-authorized synthetic workflow,
    # not a production authorization or a gate approval.
    auth = {"record_id": "SYNTHETIC-DECISION-043-PILOT", "record_sha256": hashlib.sha256(b"DECISION-043 synthetic pilot authorization").hexdigest(), "authorized_request_sha256": digest}
    return raw, auth


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="run the synthetic, fixed-input adapter pilot")
    args = parser.parse_args(argv)
    if not args.pilot:
        parser.error("only the reviewed --pilot entrypoint is available in this implementation unit")
    def cancel_handler(_signum: int, _frame: Any) -> None:
        raise AdapterCancelled
    signal.signal(signal.SIGTERM, cancel_handler)
    signal.signal(signal.SIGINT, cancel_handler)
    env = dict(os.environ)
    root = Path(tempfile.mkdtemp(prefix="fw030-adapter.", dir=env.get("RUNNER_TEMP")))
    os.chmod(root, 0o700)
    (root / "input").mkdir(mode=0o700)
    (root / "output").mkdir(mode=0o700)
    sentinel = root / "host-sentinel.txt"
    sentinel.write_text("synthetic-host-only-value", encoding="utf-8")
    (root / "input" / "fixture.txt").write_text("synthetic-fixture", encoding="utf-8")
    script = f'''#!/bin/sh
set -eu
test "$(cat /input/fixture.txt)" = synthetic-fixture
if touch /input/forbidden-write 2>/dev/null; then exit 61; fi
if cat "{sentinel}" >/dev/null 2>&1; then exit 62; fi
if /bin/busybox wget -T 2 -qO- http://1.1.1.1/ >/dev/null 2>&1; then exit 63; fi
printf '[{{"case_id":"INPUT_READONLY","outcome":"passed"}},{{"case_id":"HOST_PATH_DENIED","outcome":"passed"}},{{"case_id":"NETWORK_DISABLED","outcome":"passed"}},{{"case_id":"OUTPUT_BOUNDED","outcome":"passed"}}]' > /output/cases.json
'''
    (root / "input" / "workload.sh").write_text(script, encoding="utf-8")
    env["FW030_PILOT_ROOT"] = str(root)
    try:
        raw, authorization = _pilot_request(env, root)
        result = run_request(raw, authorization, env)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    if root.exists():
        result["states"]["cleanup"] = "failed"
        result["diagnostics"].append(_diag("fw030.adapter.temp_cleanup_failed", "$.states.cleanup", "temporary pilot files remain after cleanup"))
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["states"]["execution"] == "succeeded" and result["states"]["cleanup"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
