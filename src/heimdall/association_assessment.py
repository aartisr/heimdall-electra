"""Confidence-aware evaluation of association recall and false coincidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .governance import digest_value
from .performance_assessment import BinomialInterval, wilson_interval


@dataclass(frozen=True)
class AssociationEvaluationRow:
    case_id: str
    stratum: str
    expected_association: bool
    associated: bool

    def __post_init__(self) -> None:
        if not self.case_id or not self.stratum:
            raise ValueError("association evaluation case and stratum are required")


@dataclass(frozen=True)
class AssociationCriterion:
    criterion_id: str
    stratum: str
    minimum_true_association_cases: int
    minimum_false_association_cases: int
    minimum_recall_lower_bound: float
    maximum_false_coincidence_upper_bound: float
    confidence_level: float = 0.95

    def __post_init__(self) -> None:
        if not self.criterion_id or not self.stratum or min(
            self.minimum_true_association_cases, self.minimum_false_association_cases
        ) < 1:
            raise ValueError("association criterion requires identity and minimum case counts")
        if not 0 <= self.minimum_recall_lower_bound <= 1 or not 0 <= self.maximum_false_coincidence_upper_bound <= 1:
            raise ValueError("association criterion probability bounds are invalid")
        if not 0 < self.confidence_level < 1:
            raise ValueError("association criterion confidence is invalid")

    @property
    def digest(self) -> str:
        return digest_value(self)


@dataclass(frozen=True)
class AssociationAssessment:
    criterion_id: str
    criterion_digest: str
    workload_digest: str
    true_association_recall: BinomialInterval | None
    false_coincidence_probability: BinomialInterval | None
    violations: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.violations


def assess_association(
    rows: Sequence[AssociationEvaluationRow],
    criterion: AssociationCriterion,
    workload_digest: str,
) -> AssociationAssessment:
    if not workload_digest:
        raise ValueError("association assessment requires workload lineage")
    stratum_rows = tuple(row for row in rows if row.stratum == criterion.stratum)
    true_cases = tuple(row for row in stratum_rows if row.expected_association)
    false_cases = tuple(row for row in stratum_rows if not row.expected_association)
    recall = wilson_interval(sum(row.associated for row in true_cases), len(true_cases), criterion.confidence_level) if true_cases else None
    false_coincidence = wilson_interval(sum(row.associated for row in false_cases), len(false_cases), criterion.confidence_level) if false_cases else None
    violations = []
    if len(true_cases) < criterion.minimum_true_association_cases:
        violations.append("true-association case count is below criterion minimum")
    elif recall is not None and recall.lower < criterion.minimum_recall_lower_bound:
        violations.append("association-recall lower confidence bound is below criterion")
    if len(false_cases) < criterion.minimum_false_association_cases:
        violations.append("false-association case count is below criterion minimum")
    elif false_coincidence is not None and false_coincidence.upper > criterion.maximum_false_coincidence_upper_bound:
        violations.append("false-coincidence upper confidence bound exceeds criterion")
    return AssociationAssessment(
        criterion.criterion_id, criterion.digest, workload_digest, recall, false_coincidence, tuple(violations)
    )
