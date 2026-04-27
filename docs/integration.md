# SkillForge Integration Guide

This guide explains how to integrate SkillForge into different types of AI systems.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Integration Mode 1: Agent-Based Systems](#integration-mode-1-agent-based-systems)
- [Integration Mode 2: LLM Applications](#integration-mode-2-llm-applications)
- [Integration Mode 3: Evaluation Pipelines](#integration-mode-3-evaluation-pipelines)
- [Integration Mode 4: API-Based AI Systems](#integration-mode-4-api-based-ai-systems)
- [Integration Mode 5: Plug-in / Middleware](#integration-mode-5-plug-in--middleware)
- [Configuration Reference](#configuration-reference)
- [Memory System Configuration](#memory-system-configuration)
- [Retrieval Strategy Guide](#retrieval-strategy-guide)

---

## Architecture Overview

SkillForge exposes its capabilities through a layered API:

```
┌─────────────────────────────────────────────────┐
│              Application Layer                   │
│  (Your Agent / LLM App / Pipeline / API)        │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│            Integration Layer                     │
│  AgentAdapter │ LLMMiddleware │ APIServer        │
│  EvalRunner   │ PluginHost                       │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│              SkillForge Core                     │
│  Generator │ Verifier │ SkillBank │ Memory       │
│  Evolution │ Retrieval │ Evaluation              │
└─────────────────────────────────────────────────┘
```

---

## Integration Mode 1: Agent-Based Systems

### When to Use

Use this mode when you have an autonomous agent that performs multi-step tasks and you want to augment it with evolving skills.

### Architecture

```
┌────────────┐     ┌──────────────┐     ┌────────────┐
│   Agent     │◄───►│ AgentAdapter │◄───►│ SkillForge │
│ (existing)  │     │   (bridge)   │     │   Core     │
└────────────┘     └──────────────┘     └────────────┘
```

### Implementation

```python
from skillforge import SkillForge
from skillforge.integrations import AgentAdapter

# Step 1: Initialize SkillForge
forge = SkillForge(config={
    "llm_backend": {
        "provider": "openai",  # or "anthropic", "azure", "local"
        "model": "gpt-4",
        "api_key_env": "OPENAI_API_KEY",
    },
    "skill_bank": {
        "storage": "local",  # or "redis", "postgres", "s3"
        "path": "./skill_bank",
    },
    "memory": {
        "tiers": ["episodic", "semantic", "procedural"],
        "episodic_capacity": 500,
        "semantic_distill_interval": 10,  # episodes
        "procedural_promotion_threshold": 0.8,
    },
    "evolution": {
        "max_rounds": 5,
        "surrogate_retries": 15,
        "convergence_threshold": 0.95,
    },
})

# Step 2: Create adapter for your agent
adapter = AgentAdapter(
    agent=your_agent,
    forge=forge,
    config={
        "retrieval_strategy": "adaptive",
        "auto_evolve_on_failure": True,
        "failure_threshold": 3,  # consecutive failures trigger evolution
        "skill_injection_mode": "prepend",  # or "append", "system_prompt"
    },
)

# Step 3: Use the adapted agent
# The adapter transparently:
#   - Retrieves relevant skills before task execution
#   - Injects skill context into the agent's prompt
#   - Monitors execution outcomes
#   - Triggers skill evolution when failure patterns emerge
#   - Updates memory tiers with task experience
result = adapter.solve(task={
    "instruction": "Analyze the CSV data and generate a summary report",
    "environment": {"tools": ["python", "pandas"]},
})

# Step 4: Access evolution history
history = adapter.get_evolution_history()
for entry in history:
    print(f"  v{entry.version}: {entry.pass_rate:.0%} ({entry.trigger})")
```

### Lifecycle Hooks

```python
class CustomAgentAdapter(AgentAdapter):
    def on_skill_retrieved(self, skill, task):
        """Called when a skill is retrieved from the bank."""
        self.logger.info(f"Using skill: {skill.trigger_condition}")

    def on_task_complete(self, task, result, skill):
        """Called after task completion."""
        # Custom feedback logic
        if result.success:
            self.forge.memory.record_success(task, skill, result)
        else:
            self.forge.memory.record_failure(task, skill, result)

    def on_evolution_triggered(self, task, failure_pattern):
        """Called when skill evolution is triggered."""
        self.logger.info(f"Evolving skill for: {failure_pattern}")

    def on_skill_evolved(self, old_skill, new_skill):
        """Called after successful skill evolution."""
        delta = new_skill.accuracy - old_skill.accuracy
        self.logger.info(f"Skill improved: +{delta:.0%}")
```

---

## Integration Mode 2: LLM Applications

### When to Use

Use this mode when you have an LLM-powered application (chatbot, content generator, code assistant) and want to inject domain-specific skill context.

### Implementation

```python
from skillforge import SkillForge
from skillforge.integrations import LLMMiddleware

forge = SkillForge.from_config("config.yaml")

# Create middleware
middleware = LLMMiddleware(
    forge=forge,
    config={
        "auto_detect_domain": True,
        "context_budget": 4096,  # max tokens for skill context
        "retrieval_top_k": 3,
        "inject_position": "system",  # or "user_prefix", "few_shot"
    },
)

# Option A: Decorator-based integration
@middleware.enhance
def generate_response(prompt: str) -> str:
    """Your existing LLM call function."""
    return llm_client.complete(prompt)

# Option B: Explicit context augmentation
def process_request(user_query: str) -> str:
    # Get skill-augmented context
    augmented_prompt = middleware.augment(user_query)

    # Call your LLM
    response = llm_client.complete(augmented_prompt)

    # Record outcome for learning
    middleware.record_outcome(user_query, response, success=True)

    return response

# Option C: Streaming integration
async def stream_response(user_query: str):
    augmented = middleware.augment(user_query)
    async for chunk in llm_client.stream(augmented):
        yield chunk
    middleware.record_outcome(user_query, collected_response)
```

### Context Injection Strategies

| Strategy | Description | Best For |
|---|---|---|
| `system` | Inject skills into system prompt | Chat applications |
| `user_prefix` | Prepend skill context before user message | Single-turn queries |
| `few_shot` | Include skill as few-shot examples | Code generation |
| `tool_description` | Add skills as tool descriptions | Tool-using agents |
| `rag_context` | Blend with RAG retrieval results | Knowledge-intensive apps |

---

## Integration Mode 3: Evaluation Pipelines

### When to Use

Use this mode when you want to evaluate skill quality, benchmark different approaches, or integrate skill testing into CI/CD.

### Implementation

```python
from skillforge.evaluation import (
    BenchmarkRunner,
    SyntheticTestGenerator,
    FailureAnalyzer,
    ComparisonReport,
)

# Step 1: Generate synthetic test cases
test_gen = SyntheticTestGenerator(
    domain="software_engineering",
    strategies=["instruction_derived", "output_probe", "metamorphic", "adversarial"],
)

test_suite = test_gen.generate(
    task_specs=load_task_specs("tasks/"),
    num_cases_per_task=10,
    difficulty_distribution={"easy": 0.3, "medium": 0.5, "hard": 0.2},
)

# Step 2: Define skill variants to compare
skills = {
    "no_skill": None,
    "human_curated": load_skills("human_skills/"),
    "skillforge_v1": forge.skill_bank.get_latest(version=1),
    "skillforge_v5": forge.skill_bank.get_latest(version=5),
}

# Step 3: Run benchmarks
runner = BenchmarkRunner(
    agent=evaluation_agent,
    config={
        "num_seeds": 5,
        "timeout_per_task": 300,  # seconds
        "parallel_workers": 4,
    },
)

results = runner.compare(skills=skills, test_suite=test_suite)

# Step 4: Analyze failures
analyzer = FailureAnalyzer()
failure_report = analyzer.analyze(
    results=results,
    categories=["coverage", "logic", "precision", "algorithm", "edge_case"],
)

# Step 5: Generate comparison report
report = ComparisonReport(results, failure_report)
report.save_html("benchmark_report.html")
report.save_json("benchmark_results.json")
report.print_summary()
```

### CI/CD Integration

```yaml
# .github/workflows/skill-evaluation.yml
name: Skill Quality Gate
on: [push, pull_request]

jobs:
  evaluate-skills:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: pip install skillforge
      - name: Run skill benchmarks
        run: python -m skillforge.evaluation.run --config eval_config.yaml
      - name: Check quality gate
        run: |
          python -c "
          import json
          results = json.load(open('benchmark_results.json'))
          assert results['pass_rate'] >= 0.65, f'Pass rate {results[\"pass_rate\"]:.0%} below threshold'
          print('Quality gate passed')
          "
```

---

## Integration Mode 4: API-Based AI Systems

### When to Use

Use this mode when you want to expose SkillForge as a standalone service that other systems can call via HTTP.

### Implementation

```python
from skillforge.server import create_app

# Create the API server
app = create_app(
    forge=forge,
    config={
        "host": "0.0.0.0",
        "port": 8080,
        "auth": {"type": "api_key", "header": "X-API-Key"},
        "rate_limit": {"requests_per_minute": 60},
        "cors": {"origins": ["*"]},
    },
)

# Run the server
if __name__ == "__main__":
    app.run()
```

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/v1/skills/evolve` | Evolve a skill for a given task |
| `GET` | `/v1/skills/{skill_id}` | Retrieve a specific skill |
| `GET` | `/v1/skills/search` | Search skills by query |
| `POST` | `/v1/skills/execute` | Execute a task with a skill |
| `POST` | `/v1/evaluate/benchmark` | Run benchmark evaluation |
| `POST` | `/v1/evaluate/test-gen` | Generate synthetic tests |
| `GET` | `/v1/memory/retrieve` | Query the memory system |
| `POST` | `/v1/memory/record` | Record a task outcome |
| `GET` | `/v1/health` | Health check |

### Example API Calls

```bash
# Evolve a skill
curl -X POST http://localhost:8080/v1/skills/evolve \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "task": {
      "instruction": "Parse and validate JSON configuration files",
      "environment": {"tools": ["python", "jsonschema"]}
    },
    "config": {
      "max_rounds": 5,
      "surrogate_retries": 10
    }
  }'

# Search for relevant skills
curl -X GET "http://localhost:8080/v1/skills/search?q=data+validation&top_k=5" \
  -H "X-API-Key: your-key"

# Run benchmark
curl -X POST http://localhost:8080/v1/evaluate/benchmark \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "skill_ids": ["skill-001", "skill-002"],
    "test_suite_id": "ts-default",
    "num_seeds": 3
  }'
```

---

## Integration Mode 5: Plug-in / Middleware

### When to Use

Use this mode when you want to add SkillForge as a transparent layer in an existing pipeline without modifying application code.

### Request/Response Middleware

```python
from skillforge.integrations import SkillForgeMiddleware

# WSGI/ASGI middleware
class SkillForgeWSGI:
    def __init__(self, app, forge):
        self.app = app
        self.forge = forge

    def __call__(self, environ, start_response):
        # Extract task context from request
        request = parse_request(environ)

        # Augment with skill context
        if self.should_augment(request):
            skill_context = self.forge.retrieve_context(request.body)
            request = self.inject_context(request, skill_context)

        # Forward to application
        response = self.app(request.environ, start_response)

        # Record outcome
        self.forge.record_outcome(request, response)

        return response

# Usage with any WSGI app
app = SkillForgeWSGI(your_app, forge)
```

### Event-Driven Integration

```python
from skillforge.integrations import EventBridge

bridge = EventBridge(forge=forge)

# Subscribe to agent events
@bridge.on("task.started")
def on_task_start(event):
    skills = forge.skill_bank.retrieve(event.task.instruction)
    event.agent.inject_skills(skills)

@bridge.on("task.failed")
def on_task_fail(event):
    forge.memory.record_failure(event.task, event.error)
    if forge.should_evolve(event.task):
        forge.evolve_skill(event.task)

@bridge.on("task.succeeded")
def on_task_success(event):
    forge.memory.record_success(event.task, event.result)
```

---

## Configuration Reference

```yaml
# config.yaml - SkillForge Configuration

llm_backend:
  provider: "openai"           # openai | anthropic | azure | local
  model: "gpt-4"
  temperature: 0.3
  max_tokens: 4096
  api_key_env: "OPENAI_API_KEY"

skill_bank:
  storage: "local"             # local | redis | postgres | s3
  path: "./skill_bank"
  max_skills: 1000
  dedup_strategy: "trigger_match"

memory:
  tiers:
    episodic:
      capacity: 500
      quality_threshold: 0.3
    semantic:
      distill_interval: 10     # episodes between distillation
      max_patterns: 200
    procedural:
      promotion_threshold: 0.8
      max_rules: 50
  retrieval:
    top_k: 5
    recency_decay: 0.01
    tier_boosts:
      episodic: 1.0
      semantic: 1.2
      procedural: 1.5

evolution:
  max_rounds: 5
  surrogate_retries: 15
  convergence_threshold: 0.95
  context_cap: 0.7             # max context usage ratio
  failure_trigger: 3           # consecutive failures to trigger

evaluation:
  timeout_per_task: 300
  parallel_workers: 4
  num_seeds: 5
  metrics:
    - pass_rate
    - correctness_score
    - evolution_efficiency
    - token_cost

server:
  host: "0.0.0.0"
  port: 8080
  auth_type: "api_key"
  rate_limit: 60               # requests per minute
```

---

## Memory System Configuration

### Retrieval Policies

| Policy | Tiers Visible | Format | Use Case |
|---|---|---|---|
| `none` | None | N/A | Simple tasks, fresh start |
| `recent_window` | Episodic | Sliding window | When recent context matters |
| `compressed` | Semantic + Procedural | Ranked + truncated | Default "high signal" mode |
| `full_detailed` | All three | Verbatim | Maximum information |
| `aggressive_learner` | All three | Large budget | Exploration phase |

### Relevance Scoring Formula

```
score(query, entry) = feature_match(query, entry)
                    × (0.5 + 0.5 × quality_score)
                    × (0.3 + 0.7 × exp(-0.01 × age))
                    × tier_boost
```

---

## Retrieval Strategy Guide

| Strategy | When to Use | Trade-off |
|---|---|---|
| **Adaptive** (recommended) | General use | Learns optimal policy over time |
| **Always** | Critical tasks | Maximum context, higher token cost |
| **Never** | Simple known tasks | Fastest, may miss useful experience |
| **Confidence-gated** | When model confidence is available | Good balance, requires calibration |
| **Proactive** | Long-horizon tasks | Learns when gaps exist, requires training |

---

*For additional help, see the [README](../README.md) or the [evaluation guide](evaluation.md).*
