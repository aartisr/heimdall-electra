from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import nan
import unittest

from heimdall.model_registry import default_model_registry
from heimdall.physics_contract import (
    CoordinateFrame,
    OrbitalState,
    PhysicsModelInput,
    PhysicsModelOutput,
    PlasmaEnvironment,
    TargetAssumptions,
    TimeScale,
)
from heimdall.physics_validation import validate_conformance


@dataclass(frozen=True)
class DeterministicFixtureModel:
    model_id: str = "null-signal-model"
    model_version: str = "0.1.0"

    def simulate(self, model_input: PhysicsModelInput) -> PhysicsModelOutput:
        return PhysicsModelOutput(
            self.model_id, self.model_version, model_input.scenario_id,
            "fixture only", "dimensionless fixture value", (0.0,),
        )


@dataclass(frozen=True)
class NonFiniteFixtureModel(DeterministicFixtureModel):
    def simulate(self, model_input: PhysicsModelInput) -> PhysicsModelOutput:
        return PhysicsModelOutput(
            self.model_id, self.model_version, model_input.scenario_id,
            "fixture only", "dimensionless fixture value", (nan,),
        )


def model_input() -> PhysicsModelInput:
    return PhysicsModelInput(
        "validation-fixture",
        OrbitalState(
            datetime(2026, 1, 1, tzinfo=timezone.utc), TimeScale.UTC,
            CoordinateFrame.ECI_J2000, (1.0, 2.0, 3.0), (4.0, 5.0, 6.0), 1.0,
        ),
        PlasmaEnvironment(1.0, 1.0, 1.0, 1.0, (0.0, 0.0, 1.0), "fixture"),
        TargetAssumptions("target", 0.01, -1e-12, "fixture", "sphere"),
        "fixture assumptions",
    )


class PhysicsValidationTests(unittest.TestCase):
    def test_contract_conforming_fixture_passes_software_checks(self) -> None:
        report = validate_conformance(
            DeterministicFixtureModel(),
            default_model_registry().resolve("null-signal-model", "0.1.0"),
            model_input(),
        )
        self.assertTrue(report.passed)
        self.assertEqual((), report.checks)

    def test_nonfinite_output_is_rejected(self) -> None:
        report = validate_conformance(
            NonFiniteFixtureModel(),
            default_model_registry().resolve("null-signal-model", "0.1.0"),
            model_input(),
        )
        self.assertFalse(report.passed)
        self.assertIn("non-finite", report.checks[0])


if __name__ == "__main__":
    unittest.main()

