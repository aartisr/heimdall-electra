"""Conformance checks for future physics-model implementations.

Passing these checks establishes software contract conformance only. It does not
validate the physics, calibrate the model, or authorize any operational claim.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Sequence

from .model_registry import ModelCard
from .physics_contract import PhysicsModel, PhysicsModelInput, PhysicsModelOutput


@dataclass(frozen=True)
class PhysicsModelConformanceReport:
    model_id: str
    model_version: str
    model_card_digest: str
    input_scenario_id: str
    checks: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.checks


def validate_conformance(
    model: PhysicsModel,
    model_card: ModelCard,
    model_input: PhysicsModelInput,
) -> PhysicsModelConformanceReport:
    failures = []
    if (model.model_id, model.model_version) != (model_card.model_id, model_card.model_version):
        failures.append("model identity does not match model card")

    first = model.simulate(model_input)
    second = model.simulate(model_input)
    if first != second:
        failures.append("model is not deterministic for identical input")
    if first.model_id != model.model_id or first.model_version != model.model_version:
        failures.append("output identity does not match model")
    if first.input_scenario_id != model_input.scenario_id:
        failures.append("output scenario lineage does not match input")
    if not first.output_units.strip():
        failures.append("output units are empty")
    if not first.validity_statement.strip():
        failures.append("output validity statement is empty")
    if not all(isfinite(value) for value in first.values):
        failures.append("output contains non-finite values")

    return PhysicsModelConformanceReport(
        model_id=model.model_id,
        model_version=model.model_version,
        model_card_digest=model_card.digest,
        input_scenario_id=model_input.scenario_id,
        checks=tuple(failures),
    )

