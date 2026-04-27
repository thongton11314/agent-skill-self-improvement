---
title: "LLM Middleware"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [integrations, middleware, llm]
sources: []
related: [forge, agent-adapter, system-overview]
source_paths:
  - src/skillforge/integrations/llm_middleware.py
status: verified
---

# LLM Middleware

Transparent skill injection decorator for LLM pipelines.

## Purpose

Wraps LLM calls to automatically retrieve and inject relevant skills into prompts with token budgeting. Records outcomes to memory for continuous learning.

## Injection Positions

`system`, `user_prefix`, `few_shot`, `append`

## Public Interface

### Class: `LLMMiddleware`

| Method | Signature | Description |
|--------|-----------|-------------|
| `enhance` | `(func) → decorator` | Wrap LLM calls with skill injection |
| `augment` | `(query) → str` | Retrieve skills + inject context with token budgeting |
| `record_outcome` | `(query, response, success)` | Log augmented call results to memory |

## Dependencies

- `SkillForge` (forge instance)

## Dependents

- LLM pipeline integrations

## Directory

```
src/skillforge/integrations/llm_middleware.py
```
