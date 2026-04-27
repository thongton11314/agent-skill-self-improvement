---
title: "Memory Manager"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [memory, tiered, retrieval, thompson-sampling]
sources: []
related: [forge, provider, system-overview]
source_paths:
  - src/skillforge/memory/manager.py
status: verified
---

# Memory Manager

Three-tier learning system with adaptive retrieval via Thompson Sampling.

## Purpose

Records task outcomes as episodic memories, periodically distills them into semantic patterns, and promotes high-quality patterns to procedural rules. A Thompson Sampling policy controller selects the optimal retrieval strategy per query.

## Tiers

| Tier | Content | Promotion Threshold |
|------|---------|---------------------|
| Episodic | Raw task outcomes | Auto-distill every N records |
| Semantic | Cross-task patterns | Quality > 0.8 |
| Procedural | Executable rules | Manual or auto-promotion |

## Retrieval Policies

`none`, `recent_window`, `compressed`, `full_detailed`, `aggressive_learner`

## Public Interface

### Class: `MemoryEntry`

Record with content, tier, quality, age, tags, source_task.

### Class: `MemoryManager`

| Method | Signature | Description |
|--------|-----------|-------------|
| `record` | `(task, skill, outputs)` | Record episodic memory; triggers periodic distillation |
| `record_success` | `(task, skill, result)` | Convenience: log successful outcome |
| `record_failure` | `(task, error)` | Convenience: log failure |
| `retrieve` | `(query, top_k) → list[MemoryEntry]` | Thompson Sampling policy selection + scoring |
| `update_policy_reward` | `(policy_name, reward)` | Update retrieval policy reward |
| `stats` | property → dict | Counts per tier |

## Dependencies

- `SkillConfig` from `config.py`

## Dependents

- [[forge]] — records outcomes and retrieves experience
- [[provider]] — exposes memory query via `skillforge.memory` agent

## Directory

```
src/skillforge/memory/manager.py
```
