"""Run the non-operational synthetic Heimdall vertical slice."""

from __future__ import annotations

from dataclasses import asdict
from json import dumps

from heimdall import (
    BaselineMatchedFilter,
    EvaluationRow,
    ClockQualityGate,
    PeakContrastGate,
    calibrate,
    detect,
    evaluate,
    evaluate_by_stratum,
    generate_observation,
    reference_registry,
)


def main() -> None:
    detector = BaselineMatchedFilter()
    rows = []
    candidates = []
    for registered in reference_registry():
        observation = generate_observation(registered.scenario)
        calibrated = calibrate(observation)
        candidate = detect(
            calibrated,
            detector,
            gates=(PeakContrastGate(), ClockQualityGate()),
        )
        candidates.append({
            "scenario_id": registered.scenario.scenario_id,
            "split": registered.split.value,
            "expected_signal_for_synthetic_evaluation_only": registered.scenario.expected_signal,
            "candidate": asdict(candidate),
        })
        rows.append(EvaluationRow(
            scenario_id=registered.scenario.scenario_id,
            stratum=registered.stratum,
            expected_signal=registered.scenario.expected_signal,
            detected=candidate.detected,
            score=candidate.score,
        ))
    report = evaluate(rows)
    by_stratum = evaluate_by_stratum(rows)
    print(dumps({
        "scientific_status": "SYNTHETIC RESEARCH ONLY — NOT AN OBSERVED DEBRIS DETECTION",
        "evaluation_scope": "Reference fixtures only. This is not flight-performance evidence.",
        "metrics": {
            "true_positive": report.true_positive,
            "false_positive": report.false_positive,
            "true_negative": report.true_negative,
            "false_negative": report.false_negative,
            "detection_probability": report.detection_probability,
            "false_alarm_rate": report.false_alarm_rate,
        },
        "metrics_by_stratum": {
            stratum: {
                "true_positive": result.true_positive,
                "false_positive": result.false_positive,
                "true_negative": result.true_negative,
                "false_negative": result.false_negative,
                "detection_probability": result.detection_probability,
                "false_alarm_rate": result.false_alarm_rate,
            }
            for stratum, result in by_stratum.items()
        },
        "candidates": candidates,
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
