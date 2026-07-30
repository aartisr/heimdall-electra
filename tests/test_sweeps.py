from __future__ import annotations

import unittest

from heimdall.domain import DatasetSplit
from heimdall.forward_models import IllustrativeBurstSineModel
from heimdall.pipeline import BaselineMatchedFilter
from heimdall.simulation import SyntheticScenario
from heimdall.sweeps import SweepAxis, SweepDefinition, expand, run_sweep


class SweepTests(unittest.TestCase):
    def test_development_sweep_is_deterministic_and_lineage_rich(self) -> None:
        definition = SweepDefinition(
            "test-sweep",
            SyntheticScenario("base", seed=1, signal_amplitude=1.0),
            (
                SweepAxis("signal_amplitude", (0.0, 1.0)),
                SweepAxis("noise_amplitude", (0.1, 0.2)),
            ),
            DatasetSplit.DEVELOPMENT,
            "test only",
        )
        report = run_sweep(
            definition, BaselineMatchedFilter(), (), IllustrativeBurstSineModel()
        )
        self.assertEqual(4, len(expand(definition)))
        self.assertEqual(4, report.result_count)
        self.assertEqual("illustrative-burst-sine", report.results[0].model_id)
        self.assertTrue(all(result.scenario_id.startswith("base:test-sweep:") for result in report.results))

    def test_sweep_rejects_locked_validation_use(self) -> None:
        with self.assertRaisesRegex(ValueError, "development-only"):
            SweepDefinition(
                "invalid",
                SyntheticScenario("base", seed=1),
                (SweepAxis("noise_amplitude", (0.1,)),),
                DatasetSplit.LOCKED_VALIDATION,
                "must fail",
            )


if __name__ == "__main__":
    unittest.main()

