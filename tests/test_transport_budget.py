from __future__ import annotations

import unittest

from heimdall.transport_budget import TransportScenario, evaluate_transport_budget


class TransportBudgetTests(unittest.TestCase):
    def test_reports_capacity_shortfall_without_hiding_loss_or_overhead(self) -> None:
        report = evaluate_transport_budget(TransportScenario("link", 100, 0.1, 0.1, 10, 20, 30, 30, ("fixture",)))
        self.assertEqual(81.0, report.usable_capacity_mib_per_day)
        self.assertEqual(9.0, report.shortfall_mib_per_day)

    def test_rejects_invalid_transport_fraction(self) -> None:
        with self.assertRaisesRegex(ValueError, "fractions"):
            TransportScenario("link", 1, 1, 0, 0, 0, 0, 0, ("fixture",))


if __name__ == "__main__":
    unittest.main()
