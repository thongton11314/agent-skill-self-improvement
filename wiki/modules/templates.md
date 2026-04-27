---
title: "Templates"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [core, templates, domain]
sources: []
related: [generator, skill-bank, system-overview]
source_paths:
  - src/skillforge/core/templates.py
status: verified
---

# Templates

Domain-specific skill templates for accelerated skill generation.

## Purpose

Provides pre-populated v0 skill structures for common domains, reducing cold-start time for skill generation.

## Available Domains

`software_engineering`, `data_analysis`, `scientific_computing`, `web_development`, `system_administration`

## Public Interface

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_template` | `(domain) → Optional[dict]` | Get template for a domain |
| `list_domains` | `() → list[str]` | List all available domain names |
| `create_from_template` | `(domain, instruction, tools) → Skill` | Create pre-populated v0 skill |

## Dependencies

- `Skill` from [[skill-bank]]

## Dependents

- [[generator]] — uses templates for domain-accelerated generation

## Directory

```
src/skillforge/core/templates.py
```
