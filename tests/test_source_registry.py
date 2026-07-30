from __future__ import annotations

from pathlib import Path
import unittest

from heimdall.domain import EvidenceClass
from heimdall.source_registry import JsonSourceRegistry, SourcePurpose


class SourceRegistryTests(unittest.TestCase):
    def test_noaa_record_is_data_driven_and_context_only(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = JsonSourceRegistry(root / "config" / "sources" / "registered_sources.json").resolve(
            "noaa-swpc-planetary-k-index"
        )
        self.assertEqual("source-registry/0.1.0", source.registry_version)
        self.assertEqual((EvidenceClass.EXTERNAL_CONTEXT,), source.source.allowed_evidence_classes)
        self.assertEqual((SourcePurpose.ENVIRONMENTAL_CONTEXT,), source.permitted_purposes)
        self.assertIn("unapproved", source.time_contract_status)
        self.assertEqual(("services.swpc.noaa.gov",), source.endpoint.allowed_hosts)


if __name__ == "__main__":
    unittest.main()

