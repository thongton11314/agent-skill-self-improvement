# Human vs AI Simulation Guide

## Overview

The simulation module validates SkillForge by running controlled comparisons between human-authored and AI-generated skills. Both are evaluated against a shared test suite to produce side-by-side benchmarks.

---

## Running a Simulation

### Option A: Synthetic Simulation (No Real Data Needed)

```python
from skillforge.evaluation.simulation import SimulationRunner

runner = SimulationRunner()
report = runner.run_synthetic_simulation(num_tasks=10)

# View results
print(f"AI wins: {report.aggregate_metrics['ai_wins']}")
print(f"Human wins: {report.aggregate_metrics['human_wins']}")
print(f"Speed ratio: {report.aggregate_metrics['speed_ratio']:.1f}x")

for insight in report.insights:
    print(f"  - {insight}")

# Save
runner.save_report(report, "simulation/results/simulation_results.json")
```

### Option B: Full Simulation with Real Data

1. **Prepare task set** — see `simulation/tasks/simulation_tasks.json`
2. **Author human skills** — write skill artifacts for each task in `simulation/human_skills/`
3. **Run simulation**:

```python
import json
from skillforge import SkillForge
from skillforge.evaluation.simulation import SimulationRunner
from skillforge.evaluation.test_gen import SyntheticTestGenerator

# Load tasks
with open("simulation/tasks/simulation_tasks.json") as f:
    tasks = json.load(f)

# Load human skills
human_skills = {}
for task in tasks:
    skill_path = f"simulation/human_skills/{task['task_id']}_*.md"
    # Load skill content from file...
    human_skills[task["task_id"]] = loaded_skill

# Generate test suite
gen = SyntheticTestGenerator()
test_suite = gen.generate(tasks, num_cases_per_task=10)

# Run simulation
forge = SkillForge.from_config("config.yaml")
runner = SimulationRunner(forge=forge)
report = runner.run_simulation(tasks, human_skills, test_suite)

runner.save_report(report, "simulation/results/simulation_results.json")
```

---

## Task Design Guidelines

Each simulation task should:

1. Be **self-contained** — solvable without external services or credentials
2. Have **verifiable outputs** — file artifacts with checkable properties
3. Span **multiple domains** — software engineering, data analysis, scientific computing, web development, system administration
4. Range in **difficulty** — easy, medium, hard
5. Require **multi-step procedures** — not solvable with a single function call

See `simulation/tasks/simulation_tasks.json` for 10 reference tasks.

---

## Human Skill Authoring Template

When writing human skills for the simulation, follow this template:

```markdown
---
name: skill-name
description: One-line description
task_id: SIM-XXX
author: human-expert
authoring_time_minutes: N
iterations: N
---

# Skill: [Descriptive Name]

## Trigger Condition
When to apply this skill.

## Strategy
### Step 1: ...
### Step 2: ...
### Step N: ...

## Common Pitfalls
- Pitfall 1
- Pitfall 2
```

Record your authoring time honestly — include research, drafting, and review.

---

## Comparison Metrics

| Metric | Description |
|---|---|
| Pass Rate | % of test cases passed by the skill |
| Authoring / Generation Time | Wall-clock time to produce the skill |
| Iteration Count | Number of revision cycles |
| Token Cost | LLM tokens consumed (AI only) |
| Artifact Lines | Total lines in skill package |
| Error Diversity | Distribution of failure categories |

---

## Interpreting Results

- **AI wins on pass rate** → co-evolutionary verification covers more sub-tasks
- **Human wins on pass rate** → human domain intuition handles ambiguity better
- **AI always wins on speed** → expected, 5-8x faster is typical
- **Tie** → pass rates within 3pp are considered equivalent

The optimal approach is **human-AI collaboration**: human high-level strategy + AI-refined executable details.

---

## Data Files

| Path | Content |
|---|---|
| `simulation/tasks/simulation_tasks.json` | 10 reference simulation tasks |
| `simulation/human_skills/` | Human-authored skill artifacts (Markdown) |
| `simulation/ai_skills/` | AI-generated skill artifacts (auto-generated) |
| `simulation/results/simulation_results.json` | Comparison results (synthetic) |
