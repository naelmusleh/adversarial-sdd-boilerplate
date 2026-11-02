from __future__ import annotations

import unittest


def python_boundary_rule(value: int, limit: int) -> bool:
    if value < limit:
        return True
    if value == limit:
        return True
    return False


def python_boundary_mutant(value: int, limit: int) -> bool:
    if value < limit:
        return True
    if value == limit:
        return False
    return False


def observed_outcome(rule, *, asserting: bool) -> str:
    try:
        outcomes = [rule(9, 10), rule(10, 10), rule(11, 10)]
        if asserting and outcomes != [True, True, False]:
            raise AssertionError(f"unexpected boundary outcomes: {outcomes!r}")
    except AssertionError:
        return "fail"
    return "pass"


class FrameworkQualityMatrixTests(unittest.TestCase):
    def test_call_only_and_assertion_evidence_distinguish_boundary_mutant(self) -> None:
        self.assertEqual(observed_outcome(python_boundary_rule, asserting=False), "pass")
        self.assertEqual(observed_outcome(python_boundary_mutant, asserting=False), "pass")
        self.assertEqual(observed_outcome(python_boundary_rule, asserting=True), "pass")
        self.assertEqual(observed_outcome(python_boundary_mutant, asserting=True), "fail")


if __name__ == "__main__":
    unittest.main()
