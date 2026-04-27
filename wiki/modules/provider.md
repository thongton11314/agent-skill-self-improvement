---
title: "Agent Provider"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [agentic, provider, discovery]
sources: []
related: [forge, tools, events, agent-interfaces, system-overview]
source_paths:
  - src/skillforge/agentic/provider.py
status: verified
---

# Agent Provider

Registry for agent discovery and delegation.

## Purpose

Wraps the SkillForge instance into 5 standard discoverable agents with consistent invoke interfaces. External orchestrators use this to list and delegate to SkillForge agents.

## Standard Agents

| Agent ID | Purpose |
|----------|---------|
| `skillforge.evolver` | Skill evolution |
| `skillforge.retriever` | Skill search |
| `skillforge.executor` | Task execution with skill |
| `skillforge.evaluator` | Benchmark + synthetic testing |
| `skillforge.memory` | Memory queries |

## Public Interface

### Class: `AgentDescriptor`

Metadata: id, name, description, capabilities, stateful.

### Class: `SkillForgeAgent`

| Method | Signature | Description |
|--------|-----------|-------------|
| `invoke` | `(**kwargs) → Any` | Async agent invocation |
| `invoke_sync` | `(**kwargs) → Any` | Sync agent invocation |

### Class: `SkillForgeAgentProvider`

| Method | Signature | Description |
|--------|-----------|-------------|
| `list_agents` | `() → list[AgentDescriptor]` | List all available agents |
| `get_agent` | `(agent_id) → SkillForgeAgent` | Get agent by ID |

## Dependencies

- `SkillForge` (forge instance)

## Dependents

- External orchestrators (LangChain, AutoGen, Semantic Kernel)

## Directory

```
src/skillforge/agentic/provider.py
```
