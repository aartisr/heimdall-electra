from __future__ import annotations

import unittest

from heimdall.uncertainty import UncertaintyBudget, UncertaintyComponent, UncertaintyKind


def component(
    component_id: str,
    uncertainty: float,
    correlation_group: str = "",
) -> UncertaintyComponent:
    return UncertaintyComponent(
        component_id=component_id,
        kind=UncertaintyKind.CALIBRATION,
        quantity_id="sensor.voltage",
        unit="V",
        standard_uncertainty=uncertainty,
        distribution="normal",
        evidence_reference="synthetic fixture only",
        correlation_group=correlation_group,
    )


class UncertaintyBudgetTests(unittest.TestCase):
    def test_independent_standard_uncertainties_combine_by_root_sum_square(self) -> None:
        budget = UncertaintyBudget(
            "budget-001", "sensor.voltage", 10.0, "V",
            (component("calibration", 3.0), component("noise", 4.0)),
            "synthetic budget",
        )
        self.assertEqual(5.0, budget.combined_standard_uncertainty)
        self.assertEqual((0.0, 20.0), budget.interval(2.0))

    def test_correlated_components_require_explicit_covariance_method(self) -> None:
        with self.assertRaisesRegex(ValueError, "correlated"):
            UncertaintyBudget(
                "budget-002", "sensor.voltage", 10.0, "V",
                (component("first", 1.0, "shared"), component("second", 1.0, "shared")),
                "synthetic budget",
            )

    def test_mixed_units_are_rejected(self) -> None:
        invalid = UncertaintyComponent(
            "timing", UncertaintyKind.TIMING, "sensor.voltage", "s", 1.0,
            "normal", "fixture",
        )
        with self.assertRaisesRegex(ValueError, "same quantity and unit"):
            UncertaintyBudget(
                "budget-003", "sensor.voltage", 10.0, "V",
                (component("calibration", 1.0), invalid),
                "synthetic budget",
            )


if __name__ == "__main__":
    unittest.main()

