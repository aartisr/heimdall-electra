from __future__ import annotations

import unittest

from heimdall.edge_benchmark import EdgeBenchmarkMeasurement, EdgeResourceBudget, evaluate_edge_budget


def budget() -> EdgeResourceBudget:
    return EdgeResourceBudget("edge/1", 10.0, 64.0, 5.0, 1024.0)


def measurement(**changes: float) -> EdgeBenchmarkMeasurement:
    values: dict[str, object] = {
        "benchmark_id": "run-001", "detector_id": "detector", "detector_version": "1.0.0",
        "workload_digest": "workload", "configuration_digest": "config", "hardware_reference": "hardware evidence",
        "p95_latency_ms": 9.0, "peak_memory_mib": 63.0, "average_power_w": 4.0,
        "throughput_samples_per_s": 1025.0, "measurement_evidence_references": ("evidence",),
    }
    values.update(changes)
    return EdgeBenchmarkMeasurement(**values)  # type: ignore[arg-type]


class EdgeBenchmarkTests(unittest.TestCase):
    def test_measurement_within_explicit_budget_passes(self) -> None:
        self.assertTrue(evaluate_edge_budget(budget(), measurement()).passed)

    def test_each_resource_violation_is_visible(self) -> None:
        report = evaluate_edge_budget(budget(), measurement(
            p95_latency_ms=11.0, peak_memory_mib=65.0, average_power_w=6.0, throughput_samples_per_s=1000.0,
        ))
        self.assertFalse(report.passed)
        self.assertEqual(4, len(report.violations))

    def test_measurement_requires_traceable_lineage_and_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "lineage"):
            EdgeBenchmarkMeasurement("run", "detector", "1", "", "config", "hardware", 1, 1, 1, 1, ("evidence",))


if __name__ == "__main__":
    unittest.main()
