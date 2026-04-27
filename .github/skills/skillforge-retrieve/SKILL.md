---
name: skillforge-retrieve
description: 'Find and apply existing skills from the SkillForge Skill Bank. Use when: find skill, search skills, retrieve skill, apply skill, reuse skill, skill lookup, check skill bank.'
---

# Retrieve and Apply an Existing Skill

## When to Use

- You have a task and want to check if a relevant skill already exists
- You want to augment your agent prompt with domain-specific guidance
- You want to reuse proven procedures instead of solving from scratch

## Procedure

### 1. Query the Skill Bank

```python
from skillforge import SkillForge

forge = SkillForge.from_config("config.yaml")
skills = forge.skill_bank.retrieve(
    query="your task description",
    top_k=3,
    min_accuracy=0.5,
)
```

### 2. Evaluate Relevance

For each returned skill, check:
- `trigger_condition` — does it match your task?
- `accuracy` — prefer skills with > 0.7
- `version` — higher versions are more refined

### 3. Apply the Skill

**Option A: Inject into prompt**
```python
augmented_prompt = skill.to_prompt_context() + "\n\n" + task_instruction
```

**Option B: Use the adapter**
```python
from skillforge.integrations import AgentAdapter

adapter = AgentAdapter(agent=your_agent, forge=forge)
result = adapter.solve(task)
```

### 4. Record Outcome

```python
forge.memory.record(task, skill, {"status": "success"})
```

## Decision Tree

| Condition | Action |
|-----------|--------|
| Match found, accuracy > 0.7 | Apply skill, record outcome |
| Match found, accuracy 0.5–0.7 | Apply with monitoring |
| No match or accuracy < 0.5 | Evolve a new skill (use skillforge-evolve) |
| Multiple matches | Pick highest accuracy, or try top-2 and compare |
