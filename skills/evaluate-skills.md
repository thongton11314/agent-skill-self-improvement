---
name: skillforge-evaluate-skills
description: Benchmark and compare skill quality using synthetic tests. Use for quality gates, A/B testing, or before deploying skills to production.
agent_id: skillforge.evaluator
tools:
  - benchmark_runner
  - synthetic_test_gen
  - failure_analyzer
---

# Skill: Evaluate and Benchmark Skills

## When to Use

Use this skill when:
- You need to validate a new or evolved skill before deployment
- You want to compare human-authored vs AI-generated skills
- You're running a CI/CD quality gate on skill quality
- You want failure analysis to identify improvement targets

## Workflow

1. **Generate Synthetic Tests**
   ```python
   from skillforge.evaluation import SyntheticTestGenerator
   gen = SyntheticTestGenerator(domain="your_domain")
   test_suite = gen.generate(task_specs, num_cases_per_task=10)
   ```

2. **Run Benchmark**
   ```python
   from skillforge.evaluation import BenchmarkRunner
   runner = BenchmarkRunner(config={"num_seeds": 5})
   results = runner.compare(
       skills={"baseline": None, "evolved": evolved_skill, "human": human_skill},
       test_suite=test_suite,
   )
   ```

3. **Analyze Failures**
   ```python
   from skillforge.evaluation.failure import FailureAnalyzer
   analyzer = FailureAnalyzer()
   # Record failures from results...
   report = analyzer.analyze()
   ```

4. **Quality Gate Decision**
   - Pass rate > 65%: Safe to deploy
   - Pass rate 50-65%: Deploy with monitoring
   - Pass rate < 50%: Needs more evolution rounds

## Output

- Benchmark comparison table (pass rate, correctness, token cost per condition)
- Failure category distribution with entropy
- Per-domain breakdown
- Actionable improvement recommendations
