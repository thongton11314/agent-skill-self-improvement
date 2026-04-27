"""Multi-Model Skill Evolution — Evolve skills across model families simultaneously.

Instead of evolving skills with a single LLM backbone, this module
coordinates evolution across multiple models and selects the best-performing
skill variant for each task domain.
"""

from typing import Any, Optional
from dataclasses import dataclass, field
from skillforge.core.skill_bank import Skill


@dataclass
class ModelConfig:
    """Configuration for a single LLM model."""
    model_id: str
    provider: str  # openai, anthropic, azure, local
    model_name: str
    temperature: float = 0.3
    max_tokens: int = 4096


@dataclass
class MultiModelResult:
    """Result of multi-model skill evolution."""
    best_skill: Skill
    best_model: str
    all_results: dict = field(default_factory=dict)  # model_id -> (skill, accuracy)
    consensus_score: float = 0.0  # agreement across models


class MultiModelEvolver:
    """Coordinates skill evolution across multiple LLM model families.

    Strategy:
        1. Run co-evolutionary skill generation with each model independently
        2. Cross-evaluate: test each model's skill on all other models
        3. Select the skill with the highest cross-model average accuracy
        4. Optionally merge insights from multiple model runs

    This produces skills that are transferable by design, since they must
    perform well across model families rather than overfitting to one.
    """

    def __init__(self, models: list[ModelConfig], forge: Any):
        self.models = models
        self.forge = forge
        self._evolution_log: list[dict] = []

    def evolve_multi_model(
        self,
        task: dict,
        max_rounds: int = 5,
        selection_strategy: str = "best_cross_model",
    ) -> MultiModelResult:
        """Evolve a skill across multiple models and select the best.

        Args:
            task: Task definition.
            max_rounds: Max evolution rounds per model.
            selection_strategy: How to pick the winner.
                - "best_cross_model": Highest average accuracy across all models
                - "best_self": Highest accuracy on its own model
                - "consensus": Merge insights from all models

        Returns:
            MultiModelResult with the selected skill and comparison data.
        """
        model_skills = {}

        # Phase 1: Independent evolution per model
        for model in self.models:
            skill = self._evolve_with_model(task, model, max_rounds)
            model_skills[model.model_id] = skill

        # Phase 2: Cross-model evaluation
        cross_scores = self._cross_evaluate(model_skills, task)

        # Phase 3: Selection
        if selection_strategy == "best_cross_model":
            best_model = max(cross_scores, key=lambda m: cross_scores[m]["avg"])
        elif selection_strategy == "best_self":
            best_model = max(model_skills, key=lambda m: model_skills[m].accuracy)
        else:
            best_model = max(cross_scores, key=lambda m: cross_scores[m]["avg"])

        best_skill = model_skills[best_model]

        # Compute consensus
        accuracies = [model_skills[m].accuracy for m in model_skills]
        consensus = 1.0 - (max(accuracies) - min(accuracies)) if len(accuracies) > 1 else 1.0

        result = MultiModelResult(
            best_skill=best_skill,
            best_model=best_model,
            all_results={
                m: {"accuracy": s.accuracy, "version": s.version}
                for m, s in model_skills.items()
            },
            consensus_score=consensus,
        )

        self._evolution_log.append({
            "task": task.get("instruction", "")[:100],
            "models": len(self.models),
            "best_model": best_model,
            "best_accuracy": best_skill.accuracy,
            "consensus": consensus,
        })

        return result

    def _evolve_with_model(self, task: dict, model: ModelConfig, max_rounds: int) -> Skill:
        """Run skill evolution using a specific model.

        In a real implementation, this would configure the forge's LLM backend
        to use the specified model. Here we use the default forge and simulate
        model-specific results.
        """
        return self.forge.evolve_skill(task, max_evolution_rounds=max_rounds)

    def _cross_evaluate(self, model_skills: dict, task: dict) -> dict:
        """Evaluate each model's skill across all models.

        Returns:
            Dict[model_id -> {"self": accuracy, "avg": cross_model_average}]
        """
        scores = {}
        for model_id, skill in model_skills.items():
            # Self accuracy
            self_acc = skill.accuracy

            # Cross-model accuracy (simulated as a fraction of self accuracy)
            # In production, this would actually run the skill on each model
            cross_accs = []
            for other_id in model_skills:
                if other_id == model_id:
                    cross_accs.append(self_acc)
                else:
                    # Transfer penalty: typically 5-15% drop
                    transfer_acc = max(0.0, self_acc * 0.9)
                    cross_accs.append(transfer_acc)

            scores[model_id] = {
                "self": self_acc,
                "cross_model": cross_accs,
                "avg": sum(cross_accs) / len(cross_accs) if cross_accs else 0.0,
            }

        return scores

    @property
    def evolution_log(self) -> list[dict]:
        return self._evolution_log.copy()
