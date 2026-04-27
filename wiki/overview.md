---
title: "SkillForge Overview"
type: overview
created: 2026-04-27
updated: 2026-04-27
tags: [overview, system, synthesis]
sources: []
related: [index, system-overview, deviations]
status: active
---

# SkillForge Overview

## What It Is

SkillForge is a self-evolving skill synthesis framework for AI agents. It enables autonomous generation, verification, evolution, and reuse of structured skill packages through co-evolutionary feedback loops.

## Core Mechanisms

1. **Co-Evolutionary Skill Synthesis** — A Skill Generator produces multi-artifact skill packages while a Surrogate Verifier independently generates test assertions. The two co-evolve: the generator improves skills based on verifier feedback, while the verifier escalates its tests based on skill improvements.

2. **Tiered Memory with Adaptive Retrieval** — Raw experience is progressively distilled from episodic records → semantic patterns → procedural rules. A Thompson Sampling retrieval controller decides when and what to retrieve.

3. **Failure-Driven Evolution** — Skills evolve primarily in response to diagnosed failure patterns. An LLM-driven reflection mechanism provides causal insights for targeted repairs.

## Architecture Layers

| Layer | Modules | Purpose |
|-------|---------|---------|
| **Core** | forge, evolution, generator, skill_bank, verifier, templates, multi_model | Skill lifecycle — create, verify, evolve, store |
| **Memory** | manager | Three-tier learning — episodic, semantic, procedural |
| **Evaluation** | benchmark, simulation, metrics, test_gen, failure | Quality measurement and comparison |
| **Agentic** | provider, tools, events | Agent discovery, tool registration, event bus |
| **Integrations** | agent_adapter, api_server, llm_middleware | External system connectivity |

## Key Interfaces

- **Python SDK** — `SkillForge` class as main entry point
- **REST API** — WSGI-compatible server via `create_app()`
- **Agent Protocol** — 5 discoverable agents via `SkillForgeAgentProvider`
- **Event Bus** — Pub/sub lifecycle events via `SkillForgeEventBus`
- **LLM Middleware** — Transparent skill injection decorator

## Tech Stack

- Python 3.x with dataclasses for domain objects
- YAML-based configuration (`SkillConfig`)
- Local file-based skill storage (default)
- LLM backend: OpenAI GPT-4 (configurable)

## Current State

- v0.1.0 — Core framework implemented
- All 5 layers operational with test coverage
- Benchmark and simulation harnesses functional
- Integration adapters for LangChain, AutoGen, Semantic Kernel patterns

> [!note] This overview was generated during brownfield onboarding (2026-04-27). Claims reflect the live codebase as audited. Mark any unverified claims as `(unverified — pending audit)`.
