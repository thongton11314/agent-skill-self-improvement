"""SkillForge Agent Provider — Exposes SkillForge agents to orchestrators.

Provides a unified interface for multi-agent systems to discover and
delegate to SkillForge agents.
"""

from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class AgentDescriptor:
    """Describes a SkillForge agent for external discovery."""
    id: str
    name: str
    description: str
    capabilities: list[str]
    stateful: bool


class SkillForgeAgent:
    """A single SkillForge agent that can be invoked by orchestrators."""

    def __init__(self, descriptor: AgentDescriptor, forge: Any):
        self.descriptor = descriptor
        self.forge = forge
        self.id = descriptor.id
        self.name = descriptor.name

    async def invoke(self, **kwargs) -> dict:
        """Invoke this agent with the given arguments (async interface)."""
        return self.invoke_sync(**kwargs)

    def invoke_sync(self, **kwargs) -> dict:
        """Invoke this agent synchronously."""
        handlers = {
            "skillforge.evolver": self._evolve,
            "skillforge.retriever": self._retrieve,
            "skillforge.executor": self._execute,
            "skillforge.evaluator": self._evaluate,
            "skillforge.memory": self._query_memory,
        }
        handler = handlers.get(self.id)
        if not handler:
            return {"error": f"Unknown agent: {self.id}"}
        return handler(**kwargs)

    def _evolve(self, **kwargs) -> dict:
        task = kwargs.get("task", {})
        config = kwargs.get("config", {})
        skill = self.forge.evolve_skill(
            task=task,
            max_evolution_rounds=config.get("max_rounds", 5),
        )
        return {
            "skill_id": skill.skill_id,
            "version": skill.version,
            "accuracy": skill.accuracy,
            "artifacts": list(skill.artifacts.keys()),
            "evolution_rounds": skill.version,
        }

    def _retrieve(self, **kwargs) -> dict:
        query = kwargs.get("query", "")
        top_k = kwargs.get("top_k", 3)
        skills = self.forge.skill_bank.retrieve(query=query, top_k=top_k)
        return {
            "count": len(skills),
            "results": [s.to_dict() for s in skills],
        }

    def _execute(self, **kwargs) -> dict:
        task = kwargs.get("task", {})
        skill_id = kwargs.get("skill_id")
        skill = self.forge.skill_bank.get(skill_id) if skill_id else None
        if not skill:
            return {"error": "No skill found", "suggestion": "Use skillforge.evolver to create one"}
        context = skill.to_prompt_context()
        if kwargs.get("record_outcome", True):
            self.forge.memory.record(task, skill, {"status": "executed"})
        return {"skill_context": context, "skill_version": skill.version}

    def _evaluate(self, **kwargs) -> dict:
        from skillforge.evaluation import SyntheticTestGenerator, BenchmarkRunner
        task_specs = kwargs.get("task_specs", [])
        gen = SyntheticTestGenerator(domain=kwargs.get("domain", "general"))
        tests = gen.generate(task_specs, num_cases_per_task=kwargs.get("num_cases", 5))
        return {"test_count": len(tests), "status": "generated"}

    def _query_memory(self, **kwargs) -> dict:
        query = kwargs.get("query", "")
        entries = self.forge.memory.retrieve(query, top_k=kwargs.get("top_k", 5))
        return {
            "count": len(entries),
            "entries": [
                {"content": e.content, "tier": e.tier, "quality": e.quality}
                for e in entries
            ],
            "memory_stats": self.forge.memory.stats,
        }


# Agent registry
_AGENT_DESCRIPTORS = [
    AgentDescriptor(
        id="skillforge.evolver",
        name="SkillEvolver",
        description="Evolve a reusable, verified skill package for a task through co-evolutionary verification.",
        capabilities=["skill_generation", "co_evolutionary_verification", "iterative_refinement"],
        stateful=True,
    ),
    AgentDescriptor(
        id="skillforge.retriever",
        name="SkillRetriever",
        description="Search the Skill Bank for existing skills matching a task description.",
        capabilities=["skill_search", "relevance_ranking", "adaptive_retrieval"],
        stateful=False,
    ),
    AgentDescriptor(
        id="skillforge.executor",
        name="SkillExecutor",
        description="Execute a task augmented with a skill from the Skill Bank.",
        capabilities=["skill_application", "context_augmentation", "outcome_recording"],
        stateful=True,
    ),
    AgentDescriptor(
        id="skillforge.evaluator",
        name="SkillEvaluator",
        description="Benchmark and compare skill quality using synthetic test generation.",
        capabilities=["benchmarking", "synthetic_testing", "failure_analysis"],
        stateful=False,
    ),
    AgentDescriptor(
        id="skillforge.memory",
        name="MemoryConsultant",
        description="Query tiered memory for relevant experience, patterns, and procedural rules.",
        capabilities=["memory_retrieval", "experience_lookup", "pattern_matching"],
        stateful=False,
    ),
]


class SkillForgeAgentProvider:
    """Provides SkillForge agents to external orchestration frameworks.

    Usage:
        provider = SkillForgeAgentProvider(forge=forge)

        # List available agents
        for agent in provider.list_agents():
            print(f"{agent.id}: {agent.description}")

        # Get a specific agent
        evolver = provider.get_agent("skillforge.evolver")
        result = evolver.invoke_sync(task={"instruction": "..."})

        # Get all agents for registration with an orchestrator
        agents = provider.get_all_agents()
    """

    def __init__(self, forge: Any):
        self.forge = forge
        self._agents: dict[str, SkillForgeAgent] = {}
        for desc in _AGENT_DESCRIPTORS:
            self._agents[desc.id] = SkillForgeAgent(desc, forge)

    def get_agent(self, agent_id: str) -> Optional[SkillForgeAgent]:
        """Get a specific SkillForge agent by ID."""
        return self._agents.get(agent_id)

    def get_all_agents(self) -> list[SkillForgeAgent]:
        """Get all available SkillForge agents."""
        return list(self._agents.values())

    def list_agents(self) -> list[AgentDescriptor]:
        """List all available agent descriptors (for discovery)."""
        return [a.descriptor for a in self._agents.values()]

    def list_agent_ids(self) -> list[str]:
        """List all available agent IDs."""
        return list(self._agents.keys())
