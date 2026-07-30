from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from heimdall.time_quality import FrameTimePolicy, PolicyFrameTimeValidator


class TimeQualityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.received = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        self.validator = PolicyFrameTimeValidator(
            FrameTimePolicy("time/1", timedelta(seconds=10), timedelta(minutes=5)), self.received
        )

    def test_accepts_bounded_delay_and_reports_it(self) -> None:
        decision = self.validator.validate(self.received - timedelta(seconds=30))
        self.assertEqual(30.0, decision.transport_delay_seconds)

    def test_rejects_excessive_future_skew_or_staleness(self) -> None:
        with self.assertRaisesRegex(ValueError, "future-skew"):
            self.validator.validate(self.received + timedelta(seconds=11))
        with self.assertRaisesRegex(ValueError, "transport delay"):
            self.validator.validate(self.received - timedelta(minutes=6))


if __name__ == "__main__":
    unittest.main()
