"""Skill Generator: Creates and iteratively refines multi-artifact skill packages."""

from typing import Any, Optional
from skillforge.config import SkillConfig
from skillforge.core.skill_bank import Skill


class SkillGenerator:
    """Generates and refines structured skill packages."""

    def __init__(self, config: SkillConfig):
        self.config = config
        self._context_history: list[dict] = []

    def generate(self, context: dict) -> Skill:
        """Generate an initial skill package (v0) from task context.

        Args:
            context: Dict with 'instruction', 'environment', and optional 'memory'.

        Returns:
            Initial Skill object.
        """
        instruction = context["instruction"]
        environment = context.get("environment", {})
        memory = context.get("memory", [])

        # Build skill artifacts
        skill_md = self._generate_skill_document(instruction, environment, memory)
        scripts = self._generate_scripts(instruction, environment)

        skill = Skill(
            trigger_condition=self._extract_trigger(instruction),
            strategy=skill_md,
            accuracy=0.0,
            version=0,
            artifacts={"SKILL.md": skill_md, **scripts},
            failure_buffer=[],
        )

        self._context_history = [context]
        return skill

    def refine(self, skill: Skill, context: dict) -> Skill:
        """Refine an existing skill based on verification feedback.

        Args:
            skill: Current skill version.
            context: Updated context including feedback from verifier.

        Returns:
            Refined Skill with incremented version.
        """
        feedback = context.get("feedback", {})
        self._context_history.append(context)

        # Incorporate failure diagnostics into skill revision
        revised_strategy = self._revise_strategy(skill.strategy, feedback)
        revised_scripts = self._revise_scripts(skill.artifacts, feedback)

        return Skill(
            trigger_condition=skill.trigger_condition,
            strategy=revised_strategy,
            accuracy=skill.accuracy,
            version=skill.version + 1,
            artifacts={"SKILL.md": revised_strategy, **revised_scripts},
            failure_buffer=skill.failure_buffer + [feedback],
        )

    def _generate_skill_document(self, instruction: str, environment: dict, memory: list) -> str:
        """Generate the SKILL.md workflow document."""
        tools = environment.get("tools", [])
        tool_list = ", ".join(tools) if tools else "general-purpose"

        return f"""# Skill: Task Execution Guide

## Trigger Condition
{instruction[:200]}

## Strategy
1. Analyze the task requirements and identify sub-tasks
2. Set up the execution environment with: {tool_list}
3. Implement each sub-task following the workflow below
4. Validate outputs against expected format and constraints
5. Handle edge cases and error conditions

## Workflow
- Step 1: Parse and validate all inputs
- Step 2: Execute core logic
- Step 3: Format and validate outputs
- Step 4: Run self-checks

## Common Pitfalls
- Verify input data format before processing
- Handle missing or malformed data gracefully
- Ensure output precision matches requirements
"""

    def _generate_scripts(self, instruction: str, environment: dict) -> dict:
        """Generate executable utility scripts."""
        return {}

    def _extract_trigger(self, instruction: str) -> str:
        """Extract a concise trigger condition from the instruction."""
        return instruction[:200].strip()

    def _revise_strategy(self, current_strategy: str, feedback: dict) -> str:
        """Revise the strategy based on failure feedback."""
        failure_summary = feedback.get("summary", "Unknown failure")
        suggestions = feedback.get("suggestions", [])

        revision_notes = f"\n## Revision Notes (v{len(self._context_history)})\n"
        revision_notes += f"- Previous failure: {failure_summary}\n"
        for suggestion in suggestions:
            revision_notes += f"- Fix applied: {suggestion}\n"

        return current_strategy + revision_notes

    def _revise_scripts(self, current_artifacts: dict, feedback: dict) -> dict:
        """Revise scripts based on failure feedback."""
        scripts = {k: v for k, v in current_artifacts.items() if k != "SKILL.md"}
        return scripts
