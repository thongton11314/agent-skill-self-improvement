"""Tests for Adaptive Retrieval Controller (integrated in MemoryManager)."""

import unittest
from skillforge.config import SkillConfig
from skillforge.memory.manager import MemoryManager, MemoryEntry
from skillforge.core.skill_bank import Skill


class TestRetrievalController(unittest.TestCase):
    """Tests for the adaptive retrieval controller embedded in MemoryManager."""

    def setUp(self):
        self.config = SkillConfig()
        self.memory = MemoryManager(self.config)
        # Populate with some entries
        for i in range(5):
            task = {"instruction": f"Build a data pipeline step {i}"}
            skill = Skill(trigger_condition="pipeline", strategy="S", accuracy=0.8, version=1)
            self.memory.record(task, skill, {"status": "success"})

    def test_retrieve_respects_top_k(self):
        results = self.memory.retrieve("pipeline", top_k=2)
        self.assertLessEqual(len(results), 2)

    def test_scoring_formula(self):
        """Score should combine feature match, quality, recency, and tier boost."""
        entry = MemoryEntry(
            content="Build a data pipeline for CSV processing",
            tier="semantic",
            quality=0.9,
            age=0,
        )
        score = self.memory._score_entry("data pipeline CSV", entry)
        self.assertGreater(score, 0.0)

    def test_tier_boost_ordering(self):
        """Procedural entries should score higher than episodic with same content."""
        query = "same query"
        episodic = MemoryEntry(content=query, tier="episodic", quality=0.8, age=0)
        procedural = MemoryEntry(content=query, tier="procedural", quality=0.8, age=0)

        score_epi = self.memory._score_entry(query, episodic)
        score_proc = self.memory._score_entry(query, procedural)
        self.assertGreater(score_proc, score_epi)

    def test_recency_decay(self):
        """Older entries should score lower due to recency decay."""
        query = "test query"
        recent = MemoryEntry(content=query, tier="episodic", quality=0.8, age=0)
        old = MemoryEntry(content=query, tier="episodic", quality=0.8, age=100)

        score_recent = self.memory._score_entry(query, recent)
        score_old = self.memory._score_entry(query, old)
        self.assertGreater(score_recent, score_old)

    def test_quality_affects_score(self):
        """Higher quality entries should score higher."""
        query = "quality test"
        high_q = MemoryEntry(content=query, tier="episodic", quality=1.0, age=0)
        low_q = MemoryEntry(content=query, tier="episodic", quality=0.1, age=0)

        score_high = self.memory._score_entry(query, high_q)
        score_low = self.memory._score_entry(query, low_q)
        self.assertGreater(score_high, score_low)

    def test_thompson_sampling_convergence(self):
        """After many updates, policy selection should favor rewarded policies."""
        # Heavily reward 'compressed' policy
        for _ in range(50):
            self.memory.update_policy_reward("compressed", 1.0)
        for _ in range(50):
            self.memory.update_policy_reward("none", 0.0)

        # Sample 100 times — 'compressed' should dominate
        selections = [self.memory._select_policy() for _ in range(100)]
        compressed_count = selections.count("compressed")
        self.assertGreater(compressed_count, 50)

    def test_five_retrieval_policies_exist(self):
        """All five documented retrieval policies should be available."""
        policies = self.memory._retrieval_policies
        expected = {"none", "recent_window", "compressed", "full_detailed", "aggressive_learner"}
        self.assertEqual(set(policies.keys()), expected)


if __name__ == "__main__":
    unittest.main()
