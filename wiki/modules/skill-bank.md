---
title: "Skill Bank"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [core, storage, retrieval]
sources: []
related: [forge, generator, evolution, provider, system-overview]
source_paths:
  - src/skillforge/core/skill_bank.py
status: verified
---

# Skill Bank

Persistent repository for storing and retrieving evolved skill packages.

## Purpose

Provides CRUD operations and keyword-based retrieval for skills. Houses the `Skill` data class which is the core domain object.

## Public Interface

### Class: `Skill`

| Attribute | Type | Description |
|-----------|------|-------------|
| `trigger_condition` | str | When this skill should activate |
| `strategy` | str | High-level approach description |
| `accuracy` | float | Skill quality score (0.0–1.0) |
| `version` | int | Iteration version number |
| `artifacts` | dict | SKILL.md + script files |
| `failure_buffer` | list | Recent failure records |

| Method | Signature | Description |
|--------|-----------|-------------|
| `to_prompt_context` | `() → str` | Format skill for LLM prompt injection |
| `to_dict` | `() → dict` | Serialize to dictionary |

### Class: `SkillBank`

| Method | Signature | Description |
|--------|-----------|-------------|
| `store` | `(skill) → str` | Store skill, returns skill_id |
| `retrieve` | `(query, top_k, min_accuracy) → list[Skill]` | Keyword-based ranked retrieval |
| `get` | `(skill_id) → Skill` | Get skill by ID |
| `get_latest` | `(version) → Skill` | Get latest version |
| `list_all` | `() → list[Skill]` | List all stored skills |
| `remove` | `(skill_id)` | Delete a skill |
| `size` | property → int | Number of stored skills |

## Dependencies

None — core data store.

## Dependents

- [[forge]], [[evolution]], [[generator]], [[provider]], [[agent-adapter]], [[llm-middleware]]

## Directory

```
src/skillforge/core/skill_bank.py
```
