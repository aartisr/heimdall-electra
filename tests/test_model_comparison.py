from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.governance import JsonlExperimentLedger
from heimdall.model_admission import AdmissionStatus, PhysicsModelAdmission
from heimdall.model_comparison import ModelComparisonCase, SealedModelComparisonSuite, execute_sealed_model_comparison
from heimdall.model_registry import ModelCard, ModelValidityTier
from heimdall.physics_benchmarks import NumericTolerance
from heimdall.physics_contract import CoordinateFrame, OrbitalState, PhysicsModelInput, PhysicsModelOutput, PlasmaEnvironment, TargetAssumptions, TimeScale


class PrimaryFixture:
    model_id, model_version = "primary", "1.0.0"

    def simulate(self, item: PhysicsModelInput) -> PhysicsModelOutput:
        return PhysicsModelOutput(self.model_id, self.model_version, item.scenario_id, "fixture", "V/m", (1.0, 2.0))


class ReferenceFixture(PrimaryFixture):
    model_id, model_version = "reference", "2.0.0"


class DivergentReference(ReferenceFixture):
    def simulate(self, item: PhysicsModelInput) -> PhysicsModelOutput:
        return PhysicsModelOutput(self.model_id, self.model_version, item.scenario_id, "fixture", "V/m", (1.0, 3.0))


def input_case() -> PhysicsModelInput:
    return PhysicsModelInput(
        "comparison-case", OrbitalState(datetime(2026, 1, 1, tzinfo=timezone.utc), TimeScale.UTC,
        CoordinateFrame.ECI_J2000, (1, 2, 3), (4, 5, 6), 0.1),
        PlasmaEnvironment(1e10, 1e10, 1000, 1000, (1e-5, 0.0, 0.0), "fixture"),
        TargetAssumptions("target", 0.01, 0.0, "fixture", "sphere"), "fixture",
    )


def admission(model_id: str, version: str) -> PhysicsModelAdmission:
    return PhysicsModelAdmission(model_id, version, AdmissionStatus.APPROVED, "owner", "hypothesis", ("equation",), "input", "output", "numerics", ("verification",), "review", "fixture")


def card(model_id: str, version: str) -> ModelCard:
    return ModelCard(model_id, version, ModelValidityTier.ANALYTIC_UNVALIDATED, "fixture", ("assumption",), ("not physical",), ("verification",), "card")


def suite() -> SealedModelComparisonSuite:
    case = ModelComparisonCase("case", input_case(), "V/m", NumericTolerance(1e-12, 1e-12), ("fixture",), "fixture only")
    return SealedModelComparisonSuite("comparison-v1", "primary", "1.0.0", "primary-digest", "reference", "2.0.0", "reference-digest", (case,), "independence review", datetime(2026, 1, 2, tzinfo=timezone.utc), "fixture only")


class ModelComparisonTests(unittest.TestCase):
    def test_matching_implementations_record_a_passing_sealed_comparison(self) -> None:
        with TemporaryDirectory() as directory:
            ledger = JsonlExperimentLedger(Path(directory) / "comparison.jsonl")
            result = execute_sealed_model_comparison(PrimaryFixture(), card("primary", "1.0.0"), admission("primary", "1.0.0"), ReferenceFixture(), card("reference", "2.0.0"), admission("reference", "2.0.0"), suite(), ledger)
        self.assertTrue(result.passed)
        self.assertTrue(result.ledger_event_digest)

    def test_divergence_is_preserved_as_a_failed_comparison(self) -> None:
        with TemporaryDirectory() as directory:
            result = execute_sealed_model_comparison(PrimaryFixture(), card("primary", "1.0.0"), admission("primary", "1.0.0"), DivergentReference(), card("reference", "2.0.0"), admission("reference", "2.0.0"), suite(), JsonlExperimentLedger(Path(directory) / "comparison.jsonl"))
        self.assertFalse(result.passed)

    def test_suite_rejects_same_model_identity_on_construction(self) -> None:
        with self.assertRaisesRegex(ValueError, "distinct"):
            SealedModelComparisonSuite("bad", "same", "1", "a", "same", "1", "b", suite().cases, "review", datetime(2026, 1, 2, tzinfo=timezone.utc), "fixture")


if __name__ == "__main__":
    unittest.main()
