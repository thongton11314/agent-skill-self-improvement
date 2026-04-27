---
title: "API Server"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [integrations, rest, api]
sources: []
related: [forge, system-overview]
source_paths:
  - src/skillforge/integrations/api_server.py
status: verified
---

# API Server

REST API for SkillForge operations.

## Purpose

Exposes SkillForge functionality as HTTP endpoints via a WSGI-compatible application.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/skills/evolve` | Evolve a skill for a task |
| GET | `/v1/skills/{skill_id}` | Retrieve a skill by ID |
| GET | `/v1/skills/search` | Search skills by query |
| POST | `/v1/evaluate/test-gen` | Generate synthetic tests |
| GET | `/v1/memory/retrieve` | Query tiered memory |
| GET | `/v1/health` | Health check |

## Public Interface

| Function | Signature | Description |
|----------|-----------|-------------|
| `create_app` | `(forge, config) → SkillForgeApp` | Create WSGI-compatible app |

## Dependencies

- `SkillForge` (forge instance)

## Dependents

- HTTP clients, MCP server adapter

## Directory

```
src/skillforge/integrations/api_server.py
```
