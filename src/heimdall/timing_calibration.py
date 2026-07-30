"""Traceable cross-node timing calibration for association inputs."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .association import TimedCandidate
from .domain import EvidenceClass
from .physics_contract import TimeScale


@dataclass(frozen=True)
class TimingCalibrationCertificate:
    certificate_id: str
    node_id: str
    time_scale: TimeScale
    valid_from_ns: int
    valid_until_ns: int
    offset_ns: int
    standard_uncertainty_ns: float
    traceability_reference: str
    evidence_references: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all((self.certificate_id, self.node_id, self.traceability_reference, self.evidence_references)):
            raise ValueError("timing calibration identity and evidence are required")
        if self.valid_until_ns <= self.valid_from_ns or self.standard_uncertainty_ns < 0:
            raise ValueError("timing calibration validity or uncertainty is invalid")

    def applies(self, node_id: str, time_scale: TimeScale, timestamp_ns: int) -> bool:
        return self.node_id == node_id and self.time_scale is time_scale and self.valid_from_ns <= timestamp_ns <= self.valid_until_ns


def calibrate_candidate_time(
    *,
    candidate_id: str,
    observation_id: str,
    node_id: str,
    observed_at_ns: int,
    time_scale: TimeScale,
    reported_time_uncertainty_ns: float,
    score: float,
    evidence_class: EvidenceClass,
    source_payload_digest: str,
    certificate: TimingCalibrationCertificate,
) -> TimedCandidate:
    """Apply an explicit node-clock correction and propagate standard uncertainty."""
    if reported_time_uncertainty_ns < 0:
        raise ValueError("reported time uncertainty must be non-negative")
    if not certificate.applies(node_id, time_scale, observed_at_ns):
        raise ValueError("timing calibration certificate does not apply to candidate")
    return TimedCandidate(
        candidate_id=candidate_id,
        observation_id=observation_id,
        node_id=node_id,
        observed_at_ns=observed_at_ns + certificate.offset_ns,
        time_scale=time_scale,
        time_uncertainty_ns=sqrt(reported_time_uncertainty_ns ** 2 + certificate.standard_uncertainty_ns ** 2),
        score=score,
        evidence_class=evidence_class,
        source_payload_digest=source_payload_digest,
    )
