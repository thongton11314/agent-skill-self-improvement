---
title: "ADR-001: Use Dataclasses for Domain Objects"
type: decision
created: 2026-04-27
updated: 2026-04-27
tags: [decision, adr, dataclasses, python]
sources: []
related: [python-style, skill-bank, memory-manager]
status: active
---

# ADR-001: Use Dataclasses for Domain Objects

## Context

SkillForge needs structured domain objects (`Skill`, `MemoryEntry`, `SkillConfig`, `BenchmarkResult`, etc.) with default values, serialization, and field validation. Two main options: Python stdlib `dataclasses` or `pydantic`.

## Options Considered

1. **`@dataclass`** — Lightweight, zero dependencies, part of stdlib.
2. **`pydantic.BaseModel`** — Rich validation, JSON schema generation, but adds dependency.

## Decision

Use `@dataclass` throughout.

## Rationale

- Zero external dependencies for the core domain.
- Sufficient for the current validation needs (manual checks where needed).
- Simpler mental model — no hidden coercion or validation magic.
- `field(default_factory=...)` handles mutable defaults cleanly.
- YAML config loading via manual `from_yaml()` class methods is adequate.

## Consequences

- No automatic JSON schema generation (must be maintained manually in API docs).
- Validation logic must be explicit in `__post_init__` or factory methods.
- If richer validation becomes needed, consider migrating to Pydantic (would be a breaking change for all domain objects).

## Status

Active — all domain objects use `@dataclass`.
