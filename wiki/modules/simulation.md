---
title: "Simulation Runner"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [evaluation, simulation, human-vs-ai]
sources: []
related: [benchmark, system-overview]
source_paths:
  - src/skillforge/evaluation/simulation.py
status: verified
---

# Simulation Runner

Controlled human vs AI skill evaluation runner.

## Purpose

Compares human-authored skills against AI-evolved skills on the same task set, producing per-task and aggregate comparison reports.

## Public Interface

### Class: `SimulationTaskResult`

Per-task comparison: human/AI pass_rate, authoring_time, iterations, lines, winner.

### Class: `SimulationReport`

Aggregate results with failure_analysis and insights.

### Class: `SimulationRunner`

| Method | Signature | Description |
|--------|-----------|-------------|
| `run_simulation` | `(tasks, human_skills, test_suite) → SimulationReport` | Run controlled comparison |
| `run_synthetic_simulation` | `(num_tasks) → SimulationReport` | Generate synthetic data for demo |

## Dependencies

None — standalone evaluation runner.

## Dependents

- Used by benchmarking workflows.

## Directory

```
src/skillforge/evaluation/simulation.py
```
