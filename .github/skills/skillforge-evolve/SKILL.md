---
name: skillforge-evolve
description: 'Evolve a new verified skill package through co-evolutionary feedback loops using SkillForge. Use when: evolve skill, create skill, generate skill, build skill package, no matching skill exists, skill synthesis.'
---

# Evolve a New Skill via SkillForge

## When to Use

- You encounter a recurring task type that would benefit from a reusable procedure
- No existing skill in the Skill Bank matches the task (check with retriever first)
- You want to create a verified, multi-artifact skill package
- The task is complex enough to benefit from structured workflow instructions + scripts

## Prerequisites

```bash
pip install -r requirements.txt
```

## Procedure

### 1. Check Existing Skills First

```python
from skillforge import SkillForge

forge = SkillForge.from_config("config.yaml")
existing = forge.skill_bank.retrieve(task_instruction, top_k=3)
# If a skill with accuracy > 0.7 exists, use it instead
```

### 2. Prepare Task Context

```python
task = {
    "instruction": "Clear description of what the skill should accomplish",
    "environment": {
        "language": "python",
        "tools": ["list", "of", "available", "tools"],
    },
}
```

### 3. Evolve the Skill

```python
skill = forge.evolve_skill(
    task=task,
    max_evolution_rounds=5,
    max_surrogate_retries=15,
)
```

### 4. Verify the Result

| Accuracy | Action |
|----------|--------|
| > 0.7 | Production-ready — deploy |
| 0.5–0.7 | Deploy with monitoring |
| < 0.5 | Needs more evolution or task decomposition |

### 5. Review Artifacts

```python
print(f"Skill v{skill.version}: {skill.accuracy:.0%} accuracy")
print(f"Artifacts: {list(skill.artifacts.keys())}")
# Should contain SKILL.md at minimum
```

## Key Constraints

- Evolution converges in 3–5 rounds typically
- Each round costs ~15–20K tokens (generator + verifier)
- The Surrogate Verifier operates in isolation — never leak its internals to the generator
- Single-pass (`max_evolution_rounds=1`) performs no better than baseline
- Monitor convergence: if accuracy plateaus after round 3, decompose the task
