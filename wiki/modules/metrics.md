---
title: "Evaluation Metrics"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [evaluation, metrics, scoring]
sources: []
related: [benchmark, simulation, system-overview]
source_paths:
  - src/skillforge/evaluation/metrics.py
status: verified
---

# Evaluation Metrics

Compute evaluation metrics from benchmark results.

## Purpose

Provides a library of metric computations for skill evaluation: pass rate, correctness, efficiency, cost, convergence, failure diversity, and generalization gap.

## Available Metrics

`pass_rate`, `correctness_score`, `evolution_efficiency`, `token_cost`, `convergence_speed`, `failure_diversity`, `generalization_gap`

## Public Interface

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_metrics` | `(results, metrics=None) → dict` | Compute selected metrics from benchmark results |

## Dependencies

None — pure computation module.

## Dependents

- [[benchmark]] — uses for metric computation in reports

## Directory

```
src/skillforge/evaluation/metrics.py
```
