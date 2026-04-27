"""Tests for Skill Generator."""

import unittest
from skillforge.config import SkillConfig
from skillforge.core.generator import SkillGenerator


class TestSkillGenerator(unittest.TestCase):
    def setUp(self):
        self.config = SkillConfig()
        self.gen = SkillGenerator(self.config)

    def test_generate_creates_v0_skill(self):
        context = {
            "instruction": "Parse CSV files and output JSON",
            "environment": {"tools": ["python", "pandas"]},
        }
        skill = self.gen.generate(context)
        self.assertEqual(skill.version, 0)
        self.assertIn("SKILL.md", skill.artifacts)
        self.assertEqual(skill.accuracy, 0.0)

    def test_generate_captures_trigger_condition(self):
        context = {"instruction": "Build a REST API with authentication"}
        skill = self.gen.generate(context)
        self.assertIn("REST API", skill.trigger_condition)

    def test_refine_increments_version(self):
        context = {"instruction": "Test task"}
        skill = self.gen.generate(context)
        refined = self.gen.refine(skill, {
            "feedback": {"summary": "Schema mismatch", "suggestions": ["Fix columns"]}
        })
        self.assertEqual(refined.version, 1)

    def test_refine_appends_feedback_to_buffer(self):
        context = {"instruction": "Test task"}
        skill = self.gen.generate(context)
        feedback = {"summary": "Failed assertion", "suggestions": ["Add validation"]}
        refined = self.gen.refine(skill, {"feedback": feedback})
        self.assertEqual(len(refined.failure_buffer), 1)

    def test_generate_with_memory_context(self):
        context = {
            "instruction": "Analyze data",
            "environment": {"tools": ["numpy"]},
            "memory": [{"content": "Use vectorized operations for speed"}],
        }
        skill = self.gen.generate(context)
        self.assertIsNotNone(skill)
        self.assertEqual(skill.version, 0)

    def test_multiple_refine_rounds(self):
        context = {"instruction": "Task"}
        skill = self.gen.generate(context)
        for i in range(5):
            skill = self.gen.refine(skill, {"feedback": {"summary": f"Issue {i}", "suggestions": []}})
        self.assertEqual(skill.version, 5)


if __name__ == "__main__":
    unittest.main()
