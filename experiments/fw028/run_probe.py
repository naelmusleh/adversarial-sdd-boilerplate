from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def digest_paths(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def execute(command: list[str], cwd: Path, expected: str, timeout: int = 300) -> tuple[int, str]:
    started = time.monotonic()
    completed = subprocess.run(
        command, cwd=cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, timeout=timeout,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    source = next((candidate for candidate in [cwd / "src/classify.ts", cwd / "src/classify.py", cwd / "src/lib.rs"] if candidate.exists()), None)
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest() if source else None
    print(json.dumps({"command": command, "cwd": str(cwd.name), "exit": completed.returncode, "elapsed_seconds": round(time.monotonic() - started, 3), "source_sha256": source_digest, "stdout_tail": completed.stdout[-2500:]}))
    if expected == "pass" and completed.returncode != 0:
        raise RuntimeError(f"expected command to pass: {command}")
    if expected == "fail" and completed.returncode == 0:
        raise RuntimeError(f"expected command to fail: {command}")
    return completed.returncode, completed.stdout


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def verify_fixture_manifest(profile: str, root: Path, inputs: list[Path]) -> None:
    manifest = json.loads((Path(__file__).with_name("fixture-manifest.json")).read_text())
    expected = sorted(manifest["profiles"][profile])
    actual = sorted(path.relative_to(root).as_posix() for path in inputs)
    if expected != actual:
        raise RuntimeError(f"fixture manifest mismatch: expected {expected}, actual {actual}")


def generated_file_probe(root: Path) -> None:
    generated = root / "src/generated/build_stamp.py"
    write(generated, "# generated\nSTAMP = 'fixture'\n")
    policy = {"src/generated/build_stamp.py": {"treatment": "exclude", "reason": "generated fixture"}}

    def check(policy_map: dict[str, dict[str, str]]) -> tuple[list[str], list[str]]:
        actual = sorted(str(p.relative_to(root)) for p in (root / "src/generated").glob("*.py"))
        missing = sorted(set(actual) - set(policy_map))
        if missing:
            raise ValueError("unclassified generated path: " + ", ".join(missing))
        included = sorted(p for p in actual if policy_map[p]["treatment"] == "include")
        excluded = sorted(p for p in actual if policy_map[p]["treatment"] == "exclude")
        return included, excluded

    included, excluded = check(policy)
    assert included == []
    assert excluded == ["src/generated/build_stamp.py"]
    includes, excluded_again = check({"src/generated/build_stamp.py": {"treatment": "include", "reason": "measured fixture"}})
    assert includes == ["src/generated/build_stamp.py"] and excluded_again == []
    try:
        check({})
    except ValueError as error:
        assert str(error) == "unclassified generated path: src/generated/build_stamp.py"
    else:
        raise AssertionError("undeclared generated file was not rejected")
    print(json.dumps({"generated_include": includes, "generated_exclude": excluded, "undeclared": "rejected"}))


def trace_probe(root: Path) -> None:
    repo = root / "trace-repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "config", "user.name", "FW-028 fixture"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=repo, check=True)
    write(repo / "src/policy.py", "VALUE = 1\n")
    write(repo / "src/ui/card.tsx", "export const Card = 1;\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture base"], cwd=repo, check=True)
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    write(repo / "src/policy.py", "VALUE = 2\n")
    write(repo / "src/ui/card.tsx", "export const Card = 2;\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture change"], cwd=repo, check=True)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    changed = sorted(subprocess.check_output(
        ["git", "diff", "--name-only", f"{base}..{head}"], cwd=repo, text=True
    ).splitlines())

    required_criteria = {"AC-1", "AC-5"}
    required_checks = {"unit", "trace"}
    manifest = {
        "source_commit": head,
        "task_id": "FW-TASK-028",
        "criterion_ids": ["AC-1", "AC-5"],
        "changed_paths": changed,
        "path_to_criteria": {
            "src/policy.py": ["AC-1"],
            "src/ui/card.tsx": ["AC-5"],
        },
        "required_checks": {"unit": "success", "trace": "success"},
        "generated_paths": {"src/generated/build_stamp.py": {"treatment": "exclude", "reason": "fixture"}},
        "exceptions": [],
    }

    def diagnostics(data: dict) -> list[str]:
        errors: list[str] = []
        if data.get("source_commit") != head:
            errors.append("stale source_commit")
        if set(data.get("criterion_ids", [])) != required_criteria:
            errors.append("missing or unexpected criterion ID")
        mapped = set(data.get("path_to_criteria", {}))
        for path in changed:
            if path not in mapped and not data.get("exceptions"):
                errors.append("unmapped changed path " + path)
        if set(data.get("changed_paths", [])) != set(changed):
            errors.append("changed path set mismatch")
        checks = data.get("required_checks", {})
        for check in required_checks:
            if checks.get(check) != "success":
                errors.append("missing or failed required check " + check)
        if data.get("exceptions"):
            errors.append("exception authorization unavailable without independently verified provider review")
        return errors

    assert diagnostics(manifest) == []
    cases = []
    broken = json.loads(json.dumps(manifest))
    broken["source_commit"] = base
    cases.append((broken, "stale source_commit"))
    broken = json.loads(json.dumps(manifest))
    broken["criterion_ids"].remove("AC-5")
    cases.append((broken, "missing or unexpected criterion ID"))
    broken = json.loads(json.dumps(manifest))
    del broken["path_to_criteria"]["src/ui/card.tsx"]
    cases.append((broken, "unmapped changed path src/ui/card.tsx"))
    broken = json.loads(json.dumps(manifest))
    del broken["required_checks"]["trace"]
    cases.append((broken, "missing or failed required check trace"))
    broken = json.loads(json.dumps(manifest))
    broken["exceptions"] = [{"path": "src/ui/card.tsx", "approved_by": "self-asserted"}]
    cases.append((broken, "exception authorization unavailable"))
    for data, expected in cases:
        result = diagnostics(data)
        assert any(expected in error for error in result), (expected, result)
        print(json.dumps({"expected_diagnostic": expected, "actual": result}))
    print(json.dumps({"valid_trace": "accepted", "changed_paths": changed, "exception_authorization": "unavailable; fail closed"}))


def make_web(root: Path) -> list[Path]:
    write(root / "package.json", json.dumps({
        "private": True, "type": "module",
        "scripts": {"test": "vitest run"},
        "devDependencies": {
            "@vitest/coverage-v8": "5.0.5",
            "typescript": "5.9.3",
            "vitest": "5.0.5",
        },
    }, indent=2) + "\n")
    write(root / "tsconfig.json", json.dumps({"compilerOptions": {"target": "ES2022", "module": "ESNext", "moduleResolution": "Bundler", "strict": True, "skipLibCheck": True}, "include": ["src", "tests"]}, indent=2))
    write(root / "vitest.config.ts", "import { defineConfig } from 'vitest/config';\nexport default defineConfig({ test: { coverage: { provider: 'v8', reporter: ['text', 'json'] } } });\n")
    write(root / "stryker.config.json", json.dumps({"$schema": "./node_modules/@stryker-mutator/core/schema/stryker-schema.json", "testRunner": "vitest", "plugins": ["@stryker-mutator/vitest-runner"], "mutate": ["src/classify.ts"], "vitest": {"configFile": "vitest.config.ts"}, "reporters": ["clear-text", "json"], "concurrency": 1}, indent=2))
    write(root / "expected_exports.json", '["classify"]\n')
    write(root / "src/classify.ts", "export function classify(n: number): string { return n > 0 ? 'positive' : 'nonpositive'; }\n")
    write(root / "src/public_api.ts", "export function classify(n: number): string { return n > 0 ? 'positive' : 'nonpositive'; }\n")
    write(root / "tests/quality.test.ts", """import { expect, it } from 'vitest';
import { classify } from '../src/classify';
it('call-only', () => { classify(1); });
it('assertion', () => { expect(classify(1)).toBe('positive'); expect(classify(0)).toBe('nonpositive'); });
""")
    write(root / "tests/exports.test.ts", """import { expect, it } from 'vitest';
import { readFile } from 'node:fs/promises';
const expected: string[] = JSON.parse(await readFile(new URL('../expected_exports.json', import.meta.url), 'utf8'));
const api = await import('../src/public_api');
it('public exports match independent manifest', () => { for (const name of expected) expect(Object.keys(api)).toContain(name); });
""")
    return [root / name for name in ["package.json", "tsconfig.json", "vitest.config.ts", "stryker.config.json", "src/classify.ts", "src/public_api.ts", "expected_exports.json", "tests/quality.test.ts", "tests/exports.test.ts"]]


def make_python(root: Path) -> list[Path]:
    write(root / "expected_exports.json", '["classify"]\n')
    write(root / "src/__init__.py", "")
    write(root / "src/classify.py", "def classify(n: int) -> str:\n    return 'positive' if n > 0 else 'nonpositive'\n")
    write(root / "src/public_api.py", "def classify(n: int) -> str:\n    return 'positive' if n > 0 else 'nonpositive'\n")
    write(root / "tests/test_quality.py", """from src.classify import classify

def test_call_only():
    classify(1)

def test_assertion():
    assert classify(1) == "positive"
    assert classify(0) == "nonpositive"
""")
    write(root / "tests/test_exports.py", """import importlib
import json
from pathlib import Path

def test_public_exports_match_independent_manifest():
    expected = json.loads(Path("expected_exports.json").read_text())
    module = importlib.import_module("src.public_api")
    for name in expected:
        assert hasattr(module, name), f"missing public export: {name}"
""")
    write(root / "pyproject.toml", '[tool.mutmut]\npaths_to_mutate = "src/classify.py"\ntests_dir = "tests"\n')
    return [root / name for name in ["pyproject.toml", "src/__init__.py", "src/classify.py", "src/public_api.py", "expected_exports.json", "tests/test_quality.py", "tests/test_exports.py"]]


def make_rust(root: Path) -> list[Path]:
    write(root / "Cargo.toml", '[package]\nname = "fw028_probe"\nversion = "0.1.0"\nedition = "2024"\n')
    write(root / "expected_exports.json", '["classify"]\n')
    write(root / "src/lib.rs", "pub fn classify(n: i32) -> &'static str { if n > 0 { \"positive\" } else { \"nonpositive\" } }\n")
    write(root / "tests/quality_fixture.rs", """use fw028_probe::classify;

#[test]
fn call_only() { let _ = classify(1); }

#[test]
fn assertion() {
    assert_eq!(classify(1), "positive");
    assert_eq!(classify(0), "nonpositive");
}
""")
    write(root / "tests/export_consumer.rs", """use fw028_probe::classify;

#[test]
fn expected_public_export_is_available() {
    let expected = include_str!("../expected_exports.json");
    assert!(expected.contains("classify"));
    assert_eq!(classify(1), "positive");
}
""")
    return [root / name for name in ["Cargo.toml", "src/lib.rs", "expected_exports.json", "tests/quality_fixture.rs", "tests/export_consumer.rs"]]


def web_probe(work: Path) -> None:
    inputs = make_web(work)
    verify_fixture_manifest("web", work, inputs)
    print(json.dumps({"profile": "web", "node": subprocess.check_output(["node", "--version"], text=True).strip(), "npm": subprocess.check_output(["npm", "--version"], text=True).strip(), "fixture_sha256": digest_paths(inputs)}))
    execute(["npm", "install", "--package-lock-only", "--ignore-scripts", "--no-audit", "--no-fund"], work, "pass", 600)
    execute(["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"], work, "pass", 600)
    execute(["npm", "exec", "--", "vitest", "run", "tests/quality.test.ts", "-t", "call-only", "--coverage"], work, "pass", 300)
    inputs.append(work / "package-lock.json")
    lock_digest = hashlib.sha256((work / "package-lock.json").read_bytes()).hexdigest()
    print(json.dumps({"profile": "web", "package_lock_sha256": lock_digest}))
    pristine = digest_paths(inputs)
    execute(["npm", "exec", "--", "vitest", "run", "tests/quality.test.ts", "-t", "assertion", "--coverage"], work, "pass", 300)
    execute(["npm", "exec", "--", "vitest", "run", "tests/quality.test.ts", "-t", "call-only"], work, "pass")
    execute(["npm", "exec", "--", "vitest", "run", "tests/quality.test.ts", "-t", "assertion"], work, "pass")
    original = (work / "src/classify.ts").read_text()
    (work / "src/classify.ts").write_text(original.replace("n > 0", "n >= 0"))
    execute(["npm", "exec", "--", "vitest", "run", "tests/quality.test.ts", "-t", "call-only"], work, "pass")
    execute(["npm", "exec", "--", "vitest", "run", "tests/quality.test.ts", "-t", "assertion"], work, "fail")
    (work / "src/classify.ts").write_text(original)
    execute(["npm", "exec", "--", "vitest", "run", "tests/exports.test.ts"], work, "pass")
    api = work / "src/public_api.ts"
    saved = api.read_text()
    api.write_text(saved.replace("export function", "function"))
    execute(["npm", "exec", "--", "vitest", "run", "tests/exports.test.ts"], work, "fail")
    api.write_text(saved)
    try:
        execute(["npm", "install", "--no-save", "--package-lock=false", "--ignore-scripts", "--no-audit", "--no-fund", "@stryker-mutator/core@10.0.0", "@stryker-mutator/vitest-runner@10.0.0"], work, "pass", 480)
        _, out = execute(["npm", "exec", "--", "stryker", "run", "--concurrency", "1", "--reporters", "clear-text", "json"], work, "pass", 480)
        mutation = "observed"
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"optional_mutation_tool": "unavailable", "reason": type(error).__name__}))
        mutation = "unavailable"
    generated_file_probe(work)
    trace_probe(work)
    final_digest = digest_paths(inputs)
    if final_digest != pristine:
        raise RuntimeError("canonical web fixture source digest changed")
    print(json.dumps({"profile": "web", "stryker": mutation, "input_tree_sha256": final_digest, "input_tree_sha256": final_digest, "source_digest_unchanged": True}))


def python_probe(work: Path) -> None:
    inputs = make_python(work)
    verify_fixture_manifest("python", work, inputs)
    setup_env = work / ".setup"
    replay_env = work / ".replay"
    execute([sys.executable, "-m", "venv", str(setup_env)], work, "pass", 120)
    setup_python = setup_env / "bin/python"
    execute([str(setup_python), "-m", "pip", "install", "pip==26.2.2", "pytest==9.1.1", "coverage==7.16.2"], work, "pass", 600)
    lock = subprocess.check_output([str(setup_python), "-m", "pip", "freeze", "--all"], cwd=work, text=True)
    write(work / "requirements.lock", lock)
    inputs.append(work / "requirements.lock")
    execute([sys.executable, "-m", "venv", str(replay_env)], work, "pass", 120)
    replay_python = replay_env / "bin/python"
    execute([str(replay_python), "-m", "pip", "install", "--requirement", "requirements.lock"], work, "pass", 600)
    print(json.dumps({"profile": "python", "python": subprocess.check_output([str(replay_python), "--version"], text=True).strip(), "pip": subprocess.check_output([str(replay_python), "-m", "pip", "--version"], text=True).strip(), "requirements_lock_sha256": hashlib.sha256((work / "requirements.lock").read_bytes()).hexdigest(), "fixture_sha256": digest_paths(inputs)}))
    py = str(replay_python)
    pristine = digest_paths(inputs)
    pristine = digest_paths(inputs)
    execute([py, "-m", "coverage", "run", "--branch", "-m", "pytest", "-q", "tests/test_quality.py", "-k", "call_only"], work, "pass")
    execute([sys.executable, "-m", "coverage", "json", "-o", "coverage.json"], work, "pass")
    execute([sys.executable, "-m", "coverage", "run", "--branch", "-m", "pytest", "-q", "tests/test_quality.py", "-k", "assertion"], work, "pass")
    execute([py, "-m", "pytest", "-q", "tests/test_quality.py", "-k", "call_only"], work, "pass")
    execute([sys.executable, "-m", "pytest", "-q", "tests/test_quality.py", "-k", "assertion"], work, "pass")
    original = (work / "src/classify.py").read_text()
    (work / "src/classify.py").write_text(original.replace("n > 0", "n >= 0"))
    execute([sys.executable, "-m", "pytest", "-q", "tests/test_quality.py", "-k", "call_only"], work, "pass")
    execute([sys.executable, "-m", "pytest", "-q", "tests/test_quality.py", "-k", "assertion"], work, "fail")
    (work / "src/classify.py").write_text(original)
    execute([sys.executable, "-m", "pytest", "-q", "tests/test_exports.py"], work, "pass")
    api = work / "src/public_api.py"
    saved = api.read_text()
    api.write_text(saved.replace("def classify", "def _classify"))
    execute([sys.executable, "-m", "pytest", "-q", "tests/test_exports.py"], work, "fail")
    api.write_text(saved)
    try:
        execute([py, "-m", "pip", "install", "mutmut==3.7.0"], work, "pass", 300)
        execute([str(replay_env / "bin/mutmut"), "run"], work, "pass", 480)
        mutation = "observed"
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"optional_mutation_tool": "unavailable", "reason": type(error).__name__}))
        mutation = "unavailable"
    generated_file_probe(work)
    trace_probe(work)
    final_digest = digest_paths(inputs)
    if final_digest != pristine:
        raise RuntimeError("canonical Python fixture source digest changed")
    print(json.dumps({"profile": "python", "mutmut": mutation, "source_digest_unchanged": True, "requirements_lock_sha256": hashlib.sha256(lock.encode()).hexdigest()}))


def rust_probe(work: Path) -> None:
    inputs = make_rust(work)
    verify_fixture_manifest("rust", work, inputs)
    execute(["cargo", "generate-lockfile"], work, "pass", 300)
    execute(["cargo", "fetch", "--locked"], work, "pass", 600)
    inputs.append(work / "Cargo.lock")
    print(json.dumps({"profile": "rust", "rustc": subprocess.check_output(["rustc", "--version"], text=True).strip(), "cargo": subprocess.check_output(["cargo", "--version"], text=True).strip(), "cargo_lock_sha256": hashlib.sha256((work / "Cargo.lock").read_bytes()).hexdigest(), "fixture_sha256": digest_paths(inputs)}))
    pristine = digest_paths(inputs)
    execute(["cargo", "test", "--locked", "--test", "quality_fixture", "call_only"], work, "pass", 300)
    execute(["cargo", "test", "--locked", "--test", "quality_fixture", "assertion"], work, "pass", 300)
    original = (work / "src/lib.rs").read_text()
    (work / "src/lib.rs").write_text(original.replace("n > 0", "n >= 0"))
    execute(["cargo", "test", "--locked", "--test", "quality_fixture", "call_only"], work, "pass", 300)
    execute(["cargo", "test", "--locked", "--test", "quality_fixture", "assertion"], work, "fail", 300)
    (work / "src/lib.rs").write_text(original)
    execute(["cargo", "test", "--locked", "--test", "export_consumer"], work, "pass", 300)
    (work / "src/lib.rs").write_text(original.replace("pub fn classify", "fn classify"))
    execute(["cargo", "test", "--locked", "--test", "export_consumer"], work, "fail", 300)
    (work / "src/lib.rs").write_text(original)
    try:
        execute(["cargo", "install", "cargo-llvm-cov", "--locked", "--version", "0.9.1"], work, "pass", 480)
        execute(["cargo", "llvm-cov", "--locked", "--json", "--output-path", "target/coverage.json"], work, "pass", 480)
        line_coverage = "observed"
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"coverage_tool": "unavailable", "reason": type(error).__name__}))
        line_coverage = "unavailable"
    try:
        execute(["cargo", "llvm-cov", "--locked", "--branch", "--json", "--output-path", "target/branch-coverage.json"], work, "pass", 480)
        branch_coverage = "observed"
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"branch_coverage": "unavailable", "reason": type(error).__name__}))
        branch_coverage = "unavailable"
    try:
        execute(["cargo", "install", "cargo-mutants", "--locked", "--version", "27.1.0"], work, "pass", 480)
        execute(["cargo", "mutants", "--no-shuffle", "--timeout", "30"], work, "pass", 480)
        mutation = "observed"
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"optional_mutation_tool": "unavailable", "reason": type(error).__name__}))
        mutation = "unavailable"
    generated_file_probe(work)
    trace_probe(work)
    final_digest = digest_paths(inputs)
    if final_digest != pristine:
        raise RuntimeError("canonical Rust fixture source digest changed")
    print(json.dumps({"profile": "rust", "line_coverage": line_coverage, "branch_coverage": branch_coverage, "cargo_mutants": mutation, "input_tree_sha256": final_digest, "source_digest_unchanged": True}))


def main() -> None:
    profile = sys.argv[1]
    if len(sys.argv) != 2:
        raise SystemExit("usage: run_probe.py {web|python|rust}")
    manifest_path = Path(__file__).with_name("fixture-manifest.json")
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    expected_files = manifest["profiles"].get(profile)
    if expected_files is None:
        raise SystemExit(f"profile not found in fixture manifest: {profile}")
    print(json.dumps({"fixture_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(), "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "profile": profile, "manifest_version": manifest["version"]}))
    root = Path(tempfile.mkdtemp(prefix=f"fw028-{profile}-"))
    try:
        if profile == "web":
            web_probe(root)
        elif profile == "python":
            python_probe(root)
        elif profile == "rust":
            rust_probe(root)
        else:
            raise ValueError(profile)
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
