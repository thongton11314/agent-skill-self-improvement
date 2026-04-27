---
name: skillforge-retrieve-and-apply
description: Find an existing skill from the Skill Bank and apply it to a task. Use when you suspect a reusable skill exists for the current task.
agent_id: skillforge.retriever
tools:
  - skill_bank
  - adaptive_retrieval
  - memory_manager
---

# Skill: Retrieve and Apply an Existing Skill

## When to Use

Use this skill when:
- You have a task and want to check if a relevant skill already exists
- You want to augment your agent's prompt with domain-specific guidance
- You want to reuse proven procedures instead of solving from scratch

## Workflow

1. **Query the Skill Bank**
   ```python
   skills = forge.skill_bank.retrieve(
       query="your task description",
       top_k=3,
       min_accuracy=0.5,
   )
   ```

2. **Evaluate Relevance**
   - Check `trigger_condition` — does it match your task?
   - Check `accuracy` — prefer skills with > 0.7
   - Check `version` — higher versions are more refined

3. **Apply the Skill**
   ```python
   # Option A: Inject into prompt
   augmented_prompt = skill.to_prompt_context() + "\n\n" + task_instruction

   # Option B: Use the adapter
   from skillforge.integrations import AgentAdapter
   adapter = AgentAdapter(agent=your_agent, forge=forge)
   result = adapter.solve(task)
   ```

4. **Report Outcome**
   ```python
   # Record success/failure for future learning
   forge.memory.record(task, skill, {"status": "success"})
   ```

## Decision Tree

```
Task arrives
    │
    ├─ Retrieve skills (top_k=3)
    │
    ├─ Match found (accuracy > 0.7)?
    │   ├─ YES → Apply skill → Record outcome
    │   └─ NO  → Evolve new skill (use evolve-skill.md)
    │
    └─ Multiple matches?
        ├─ Pick highest accuracy
        └─ Or try top-2 and compare results
```

## Key Constraints

- Retrieval uses the Adaptive Retrieval Controller (Thompson Sampling)
- Relevance scoring combines: keyword match, quality, recency, tier boost
- Recording outcomes improves future retrieval quality
