---
title: "Forge"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [core, orchestrator, entry-point]
sources: []
related: [evolution, generator, skill-bank, verifier, memory-manager, system-overview]
source_paths:
  - src/skillforge/core/forge.py
status: verified
---

# Forge

Main orchestrator and entry point for the SkillForge framework.

## Purpose

Coordinates the full skill lifecycle: generation → verification → evolution → storage → execution. All other core modules are composed through this class.

## Public Interface

### Class: `SkillForge`

| Method | Signature | Description |
|--------|-----------|-------------|
| `evolve_skill` | `(task, max_evolution_rounds=5, max_surrogate_retries=15)` | Evolve a skill through co-evolutionary verification with surrogate & oracle loop |
| `execute_with_skill` | `(agent, task, skill)` | Execute a task with a specific skill, augmenting agent context |
| `from_config` | `(path) → SkillForge` | Class method to instantiate from YAML config |

## Dependencies

- `SkillGenerator` from [[generator]]
- `SurrogateVerifier` from [[verifier]]
- `SkillBank` from [[skill-bank]]
- `EvolutionEngine` from [[evolution]]
- `MemoryManager` from [[memory-manager]]

## Dependents

- [[provider]] — wraps `SkillForge` instance for agent exposure
- [[tools]] — binds tools to `SkillForge` instance
- [[agent-adapter]] — uses `forge` for skill augmentation
- [[api-server]] — routes HTTP requests to `forge` methods
- [[llm-middleware]] — retrieves skills via `forge`

## Directory

```
src/skillforge/core/forge.py
```
