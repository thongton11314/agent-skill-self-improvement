---
name: skillforge-evolve-skill
description: Evolve a reusable, verified skill package for any task through co-evolutionary feedback loops. Use when you need to create a new skill that doesn't exist in the Skill Bank.
agent_id: skillforge.evolver
tools:
  - skill_generator
  - surrogate_verifier
  - evolution_engine
  - skill_bank
---

# Skill: Evolve a New Skill via SkillForge

## When to Use

Use this skill when:
- You encounter a recurring task type that would benefit from a reusable procedure
- No existing skill in the Skill Bank matches the task (check with `skillforge.retriever` first)
- You want to create a verified, multi-artifact skill package (not just a one-off solution)
- The task is complex enough to benefit from structured workflow instructions + executable scripts

Do NOT use when:
- A matching skill already exists (use `skillforge.executor` instead)
- The task is trivial and doesn't warrant skill creation
- You need a one-time answer, not a reusable procedure

## Workflow

1. **Check Existing Skills First**
   - Query the Skill Bank: `forge.skill_bank.retrieve(task_instruction, top_k=3)`
   - If a skill with accuracy > 0.7 exists, use it instead of evolving a new one

2. **Prepare Task Context**
   ```python
   task = {
       "instruction": "Clear description of what the skill should accomplish",
       "environment": {
           "language": "python",
           "tools": ["list", "of", "available", "tools"],
       },
   }
   ```

3. **Evolve the Skill**
   ```python
   from skillforge import SkillForge
   forge = SkillForge.from_config("config.yaml")
   skill = forge.evolve_skill(task, max_evolution_rounds=5)
   ```

4. **Verify the Result**
   - Check `skill.accuracy` — should be > 0.7 for production use
   - Check `skill.version` — higher versions indicate more refinement
   - Review `skill.artifacts` — should contain SKILL.md at minimum

5. **Store for Reuse**
   - The skill is automatically stored in the Skill Bank
   - Future tasks matching the trigger condition will retrieve it

## Key Constraints

- Evolution typically converges in 3-5 rounds
- Each round costs ~15-20K tokens (generator + verifier)
- The Surrogate Verifier operates in isolation — it cannot see the generator's code
- If the oracle fails after surrogate passes, tests are escalated (not revealed)

## Common Pitfalls

- Don't skip the retrieval check — evolving a duplicate skill wastes compute
- Don't set `max_evolution_rounds=1` — single-pass generation performs no better than baseline
- Don't feed the verifier's internals to the generator — information isolation is critical
- Monitor convergence: if accuracy plateaus after round 3, the task may need decomposition
