from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.context import JsonlContextStore, NoaaPlanetaryKIndexParser
from heimdall.domain import EvidenceClass


PAYLOAD = (
    b'[{"time_tag":"2026-07-30T00:00:00","kp_index":2,'
    b'"estimated_kp":2.33,"kp":"2+"}]'
)


class ContextParserTests(unittest.TestCase):
    def test_parser_preserves_external_context_lineage_and_time_limit(self) -> None:
        records = NoaaPlanetaryKIndexParser().parse(
            PAYLOAD,
            source_id="noaa-swpc-planetary-k-index",
            source_manifest_digest="manifest-123",
            source_artifact_digest="artifact-456",
            evidence_class=EvidenceClass.EXTERNAL_CONTEXT,
        )
        self.assertEqual(1, len(records))
        self.assertEqual("external_context", EvidenceClass.EXTERNAL_CONTEXT.value)
        self.assertEqual("manifest-123", records[0].source_manifest_digest)
        self.assertEqual("geomagnetic.planetary_k_index", records[0].variable_id)
        self.assertIn("not asserted", records[0].time_interpretation)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "context.jsonl"
            self.assertEqual(1, JsonlContextStore(path).append(records))
            self.assertIn(records[0].context_id, path.read_text())

    def test_parser_refuses_non_context_and_invalid_schema(self) -> None:
        parser = NoaaPlanetaryKIndexParser()
        with self.assertRaisesRegex(ValueError, "external_context"):
            parser.parse(
                PAYLOAD, source_id="noaa-swpc-planetary-k-index",
                source_manifest_digest="m", source_artifact_digest="a",
                evidence_class=EvidenceClass.OBSERVED,
            )
        with self.assertRaisesRegex(ValueError, "expected NOAA"):
            parser.parse(
                b'{}', source_id="noaa-swpc-planetary-k-index",
                source_manifest_digest="m", source_artifact_digest="a",
                evidence_class=EvidenceClass.EXTERNAL_CONTEXT,
            )


if __name__ == "__main__":
    unittest.main()

