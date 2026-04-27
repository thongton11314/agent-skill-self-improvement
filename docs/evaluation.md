# SkillForge Evaluation Methodology

## Overview

SkillForge uses an evaluation-driven design where every framework mechanism is validated through measurable metrics. This document provides the deep-dive complement to the README's Evaluation Methodology section.

---

## Evaluation Pipeline

```
Task Set → Skill Evolution → Test Execution → Metric Computation → Failure Analysis → Report
```

### Step 1: Task Set Preparation

Select tasks across multiple domains. Each task must include:
- A clear instruction with verifiable output requirements
- An environment specification (language, tools, constraints)
- A difficulty label (easy / medium / hard)
- Expected output artifacts

See `benchmarks/tasks/benchmark_tasks.json` for the reference task set.

### Step 2: Synthetic Test Generation

Generate test cases using `SyntheticTestGenerator` with five strategies:

| Strategy | Purpose | Best For |
|---|---|---|
| Instruction-derived | Extract testable requirements from instructions | All tasks |
| Output-probing | Test output format, schema, and edge values | Data-producing tasks |
| Metamorphic | Verify consistent behavior under transformations | Algorithmic tasks |
| Adversarial | Probe robustness with malformed inputs | All tasks |
| Regression | Compare against known-good outputs | Evolved skills |

### Step 3: Multi-Condition Comparison

Run each task under multiple conditions in the same environment:

1. **No-Skill Baseline** — raw agent, no skill augmentation
2. **Human-Curated Skills** — pre-authored skill packages
3. **One-Shot Self-Gen** — agent generates skills in a single pass
4. **SkillForge (N rounds)** — co-evolutionary evolution with N rounds

### Step 4: Metric Computation

All metrics are computed per-condition across the full task set:

- **Pass Rate**: Binary — all assertions must pass for a task to count
- **Correctness Score**: Fraction of individual assertions passed
- **Evolution Efficiency**: Pass rate improvement per evolution round
- **Token Cost**: Total LLM tokens consumed during evolution
- **Convergence Speed**: Rounds to reach 90% of final performance

### Step 5: Statistical Reporting

- Run each condition with 5 random seeds
- Report mean ± standard deviation
- Use paired comparisons (Δ vs baseline) for effect size

---

## Failure Analysis Framework

### Categories

| Category | Description | Detection Method |
|---|---|---|
| Coverage Gaps | Skill does not address required sub-tasks | Missing output files or fields |
| Logic Errors | Incorrect workflow sequencing | Wrong computation results |
| Precision Failures | Output format or numerical issues | Format/value assertions |
| Algorithm Selection | Wrong algorithm for problem class | Systematic pattern failures |
| Edge Case Misses | Unhandled corner cases | Adversarial test failures |

### Analysis Process

1. Collect all failed assertions across conditions
2. Classify each failure into one of the five categories
3. Compute category distribution and entropy
4. Identify the dominant failure mode per domain
5. Generate targeted improvement recommendations

---

## Running Evaluations

```python
from skillforge.evaluation import BenchmarkRunner, SyntheticTestGenerator
from skillforge.evaluation.failure import FailureAnalyzer

# 1. Generate tests
gen = SyntheticTestGenerator(domain="software_engineering")
tests = gen.generate(task_specs, num_cases_per_task=10)

# 2. Run benchmarks
runner = BenchmarkRunner(config={"num_seeds": 5})
results = runner.compare(skills=skill_variants, test_suite=tests)

# 3. Analyze failures
analyzer = FailureAnalyzer()
for result in results.values():
    for task_result in result.per_task_results:
        if not task_result["passed"]:
            analyzer.record_failure(task_result["task_id"], "logic_errors", "Computation incorrect")

report = analyzer.analyze()

# 4. Generate report
runner.generate_report(results, output="benchmark_report.html")
runner.save_results(results, output="benchmark_results.json")
```

---

## Benchmark Data

Benchmark results are stored in `benchmarks/results/`. Current data is synthetic/demonstrative. Replace with real results by running the evaluation pipeline against actual tasks and LLM backends.
