"""Solver-neutral TDOA inference contract for associated multi-node candidates.

This establishes typed inputs and outputs for future localization solvers. No
localization algorithm, object identity, or track estimator is implemented.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from .association import CandidateAssociation, TimedCandidate
from .covariance import validate_covariance_3x3
from .physics_contract import CoordinateFrame, TimeScale


Vector3 = tuple[float, float, float]


@dataclass(frozen=True)
class NodeGeometry:
    node_id: str
    position_m: Vector3
    position_uncertainty_m: float
    frame: CoordinateFrame

    def __post_init__(self) -> None:
        if not self.node_id or self.position_uncertainty_m < 0:
            raise ValueError("node geometry identity or uncertainty is invalid")


@dataclass(frozen=True)
class TdoaInferenceInput:
    association: CandidateAssociation
    candidates: tuple[TimedCandidate, ...]
    node_geometry: tuple[NodeGeometry, ...]
    frame: CoordinateFrame
    time_scale: TimeScale
    model_assumption_reference: str

    def __post_init__(self) -> None:
        if not self.model_assumption_reference:
            raise ValueError("TDOA inference requires model assumptions")
        candidate_ids = tuple(sorted(candidate.candidate_id for candidate in self.candidates))
        if candidate_ids != self.association.candidate_ids:
            raise ValueError("inference candidates do not match association lineage")
        if self.association.time_scale is not self.time_scale or any(candidate.time_scale is not self.time_scale for candidate in self.candidates):
            raise ValueError("inference time scale does not match association")
        geometry = {item.node_id: item for item in self.node_geometry}
        if len(geometry) != len(self.node_geometry) or set(self.association.node_ids) != set(geometry):
            raise ValueError("node geometry must map exactly to association nodes")
        if any(item.frame is not self.frame for item in self.node_geometry):
            raise ValueError("node geometry frame does not match inference frame")


@dataclass(frozen=True)
class TdoaMode:
    mode_id: str
    position_m: Vector3
    residual_ns: float
    covariance_m2: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.mode_id or self.residual_ns < 0:
            raise ValueError("TDOA mode identity, residual, or covariance is invalid")
        validate_covariance_3x3(self.covariance_m2)


@dataclass(frozen=True)
class TdoaInferenceResult:
    association_id: str
    solver_id: str
    solver_version: str
    input_assumption_reference: str
    modes: tuple[TdoaMode, ...]
    limitation: str

    def __post_init__(self) -> None:
        if not all((self.association_id, self.solver_id, self.solver_version, self.input_assumption_reference, self.modes, self.limitation)):
            raise ValueError("TDOA result identity, modes, and limitation are required")


class TdoaSolver(Protocol):
    solver_id: str
    solver_version: str

    def infer(self, inference_input: TdoaInferenceInput) -> TdoaInferenceResult:
        """Return all plausible modes; do not silently collapse ambiguity."""


def validate_tdoa_result(result: TdoaInferenceResult, inference_input: TdoaInferenceInput, solver: TdoaSolver) -> None:
    if result.association_id != inference_input.association.association_id:
        raise ValueError("TDOA result does not match association")
    if (result.solver_id, result.solver_version) != (solver.solver_id, solver.solver_version):
        raise ValueError("TDOA result does not match solver identity")
    if result.input_assumption_reference != inference_input.model_assumption_reference:
        raise ValueError("TDOA result does not preserve assumption lineage")
    if len({mode.mode_id for mode in result.modes}) != len(result.modes):
        raise ValueError("TDOA result modes must be unique")
