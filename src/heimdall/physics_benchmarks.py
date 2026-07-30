"""Predeclared numerical benchmarks for admitted analytic physics models.

The harness compares a model against declared expected outputs using explicit
tolerances. Passing establishes reproducible agreement with those benchmark
fixtures only; it does not establish physical correctness or experimental
validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isclose
from typing import Sequence

from .model_admission import PhysicsModelAdmission, validate_analytic_model_admission
from .model_registry import ModelCard
from .physics_contract import PhysicsModel, PhysicsModelInput
from .physics_validation import validate_conformance
from .governance import ExperimentLedger, digest_value


@dataclass(frozen=True)
class NumericTolerance:
    absolute: float
    relative: float

    def __post_init__(self) -> None:
        if self.absolute < 0 or self.relative < 0 or (self.absolute == 0 and self.relative == 0):
            raise ValueError("benchmark tolerance requires a positive absolute or relative bound")


@dataclass(frozen=True)
class PhysicsBenchmarkCase:
    case_id: str
    model_id: str
    model_version: str
    model_input: PhysicsModelInput
    expected_output_units: str
    expected_values: tuple[float, ...]
    tolerance: NumericTolerance
    evidence_references: tuple[str, ...]
    limitation: str

    def __post_init__(self) -> None:
        if not all((
            self.case_id, self.model_id, self.model_version, self.expected_output_units,
            self.evidence_references, self.limitation,
        )):
            raise ValueError("benchmark case metadata and evidence references are required")

    @property
    def digest(self) -> str:
        return digest_value({
            "case_id": self.case_id,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "model_input": self.model_input,
            "expected_output_units": self.expected_output_units,
            "expected_values": self.expected_values,
            "tolerance": self.tolerance,
            "evidence_references": self.evidence_references,
            "limitation": self.limitation,
        })


@dataclass(frozen=True)
class SealedPhysicsBenchmarkSuite:
    suite_id: str
    model_id: str
    model_version: str
    cases: tuple[PhysicsBenchmarkCase, ...]
    review_reference: str
    sealed_at: datetime

    def __post_init__(self) -> None:
        if not self.suite_id or not self.review_reference or self.sealed_at.tzinfo is None:
            raise ValueError("sealed suite requires identity, review reference, and timezone-aware seal time")
        if not self.cases:
            raise ValueError("sealed suite requires at least one case")
        case_ids = [case.case_id for case in self.cases]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("sealed suite case IDs must be unique")
        identities = {(case.model_id, case.model_version) for case in self.cases}
        if identities != {(self.model_id, self.model_version)}:
            raise ValueError("sealed suite cases must match the suite model identity")

    @property
    def digest(self) -> str:
        return digest_value({
            "suite_id": self.suite_id,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "case_digests": tuple(case.digest for case in self.cases),
            "review_reference": self.review_reference,
            "sealed_at": self.sealed_at.isoformat(),
        })


@dataclass(frozen=True)
class PhysicsBenchmarkResult:
    case_id: str
    model_id: str
    model_version: str
    conformance_failures: tuple[str, ...]
    comparison_failures: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.conformance_failures and not self.comparison_failures


@dataclass(frozen=True)
class SealedPhysicsBenchmarkResult:
    suite_id: str
    suite_digest: str
    results: tuple[PhysicsBenchmarkResult, ...]

    @property
    def passed(self) -> bool:
        return all(result.passed for result in self.results)


@dataclass(frozen=True)
class PhysicsBenchmarkExecution:
    suite_id: str
    suite_digest: str
    result_digest: str
    ledger_event_digest: str
    passed: bool


def run_physics_benchmark(
    model: PhysicsModel,
    card: ModelCard,
    admission: PhysicsModelAdmission,
    case: PhysicsBenchmarkCase,
) -> PhysicsBenchmarkResult:
    """Run one sealed case without mutating model, admission, or benchmark state."""
    validate_analytic_model_admission(admission, card)
    if (case.model_id, case.model_version) != (model.model_id, model.model_version):
        raise ValueError("benchmark case does not match model identity")
    conformance = validate_conformance(model, card, case.model_input)
    output = model.simulate(case.model_input)
    failures = []
    if output.output_units != case.expected_output_units:
        failures.append("output units do not match benchmark expectation")
    if len(output.values) != len(case.expected_values):
        failures.append("output value count does not match benchmark expectation")
    else:
        for index, (actual, expected) in enumerate(zip(output.values, case.expected_values)):
            if not isclose(actual, expected, rel_tol=case.tolerance.relative, abs_tol=case.tolerance.absolute):
                failures.append(f"value at index {index} exceeds declared tolerance")
    return PhysicsBenchmarkResult(
        case_id=case.case_id,
        model_id=model.model_id,
        model_version=model.model_version,
        conformance_failures=conformance.checks,
        comparison_failures=tuple(failures),
    )


def run_physics_benchmark_suite(
    model: PhysicsModel,
    card: ModelCard,
    admission: PhysicsModelAdmission,
    cases: Sequence[PhysicsBenchmarkCase],
) -> tuple[PhysicsBenchmarkResult, ...]:
    if not cases:
        raise ValueError("benchmark suite requires at least one predeclared case")
    case_ids = [case.case_id for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("benchmark case IDs must be unique")
    return tuple(run_physics_benchmark(model, card, admission, case) for case in cases)


def run_sealed_physics_benchmark_suite(
    model: PhysicsModel,
    card: ModelCard,
    admission: PhysicsModelAdmission,
    suite: SealedPhysicsBenchmarkSuite,
) -> SealedPhysicsBenchmarkResult:
    """Execute exactly the cases bound into a sealed suite; no run-time selection."""
    if (model.model_id, model.model_version) != (suite.model_id, suite.model_version):
        raise ValueError("sealed suite does not match model identity")
    results = run_physics_benchmark_suite(model, card, admission, suite.cases)
    return SealedPhysicsBenchmarkResult(suite.suite_id, suite.digest, results)


def execute_sealed_physics_benchmark_suite(
    model: PhysicsModel,
    card: ModelCard,
    admission: PhysicsModelAdmission,
    suite: SealedPhysicsBenchmarkSuite,
    ledger: ExperimentLedger,
) -> PhysicsBenchmarkExecution:
    """Execute a sealed suite and record its complete outcome in the research ledger."""
    result = run_sealed_physics_benchmark_suite(model, card, admission, suite)
    payload = {
        "suite_id": result.suite_id,
        "suite_digest": result.suite_digest,
        "model_card_digest": card.digest,
        "model_admission_identity": f"{admission.model_id}:{admission.model_version}",
        "passed": result.passed,
        "results": tuple({
            "case_id": item.case_id,
            "passed": item.passed,
            "conformance_failures": item.conformance_failures,
            "comparison_failures": item.comparison_failures,
        } for item in result.results),
    }
    event = ledger.append("physics_benchmark_suite_executed", payload)
    return PhysicsBenchmarkExecution(
        suite_id=result.suite_id,
        suite_digest=result.suite_digest,
        result_digest=digest_value(payload),
        ledger_event_digest=event.digest,
        passed=result.passed,
    )
