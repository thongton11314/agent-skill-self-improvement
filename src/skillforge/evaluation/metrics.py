"""Evaluation Metrics for SkillForge."""

from typing import Optional
import math


def compute_metrics(results: dict, metrics: Optional[list[str]] = None) -> dict:
    """Compute evaluation metrics from benchmark results.

    Args:
        results: Dict of condition_name -> BenchmarkResult.
        metrics: Specific metrics to compute (default: all).

    Returns:
        Dict of condition_name -> metric_name -> value.
    """
    all_metrics = metrics or [
        "pass_rate", "correctness_score", "evolution_efficiency",
        "token_cost", "convergence_speed", "failure_diversity",
        "generalization_gap",
    ]

    computed = {}
    for condition_name, result in results.items():
        condition_metrics = {}

        if "pass_rate" in all_metrics:
            condition_metrics["pass_rate"] = result.pass_rate

        if "correctness_score" in all_metrics:
            condition_metrics["correctness_score"] = result.correctness_score

        if "evolution_efficiency" in all_metrics:
            rounds = max(result.evolution_rounds, 1)
            condition_metrics["evolution_efficiency"] = result.pass_rate / rounds

        if "token_cost" in all_metrics:
            condition_metrics["token_cost"] = result.total_tokens

        if "convergence_speed" in all_metrics:
            condition_metrics["convergence_speed"] = _estimate_convergence(result)

        if "failure_diversity" in all_metrics:
            condition_metrics["failure_diversity"] = _compute_failure_entropy(result)

        if "generalization_gap" in all_metrics:
            condition_metrics["generalization_gap"] = 0.0  # Requires train/test split

        computed[condition_name] = condition_metrics

    return computed


def compute_transfer_score(
    self_evolved_pass_rate: float,
    transferred_pass_rate: float,
) -> float:
    """Compute skill transferability score.

    transfer_score = transferred_pass_rate / self_evolved_pass_rate
    """
    if self_evolved_pass_rate == 0:
        return 0.0
    return transferred_pass_rate / self_evolved_pass_rate


def _estimate_convergence(result) -> int:
    """Estimate rounds to 90% of final performance."""
    # Simplified: assume linear improvement
    if result.pass_rate == 0:
        return result.evolution_rounds
    target = 0.9 * result.pass_rate
    return max(1, int(result.evolution_rounds * target / result.pass_rate))


def _compute_failure_entropy(result) -> float:
    """Compute entropy of failure categories."""
    if not result.per_task_results:
        return 0.0

    # Count failure types
    failures = [r for r in result.per_task_results if not r.get("passed", True)]
    if not failures:
        return 0.0

    # Simplified: uniform distribution assumption
    n_categories = min(len(failures), 5)
    if n_categories <= 1:
        return 0.0

    # Maximum entropy for n categories
    return math.log2(n_categories)
