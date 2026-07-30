"""Non-destructive L0 to L1 calibration contract for the research reference."""

from __future__ import annotations

from .domain import CalibratedObservationL1, ObservationL0


def calibrate(
    observation: ObservationL0,
    *,
    scale: float = 1.0,
    uncertainty_fraction: float = 0.02,
    calibration_id: str | None = None,
    additional_quality_flags: tuple[str, ...] = (),
) -> CalibratedObservationL1:
    if scale <= 0 or uncertainty_fraction < 0:
        raise ValueError("calibration scale must be positive and uncertainty non-negative")
    flags = (("synthetic_input",) if observation.provenance.evidence_class.value == "synthetic" else ()) + additional_quality_flags
    return CalibratedObservationL1(
        observation_id=observation.observation_id,
        parent_payload_digest=observation.payload_digest,
        samples=tuple(sample * scale for sample in observation.samples),
        sample_rate_hz=observation.sample_rate_hz,
        clock_uncertainty_ns=observation.clock_uncertainty_ns,
        calibration_id=calibration_id or f"{observation.calibration_id}:l1-reference",
        calibration_scale=scale,
        calibration_uncertainty_fraction=uncertainty_fraction,
        quality_flags=flags,
        provenance=observation.provenance,
    )
