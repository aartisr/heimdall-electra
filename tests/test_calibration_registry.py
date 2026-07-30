from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.calibration_registry import CalibrationCertificate, CalibrationStatus, JsonCalibrationRegistry, calibrate_with_certificate
from heimdall.simulation import SyntheticScenario, generate_observation


def certificate(status: CalibrationStatus = CalibrationStatus.ACTIVE, sensor_id: str = "synthetic-node-001") -> CalibrationCertificate:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return CalibrationCertificate(
        "certificate-001", sensor_id, "electric field", "ADC count", "V/m", 2.0, 0.03,
        start, start + timedelta(days=1000), "docs/traceability.md", ("docs/evidence.md",), status,
    )


class CalibrationRegistryTests(unittest.TestCase):
    def test_traceable_certificate_binds_scale_uncertainty_and_lineage(self) -> None:
        observation = generate_observation(SyntheticScenario("cal-cert", seed=5, signal_amplitude=1.0))
        calibrated = calibrate_with_certificate(observation, certificate())
        self.assertEqual("certificate-001", calibrated.calibration_id)
        self.assertEqual(2.0, calibrated.calibration_scale)
        self.assertIn("certificate_traceable", calibrated.quality_flags)

    def test_rejects_revoked_mismatched_or_expired_certificate(self) -> None:
        observation = generate_observation(SyntheticScenario("cal-invalid", seed=5, signal_amplitude=1.0))
        with self.assertRaisesRegex(ValueError, "not active"):
            calibrate_with_certificate(observation, certificate(CalibrationStatus.REVOKED))
        with self.assertRaisesRegex(ValueError, "sensor"):
            calibrate_with_certificate(observation, certificate(sensor_id="other"))
        expired = CalibrationCertificate(
            "expired", observation.sensor_id, "field", "count", "V/m", 1.0, 0.01,
            datetime(2020, 1, 1, tzinfo=timezone.utc), datetime(2021, 1, 1, tzinfo=timezone.utc),
            "docs/traceability.md", ("docs/evidence.md",), CalibrationStatus.ACTIVE,
        )
        with self.assertRaisesRegex(ValueError, "outside"):
            calibrate_with_certificate(observation, expired)

    def test_registry_rejects_missing_referenced_evidence(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "config" / "research" / "calibration_certificates.json"
            path.parent.mkdir(parents=True)
            path.write_text(
                '{"certificates":[{"certificate_id":"x","sensor_id":"s","measurand":"m",'
                '"input_unit":"a","output_unit":"b","scale":1,"standard_uncertainty_fraction":0.1,'
                '"valid_from":"2026-01-01T00:00:00Z","valid_until":"2027-01-01T00:00:00Z",'
                '"traceability_reference":"docs/missing.md","evidence_references":["docs/missing.md"],'
                '"status":"active"}]}', encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "does not exist"):
                JsonCalibrationRegistry(path).resolve("x")


if __name__ == "__main__":
    unittest.main()
