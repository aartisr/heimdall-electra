"""Traceable hardware-in-the-loop test-plan and result contract."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HilTestPlan:
    plan_id: str
    device_id: str
    firmware_digest: str
    calibration_certificate_id: str
    injected_input_artifact_digest: str
    expected_behavior_reference: str
    environmental_condition_reference: str
    safety_review_reference: str

    def __post_init__(self) -> None:
        if not all((
            self.plan_id, self.device_id, self.firmware_digest, self.calibration_certificate_id,
            self.injected_input_artifact_digest, self.expected_behavior_reference,
            self.environmental_condition_reference, self.safety_review_reference,
        )):
            raise ValueError("HIL plan identity, configuration, input, conditions, and review are required")


@dataclass(frozen=True)
class HilTestResult:
    plan_id: str
    device_id: str
    firmware_digest: str
    calibration_certificate_id: str
    raw_output_artifact_digest: str
    measurement_evidence_references: tuple[str, ...]
    passed: bool
    limitation: str

    def __post_init__(self) -> None:
        if not all((
            self.plan_id, self.device_id, self.firmware_digest, self.calibration_certificate_id,
            self.raw_output_artifact_digest, self.measurement_evidence_references, self.limitation,
        )):
            raise ValueError("HIL result identity, raw output, evidence, and limitation are required")


def validate_hil_result(plan: HilTestPlan, result: HilTestResult) -> None:
    if (result.plan_id, result.device_id, result.firmware_digest, result.calibration_certificate_id) != (
        plan.plan_id, plan.device_id, plan.firmware_digest, plan.calibration_certificate_id,
    ):
        raise ValueError("HIL result does not match sealed plan configuration")
