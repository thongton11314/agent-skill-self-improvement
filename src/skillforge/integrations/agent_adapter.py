"""Agent Adapter: Wraps existing agents with SkillForge capabilities."""

from typing import Any, Optional


class AgentAdapter:
    """Wraps an existing AI agent with SkillForge skill retrieval and evolution.

    The adapter transparently:
    1. Retrieves relevant skills from the Skill Bank before task execution
    2. Augments the agent's context with skill instructions
    3. Monitors execution outcomes
    4. Triggers skill evolution when failure patterns emerge
    """

    def __init__(self, agent: Any, forge: Any, config: Optional[dict] = None):
        self.agent = agent
        self.forge = forge
        self.config = config or {}
        self._retrieval_strategy = self.config.get("retrieval_strategy", "adaptive")
        self._auto_evolve = self.config.get("auto_evolve_on_failure", True)
        self._failure_threshold = self.config.get("failure_threshold", 3)
        self._injection_mode = self.config.get("skill_injection_mode", "prepend")
        self._consecutive_failures = 0
        self._evolution_history: list[dict] = []

    def solve(self, task: dict) -> Any:
        """Solve a task using the agent with skill augmentation.

        Args:
            task: Task definition with 'instruction' and optional 'environment'.

        Returns:
            Agent execution result.
        """
        # Step 1: Retrieve relevant skills
        skills = self.forge.skill_bank.retrieve(
            query=task.get("instruction", ""),
            top_k=3,
            min_accuracy=0.5,
        )

        # Step 2: Augment task with skill context
        augmented_task = self._inject_skills(task, skills)

        # Step 3: Execute with agent
        result = self.agent.execute(augmented_task) if hasattr(self.agent, "execute") else None

        # Step 4: Monitor outcome
        success = self._evaluate_result(result)

        if success:
            self._consecutive_failures = 0
            self.on_task_complete(task, result, skills[0] if skills else None)
        else:
            self._consecutive_failures += 1
            self.on_task_failed(task, result)

            # Step 5: Auto-evolve if threshold reached
            if self._auto_evolve and self._consecutive_failures >= self._failure_threshold:
                self._trigger_evolution(task)

        return result

    def _inject_skills(self, task: dict, skills: list) -> dict:
        """Inject retrieved skills into the task context."""
        if not skills:
            return task

        skill_context = "\n\n".join(s.to_prompt_context() for s in skills)

        augmented = task.copy()
        instruction = task.get("instruction", "")

        if self._injection_mode == "prepend":
            augmented["instruction"] = f"{skill_context}\n\n{instruction}"
        elif self._injection_mode == "append":
            augmented["instruction"] = f"{instruction}\n\n{skill_context}"
        elif self._injection_mode == "system_prompt":
            augmented["system_prompt"] = skill_context

        return augmented

    def _evaluate_result(self, result: Any) -> bool:
        """Evaluate whether the result indicates success."""
        if result is None:
            return False
        if hasattr(result, "success"):
            return result.success
        return True

    def _trigger_evolution(self, task: dict):
        """Trigger skill evolution for the failing task."""
        evolved_skill = self.forge.evolve_skill(task)
        self._consecutive_failures = 0
        self._evolution_history.append({
            "task": task.get("instruction", "")[:100],
            "skill_version": evolved_skill.version,
            "accuracy": evolved_skill.accuracy,
        })
        self.on_evolution_triggered(task, "consecutive_failure_threshold")

    def on_task_complete(self, task: dict, result: Any, skill: Any):
        """Hook: Called after successful task completion. Override for custom behavior."""
        pass

    def on_task_failed(self, task: dict, result: Any):
        """Hook: Called after task failure. Override for custom behavior."""
        pass

    def on_evolution_triggered(self, task: dict, failure_pattern: str):
        """Hook: Called when skill evolution is triggered. Override for custom behavior."""
        pass

    def on_skill_evolved(self, old_skill: Any, new_skill: Any):
        """Hook: Called after successful skill evolution. Override for custom behavior."""
        pass

    def get_evolution_history(self) -> list[dict]:
        """Get the history of skill evolutions triggered by this adapter."""
        return self._evolution_history.copy()
