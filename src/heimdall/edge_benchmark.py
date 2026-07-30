"""Traceable resource-budget evaluation for future edge detector runs."""

from __future__ import annotations

from dataclasses import dataclass

from .governance import digest_value


@dataclass(frozen=True)
class EdgeResourceBudget:
    budget_id: str
    maximum_p95_latency_ms: float
    maximum_peak_memory_mib: float
    maximum_average_power_w: float
    minimum_throughput_samples_per_s: float

    def __post_init__(self) -> None:
        if not self.budget_id or min(
            self.maximum_p95_latency_ms, self.maximum_peak_memory_mib,
            self.maximum_average_power_w, self.minimum_throughput_samples_per_s,
        ) <= 0:
            raise ValueError("edge resource budget requires positive bounds")


@dataclass(frozen=True)
class EdgeBenchmarkMeasurement:
    benchmark_id: str
    detector_id: str
    detector_version: str
    workload_digest: str
    configuration_digest: str
    hardware_reference: str
    p95_latency_ms: float
    peak_memory_mib: float
    average_power_w: float
    throughput_samples_per_s: float
    measurement_evidence_references: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all((
            self.benchmark_id, self.detector_id, self.detector_version, self.workload_digest,
            self.configuration_digest, self.hardware_reference, self.measurement_evidence_references,
        )):
            raise ValueError("edge benchmark identity, lineage, hardware, and evidence are required")
        if min(self.p95_latency_ms, self.peak_memory_mib, self.average_power_w, self.throughput_samples_per_s) < 0:
            raise ValueError("edge benchmark measurements must be non-negative")

    @property
    def digest(self) -> str:
        return digest_value(self)


@dataclass(frozen=True)
class EdgeBenchmarkReport:
    budget_id: str
    measurement_digest: str
    violations: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.violations


def evaluate_edge_budget(
    budget: EdgeResourceBudget,
    measurement: EdgeBenchmarkMeasurement,
) -> EdgeBenchmarkReport:
    violations = []
    if measurement.p95_latency_ms > budget.maximum_p95_latency_ms:
        violations.append("p95 latency exceeds budget")
    if measurement.peak_memory_mib > budget.maximum_peak_memory_mib:
        violations.append("peak memory exceeds budget")
    if measurement.average_power_w > budget.maximum_average_power_w:
        violations.append("average power exceeds budget")
    if measurement.throughput_samples_per_s < budget.minimum_throughput_samples_per_s:
        violations.append("throughput is below budget")
    return EdgeBenchmarkReport(budget.budget_id, measurement.digest, tuple(violations))
