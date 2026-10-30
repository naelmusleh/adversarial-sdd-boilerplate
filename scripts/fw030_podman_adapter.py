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
import stat
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

if __package__:
    from .fw030_contract import validate_request, validate_result
else:  # Direct script execution places scripts/ on sys.path.
    from fw030_contract import validate_request, validate_result


PROFILE_ID = "github-actions.ubuntu-24.04.rootless-podman"
PROFILE_REVISION = "2026-10-28.1"
PODMAN_VERSION = "4.9.3"
OCI_RUNTIME = "crun"
OCI_RUNTIME_VERSION = "1.14.1"
PINNED_IMAGE = "docker.io/library/alpine@sha256:dc92f017beea8e7f43263073d717f7bc011228c95d5312e440deb4d035bb4eec"
PODMAN_DEFAULT_CAPABILITIES = frozenset({
    "CAP_CHOWN", "CAP_DAC_OVERRIDE", "CAP_FOWNER", "CAP_FSETID", "CAP_KILL",
    "CAP_NET_BIND_SERVICE", "CAP_SETFCAP", "CAP_SETGID", "CAP_SETPCAP", "CAP_SETUID", "CAP_SYS_CHROOT",
})
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
    base = env or os.environ
    root = Path(base.get("FW030_PILOT_ROOT", "/tmp"))
    safe_env = {
        "PATH": base.get("PATH", "/usr/bin:/bin"),
        "HOME": str(root / "podman-home"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }
    for name in ("XDG_RUNTIME_DIR",):
        if base.get(name):
            safe_env[name] = base[name]
    safe_env["TMPDIR"] = str(root / "podman-tmp")
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


def _safe_runtime_error_hint(stderr: str) -> str:
    """Expose one bounded first-line hint with paths and credential-like values redacted."""
    first = next((line.strip() for line in stderr.splitlines() if line.strip()), "")
    if not first:
        return "empty"
    first = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", first)
    first = re.sub(
        r"(?i)\b(token|password|secret|authorization|authfile)(?:\s*[=:]\s*|\s+)(?:bearer\s+)?[^\s,;]+",
        r"\1=<redacted>",
        first,
    )
    first = re.sub(r"https?://[^\s]+", "<url>", first)
    first = re.sub(r"(?<![A-Za-z0-9])/(?:[^\s,:;]+)", "<path>", first)
    first = re.sub(r"(?i)(?:sha256:)?[0-9a-f]{32,64}", "<id>", first)
    first = re.sub(r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b", "<id>", first, flags=re.I)
    first = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<ip>", first)
    first = "".join(char if char.isprintable() else " " for char in first)
    return first[:160] or "empty"


def _record_cleanup_error(failure: dict[str, Any], root: Path,
                          function: Callable[..., Any], path: str, exc: OSError) -> None:
    """Keep the first bounded cleanup error; never expose absolute workspace paths or owner IDs."""
    if failure:
        return
    try:
        relative = Path(path).relative_to(root).as_posix()
    except ValueError:
        relative = "outside_workspace"
    relative = re.sub(r"(?i)\b[0-9a-f]{16,}\b", "<id>", relative)[:160]
    try:
        info = os.lstat(path)
        kind = ("symlink" if stat.S_ISLNK(info.st_mode) else
                "directory" if stat.S_ISDIR(info.st_mode) else
                "file" if stat.S_ISREG(info.st_mode) else "other")
        mode = format(stat.S_IMODE(info.st_mode), "04o")
        owner = "runner" if info.st_uid == os.getuid() else "other"
        group = "runner" if info.st_gid == os.getgid() else "other"
    except OSError:
        kind, mode, owner, group = "unavailable", "unknown", "unknown", "unknown"
    failure.update(
        operation=getattr(function, "__name__", "unknown"),
        entry=relative or ".",
        errno=exc.errno or 0,
        entry_kind=kind,
        mode=mode,
        owner=owner,
        group=group,
    )


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
    try:
        run_attempt = int(env.get("GITHUB_RUN_ATTEMPT", "0"))
    except ValueError:
        raise AdapterError("fw030.adapter.provider_context_invalid", "GitHub Actions attempt metadata is invalid", "unsupported")
    expected_pairs = {
        "provider": "GitHub Actions", "run_id": env.get("GITHUB_RUN_ID"),
        "attempt": run_attempt, "event": env.get("GITHUB_EVENT_NAME"),
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


def _has_nested_mounts(input_dir: Path, mountinfo: bytes | None = None) -> bool:
    """Fail closed if mountinfo is unavailable or malformed; detect mounts below input."""
    try:
        raw = Path("/proc/self/mountinfo").read_bytes() if mountinfo is None else mountinfo
        text = raw.decode("ascii", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise AdapterError("fw030.adapter.mount_preflight_unknown",
                           "input mount preflight could not be completed") from exc
    input_path = Path(os.path.normpath(str(input_dir)))
    if not input_path.is_absolute():
        raise AdapterError("fw030.adapter.mount_preflight_unknown",
                           "input mount preflight path is not absolute")
    lines = text.splitlines()
    if not lines or any(not line.strip() for line in lines):
        raise AdapterError("fw030.adapter.mount_preflight_unknown",
                           "input mount preflight data was empty or malformed")
    for line in lines:
        fields = line.split()
        try:
            separator = fields.index("-", 6)
        except ValueError as exc:
            raise AdapterError("fw030.adapter.mount_preflight_unknown",
                               "input mount preflight data was malformed") from exc
        if separator < 6 or separator + 4 != len(fields):
            raise AdapterError("fw030.adapter.mount_preflight_unknown",
                               "input mount preflight data was malformed")
        encoded = fields[4]
        def decode_mount_escape(match: re.Match[str]) -> str:
            return chr(int(match.group(1), 8))
        mount_text = re.sub(r"\\([0-7]{3})", decode_mount_escape, encoded)
        if "\\" in mount_text or not mount_text.startswith("/"):
            raise AdapterError("fw030.adapter.mount_preflight_unknown",
                               "input mount preflight data was malformed")
        mount_path = Path(os.path.normpath(mount_text))
        if mount_path != input_path and input_path in mount_path.parents:
            return True
    return False


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
    if _has_nested_mounts(input_dir):
        raise AdapterError("fw030.adapter.input_nested_mount",
                           "synthetic input contains a nested mount; recursive bind is refused")
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
    runtime_version_raw = str(runtime_version)
    version_match = re.match(r"^(?:crun version\s+)?(\d+\.\d+\.\d+)(?=$|\s)", runtime_version_raw)
    if version_match is None:
        raise AdapterError("fw030.adapter.runtime_observation_invalid", "Podman returned an unrecognized OCI runtime version", "unsupported")
    return {"podman": PODMAN_VERSION, "oci_runtime": str(runtime),
            "oci_runtime_version": version_match.group(1), "oci_runtime_version_raw": runtime_version_raw}


def _tmpfs_options_match(raw: Any, disk_mb: int) -> bool:
    if not isinstance(raw, str):
        return False
    options = raw.split(",")
    required = {"rw", "noexec", "nosuid", "nodev", "mode=1777", f"size={disk_mb}m"}
    # Podman 4.9 may normalize namespace/copy-up options and duplicate nodev.
    # Permit those known additions, but reject conflicting or unrecognized options.
    allowed = required | {"rprivate", "tmpcopyup"}
    return required.issubset(options) and set(options).issubset(allowed)


def _effective_tmpfs_mount_matches(raw: bytes, disk_mb: int) -> bool:
    try:
        mountpoint, fs_type, mount_options, super_options = raw.decode("ascii", errors="strict").strip().split("|", 3)
    except (UnicodeError, ValueError):
        return False
    if mountpoint != "/output" or fs_type != "tmpfs":
        return False
    options = set(mount_options.split(",")) | set(super_options.split(","))
    required = {"rw", "noexec", "nosuid", "nodev", "mode=1777"}
    size_options = {f"size={disk_mb}m", f"size={disk_mb * 1024}k"}
    allowed = required | size_options | {"relatime", "inode64"}
    return required.issubset(options) and bool(options & size_options) and options.issubset(allowed)


def _effective_tmpfs_diagnostic(raw: bytes, disk_mb: int) -> str:
    """Summarize only allowlisted tmpfs properties; never emit raw mount data."""
    try:
        fields = raw.decode("ascii", errors="strict").strip().split("|", 3)
    except UnicodeError:
        return "field_parse=invalid; reason=non_ascii"
    if len(fields) != 4:
        return f"field_parse=invalid; field_count={min(len(fields), 9)}"
    mountpoint, fs_type, mount_options_raw, super_options_raw = fields
    mount_options = mount_options_raw.split(",")
    super_options = super_options_raw.split(",")
    all_options = mount_options + super_options
    required_flags = {"rw", "noexec", "nosuid", "nodev"}
    missing = sorted(required_flags - set(all_options))
    expected_sizes = {f"{disk_mb}m", f"{disk_mb * 1024}k"}
    size_values = [option[5:] for option in all_options if option.startswith("size=")]
    mode_values = [option[5:] for option in all_options if option.startswith("mode=")]
    size_match = len(size_values) > 0 and all(value in expected_sizes for value in size_values)
    mode_match = len(mode_values) > 0 and all(value == "1777" for value in mode_values)
    conflicting_flags = {"ro", "suid", "dev", "exec"}
    flag_conflict_count = sum(1 for option in all_options if option in conflicting_flags)
    known_keys = required_flags | conflicting_flags | {"relatime", "inode64", "mode", "size"}
    unknown_count = sum(1 for option in all_options if option.split("=", 1)[0] not in known_keys)
    return (
        f"field_parse=valid; mountpoint_match={str(mountpoint == '/output').lower()}; "
        f"filesystem_match={str(fs_type == 'tmpfs').lower()}; missing_flags={','.join(missing) or 'none'}; "
        f"flag_conflict_count={min(flag_conflict_count, 32)}; "
        f"size_match={str(size_match).lower()}; size_conflict_count={min(sum(value not in expected_sizes for value in size_values), 32)}; "
        f"mode_match={str(mode_match).lower()}; mode_conflict_count={min(sum(value != '1777' for value in mode_values), 32)}; "
        f"unknown_option_count={min(unknown_count, 32)}"
    )


def _parse_workload_output(raw: str, max_case_bytes: int, disk_mb: int) -> bytes:
    """Parse bounded synthetic evidence streamed while its tmpfs mount is still alive."""
    try:
        encoded = raw.encode("ascii", errors="strict")
    except UnicodeError as exc:
        raise AdapterError("fw030.adapter.output_invalid", "workload output was not bounded ASCII evidence") from exc
    if len(encoded) > max_case_bytes + 4096 + 64:
        raise AdapterError("fw030.adapter.output_invalid", "workload output exceeded the bounded evidence envelope")
    lines = raw.splitlines()
    if len(lines) != 3 or lines[0] != "FW030_OUTPUT_V1":
        raise AdapterError("fw030.adapter.output_invalid", "workload output envelope was missing or malformed")
    case_bytes, mount_bytes = lines[1].encode("ascii"), lines[2].encode("ascii")
    if not case_bytes or len(case_bytes) > max_case_bytes:
        raise AdapterError("fw030.adapter.output_invalid", "case evidence exceeded the declared output limit")
    if len(mount_bytes) > 4096 or not _effective_tmpfs_mount_matches(mount_bytes, disk_mb):
        raise AdapterError("fw030.adapter.tmpfs_observation_invalid", "effective output tmpfs evidence was missing or invalid; " + _effective_tmpfs_diagnostic(mount_bytes, disk_mb))
    return case_bytes


def _cap_drop_matches(raw: Any) -> bool:
    return (isinstance(raw, list) and all(isinstance(item, str) for item in raw)
            and len(raw) == len(PODMAN_DEFAULT_CAPABILITIES)
            and set(raw) == PODMAN_DEFAULT_CAPABILITIES)


def _mount_observation_summary(item: Mapping[str, Any], input_source: str) -> dict[str, Any]:
    """Return bounded mount facts without disclosing host paths or raw inspect data."""
    host = item.get("HostConfig", {})
    binds = host.get("Binds", []) if isinstance(host, dict) else []
    effective = item.get("Mounts", [])
    bind_rows: list[dict[str, Any]] = []
    if isinstance(binds, list):
        for raw in binds[:4]:
            if not isinstance(raw, str):
                bind_rows.append({"type": type(raw).__name__[:24]})
                continue
            fields = raw.split(":")
            option_tokens = fields[2].split(",") if len(fields) == 3 else []
            recognized = {"ro", "rw", "rprivate", "rshared", "rslave"}
            safe_details: list[dict[str, Any]] = []
            other_keys: set[str] = set()
            for token in option_tokens[:32]:
                key, separator, _value = token.partition("=")
                safe_key = key.lower() if re.fullmatch(r"[A-Za-z0-9_-]{1,24}", key) else "<other>"
                has_value = bool(separator)
                if safe_key not in recognized or has_value:
                    other_keys.add(safe_key)
                if len(safe_details) < 8:
                    safe_details.append({"key": safe_key if safe_key in recognized or safe_key in other_keys else "<other>",
                                         "has_value": has_value})
            bind_rows.append({"source_matches_expected": len(fields) == 3 and fields[0] == input_source,
                              "destination": fields[1] if len(fields) == 3 and fields[1] in {"/input", "/output"} else "other",
                              "options": sorted({token for token in option_tokens if token in recognized})[:5],
                              "option_count": min(len(option_tokens), 32),
                              "option_count_truncated": len(option_tokens) > 32,
                              "other_option_count": len(other_keys),
                              "other_option_keys": sorted(other_keys)[:8],
                              "option_details": safe_details})
    else:
        binds = []
    effective_rows: list[dict[str, Any]] = []
    if isinstance(effective, list):
        for mount in effective[:4]:
            if not isinstance(mount, dict):
                effective_rows.append({"type": type(mount).__name__[:24]})
                continue
            effective_rows.append({"type": mount.get("Type") if mount.get("Type") in {"bind", "volume", "tmpfs"} else "other",
                                   "source_matches_expected": mount.get("Source") == input_source,
                                   "destination": mount.get("Destination") if mount.get("Destination") in {"/input", "/output"} else "other",
                                   "read_only": mount.get("RW") is False})
    else:
        effective = []
    return {"bind_count": len(binds), "binds": bind_rows,
            "effective_mount_count": len(effective), "effective_mounts": effective_rows}


def _verify_container(inspect: Any, request: Mapping[str, Any],
                      observation_sink: Callable[[dict[str, Any]], None] | None = None) -> None:
    if not isinstance(inspect, list) or len(inspect) != 1 or not isinstance(inspect[0], dict):
        raise AdapterError("fw030.adapter.inspect_invalid", "runtime inspection did not return one expected container")
    item = inspect[0]
    config = item.get("Config", {})
    host = item.get("HostConfig", {})
    limits = request["policy"]["limits"]
    input_source = next(mount["source"] for mount in request["policy"]["mounts"] if mount["kind"] == "input")
    cpu_nano = limits["cpu_millis"] * 1_000_000
    tmpfs_config = host.get("Tmpfs")
    configured_tmpfs = tmpfs_config.get("/output") if isinstance(tmpfs_config, dict) else None
    if (host.get("NetworkMode") != "none" or host.get("ReadonlyRootfs") is not True
            or host.get("Memory") != limits["memory_mb"] * 1024 * 1024
            or host.get("NanoCpus") != cpu_nano or host.get("PidsLimit") != limits["process_count"]
            or config.get("User") != f"{request['policy']['uid']}:{request['policy']['gid']}"
            or config.get("Image") != request["workload"]["image"]
            or config.get("Cmd") != request["workload"]["argv"]
            or config.get("WorkingDir") != request["workload"]["working_directory"]
            or any(str(value).startswith("FW030_SECRET_SENTINEL=") for value in config.get("Env", []))
            or not _cap_drop_matches(host.get("CapDrop"))
            or host.get("CapAdd") not in (None, [])
            or host.get("Privileged") is True
            or host.get("Devices") not in (None, [])
            or (host.get("PortBindings") or {}) != {}
            or not any("no-new-privileges" in item for item in host.get("SecurityOpt", []))
            or set(host.get("Tmpfs", {})) != {"/output"}
            or not _tmpfs_options_match(configured_tmpfs, limits["disk_mb"])):
        raise AdapterError("fw030.adapter.policy_mismatch", "observed container configuration does not match the requested controls")
    mounts = host.get("Binds", [])
    if observation_sink:
        observation_sink(_mount_observation_summary(item, input_source))
    expected_options = ({"ro"}, {"ro", "rprivate"}, {"ro", "rprivate", "rbind"})
    parsed_bind: tuple[str, str, set[str]] | None = None
    if isinstance(mounts, list) and len(mounts) == 1 and isinstance(mounts[0], str):
        fields = mounts[0].split(":")
        if len(fields) == 3:
            parsed_bind = fields[0], fields[1], set(fields[2].split(","))
    if (parsed_bind is None or parsed_bind[0] != input_source or parsed_bind[1] != "/input"
            or parsed_bind[2] not in expected_options):
        raise AdapterError("fw030.adapter.mount_observation_mismatch", "observed input binding is not the declared read-only input")
    effective_mounts = item.get("Mounts")
    if (not isinstance(effective_mounts, list) or len(effective_mounts) != 1
            or not isinstance(effective_mounts[0], dict)
            or effective_mounts[0].get("Type") != "bind"
            or effective_mounts[0].get("Source") != input_source
            or effective_mounts[0].get("Destination") != "/input"
            or effective_mounts[0].get("RW") is not False):
        raise AdapterError("fw030.adapter.mount_observation_mismatch", "effective bind mounts differ from the exact read-only input declaration")


def run_request(raw: bytes, authorization: Mapping[str, str] | None,
                env: Mapping[str, str] | None = None, runner: Runner | None = None,
                observation_sink: Callable[[dict[str, str]], None] | None = None) -> dict[str, Any]:
    """Execute one fixed-profile request; caller supplies, but cannot create, authorization."""
    active_env = dict(os.environ if env is None else env)
    request: dict[str, Any] | None = None
    auth: dict[str, str] | None = None
    request_digest = ""
    execution, cleanup, readiness = "not_started", "not_applicable", "blocked"
    cases: list[dict[str, str]] = []
    diagnostics: list[dict[str, str]] = []
    container_name = ""
    run = runner or (lambda argv, timeout: _run(argv, timeout, active_env))
    try:
        host = _host_facts(active_env)
        request, request_digest = _check_request(raw, active_env)
        root, input_dir, output_dir = _safe_paths(request, active_env)
        (root / "podman-home").mkdir(mode=0o700, exist_ok=True)
        (root / "podman-tmp").mkdir(mode=0o700, exist_ok=True)
        auth_file = root / "podman-home" / "auth.json"
        auth_file.write_text("{}", encoding="utf-8")
        os.chmod(auth_file, 0o600)
        timeout = request["policy"]["limits"]["wall_seconds"]
        runtime = _profile_observation(run, min(timeout, 30))
        if observation_sink:
            observation_sink({**host, **runtime, "image_pull": "not_attempted; permitted host access is limited to pinned-image retrieval; workload network remains disabled"})
        if runtime["oci_runtime"] != OCI_RUNTIME or runtime["oci_runtime_version"] != OCI_RUNTIME_VERSION:
            raise AdapterError("fw030.adapter.oci_runtime_mismatch", "OCI runtime identity does not match the observed profile", "unsupported")
        try:
            pulled = run(["podman", "pull", "--authfile", str(auth_file), "--platform", "linux/amd64", "--quiet", PINNED_IMAGE], min(timeout, 120))
        except AdapterError:
            if observation_sink:
                observation_sink({**host, **runtime, "image_pull": "attempted_outcome_unknown; permitted host access is limited to pinned-image retrieval; workload network remains disabled"})
            raise
        if observation_sink:
            image_pull = "completed" if pulled.returncode == 0 else "failed"
            observation_sink({**host, **runtime, "image_pull": f"{image_pull}; permitted host access is limited to pinned-image retrieval; workload network remains disabled"})
        if pulled.returncode != 0:
            raise AdapterError("fw030.adapter.image_unavailable", "the exact pinned workload image could not be retrieved")
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
            f"--timeout={timeout}", f"--workdir={request['workload']['working_directory']}",
            f"--tmpfs=/output:rw,noexec,nosuid,nodev,size={limit['disk_mb']}m,mode=1777",
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
                _verify_container(json.loads(inspect.stdout), request,
                                  (lambda value: observation_sink({"mount_observation": value})) if observation_sink else None)
            except (json.JSONDecodeError, TypeError):
                raise AdapterError("fw030.adapter.inspect_invalid", "container policy inspection was not valid JSON")
            case_bytes = _parse_workload_output(
                ran.stdout or "", min(MAX_OUTPUT_BYTES, request["policy"]["evidence"]["max_output_bytes"]),
                limit["disk_mb"],
            )
            try:
                parsed = _json_without_duplicates(case_bytes)
                if not isinstance(parsed, list) or any(not isinstance(item, dict) or set(item) != {"case_id", "outcome"} for item in parsed):
                    raise ValueError("shape")
                if any(not isinstance(item["case_id"], str) or not isinstance(item["outcome"], str) for item in parsed):
                    raise ValueError("type")
                if any(item["outcome"] not in {"passed", "failed", "skipped", "unknown"} for item in parsed):
                    raise ValueError("outcome")
            except (UnicodeError, json.JSONDecodeError, ValueError, TypeError, RecursionError):
                raise AdapterError("fw030.adapter.cases_invalid", "case results do not match the bounded output contract")
            cases = [{"case_id": item["case_id"], "outcome": item["outcome"]} for item in parsed]
            tmpfs_cases = [item for item in cases if item["case_id"] == "OUTPUT_TMPFS_EFFECTIVE"]
            if len(tmpfs_cases) != 1 or tmpfs_cases[0]["outcome"] != "unknown":
                raise AdapterError("fw030.adapter.tmpfs_observation_invalid", "workload did not provide exactly one unclaimed tmpfs evidence case")
            tmpfs_cases[0]["outcome"] = "passed"
            expected = request["policy"]["evidence"]["case_ids"]
            if sorted(item["case_id"] for item in cases) != sorted(expected) or any(item["outcome"] != "passed" for item in cases):
                raise AdapterError("fw030.adapter.case_failure", "one or more required synthetic boundary cases failed")
            execution = "succeeded"
        else:
            execution = "failed"
            stderr = (ran.stderr or "").lower()
            error_classes = (
                ("permission denied", "permission_denied"),
                ("operation not permitted", "operation_not_permitted"),
                ("invalid argument", "invalid_argument"),
                ("exec format error", "exec_format_error"),
                ("no such file or directory", "missing_runtime_path"),
                ("cannot set up namespace", "namespace_setup_failed"),
                ("executable file not found", "executable_missing"),
                ("creating container storage", "storage_setup_failed"),
                ("error creating container", "container_setup_failed"),
                ("failed to create container", "container_setup_failed"),
                ("oci runtime create failed", "oci_runtime_create_failed"),
                ("error during container create", "container_setup_failed"),
                ("crun: error", "oci_runtime_error"),
                ("newuidmap", "id_mapping_unavailable"),
                ("newgidmap", "id_mapping_unavailable"),
                ("no space left on device", "storage_exhausted"),
                ("cannot re-exec process", "runtime_reexec_failed"),
                ("unknown flag", "runtime_argument_rejected"),
                ("cannot connect", "runtime_service_unavailable"),
                ("invalid mount option", "mount_option_rejected"),
                ("unrecognized mount option", "mount_option_rejected"),
                ("unknown option", "runtime_argument_rejected"),
                ("resource limits are not supported", "resource_limit_unsupported"),
                ("cgroup v1", "cgroup_profile_unsupported"),
            )
            error_class = next((label for marker, label in error_classes if marker in stderr), "unclassified")
            hint = _safe_runtime_error_hint(ran.stderr or "")
            diagnostics.append(_diag("fw030.adapter.workload_failed", "$.states.execution", f"workload exited with status {ran.returncode}; runtime_error_class={error_class}; stderr_hint={hint}; case results are unavailable"))
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
                     "case_ids": ["INPUT_READONLY", "HOST_PATH_DENIED", "NETWORK_DISABLED", "SECRETS_NOT_INJECTED", "OUTPUT_BOUNDED", "OUTPUT_TMPFS_EFFECTIVE", "CAPABILITIES_DROPPED"]},
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


def _pilot_workload_script(sentinel: Path) -> str:
    return f'''#!/bin/sh
set -u
input_read=failed
if [ "$(cat /input/fixture.txt 2>/dev/null)" = synthetic-fixture ]; then input_read=passed; fi
input_readonly=failed
if [ "$input_read" = passed ] && ! touch /input/forbidden-write 2>/dev/null; then input_readonly=passed; fi
host_denied=failed
if ! cat "{sentinel}" >/dev/null 2>&1; then host_denied=passed; fi
network_disabled=unknown
if [ -x /bin/busybox ]; then
  if ! /bin/busybox wget -T 2 -qO- http://1.1.1.1/ >/dev/null 2>&1; then network_disabled=passed; else network_disabled=failed; fi
fi
secrets_disabled=failed
if [ -z "${{FW030_SECRET_SENTINEL-}}" ]; then secrets_disabled=passed; fi
output_bounded=passed
capabilities_dropped=passed
for field in CapEff CapPrm CapInh CapBnd CapAmb; do
  if ! awk -v key="$field:" '$1 == key {{ found=1; if (tolower($2) !~ /^0+$/) bad=1 }} END {{ if (!found || bad) exit 1 }}' /proc/self/status; then capabilities_dropped=failed; fi
done
mount_row=$(awk '$5 == "/output" {{ for (i=1;i<=NF;i++) if ($i == "-") {{ print $5 "|" $(i+1) "|" $6 "|" $(i+3); exit }} }}' /proc/self/mountinfo)
printf '%s' "$mount_row" > /output/tmpfs-mountinfo.txt 2>/dev/null || exit 70
cases='[{{"case_id":"INPUT_READONLY","outcome":"'${{input_readonly}}'"}},{{"case_id":"HOST_PATH_DENIED","outcome":"'${{host_denied}}'"}},{{"case_id":"NETWORK_DISABLED","outcome":"'${{network_disabled}}'"}},{{"case_id":"SECRETS_NOT_INJECTED","outcome":"'${{secrets_disabled}}'"}},{{"case_id":"OUTPUT_BOUNDED","outcome":"'${{output_bounded}}'"}},{{"case_id":"OUTPUT_TMPFS_EFFECTIVE","outcome":"unknown"}},{{"case_id":"CAPABILITIES_DROPPED","outcome":"'${{capabilities_dropped}}'"}}]'
printf '%s' "$cases" > /output/cases.json 2>/dev/null || exit 70
if [ "$(wc -c < /output/cases.json)" -gt 4096 ]; then
  output_bounded=failed
  cases='[{{"case_id":"INPUT_READONLY","outcome":"'${{input_readonly}}'"}},{{"case_id":"HOST_PATH_DENIED","outcome":"'${{host_denied}}'"}},{{"case_id":"NETWORK_DISABLED","outcome":"'${{network_disabled}}'"}},{{"case_id":"SECRETS_NOT_INJECTED","outcome":"'${{secrets_disabled}}'"}},{{"case_id":"OUTPUT_BOUNDED","outcome":"failed"}},{{"case_id":"OUTPUT_TMPFS_EFFECTIVE","outcome":"unknown"}},{{"case_id":"CAPABILITIES_DROPPED","outcome":"'${{capabilities_dropped}}'"}}]'
  printf '%s' "$cases" > /output/cases.json 2>/dev/null || exit 70
fi
printf 'FW030_OUTPUT_V1\n'
cat /output/cases.json 2>/dev/null || exit 70
printf '\n'
cat /output/tmpfs-mountinfo.txt 2>/dev/null || exit 70
printf '\n'
'''


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
    # The container runs as a distinct unprivileged UID. Make only the synthetic
    # input tree traversable/readable; the host-only sentinel remains under root.
    (root / "input").mkdir(mode=0o755)
    (root / "output").mkdir(mode=0o700)
    sentinel = root / "host-sentinel.txt"
    sentinel.write_text("synthetic-host-only-value", encoding="utf-8")
    (root / "input" / "fixture.txt").write_text("synthetic-fixture", encoding="utf-8")
    script = _pilot_workload_script(sentinel)
    (root / "input" / "workload.sh").write_text(script, encoding="utf-8")
    os.chmod(root / "input" / "fixture.txt", 0o644)
    os.chmod(root / "input" / "workload.sh", 0o644)
    env["FW030_PILOT_ROOT"] = str(root)
    try:
        raw, authorization = _pilot_request(env, root)
        observations: list[dict[str, str]] = []
        result = run_request(raw, authorization, env, observation_sink=observations.append)
        image_state: subprocess.CompletedProcess[str] | None = None
        try:
            image_state = _run(["podman", "image", "exists", PINNED_IMAGE], 15, env)
            if image_state.returncode == 0:
                removed_image = _run(["podman", "image", "rm", PINNED_IMAGE], 30, env)
                verified_absent = _run(["podman", "image", "exists", PINNED_IMAGE], 15, env)
                if removed_image.returncode != 0 or verified_absent.returncode != 1:
                    result["states"]["cleanup"] = "failed"
                    hint = _safe_runtime_error_hint(removed_image.stderr or "")
                    result["diagnostics"].append(_diag(
                        "fw030.adapter.image_cleanup_failed", "$.states.cleanup",
                        f"pinned synthetic image removal or absence verification failed; stderr_hint={hint}",
                    ))
            elif image_state.returncode != 1:
                result["states"]["cleanup"] = "unknown"
                hint = _safe_runtime_error_hint(image_state.stderr or "")
                result["diagnostics"].append(_diag(
                    "fw030.adapter.image_cleanup_unknown", "$.states.cleanup",
                    f"pinned synthetic image presence could not be determined; stderr_hint={hint}",
                ))
        except AdapterError:
            result["states"]["cleanup"] = "unknown"
            result["diagnostics"].append(_diag(
                "fw030.adapter.image_cleanup_unknown", "$.states.cleanup",
                "pinned synthetic image cleanup command failed; resource absence is not established",
            ))
    finally:
        temp_cleanup_errno: int | None = None
        cleanup_failure: dict[str, Any] = {}
        def record_cleanup_error(function: Callable[..., Any], path: str, exc: OSError) -> None:
            _record_cleanup_error(cleanup_failure, root, function, path, exc)
        try:
            shutil.rmtree(root, onexc=record_cleanup_error)
        except OSError as exc:
            temp_cleanup_errno = exc.errno
            _record_cleanup_error(cleanup_failure, root, shutil.rmtree, str(root), exc)
    if root.exists():
        result["states"]["cleanup"] = "failed"
        operation = str(cleanup_failure.get("operation", "unknown"))
        entry = str(cleanup_failure.get("entry", "unknown"))
        errno = int(cleanup_failure.get("errno", temp_cleanup_errno or 0))
        kind = str(cleanup_failure.get("entry_kind", "unknown"))
        mode = str(cleanup_failure.get("mode", "unknown"))
        owner = str(cleanup_failure.get("owner", "unknown"))
        group = str(cleanup_failure.get("group", "unknown"))
        detail = f"temporary pilot cleanup failed (first_operation={operation}; entry={entry}; errno={errno}; kind={kind}; mode={mode}; owner={owner}; group={group})"
        result["diagnostics"].append(_diag("fw030.adapter.temp_cleanup_failed", "$.states.cleanup", detail))
    report = {
        "schema": "FW030-PILOT-REPORT-1.0",
        "source": {"repository": env.get("GITHUB_REPOSITORY"), "revision": env.get("GITHUB_SHA")},
        "provider_run": {"run_id": env.get("GITHUB_RUN_ID"), "attempt": env.get("GITHUB_RUN_ATTEMPT"), "event": env.get("GITHUB_EVENT_NAME"), "ref": env.get("GITHUB_REF")},
        "profile": {"id": PROFILE_ID, "revision": PROFILE_REVISION, **(observations[-1] if observations else {})},
        "limitations": ["single hosted runner observation", "runner image header and ImageVersion may disagree", "Podman may escalate SIGTERM to SIGKILL; graceful termination is not claimed", "no complete host-isolation or production-readiness claim", "the profile permits host network access only for pinned-image retrieval; workload networking remains disabled", "evidence is emitted to this run log only; no retention or durability guarantee"],
        "invocation_result": result,
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if result["states"]["execution"] == "succeeded" and result["states"]["cleanup"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())

