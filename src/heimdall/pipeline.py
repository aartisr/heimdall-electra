"""Pluggable, transparent detector pipeline for synthetic vertical-slice validation."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import pi, sin
from statistics import fmean
from typing import Protocol, Sequence

from .domain import CalibratedObservationL1, CandidateL2, ObservationL0


@dataclass(frozen=True)
class BaselineMatchedFilter:
    detector_id: str = "wavelet-matched-filter-baseline"
    detector_version: str = "0.1.0"
    threshold_policy_id: str = "synthetic-research-only/0.1.0"
    target_frequency_hz: float = 64.0
    window_duration_s: float = 0.25
    threshold: float = 0.55

    def __post_init__(self) -> None:
        if self.target_frequency_hz <= 0 or self.window_duration_s <= 0:
            raise ValueError("frequency and window duration must be positive")
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("threshold must be normalized")


@dataclass(frozen=True)
class GateDecision:
    gate_id: str
    passed: bool
    reason: str
    metrics: dict[str, float]


@dataclass(frozen=True)
class DetectionContext:
    scores: tuple[float, ...]
    peak_score: float
    peak_start_sample: int
    clock_uncertainty_ns: float


class CandidateGate(Protocol):
    """Port for policy-controlled candidate acceptance checks."""

    def assess(self, context: DetectionContext) -> GateDecision:
        """Return an auditable decision without mutating the raw detector score."""


@dataclass(frozen=True)
class PeakContrastGate:
    """Reject near-continuous matched-filter energy in synthetic reference data.

    A burst-like fixture is expected to have a substantially stronger peak than
    its mean window score. This is a generic interference-control example only;
    its parameter must be independently calibrated before use with observations.
    """

    minimum_peak_to_mean_ratio: float = 1.75
    gate_id: str = "peak-contrast/synthetic-research-only/0.1.0"

    def __post_init__(self) -> None:
        if self.minimum_peak_to_mean_ratio <= 1.0:
            raise ValueError("contrast ratio must be greater than one")

    def assess(self, context: DetectionContext) -> GateDecision:
        mean_score = fmean(context.scores) if context.scores else 0.0
        ratio = context.peak_score / max(mean_score, 1e-12)
        passed = ratio >= self.minimum_peak_to_mean_ratio
        return GateDecision(
            gate_id=self.gate_id,
            passed=passed,
            reason=(
                "burst contrast passed"
                if passed
                else "rejected: continuous-tone-like matched-filter response"
            ),
            metrics={"peak_to_mean_ratio": ratio, "mean_window_score": mean_score},
        )


@dataclass(frozen=True)
class ClockQualityGate:
    """Reject an otherwise high score when synthetic clock quality is inadequate.

    This is a quality-policy example. Its limit must be derived from the timing
    error budget before any laboratory or flight use.
    """

    maximum_clock_uncertainty_ns: float = 1_000.0
    gate_id: str = "clock-quality/synthetic-research-only/0.1.0"

    def __post_init__(self) -> None:
        if self.maximum_clock_uncertainty_ns < 0:
            raise ValueError("clock limit must be non-negative")

    def assess(self, context: DetectionContext) -> GateDecision:
        passed = context.clock_uncertainty_ns <= self.maximum_clock_uncertainty_ns
        return GateDecision(
            gate_id=self.gate_id,
            passed=passed,
            reason=(
                "clock quality passed"
                if passed
                else "rejected: clock uncertainty exceeds synthetic policy limit"
            ),
            metrics={
                "clock_uncertainty_ns": context.clock_uncertainty_ns,
                "maximum_clock_uncertainty_ns": self.maximum_clock_uncertainty_ns,
            },
        )


def detect(
    observation: ObservationL0 | CalibratedObservationL1,
    detector: BaselineMatchedFilter,
    gates: Sequence[CandidateGate] = (),
) -> CandidateL2:
    window_size = max(1, int(observation.sample_rate_hz * detector.window_duration_s))
    best_score = 0.0
    best_start = 0
    scores = []

    for start in range(0, len(observation.samples) - window_size + 1):
        correlation = 0.0
        signal_energy = 0.0
        for offset in range(window_size):
            template = sin(2 * pi * detector.target_frequency_hz * (start + offset) / observation.sample_rate_hz)
            value = observation.samples[start + offset]
            correlation += value * template
            signal_energy += abs(value)
        normalized = min(1.0, abs(correlation) / max(1e-12, signal_energy))
        scores.append(normalized)
        if normalized > best_score:
            best_score = normalized
            best_start = start

    context = DetectionContext(
        tuple(scores),
        best_score,
        best_start,
        observation.clock_uncertainty_ns,
    )
    decisions = tuple(gate.assess(context) for gate in gates)
    gates_passed = all(decision.passed for decision in decisions)
    candidate_key = f"{observation.observation_id}:{detector.detector_version}:{best_start}:{gates_passed}".encode()
    explanation = {
        "best_window_start_sample": float(best_start),
        "target_frequency_hz": detector.target_frequency_hz,
        "window_duration_s": detector.window_duration_s,
    }
    for decision in decisions:
        explanation.update({f"{decision.gate_id}:{key}": value for key, value in decision.metrics.items()})
    return CandidateL2(
        candidate_id=f"l2-{sha256(candidate_key).hexdigest()[:16]}",
        observation_id=observation.observation_id,
        detector_id=detector.detector_id,
        detector_version=detector.detector_version,
        threshold_policy_id=detector.threshold_policy_id,
        score=best_score,
        threshold=detector.threshold,
        detected=best_score >= detector.threshold and gates_passed,
        evidence_class=observation.provenance.evidence_class,
        explanation=explanation,
        source_payload_digest=(
            observation.payload_digest
            if isinstance(observation, ObservationL0)
            else observation.parent_payload_digest
        ),
        gates_passed=gates_passed,
        decision_reasons=tuple(decision.reason for decision in decisions if not decision.passed),
    )
