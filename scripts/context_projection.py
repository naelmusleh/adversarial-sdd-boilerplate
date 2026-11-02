#!/usr/bin/env python3
"""Create auditable, temporary task-context copies without claiming isolation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


TOOL_ID = "adversarial-sdd-context-projection"
MANIFEST_NAME = "projection-manifest.json"
OWNER_NAME = ".context-projection-owner.json"
POLICY_SCHEMA_VERSION = 1
GATES = {
    "G-INTENT", "G-SETUP", "G-REQ", "G-FEAS", "G-COVERAGE",
    "G-CX", "G-ARCH", "G-IMPL", "G-RELEASE", "G-OPERATE",
}
PRUNED_DIRECTORIES = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".next",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build",
}
WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


class ProjectionError(ValueError):
    """Raised for an invalid policy, unsafe path, or failed projection."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProjectionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ProjectionError(f"cannot read JSON file {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProjectionError(f"JSON root must be an object: {label}")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ProjectionError(f"cannot read JSON file {path}: {exc}") from exc
    return _parse_json(raw, str(path))


def _validate_relative_path(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ProjectionError(f"{field} must be a non-empty POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ProjectionError(f"{field} escapes or aliases the repository root: {value!r}")
    for part in path.parts:
        if part.endswith((".", " ")) or any(ch in part for ch in '<>:"|?*'):
            raise ProjectionError(f"{field} is not portable across supported filesystems: {value!r}")
        if part.split(".", 1)[0].upper() in WINDOWS_RESERVED:
            raise ProjectionError(f"{field} uses a reserved path component: {value!r}")
    return path.as_posix()


def _validate_policy(policy: dict[str, Any]) -> dict[str, Any]:
    required_root = {"schema_version", "policy_id", "policy_revision", "contract_version", "profile_revision", "policies"}
    if set(policy) != required_root:
        raise ProjectionError(f"policy keys must be exactly: {', '.join(sorted(required_root))}")
    if type(policy["schema_version"]) is not int or policy["schema_version"] != POLICY_SCHEMA_VERSION:
        raise ProjectionError(f"unsupported policy schema_version: {policy['schema_version']!r}")
    for name in ("policy_id", "policy_revision", "contract_version", "profile_revision"):
        if not isinstance(policy[name], str) or not policy[name].strip():
            raise ProjectionError(f"policy {name} must be a non-empty string")
    if not isinstance(policy["policies"], list) or not policy["policies"]:
        raise ProjectionError("policy must declare at least one gate/role entry")
    seen: set[tuple[str, str]] = set()
    for index, entry in enumerate(policy["policies"]):
        label = f"policies[{index}]"
        if not isinstance(entry, dict) or set(entry) != {"gate", "role", "required_paths", "optional_paths", "excluded_paths"}:
            raise ProjectionError(f"{label} must contain exactly gate, role, required_paths, optional_paths, excluded_paths")
        gate, role = entry["gate"], entry["role"]
        if not isinstance(gate, str) or gate not in GATES:
            raise ProjectionError(f"{label}.gate is not a supported lifecycle gate")
        if not isinstance(role, str) or not role.strip():
            raise ProjectionError(f"{label}.role must be a non-empty string")
        key = (gate, role)
        if key in seen:
            raise ProjectionError(f"duplicate gate/role policy: {gate}/{role}")
        seen.add(key)
        for field in ("required_paths", "optional_paths", "excluded_paths"):
            values = entry[field]
            if not isinstance(values, list):
                raise ProjectionError(f"{label}.{field} must be an array")
            normalized = [_validate_relative_path(item, field=f"{label}.{field}") for item in values]
            if len(normalized) != len(set(normalized)):
                raise ProjectionError(f"{label}.{field} contains duplicate paths")
            entry[field] = normalized
        if not entry["required_paths"]:
            raise ProjectionError(f"{label}.required_paths must not be empty")
        overlap = set(entry["required_paths"]) & set(entry["excluded_paths"])
        if overlap:
            raise ProjectionError(f"required paths are explicitly excluded: {', '.join(sorted(overlap))}")
    return policy


def load_policy(policy_path: Path) -> dict[str, Any]:
    return _validate_policy(_load_json(policy_path))


def _git_metadata(root: Path) -> tuple[str, tuple[str, ...], list[str]]:
    try:
        revision = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
            check=True, capture_output=True, text=True,
        ).stdout.splitlines()
        tracked = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=True, capture_output=True,
        ).stdout.decode("utf-8", errors="strict").split("\0")
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        raise ProjectionError(f"cannot capture source Git revision and status: {exc}") from exc
    return revision, tuple(status), [item for item in tracked if item]


def _is_protected_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    name = parts[-1].casefold()
    if any(part.casefold() in {".git", "node_modules", ".aws", ".ssh"} for part in parts):
        return True
    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        return True
    if name in {"credentials", "secrets.json"}:
        return True
    return name.endswith((".pem", ".p12", ".pfx", ".key"))


def _contained(root: Path, candidate: Path, *, label: str) -> Path:
    try:
        lexical = candidate.absolute()
        relative = lexical.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ProjectionError(f"{label} resolves outside the authorized repository root") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ProjectionError(f"symlink path is not allowed: {current.relative_to(root).as_posix()}")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ProjectionError(f"{label} resolves outside the authorized repository root") from exc
    return resolved


def _expand_policy_path(root: Path, value: str, *, required: bool) -> list[Path]:
    path = root.joinpath(*PurePosixPath(value).parts)
    if not path.exists() and not path.is_symlink():
        if required:
            raise ProjectionError(f"required context path is missing: {value}")
        return []
    resolved = _contained(root, path, label="policy path")
    if resolved.is_file():
        return [resolved]
    if not resolved.is_dir():
        raise ProjectionError(f"context path is not a regular file or directory: {value}")
    files: list[Path] = []
    for current, dirs, names in os.walk(resolved, topdown=True, followlinks=False):
        directory = Path(current)
        kept_dirs: list[str] = []
        for name in sorted(dirs):
            child = directory / name
            rel = child.relative_to(root).as_posix()
            if child.is_symlink():
                raise ProjectionError(f"symlink inside selected directory: {rel}")
            if name in PRUNED_DIRECTORIES or _is_protected_path(rel):
                continue
            _contained(root, child, label="selected directory")
            kept_dirs.append(name)
        dirs[:] = kept_dirs
        for name in sorted(names):
            child = directory / name
            rel = child.relative_to(root).as_posix()
            if child.is_symlink():
                raise ProjectionError(f"symlink inside selected directory: {rel}")
            if _is_protected_path(rel):
                continue
            candidate = _contained(root, child, label="selected file")
            if not candidate.is_file():
                raise ProjectionError(f"non-regular file in selected directory: {rel}")
            files.append(candidate)
    if required and not files:
        raise ProjectionError(f"required directory has no eligible files: {value}")
    return files


def _matches(path: str, policies: list[str]) -> bool:
    return any(path == item or path.startswith(item.rstrip("/") + "/") for item in policies)


def _inventory(root: Path) -> tuple[list[str], list[dict[str, str]]]:
    files: list[str] = []
    skipped: list[dict[str, str]] = []
    for current, dirs, names in os.walk(root, topdown=True, followlinks=False):
        directory = Path(current)
        kept: list[str] = []
        for name in sorted(dirs):
            path = directory / name
            rel = path.relative_to(root).as_posix()
            if name in PRUNED_DIRECTORIES or _is_protected_path(rel):
                skipped.append({"path": rel, "reason": "generated-or-runtime-directory"})
            elif path.is_symlink():
                skipped.append({"path": rel, "reason": "symlink-not-followed"})
            else:
                kept.append(name)
        dirs[:] = kept
        for name in sorted(names):
            path = directory / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                skipped.append({"path": rel, "reason": "symlink-not-followed"})
            elif path.is_file():
                files.append(rel)
    return files, skipped


def _read_stable_file(root: Path, path: Path) -> tuple[bytes, int]:
    relative = path.relative_to(root).as_posix()
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise ProjectionError(f"cannot safely open selected file {relative}: {exc}") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ProjectionError(f"selected path is not a regular file: {relative}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(fd)
    finally:
        os.close(fd)
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
        raise ProjectionError(f"selected file changed while being read: {relative}")
    try:
        _contained(root, path, label="selected file")
    except ProjectionError as exc:
        raise ProjectionError(f"selected path changed during read: {relative}") from exc
    return b"".join(chunks), stat.S_IMODE(before.st_mode)


def create_projection(
    repo_root: Path,
    policy_path: Path,
    gate: str,
    role: str,
    output_parent: Path,
) -> dict[str, Any]:
    root = repo_root.resolve(strict=True)
    if not root.is_dir():
        raise ProjectionError("repository root must be a directory")
    try:
        policy_bytes = policy_path.read_bytes()
    except OSError as exc:
        raise ProjectionError(f"cannot read policy file {policy_path}: {exc}") from exc
    policy = _validate_policy(_parse_json(policy_bytes, str(policy_path)))
    matches = [item for item in policy["policies"] if item["gate"] == gate and item["role"] == role]
    if len(matches) != 1:
        raise ProjectionError(f"no unique policy exists for {gate}/{role}")
    selected_policy = matches[0]
    revision, initial_status, tracked_paths = _git_metadata(root)
    clean = not initial_status

    selected: dict[str, Path] = {}
    for path_string in selected_policy["required_paths"]:
        for path in _expand_policy_path(root, path_string, required=True):
            relative = path.relative_to(root).as_posix()
            _validate_relative_path(relative, field="repository path")
            if _is_protected_path(relative):
                raise ProjectionError(f"protected path cannot be projected: {relative}")
            selected[relative] = path
    missing_optional: list[str] = []
    for path_string in selected_policy["optional_paths"]:
        expanded = _expand_policy_path(root, path_string, required=False)
        if not expanded:
            missing_optional.append(path_string)
        for path in expanded:
            relative = path.relative_to(root).as_posix()
            _validate_relative_path(relative, field="repository path")
            if _is_protected_path(relative):
                raise ProjectionError(f"protected path cannot be projected: {relative}")
            selected[relative] = path

    selected_paths = {path.relative_to(root).as_posix(): path for path in selected.values()}
    for path in list(selected_paths):
        if _matches(path, selected_policy["excluded_paths"]):
            raise ProjectionError(f"selected context conflicts with an excluded path: {path}")
    folded: dict[str, str] = {}
    for path in selected_paths:
        previous = folded.setdefault(path.casefold(), path)
        if previous != path:
            raise ProjectionError(f"case-insensitive output collision: {previous} and {path}")

    inventory, skipped = _inventory(root)
    excluded: list[dict[str, str]] = list(skipped)
    included_set = set(selected_paths)
    for path in inventory:
        if path in included_set:
            continue
        if _matches(path, selected_policy["excluded_paths"]):
            reason = "explicitly-excluded-by-policy"
        elif _is_protected_path(path):
            reason = "protected-secret-or-credential-path"
        else:
            reason = "not-selected-by-policy"
        excluded.append({"path": path, "reason": reason})
    for path in missing_optional:
        excluded.append({"path": path, "reason": "optional-path-missing"})
    excluded.sort(key=lambda item: (item["path"].casefold(), item["path"], item["reason"]))
    initial_selected_hashes: dict[str, str] = {}
    for relative, source in selected_paths.items():
        data, _mode = _read_stable_file(root, source)
        initial_selected_hashes[relative] = hashlib.sha256(data).hexdigest()

    output_parent = output_parent.expanduser()
    if output_parent.is_symlink():
        raise ProjectionError("projection output parent must not be a symlink")
    output_parent = output_parent.resolve(strict=False)
    if output_parent == root or root in output_parent.parents:
        raise ProjectionError("projection output must be outside the source repository")
    output_parent.mkdir(parents=True, exist_ok=True)
    if output_parent.is_symlink() or not output_parent.is_dir():
        raise ProjectionError("projection output parent must be a non-symlink directory")
    parent_stat = output_parent.stat()
    effective_uid = getattr(os, "geteuid", None)
    if effective_uid is not None and parent_stat.st_uid != effective_uid():
        raise ProjectionError("projection output parent must be owned by the current user")
    if stat.S_IMODE(parent_stat.st_mode) & 0o022:
        raise ProjectionError("projection output parent must not be group- or world-writable")
    projection_id = str(uuid.uuid4())
    stage = output_parent / f".context-projection-staging-{projection_id}"
    destination = output_parent / f"context-projection-{projection_id}"
    stage.mkdir(mode=0o700)
    try:
        (stage / OWNER_NAME).write_text(
            json.dumps({"tool": TOOL_ID, "projection_id": projection_id}, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        included: list[dict[str, Any]] = []
        total_bytes = 0
        for relative, source in sorted(selected_paths.items(), key=lambda pair: pair[0].casefold()):
            data, source_mode = _read_stable_file(root, source)
            target = stage.joinpath(*PurePosixPath(relative).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(source_mode)
            digest = hashlib.sha256(data).hexdigest()
            total_bytes += len(data)
            included.append({
                "path": relative,
                "sha256": f"sha256:{digest}",
                "size_bytes": len(data),
                "mode_octal": format(source_mode, "04o"),
            })
        baseline_bytes = 0
        for relative in tracked_paths:
            candidate = root.joinpath(*PurePosixPath(relative).parts)
            try:
                contained = _contained(root, candidate, label="tracked baseline path")
                if contained.is_file():
                    baseline_bytes += contained.stat().st_size
            except OSError:
                continue
            except ProjectionError:
                continue
        manifest: dict[str, Any] = {
            "manifest_version": 1,
            "projection_id": projection_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "gate": gate,
            "role": role,
            "claim": "context-minimization-only",
            "access_isolation_verified": False,
            "source": {
                "repository_label": root.name,
                "git_revision": revision,
                "worktree_clean": clean,
            },
            "policy": {
                "policy_id": policy["policy_id"],
                "policy_revision": policy["policy_revision"],
                "contract_version": policy["contract_version"],
                "profile_revision": policy["profile_revision"],
                "sha256": f"sha256:{hashlib.sha256(policy_bytes).hexdigest()}",
            },
            "generator": {
                "id": TOOL_ID,
                "sha256": f"sha256:{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}",
            },
            "included_paths": included,
            "excluded_paths": excluded,
            "missing_optional_paths": missing_optional,
            "size_measurement": {
                "metric": "git-tracked-file-bytes",
                "baseline_bytes": baseline_bytes,
                "included_bytes": total_bytes,
                "reduction_percent": round((1 - total_bytes / baseline_bytes) * 100, 2) if baseline_bytes else None,
                "limitation": "Byte size is a context-size proxy, not a tokenizer token count or quality measure.",
            },
        }
        (stage / MANIFEST_NAME).write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        # Recheck at the publication boundary, after all copy and manifest work.
        post_revision, post_status, _ = _git_metadata(root)
        if post_revision != revision or post_status != initial_status:
            raise ProjectionError("source revision or worktree state changed during projection")
        for item in included:
            current = root.joinpath(*PurePosixPath(item["path"]).parts)
            data, _mode = _read_stable_file(root, current)
            copied_hash = item["sha256"].removeprefix("sha256:")
            if copied_hash != initial_selected_hashes[item["path"]] or hashlib.sha256(data).hexdigest() != copied_hash:
                raise ProjectionError(f"source file changed during projection: {item['path']}")
        try:
            if policy_path.read_bytes() != policy_bytes:
                raise ProjectionError("policy file changed during projection")
        except OSError as exc:
            raise ProjectionError(f"policy file became unavailable during projection: {exc}") from exc
        stage.rename(destination)
    except BaseException:
        # Only this invocation's uniquely named staging directory is removed.
        if stage.exists() and not stage.is_symlink():
            shutil.rmtree(stage)
        raise
    manifest["projection_path"] = str(destination)
    return manifest


def cleanup_projection(projection_path: Path) -> None:
    target = projection_path.expanduser().absolute()
    recovery_quarantine = False
    if not target.exists() and not target.is_symlink():
        prefix = ".context-projection-staging-" if target.name.startswith(".context-projection-staging-") else "context-projection-"
        supplied_id = target.name.removeprefix(prefix)
        try:
            projection_uuid = str(uuid.UUID(supplied_id))
        except (ValueError, AttributeError):
            projection_uuid = ""
        if projection_uuid:
            quarantine_candidate = target.parent / f".context-projection-cleanup-{projection_uuid}"
            if quarantine_candidate.exists() and not quarantine_candidate.is_symlink():
                target = quarantine_candidate
                recovery_quarantine = True
    current = Path(target.anchor)
    for component in target.parts[1:]:
        current = current / component
        if current.is_symlink():
            raise ProjectionError("cleanup target path must not contain symlinks")
    if target.is_symlink() or not target.is_dir():
        raise ProjectionError("cleanup target must be a real projection directory")
    try:
        resolved = target.resolve(strict=True)
    except OSError as exc:
        raise ProjectionError(f"cleanup target cannot be resolved safely: {exc}") from exc
    if resolved != target:
        raise ProjectionError("cleanup target path does not match its canonical path")
    staging = target.name.startswith(".context-projection-staging-")
    # Walk from the filesystem root with O_NOFOLLOW at every component. A plain
    # open(parent_path, O_NOFOLLOW) protects only the last component.
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    parent_fd = os.open(target.anchor, directory_flags)
    try:
        for component in target.parent.parts[1:]:
            next_fd = os.open(component, directory_flags, dir_fd=parent_fd)
            os.close(parent_fd)
            parent_fd = next_fd
        target_fd = os.open(target.name, directory_flags, dir_fd=parent_fd)
        try:
            opened_stat = os.fstat(target_fd)
            named_stat = os.stat(target.name, dir_fd=parent_fd, follow_symlinks=False)
            if (opened_stat.st_dev, opened_stat.st_ino) != (named_stat.st_dev, named_stat.st_ino):
                raise ProjectionError("cleanup target changed during ownership verification")
            owner = _read_json_at(target_fd, OWNER_NAME)
            if owner.get("tool") != TOOL_ID or not owner.get("projection_id"):
                raise ProjectionError("cleanup target is not a projection owned by this tool")
            try:
                projection_uuid = str(uuid.UUID(owner["projection_id"]))
            except (ValueError, TypeError, AttributeError) as exc:
                raise ProjectionError("projection ownership ID is invalid") from exc
            expected_names = {f".context-projection-staging-{projection_uuid}"} if staging else {
                f"context-projection-{projection_uuid}", f".context-projection-cleanup-{projection_uuid}"
            }
            if target.name not in expected_names:
                raise ProjectionError("cleanup target name does not match its projection ownership ID")
            if not staging:
                manifest = _read_json_at(target_fd, MANIFEST_NAME)
                if owner.get("projection_id") != manifest.get("projection_id"):
                    raise ProjectionError("projection ownership does not match its manifest")
            current_stat = os.stat(target.name, dir_fd=parent_fd, follow_symlinks=False)
            if (opened_stat.st_dev, opened_stat.st_ino) != (current_stat.st_dev, current_stat.st_ino):
                raise ProjectionError("cleanup target changed before removal")
            # Atomically move the name to a fresh quarantine, then prove the moved
            # object is the directory whose ownership was checked before deleting it.
            quarantine = target.name if recovery_quarantine else f".context-projection-cleanup-{projection_uuid}"
            if not recovery_quarantine:
                if os.path.lexists(target.parent / quarantine):
                    raise ProjectionError("a recoverable cleanup directory already exists")
                os.rename(target.name, quarantine, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
            moved_fd = os.open(quarantine, directory_flags, dir_fd=parent_fd)
            try:
                moved_stat = os.fstat(moved_fd)
                if (opened_stat.st_dev, opened_stat.st_ino) != (moved_stat.st_dev, moved_stat.st_ino):
                    try:
                        os.rename(quarantine, target.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
                    except OSError:
                        pass
                    raise ProjectionError("cleanup target was replaced; refusing to remove the replacement")
            finally:
                os.close(moved_fd)
            shutil.rmtree(quarantine, dir_fd=parent_fd)
        finally:
            os.close(target_fd)
    finally:
        os.close(parent_fd)


def _read_json_at(directory_fd: int, name: str) -> dict[str, Any]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(name, flags, dir_fd=directory_fd)
    except OSError as exc:
        if name == OWNER_NAME:
            raise ProjectionError("cleanup target is not a projection owned by this tool") from exc
        raise ProjectionError(f"projection ownership file is unavailable: {name}") from exc
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ProjectionError(f"projection ownership file is not regular: {name}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        return _parse_json(b"".join(chunks), f"projection/{name}")
    finally:
        os.close(fd)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create", help="create a policy-scoped context copy")
    create.add_argument("--repo-root", type=Path, default=Path.cwd())
    create.add_argument("--policy", type=Path, required=True)
    create.add_argument("--gate", required=True, choices=sorted(GATES))
    create.add_argument("--role", required=True)
    create.add_argument("--output-parent", type=Path, default=Path(tempfile.gettempdir()))
    cleanup = commands.add_parser("cleanup", help="remove one tool-owned projection")
    cleanup.add_argument("--projection", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            manifest = create_projection(args.repo_root, args.policy, args.gate, args.role, args.output_parent)
            print(json.dumps(manifest, indent=2, sort_keys=True))
        else:
            cleanup_projection(args.projection)
            print(f"Removed projection: {args.projection}")
    except (ProjectionError, OSError) as exc:
        print(f"context projection error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
