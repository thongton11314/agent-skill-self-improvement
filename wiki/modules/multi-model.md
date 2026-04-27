---
title: "Multi-Model Evolver"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [core, multi-model, cross-evaluation]
sources: []
related: [forge, evolution, skill-bank, system-overview]
source_paths:
  - src/skillforge/core/multi_model.py
status: verified
---

# Multi-Model Evolver

Coordinates skill evolution across multiple LLM backends for cross-model validation.

## Purpose

Evolves skills using multiple models simultaneously and selects the best result via cross-evaluation. Supports strategies: `best_cross_model`, `best_self`, `consensus`.

## Public Interface

### Class: `ModelConfig`

Configuration for a single LLM (model_id, provider, temperature, max_tokens).

### Class: `MultiModelResult`

Result with `best_skill`, `best_model`, `all_results`, `consensus_score`.

### Class: `MultiModelEvolver`

| Method | Signature | Description |
|--------|-----------|-------------|
| `evolve_multi_model` | `(task, max_rounds, selection_strategy) → MultiModelResult` | Evolve across multiple models |

## Dependencies

- `Skill` from [[skill-bank]]

## Dependents

- [[forge]] — optional multi-model evolution path

## Directory

```
src/skillforge/core/multi_model.py
```
