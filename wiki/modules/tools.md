---
title: "Tool Wrappers"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [agentic, tools, langchain, autogen]
sources: []
related: [forge, provider, system-overview]
source_paths:
  - src/skillforge/agentic/tools.py
status: verified
---

# Tool Wrappers

LangChain / AutoGen / Semantic Kernel compatible tool wrappers.

## Purpose

Wraps SkillForge operations as callable tools with standard schemas for framework integration.

## Public Interface

### Class: `SkillForgeTool`

| Method | Signature | Description |
|--------|-----------|-------------|
| `__call__` | `(**kwargs) → dict` | Execute the tool |
| `bind` | `(forge) → Self` | Bind to a SkillForge instance |
| `to_langchain` | `() → dict` | Export as LangChain tool schema |
| `to_openai_function` | `() → dict` | Export as OpenAI function schema |

### Factory

| Function | Signature | Description |
|----------|-----------|-------------|
| `create_tools` | `(forge) → list[SkillForgeTool]` | Create standard 5 tools |

## Dependencies

- `SkillForge` (forge instance)

## Dependents

- External agents registering SkillForge as tools

## Directory

```
src/skillforge/agentic/tools.py
```
