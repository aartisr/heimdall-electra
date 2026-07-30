"""Unit-, frame-, and time-aware contract for future physics models.

No physical solver is implemented here. The contract exists so future analytic,
reduced-order, or PIC implementations cannot silently accept ambiguous units,
coordinate frames, timestamps, or environmental assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol


Vector3 = tuple[float, float, float]


class CoordinateFrame(str, Enum):
    ECI_J2000 = "eci_j2000"
    ECEF_ITRF = "ecef_itrf"
    LOCAL_MAGNETIC = "local_magnetic"


class TimeScale(str, Enum):
    UTC = "utc"
    TAI = "tai"
    GPS = "gps"


@dataclass(frozen=True)
class OrbitalState:
    reference_time: datetime
    time_scale: TimeScale
    frame: CoordinateFrame
    position_m: Vector3
    velocity_m_per_s: Vector3
    state_uncertainty_m: float

    def __post_init__(self) -> None:
        if self.reference_time.tzinfo is None:
            raise ValueError("reference time must be timezone-aware")
        if self.state_uncertainty_m < 0:
            raise ValueError("state uncertainty must be non-negative")


@dataclass(frozen=True)
class PlasmaEnvironment:
    electron_density_per_m3: float
    ion_density_per_m3: float
    electron_temperature_k: float
    ion_temperature_k: float
    magnetic_field_t: Vector3
    environment_source_reference: str

    def __post_init__(self) -> None:
        values = (
            self.electron_density_per_m3,
            self.ion_density_per_m3,
            self.electron_temperature_k,
            self.ion_temperature_k,
        )
        if any(value <= 0 for value in values):
            raise ValueError("plasma densities and temperatures must be positive")
        if not self.environment_source_reference:
            raise ValueError("environment source reference is required")


@dataclass(frozen=True)
class TargetAssumptions:
    target_id: str
    characteristic_length_m: float
    net_charge_c: float
    material_assumption: str
    shape_assumption: str

    def __post_init__(self) -> None:
        if not self.target_id or not self.material_assumption or not self.shape_assumption:
            raise ValueError("target assumptions require declared identity, material, and shape")
        if self.characteristic_length_m <= 0:
            raise ValueError("characteristic length must be positive")


@dataclass(frozen=True)
class PhysicsModelInput:
    scenario_id: str
    state: OrbitalState
    plasma: PlasmaEnvironment
    target: TargetAssumptions
    validity_assumption_reference: str

    def __post_init__(self) -> None:
        if not self.scenario_id or not self.validity_assumption_reference:
            raise ValueError("physics input requires scenario and validity assumptions")


@dataclass(frozen=True)
class PhysicsModelOutput:
    model_id: str
    model_version: str
    input_scenario_id: str
    validity_statement: str
    output_units: str
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if not all((
            self.model_id, self.model_version, self.input_scenario_id,
            self.validity_statement, self.output_units,
        )):
            raise ValueError("physics output requires complete model and validity metadata")


class PhysicsModel(Protocol):
    model_id: str
    model_version: str

    def simulate(self, model_input: PhysicsModelInput) -> PhysicsModelOutput:
        """Produce a unit-declared result under the model's documented validity envelope."""

