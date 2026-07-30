"""Immutable domain contracts for the first Heimdall research vertical slice."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Mapping, Sequence


class EvidenceClass(str, Enum):
    SYNTHETIC = "synthetic"
    LABORATORY = "laboratory"
    OBSERVED = "observed"
    EXTERNAL_CONTEXT = "external_context"


class DatasetSplit(str, Enum):
    DEVELOPMENT = "development"
    LOCKED_VALIDATION = "locked_validation"


@dataclass(frozen=True)
class Provenance:
    evidence_class: EvidenceClass
    scenario_id: str
    generator_version: str
    configuration_digest: str
    model_card_digest: str
    created_at: datetime
    source_artifact_digest: str = ""
    source_manifest_digest: str = ""

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        if not self.scenario_id:
            raise ValueError("scenario_id is required")
        if not self.configuration_digest or not self.model_card_digest:
            raise ValueError("configuration_digest and model_card_digest are required")
        if self.evidence_class is EvidenceClass.OBSERVED and not all((
            self.source_artifact_digest, self.source_manifest_digest,
        )):
            raise ValueError("observed provenance requires raw artifact and acquisition manifest lineage")


@dataclass(frozen=True)
class ObservationL0:
    observation_id: str
    samples: tuple[float, ...]
    sample_rate_hz: int
    started_at: datetime
    sensor_id: str
    sequence_number: int
    clock_uncertainty_ns: float
    calibration_id: str
    provenance: Provenance
    payload_digest: str

    def __post_init__(self) -> None:
        if not self.observation_id or not self.sensor_id:
            raise ValueError("observation_id and sensor_id are required")
        if self.sample_rate_hz <= 0 or not self.samples:
            raise ValueError("samples and positive sample_rate_hz are required")
        if self.started_at.tzinfo is None:
            raise ValueError("started_at must be timezone-aware")
        if self.sequence_number < 0 or self.clock_uncertainty_ns < 0:
            raise ValueError("sequence_number and clock uncertainty must be non-negative")
        expected = waveform_digest(self.samples)
        if self.payload_digest != expected:
            raise ValueError("payload_digest does not match samples")


@dataclass(frozen=True)
class CandidateL2:
    candidate_id: str
    observation_id: str
    detector_id: str
    detector_version: str
    threshold_policy_id: str
    score: float
    threshold: float
    detected: bool
    evidence_class: EvidenceClass
    explanation: Mapping[str, float]
    source_payload_digest: str
    gates_passed: bool = True
    decision_reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not all((self.candidate_id, self.observation_id, self.detector_id, self.detector_version)):
            raise ValueError("candidate identifiers are required")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be normalized to [0, 1]")
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("threshold must be normalized to [0, 1]")
        if self.detected != (self.score >= self.threshold and self.gates_passed):
            raise ValueError("detected must agree with score, threshold, and gate decision")
        if not self.gates_passed and not self.decision_reasons:
            raise ValueError("a rejected candidate must explain the gate decision")


@dataclass(frozen=True)
class CalibratedObservationL1:
    observation_id: str
    parent_payload_digest: str
    samples: tuple[float, ...]
    sample_rate_hz: int
    clock_uncertainty_ns: float
    calibration_id: str
    calibration_scale: float
    calibration_uncertainty_fraction: float
    quality_flags: tuple[str, ...]
    provenance: Provenance

    def __post_init__(self) -> None:
        if not self.observation_id or not self.parent_payload_digest or not self.calibration_id:
            raise ValueError("L1 identifiers are required")
        if not self.samples or self.sample_rate_hz <= 0:
            raise ValueError("L1 requires samples and positive sample rate")
        if (
            self.calibration_scale <= 0
            or self.calibration_uncertainty_fraction < 0
            or self.clock_uncertainty_ns < 0
        ):
            raise ValueError("calibration values are invalid")


def waveform_digest(samples: Sequence[float]) -> str:
    canonical = ",".join(f"{sample:.12g}" for sample in samples).encode("utf-8")
    return sha256(canonical).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
