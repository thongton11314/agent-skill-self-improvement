---
title: "Failure Analyzer"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [evaluation, failure, diagnostics]
sources: []
related: [benchmark, simulation, evolution, system-overview]
source_paths:
  - src/skillforge/evaluation/failure.py
status: verified
---

# Failure Analyzer

Categorize and analyze failure modes across domains.

## Purpose

Provides structured failure categorization with severity tracking. Used by the evolution engine and benchmarking to understand why skills fail.

## Failure Categories

`coverage_gaps`, `logic_errors`, `precision_failures`, `algorithm_selection`, `edge_case_misses`

## Public Interface

### Class: `FailureRecord`

Dataclass: task_id, category, description, severity (critical/major/minor), skill_version.

### Class: `FailureAnalyzer`

| Method | Signature | Description |
|--------|-----------|-------------|
| `record_failure` | `(task_id, category, description, severity, skill_version) → None` | Record a single failure |
| `analyze` | `(results, categories) → dict` | Categorize and aggregate failure patterns |
| `records` | `property → list[FailureRecord]` | Access recorded failures |

## Dependencies

None — standalone analysis module.

## Dependents

- [[evolution]] — uses failure categories for diagnosis
- [[benchmark]] — failure analysis in benchmark results

## Directory

```
src/skillforge/evaluation/failure.py
```
