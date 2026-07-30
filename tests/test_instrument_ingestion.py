from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.domain import EvidenceClass
from heimdall.ingestion import DataSource, FileEvidenceStore, JsonlManifestLedger, SourceKind
from heimdall.instrument_ingestion import SignedInstrumentFrame, SignatureVerificationResult, ingest_verified_instrument_frame
from heimdall.replay_protection import JsonMonotonicReplayProtector, SequencePolicy
from heimdall.frame_validation import FramePayloadPolicy, PolicyFramePayloadValidator
from heimdall.time_quality import FrameTimePolicy, PolicyFrameTimeValidator


class FakeVerifier:
    def __init__(self, verified: bool = True, key_id: str = "key-001") -> None:
        self.verified = verified
        self.key_id = key_id

    def verify(self, _frame: SignedInstrumentFrame) -> SignatureVerificationResult:
        return SignatureVerificationResult(self.verified, "test-verifier", self.key_id, "test-signature-proof")


def source() -> DataSource:
    return DataSource(
        "instrument-source", SourceKind.INSTRUMENT, "test owner", "test terms", True,
        (EvidenceClass.OBSERVED,), ("detached_signature",),
    )


def frame() -> SignedInstrumentFrame:
    return SignedInstrumentFrame(
        "instrument-source", "node-001", "serial-001", datetime(2026, 1, 1, tzinfo=timezone.utc),
        b"raw frame", "application/octet-stream", "heimdall-frame/1", 1, b"signature", "key-001",
    )


def protector(root: Path) -> JsonMonotonicReplayProtector:
    return JsonMonotonicReplayProtector(root / "replay.json", SequencePolicy("test/1", 5))


def time_validator() -> PolicyFrameTimeValidator:
    return PolicyFrameTimeValidator(
        FrameTimePolicy("test-time/1", timedelta(seconds=5), timedelta(hours=1)),
        datetime(2026, 1, 1, 0, 0, 5, tzinfo=timezone.utc),
    )


def payload_validator() -> PolicyFramePayloadValidator:
    return PolicyFramePayloadValidator(FramePayloadPolicy("test-payload/1", ("heimdall-frame/1",), ("application/octet-stream",), 1024))


class InstrumentIngestionTests(unittest.TestCase):
    def test_verified_instrument_frame_preserves_observed_provenance(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = ingest_verified_instrument_frame(
                frame(), source(), FakeVerifier(), protector(root), time_validator(), payload_validator(), FileEvidenceStore(root), JsonlManifestLedger(root / "manifests.jsonl")
            )
            self.assertEqual(EvidenceClass.OBSERVED, manifest.evidence_class)
            self.assertEqual("key-001", manifest.transport_metadata["signer_key_id"])
            self.assertEqual("test-verifier", manifest.transport_metadata["verifier_id"])

    def test_rejects_invalid_signature_key_or_source_policy(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "failed"):
                ingest_verified_instrument_frame(frame(), source(), FakeVerifier(verified=False), protector(root), time_validator(), payload_validator(), FileEvidenceStore(root), JsonlManifestLedger(root / "m.jsonl"))
            with self.assertRaisesRegex(ValueError, "does not match"):
                ingest_verified_instrument_frame(frame(), source(), FakeVerifier(key_id="wrong"), protector(root), time_validator(), payload_validator(), FileEvidenceStore(root), JsonlManifestLedger(root / "m.jsonl"))
            partner = DataSource("instrument-source", SourceKind.PARTNER, "owner", "terms", True, (EvidenceClass.OBSERVED,), ("detached_signature",))
            with self.assertRaisesRegex(ValueError, "instrument source"):
                ingest_verified_instrument_frame(frame(), partner, FakeVerifier(), protector(root), time_validator(), payload_validator(), FileEvidenceStore(root), JsonlManifestLedger(root / "m.jsonl"))

    def test_rejects_replayed_signed_frame(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            guard = protector(root)
            ingest_verified_instrument_frame(frame(), source(), FakeVerifier(), guard, time_validator(), payload_validator(), FileEvidenceStore(root), JsonlManifestLedger(root / "m.jsonl"))
            with self.assertRaisesRegex(ValueError, "replayed"):
                ingest_verified_instrument_frame(frame(), source(), FakeVerifier(), guard, time_validator(), payload_validator(), FileEvidenceStore(root), JsonlManifestLedger(root / "m.jsonl"))

    def test_rejects_unapproved_schema_before_signature_processing(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            unapproved = SignedInstrumentFrame(
                "instrument-source", "node-001", "serial-001", datetime(2026, 1, 1, tzinfo=timezone.utc),
                b"raw", "application/octet-stream", "other/1", 1, b"signature", "key-001",
            )
            with self.assertRaisesRegex(ValueError, "schema"):
                ingest_verified_instrument_frame(unapproved, source(), FakeVerifier(), protector(root), time_validator(), payload_validator(), FileEvidenceStore(root), JsonlManifestLedger(root / "m.jsonl"))


if __name__ == "__main__":
    unittest.main()
