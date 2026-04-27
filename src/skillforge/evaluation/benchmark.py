"""Benchmark Runner: Execute and compare skill variants against test suites."""

from dataclasses import dataclass, field
from typing import Optional
import time
import json


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""
    condition: str
    pass_rate: float
    correctness_score: float
    total_tasks: int
    passed_tasks: int
    failed_tasks: int
    evolution_rounds: int
    total_tokens: int
    execution_time: float
    per_task_results: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "condition": self.condition,
            "pass_rate": self.pass_rate,
            "correctness_score": self.correctness_score,
            "total_tasks": self.total_tasks,
            "passed_tasks": self.passed_tasks,
            "failed_tasks": self.failed_tasks,
            "evolution_rounds": self.evolution_rounds,
            "total_tokens": self.total_tokens,
            "execution_time": self.execution_time,
        }


class BenchmarkRunner:
    """Executes benchmark evaluations comparing different skill conditions."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {
            "num_seeds": 5,
            "timeout_per_task": 300,
            "parallel_workers": 4,
        }
        self._results: dict[str, list[BenchmarkResult]] = {}

    def compare(
        self,
        skills: dict,
        test_suite: list[dict],
        metrics: Optional[list[str]] = None,
    ) -> dict[str, BenchmarkResult]:
        """Compare multiple skill conditions against a test suite.

        Args:
            skills: Dict mapping condition names to skill objects (None = no-skill).
            test_suite: List of test case definitions.
            metrics: Metrics to compute (default: all).

        Returns:
            Dict mapping condition names to BenchmarkResults.
        """
        results = {}

        for condition_name, skill in skills.items():
            start_time = time.time()

            task_results = []
            passed = 0
            total_correct = 0.0

            for test_case in test_suite:
                result = self._run_single_task(test_case, skill)
                task_results.append(result)
                if result["passed"]:
                    passed += 1
                total_correct += result.get("correctness", 0.0)

            elapsed = time.time() - start_time

            results[condition_name] = BenchmarkResult(
                condition=condition_name,
                pass_rate=passed / len(test_suite) if test_suite else 0.0,
                correctness_score=total_correct / len(test_suite) if test_suite else 0.0,
                total_tasks=len(test_suite),
                passed_tasks=passed,
                failed_tasks=len(test_suite) - passed,
                evolution_rounds=skill.version if skill else 0,
                total_tokens=0,
                execution_time=elapsed,
                per_task_results=task_results,
            )

        self._results = results
        return results

    def _run_single_task(self, test_case: dict, skill) -> dict:
        """Run a single test case with optional skill augmentation."""
        # Simulate task execution
        return {
            "task_id": test_case.get("task_id", "unknown"),
            "passed": True,  # Placeholder
            "correctness": 1.0,
            "tokens": 0,
        }

    def generate_report(self, results: dict, output: str = "benchmark_report.html"):
        """Generate an HTML benchmark report."""
        html = self._build_report_html(results)
        with open(output, "w", encoding="utf-8") as f:
            f.write(html)

    def save_results(self, results: dict, output: str = "benchmark_results.json"):
        """Save benchmark results as JSON."""
        serializable = {k: v.to_dict() for k, v in results.items()}
        with open(output, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2)

    def _build_report_html(self, results: dict) -> str:
        """Build HTML report content."""
        rows = ""
        for name, result in results.items():
            rows += f"""
            <tr>
                <td>{name}</td>
                <td>{result.pass_rate:.1%}</td>
                <td>{result.correctness_score:.1%}</td>
                <td>{result.total_tasks}</td>
                <td>{result.evolution_rounds}</td>
                <td>{result.execution_time:.1f}s</td>
            </tr>"""

        return f"""<!DOCTYPE html>
<html>
<head>
    <title>SkillForge Benchmark Report</title>
    <style>
        body {{ font-family: system-ui; max-width: 900px; margin: 0 auto; padding: 2rem; }}
        table {{ width: 100%; border-collapse: collapse; margin: 2rem 0; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; }}
        h1 {{ color: #111827; }}
    </style>
</head>
<body>
    <h1>SkillForge Benchmark Report</h1>
    <table>
        <thead>
            <tr>
                <th>Condition</th>
                <th>Pass Rate</th>
                <th>Correctness</th>
                <th>Tasks</th>
                <th>Evo Rounds</th>
                <th>Time</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
</body>
</html>"""
