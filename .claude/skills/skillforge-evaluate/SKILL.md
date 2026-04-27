---
name: skillforge-evaluate
description: 'Benchmark and compare skill quality using synthetic tests. Use when: evaluate skill, benchmark skill, compare skills, quality gate, A/B test, skill metrics, validate skill.'
---

# Evaluate and Benchmark Skills

## When to Use

- Validate a new or evolved skill before deployment
- Compare human-authored vs AI-generated skills
- Run a CI/CD quality gate on skill quality
- Identify failure patterns for targeted improvement

## Procedure

### 1. Generate Synthetic Tests

```python
from skillforge.evaluation import SyntheticTestGenerator

gen = SyntheticTestGenerator(domain="your_domain")
test_suite = gen.generate(task_specs, num_cases_per_task=10)
```

### 2. Run Benchmark

```python
from skillforge.evaluation import BenchmarkRunner

runner = BenchmarkRunner(config={"num_seeds": 5})
results = runner.compare(
    skills={"baseline": None, "evolved": evolved_skill, "human": human_skill},
    test_suite=test_suite,
)
```

### 3. Analyze Failures

```python
from skillforge.evaluation.failure import FailureAnalyzer

analyzer = FailureAnalyzer()
report = analyzer.analyze()
```

### 4. Quality Gate Decision

| Pass Rate | Decision |
|-----------|----------|
| > 65% | Safe to deploy |
| 50–65% | Deploy with monitoring |
| < 50% | Needs more evolution rounds |
