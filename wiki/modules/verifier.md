---
title: "Surrogate Verifier"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [core, verification, testing]
sources: []
related: [forge, generator, evolution, system-overview]
source_paths:
  - src/skillforge/core/verifier.py
status: verified
---

# Surrogate Verifier

Informationally isolated test generator and validator for skill quality.

## Purpose

Synthesizes test assertions from task instructions (without access to generator internals) and validates skill outputs. Provides structured failure diagnostics for evolution.

## Public Interface

### Class: `Assertion`

Single test assertion with types: `file_exists`, `content_match`, `schema_valid`, `value_range`, `precision_check`, `edge_case`.

### Class: `VerificationResult`

Outcome with per-assertion results and aggregate `pass_rate`.

### Class: `SurrogateVerifier`

| Method | Signature | Description |
|--------|-----------|-------------|
| `verify` | `(task, outputs, retry_round) → VerificationResult` | Synthesize and run test assertions |
| `diagnose` | `(task, outputs, result) → dict` | Failure analysis with root_cause + suggestions |
| `escalate` | `(task, outputs)` | Amplify test suite when surrogate passes but oracle fails |

## Dependencies

- `SkillConfig` from `config.py`

## Dependents

- [[forge]] — invokes verification in the evolve loop

## Directory

```
src/skillforge/core/verifier.py
```
