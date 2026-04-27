"""SkillForge Tools — Callable tools for agent orchestrators.

Each tool wraps a SkillForge capability with a standardized interface
that agent frameworks (LangChain, AutoGen, Semantic Kernel) can discover
and invoke.
"""

from typing import Any, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class SkillForgeTool:
    """A single callable tool that wraps a SkillForge agent capability.

    Compatible with LangChain Tool, AutoGen FunctionTool, and
    Semantic Kernel KernelFunction interfaces.
    """
    agent_id: str
    name: str
    description: str = ""
    parameters: dict = field(default_factory=dict)
    _forge: Any = field(default=None, repr=False)
    _handler: Optional[Callable] = field(default=None, repr=False)

    def __call__(self, **kwargs) -> dict:
        """Invoke the tool with the given arguments."""
        if self._handler:
            return self._handler(**kwargs)
        raise NotImplementedError(f"Tool {self.name} has no handler bound. Call bind(forge) first.")

    def bind(self, forge: Any) -> "SkillForgeTool":
        """Bind this tool to a SkillForge instance."""
        self._forge = forge
        handlers = {
            "skillforge.evolver": self._handle_evolve,
            "skillforge.retriever": self._handle_retrieve,
            "skillforge.executor": self._handle_execute,
            "skillforge.evaluator": self._handle_evaluate,
            "skillforge.memory": self._handle_memory,
        }
        self._handler = handlers.get(self.agent_id)
        return self

    def _handle_evolve(self, **kwargs) -> dict:
        """Handle skill evolution requests."""
        task = kwargs.get("task", {})
        config = kwargs.get("config", {})
        skill = self._forge.evolve_skill(
            task=task,
            max_evolution_rounds=config.get("max_rounds", 5),
            max_surrogate_retries=config.get("surrogate_retries", 15),
        )
        return {
            "skill_id": skill.skill_id,
            "version": skill.version,
            "accuracy": skill.accuracy,
            "artifacts": list(skill.artifacts.keys()),
        }

    def _handle_retrieve(self, **kwargs) -> dict:
        """Handle skill retrieval requests."""
        query = kwargs.get("query", "")
        top_k = kwargs.get("top_k", 3)
        min_accuracy = kwargs.get("min_accuracy", 0.5)
        skills = self._forge.skill_bank.retrieve(query=query, top_k=top_k, min_accuracy=min_accuracy)
        return {
            "results": [
                {
                    "skill_id": s.skill_id,
                    "trigger_condition": s.trigger_condition,
                    "accuracy": s.accuracy,
                    "version": s.version,
                }
                for s in skills
            ]
        }

    def _handle_execute(self, **kwargs) -> dict:
        """Handle skill execution requests."""
        task = kwargs.get("task", {})
        skill_id = kwargs.get("skill_id", "")
        skill = self._forge.skill_bank.get(skill_id)
        if not skill:
            return {"error": f"Skill {skill_id} not found"}
        augmented = skill.to_prompt_context() + "\n\n" + task.get("instruction", "")
        return {"augmented_prompt": augmented, "skill_version": skill.version}

    def _handle_evaluate(self, **kwargs) -> dict:
        """Handle evaluation requests."""
        from skillforge.evaluation import SyntheticTestGenerator, BenchmarkRunner
        task_specs = kwargs.get("task_specs", [])
        gen = SyntheticTestGenerator()
        tests = gen.generate(task_specs, num_cases_per_task=kwargs.get("num_cases", 5))
        return {"test_count": len(tests), "tests_generated": True}

    def _handle_memory(self, **kwargs) -> dict:
        """Handle memory query requests."""
        query = kwargs.get("query", "")
        top_k = kwargs.get("top_k", 5)
        entries = self._forge.memory.retrieve(query, top_k=top_k)
        return {
            "results": [
                {"content": e.content, "tier": e.tier, "quality": e.quality}
                for e in entries
            ]
        }

    def to_langchain(self) -> dict:
        """Export as a LangChain-compatible tool definition."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "func": self.__call__,
        }

    def to_openai_function(self) -> dict:
        """Export as an OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                },
            },
        }


def create_tools(forge: Any) -> list[SkillForgeTool]:
    """Create the standard set of SkillForge tools, bound to a forge instance.

    Returns:
        List of bound SkillForgeTools ready for registration with any agent framework.
    """
    tools = [
        SkillForgeTool(
            agent_id="skillforge.evolver",
            name="skillforge_evolve_skill",
            description="Evolve a reusable skill package for a task through co-evolutionary verification. "
                        "Use when no existing skill matches the task.",
            parameters={
                "task": {"type": "object", "description": "Task with 'instruction' and 'environment' keys"},
                "config": {"type": "object", "description": "Optional: max_rounds, surrogate_retries"},
            },
        ),
        SkillForgeTool(
            agent_id="skillforge.retriever",
            name="skillforge_find_skill",
            description="Search the Skill Bank for existing skills matching a task description. "
                        "Use before evolving to avoid duplicates.",
            parameters={
                "query": {"type": "string", "description": "Task description to search for"},
                "top_k": {"type": "integer", "description": "Max results (default: 3)"},
                "min_accuracy": {"type": "number", "description": "Min accuracy threshold (default: 0.5)"},
            },
        ),
        SkillForgeTool(
            agent_id="skillforge.executor",
            name="skillforge_run_with_skill",
            description="Execute a task augmented with a specific skill from the Skill Bank.",
            parameters={
                "task": {"type": "object", "description": "Task definition"},
                "skill_id": {"type": "string", "description": "Skill ID from the bank"},
            },
        ),
        SkillForgeTool(
            agent_id="skillforge.evaluator",
            name="skillforge_evaluate",
            description="Generate synthetic tests and benchmark skill quality.",
            parameters={
                "task_specs": {"type": "array", "description": "List of task specifications"},
                "num_cases": {"type": "integer", "description": "Test cases per task (default: 5)"},
            },
        ),
        SkillForgeTool(
            agent_id="skillforge.memory",
            name="skillforge_query_memory",
            description="Query the tiered memory system for relevant experience and learned patterns.",
            parameters={
                "query": {"type": "string", "description": "What to search for"},
                "top_k": {"type": "integer", "description": "Max results (default: 5)"},
            },
        ),
    ]

    # Bind all tools to the forge instance
    for tool in tools:
        tool.bind(forge)

    return tools
