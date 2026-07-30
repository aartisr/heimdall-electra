"""Metrics for synthetic experiments; not estimates of flight performance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class EvaluationRow:
    scenario_id: str
    stratum: str
    expected_signal: bool
    detected: bool
    score: float


@dataclass(frozen=True)
class DetectionReport:
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int

    @property
    def detection_probability(self) -> float:
        denominator = self.true_positive + self.false_negative
        return self.true_positive / denominator if denominator else 0.0

    @property
    def false_alarm_rate(self) -> float:
        denominator = self.false_positive + self.true_negative
        return self.false_positive / denominator if denominator else 0.0


def evaluate(rows: Iterable[EvaluationRow]) -> DetectionReport:
    tp = fp = tn = fn = 0
    for row in rows:
        if row.expected_signal and row.detected:
            tp += 1
        elif row.expected_signal:
            fn += 1
        elif row.detected:
            fp += 1
        else:
            tn += 1
    return DetectionReport(tp, fp, tn, fn)


def evaluate_by_stratum(rows: Iterable[EvaluationRow]) -> Mapping[str, DetectionReport]:
    grouped: dict[str, list[EvaluationRow]] = {}
    for row in rows:
        grouped.setdefault(row.stratum, []).append(row)
    return {stratum: evaluate(group) for stratum, group in grouped.items()}
