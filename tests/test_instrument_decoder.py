from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from unittest import TestCase

from heimdall.domain import EvidenceClass
from heimdall.ingestion import AcquisitionManifest, IntegrityVerification
from heimdall.instrument_decoder import DecodedWaveform, decode_verified_instrument_frame
from heimdall.instrument_ingestion import SignedInstrumentFrame


class FakeDecoder:
    decoder_id = "fixture-decoder"
    decoder_version = "1.0.0"

    def decode(self, _frame: SignedInstrumentFrame) -> DecodedWaveform:
        return DecodedWaveform((1.0, -1.0), 1024, "sensor-001", 5.0, "certificate-001")


def frame() -> SignedInstrumentFrame:
    return SignedInstrumentFrame(
        "instrument-source", "node-001", "serial-001", datetime(2026, 1, 1, tzinfo=timezone.utc),
        b"raw frame", "application/octet-stream", "heimdall-frame/1", 3, b"signature", "key-001",
    )


def manifest(frame_value: SignedInstrumentFrame) -> AcquisitionManifest:
    return AcquisitionManifest(
        "instrument-source", EvidenceClass.OBSERVED, frame_value.payload_digest, len(frame_value.payload), "frame",
        frame_value.media_type, frame_value.acquired_at,
        IntegrityVerification("detached_signature", "proof", frame_value.payload_digest),
        "instrument://node-001/serial-001",
        {
            "node_id": "node-001", "instrument_serial": "serial-001", "signer_key_id": "key-001",
            "signature_digest": frame_value.signature_digest, "schema_id": "heimdall-frame/1", "sequence_number": "3",
        },
    )


class InstrumentDecoderTests(TestCase):
    def test_decoder_binds_observed_l0_to_exact_raw_manifest(self) -> None:
        frame_value = frame()
        observation = decode_verified_instrument_frame(frame_value, manifest(frame_value), FakeDecoder(), "decoder-config")
        self.assertEqual(EvidenceClass.OBSERVED, observation.provenance.evidence_class)
        self.assertEqual(frame_value.payload_digest, observation.provenance.source_artifact_digest)
        self.assertEqual(3, observation.sequence_number)

    def test_decoder_rejects_mismatched_manifest_security_metadata(self) -> None:
        frame_value = frame()
        invalid = manifest(frame_value)
        invalid_metadata = {**invalid.transport_metadata, "schema_id": "other"}
        invalid = AcquisitionManifest(
            invalid.source_id, invalid.evidence_class, invalid.artifact_digest, invalid.byte_count, invalid.original_name,
            invalid.media_type, invalid.retrieved_at, invalid.verification, invalid.origin_uri, invalid_metadata,
        )
        with self.assertRaisesRegex(ValueError, "security metadata"):
            decode_verified_instrument_frame(frame_value, invalid, FakeDecoder(), "decoder-config")


if __name__ == "__main__":
    import unittest
    unittest.main()
