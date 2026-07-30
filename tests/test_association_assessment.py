from __future__ import annotations

import unittest

from heimdall.association_assessment import AssociationCriterion, AssociationEvaluationRow, assess_association


class AssociationAssessmentTests(unittest.TestCase):
    def test_assessment_requires_negative_false_coincidence_cases(self) -> None:
        criterion = AssociationCriterion("association/1", "geometry", 5, 5, 0.5, 0.5)
        rows = tuple(AssociationEvaluationRow(f"true-{index}", "geometry", True, True) for index in range(5))
        result = assess_association(rows, criterion, "workload")
        self.assertFalse(result.passed)
        self.assertIn("false-association", result.violations[0])

    def test_assessment_reports_false_coincidence_confidence_failure(self) -> None:
        criterion = AssociationCriterion("association/2", "geometry", 10, 10, 0.5, 0.2)
        rows = tuple(
            [AssociationEvaluationRow(f"true-{index}", "geometry", True, True) for index in range(10)]
            + [AssociationEvaluationRow(f"false-{index}", "geometry", False, index == 0) for index in range(10)]
        )
        result = assess_association(rows, criterion, "workload")
        self.assertFalse(result.passed)
        self.assertIn("false-coincidence", result.violations[0])

    def test_assessment_passes_when_both_conservative_bounds_are_met(self) -> None:
        criterion = AssociationCriterion("association/3", "geometry", 20, 20, 0.7, 0.2)
        rows = tuple(
            [AssociationEvaluationRow(f"true-{index}", "geometry", True, True) for index in range(20)]
            + [AssociationEvaluationRow(f"false-{index}", "geometry", False, False) for index in range(20)]
        )
        self.assertTrue(assess_association(rows, criterion, "workload").passed)


if __name__ == "__main__":
    unittest.main()
