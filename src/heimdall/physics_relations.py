"""Sealed metamorphic and limiting-case checks for future physics models.

These checks compare model outputs for a predeclared pair of inputs. They are
an additional numerical-verification control, not a substitute for independent
physical validation, calibration, or laboratory evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from math import isclose, isfinite
from typing import Sequence

from .governance import ExperimentLedger, digest_value
from .model_admission import PhysicsModelAdmission, validate_analytic_model_admission
from .model_registry import ModelCard
from .physics_benchmarks import NumericTolerance
from .physics_contract import PhysicsModel, PhysicsModelInput
from .physics_validation import validate_conformance


class RelationKind(str, Enum):
    EQUAL = "equal"
    OPPOSITE = "opposite"
    SCALED = "scaled"


@dataclass(frozen=True)
class MetamorphicPhysicsCase:
    case_id: str
    model_id: str
    model_version: str
    baseline_input: PhysicsModelInput
    transformed_input: PhysicsModelInput
    expected_output_units: str
    relation: RelationKind
    scale_factor: float | None
    tolerance: NumericTolerance
    evidence_references: tuple[str, ...]
    limitation: str

    def __post_init__(self) -> None:
        if not all((self.case_id, self.model_id, self.model_version, self.expected_output_units,
                    self.evidence_references, self.limitation)):
            raise ValueError("relation case metadata and evidence references are required")
        if self.relation is RelationKind.SCALED:
            if self.scale_factor is None or not isfinite(self.scale_factor):
                raise ValueError("scaled relation requires a finite scale factor")
        elif self.scale_factor is not None:
            raise ValueError("only scaled relations may declare a scale factor")

    @property
    def digest(self) -> str:
        return digest_value({
            "case_id": self.case_id, "model_id": self.model_id, "model_version": self.model_version,
            "baseline_input": self.baseline_input, "transformed_input": self.transformed_input,
            "expected_output_units": self.expected_output_units, "relation": self.relation.value,
            "scale_factor": self.scale_factor, "tolerance": self.tolerance,
            "evidence_references": self.evidence_references, "limitation": self.limitation,
        })


@dataclass(frozen=True)
class SealedMetamorphicSuite:
    suite_id: str
    model_id: str
    model_version: str
    cases: tuple[MetamorphicPhysicsCase, ...]
    review_reference: str
    sealed_at: datetime

    def __post_init__(self) -> None:
        if not self.suite_id or not self.review_reference or self.sealed_at.tzinfo is None:
            raise ValueError("sealed relation suite requires identity, review reference, and timezone-aware seal time")
        if not self.cases:
            raise ValueError("sealed relation suite requires at least one case")
        if len({case.case_id for case in self.cases}) != len(self.cases):
            raise ValueError("sealed relation suite case IDs must be unique")
        if {(case.model_id, case.model_version) for case in self.cases} != {(self.model_id, self.model_version)}:
            raise ValueError("sealed relation suite cases must match the suite model identity")

    @property
    def digest(self) -> str:
        return digest_value({
            "suite_id": self.suite_id, "model_id": self.model_id, "model_version": self.model_version,
            "case_digests": tuple(case.digest for case in self.cases),
            "review_reference": self.review_reference, "sealed_at": self.sealed_at.isoformat(),
        })


@dataclass(frozen=True)
class MetamorphicPhysicsResult:
    case_id: str
    conformance_failures: tuple[str, ...]
    relation_failures: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.conformance_failures and not self.relation_failures


@dataclass(frozen=True)
class MetamorphicSuiteExecution:
    suite_id: str
    suite_digest: str
    result_digest: str
    ledger_event_digest: str
    passed: bool


def run_metamorphic_case(
    model: PhysicsModel, card: ModelCard, admission: PhysicsModelAdmission, case: MetamorphicPhysicsCase,
) -> MetamorphicPhysicsResult:
    validate_analytic_model_admission(admission, card)
    if (case.model_id, case.model_version) != (model.model_id, model.model_version):
        raise ValueError("relation case does not match model identity")
    baseline_conformance = validate_conformance(model, card, case.baseline_input)
    transformed_conformance = validate_conformance(model, card, case.transformed_input)
    baseline = model.simulate(case.baseline_input)
    transformed = model.simulate(case.transformed_input)
    failures = []
    if baseline.output_units != case.expected_output_units or transformed.output_units != case.expected_output_units:
        failures.append("output units do not match relation expectation")
    if len(baseline.values) != len(transformed.values):
        failures.append("output value counts do not match")
    else:
        for index, (source, actual) in enumerate(zip(baseline.values, transformed.values)):
            expected = _expected_value(case, source)
            if not isclose(actual, expected, rel_tol=case.tolerance.relative, abs_tol=case.tolerance.absolute):
                failures.append(f"value at index {index} violates declared {case.relation.value} relation")
    return MetamorphicPhysicsResult(
        case_id=case.case_id,
        conformance_failures=baseline_conformance.checks + transformed_conformance.checks,
        relation_failures=tuple(failures),
    )


def execute_sealed_metamorphic_suite(
    model: PhysicsModel, card: ModelCard, admission: PhysicsModelAdmission,
    suite: SealedMetamorphicSuite, ledger: ExperimentLedger,
) -> MetamorphicSuiteExecution:
    if (model.model_id, model.model_version) != (suite.model_id, suite.model_version):
        raise ValueError("sealed relation suite does not match model identity")
    results = tuple(run_metamorphic_case(model, card, admission, case) for case in suite.cases)
    payload = {
        "suite_id": suite.suite_id, "suite_digest": suite.digest, "model_card_digest": card.digest,
        "model_admission_identity": f"{admission.model_id}:{admission.model_version}",
        "passed": all(result.passed for result in results),
        "results": tuple({"case_id": result.case_id, "passed": result.passed,
                          "conformance_failures": result.conformance_failures,
                          "relation_failures": result.relation_failures} for result in results),
    }
    event = ledger.append("metamorphic_physics_suite_executed", payload)
    return MetamorphicSuiteExecution(
        suite_id=suite.suite_id, suite_digest=suite.digest, result_digest=digest_value(payload),
        ledger_event_digest=event.digest, passed=payload["passed"],
    )


def _expected_value(case: MetamorphicPhysicsCase, source: float) -> float:
    if case.relation is RelationKind.EQUAL:
        return source
    if case.relation is RelationKind.OPPOSITE:
        return -source
    assert case.scale_factor is not None
    return case.scale_factor * source
