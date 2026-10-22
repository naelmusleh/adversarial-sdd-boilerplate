from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import unittest
import uuid
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import scripts.context_projection as projection_module
from scripts.context_projection import (
    OWNER_NAME,
    TOOL_ID,
    ProjectionError,
    cleanup_projection,
    create_projection,
    load_policy,
)


@contextmanager
def assert_raises(exception_type: type[Exception], match: str):
    try:
        yield
    except exception_type as error:
        assert re.search(match, str(error)), f"{error!s} did not match {match!r}"
    else:
        raise AssertionError(f"expected {exception_type.__name__}")


GATES = [
    "G-INTENT", "G-SETUP", "G-REQ", "G-FEAS", "G-COVERAGE",
    "G-CX", "G-ARCH", "G-IMPL", "G-RELEASE", "G-OPERATE",
]
ROLES = ["implementation-agent", "independent-reviewer"]


def make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "source repository"
    root.mkdir()
    files = {
        "common.md": "required common contract\nAcceptance: FW-027-AC-01\nAcceptance: FW-027-AC-02\nAcceptance: FW-027-AC-03\nAcceptance: FW-027-AC-05\nAcceptance: FW-027-AC-06\n",
        "roles/implementation-agent.md": "implementation role context\n",
        "roles/independent-reviewer.md": "review role context\n",
        "unrelated/bulk.txt": "unrelated " * 30000,
        "private-data/fixture.txt": "must be explicitly excluded\n",
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Context Test"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "context-test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(root), "add", "common.md", "roles", "unrelated", "private-data"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture source"], check=True)
    (root / ".env").write_text("private=never-copy\n", encoding="utf-8")
    return root


def write_policy(path: Path, *, policies: list[dict] | None = None) -> Path:
    entries = policies if policies is not None else [
        {
            "gate": gate,
            "role": role,
            "required_paths": ["common.md", f"roles/{role}.md"],
            "optional_paths": ["optional.md"],
            "excluded_paths": ["private-data"],
        }
        for gate in GATES
        for role in ROLES
    ]
    policy = {
        "schema_version": 1,
        "policy_id": "CONTEXT-POLICY-TEST-001",
        "policy_revision": "test-1",
        "contract_version": "context-projection-v1",
        "profile_revision": "test-profile-1",
        "policies": entries,
    }
    path.write_text(json.dumps(policy, indent=2), encoding="utf-8")
    return path


def test_all_gate_role_policies_create_auditable_context_only_views(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    policy = write_policy(tmp_path / "policy.json")
    before = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink() and ".git" not in path.parts
    }
    output_parent = tmp_path / "projections"

    for gate in GATES:
        for role in ROLES:
            manifest = create_projection(root, policy, gate, role, output_parent)
            projection = Path(manifest["projection_path"])
            assert manifest["gate"] == gate
            assert manifest["role"] == role
            assert manifest["claim"] == "context-minimization-only"
            assert manifest["access_isolation_verified"] is False
            assert manifest["source"]["git_revision"]
            assert manifest["source"]["worktree_clean"] is False  # the untracked .env is visible
            assert manifest["policy"]["contract_version"] == "context-projection-v1"
            assert manifest["policy"]["sha256"].startswith("sha256:")
            assert manifest["generator"]["sha256"].startswith("sha256:")
            assert {item["path"] for item in manifest["included_paths"]} == {
                "common.md", f"roles/{role}.md"
            }
            assert all(item["sha256"].startswith("sha256:") for item in manifest["included_paths"])
            projected_contract = (projection / "common.md").read_text(encoding="utf-8")
            for acceptance_id in ("FW-027-AC-01", "FW-027-AC-02", "FW-027-AC-03", "FW-027-AC-05", "FW-027-AC-06"):
                assert acceptance_id in projected_contract
            excluded = {item["path"]: item["reason"] for item in manifest["excluded_paths"]}
            assert excluded["unrelated/bulk.txt"] == "not-selected-by-policy"
            assert excluded["private-data/fixture.txt"] == "explicitly-excluded-by-policy"
            assert excluded[".env"] == "protected-secret-or-credential-path"
            assert not (projection / ".env").exists()
            assert manifest["size_measurement"]["metric"] == "git-tracked-file-bytes"
            assert manifest["size_measurement"]["reduction_percent"] > 0
            assert "not a tokenizer token count" in manifest["size_measurement"]["limitation"]
            cleanup_projection(projection)
            assert not projection.exists()

    after = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink() and ".git" not in path.parts
    }
    assert before == after


def test_missing_policy_role_or_required_context_fails_closed(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    policy_path = write_policy(
        tmp_path / "policy.json",
        policies=[{
            "gate": "G-IMPL", "role": "implementer",
            "required_paths": ["missing/acceptance.md"],
            "optional_paths": [], "excluded_paths": [],
        }],
    )
    with assert_raises(ProjectionError, match="no unique policy"):
        create_projection(root, policy_path, "G-IMPL", "reviewer", tmp_path / "out")
    with assert_raises(ProjectionError, match="required context path is missing"):
        create_projection(root, policy_path, "G-IMPL", "implementer", tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_policy_rejects_absolute_parent_and_non_posix_paths(tmp_path: Path) -> None:
    for unsafe in ("../outside.txt", "/outside.txt", "roles\\escape.md"):
        policy = write_policy(
            tmp_path / "policy.json",
            policies=[{
                "gate": "G-IMPL", "role": "implementer",
                "required_paths": [unsafe], "optional_paths": [], "excluded_paths": [],
            }],
        )
        with assert_raises(ProjectionError, match="relative path|escapes"):
            load_policy(policy)

    for malformed in ({"schema_version": True}, {"gate": []}):
        entry = {
            "gate": "G-IMPL", "role": "implementer", "required_paths": ["common.md"],
            "optional_paths": [], "excluded_paths": [],
        }
        if "gate" in malformed:
            entry.update(malformed)
            schema_version = 1
        else:
            schema_version = malformed["schema_version"]
        policy = write_policy(
            tmp_path / "policy.json",
            policies=[entry],
        )
        payload = json.loads(policy.read_text(encoding="utf-8"))
        payload["schema_version"] = schema_version
        policy.write_text(json.dumps(payload), encoding="utf-8")
        with assert_raises(ProjectionError, match="schema_version|gate"):
            load_policy(policy)


def test_selected_symlink_escape_and_required_exclusion_are_rejected(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    external = tmp_path / "outside.txt"
    external.write_text("outside", encoding="utf-8")
    (root / "linked.txt").symlink_to(external)
    policy_path = write_policy(
        tmp_path / "policy.json",
        policies=[{
            "gate": "G-IMPL", "role": "implementer",
            "required_paths": ["linked.txt"], "optional_paths": [], "excluded_paths": [],
        }],
    )
    with assert_raises(ProjectionError, match="symlink"):
        create_projection(root, policy_path, "G-IMPL", "implementer", tmp_path / "out")

    policy_path = write_policy(
        tmp_path / "policy.json",
        policies=[{
            "gate": "G-IMPL", "role": "implementer",
            "required_paths": ["common.md"], "optional_paths": [],
            "excluded_paths": ["common.md"],
        }],
    )
    with assert_raises(ProjectionError, match="required paths are explicitly excluded"):
        load_policy(policy_path)


def test_concurrent_projection_creation_is_unique_and_cleanup_is_scoped(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    policy = write_policy(tmp_path / "policy.json")
    out = tmp_path / "projections"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(
            lambda _: create_projection(root, policy, "G-IMPL", ROLES[0], out), range(2)
        ))
    paths = [Path(result["projection_path"]) for result in results]
    assert len(set(paths)) == 2
    for path in paths:
        cleanup_projection(path)
    assert list(out.iterdir()) == []


def test_cleanup_recovers_owned_interrupted_staging_and_refuses_foreign_dir(tmp_path: Path) -> None:
    interrupted_id = str(uuid.uuid4())
    staging = tmp_path.resolve() / f".context-projection-staging-{interrupted_id}"
    staging.mkdir()
    (staging / OWNER_NAME).write_text(
        json.dumps({"tool": TOOL_ID, "projection_id": interrupted_id}), encoding="utf-8"
    )
    cleanup_projection(staging)
    assert not staging.exists()

    foreign = tmp_path.resolve() / "foreign"
    foreign.mkdir()
    with assert_raises(ProjectionError, match="owned by this tool"):
        cleanup_projection(foreign)


def test_cleanup_rejects_symlinked_ancestor(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    policy = write_policy(tmp_path / "policy.json")
    output = tmp_path / "projections"
    manifest = create_projection(root, policy, "G-IMPL", ROLES[0], output)
    projection = Path(manifest["projection_path"])
    alias = tmp_path / "alias"
    alias.symlink_to(output, target_is_directory=True)
    with assert_raises(ProjectionError, match="must not contain symlinks"):
        cleanup_projection(alias / projection.name)
    assert projection.exists()
    cleanup_projection(projection)


def test_cleanup_recovers_quarantined_projection(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    policy = write_policy(tmp_path / "policy.json")
    output = tmp_path / "projections"
    manifest = create_projection(root, policy, "G-IMPL", ROLES[0], output)
    projection = Path(manifest["projection_path"])
    quarantine = projection.parent / f".context-projection-cleanup-{manifest['projection_id']}"
    projection.rename(quarantine)
    cleanup_projection(projection)
    assert not quarantine.exists()


def test_concurrent_cleanup_of_one_projection_is_bounded(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    policy = write_policy(tmp_path / "policy.json")
    output = tmp_path / "projections"
    manifest = create_projection(root, policy, "G-IMPL", ROLES[0], output)
    projection = Path(manifest["projection_path"])

    def cleanup_once() -> str:
        try:
            cleanup_projection(projection)
            return "removed"
        except (ProjectionError, OSError):
            return "already-removed-or-in-progress"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: cleanup_once(), range(2)))
    assert "removed" in results
    assert not projection.exists()
    assert not list(output.iterdir())


def test_source_change_during_projection_discards_staged_view(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    policy = write_policy(tmp_path / "policy.json")
    output = tmp_path / "projections"
    original_read = projection_module._read_stable_file
    common_reads = 0

    def mutate_after_copy(repo_root: Path, source: Path):
        nonlocal common_reads
        result = original_read(repo_root, source)
        if source.name == "common.md":
            common_reads += 1
            if common_reads == 2:  # preflight, then mutate immediately after copied bytes are read
                source.write_text("changed during projection\n", encoding="utf-8")
        return result

    with patch.object(projection_module, "_read_stable_file", side_effect=mutate_after_copy):
        with assert_raises(ProjectionError, match="source revision or worktree state changed|source file changed"):
            create_projection(root, policy, "G-IMPL", ROLES[0], output)
    assert not output.exists() or not list(output.iterdir())


def test_policy_change_during_projection_discards_staged_view(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    policy = write_policy(tmp_path / "policy.json")
    output = tmp_path / "projections"
    original_read_bytes = Path.read_bytes
    policy_reads = 0

    def mutate_policy(path: Path) -> bytes:
        nonlocal policy_reads
        if path == policy:
            policy_reads += 1
            if policy_reads == 2:  # final publication check
                policy.write_text("{}\n", encoding="utf-8")
        return original_read_bytes(path)

    with patch.object(Path, "read_bytes", mutate_policy):
        with assert_raises(ProjectionError, match="policy file changed"):
            create_projection(root, policy, "G-IMPL", ROLES[0], output)
    assert not output.exists() or not list(output.iterdir())


def test_projection_cannot_be_created_inside_source_repository(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    policy = write_policy(tmp_path / "policy.json")
    with assert_raises(ProjectionError, match="outside the source repository"):
        create_projection(root, policy, "G-IMPL", ROLES[0], root / ".projection-output")
    assert not (root / ".projection-output").exists()


def test_projection_refuses_shared_writable_output_parent(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    policy = write_policy(tmp_path / "policy.json")
    output = tmp_path / "shared-output"
    output.mkdir(mode=0o700)
    output.chmod(0o777)
    try:
        with assert_raises(ProjectionError, match="must not be group- or world-writable"):
            create_projection(root, policy, "G-IMPL", ROLES[0], output)
        assert list(output.iterdir()) == []
    finally:
        output.chmod(0o700)


class ContextProjectionTests(unittest.TestCase):
    def _run_scenario(self, scenario) -> None:
        with tempfile.TemporaryDirectory() as directory:
            scenario(Path(directory))

    def test_all_gate_role_policies_create_auditable_context_only_views(self) -> None:
        self._run_scenario(test_all_gate_role_policies_create_auditable_context_only_views)

    def test_missing_policy_role_or_required_context_fails_closed(self) -> None:
        self._run_scenario(test_missing_policy_role_or_required_context_fails_closed)

    def test_policy_rejects_absolute_parent_and_non_posix_paths(self) -> None:
        self._run_scenario(test_policy_rejects_absolute_parent_and_non_posix_paths)

    def test_selected_symlink_escape_and_required_exclusion_are_rejected(self) -> None:
        self._run_scenario(test_selected_symlink_escape_and_required_exclusion_are_rejected)

    def test_concurrent_projection_creation_is_unique_and_cleanup_is_scoped(self) -> None:
        self._run_scenario(test_concurrent_projection_creation_is_unique_and_cleanup_is_scoped)

    def test_cleanup_recovers_owned_interrupted_staging_and_refuses_foreign_dir(self) -> None:
        self._run_scenario(test_cleanup_recovers_owned_interrupted_staging_and_refuses_foreign_dir)

    def test_cleanup_rejects_symlinked_ancestor(self) -> None:
        self._run_scenario(test_cleanup_rejects_symlinked_ancestor)

    def test_cleanup_recovers_quarantined_projection(self) -> None:
        self._run_scenario(test_cleanup_recovers_quarantined_projection)

    def test_concurrent_cleanup_of_one_projection_is_bounded(self) -> None:
        self._run_scenario(test_concurrent_cleanup_of_one_projection_is_bounded)

    def test_source_change_during_projection_discards_staged_view(self) -> None:
        self._run_scenario(test_source_change_during_projection_discards_staged_view)

    def test_policy_change_during_projection_discards_staged_view(self) -> None:
        self._run_scenario(test_policy_change_during_projection_discards_staged_view)

    def test_projection_cannot_be_created_inside_source_repository(self) -> None:
        self._run_scenario(test_projection_cannot_be_created_inside_source_repository)

    def test_projection_refuses_shared_writable_output_parent(self) -> None:
        self._run_scenario(test_projection_refuses_shared_writable_output_parent)
