---
title: "Event Bus"
type: module
created: 2026-04-27
updated: 2026-04-27
tags: [agentic, events, pubsub]
sources: []
related: [forge, provider, system-overview]
source_paths:
  - src/skillforge/agentic/events.py
status: verified
---

# Event Bus

Pub/sub event system for SkillForge lifecycle events.

## Purpose

Enables event-driven integration by broadcasting lifecycle events (skill evolved, task failed, memory promoted, etc.) to registered handlers.

## Event Types

`skill.evolved`, `skill.stored`, `task.completed`, `task.failed`, `memory.recorded`, `memory.promoted`, `verifier.passed`, `verifier.failed`, `oracle.passed`, `oracle.failed`, `evolution.triggered`

## Public Interface

### Class: `SkillForgeEvent`

Event object: event_type, timestamp, data.

### Class: `SkillForgeEventBus`

| Method | Signature | Description |
|--------|-----------|-------------|
| `on` | `(event_type) → decorator` | Decorator for subscription |
| `subscribe` | `(event_type, handler)` | Programmatic registration |
| `unsubscribe` | `(event_type, handler)` | Remove handler |
| `emit` | `(event_type, data)` | Broadcast to all handlers |
| `list_event_types` | `() → list[str]` | Available event types |
| `list_subscriptions` | `() → dict` | Current subscriptions |

## Dependencies

None — standalone event system.

## Dependents

- [[forge]] — emits lifecycle events
- External systems subscribing to events

## Directory

```
src/skillforge/agentic/events.py
```
