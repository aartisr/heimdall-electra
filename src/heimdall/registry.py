"""Versioned synthetic scenarios. Labels are available only for experiment evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .domain import DatasetSplit, EvidenceClass
from .simulation import SyntheticScenario


@dataclass(frozen=True)
class RegisteredScenario:
    scenario: SyntheticScenario
    split: DatasetSplit
    registry_version: str
    stratum: str
    evidence_class: EvidenceClass = EvidenceClass.SYNTHETIC

    @property
    def manifest_digest(self) -> str:
        value = (
            f"{self.registry_version}:{self.split.value}:{self.stratum}:"
            f"{self.evidence_class.value}:{self.scenario!r}"
        ).encode()
        return sha256(value).hexdigest()


def reference_registry() -> tuple[RegisteredScenario, ...]:
    return (
        RegisteredScenario(
            SyntheticScenario("dev-signal-001", seed=11, signal_amplitude=1.0, expected_signal=True),
            DatasetSplit.DEVELOPMENT,
            "synthetic-registry/0.2.0",
            "burst_signal",
        ),
        RegisteredScenario(
            SyntheticScenario("dev-noise-001", seed=12, signal_amplitude=0.0, expected_signal=False),
            DatasetSplit.DEVELOPMENT,
            "synthetic-registry/0.2.0",
            "background_noise",
        ),
        RegisteredScenario(
            SyntheticScenario("locked-signal-001", seed=21, signal_amplitude=0.85, expected_signal=True),
            DatasetSplit.LOCKED_VALIDATION,
            "synthetic-registry/0.2.0",
            "burst_signal",
        ),
        RegisteredScenario(
            SyntheticScenario(
                "locked-interference-001",
                seed=22,
                signal_amplitude=0.0,
                interference_frequency_hz=64.0,
                interference_amplitude=0.75,
                expected_signal=False,
            ),
            DatasetSplit.LOCKED_VALIDATION,
            "synthetic-registry/0.2.0",
            "continuous_tone_interference",
        ),
        RegisteredScenario(
            SyntheticScenario(
                "locked-transient-interference-001",
                seed=23,
                interference_frequency_hz=64.0,
                interference_amplitude=0.75,
                interference_start_s=0.75,
                interference_duration_s=0.25,
                expected_signal=False,
            ),
            DatasetSplit.LOCKED_VALIDATION,
            "synthetic-registry/0.2.0",
            "transient_same_frequency_interference",
        ),
        RegisteredScenario(
            SyntheticScenario(
                "locked-off-target-tone-001",
                seed=24,
                interference_frequency_hz=91.0,
                interference_amplitude=0.75,
                expected_signal=False,
            ),
            DatasetSplit.LOCKED_VALIDATION,
            "synthetic-registry/0.2.0",
            "off_target_tone_interference",
        ),
        RegisteredScenario(
            SyntheticScenario(
                "locked-clock-degraded-signal-001",
                seed=25,
                signal_amplitude=0.85,
                clock_uncertainty_ns=10_000.0,
                expected_signal=True,
            ),
            DatasetSplit.LOCKED_VALIDATION,
            "synthetic-registry/0.2.0",
            "degraded_clock",
        ),
    )
