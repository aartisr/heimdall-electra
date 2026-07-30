from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import unittest

from heimdall.status_snapshot import build_snapshot


class StatusSnapshotTests(unittest.TestCase):
    def test_snapshot_is_derived_from_governed_registries(self) -> None:
        root = Path(__file__).resolve().parents[1]
        snapshot = build_snapshot(root, datetime(2026, 7, 30, tzinfo=timezone.utc))

        self.assertEqual("2026-07-30T00:00:00Z", snapshot.generated_at)
        self.assertTrue(any(source.id == "noaa-swpc-planetary-k-index" for source in snapshot.sources))
        self.assertTrue(any(source.id == "synthetic forward-model registry" for source in snapshot.sources))
        self.assertTrue(any(source.id == "calibration certificate registry" for source in snapshot.sources))
        model_registry = next(source for source in snapshot.sources if source.id == "synthetic forward-model registry")
        self.assertIn("fixture_only", model_registry.limitation)
        self.assertTrue(any(gate.status == "blocked" for gate in snapshot.gates))
        self.assertTrue(any(claim.status == "prohibited" for claim in snapshot.claims))
        self.assertIn("generatedAt", snapshot.to_ui_json())


if __name__ == "__main__":
    unittest.main()
