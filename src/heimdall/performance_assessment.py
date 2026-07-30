"""Confidence-aware detector performance assessment for predeclared strata."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import NormalDist
from typing import Sequence

from .evaluation import EvaluationRow
from .governance import digest_value


@dataclass(frozen=True)
class BinomialInterval:
    successes: int
    trials: int
    confidence_level: float
    estimate: float
    lower: float
    upper: float

    def __post_init__(self) -> None:
        if self.trials <= 0 or not 0 <= self.successes <= self.trials:
            raise ValueError("binomial counts are invalid")
        if not 0 < self.confidence_level < 1:
            raise ValueError("confidence level must be between zero and one")


@dataclass(frozen=True)
class StratumPerformance:
    stratum: str
    detection_probability: BinomialInterval | None
    false_alarm_probability: BinomialInterval | None


@dataclass(frozen=True)
class DetectorPerformanceCriterion:
    criterion_id: str
    stratum: str
    minimum_positive_trials: int
    minimum_negative_trials: int
    minimum_detection_lower_bound: float
    maximum_false_alarm_upper_bound: float
    confidence_level: float = 0.95

    def __post_init__(self) -> None:
        if not self.criterion_id or not self.stratum or min(self.minimum_positive_trials, self.minimum_negative_trials) < 1:
            raise ValueError("performance criterion identity and minimum sample sizes are required")
        if not 0 <= self.minimum_detection_lower_bound <= 1 or not 0 <= self.maximum_false_alarm_upper_bound <= 1:
            raise ValueError("performance criterion probability bounds are invalid")
        if not 0 < self.confidence_level < 1:
            raise ValueError("confidence level must be between zero and one")

    @property
    def digest(self) -> str:
        return digest_value(self)


@dataclass(frozen=True)
class PerformanceAssessment:
    criterion_id: str
    criterion_digest: str
    stratum: str
    workload_digest: str
    detector_configuration_digest: str
    performance: StratumPerformance
    violations: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.violations


def wilson_interval(successes: int, trials: int, confidence_level: float) -> BinomialInterval:
    if trials <= 0 or not 0 <= successes <= trials:
        raise ValueError("binomial counts are invalid")
    z = NormalDist().inv_cdf(0.5 + confidence_level / 2)
    estimate = successes / trials
    denominator = 1 + z * z / trials
    center = (estimate + z * z / (2 * trials)) / denominator
    half_width = z * sqrt((estimate * (1 - estimate) + z * z / (4 * trials)) / trials) / denominator
    return BinomialInterval(successes, trials, confidence_level, estimate, max(0.0, center - half_width), min(1.0, center + half_width))


def assess_detector_performance(
    rows: Sequence[EvaluationRow],
    criterion: DetectorPerformanceCriterion,
    workload_digest: str,
    detector_configuration_digest: str,
) -> PerformanceAssessment:
    if not workload_digest or not detector_configuration_digest:
        raise ValueError("assessment requires workload and detector configuration lineage")
    matching = tuple(row for row in rows if row.stratum == criterion.stratum)
    positive = tuple(row for row in matching if row.expected_signal)
    negative = tuple(row for row in matching if not row.expected_signal)
    detection = wilson_interval(sum(row.detected for row in positive), len(positive), criterion.confidence_level) if positive else None
    false_alarm = wilson_interval(sum(row.detected for row in negative), len(negative), criterion.confidence_level) if negative else None
    performance = StratumPerformance(criterion.stratum, detection, false_alarm)
    violations = []
    if len(positive) < criterion.minimum_positive_trials:
        violations.append("positive trial count is below criterion minimum")
    elif detection is not None and detection.lower < criterion.minimum_detection_lower_bound:
        violations.append("detection-probability lower confidence bound is below criterion")
    if len(negative) < criterion.minimum_negative_trials:
        violations.append("negative trial count is below criterion minimum")
    elif false_alarm is not None and false_alarm.upper > criterion.maximum_false_alarm_upper_bound:
        violations.append("false-alarm-probability upper confidence bound exceeds criterion")
    return PerformanceAssessment(
        criterion.criterion_id, criterion.digest, criterion.stratum, workload_digest,
        detector_configuration_digest, performance, tuple(violations),
    )
