"""Failure Analyzer: Categorize and analyze failure modes across domains."""

from dataclasses import dataclass, field
from typing import Optional
import math


FAILURE_CATEGORIES = [
    "coverage_gaps",
    "logic_errors",
    "precision_failures",
    "algorithm_selection",
    "edge_case_misses",
]


@dataclass
class FailureRecord:
    task_id: str
    category: str
    description: str
    severity: str = "major"  # critical, major, minor
    skill_version: int = 0


class FailureAnalyzer:
    """Categorize and analyze failure modes across domains."""

    def __init__(self, categories: Optional[list[str]] = None):
        self.categories = categories or FAILURE_CATEGORIES
        self._records: list[FailureRecord] = []

    def record_failure(self, task_id: str, category: str, description: str, severity: str = "major", skill_version: int = 0):
        """Record a single failure."""
        if category not in self.categories:
            category = "edge_case_misses"
        self._records.append(FailureRecord(
            task_id=task_id,
            category=category,
            description=description,
            severity=severity,
            skill_version=skill_version,
        ))

    def analyze(self, results: Optional[dict] = None, categories: Optional[list[str]] = None) -> dict:
        """Analyze failure patterns from benchmark results or recorded failures.

        Returns:
            Dict with category distribution, severity breakdown, and insights.
        """
        cats = categories or self.categories
        records = self._records

        # Category distribution
        cat_counts = {c: 0 for c in cats}
        for r in records:
            if r.category in cat_counts:
                cat_counts[r.category] += 1

        total = sum(cat_counts.values())
        cat_distribution = {
            c: count / total if total > 0 else 0.0
            for c, count in cat_counts.items()
        }

        # Severity breakdown
        severity_counts = {"critical": 0, "major": 0, "minor": 0}
        for r in records:
            if r.severity in severity_counts:
                severity_counts[r.severity] += 1

        # Entropy (failure diversity)
        entropy = 0.0
        for proportion in cat_distribution.values():
            if proportion > 0:
                entropy -= proportion * math.log2(proportion)

        return {
            "total_failures": total,
            "category_distribution": cat_distribution,
            "severity_breakdown": severity_counts,
            "failure_diversity_entropy": entropy,
            "top_category": max(cat_distribution, key=cat_distribution.get) if total > 0 else None,
            "insights": self._generate_insights(cat_distribution, total),
        }

    def _generate_insights(self, distribution: dict, total: int) -> list[str]:
        """Generate actionable insights from failure distribution."""
        insights = []
        if total == 0:
            return ["No failures recorded"]

        sorted_cats = sorted(distribution.items(), key=lambda x: x[1], reverse=True)

        top = sorted_cats[0]
        if top[1] > 0.3:
            insights.append(f"Dominant failure mode: {top[0]} ({top[1]:.0%}) — prioritize improvement here")

        if distribution.get("coverage_gaps", 0) > 0.15:
            insights.append("High coverage gap rate — skills are not addressing all sub-tasks")

        if distribution.get("edge_case_misses", 0) > 0.20:
            insights.append("Edge case handling needs improvement — add adversarial test generation")

        if distribution.get("precision_failures", 0) > 0.10:
            insights.append("Precision failures detected — tighten output format validation in verifier")

        return insights

    @property
    def records(self) -> list[FailureRecord]:
        return self._records.copy()
