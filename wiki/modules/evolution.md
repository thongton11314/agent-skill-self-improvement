---
title: "Evolution Engine"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [core, evolution, failure-driven]
sources: []
related: [forge, generator, verifier, system-overview]
source_paths:
  - src/skillforge/core/evolution.py
status: verified
---

# Evolution Engine

Failure-driven skill improvement through diagnosis and targeted repair.

## Purpose

Diagnoses failure patterns in skills and prescribes targeted evolution actions. Three severity levels: `algorithm_change`, `strategy_revision`, `parameter_tuning`.

## Public Interface

### Class: `EvolutionEngine`

| Method | Signature | Description |
|--------|-----------|-------------|
| `evolve` | `(skill, context) → Skill` | Evolve skill based on diagnosed failures |
| `evolution_history` | property → list | Log of all evolution operations |

## Dependencies

- `Skill` from [[skill-bank]]

## Dependents

- [[forge]] — invokes evolution after verification failures

## Directory

```
src/skillforge/core/evolution.py
```
