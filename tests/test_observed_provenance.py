from __future__ import annotations

from datetime import datetime, timezone
import unittest

from heimdall.domain import EvidenceClass, Provenance


class ObservedProvenanceTests(unittest.TestCase):
    def test_observed_record_requires_raw_artifact_and_manifest_lineage(self) -> None:
        with self.assertRaisesRegex(ValueError, "raw artifact"):
            Provenance(
                EvidenceClass.OBSERVED, "observed-001", "decoder/1", "config", "model", datetime(2026, 1, 1, tzinfo=timezone.utc)
            )
        provenance = Provenance(
            EvidenceClass.OBSERVED, "observed-001", "decoder/1", "config", "model", datetime(2026, 1, 1, tzinfo=timezone.utc),
            "artifact-digest", "manifest-digest",
        )
        self.assertEqual("artifact-digest", provenance.source_artifact_digest)

    def test_synthetic_record_remains_explicitly_non_observed(self) -> None:
        provenance = Provenance(
            EvidenceClass.SYNTHETIC, "synthetic-001", "generator/1", "config", "model", datetime(2026, 1, 1, tzinfo=timezone.utc)
        )
        self.assertEqual("", provenance.source_manifest_digest)


if __name__ == "__main__":
    unittest.main()
