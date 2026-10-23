from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.profile_composer import compose_profiles


ROOT = Path(__file__).resolve().parents[1]


class FrameworkProfileCompositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.profile_root = self.root / "profiles"
        shutil.copytree(ROOT / "framework" / "profiles", self.profile_root)
        self.core_source = self.root / "core.md"
        self.core_source.write_text("core source\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def available_probe(name: str, constraint: str) -> dict[str, str]:
        versions = {"node": "22.23.3", "npm": "12.1.0", "python3": "3.13.2", "rustc": "1.97.0", "cargo": "1.97.0"}
        return {"state": "available", "observed_version": versions[name]}

    def compose(self, selected: list[str], probe=None):
        return compose_profiles(
            selected,
            {"README.md": "synthetic core output\n"},
            {"README.md": self.core_source},
            "a" * 40,
            profile_root=self.profile_root,
            prerequisite_probe=probe or self.available_probe,
        )

    def test_core_only_emits_no_stack_files_or_checks(self) -> None:
        outputs, core, selection, result = self.compose([])
        self.assertEqual(outputs, {})
        self.assertEqual(selection["selected_profiles"], {})
        self.assertEqual(selection["profile_checks"], {})
        self.assertEqual(selection["prerequisites"], {})
        self.assertEqual(result["check_results"], {})
        self.assertEqual(set(core["files"]), {"README.md"})

    def test_multiple_profiles_keep_owned_outputs_and_check_results_separate(self) -> None:
        outputs, _, selection, result = self.compose(["nextjs-typescript", "fastapi-python", "rust-axum"])
        self.assertEqual(set(selection["selected_profiles"]), {"nextjs-typescript", "fastapi-python", "rust-axum"})
        self.assertIn("profiles/nextjs-typescript/package.json", outputs)
        self.assertIn("profiles/fastapi-python/requirements.txt", outputs)
        self.assertIn("profiles/rust-axum/Cargo.toml", outputs)
        self.assertEqual(set(result["check_results"]), set(selection["selected_profiles"]))
        self.assertEqual(result["check_results"]["fastapi-python"]["contract-tests"]["state"], "not-run")
        self.assertEqual(result["check_results"]["rust-axum"]["persistent-storage"]["state"], "unsupported")

    def test_missing_required_prerequisite_fails_before_returning_outputs(self) -> None:
        def missing_node(name: str, constraint: str) -> dict[str, str]:
            if name == "node":
                return {"state": "missing", "reason": "node is absent in this controlled fixture"}
            return self.available_probe(name, constraint)

        with self.assertRaisesRegex(ValueError, "Required profile prerequisites are missing"):
            self.compose(["nextjs-typescript"], missing_node)

    def test_unrecognized_prerequisite_constraint_fails_closed(self) -> None:
        manifest = self.profile_root / "nextjs-typescript/profile.json"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(">=22.12.0", "<=22.12.0"),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "supported >=X.Y.Z"):
            self.compose(["nextjs-typescript"])

    def test_unsupported_check_cannot_be_required(self) -> None:
        manifest = self.profile_root / "fastapi-python/profile.json"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                '"status": "unsupported", "required": false',
                '"status": "unsupported", "required": true',
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "unsupported check .* must be optional"):
            self.compose(["fastapi-python"])

    def test_dependency_leakage_between_selected_profiles_is_rejected(self) -> None:
        package = self.profile_root / "nextjs-typescript/files/package.json"
        package.write_text(package.read_text(encoding="utf-8").replace('"react-dom": "19.2.8"', '"react-dom": "19.2.8", "fastapi": "0.157.0"'), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Profile leakage detected"):
            self.compose(["nextjs-typescript", "fastapi-python"])

    def test_profile_instruction_leakage_is_rejected(self) -> None:
        readme = self.profile_root / "nextjs-typescript/files/README.md"
        readme.write_text(readme.read_text(encoding="utf-8").replace("profile-instructions: nextjs-typescript", "profile-instructions: fastapi-python"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Profile leakage detected"):
            self.compose(["nextjs-typescript", "fastapi-python"])

    def test_unselected_profile_dependency_leakage_is_rejected(self) -> None:
        package = self.profile_root / "nextjs-typescript/files/package.json"
        package.write_text(package.read_text(encoding="utf-8").replace(
            '"react-dom": "19.2.8"', '"react-dom": "19.2.8", "fastapi": "0.157.0"',
        ), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Profile leakage detected: nextjs-typescript"):
            self.compose(["nextjs-typescript"])

    def test_unselected_profile_instruction_leakage_is_rejected(self) -> None:
        readme = self.profile_root / "nextjs-typescript/files/README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\nprofile-instructions: fastapi-python\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Profile leakage detected: nextjs-typescript"):
            self.compose(["nextjs-typescript"])


if __name__ == "__main__":
    unittest.main()
