"""Tests for Surrogate Verifier."""

import unittest
from skillforge.config import SkillConfig
from skillforge.core.verifier import SurrogateVerifier


class TestSurrogateVerifier(unittest.TestCase):
    def setUp(self):
        self.config = SkillConfig()
        self.verifier = SurrogateVerifier(self.config)

    def test_verify_returns_result(self):
        task = {"instruction": "Parse a CSV file"}
        outputs = {"status": "executed", "files": ["output.csv"]}
        result = self.verifier.verify(task, outputs)
        self.assertIsNotNone(result)
        self.assertIsInstance(result.passed, bool)
        self.assertIsInstance(result.pass_rate, float)

    def test_verify_generates_assertions(self):
        task = {"instruction": "Build a REST API"}
        outputs = {"status": "executed"}
        result = self.verifier.verify(task, outputs)
        self.assertTrue(len(result.assertions) > 0)

    def test_diagnose_returns_structured_feedback(self):
        task = {"instruction": "Sort a list"}
        outputs = {"status": "executed"}
        result = self.verifier.verify(task, outputs)
        diagnostics = self.verifier.diagnose(task, outputs, result)
        self.assertIn("summary", diagnostics)
        self.assertIn("root_cause", diagnostics)
        self.assertIn("suggestions", diagnostics)
        self.assertIn("failed_assertions", diagnostics)

    def test_escalate_increases_test_count(self):
        task = {"instruction": "Parse JSON"}
        outputs = {"status": "executed"}
        self.verifier.verify(task, outputs)
        task_key = self.verifier._task_key(task)
        initial_count = len(self.verifier._test_suites.get(task_key, []))
        self.verifier.escalate(task, outputs)
        new_count = len(self.verifier._test_suites.get(task_key, []))
        self.assertGreater(new_count, initial_count)

    def test_information_isolation(self):
        """Verifier should not have access to generator internals."""
        task = {"instruction": "Test isolation"}
        outputs = {"status": "executed"}
        result = self.verifier.verify(task, outputs)
        # Verifier only sees instruction and outputs, not skill code
        for assertion in result.assertions:
            self.assertNotIn("generator", assertion.condition.lower())

    def test_multiple_verify_rounds(self):
        task = {"instruction": "Compute statistics"}
        outputs = {"status": "executed"}
        for i in range(3):
            result = self.verifier.verify(task, outputs, retry_round=i)
            self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
