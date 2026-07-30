from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.model_admission import AdmissionStatus, PhysicsModelAdmission
from heimdall.model_registry import ModelCard, ModelValidityTier
from heimdall.governance import JsonlExperimentLedger
from heimdall.physics_benchmarks import (
    NumericTolerance, PhysicsBenchmarkCase, SealedPhysicsBenchmarkSuite,
    execute_sealed_physics_benchmark_suite, run_physics_benchmark, run_physics_benchmark_suite,
    run_sealed_physics_benchmark_suite,
)
from heimdall.physics_contract import CoordinateFrame, OrbitalState, PhysicsModelInput, PhysicsModelOutput, PlasmaEnvironment, TargetAssumptions, TimeScale


class ConstantAnalyticFixture:
    model_id = "candidate"
    model_version = "1.0.0"

    def simulate(self, model_input: PhysicsModelInput) -> PhysicsModelOutput:
        return PhysicsModelOutput(
            self.model_id, self.model_version, model_input.scenario_id,
            "fixture output for benchmark harness testing only", "V/m", (1.0, 2.0),
        )


def input_case() -> PhysicsModelInput:
    return PhysicsModelInput(
        "benchmark-case", OrbitalState(
            datetime(2026, 1, 1, tzinfo=timezone.utc), TimeScale.UTC, CoordinateFrame.ECI_J2000,
            (1.0, 2.0, 3.0), (4.0, 5.0, 6.0), 0.1,
        ), PlasmaEnvironment(1e10, 1e10, 1000, 1000, (1e-5, 0.0, 0.0), "test source"),
        TargetAssumptions("target", 0.01, 0.0, "test material", "sphere"), "test assumptions",
    )


def admission() -> PhysicsModelAdmission:
    return PhysicsModelAdmission(
        "candidate", "1.0.0", AdmissionStatus.APPROVED, "owner", "hypothesis", ("equations",),
        "input", "output", "numerics", ("verification",), "independent review", "test limits",
    )


def card() -> ModelCard:
    return ModelCard(
        "candidate", "1.0.0", ModelValidityTier.ANALYTIC_UNVALIDATED, "test", ("assumption",),
        ("not flight",), ("verification",), "card",
    )


def benchmark(expected_values: tuple[float, ...] = (1.0, 2.0)) -> PhysicsBenchmarkCase:
    return PhysicsBenchmarkCase(
        "constant-output", "candidate", "1.0.0", input_case(), "V/m", expected_values,
        NumericTolerance(absolute=1e-9, relative=1e-9), ("benchmark evidence",), "test only",
    )


class PhysicsBenchmarkTests(unittest.TestCase):
    def test_declared_benchmark_passes_for_matching_output(self) -> None:
        result = run_physics_benchmark(ConstantAnalyticFixture(), card(), admission(), benchmark())
        self.assertTrue(result.passed)

    def test_declared_benchmark_reports_numeric_or_unit_failure(self) -> None:
        numeric = run_physics_benchmark(ConstantAnalyticFixture(), card(), admission(), benchmark((1.0, 3.0)))
        self.assertFalse(numeric.passed)
        self.assertIn("index 1", numeric.comparison_failures[0])
        wrong_units = PhysicsBenchmarkCase(
            "wrong-units", "candidate", "1.0.0", input_case(), "T", (1.0, 2.0),
            NumericTolerance(1e-9, 1e-9), ("evidence",), "test",
        )
        self.assertFalse(run_physics_benchmark(ConstantAnalyticFixture(), card(), admission(), wrong_units).passed)

    def test_suite_refuses_duplicate_or_empty_cases(self) -> None:
        fixture = ConstantAnalyticFixture()
        with self.assertRaisesRegex(ValueError, "at least"):
            run_physics_benchmark_suite(fixture, card(), admission(), ())
        with self.assertRaisesRegex(ValueError, "unique"):
            run_physics_benchmark_suite(fixture, card(), admission(), (benchmark(), benchmark()))

    def test_sealed_suite_binds_exact_cases_and_identity(self) -> None:
        suite = SealedPhysicsBenchmarkSuite(
            "suite-001", "candidate", "1.0.0", (benchmark(),), "independent review",
            datetime(2026, 1, 2, tzinfo=timezone.utc),
        )
        result = run_sealed_physics_benchmark_suite(ConstantAnalyticFixture(), card(), admission(), suite)
        self.assertTrue(result.passed)
        self.assertEqual(suite.digest, result.suite_digest)
        changed = SealedPhysicsBenchmarkSuite(
            "suite-001", "candidate", "1.0.0", (benchmark((1.0, 3.0)),), "independent review",
            datetime(2026, 1, 2, tzinfo=timezone.utc),
        )
        self.assertNotEqual(suite.digest, changed.digest)

    def test_sealed_suite_rejects_mixed_case_identity(self) -> None:
        other = PhysicsBenchmarkCase(
            "other", "other-model", "1.0.0", input_case(), "V/m", (1.0, 2.0),
            NumericTolerance(1e-9, 1e-9), ("evidence",), "test",
        )
        with self.assertRaisesRegex(ValueError, "match the suite"):
            SealedPhysicsBenchmarkSuite(
                "bad", "candidate", "1.0.0", (benchmark(), other), "review",
                datetime(2026, 1, 2, tzinfo=timezone.utc),
            )

    def test_execution_binds_sealed_result_to_append_only_ledger(self) -> None:
        suite = SealedPhysicsBenchmarkSuite(
            "suite-001", "candidate", "1.0.0", (benchmark(),), "independent review",
            datetime(2026, 1, 2, tzinfo=timezone.utc),
        )
        with TemporaryDirectory() as directory:
            ledger = JsonlExperimentLedger(Path(directory) / "benchmarks.jsonl")
            execution = execute_sealed_physics_benchmark_suite(
                ConstantAnalyticFixture(), card(), admission(), suite, ledger
            )
            self.assertTrue(execution.passed)
            self.assertTrue(execution.ledger_event_digest)
            self.assertTrue(ledger.verify())


if __name__ == "__main__":
    unittest.main()
