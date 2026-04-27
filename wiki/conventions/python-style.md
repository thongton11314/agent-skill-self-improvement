---
title: "Python Style Conventions"
type: convention
created: 2026-04-27
updated: 2026-04-27
tags: [convention, python, style]
sources: []
related: [testing-conventions]
source_paths:
  - src/skillforge/
status: verified
---

# Python Style Conventions

Coding patterns established in the SkillForge codebase.

## Domain Objects

- Use `@dataclass` for domain objects (e.g. `Skill`, `MemoryEntry`, `SkillConfig`, `BenchmarkResult`).
- Use `field(default_factory=...)` for mutable defaults.
- Prefer composition over inheritance.

## Configuration

- Nested dataclasses for config hierarchy: `SkillConfig` → `LLMBackendConfig`, `SkillBankConfig`, etc.
- YAML loading via `from_yaml()` class method.
- Environment variable names stored in config, not hardcoded.

## Module Structure

- One primary class per module file.
- Public interface documented via docstrings.
- Internal methods prefixed with `_`.
- `__init__.py` exports key classes for each package.

## Naming

- Classes: PascalCase (`SkillForge`, `EvolutionEngine`, `MemoryManager`)
- Functions/methods: snake_case (`evolve_skill`, `record_failure`)
- Constants: UPPER_SNAKE_CASE
- Files: snake_case (`skill_bank.py`, `multi_model.py`)

## Imports

- Standard library → third-party → local imports, separated by blank lines.
- Relative imports within `skillforge` package.

## Type Hints

- Use type hints on public method signatures.
- `Optional[X]` for nullable parameters.
- Return type annotations on public methods.
