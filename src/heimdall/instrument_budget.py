"""Explicit resource-envelope contract for future instrument trades."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InstrumentBudget:
    budget_id: str
    sensor_sample_rate_hz: float
    adc_dynamic_range_db: float
    timing_uncertainty_ns: float
    average_power_w: float
    peak_power_w: float
    mass_kg: float
    downlink_mib_per_day: float
    assumption_references: tuple[str, ...]
    limitation: str

    def __post_init__(self) -> None:
        if not all((self.budget_id, self.assumption_references, self.limitation)):
            raise ValueError("instrument budget identity, assumptions, and limitation are required")
        if min(
            self.sensor_sample_rate_hz, self.adc_dynamic_range_db, self.timing_uncertainty_ns,
            self.average_power_w, self.peak_power_w, self.mass_kg, self.downlink_mib_per_day,
        ) < 0:
            raise ValueError("instrument budget values must be non-negative")
        if self.peak_power_w < self.average_power_w:
            raise ValueError("instrument peak power cannot be below average power")


@dataclass(frozen=True)
class InstrumentBudgetLimit:
    limit_id: str
    maximum_average_power_w: float
    maximum_peak_power_w: float
    maximum_mass_kg: float
    maximum_downlink_mib_per_day: float

    def __post_init__(self) -> None:
        if not self.limit_id or min(self.maximum_average_power_w, self.maximum_peak_power_w, self.maximum_mass_kg, self.maximum_downlink_mib_per_day) <= 0:
            raise ValueError("instrument budget limit is invalid")


def evaluate_instrument_budget(budget: InstrumentBudget, limit: InstrumentBudgetLimit) -> tuple[str, ...]:
    violations = []
    if budget.average_power_w > limit.maximum_average_power_w:
        violations.append("average power exceeds limit")
    if budget.peak_power_w > limit.maximum_peak_power_w:
        violations.append("peak power exceeds limit")
    if budget.mass_kg > limit.maximum_mass_kg:
        violations.append("mass exceeds limit")
    if budget.downlink_mib_per_day > limit.maximum_downlink_mib_per_day:
        violations.append("downlink exceeds limit")
    return tuple(violations)
