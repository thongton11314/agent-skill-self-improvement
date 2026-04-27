---
title: "Testing Conventions"
type: convention
created: 2026-04-27
updated: 2026-04-27
tags: [convention, testing, pytest]
sources: []
related: [python-style]
source_paths:
  - tests/
status: verified
---

# Testing Conventions

Test structure and patterns used in SkillForge.

## Framework

- `pytest` as the test runner.
- Test files in `tests/` directory at project root.
- Run with: `pytest tests/`

## File Naming

- `test_<module>.py` — one test file per logical module or concern.
- Current test files: `test_core.py`, `test_evaluation.py`, `test_generator.py`, `test_memory.py`, `test_retrieval.py`, `test_verifier.py`, `test_platform_integration.py`.

## Patterns

- Test functions: `test_<behavior_description>()`
- Fixtures for shared setup where appropriate.
- Assertions use plain `assert` statements.
- Mock external dependencies (LLM calls) in unit tests.

## Coverage Areas

| Test File | Covers |
|-----------|--------|
| `test_core.py` | `SkillForge` orchestrator, `Skill` data class |
| `test_generator.py` | `SkillGenerator` generation and refinement |
| `test_verifier.py` | `SurrogateVerifier` assertion synthesis |
| `test_memory.py` | `MemoryManager` tiers, promotion, retrieval |
| `test_retrieval.py` | `SkillBank` storage and retrieval |
| `test_evaluation.py` | `BenchmarkRunner`, `SimulationRunner` |
| `test_agentic.py` | `SkillForgeAgentProvider`, `SkillForgeTool`, `SkillForgeEventBus` |
| `test_platform_integration.py` | Cross-platform integration: VS Code Copilot agents/skills, Claude CLAUDE.md/skills, Codex AGENTS.md, cross-platform consistency, runtime alignment |
