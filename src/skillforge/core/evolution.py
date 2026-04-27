"""Evolution Engine: Drives iterative skill improvement through diagnose-before-prescribe."""

from skillforge.config import EvolutionConfig
from skillforge.core.skill_bank import Skill


class EvolutionEngine:
    """Drives skill evolution through failure diagnosis and targeted improvement."""

    def __init__(self, config: EvolutionConfig):
        self.config = config
        self._evolution_log: list[dict] = []

    def evolve(self, skill: Skill, context: dict) -> Skill:
        """Evolve a skill based on diagnosed failure patterns.

        The evolution follows a diagnose-before-prescribe approach:
        1. Diagnose why the skill failed (root cause analysis)
        2. Determine if the failure requires strategy revision or algorithm change
        3. Generate targeted improvements
        """
        feedback = context.get("feedback", {})
        failure_pattern = self._diagnose_failure(skill, feedback)

        if failure_pattern["severity"] == "algorithm_change":
            evolved = self._algorithm_evolution(skill, failure_pattern)
        elif failure_pattern["severity"] == "strategy_revision":
            evolved = self._strategy_evolution(skill, failure_pattern)
        else:
            evolved = self._parameter_tuning(skill, failure_pattern)

        self._evolution_log.append({
            "from_version": skill.version,
            "to_version": evolved.version,
            "pattern": failure_pattern,
            "trigger": "evolution_engine",
        })

        return evolved

    def _diagnose_failure(self, skill: Skill, feedback: dict) -> dict:
        """Diagnose the failure pattern from accumulated feedback."""
        failed_types = set()
        if isinstance(feedback, dict):
            for fa in feedback.get("failed_assertions", []):
                failed_types.add(fa.get("type", "unknown"))

        # Determine severity based on failure patterns
        if "precision_check" in failed_types or "algorithm" in str(feedback):
            severity = "algorithm_change"
        elif len(failed_types) > 2:
            severity = "strategy_revision"
        else:
            severity = "parameter_tuning"

        return {
            "severity": severity,
            "failed_types": list(failed_types),
            "consecutive_failures": len(skill.failure_buffer),
            "root_cause": feedback.get("root_cause", "Unknown"),
        }

    def _algorithm_evolution(self, skill: Skill, pattern: dict) -> Skill:
        """Replace the core algorithm when parameter tuning is insufficient."""
        new_strategy = skill.strategy + f"""

## Algorithm Evolution (v{skill.version + 1})
- Previous algorithm inadequate: {pattern['root_cause']}
- Switching to alternative approach based on failure analysis
- Applying two-stage refinement: broad search followed by narrow optimization
"""
        return Skill(
            trigger_condition=skill.trigger_condition,
            strategy=new_strategy,
            accuracy=skill.accuracy,
            version=skill.version + 1,
            artifacts=skill.artifacts.copy(),
            failure_buffer=[],
        )

    def _strategy_evolution(self, skill: Skill, pattern: dict) -> Skill:
        """Revise the strategy while keeping the algorithm."""
        new_strategy = skill.strategy + f"""

## Strategy Revision (v{skill.version + 1})
- Addressing: {', '.join(pattern['failed_types'])}
- Root cause: {pattern['root_cause']}
"""
        return Skill(
            trigger_condition=skill.trigger_condition,
            strategy=new_strategy,
            accuracy=skill.accuracy,
            version=skill.version + 1,
            artifacts=skill.artifacts.copy(),
            failure_buffer=[],
        )

    def _parameter_tuning(self, skill: Skill, pattern: dict) -> Skill:
        """Fine-tune parameters without changing strategy."""
        return Skill(
            trigger_condition=skill.trigger_condition,
            strategy=skill.strategy,
            accuracy=skill.accuracy,
            version=skill.version + 1,
            artifacts=skill.artifacts.copy(),
            failure_buffer=skill.failure_buffer,
        )

    @property
    def evolution_history(self) -> list[dict]:
        return self._evolution_log.copy()
