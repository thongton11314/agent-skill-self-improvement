---
title: "Platform Integration"
type: architecture
created: 2026-04-27
updated: 2026-04-27
tags: [architecture, platform, copilot, claude, codex, integration]
sources: []
related: [agent-interfaces, system-overview, provider, tools]
source_paths:
  - .github/copilot-instructions.md
  - .github/agents/skillforge-evolver.agent.md
  - .github/agents/skillforge-retriever.agent.md
  - .github/agents/skillforge-evaluator.agent.md
  - .github/skills/skillforge-evolve/SKILL.md
  - .github/skills/skillforge-retrieve/SKILL.md
  - .github/skills/skillforge-evaluate/SKILL.md
  - CLAUDE.md
  - .claude/skills/skillforge-evolve/SKILL.md
  - .claude/skills/skillforge-retrieve/SKILL.md
  - .claude/skills/skillforge-evaluate/SKILL.md
  - AGENTS.md
  - skills/evolve-skill.md
  - skills/retrieve-and-apply.md
  - skills/evaluate-skills.md
status: verified
---

# Platform Integration

How SkillForge integrates natively with three AI coding platforms: VS Code Copilot Chat, Claude Code, and OpenAI Codex.

## Overview

| Platform | Context File | Custom Agents | Skills | Discovery |
|----------|-------------|---------------|--------|-----------|
| VS Code Copilot Chat | `.github/copilot-instructions.md` | 3 (`.agent.md`) | 3 (`SKILL.md`) | `@` picker + `/` slash commands |
| Claude Code / Workspace | `CLAUDE.md` | — | 3 (`.claude/skills/`) | Auto-loaded at session start |
| OpenAI Codex | `AGENTS.md` | — | 3 (`skills/`) | Auto-read from repo root |

## VS Code Copilot Chat

### Files

| File | Purpose |
|------|---------|
| `.github/copilot-instructions.md` | Project-wide instructions loaded into every Copilot session |
| `.github/agents/skillforge-evolver.agent.md` | Custom agent: evolve skills via co-evolutionary loops |
| `.github/agents/skillforge-retriever.agent.md` | Custom agent: find and apply existing skills |
| `.github/agents/skillforge-evaluator.agent.md` | Custom agent: benchmark and compare skill quality |
| `.github/skills/skillforge-evolve/SKILL.md` | Skill: step-by-step skill evolution procedure |
| `.github/skills/skillforge-retrieve/SKILL.md` | Skill: find and apply existing skills |
| `.github/skills/skillforge-evaluate/SKILL.md` | Skill: benchmark and compare skill quality |

### Agent Format

Agents use `.agent.md` files with YAML frontmatter:

```yaml
---
description: "Trigger phrases for discovery"
name: "Agent Name"
tools: [read, edit, execute, search]
argument-hint: "Task description"
---
```

- Agents appear in the `@` agent picker in Copilot Chat
- Each agent has a focused role with minimal tool set
- Description field enables automatic delegation from parent agents

### Skill Format

Skills use `SKILL.md` files inside named folders:

```yaml
---
name: skill-name
description: 'What and when to use.'
---
```

- Skills appear as `/` slash commands in Copilot Chat
- Progressive loading: discovery (frontmatter) → instructions (body) → resources (linked files)
- Folder name must match the `name` field

### Setup

1. Open the repo in VS Code with GitHub Copilot Chat extension
2. Agents auto-discovered from `.github/agents/`
3. Skills auto-discovered from `.github/skills/`

## Claude Code / Claude Workspace

### Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project context loaded at the start of every Claude session |
| `.claude/skills/skillforge-evolve/SKILL.md` | Skill: step-by-step skill evolution procedure |
| `.claude/skills/skillforge-retrieve/SKILL.md` | Skill: find and apply existing skills |
| `.claude/skills/skillforge-evaluate/SKILL.md` | Skill: benchmark and compare skill quality |

### CLAUDE.md Contents

- Project overview and architecture summary
- Directory structure and module map
- Development conventions (Python style, testing, post-change pipeline)
- Common tasks with code examples (evolve, retrieve, benchmark)
- References to `.claude/skills/` for guided workflows

### Setup

1. Open the repo in Claude Code or attach as a Claude workspace
2. `CLAUDE.md` is read automatically at session start
3. Skills are discovered from `.claude/skills/`

## OpenAI Codex

### Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Full project schema, conventions, workflows, and agent interfaces |
| `skills/evolve-skill.md` | Cross-platform skill: evolve new skills |
| `skills/retrieve-and-apply.md` | Cross-platform skill: find and apply existing skills |
| `skills/evaluate-skills.md` | Cross-platform skill: benchmark skill quality |

### Setup

1. Open the repo in Codex
2. `AGENTS.md` at the repo root is read automatically
3. `skills/` directory contains framework-agnostic YAML+markdown skill definitions

## Cross-Platform Skill Definitions

The `skills/` directory at the repo root contains framework-agnostic versions that any platform can reference. Platform-specific copies in `.github/skills/` and `.claude/skills/` follow the same content but use platform-specific discovery formats.

| Skill | File | Purpose |
|-------|------|---------|
| Evolve | `skills/evolve-skill.md` | Create a new verified skill package |
| Retrieve | `skills/retrieve-and-apply.md` | Find and apply existing skills |
| Evaluate | `skills/evaluate-skills.md` | Benchmark and compare skill quality |
