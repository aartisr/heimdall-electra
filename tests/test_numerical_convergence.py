from __future__ import annotations

import unittest

from heimdall.numerical_convergence import ConvergenceRun, ConvergenceStudyPlan, assess_convergence


def plan() -> ConvergenceStudyPlan:
    return ConvergenceStudyPlan(
        study_id="analytic-fixture-convergence-v1", model_id="analytic-fixture", model_version="0.1.0",
        implementation_digest="implementation-sha256", environment_digest="environment-sha256",
        input_digest="input-sha256", quantity_id="fixture-amplitude", quantity_unit="V/m",
        resolution_scales=(1.0, 0.5, 0.25), finest_relative_change_limit=0.1,
        review_reference="docs/PHYSICS_MODEL_VALIDATION.md",
        limitation="Fixture values exercise only the numerical verification contract.",
    )


def run(scale: float, value: float, *, implementation: str = "implementation-sha256") -> ConvergenceRun:
    return ConvergenceRun(
        study_id="analytic-fixture-convergence-v1", model_id="analytic-fixture", model_version="0.1.0",
        implementation_digest=implementation, environment_digest="environment-sha256",
        input_digest="input-sha256", resolution_scale=scale, quantity_value=value,
        output_artifact_digest=f"output-{scale}", measurement_reference="fixture-output",
    )


class NumericalConvergenceTests(unittest.TestCase):
    def test_sealed_refinement_with_small_final_change_passes(self) -> None:
        assessment = assess_convergence(plan(), (run(1.0, 1.16), run(0.5, 1.04), run(0.25, 1.01)))
        self.assertTrue(assessment.passed)
        self.assertAlmostEqual(2.0, assessment.observed_order)
        self.assertLess(assessment.finest_relative_change, 0.1)

    def test_implementation_mismatch_is_not_comparable(self) -> None:
        assessment = assess_convergence(plan(), (run(1.0, 1.16), run(0.5, 1.04), run(0.25, 1.01, implementation="other")))
        self.assertFalse(assessment.passed)
        self.assertIn("configuration", assessment.checks[0])

    def test_unsettled_finest_levels_fail_declared_limit(self) -> None:
        assessment = assess_convergence(plan(), (run(1.0, 2.0), run(0.5, 1.5), run(0.25, 1.0)))
        self.assertFalse(assessment.passed)
        self.assertTrue(any("finest refinement" in check for check in assessment.checks))


if __name__ == "__main__":
    unittest.main()
