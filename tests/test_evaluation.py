"""Tests for SkillForge evaluation and simulation modules."""

import unittest
from skillforge.evaluation.test_gen import SyntheticTestGenerator
from skillforge.evaluation.simulation import SimulationRunner
from skillforge.evaluation.benchmark import BenchmarkRunner, BenchmarkResult
from skillforge.evaluation.metrics import compute_metrics, compute_transfer_score
from skillforge.core.skill_bank import Skill


class TestSyntheticTestGenerator(unittest.TestCase):
    def setUp(self):
        self.gen = SyntheticTestGenerator(domain="software_engineering")

    def test_generate_creates_test_cases(self):
        tasks = [{"task_id": "T1", "instruction": "Build a REST API"}]
        tests = self.gen.generate(tasks, num_cases_per_task=4)
        self.assertEqual(len(tests), 4)

    def test_test_case_has_required_fields(self):
        tasks = [{"task_id": "T1", "instruction": "Parse JSON"}]
        tests = self.gen.generate(tasks, num_cases_per_task=1)
        tc = tests[0]
        self.assertTrue(tc.test_id)
        self.assertTrue(tc.task_id)
        self.assertTrue(tc.test_type)
        self.assertTrue(tc.description)

    def test_multiple_strategies(self):
        tasks = [{"task_id": "T1", "instruction": "Test"}]
        tests = self.gen.generate(tasks, num_cases_per_task=8)
        types = {t.test_type for t in tests}
        self.assertTrue(len(types) > 1)


class TestBenchmarkRunner(unittest.TestCase):
    def setUp(self):
        self.runner = BenchmarkRunner()

    def test_compare_returns_results(self):
        skills = {
            "no_skill": None,
            "evolved": Skill(trigger_condition="T", strategy="S", accuracy=0.8, version=3),
        }
        test_suite = [{"task_id": f"T{i}"} for i in range(5)]
        results = self.runner.compare(skills, test_suite)

        self.assertIn("no_skill", results)
        self.assertIn("evolved", results)
        self.assertEqual(results["no_skill"].total_tasks, 5)


class TestMetrics(unittest.TestCase):
    def test_compute_transfer_score(self):
        score = compute_transfer_score(0.72, 0.65)
        self.assertAlmostEqual(score, 0.65 / 0.72, places=3)

    def test_transfer_score_zero_base(self):
        score = compute_transfer_score(0.0, 0.5)
        self.assertEqual(score, 0.0)


class TestSimulationRunner(unittest.TestCase):
    def test_synthetic_simulation(self):
        runner = SimulationRunner()
        report = runner.run_synthetic_simulation(num_tasks=5)

        self.assertEqual(len(report.task_results), 5)
        self.assertIn("human_avg_pass_rate", report.aggregate_metrics)
        self.assertIn("ai_avg_pass_rate", report.aggregate_metrics)
        self.assertTrue(len(report.insights) > 0)

    def test_report_serialization(self):
        runner = SimulationRunner()
        report = runner.run_synthetic_simulation(num_tasks=3)
        data = report.to_dict()

        self.assertIn("task_results", data)
        self.assertIn("aggregate_metrics", data)
        self.assertIn("insights", data)


if __name__ == "__main__":
    unittest.main()
