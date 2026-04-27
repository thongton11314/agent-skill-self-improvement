"""Core SkillForge orchestrator."""

from typing import Any, Optional
from skillforge.config import SkillConfig
from skillforge.core.generator import SkillGenerator
from skillforge.core.verifier import SurrogateVerifier
from skillforge.core.skill_bank import SkillBank, Skill
from skillforge.core.evolution import EvolutionEngine
from skillforge.memory.manager import MemoryManager


class SkillForge:
    """Main entry point for the SkillForge framework."""

    def __init__(self, config: Optional[SkillConfig] = None):
        self.config = config or SkillConfig()
        self.generator = SkillGenerator(self.config)
        self.verifier = SurrogateVerifier(self.config)
        self.skill_bank = SkillBank(self.config.skill_bank)
        self.evolution_engine = EvolutionEngine(self.config.evolution)
        self.memory = MemoryManager(self.config)

    @classmethod
    def from_config(cls, path: str) -> "SkillForge":
        config = SkillConfig.from_yaml(path)
        return cls(config)

    def evolve_skill(
        self,
        task: dict,
        max_evolution_rounds: Optional[int] = None,
        max_surrogate_retries: Optional[int] = None,
    ) -> Skill:
        """Evolve a skill for the given task through co-evolutionary verification.

        Args:
            task: Task definition with 'instruction' and 'environment' keys.
            max_evolution_rounds: Override for max evolution iterations.
            max_surrogate_retries: Override for max surrogate verification retries.

        Returns:
            The evolved Skill object.
        """
        max_rounds = max_evolution_rounds or self.config.evolution.max_rounds
        max_retries = max_surrogate_retries or self.config.evolution.surrogate_retries

        # Initialize context with task instruction
        context = {"instruction": task["instruction"], "environment": task.get("environment", {})}

        # Retrieve relevant experience from memory
        memory_context = self.memory.retrieve(task["instruction"])
        if memory_context:
            context["memory"] = memory_context

        # Generate initial skill (v0)
        skill = self.generator.generate(context)

        for round_idx in range(max_rounds):
            # Execute skill to produce outputs
            outputs = self._execute_skill(skill, task)

            # Surrogate verification loop
            verification_passed = False
            for retry in range(max_retries):
                verification = self.verifier.verify(task, outputs, retry_round=retry)

                if verification.passed:
                    verification_passed = True
                    break

                # Generate failure diagnostics and refine skill
                diagnostics = self.verifier.diagnose(task, outputs, verification)
                context["feedback"] = diagnostics
                skill = self.generator.refine(skill, context)
                outputs = self._execute_skill(skill, task)

            if verification_passed:
                # Oracle validation (opaque pass/fail)
                oracle_result = self._oracle_validate(skill, task)
                if oracle_result:
                    break
                # Oracle failed - escalate verifier tests
                self.verifier.escalate(task, outputs)
            else:
                # Surrogate never passed - trigger evolution
                skill = self.evolution_engine.evolve(skill, context)

        # Store evolved skill
        self.skill_bank.store(skill)

        # Update memory with task experience
        self.memory.record(task, skill, outputs)

        return skill

    def execute_with_skill(self, agent: Any, task: dict, skill: Skill) -> Any:
        """Execute a task using a specific skill with the given agent."""
        augmented_prompt = self._augment_prompt(task, skill)
        return agent.execute(augmented_prompt)

    def _execute_skill(self, skill: Skill, task: dict) -> dict:
        """Execute a skill package in the target environment."""
        return {
            "skill_version": skill.version,
            "artifacts": skill.artifacts,
            "status": "executed",
        }

    def _oracle_validate(self, skill: Skill, task: dict) -> bool:
        """Run ground-truth oracle validation (returns opaque pass/fail)."""
        # In practice, this runs the actual test suite
        return skill.accuracy >= self.config.evolution.convergence_threshold

    def _augment_prompt(self, task: dict, skill: Skill) -> str:
        """Augment task prompt with skill context."""
        skill_context = skill.to_prompt_context()
        return f"{skill_context}\n\n{task['instruction']}"
