# SkillForge Agents

This file describes the SkillForge agents available for integration with external agent orchestrators and multi-agent systems.

---

## Overview

SkillForge exposes its capabilities as **discoverable agents** that any orchestration framework can invoke. Each agent has a well-defined interface, input/output schema, and set of tools it can use.

Supported orchestration patterns:
- **Direct invocation**: Call a SkillForge agent as a sub-agent from any orchestrator
- **Tool-based**: Register SkillForge functions as tools in your agent's tool registry
- **Event-driven**: Subscribe to SkillForge events (skill evolved, task completed, failure detected)
- **MCP-compatible**: Expose SkillForge as an MCP server for VS Code agents and Copilot

---

## Available Agents

### 1. SkillEvolver Agent

**Purpose**: Autonomously evolve a skill for a given task through co-evolutionary verification.

**When to use**: When you need a reusable, verified skill package for a recurring task type.

| Property | Value |
|---|---|
| Agent ID | `skillforge.evolver` |
| Input | Task instruction + environment spec |
| Output | Evolved skill package (SKILL.md + scripts) |
| Tools used | Skill Generator, Surrogate Verifier, Evolution Engine |
| Stateful | Yes (maintains evolution context across rounds) |

**Input Schema**:
```json
{
  "task": {
    "instruction": "string — what the skill should accomplish",
    "environment": {
      "language": "string — python, javascript, etc.",
      "tools": ["string — available libraries/tools"],
      "constraints": "string — optional constraints"
    }
  },
  "config": {
    "max_rounds": "int — max evolution iterations (default: 5)",
    "surrogate_retries": "int — max verifier retries per round (default: 15)"
  }
}
```

**Output Schema**:
```json
{
  "skill_id": "string",
  "version": "int",
  "accuracy": "float (0.0-1.0)",
  "artifacts": {
    "SKILL.md": "string — workflow instructions",
    "scripts/...": "string — executable code"
  },
  "evolution_trace": [
    {"round": "int", "pass_rate": "float", "action": "string"}
  ]
}
```

---

### 2. SkillRetriever Agent

**Purpose**: Find and return the most relevant existing skills from the Skill Bank for a given task.

**When to use**: Before executing a task, to check if a relevant skill already exists.

| Property | Value |
|---|---|
| Agent ID | `skillforge.retriever` |
| Input | Natural language query |
| Output | Ranked list of matching skills |
| Tools used | Skill Bank, Adaptive Retrieval Controller |
| Stateful | No |

**Input Schema**:
```json
{
  "query": "string — task description or keyword",
  "top_k": "int — max results (default: 3)",
  "min_accuracy": "float — minimum skill accuracy (default: 0.5)"
}
```

**Output Schema**:
```json
{
  "results": [
    {
      "skill_id": "string",
      "trigger_condition": "string",
      "accuracy": "float",
      "version": "int",
      "relevance_score": "float"
    }
  ]
}
```

---

### 3. SkillExecutor Agent

**Purpose**: Execute a task using a specific skill, augmenting the calling agent's context.

**When to use**: When you have a skill (from retrieval or evolution) and want to apply it to a concrete task.

| Property | Value |
|---|---|
| Agent ID | `skillforge.executor` |
| Input | Task + skill ID or skill object |
| Output | Execution result + outcome metrics |
| Tools used | Skill Bank, Memory Manager |
| Stateful | Yes (records outcomes for learning) |

**Input Schema**:
```json
{
  "task": {
    "instruction": "string",
    "environment": {}
  },
  "skill_id": "string — ID from Skill Bank",
  "record_outcome": "bool — whether to save to memory (default: true)"
}
```

---

### 4. SkillEvaluator Agent

**Purpose**: Evaluate and benchmark skill quality using synthetic test generation.

**When to use**: For quality assurance, comparing skill variants, or CI/CD gates.

| Property | Value |
|---|---|
| Agent ID | `skillforge.evaluator` |
| Input | Skill IDs + task set |
| Output | Benchmark results with metrics |
| Tools used | Benchmark Runner, Synthetic Test Gen, Failure Analyzer |
| Stateful | No |

---

### 5. MemoryConsultant Agent

**Purpose**: Query the tiered memory system for relevant experience, patterns, and rules.

**When to use**: When an external agent needs to consult accumulated experience before making a decision.

| Property | Value |
|---|---|
| Agent ID | `skillforge.memory` |
| Input | Natural language query |
| Output | Typed memory entries (episodic, semantic, procedural) |
| Tools used | Memory Manager, Adaptive Retrieval Controller |
| Stateful | No (read-only) |

---

## Integration Protocols

### Protocol 1: Tool Registration

Register SkillForge agents as callable tools in your orchestrator:

```python
# LangChain-style
from skillforge.agentic import SkillForgeTool

tools = [
    SkillForgeTool(agent_id="skillforge.retriever", name="find_skill"),
    SkillForgeTool(agent_id="skillforge.evolver", name="evolve_skill"),
    SkillForgeTool(agent_id="skillforge.executor", name="run_with_skill"),
]

agent = create_agent(llm=llm, tools=tools)
```

### Protocol 2: Sub-Agent Delegation

Delegate to SkillForge agents from an orchestrator:

```python
# AutoGen / CrewAI / Semantic Kernel style
from skillforge.agentic import SkillForgeAgentProvider

provider = SkillForgeAgentProvider(forge=forge)

# Register as a participant in multi-agent conversation
evolver = provider.get_agent("skillforge.evolver")
retriever = provider.get_agent("skillforge.retriever")

# Orchestrator delegates skill tasks
result = await orchestrator.delegate(evolver, task)
```

### Protocol 3: Event-Driven

Subscribe to SkillForge lifecycle events:

```python
from skillforge.agentic import SkillForgeEventBus

bus = SkillForgeEventBus(forge=forge)

@bus.on("skill.evolved")
def on_skill_evolved(event):
    print(f"New skill v{event.skill.version}: {event.skill.accuracy:.0%}")

@bus.on("task.failed")
def on_failure(event):
    # Trigger re-evolution or escalation
    pass

@bus.on("memory.promoted")
def on_memory_promoted(event):
    # Semantic → Procedural promotion happened
    pass
```

### Protocol 4: MCP Server

Expose SkillForge as a Model Context Protocol server:

```json
{
  "mcpServers": {
    "skillforge": {
      "command": "python",
      "args": ["-m", "skillforge.agentic.mcp_server"],
      "env": {
        "SKILLFORGE_CONFIG": "./config.yaml"
      }
    }
  }
}
```

MCP tools exposed:
- `skillforge_evolve_skill` — Evolve a skill for a task
- `skillforge_find_skill` — Search the Skill Bank
- `skillforge_run_with_skill` — Execute with skill augmentation
- `skillforge_query_memory` — Query tiered memory
- `skillforge_evaluate` — Run benchmark evaluation

---

## Skill Discovery

External agents can discover available skills via:

```python
from skillforge.agentic import SkillForgeAgentProvider

provider = SkillForgeAgentProvider(forge=forge)

# List all available agents
agents = provider.list_agents()
for agent in agents:
    print(f"{agent.id}: {agent.description}")

# List all skills in the bank
skills = forge.skill_bank.list_all()
for skill in skills:
    print(f"  [{skill.skill_id}] {skill.trigger_condition} (v{skill.version}, {skill.accuracy:.0%})")
```

---

## Multi-Agent Collaboration Pattern

SkillForge agents can participate in multi-agent workflows:

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Orchestrator │────►│ SkillRetriever   │────►│ SkillExecutor│
│  (external)  │     │ "Do we have a    │     │ "Apply skill │
│              │     │  skill for this?" │     │  to task"    │
└──────┬───────┘     └──────────────────┘     └──────┬───────┘
       │                                              │
       │  No skill found                              │ Result
       ▼                                              ▼
┌──────────────┐                              ┌──────────────┐
│ SkillEvolver │                              │ Memory       │
│ "Create one" │                              │ Consultant   │
└──────────────┘                              └──────────────┘
```
