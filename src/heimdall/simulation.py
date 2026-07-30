"""Deterministic synthetic waveform generator.

This is a test fixture and interface exerciser, not a validated plasma-physics or
flight sensor model. Its output is always marked EvidenceClass.SYNTHETIC.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
from math import pi, sin
from random import Random

from .domain import EvidenceClass, ObservationL0, Provenance, waveform_digest
from .forward_models import ForwardModel, IllustrativeBurstSineModel
from .model_registry import ModelRegistry, default_model_registry


@dataclass(frozen=True)
class SyntheticScenario:
    scenario_id: str
    seed: int
    sample_rate_hz: int = 1024
    duration_s: float = 2.0
    signal_frequency_hz: float = 64.0
    signal_amplitude: float = 0.0
    noise_amplitude: float = 0.20
    signal_start_s: float = 0.75
    signal_duration_s: float = 0.25
    interference_frequency_hz: float = 0.0
    interference_amplitude: float = 0.0
    interference_start_s: float = 0.0
    interference_duration_s: float = 0.0
    clock_uncertainty_ns: float = 0.0
    expected_signal: bool = False

    def __post_init__(self) -> None:
        if self.sample_rate_hz <= 0 or self.duration_s <= 0:
            raise ValueError("sample rate and duration must be positive")
        if min(
            self.signal_amplitude, self.noise_amplitude, self.signal_start_s,
            self.signal_duration_s, self.interference_frequency_hz,
            self.interference_amplitude, self.interference_start_s,
            self.interference_duration_s, self.clock_uncertainty_ns,
        ) < 0:
            raise ValueError("scenario values must be non-negative")


def generate_observation(
    scenario: SyntheticScenario,
    model: ForwardModel | None = None,
    model_registry: ModelRegistry | None = None,
) -> ObservationL0:
    model = model or IllustrativeBurstSineModel()
    model_card = (model_registry or default_model_registry()).resolve(
        model.model_id,
        model.model_version,
    )
    rng = Random(scenario.seed)
    count = int(scenario.sample_rate_hz * scenario.duration_s)
    interference_start_index = int(scenario.interference_start_s * scenario.sample_rate_hz)
    interference_end_index = (
        count
        if scenario.interference_duration_s == 0
        else interference_start_index + int(scenario.interference_duration_s * scenario.sample_rate_hz)
    )
    samples = []

    for index in range(count):
        value = rng.uniform(-scenario.noise_amplitude, scenario.noise_amplitude)
        value += model.signal_at(scenario, index)
        if scenario.interference_amplitude and interference_start_index <= index < interference_end_index:
            seconds = index / scenario.sample_rate_hz
            value += scenario.interference_amplitude * sin(
                2 * pi * scenario.interference_frequency_hz * seconds
            )
        samples.append(value)

    configuration = repr({
        "scenario": sorted(asdict(scenario).items()),
        "forward_model": (model.model_id, model.model_version),
        "model_card_digest": model_card.digest,
    }).encode("utf-8")
    config_digest = sha256(configuration).hexdigest()
    provenance = Provenance(
        evidence_class=EvidenceClass.SYNTHETIC,
        scenario_id=scenario.scenario_id,
        generator_version=f"{model.model_id}/{model.model_version}",
        configuration_digest=config_digest,
        model_card_digest=model_card.digest,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    payload = tuple(samples)
    return ObservationL0(
        observation_id=f"l0-{scenario.scenario_id}-{config_digest[:12]}",
        samples=payload,
        sample_rate_hz=scenario.sample_rate_hz,
        started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        sensor_id="synthetic-node-001",
        sequence_number=0,
        clock_uncertainty_ns=scenario.clock_uncertainty_ns,
        calibration_id="synthetic-calibration/0.1.0",
        provenance=provenance,
        payload_digest=waveform_digest(payload),
    )
