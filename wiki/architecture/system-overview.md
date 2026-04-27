---
title: "System Overview"
type: architecture
created: 2026-04-27
updated: 2026-04-27
tags: [architecture, layers, data-flow]
sources: []
related: [overview, forge, agent-interfaces]
source_paths:
  - src/skillforge/
status: verified
---

# System Overview

Top-level architecture of the SkillForge framework.

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SkillForge Framework                     │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │    Skill      │◄──►│   Surrogate  │    │   Evolution  │      │
│  │  Generator    │    │   Verifier   │    │    Engine    │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │               │
│  ┌──────▼───────────────────▼───────────────────▼───────┐      │
│  │                    Skill Bank                         │      │
│  └──────────────────────────┬───────────────────────────┘      │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────┐       │
│  │              Tiered Memory System                    │       │
│  │  ┌───────────┐  ┌───────────┐  ┌──────────────┐    │       │
│  │  │ Episodic  │─►│ Semantic  │─►│  Procedural  │    │       │
│  │  └───────────┘  └───────────┘  └──────────────┘    │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │              Integration Layer                       │       │
│  │  Agent Adapter │ API Server │ LLM Middleware         │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Layers

| Layer | Package | Modules | Responsibility |
|-------|---------|---------|----------------|
| Core | `src/skillforge/core/` | forge, evolution, generator, skill_bank, verifier, templates, multi_model | Skill lifecycle — create, verify, evolve, store |
| Memory | `src/skillforge/memory/` | manager | Three-tier learning — episodic, semantic, procedural |
| Evaluation | `src/skillforge/evaluation/` | benchmark, simulation, metrics, test_gen, failure | Quality measurement and comparison |
| Agentic | `src/skillforge/agentic/` | provider, tools, events | Agent discovery, tool registration, event bus |
| Integrations | `src/skillforge/integrations/` | agent_adapter, api_server, llm_middleware | External system connectivity |

## Data Flow

1. **Task arrives** → `SkillForge.evolve_skill()` or `AgentAdapter.solve()`
2. **Skill retrieval** → `SkillBank.retrieve()` checks for existing skills
3. **Generation** → `SkillGenerator.generate()` creates v0 skill
4. **Verification loop** → `SurrogateVerifier.verify()` ↔ `EvolutionEngine.evolve()` co-evolve
5. **Storage** → converged skill stored in `SkillBank`
6. **Memory** → outcome recorded in `MemoryManager` (episodic → semantic → procedural)
7. **Events** → `SkillForgeEventBus` broadcasts lifecycle events

## Configuration

All modules configured via `SkillConfig` (dataclass tree):

- `llm_backend` — provider, model, temperature, max_tokens
- `skill_bank` — storage path, max skills, dedup strategy
- `memory` — tier capacities, thresholds, promotion rules
- `retrieval` — top_k, recency decay, tier boosts
- `evolution` — max rounds, convergence threshold, failure triggers
- `evaluation` — timeout, parallel workers, seed count, metrics
