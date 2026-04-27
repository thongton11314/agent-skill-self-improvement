# CLAUDE.md — SkillForge Project Instructions for Claude Code

This file provides Claude with the context needed to work effectively on the SkillForge codebase.

## Project Overview

**SkillForge** is a self-evolving skill synthesis framework for AI agents. It enables autonomous generation, verification, evolution, and reuse of structured skill packages through co-evolutionary feedback loops.

## Key Files

- `AGENTS.md` — Schema, conventions, workflows. The single source of truth for development.
- `wiki/index.md` — Master catalog of all wiki pages.
- `wiki/log.md` — Chronological operation log.
- `wiki/overview.md` — High-level synthesis of the system.
- `src/skillforge/` — Main Python package.
- `tests/` — Test suite (`pytest tests/`).

## Directory Structure

```
src/skillforge/
  core/        — Skill lifecycle: forge, evolution, generator, skill_bank, verifier, templates, multi_model
  memory/      — Three-tier learning: episodic → semantic → procedural
  evaluation/  — Quality measurement: benchmark, simulation, metrics, test_gen, failure
  agentic/     — Agent discovery: provider, tools, events
  integrations/— External connectivity: agent_adapter, api_server, llm_middleware
tests/         — Test suite (pytest)
wiki/          — AI-maintained knowledge pages
skills/        — Discoverable skill definitions (YAML frontmatter + markdown)
```

## Development Conventions

### Python Style
- Use `dataclasses` for domain objects (not Pydantic) — see `wiki/decisions/adr-001-use-dataclasses.md`
- Type hints on all public signatures
- Docstrings on all public classes and methods
- Imports: stdlib → third-party → local, with blank lines between groups
- Error handling: validate at boundaries, not internally

### Testing
- Test files: `tests/test_<module>.py`
- Name pattern: `test_<what>_<condition>_<expected>`
- Framework: `pytest` with `unittest.mock`
- Run: `pytest tests/`

### Post-Change Pipeline (Mandatory)
After every code change, execute all 4 steps:
1. **Update the Wiki** — module pages, architecture, log.md, index.md
2. **Sync Gate** — Code-Wiki Mapping Table + bidirectional verification
3. **Run Tests** — `pytest tests/`; fix code on failure
4. **Update README.md** — if architecture, API surface, or setup changed

### Wiki Discipline
- Never modify files in `raw/` — sources are immutable
- YAML frontmatter on every wiki page
- Use `[[wikilinks]]` for cross-references
- Flag contradictions with `> [!contradiction]` callouts
- Flag breaking changes with `> [!breaking]` callouts

## Architecture

SkillForge exposes 5 discoverable agents:

| Agent ID | Purpose | Stateful |
|---|---|---|
| `skillforge.evolver` | Evolve a skill through co-evolutionary verification | Yes |
| `skillforge.retriever` | Find relevant skills from the Skill Bank | No |
| `skillforge.executor` | Execute a task using a specific skill | Yes |
| `skillforge.evaluator` | Benchmark skill quality with synthetic tests | No |
| `skillforge.memory` | Query tiered memory for experience and patterns | No |

## Integration Points

- **Python SDK**: `from skillforge import SkillForge`
- **Agent Provider**: `SkillForgeAgentProvider(forge).get_agent("skillforge.evolver")`
- **Tool Registry**: `create_tools(forge)` — compatible with LangChain/AutoGen/SK
- **Event Bus**: `SkillForgeEventBus(forge)` — pub/sub lifecycle events
- **REST API**: `create_app(forge)` — WSGI-compatible HTTP server
- **LLM Middleware**: `@LLMMiddleware(forge).enhance` — transparent skill injection

## Common Tasks

### Evolve a skill
```python
from skillforge import SkillForge
forge = SkillForge.from_config("config.yaml")
skill = forge.evolve_skill(task={"instruction": "...", "environment": {...}}, max_evolution_rounds=5)
```

### Retrieve an existing skill
```python
skills = forge.skill_bank.retrieve(query="task description", top_k=3, min_accuracy=0.5)
```

### Run benchmarks
```python
from skillforge.evaluation import BenchmarkRunner, SyntheticTestGenerator
gen = SyntheticTestGenerator(domain="software_engineering")
tests = gen.generate(task_specs, num_cases=50)
runner = BenchmarkRunner()
results = runner.compare(skills={"evolved": skill, "baseline": None}, test_suite=tests)
```

## Skills Available

Claude can use the skills in `.claude/skills/` for SkillForge-specific workflows:
- `skillforge-evolve/` — Step-by-step skill evolution procedure
- `skillforge-retrieve/` — Find and apply existing skills
- `skillforge-evaluate/` — Benchmark and compare skill quality
