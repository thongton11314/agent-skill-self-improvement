---
title: "Configuration"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [config, core, settings]
sources: []
related: [forge, generator, verifier, memory-manager, system-overview, adr-001-use-dataclasses]
source_paths:
  - src/skillforge/config.py
status: verified
---

# Configuration

Central configuration management for SkillForge via nested dataclasses.

## Purpose

Defines the complete configuration tree for all SkillForge subsystems. Supports YAML loading via `from_yaml()` class method.

## Configuration Tree

| Config Class | Controls | Key Fields |
|-------------|----------|------------|
| `LLMBackendConfig` | LLM provider | provider, model, temperature, max_tokens, api_key_env |
| `SkillBankConfig` | Skill storage | storage, path, max_skills, dedup_strategy |
| `MemoryTierConfig` | Memory system | capacity, quality_threshold, distill_interval, promotion_threshold |
| `RetrievalConfig` | Retrieval policy | top_k, recency_decay, tier_boosts |
| `EvolutionConfig` | Evolution loop | max_rounds, surrogate_retries, convergence_threshold, failure_trigger |
| `EvaluationConfig` | Benchmarking | timeout_per_task, parallel_workers, num_seeds, metrics |

## Public Interface

### Class: `SkillConfig`

| Method | Signature | Description |
|--------|-----------|-------------|
| `from_yaml` | `(path) → SkillConfig` | Load configuration from YAML file |

## Dependencies

- `yaml` (third-party)

## Dependents

- [[forge]], [[generator]], [[verifier]], [[memory-manager]] — all consume `SkillConfig`

## Directory

```
src/skillforge/config.py
```
