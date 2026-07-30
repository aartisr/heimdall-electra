from __future__ import annotations

import unittest

from heimdall.evaluation import EvaluationRow
from heimdall.performance_assessment import DetectorPerformanceCriterion, assess_detector_performance, wilson_interval


class PerformanceAssessmentTests(unittest.TestCase):
    def test_wilson_interval_is_conservative_for_small_samples(self) -> None:
        interval = wilson_interval(1, 1, 0.95)
        self.assertEqual(1.0, interval.estimate)
        self.assertLess(interval.lower, 1.0)

    def test_assessment_refuses_aggregate_success_without_stratum_evidence(self) -> None:
        criterion = DetectorPerformanceCriterion("signal/1", "signal", 5, 5, 0.5, 0.5)
        rows = tuple(EvaluationRow(f"p{index}", "signal", True, True, 0.9) for index in range(5))
        assessment = assess_detector_performance(rows, criterion, "workload", "configuration")
        self.assertFalse(assessment.passed)
        self.assertIn("negative trial", assessment.violations[0])

    def test_assessment_uses_confidence_bounds_not_point_estimates(self) -> None:
        criterion = DetectorPerformanceCriterion("signal/2", "signal", 10, 10, 0.5, 0.5)
        rows = tuple(
            [EvaluationRow(f"p{index}", "signal", True, True, 0.9) for index in range(10)]
            + [EvaluationRow(f"n{index}", "signal", False, False, 0.1) for index in range(10)]
        )
        assessment = assess_detector_performance(rows, criterion, "workload", "configuration")
        self.assertTrue(assessment.passed)
        self.assertGreater(assessment.performance.detection_probability.lower, 0.5)  # type: ignore[union-attr]


if __name__ == "__main__":
    unittest.main()
