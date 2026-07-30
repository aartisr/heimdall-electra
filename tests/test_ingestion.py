from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.domain import EvidenceClass
from heimdall.ingestion import (
    DataSource,
    FileEvidenceStore,
    IntegrityVerification,
    JsonlManifestLedger,
    SourceKind,
    ingest_bytes,
)


class IngestionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = DataSource(
            source_id="synthetic-fixture",
            kind=SourceKind.SYNTHETIC_GENERATOR,
            owner="test",
            terms_reference="test fixture",
            approved=True,
            allowed_evidence_classes=(EvidenceClass.SYNTHETIC,),
            allowed_verification_schemes=("sha256",),
        )

    def test_ingestion_preserves_original_bytes_by_digest(self) -> None:
        payload = b"known synthetic test data"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store = FileEvidenceStore(root)
            manifest = ingest_bytes(
                payload,
                self.source,
                EvidenceClass.SYNTHETIC,
                "fixture.bin",
                "application/octet-stream",
                IntegrityVerification("sha256", "test-proof", sha256(payload).hexdigest()),
                store,
                JsonlManifestLedger(root / "manifests.jsonl"),
            )
            self.assertEqual(payload, store.read(manifest.artifact_digest))
            self.assertIn(manifest.digest, (root / "manifests.jsonl").read_text())

    def test_ingestion_refuses_hash_mismatch_and_unapproved_evidence_class(self) -> None:
        payload = b"known synthetic test data"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "digest"):
                ingest_bytes(
                    payload, self.source, EvidenceClass.SYNTHETIC, "fixture.bin",
                    "application/octet-stream",
                    IntegrityVerification("sha256", "test-proof", "not-the-digest"),
                    FileEvidenceStore(root), JsonlManifestLedger(root / "manifests.jsonl"),
                )
            with self.assertRaisesRegex(ValueError, "evidence class"):
                ingest_bytes(
                    payload, self.source, EvidenceClass.OBSERVED, "fixture.bin",
                    "application/octet-stream",
                    IntegrityVerification("sha256", "test-proof", sha256(payload).hexdigest()),
                    FileEvidenceStore(root), JsonlManifestLedger(root / "manifests.jsonl"),
                )

    def test_content_addressed_store_detects_tampered_existing_object(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store = FileEvidenceStore(root)
            digest = store.put(b"original")
            path = root / "objects" / digest[:2] / digest
            path.write_bytes(b"tampered")
            with self.assertRaisesRegex(RuntimeError, "integrity"):
                store.read(digest)
            with self.assertRaisesRegex(RuntimeError, "corrupt"):
                store.put(b"original")


if __name__ == "__main__":
    unittest.main()
