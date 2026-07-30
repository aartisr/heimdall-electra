"""Sealed cross-implementation comparison for future analytic physics models.

Agreement is recorded as reviewable numerical evidence. It cannot establish
that two implementations are actually independent or that their shared model
is physically correct; those conclusions require the declared review evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isclose
from typing import Sequence

from .governance import ExperimentLedger, digest_value
from .model_admission import PhysicsModelAdmission, validate_analytic_model_admission
from .model_registry import ModelCard
from .physics_benchmarks import NumericTolerance
from .physics_contract import PhysicsModel, PhysicsModelInput
from .physics_validation import validate_conformance


@dataclass(frozen=True)
class ModelComparisonCase:
    case_id: str
    model_input: PhysicsModelInput
    expected_output_units: str
    tolerance: NumericTolerance
    evidence_references: tuple[str, ...]
    limitation: str

    def __post_init__(self) -> None:
        if not all((self.case_id, self.expected_output_units, self.evidence_references, self.limitation)):
            raise ValueError("comparison case metadata and evidence references are required")

    @property
    def digest(self) -> str:
        return digest_value({
            "case_id": self.case_id, "model_input": self.model_input,
            "expected_output_units": self.expected_output_units, "tolerance": self.tolerance,
            "evidence_references": self.evidence_references, "limitation": self.limitation,
        })


@dataclass(frozen=True)
class SealedModelComparisonSuite:
    suite_id: str
    primary_model_id: str
    primary_model_version: str
    primary_implementation_digest: str
    reference_model_id: str
    reference_model_version: str
    reference_implementation_digest: str
    cases: tuple[ModelComparisonCase, ...]
    independence_review_reference: str
    sealed_at: datetime
    limitation: str

    def __post_init__(self) -> None:
        if not all((
            self.suite_id, self.primary_model_id, self.primary_model_version, self.primary_implementation_digest,
            self.reference_model_id, self.reference_model_version, self.reference_implementation_digest,
            self.independence_review_reference, self.limitation,
        )) or self.sealed_at.tzinfo is None:
            raise ValueError("comparison suite identity, digests, review, limitation, and seal time are required")
        if not self.cases:
            raise ValueError("comparison suite requires at least one case")
        if len({case.case_id for case in self.cases}) != len(self.cases):
            raise ValueError("comparison suite case IDs must be unique")
        if (self.primary_model_id, self.primary_model_version) == (self.reference_model_id, self.reference_model_version):
            raise ValueError("comparison suite requires distinct primary and reference model identities")

    @property
    def digest(self) -> str:
        return digest_value({
            "suite_id": self.suite_id,
            "primary": (self.primary_model_id, self.primary_model_version, self.primary_implementation_digest),
            "reference": (self.reference_model_id, self.reference_model_version, self.reference_implementation_digest),
            "case_digests": tuple(case.digest for case in self.cases),
            "independence_review_reference": self.independence_review_reference,
            "sealed_at": self.sealed_at.isoformat(), "limitation": self.limitation,
        })


@dataclass(frozen=True)
class ModelComparisonResult:
    case_id: str
    conformance_failures: tuple[str, ...]
    comparison_failures: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.conformance_failures and not self.comparison_failures


@dataclass(frozen=True)
class ModelComparisonExecution:
    suite_id: str
    suite_digest: str
    result_digest: str
    ledger_event_digest: str
    passed: bool


def execute_sealed_model_comparison(
    primary: PhysicsModel, primary_card: ModelCard, primary_admission: PhysicsModelAdmission,
    reference: PhysicsModel, reference_card: ModelCard, reference_admission: PhysicsModelAdmission,
    suite: SealedModelComparisonSuite, ledger: ExperimentLedger,
) -> ModelComparisonExecution:
    _validate_model_identity(primary, suite.primary_model_id, suite.primary_model_version, "primary")
    _validate_model_identity(reference, suite.reference_model_id, suite.reference_model_version, "reference")
    validate_analytic_model_admission(primary_admission, primary_card)
    validate_analytic_model_admission(reference_admission, reference_card)
    results = tuple(_compare_case(primary, primary_card, reference, reference_card, case) for case in suite.cases)
    payload = {
        "suite_id": suite.suite_id, "suite_digest": suite.digest,
        "primary_model_card_digest": primary_card.digest, "reference_model_card_digest": reference_card.digest,
        "primary_admission_identity": f"{primary_admission.model_id}:{primary_admission.model_version}",
        "reference_admission_identity": f"{reference_admission.model_id}:{reference_admission.model_version}",
        "passed": all(result.passed for result in results),
        "results": tuple({"case_id": result.case_id, "passed": result.passed,
                          "conformance_failures": result.conformance_failures,
                          "comparison_failures": result.comparison_failures} for result in results),
    }
    event = ledger.append("physics_model_comparison_executed", payload)
    return ModelComparisonExecution(suite.suite_id, suite.digest, digest_value(payload), event.digest, payload["passed"])


def _compare_case(
    primary: PhysicsModel, primary_card: ModelCard, reference: PhysicsModel, reference_card: ModelCard,
    case: ModelComparisonCase,
) -> ModelComparisonResult:
    primary_conformance = validate_conformance(primary, primary_card, case.model_input)
    reference_conformance = validate_conformance(reference, reference_card, case.model_input)
    primary_output, reference_output = primary.simulate(case.model_input), reference.simulate(case.model_input)
    failures = []
    if primary_output.output_units != case.expected_output_units or reference_output.output_units != case.expected_output_units:
        failures.append("output units do not match comparison expectation")
    if len(primary_output.values) != len(reference_output.values):
        failures.append("output value counts do not match")
    else:
        for index, (actual, expected) in enumerate(zip(primary_output.values, reference_output.values)):
            if not isclose(actual, expected, rel_tol=case.tolerance.relative, abs_tol=case.tolerance.absolute):
                failures.append(f"value at index {index} differs beyond declared tolerance")
    return ModelComparisonResult(case.case_id, primary_conformance.checks + reference_conformance.checks, tuple(failures))


def _validate_model_identity(model: PhysicsModel, model_id: str, model_version: str, role: str) -> None:
    if (model.model_id, model.model_version) != (model_id, model_version):
        raise ValueError(f"{role} model does not match sealed comparison suite")
