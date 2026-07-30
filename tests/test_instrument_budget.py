from __future__ import annotations

import unittest

from heimdall.instrument_budget import InstrumentBudget, InstrumentBudgetLimit, evaluate_instrument_budget


class InstrumentBudgetTests(unittest.TestCase):
    def test_reports_each_resource_limit_violation(self) -> None:
        budget = InstrumentBudget("budget", 1000, 60, 10, 6, 8, 4, 20, ("fixture",), "fixture only")
        limit = InstrumentBudgetLimit("limit", 5, 7, 3, 10)
        self.assertEqual(4, len(evaluate_instrument_budget(budget, limit)))

    def test_rejects_impossible_peak_power(self) -> None:
        with self.assertRaisesRegex(ValueError, "peak"):
            InstrumentBudget("budget", 1, 1, 1, 2, 1, 1, 1, ("fixture",), "fixture")


if __name__ == "__main__":
    unittest.main()
