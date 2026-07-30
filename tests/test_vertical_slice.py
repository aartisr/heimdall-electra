from __future__ import annotations

import unittest

from heimdall import (
    BaselineMatchedFilter,
    ClockQualityGate,
    DatasetSplit,
    EvidenceClass,
    EvaluationRow,
    NullSignalModel,
    PeakContrastGate,
    SyntheticScenario,
    calibrate,
    detect,
    evaluate,
    evaluate_by_stratum,
    generate_observation,
    reference_registry,
)


class VerticalSliceTests(unittest.TestCase):
    def test_generation_is_reproducible_and_explicitly_synthetic(self) -> None:
        scenario = SyntheticScenario("repeatable", seed=7, signal_amplitude=1.0)
        first = generate_observation(scenario)
        second = generate_observation(scenario)

        self.assertEqual(first.payload_digest, second.payload_digest)
        self.assertEqual(EvidenceClass.SYNTHETIC, first.provenance.evidence_class)
        self.assertEqual(first.observation_id, second.observation_id)

    def test_baseline_detector_separates_reference_signal_from_noise_fixture(self) -> None:
        detector = BaselineMatchedFilter(threshold=0.55)
        signal = generate_observation(SyntheticScenario("signal", seed=42, signal_amplitude=1.0))
        noise = generate_observation(SyntheticScenario("noise", seed=42, signal_amplitude=0.0))

        signal_candidate = detect(signal, detector)
        noise_candidate = detect(noise, detector)

        self.assertTrue(signal_candidate.detected)
        self.assertFalse(noise_candidate.detected)
        self.assertEqual(signal.payload_digest, signal_candidate.source_payload_digest)
        self.assertEqual(EvidenceClass.SYNTHETIC, signal_candidate.evidence_class)

    def test_l1_calibration_preserves_l0_lineage(self) -> None:
        observation = generate_observation(SyntheticScenario("calibration", seed=5, signal_amplitude=1.0))
        calibrated = calibrate(observation, scale=2.0, uncertainty_fraction=0.03)
        candidate = detect(calibrated, BaselineMatchedFilter())

        self.assertEqual(observation.payload_digest, calibrated.parent_payload_digest)
        self.assertEqual(observation.payload_digest, candidate.source_payload_digest)
        self.assertEqual(("synthetic_input",), calibrated.quality_flags)

    def test_registry_separates_development_and_locked_validation(self) -> None:
        registered = reference_registry()
        splits = {item.split for item in registered}
        self.assertEqual({DatasetSplit.DEVELOPMENT, DatasetSplit.LOCKED_VALIDATION}, splits)
        self.assertEqual(len({item.manifest_digest for item in registered}), len(registered))

    def test_evaluation_counts_explicit_synthetic_labels(self) -> None:
        report = evaluate((
            EvaluationRow("tp", "signal", True, True, 0.9),
            EvaluationRow("fn", "signal", True, False, 0.2),
            EvaluationRow("fp", "noise", False, True, 0.8),
            EvaluationRow("tn", "noise", False, False, 0.1),
        ))
        self.assertEqual((1, 1, 1, 1), (
            report.true_positive, report.false_positive,
            report.true_negative, report.false_negative,
        ))
        self.assertEqual(0.5, report.detection_probability)
        self.assertEqual(0.5, report.false_alarm_rate)
        by_stratum = evaluate_by_stratum((
            EvaluationRow("tp", "signal", True, True, 0.9),
            EvaluationRow("tn", "noise", False, False, 0.1),
        ))
        self.assertEqual(1.0, by_stratum["signal"].detection_probability)
        self.assertEqual(0.0, by_stratum["noise"].false_alarm_rate)

    def test_peak_contrast_gate_rejects_continuous_tone_fixture_with_a_reason(self) -> None:
        interference = generate_observation(SyntheticScenario(
            "continuous-tone", seed=22, interference_frequency_hz=64.0,
            interference_amplitude=0.75,
        ))
        candidate = detect(
            interference,
            BaselineMatchedFilter(),
            gates=(PeakContrastGate(),),
        )

        self.assertGreaterEqual(candidate.score, candidate.threshold)
        self.assertFalse(candidate.detected)
        self.assertFalse(candidate.gates_passed)
        self.assertIn("continuous-tone-like", candidate.decision_reasons[0])

    def test_clock_quality_gate_rejects_signal_with_degraded_clock_fixture(self) -> None:
        observation = generate_observation(SyntheticScenario(
            "degraded-clock", seed=25, signal_amplitude=0.85,
            clock_uncertainty_ns=10_000.0,
        ))
        candidate = detect(
            calibrate(observation),
            BaselineMatchedFilter(),
            gates=(ClockQualityGate(),),
        )

        self.assertGreaterEqual(candidate.score, candidate.threshold)
        self.assertFalse(candidate.detected)
        self.assertIn("clock uncertainty", candidate.decision_reasons[0])

    def test_forward_model_identity_changes_provenance_and_null_control_has_no_signal(self) -> None:
        scenario = SyntheticScenario("model-control", seed=42, signal_amplitude=1.0)
        illustrative = generate_observation(scenario)
        null = generate_observation(scenario, NullSignalModel())
        candidate = detect(null, BaselineMatchedFilter())

        self.assertNotEqual(illustrative.payload_digest, null.payload_digest)
        self.assertNotEqual(
            illustrative.provenance.configuration_digest,
            null.provenance.configuration_digest,
        )
        self.assertEqual("null-signal-model/0.1.0", null.provenance.generator_version)
        self.assertTrue(null.provenance.model_card_digest)
        self.assertFalse(candidate.detected)


if __name__ == "__main__":
    unittest.main()
