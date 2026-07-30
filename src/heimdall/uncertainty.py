"""Traceable uncertainty budgets for future Heimdall quantities.

This module combines only independent standard uncertainties. Correlated terms
must be modeled with an explicit covariance method; silently treating them as
independent is prohibited.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import sqrt


class UncertaintyKind(str, Enum):
    CALIBRATION = "calibration"
    TIMING = "timing"
    ENVIRONMENT = "environment"
    MODEL_FORM = "model_form"
    NUMERICAL = "numerical"
    MEASUREMENT_NOISE = "measurement_noise"
    EPHEMERIS = "ephemeris"
    ATTITUDE = "attitude"


@dataclass(frozen=True)
class UncertaintyComponent:
    component_id: str
    kind: UncertaintyKind
    quantity_id: str
    unit: str
    standard_uncertainty: float
    distribution: str
    evidence_reference: str
    correlation_group: str = ""

    def __post_init__(self) -> None:
        if not all((
            self.component_id, self.quantity_id, self.unit,
            self.distribution, self.evidence_reference,
        )):
            raise ValueError("uncertainty component metadata is required")
        if self.standard_uncertainty < 0:
            raise ValueError("standard uncertainty must be non-negative")


@dataclass(frozen=True)
class UncertaintyBudget:
    budget_id: str
    quantity_id: str
    nominal_value: float
    unit: str
    components: tuple[UncertaintyComponent, ...]
    provenance_reference: str

    def __post_init__(self) -> None:
        if not all((self.budget_id, self.quantity_id, self.unit, self.provenance_reference)):
            raise ValueError("budget identity and provenance are required")
        if not self.components:
            raise ValueError("budget requires uncertainty components")
        if any(
            component.quantity_id != self.quantity_id or component.unit != self.unit
            for component in self.components
        ):
            raise ValueError("all components must describe the same quantity and unit")
        groups = [component.correlation_group for component in self.components if component.correlation_group]
        if len(groups) != len(set(groups)):
            raise ValueError("correlated components require an explicit covariance method")

    @property
    def combined_standard_uncertainty(self) -> float:
        return sqrt(sum(component.standard_uncertainty ** 2 for component in self.components))

    def interval(self, coverage_factor: float) -> tuple[float, float]:
        if coverage_factor <= 0:
            raise ValueError("coverage factor must be positive")
        half_width = coverage_factor * self.combined_standard_uncertainty
        return (self.nominal_value - half_width, self.nominal_value + half_width)

