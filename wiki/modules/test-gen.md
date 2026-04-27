---
title: "Synthetic Test Generator"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [evaluation, testing, synthetic]
sources: []
related: [benchmark, verifier, system-overview]
source_paths:
  - src/skillforge/evaluation/test_gen.py
status: verified
---

# Synthetic Test Generator

Generate synthetic test cases for skill evaluation.

## Purpose

Creates structured test cases with assertions and difficulty levels for benchmarking skills without requiring human-written test suites.

## Public Interface

### Class: `TestCase`

Dataclass: test_id, task_id, test_type, description, assertions, expected_outcome, difficulty.

| Method | Signature | Description |
|--------|-----------|-------------|
| `to_dict` | `() → dict` | Serialize to dictionary |

### Class: `SyntheticTestGenerator`

| Method | Signature | Description |
|--------|-----------|-------------|
| `generate` | `(task, num_tests, difficulty) → list[TestCase]` | Generate synthetic test cases for a task |

## Dependencies

None — standalone generator.

## Dependents

- [[benchmark]] — generates test suites for evaluation
- [[provider]] — exposed via `skillforge.evaluator` agent

## Directory

```
src/skillforge/evaluation/test_gen.py
```
