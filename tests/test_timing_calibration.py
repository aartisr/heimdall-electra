from __future__ import annotations

import unittest

from heimdall.domain import EvidenceClass
from heimdall.physics_contract import TimeScale
from heimdall.timing_calibration import TimingCalibrationCertificate, calibrate_candidate_time


def certificate() -> TimingCalibrationCertificate:
    return TimingCalibrationCertificate(
        "timing-cert-001", "node-a", TimeScale.TAI, 1000, 2000, 25, 3.0,
        "timing traceability", ("timing evidence",),
    )


class TimingCalibrationTests(unittest.TestCase):
    def test_applies_integer_nanosecond_offset_and_uncertainty(self) -> None:
        candidate = calibrate_candidate_time(
            candidate_id="candidate", observation_id="observation", node_id="node-a", observed_at_ns=1500,
            time_scale=TimeScale.TAI, reported_time_uncertainty_ns=4.0, score=0.9,
            evidence_class=EvidenceClass.SYNTHETIC, source_payload_digest="payload", certificate=certificate(),
        )
        self.assertEqual(1525, candidate.observed_at_ns)
        self.assertEqual(5.0, candidate.time_uncertainty_ns)

    def test_rejects_wrong_node_scale_or_validity_interval(self) -> None:
        arguments = dict(
            candidate_id="candidate", observation_id="observation", node_id="node-a", observed_at_ns=1500,
            time_scale=TimeScale.TAI, reported_time_uncertainty_ns=4.0, score=0.9,
            evidence_class=EvidenceClass.SYNTHETIC, source_payload_digest="payload", certificate=certificate(),
        )
        with self.assertRaisesRegex(ValueError, "does not apply"):
            calibrate_candidate_time(**{**arguments, "node_id": "node-b"})
        with self.assertRaisesRegex(ValueError, "does not apply"):
            calibrate_candidate_time(**{**arguments, "observed_at_ns": 2001})


if __name__ == "__main__":
    unittest.main()
