---
title: "Skill Generator"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [core, generator, artifacts]
sources: []
related: [forge, verifier, skill-bank, templates, system-overview]
source_paths:
  - src/skillforge/core/generator.py
status: verified
---

# Skill Generator

Creates and refines multi-artifact skill packages (SKILL.md + scripts).

## Purpose

Generates initial skill packages (v0) from task context and refines them based on verifier feedback, incrementing versions.

## Public Interface

### Class: `SkillGenerator`

| Method | Signature | Description |
|--------|-----------|-------------|
| `generate` | `(context) → Skill` | Generate initial skill (v0) with SKILL.md + scripts |
| `refine` | `(skill, context) → Skill` | Refine skill with verifier feedback, incrementing version |

## Dependencies

- `SkillConfig` from `config.py`
- `Skill` from [[skill-bank]]

## Dependents

- [[forge]] — uses generator for skill creation and refinement

## Directory

```
src/skillforge/core/generator.py
```
