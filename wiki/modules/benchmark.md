---
title: "Benchmark Runner"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [evaluation, benchmark, metrics]
sources: []
related: [simulation, provider, system-overview]
source_paths:
  - src/skillforge/evaluation/benchmark.py
status: verified
---

# Benchmark Runner

Multi-skill comparison and evaluation harness.

## Purpose

Runs skills against test suites and produces per-condition metrics for comparison. Supports HTML report and JSON export.

## Public Interface

### Class: `BenchmarkResult`

Metrics: pass_rate, correctness_score, tokens, execution_time, per_task_results.

### Class: `BenchmarkRunner`

| Method | Signature | Description |
|--------|-----------|-------------|
| `compare` | `(skills, test_suite, metrics) → dict` | Run multi-skill benchmark |
| `generate_report` | `(results, output)` | Write HTML report |
| `save_results` | `(results, output)` | Export JSON results |

## Dependencies

None — standalone test execution harness.

## Dependents

- [[provider]] — exposes via `skillforge.evaluator` agent

## Directory

```
src/skillforge/evaluation/benchmark.py
```
