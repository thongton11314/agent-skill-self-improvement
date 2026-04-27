---
title: "Agent Interfaces"
type: architecture
created: 2026-04-27
updated: 2026-04-27
tags: [architecture, agents, integration, mcp, platform]
sources: []
related: [system-overview, provider, tools, events, platform-integration]
source_paths:
  - src/skillforge/agentic/provider.py
  - src/skillforge/agentic/tools.py
  - src/skillforge/agentic/events.py
  - .github/agents/
  - .github/skills/
  - .claude/skills/
  - CLAUDE.md
  - AGENTS.md
status: verified
---

# Agent Interfaces

How SkillForge exposes its capabilities to external orchestrators.

## Available Agents

| Agent ID | Purpose | Stateful |
|---|---|---|
| `skillforge.evolver` | Evolve a skill through co-evolutionary verification | Yes |
| `skillforge.retriever` | Find relevant skills from the Skill Bank | No |
| `skillforge.executor` | Execute a task using a specific skill | Yes |
| `skillforge.evaluator` | Benchmark skill quality with synthetic tests | No |
| `skillforge.memory` | Query tiered memory for experience and patterns | No |

## Integration Protocols

### Tool Registration

Register as callable tools in LangChain / AutoGen / Semantic Kernel via `SkillForgeTool` wrappers. Factory: `create_tools(forge)`.

### Sub-Agent Delegation

Invoke via `SkillForgeAgentProvider.get_agent(agent_id)`. Supports both sync (`invoke_sync`) and async (`invoke`) interfaces.

### Event-Driven

Subscribe to lifecycle events via `SkillForgeEventBus`. Events: `skill.evolved`, `skill.stored`, `task.completed`, `task.failed`, `memory.recorded`, `memory.promoted`, `verifier.passed/failed`, `oracle.passed/failed`, `evolution.triggered`.

### MCP Server

Expose as Model Context Protocol server. Tools: `skillforge_evolve_skill`, `skillforge_find_skill`, `skillforge_run_with_skill`, `skillforge_query_memory`, `skillforge_evaluate`.

### REST API

HTTP endpoints via `create_app(forge, config)`. See [[api-server]] for full route table.

## Collaboration Pattern

```
Orchestrator → SkillRetriever → SkillExecutor → Memory
     │                                            │
     └── (no skill) → SkillEvolver ───────────────┘
```

## Platform Integration

SkillForge provides native integration files for three AI coding platforms. See [[platform-integration]] for full details.

| Platform | Discovery File | Agents | Skills |
|----------|---------------|--------|--------|
| VS Code Copilot Chat | `.github/copilot-instructions.md` | 3 `.agent.md` files | 3 `SKILL.md` files |
| Claude Code / Workspace | `CLAUDE.md` | — | 3 `SKILL.md` files |
| OpenAI Codex | `AGENTS.md` (root) | — | `skills/*.md` |
