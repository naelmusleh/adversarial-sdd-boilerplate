from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_role_catalog import ROOT, validate_catalog


CATALOG = ROOT / "docs/framework/ROLE-CAPABILITIES-001.md"


def edit_catalog_cell(text: str, row_number: int, column_name: str, value: str) -> str:
    lines = text.splitlines()
    header_index = next(
        index for index, line in enumerate(lines) if line.startswith("| role_id |")
    )
    headers = [cell.strip() for cell in lines[header_index].strip().strip("|").split("|")]
    data_rows = [
        index for index in range(header_index + 2, len(lines)) if lines[index].startswith("| ROLE-")
    ]
    row_index = data_rows[row_number]
    cells = [cell.strip() for cell in lines[row_index].strip().strip("|").split("|")]
    cells[headers.index(column_name)] = value
    lines[row_index] = "| " + " | ".join(cells) + " |"
    return "\n".join(lines) + "\n"


class RoleCatalogValidationTests(unittest.TestCase):
    def validate_mutation(self, content: str, expected_problem: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "ROLE-CAPABILITIES-001.md"
            candidate.write_text(content, encoding="utf-8")
            problems = validate_catalog(ROOT, candidate)
        self.assertTrue(
            any(expected_problem in problem for problem in problems),
            f"Expected {expected_problem!r}; received {problems!r}",
        )

    def test_rejects_duplicate_role_ids(self) -> None:
        original = CATALOG.read_text(encoding="utf-8")
        first_role_id = "ROLE-ORCHESTRATOR"
        invalid = edit_catalog_cell(original, 1, "role_id", first_role_id)
        self.validate_mutation(invalid, f"duplicate role_id '{first_role_id}'")

    def test_rejects_missing_required_fields(self) -> None:
        original = CATALOG.read_text(encoding="utf-8")
        invalid = edit_catalog_cell(original, 0, "deliverable", "")
        self.validate_mutation(invalid, "required field 'deliverable' is empty")

    def test_rejects_invalid_enums(self) -> None:
        original = CATALOG.read_text(encoding="utf-8")
        invalid = edit_catalog_cell(original, 0, "classification", "super-agent")
        self.validate_mutation(invalid, "unsupported classification 'super-agent'")

    def test_rejects_broken_artifact_references(self) -> None:
        original = CATALOG.read_text(encoding="utf-8")
        invalid = edit_catalog_cell(original, 0, "artifact_refs", "FRAMEWORK-NOTFOUND-999")
        self.validate_mutation(
            invalid,
            "artifact reference 'FRAMEWORK-NOTFOUND-999' does not resolve",
        )
