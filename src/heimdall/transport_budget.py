"""Explicit store-and-forward transport budget for evidence preservation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransportScenario:
    scenario_id: str
    contact_capacity_mib_per_day: float
    protocol_overhead_fraction: float
    expected_loss_fraction: float
    health_mib_per_day: float
    candidate_context_mib_per_day: float
    background_mib_per_day: float
    forensic_burst_mib_per_day: float
    assumption_references: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.scenario_id or not self.assumption_references:
            raise ValueError("transport scenario identity and assumptions are required")
        if self.contact_capacity_mib_per_day < 0 or min(
            self.protocol_overhead_fraction, self.expected_loss_fraction
        ) < 0 or max(self.protocol_overhead_fraction, self.expected_loss_fraction) >= 1:
            raise ValueError("transport capacity or fractions are invalid")
        if min(self.health_mib_per_day, self.candidate_context_mib_per_day, self.background_mib_per_day, self.forensic_burst_mib_per_day) < 0:
            raise ValueError("transport data volumes must be non-negative")

    @property
    def requested_mib_per_day(self) -> float:
        return self.health_mib_per_day + self.candidate_context_mib_per_day + self.background_mib_per_day + self.forensic_burst_mib_per_day

    @property
    def usable_capacity_mib_per_day(self) -> float:
        return self.contact_capacity_mib_per_day * (1 - self.protocol_overhead_fraction) * (1 - self.expected_loss_fraction)


@dataclass(frozen=True)
class TransportBudgetReport:
    scenario_id: str
    requested_mib_per_day: float
    usable_capacity_mib_per_day: float
    shortfall_mib_per_day: float
    limitation: str

    @property
    def feasible(self) -> bool:
        return self.shortfall_mib_per_day == 0


def evaluate_transport_budget(scenario: TransportScenario) -> TransportBudgetReport:
    return TransportBudgetReport(
        scenario.scenario_id, scenario.requested_mib_per_day, scenario.usable_capacity_mib_per_day,
        max(0.0, scenario.requested_mib_per_day - scenario.usable_capacity_mib_per_day),
        "Budget arithmetic only; not a contact, RF, FEC, encryption, or operational-link validation.",
    )
