"""Development-only synthetic parameter sweeps.

A sweep explores stated fixture sensitivity. It is not a physical validation,
confidence interval, or flight-performance study and may not consume locked
validation scenarios.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from itertools import product
from statistics import fmean
from typing import Sequence

from .domain import DatasetSplit
from .forward_models import ForwardModel
from .pipeline import BaselineMatchedFilter, CandidateGate, detect
from .simulation import SyntheticScenario, generate_observation


@dataclass(frozen=True)
class SweepAxis:
    field_name: str
    values: tuple[float | int, ...]

    def __post_init__(self) -> None:
        allowed = set(SyntheticScenario.__dataclass_fields__) - {"scenario_id", "expected_signal"}
        if self.field_name not in allowed:
            raise ValueError("sweep axis is not a permitted scenario field")
        if not self.values:
            raise ValueError("sweep axis must contain values")


@dataclass(frozen=True)
class SweepDefinition:
    sweep_id: str
    base_scenario: SyntheticScenario
    axes: tuple[SweepAxis, ...]
    dataset_split: DatasetSplit
    purpose: str

    def __post_init__(self) -> None:
        if not self.sweep_id or not self.purpose:
            raise ValueError("sweep ID and purpose are required")
        if self.dataset_split is not DatasetSplit.DEVELOPMENT:
            raise ValueError("parameter sweeps are development-only; locked validation is prohibited")
        names = [axis.field_name for axis in self.axes]
        if len(names) != len(set(names)):
            raise ValueError("sweep axes must use unique scenario fields")


@dataclass(frozen=True)
class SweepResult:
    scenario_id: str
    parameters: dict[str, float | int]
    model_id: str
    model_version: str
    score: float
    detected: bool
    gates_passed: bool


@dataclass(frozen=True)
class SweepReport:
    sweep_id: str
    result_count: int
    score_min: float
    score_max: float
    score_mean: float
    accepted_count: int
    results: tuple[SweepResult, ...]


def expand(definition: SweepDefinition) -> tuple[SyntheticScenario, ...]:
    if not definition.axes:
        return (definition.base_scenario,)
    scenarios = []
    for index, values in enumerate(product(*(axis.values for axis in definition.axes))):
        updates = {axis.field_name: value for axis, value in zip(definition.axes, values)}
        scenario_id = f"{definition.base_scenario.scenario_id}:{definition.sweep_id}:{index:04d}"
        scenarios.append(replace(definition.base_scenario, scenario_id=scenario_id, **updates))
    return tuple(scenarios)


def run_sweep(
    definition: SweepDefinition,
    detector: BaselineMatchedFilter,
    gates: Sequence[CandidateGate],
    model: ForwardModel,
) -> SweepReport:
    results = []
    for scenario in expand(definition):
        observation = generate_observation(scenario, model)
        candidate = detect(observation, detector, gates=gates)
        parameters = {
            axis.field_name: getattr(scenario, axis.field_name)
            for axis in definition.axes
        }
        results.append(SweepResult(
            scenario_id=scenario.scenario_id,
            parameters=parameters,
            model_id=model.model_id,
            model_version=model.model_version,
            score=candidate.score,
            detected=candidate.detected,
            gates_passed=candidate.gates_passed,
        ))
    scores = [result.score for result in results]
    return SweepReport(
        sweep_id=definition.sweep_id,
        result_count=len(results),
        score_min=min(scores),
        score_max=max(scores),
        score_mean=fmean(scores),
        accepted_count=sum(result.detected for result in results),
        results=tuple(results),
    )

