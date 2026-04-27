"""API Server: Deploy SkillForge as a REST API."""

from typing import Any, Optional
import json


def create_app(forge: Any, config: Optional[dict] = None):
    """Create a REST API application for SkillForge.

    This is a framework-agnostic factory that returns a simple
    WSGI-compatible app. In production, wrap with Flask or FastAPI.

    Endpoints:
        POST /v1/skills/evolve        Evolve a skill for a given task
        GET  /v1/skills/{skill_id}    Retrieve a specific skill
        GET  /v1/skills/search        Search skills by query
        POST /v1/skills/execute       Execute a task with a skill
        POST /v1/evaluate/benchmark   Run benchmark evaluation
        POST /v1/evaluate/test-gen    Generate synthetic tests
        GET  /v1/memory/retrieve      Query the memory system
        POST /v1/memory/record        Record a task outcome
        GET  /v1/health               Health check
    """
    config = config or {}

    class SkillForgeApp:
        """Minimal API application wrapping SkillForge."""

        def __init__(self, forge_instance):
            self.forge = forge_instance
            self.routes = {
                ("POST", "/v1/skills/evolve"): self.evolve_skill,
                ("GET", "/v1/skills/search"): self.search_skills,
                ("POST", "/v1/evaluate/test-gen"): self.generate_tests,
                ("GET", "/v1/memory/retrieve"): self.retrieve_memory,
                ("GET", "/v1/health"): self.health_check,
            }

        def handle_request(self, method: str, path: str, body: Optional[dict] = None) -> dict:
            """Route a request to the appropriate handler."""
            handler = self.routes.get((method, path))
            if handler:
                return handler(body or {})

            # Dynamic skill retrieval: GET /v1/skills/{id}
            if method == "GET" and path.startswith("/v1/skills/"):
                skill_id = path.split("/")[-1]
                return self.get_skill(skill_id)

            return {"error": "Not found", "status": 404}

        def evolve_skill(self, body: dict) -> dict:
            """POST /v1/skills/evolve"""
            task = body.get("task", {})
            evolve_config = body.get("config", {})

            skill = self.forge.evolve_skill(
                task=task,
                max_evolution_rounds=evolve_config.get("max_rounds", 5),
                max_surrogate_retries=evolve_config.get("surrogate_retries", 15),
            )

            return {
                "status": 200,
                "skill_id": skill.skill_id,
                "version": skill.version,
                "accuracy": skill.accuracy,
                "artifacts": list(skill.artifacts.keys()),
            }

        def get_skill(self, skill_id: str) -> dict:
            """GET /v1/skills/{skill_id}"""
            skill = self.forge.skill_bank.get(skill_id)
            if not skill:
                return {"error": f"Skill {skill_id} not found", "status": 404}
            return {"status": 200, "skill": skill.to_dict()}

        def search_skills(self, body: dict) -> dict:
            """GET /v1/skills/search"""
            query = body.get("q", "")
            top_k = body.get("top_k", 5)
            skills = self.forge.skill_bank.retrieve(query=query, top_k=top_k)
            return {
                "status": 200,
                "results": [s.to_dict() for s in skills],
            }

        def generate_tests(self, body: dict) -> dict:
            """POST /v1/evaluate/test-gen"""
            from skillforge.evaluation.test_gen import SyntheticTestGenerator

            domain = body.get("domain", "general")
            task_specs = body.get("task_specs", [])
            num_cases = body.get("num_cases", 10)

            gen = SyntheticTestGenerator(domain=domain)
            tests = gen.generate(task_specs, num_cases_per_task=num_cases)
            return {
                "status": 200,
                "test_count": len(tests),
                "tests": [t.to_dict() for t in tests],
            }

        def retrieve_memory(self, body: dict) -> dict:
            """GET /v1/memory/retrieve"""
            query = body.get("q", "")
            top_k = body.get("top_k", 5)
            entries = self.forge.memory.retrieve(query, top_k=top_k)
            return {
                "status": 200,
                "results": [
                    {"content": e.content, "tier": e.tier, "quality": e.quality}
                    for e in entries
                ],
            }

        def health_check(self, body: dict) -> dict:
            """GET /v1/health"""
            return {
                "status": 200,
                "healthy": True,
                "skill_bank_size": self.forge.skill_bank.size,
                "memory_stats": self.forge.memory.stats,
            }

        def run(self, host: str = "0.0.0.0", port: int = 8080):
            """Start the server (placeholder — use Flask/FastAPI in production)."""
            print(f"SkillForge API server ready at http://{host}:{port}")
            print("Endpoints:")
            for (method, path) in self.routes:
                print(f"  {method:6s} {path}")

    return SkillForgeApp(forge)
