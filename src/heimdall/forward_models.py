"""Plug-in forward models for synthetic research scenarios.

The included models are fixtures, not plasma-physics validation. A future
analytic, reduced-order, or PIC model must expose its ID/version and be
validated through a separate model card before it can generate research data.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sin
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .simulation import SyntheticScenario


class ForwardModel(Protocol):
    model_id: str
    model_version: str

    def signal_at(self, scenario: "SyntheticScenario", sample_index: int) -> float:
        """Return one synthetic signal value without adding noise or interference."""


@dataclass(frozen=True)
class NullSignalModel:
    model_id: str = "null-signal-model"
    model_version: str = "0.1.0"

    def signal_at(self, scenario: "SyntheticScenario", sample_index: int) -> float:
        return 0.0


@dataclass(frozen=True)
class IllustrativeBurstSineModel:
    """Legacy illustrative burst fixture retained for regression tests.

    It has no plasma-wave, charging, geomagnetic, material, or sensor-physics
    validity claim. Its only purpose is to exercise pipeline interfaces.
    """

    model_id: str = "illustrative-burst-sine"
    model_version: str = "0.1.0"

    def signal_at(self, scenario: "SyntheticScenario", sample_index: int) -> float:
        start = int(scenario.signal_start_s * scenario.sample_rate_hz)
        end = start + int(scenario.signal_duration_s * scenario.sample_rate_hz)
        if not start <= sample_index < end:
            return 0.0
        seconds = sample_index / scenario.sample_rate_hz
        return scenario.signal_amplitude * sin(2 * pi * scenario.signal_frequency_hz * seconds)

