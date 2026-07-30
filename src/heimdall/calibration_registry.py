"""Traceable calibration-certificate admission for future instrument data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from json import loads
from pathlib import Path

from .calibration import calibrate
from .domain import CalibratedObservationL1, ObservationL0


class CalibrationStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class CalibrationCertificate:
    certificate_id: str
    sensor_id: str
    measurand: str
    input_unit: str
    output_unit: str
    scale: float
    standard_uncertainty_fraction: float
    valid_from: datetime
    valid_until: datetime
    traceability_reference: str
    evidence_references: tuple[str, ...]
    status: CalibrationStatus

    def __post_init__(self) -> None:
        if not all((
            self.certificate_id, self.sensor_id, self.measurand, self.input_unit,
            self.output_unit, self.traceability_reference, self.evidence_references,
        )):
            raise ValueError("calibration certificate metadata and evidence are required")
        if self.scale <= 0 or self.standard_uncertainty_fraction < 0:
            raise ValueError("calibration scale and uncertainty are invalid")
        if self.valid_from.tzinfo is None or self.valid_until.tzinfo is None:
            raise ValueError("calibration validity times must be timezone-aware")
        if self.valid_until <= self.valid_from:
            raise ValueError("calibration validity interval is invalid")

    def applies_to(self, observation: ObservationL0) -> bool:
        return (
            self.status is CalibrationStatus.ACTIVE
            and self.sensor_id == observation.sensor_id
            and self.valid_from <= observation.started_at <= self.valid_until
        )


class JsonCalibrationRegistry:
    def __init__(self, path: Path) -> None:
        self.path = path

    def resolve(self, certificate_id: str) -> CalibrationCertificate:
        document = loads(self.path.read_text(encoding="utf-8"))
        matches = [item for item in document.get("certificates", []) if item.get("certificate_id") == certificate_id]
        if len(matches) != 1:
            raise ValueError("calibration registry must contain exactly one matching certificate")
        item = matches[0]
        certificate = CalibrationCertificate(
            certificate_id=str(item["certificate_id"]), sensor_id=str(item["sensor_id"]),
            measurand=str(item["measurand"]), input_unit=str(item["input_unit"]),
            output_unit=str(item["output_unit"]), scale=float(item["scale"]),
            standard_uncertainty_fraction=float(item["standard_uncertainty_fraction"]),
            valid_from=datetime.fromisoformat(str(item["valid_from"]).replace("Z", "+00:00")),
            valid_until=datetime.fromisoformat(str(item["valid_until"]).replace("Z", "+00:00")),
            traceability_reference=str(item["traceability_reference"]),
            evidence_references=tuple(str(value) for value in item["evidence_references"]),
            status=CalibrationStatus(str(item["status"])),
        )
        for reference in (certificate.traceability_reference, *certificate.evidence_references):
            if not (self.path.parents[2] / reference).is_file():
                raise ValueError("calibration certificate reference does not exist")
        return certificate


def calibrate_with_certificate(
    observation: ObservationL0,
    certificate: CalibrationCertificate,
) -> CalibratedObservationL1:
    if certificate.status is not CalibrationStatus.ACTIVE:
        raise ValueError("calibration certificate is not active")
    if certificate.sensor_id != observation.sensor_id:
        raise ValueError("calibration certificate does not match observation sensor")
    if not certificate.valid_from <= observation.started_at <= certificate.valid_until:
        raise ValueError("observation time is outside calibration certificate validity")
    return calibrate(
        observation,
        scale=certificate.scale,
        uncertainty_fraction=certificate.standard_uncertainty_fraction,
        calibration_id=certificate.certificate_id,
        additional_quality_flags=("certificate_traceable",),
    )
