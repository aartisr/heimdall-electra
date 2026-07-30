from __future__ import annotations

import unittest

from heimdall.coverage_trade import ConstellationTradeScenario, CoverageDefinition, CoverageTradeResult, validate_coverage_result


class FakeCoverageModel:
    model_id = "fixture-coverage"
    model_version = "1.0.0"


def scenario() -> ConstellationTradeScenario:
    return ConstellationTradeScenario("trade-001", 3, 0.5, 0.9, "orbit fixture", "instrument fixture", CoverageDefinition("coverage/1", "research proxy", "defined region", 3600, "fixture confidence"))


class CoverageTradeTests(unittest.TestCase):
    def test_result_binds_scenario_and_model_identity(self) -> None:
        result = CoverageTradeResult("trade-001", "fixture-coverage", "1.0.0", 0.2, 0.1, "fixture only")
        validate_coverage_result(result, scenario(), FakeCoverageModel())

    def test_invalid_definition_or_identity_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "availability"):
            ConstellationTradeScenario("trade", 0, 0.5, 0.9, "orbit", "instrument", scenario().coverage_definition)
        with self.assertRaisesRegex(ValueError, "scenario"):
            validate_coverage_result(CoverageTradeResult("other", "fixture-coverage", "1.0.0", 0.2, 0.1, "fixture"), scenario(), FakeCoverageModel())


if __name__ == "__main__":
    unittest.main()
