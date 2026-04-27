"""Tests for Memory Manager."""

import unittest
from skillforge.config import SkillConfig
from skillforge.memory.manager import MemoryManager
from skillforge.core.skill_bank import Skill


class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.config = SkillConfig()
        self.memory = MemoryManager(self.config)

    def test_initial_stats(self):
        stats = self.memory.stats
        self.assertEqual(stats["episodic_count"], 0)
        self.assertEqual(stats["semantic_count"], 0)
        self.assertEqual(stats["procedural_count"], 0)
        self.assertEqual(stats["total_episodes"], 0)

    def test_record_adds_episodic_entry(self):
        task = {"instruction": "Build a parser"}
        skill = Skill(trigger_condition="T", strategy="S", accuracy=0.8, version=1)
        self.memory.record(task, skill, {"status": "success"})
        self.assertEqual(self.memory.stats["episodic_count"], 1)
        self.assertEqual(self.memory.stats["total_episodes"], 1)

    def test_record_success(self):
        task = {"instruction": "Sort data"}
        self.memory.record_success(task, None, {"result": "ok"})
        self.assertEqual(self.memory.stats["episodic_count"], 1)

    def test_record_failure(self):
        task = {"instruction": "Failed task"}
        self.memory.record_failure(task, error="Timeout")
        entries = self.memory._episodic
        self.assertTrue(any("FAILURE" in e.content for e in entries))

    def test_retrieve_empty_returns_empty(self):
        results = self.memory.retrieve("anything")
        self.assertEqual(len(results), 0)

    def test_retrieve_after_records(self):
        task = {"instruction": "Parse CSV data files"}
        skill = Skill(trigger_condition="CSV", strategy="S", accuracy=0.9, version=1)
        self.memory.record(task, skill, {"status": "success"})
        # Retrieval may or may not return based on quality threshold
        results = self.memory.retrieve("CSV")
        self.assertIsInstance(results, list)

    def test_semantic_distillation_triggers(self):
        """After distill_interval episodes, semantic memory should grow."""
        skill = Skill(trigger_condition="T", strategy="S", accuracy=0.9, version=1)
        for i in range(self.config.memory.distill_interval):
            task = {"instruction": f"Task {i}"}
            self.memory.record(task, skill, {"status": "success"})
        self.assertGreater(self.memory.stats["semantic_count"], 0)

    def test_policy_selection(self):
        """Thompson Sampling should return a valid policy name."""
        policy = self.memory._select_policy()
        valid_policies = {"none", "recent_window", "compressed", "full_detailed", "aggressive_learner"}
        self.assertIn(policy, valid_policies)

    def test_update_policy_reward(self):
        """Policy reward update should modify posteriors."""
        self.memory.update_policy_reward("compressed", 1.0)
        scores = self.memory._policy_scores["compressed"]
        self.assertGreater(scores["alpha"], 1.0)


if __name__ == "__main__":
    unittest.main()
