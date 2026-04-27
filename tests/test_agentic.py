"""Tests for Agentic Platform Integration and Phase 2 modules."""

import unittest
from skillforge.config import SkillConfig
from skillforge.core.forge import SkillForge
from skillforge.core.skill_bank import Skill
from skillforge.core.templates import get_template, list_domains, create_from_template
from skillforge.core.multi_model import MultiModelEvolver, ModelConfig
from skillforge.agentic.tools import SkillForgeTool, create_tools
from skillforge.agentic.provider import SkillForgeAgentProvider
from skillforge.agentic.events import SkillForgeEventBus, EVENT_SKILL_EVOLVED


class TestSkillForgeTools(unittest.TestCase):
    def setUp(self):
        self.forge = SkillForge()
        self.tools = create_tools(self.forge)

    def test_creates_five_tools(self):
        self.assertEqual(len(self.tools), 5)

    def test_tool_names(self):
        names = {t.name for t in self.tools}
        expected = {
            "skillforge_evolve_skill",
            "skillforge_find_skill",
            "skillforge_run_with_skill",
            "skillforge_evaluate",
            "skillforge_query_memory",
        }
        self.assertEqual(names, expected)

    def test_tools_are_bound(self):
        for tool in self.tools:
            self.assertIsNotNone(tool._forge)
            self.assertIsNotNone(tool._handler)

    def test_find_skill_callable(self):
        tool = next(t for t in self.tools if t.name == "skillforge_find_skill")
        result = tool(query="parse CSV", top_k=2)
        self.assertIn("results", result)

    def test_query_memory_callable(self):
        tool = next(t for t in self.tools if t.name == "skillforge_query_memory")
        result = tool(query="data processing")
        self.assertIn("results", result)

    def test_to_openai_function(self):
        tool = self.tools[0]
        schema = tool.to_openai_function()
        self.assertEqual(schema["type"], "function")
        self.assertIn("name", schema["function"])
        self.assertIn("description", schema["function"])

    def test_to_langchain(self):
        tool = self.tools[0]
        lc = tool.to_langchain()
        self.assertIn("name", lc)
        self.assertIn("description", lc)
        self.assertIn("func", lc)


class TestSkillForgeAgentProvider(unittest.TestCase):
    def setUp(self):
        self.forge = SkillForge()
        self.provider = SkillForgeAgentProvider(self.forge)

    def test_lists_five_agents(self):
        agents = self.provider.list_agents()
        self.assertEqual(len(agents), 5)

    def test_agent_ids(self):
        ids = self.provider.list_agent_ids()
        expected = [
            "skillforge.evolver",
            "skillforge.retriever",
            "skillforge.executor",
            "skillforge.evaluator",
            "skillforge.memory",
        ]
        self.assertEqual(sorted(ids), sorted(expected))

    def test_get_agent_by_id(self):
        agent = self.provider.get_agent("skillforge.retriever")
        self.assertIsNotNone(agent)
        self.assertEqual(agent.id, "skillforge.retriever")

    def test_retriever_invoke(self):
        agent = self.provider.get_agent("skillforge.retriever")
        result = agent.invoke_sync(query="parse CSV", top_k=2)
        self.assertIn("results", result)

    def test_memory_invoke(self):
        agent = self.provider.get_agent("skillforge.memory")
        result = agent.invoke_sync(query="data processing")
        self.assertIn("entries", result)
        self.assertIn("memory_stats", result)

    def test_unknown_agent(self):
        agent = self.provider.get_agent("skillforge.nonexistent")
        self.assertIsNone(agent)


class TestSkillForgeEventBus(unittest.TestCase):
    def setUp(self):
        self.bus = SkillForgeEventBus()

    def test_subscribe_and_emit(self):
        received = []

        @self.bus.on(EVENT_SKILL_EVOLVED)
        def handler(event):
            received.append(event)

        self.bus.emit(EVENT_SKILL_EVOLVED, {"skill_id": "s1", "version": 3})
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].data["skill_id"], "s1")

    def test_wildcard_handler(self):
        received = []
        self.bus.subscribe("*", lambda e: received.append(e))
        self.bus.emit("any.event", {"test": True})
        self.assertEqual(len(received), 1)

    def test_unsubscribe(self):
        received = []
        handler = lambda e: received.append(e)
        self.bus.subscribe("test.event", handler)
        self.bus.emit("test.event")
        self.assertEqual(len(received), 1)

        self.bus.unsubscribe("test.event", handler)
        self.bus.emit("test.event")
        self.assertEqual(len(received), 1)  # no new events

    def test_list_event_types(self):
        types = self.bus.list_event_types()
        self.assertIn(EVENT_SKILL_EVOLVED, types)
        self.assertGreater(len(types), 5)

    def test_list_subscriptions(self):
        self.bus.subscribe("a", lambda e: None)
        self.bus.subscribe("a", lambda e: None)
        self.bus.subscribe("b", lambda e: None)
        subs = self.bus.list_subscriptions()
        self.assertEqual(subs["a"], 2)
        self.assertEqual(subs["b"], 1)


class TestDomainTemplates(unittest.TestCase):
    def test_list_domains(self):
        domains = list_domains()
        self.assertIn("software_engineering", domains)
        self.assertIn("data_analysis", domains)
        self.assertIn("scientific_computing", domains)
        self.assertIn("web_development", domains)
        self.assertIn("system_administration", domains)
        self.assertEqual(len(domains), 5)

    def test_get_template(self):
        template = get_template("data_analysis")
        self.assertIsNotNone(template)
        self.assertIn("strategy_template", template)
        self.assertIn("default_tools", template)
        self.assertIn("pandas", template["default_tools"])

    def test_unknown_domain_returns_none(self):
        self.assertIsNone(get_template("quantum_physics"))

    def test_create_from_template(self):
        skill = create_from_template("software_engineering", "Build a REST API")
        self.assertEqual(skill.version, 0)
        self.assertIn("SKILL.md", skill.artifacts)
        self.assertIn("Software Engineering", skill.strategy)

    def test_create_from_unknown_domain(self):
        skill = create_from_template("unknown", "Some task")
        self.assertEqual(skill.version, 0)
        self.assertIn("SKILL.md", skill.artifacts)


class TestMultiModelEvolver(unittest.TestCase):
    def setUp(self):
        self.forge = SkillForge()
        self.models = [
            ModelConfig(model_id="model-a", provider="openai", model_name="gpt-4"),
            ModelConfig(model_id="model-b", provider="anthropic", model_name="claude"),
            ModelConfig(model_id="model-c", provider="local", model_name="llama"),
        ]
        self.evolver = MultiModelEvolver(self.models, self.forge)

    def test_evolve_multi_model(self):
        task = {"instruction": "Build a CSV parser", "environment": {"tools": ["python"]}}
        result = self.evolver.evolve_multi_model(task, max_rounds=2)
        self.assertIsNotNone(result.best_skill)
        self.assertIn(result.best_model, ["model-a", "model-b", "model-c"])
        self.assertEqual(len(result.all_results), 3)

    def test_consensus_score(self):
        task = {"instruction": "Parse JSON"}
        result = self.evolver.evolve_multi_model(task, max_rounds=1)
        self.assertGreaterEqual(result.consensus_score, 0.0)
        self.assertLessEqual(result.consensus_score, 1.0)

    def test_evolution_log(self):
        task = {"instruction": "Test task"}
        self.evolver.evolve_multi_model(task, max_rounds=1)
        log = self.evolver.evolution_log
        self.assertEqual(len(log), 1)
        self.assertIn("best_model", log[0])


if __name__ == "__main__":
    unittest.main()
