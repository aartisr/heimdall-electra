from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.governance import JsonlExperimentLedger
from heimdall.model_admission import AdmissionStatus, PhysicsModelAdmission
from heimdall.model_registry import ModelCard, ModelValidityTier
from heimdall.physics_benchmarks import NumericTolerance
from heimdall.physics_contract import CoordinateFrame, OrbitalState, PhysicsModelInput, PhysicsModelOutput, PlasmaEnvironment, TargetAssumptions, TimeScale
from heimdall.physics_relations import MetamorphicPhysicsCase, RelationKind, SealedMetamorphicSuite, execute_sealed_metamorphic_suite, run_metamorphic_case


class SignFixtureModel:
    model_id = "candidate"
    model_version = "1.0.0"

    def simulate(self, model_input: PhysicsModelInput) -> PhysicsModelOutput:
        sign = -1.0 if model_input.scenario_id == "reversed" else 1.0
        return PhysicsModelOutput(self.model_id, self.model_version, model_input.scenario_id, "fixture only", "V/m", (sign, 2 * sign))


def model_input(scenario_id: str) -> PhysicsModelInput:
    return PhysicsModelInput(
        scenario_id, OrbitalState(datetime(2026, 1, 1, tzinfo=timezone.utc), TimeScale.UTC,
        CoordinateFrame.ECI_J2000, (1.0, 2.0, 3.0), (4.0, 5.0, 6.0), 0.1),
        PlasmaEnvironment(1e10, 1e10, 1000, 1000, (1e-5, 0.0, 0.0), "fixture"),
        TargetAssumptions("target", 0.01, 0.0, "fixture", "sphere"), "fixture",
    )


def admission() -> PhysicsModelAdmission:
    return PhysicsModelAdmission("candidate", "1.0.0", AdmissionStatus.APPROVED, "owner", "hypothesis", ("equation",), "input", "output", "numerics", ("verification",), "review", "fixture only")


def card() -> ModelCard:
    return ModelCard("candidate", "1.0.0", ModelValidityTier.ANALYTIC_UNVALIDATED, "fixture", ("assumption",), ("not physical",), ("verification",), "card")


def opposite_case(kind: RelationKind = RelationKind.OPPOSITE) -> MetamorphicPhysicsCase:
    return MetamorphicPhysicsCase(
        "sign-reversal", "candidate", "1.0.0", model_input("baseline"), model_input("reversed"), "V/m",
        kind, None, NumericTolerance(1e-12, 1e-12), ("fixture evidence",), "fixture relation only",
    )


class PhysicsRelationsTests(unittest.TestCase):
    def test_declared_opposite_relation_passes(self) -> None:
        self.assertTrue(run_metamorphic_case(SignFixtureModel(), card(), admission(), opposite_case()).passed)

    def test_incorrect_relation_is_preserved_as_failure(self) -> None:
        result = run_metamorphic_case(SignFixtureModel(), card(), admission(), opposite_case(RelationKind.EQUAL))
        self.assertFalse(result.passed)
        self.assertIn("violates", result.relation_failures[0])

    def test_sealed_suite_records_full_outcome_in_ledger(self) -> None:
        suite = SealedMetamorphicSuite("relations-v1", "candidate", "1.0.0", (opposite_case(),), "review", datetime(2026, 1, 2, tzinfo=timezone.utc))
        with TemporaryDirectory() as directory:
            ledger = JsonlExperimentLedger(Path(directory) / "relations.jsonl")
            execution = execute_sealed_metamorphic_suite(SignFixtureModel(), card(), admission(), suite, ledger)
        self.assertTrue(execution.passed)
        self.assertTrue(execution.ledger_event_digest)


if __name__ == "__main__":
    unittest.main()
