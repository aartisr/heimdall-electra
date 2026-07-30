from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from heimdall import NOAA_SWPC_PLANETARY_K_INDEX, NOAA_SWPC_PLANETARY_K_INDEX_ENDPOINT
from heimdall.ingestion import FileEvidenceStore, JsonlManifestLedger
from heimdall.remote_context import (
    OfficialEndpoint,
    TransportReceipt,
    ingest_external_context,
)


class FakeConnector:
    def fetch(self, endpoint: OfficialEndpoint) -> TransportReceipt:
        return TransportReceipt(
            final_uri=endpoint.uri,
            retrieved_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
            content_type="application/json",
            payload=b"[{\"time_tag\":\"2026-07-30T00:00:00Z\",\"kp_index\":2.0}]",
        )


class FakeHttpsResponse:
    def __init__(self, content_type: str) -> None:
        self.headers = type("Headers", (), {"get_content_type": lambda _self: content_type})()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def geturl(self) -> str:
        return NOAA_SWPC_PLANETARY_K_INDEX_ENDPOINT.uri

    def read(self, _limit: int) -> bytes:
        return b"[]"


class RemoteContextTests(unittest.TestCase):
    def test_external_context_is_preserved_but_not_labeled_observed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = ingest_external_context(
                NOAA_SWPC_PLANETARY_K_INDEX_ENDPOINT,
                NOAA_SWPC_PLANETARY_K_INDEX,
                FakeConnector(),
                FileEvidenceStore(root),
                JsonlManifestLedger(root / "manifests.jsonl"),
            )
            self.assertEqual("external_context", manifest.evidence_class.value)
            self.assertEqual(NOAA_SWPC_PLANETARY_K_INDEX_ENDPOINT.uri, manifest.origin_uri)
            self.assertIn("provider content not independently signed", manifest.transport_metadata["verification_limit"])

    def test_endpoint_rejects_non_https_or_non_allowlisted_host(self) -> None:
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            OfficialEndpoint("bad", "source", "http://example.test/data", ("example.test",), 1)
        with self.assertRaisesRegex(ValueError, "allow-listed"):
            OfficialEndpoint("bad", "source", "https://other.test/data", ("example.test",), 1)

    def test_https_connector_rejects_unexpected_media_type(self) -> None:
        from heimdall.remote_context import HttpsContextConnector

        with patch("heimdall.remote_context.urlopen", return_value=FakeHttpsResponse("text/html")):
            with self.assertRaisesRegex(ValueError, "media type"):
                HttpsContextConnector().fetch(NOAA_SWPC_PLANETARY_K_INDEX_ENDPOINT)


if __name__ == "__main__":
    unittest.main()
