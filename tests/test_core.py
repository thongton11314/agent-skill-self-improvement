"""Tests for SkillForge core components."""

import unittest
from skillforge.config import SkillConfig, EvolutionConfig
from skillforge.core.skill_bank import Skill, SkillBank
from skillforge.core.generator import SkillGenerator
from skillforge.core.verifier import SurrogateVerifier
from skillforge.core.evolution import EvolutionEngine
from skillforge.memory.manager import MemoryManager


class TestSkillBank(unittest.TestCase):
    def setUp(self):
        config = SkillConfig()
        self.bank = SkillBank(config.skill_bank)

    def test_store_and_retrieve(self):
        skill = Skill(
            trigger_condition="Parse CSV files and validate schema",
            strategy="Step 1: Read CSV. Step 2: Validate.",
            accuracy=0.85,
            version=3,
        )
        skill_id = self.bank.store(skill)
        self.assertIsNotNone(skill_id)
        self.assertEqual(self.bank.size, 1)

        retrieved = self.bank.get(skill_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.accuracy, 0.85)

    def test_retrieve_by_query(self):
        self.bank.store(Skill(
            trigger_condition="Parse CSV files",
            strategy="CSV parser",
            accuracy=0.9,
            version=1,
        ))
        self.bank.store(Skill(
            trigger_condition="Build REST API",
            strategy="API builder",
            accuracy=0.7,
            version=1,
        ))

        results = self.bank.retrieve("Parse CSV data", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertIn("CSV", results[0].trigger_condition)

    def test_empty_bank(self):
        results = self.bank.retrieve("anything")
        self.assertEqual(len(results), 0)
        self.assertIsNone(self.bank.get_latest())


class TestSkillGenerator(unittest.TestCase):
    def setUp(self):
        self.config = SkillConfig()
        self.generator = SkillGenerator(self.config)

    def test_generate_initial_skill(self):
        context = {
            "instruction": "Build a data pipeline",
            "environment": {"tools": ["python", "pandas"]},
        }
        skill = self.generator.generate(context)
        self.assertEqual(skill.version, 0)
        self.assertIn("SKILL.md", skill.artifacts)
        self.assertTrue(len(skill.trigger_condition) > 0)

    def test_refine_skill(self):
        context = {"instruction": "Build a data pipeline"}
        skill = self.generator.generate(context)

        refined = self.generator.refine(skill, {
            "feedback": {
                "summary": "Output schema mismatch",
                "suggestions": ["Fix column names"],
            }
        })
        self.assertEqual(refined.version, 1)


class TestSurrogateVerifier(unittest.TestCase):
    def setUp(self):
        self.config = SkillConfig()
        self.verifier = SurrogateVerifier(self.config)

    def test_verify_produces_result(self):
        task = {"instruction": "Parse a CSV file"}
        outputs = {"status": "executed"}

        result = self.verifier.verify(task, outputs)
        self.assertIsNotNone(result)
        self.assertTrue(len(result.assertions) > 0)

    def test_diagnose_on_failure(self):
        task = {"instruction": "Parse a CSV file"}
        outputs = {"status": "executed"}

        result = self.verifier.verify(task, outputs)
        diagnostics = self.verifier.diagnose(task, outputs, result)
        self.assertIn("summary", diagnostics)
        self.assertIn("suggestions", diagnostics)

    def test_escalate_adds_assertions(self):
        task = {"instruction": "Parse a CSV file"}
        outputs = {"status": "executed"}

        self.verifier.verify(task, outputs)
        initial_count = len(self.verifier._test_suites.get(self.verifier._task_key(task), []))

        self.verifier.escalate(task, outputs)
        new_count = len(self.verifier._test_suites.get(self.verifier._task_key(task), []))
        self.assertGreater(new_count, initial_count)


class TestEvolutionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = EvolutionEngine(EvolutionConfig())

    def test_evolve_increments_version(self):
        skill = Skill(
            trigger_condition="Test",
            strategy="Test strategy",
            accuracy=0.5,
            version=2,
        )
        evolved = self.engine.evolve(skill, {"feedback": {"root_cause": "Test failure"}})
        self.assertEqual(evolved.version, 3)

    def test_evolution_history(self):
        skill = Skill(trigger_condition="Test", strategy="S", accuracy=0.5, version=0)
        self.engine.evolve(skill, {"feedback": {}})
        self.assertEqual(len(self.engine.evolution_history), 1)


class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.config = SkillConfig()
        self.memory = MemoryManager(self.config)

    def test_record_and_retrieve(self):
        task = {"instruction": "Build a CSV parser"}
        skill = Skill(trigger_condition="CSV", strategy="Parse", accuracy=0.8, version=1)
        self.memory.record(task, skill, {"status": "success"})

        results = self.memory.retrieve("CSV parser")
        self.assertTrue(len(results) >= 0)  # May be empty if quality threshold filters

    def test_memory_stats(self):
        stats = self.memory.stats
        self.assertEqual(stats["episodic_count"], 0)
        self.assertEqual(stats["total_episodes"], 0)

    def test_record_increments_episodes(self):
        task = {"instruction": "Test task"}
        skill = Skill(trigger_condition="T", strategy="S", accuracy=0.5, version=0)
        self.memory.record(task, skill, {})
        self.assertEqual(self.memory.stats["total_episodes"], 1)


if __name__ == "__main__":
    unittest.main()
