"""Sealed convergence-study contracts for future numerical forward models.

This solver-neutral module makes numerical-refinement evidence reviewable. It
does not implement plasma physics. Passing is numerical evidence for the named
quantity only, never physical validation or a debris-detection claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from typing import Sequence

from .governance import digest_value


@dataclass(frozen=True)
class ConvergenceStudyPlan:
    """An exact, predeclared discretization-refinement study."""

    study_id: str
    model_id: str
    model_version: str
    implementation_digest: str
    environment_digest: str
    input_digest: str
    quantity_id: str
    quantity_unit: str
    resolution_scales: tuple[float, ...]
    finest_relative_change_limit: float
    review_reference: str
    limitation: str

    def __post_init__(self) -> None:
        if not all((
            self.study_id, self.model_id, self.model_version,
            self.implementation_digest, self.environment_digest, self.input_digest,
            self.quantity_id, self.quantity_unit, self.review_reference, self.limitation,
        )):
            raise ValueError("convergence study identity, bindings, and review metadata are required")
        if len(self.resolution_scales) < 3:
            raise ValueError("convergence study requires at least three refinement levels")
        if not all(isfinite(scale) and scale > 0 for scale in self.resolution_scales):
            raise ValueError("resolution scales must be finite and positive")
        if any(later >= earlier for earlier, later in zip(self.resolution_scales, self.resolution_scales[1:])):
            raise ValueError("resolution scales must be strictly decreasing from coarse to fine")
        if not isfinite(self.finest_relative_change_limit) or not 0 < self.finest_relative_change_limit < 1:
            raise ValueError("finest relative-change limit must be finite and between zero and one")

    @property
    def digest(self) -> str:
        return digest_value({
            "study_id": self.study_id, "model_id": self.model_id, "model_version": self.model_version,
            "implementation_digest": self.implementation_digest, "environment_digest": self.environment_digest,
            "input_digest": self.input_digest, "quantity_id": self.quantity_id, "quantity_unit": self.quantity_unit,
            "resolution_scales": self.resolution_scales,
            "finest_relative_change_limit": self.finest_relative_change_limit,
            "review_reference": self.review_reference, "limitation": self.limitation,
        })


@dataclass(frozen=True)
class ConvergenceRun:
    """One non-mutating result from a plan-bound resolution level."""

    study_id: str
    model_id: str
    model_version: str
    implementation_digest: str
    environment_digest: str
    input_digest: str
    resolution_scale: float
    quantity_value: float
    output_artifact_digest: str
    measurement_reference: str

    def __post_init__(self) -> None:
        if not all((
            self.study_id, self.model_id, self.model_version,
            self.implementation_digest, self.environment_digest, self.input_digest,
            self.output_artifact_digest, self.measurement_reference,
        )):
            raise ValueError("convergence run identity and evidence references are required")
        if not isfinite(self.resolution_scale) or self.resolution_scale <= 0:
            raise ValueError("run resolution scale must be finite and positive")
        if not isfinite(self.quantity_value):
            raise ValueError("run quantity value must be finite")


@dataclass(frozen=True)
class ConvergenceAssessment:
    study_id: str
    study_digest: str
    finest_relative_change: float
    observed_order: float | None
    checks: tuple[str, ...]
    limitation: str

    @property
    def passed(self) -> bool:
        return not self.checks


def assess_convergence(plan: ConvergenceStudyPlan, runs: Sequence[ConvergenceRun]) -> ConvergenceAssessment:
    """Assess exact plan-bound runs without repairing or discarding failures."""
    checks: list[str] = []
    if len(runs) != len(plan.resolution_scales):
        checks.append("run count does not match sealed refinement plan")
    expected_binding = (
        plan.study_id, plan.model_id, plan.model_version, plan.implementation_digest,
        plan.environment_digest, plan.input_digest,
    )
    if any((run.study_id, run.model_id, run.model_version, run.implementation_digest,
            run.environment_digest, run.input_digest) != expected_binding for run in runs):
        checks.append("run configuration does not match sealed study plan")
    if tuple(run.resolution_scale for run in runs) != plan.resolution_scales:
        checks.append("run resolution scales do not match sealed refinement plan")

    finest_relative_change = float("inf")
    observed_order: float | None = None
    if len(runs) >= 2:
        coarse, fine = runs[-2:]
        denominator = max(abs(fine.quantity_value), abs(coarse.quantity_value), 1e-30)
        finest_relative_change = abs(fine.quantity_value - coarse.quantity_value) / denominator
        if finest_relative_change > plan.finest_relative_change_limit:
            checks.append("finest refinement relative change exceeds sealed limit")
    if len(runs) >= 3:
        coarse, medium, fine = runs[-3:]
        first_difference = abs(coarse.quantity_value - medium.quantity_value)
        second_difference = abs(medium.quantity_value - fine.quantity_value)
        first_ratio = coarse.resolution_scale / medium.resolution_scale
        second_ratio = medium.resolution_scale / fine.resolution_scale
        if first_difference > 0 and second_difference > 0 and abs(first_ratio - second_ratio) <= 1e-12:
            observed_order = log(first_difference / second_difference) / log(first_ratio)

    return ConvergenceAssessment(
        study_id=plan.study_id, study_digest=plan.digest,
        finest_relative_change=finest_relative_change, observed_order=observed_order,
        checks=tuple(checks),
        limitation=("Numerical refinement evidence only; it does not establish governing-equation "
                    "correctness, physical validity, calibration, or debris detection."),
    )
