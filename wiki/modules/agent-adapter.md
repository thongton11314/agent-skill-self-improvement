---
title: "Agent Adapter"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [integrations, adapter, augmentation]
sources: []
related: [forge, llm-middleware, system-overview]
source_paths:
  - src/skillforge/integrations/agent_adapter.py
status: verified
---

# Agent Adapter

Transparently augments existing agents with SkillForge capabilities.

## Purpose

Wraps any existing agent to automatically retrieve relevant skills, inject them into context, execute tasks, monitor outcomes, and auto-evolve on failure.

## Public Interface

### Class: `AgentAdapter`

| Method | Signature | Description |
|--------|-----------|-------------|
| `solve` | `(task) → Any` | Retrieve skills → augment context → execute → monitor → auto-evolve on failure |
| `get_evolution_history` | `() → list[dict]` | History of auto-evolutions triggered |

### Injection Modes

`prepend`, `append`, `system_prompt`

### Override Hooks

`on_task_complete()`, `on_task_failed()`, `on_evolution_triggered()`

## Dependencies

- `SkillForge` (forge instance) + existing agent

## Dependents

- External agents using SkillForge as a wrapper

## Directory

```
src/skillforge/integrations/agent_adapter.py
```
