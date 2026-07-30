# Edge resource benchmarks

## Purpose

The edge benchmark contract evaluates a detector run against named resource limits: p95 latency, peak memory, average power, and sustained sample throughput. Each measurement must cite a workload digest, configuration digest, hardware reference, and evidence references. A pass is impossible if any bound is exceeded.

## Scientific and performance boundary

The contract does not manufacture a benchmark or assert that a fixture run represents a radiation-tolerant flight processor. No project resource measurement is currently registered. A real Stage 2 benchmark must record the actual hardware/firmware configuration, workload corpus, thermal/power measurement method, run count, distribution/percentiles, raw measurement artifacts, and any load-shedding or fault conditions.

## Use

Benchmark budgets must be sealed into the relevant detector experiment plan before a representative run. A report is suitable for evidence review only when its workload and configuration artifacts can be independently resolved and its raw measurements are retained through the provenance controls.
