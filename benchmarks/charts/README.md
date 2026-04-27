# Benchmark Charts

This directory contains generated benchmark visualizations.

Charts are produced by running:

```python
from skillforge.evaluation import BenchmarkRunner
runner = BenchmarkRunner()
results = runner.compare(skills, test_suite)
runner.generate_report(results, output="benchmarks/charts/report.html")
```

Currently available (synthetic/demonstrative):
- See `benchmarks/results/benchmark_results.json` for raw data
- See `README.md` Benchmarking section for rendered charts
