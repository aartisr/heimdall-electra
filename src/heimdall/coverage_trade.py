"""Explicit coverage-trade contract for future constellation models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CoverageDefinition:
    definition_id: str
    target_regime: str
    geography: str
    time_window_seconds: float
    confidence_requirement: str

    def __post_init__(self) -> None:
        if not all((self.definition_id, self.target_regime, self.geography, self.confidence_requirement)) or self.time_window_seconds <= 0:
            raise ValueError("coverage definition is incomplete")


@dataclass(frozen=True)
class ConstellationTradeScenario:
    scenario_id: str
    node_count: int
    duty_cycle_fraction: float
    node_availability_fraction: float
    orbital_assumption_reference: str
    instrument_assumption_reference: str
    coverage_definition: CoverageDefinition

    def __post_init__(self) -> None:
        if not all((self.scenario_id, self.orbital_assumption_reference, self.instrument_assumption_reference)):
            raise ValueError("constellation trade identity and assumptions are required")
        if self.node_count < 1 or not 0 < self.duty_cycle_fraction <= 1 or not 0 < self.node_availability_fraction <= 1:
            raise ValueError("constellation trade node count or availability is invalid")


@dataclass(frozen=True)
class CoverageTradeResult:
    scenario_id: str
    model_id: str
    model_version: str
    coverage_fraction: float
    coverage_uncertainty_fraction: float
    limitation: str

    def __post_init__(self) -> None:
        if not all((self.scenario_id, self.model_id, self.model_version, self.limitation)):
            raise ValueError("coverage result identity and limitation are required")
        if not 0 <= self.coverage_fraction <= 1 or self.coverage_uncertainty_fraction < 0:
            raise ValueError("coverage result values are invalid")


class CoverageModel(Protocol):
    model_id: str
    model_version: str

    def evaluate(self, scenario: ConstellationTradeScenario) -> CoverageTradeResult:
        """Evaluate one explicitly defined trade scenario."""


def validate_coverage_result(result: CoverageTradeResult, scenario: ConstellationTradeScenario, model: CoverageModel) -> None:
    if result.scenario_id != scenario.scenario_id:
        raise ValueError("coverage result does not match trade scenario")
    if (result.model_id, result.model_version) != (model.model_id, model.model_version):
        raise ValueError("coverage result does not match model identity")
