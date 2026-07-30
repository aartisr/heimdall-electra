"""Fail-closed signed-frame ingestion boundary for future Heimdall instruments.

No signature algorithm is embedded here. A deployment supplies a reviewed
SignatureVerifier adapter backed by its approved key-management system. Without
successful verification, no observed evidence is persisted.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Protocol

from .domain import EvidenceClass
from .frame_validation import FramePayloadValidator
from .ingestion import AcquisitionManifest, DataSource, EvidenceStore, IntegrityVerification, ManifestLedger, SourceKind, ingest_bytes
from .replay_protection import ReplayProtector
from .time_quality import FrameTimeValidator


@dataclass(frozen=True)
class SignedInstrumentFrame:
    source_id: str
    node_id: str
    instrument_serial: str
    acquired_at: datetime
    payload: bytes
    media_type: str
    schema_id: str
    sequence_number: int
    signature: bytes
    signer_key_id: str

    def __post_init__(self) -> None:
        if not all((self.source_id, self.node_id, self.instrument_serial, self.media_type, self.schema_id, self.signature, self.signer_key_id)):
            raise ValueError("signed instrument frame metadata and signature are required")
        if self.acquired_at.tzinfo is None or not self.payload or self.sequence_number < 0:
            raise ValueError("frame requires timezone-aware acquisition time and payload")

    @property
    def payload_digest(self) -> str:
        return sha256(self.payload).hexdigest()

    @property
    def signature_digest(self) -> str:
        return sha256(self.signature).hexdigest()


@dataclass(frozen=True)
class SignatureVerificationResult:
    verified: bool
    verifier_id: str
    signer_key_id: str
    verification_reference: str

    def __post_init__(self) -> None:
        if not all((self.verifier_id, self.signer_key_id, self.verification_reference)):
            raise ValueError("signature verification lineage is required")


class SignatureVerifier(Protocol):
    def verify(self, frame: SignedInstrumentFrame) -> SignatureVerificationResult:
        """Verify the frame payload and signature against approved signer material."""


def ingest_verified_instrument_frame(
    frame: SignedInstrumentFrame,
    source: DataSource,
    verifier: SignatureVerifier,
    replay_protector: ReplayProtector,
    time_validator: FrameTimeValidator,
    payload_validator: FramePayloadValidator,
    store: EvidenceStore,
    manifest_ledger: ManifestLedger,
) -> AcquisitionManifest:
    """Persist observed instrument bytes only after exact signature verification."""
    if source.kind is not SourceKind.INSTRUMENT:
        raise ValueError("signed instrument ingestion requires an instrument source")
    if source.source_id != frame.source_id:
        raise ValueError("instrument frame source does not match registered source")
    if EvidenceClass.OBSERVED not in source.allowed_evidence_classes:
        raise ValueError("source is not approved for observed evidence")
    payload_policy_id = payload_validator.validate(frame)
    verification = verifier.verify(frame)
    if not verification.verified:
        raise ValueError("instrument signature verification failed")
    if verification.signer_key_id != frame.signer_key_id:
        raise ValueError("verified signer key does not match frame signer key")
    if "detached_signature" not in source.allowed_verification_schemes:
        raise ValueError("source is not approved for detached signature verification")
    time_quality = time_validator.validate(frame.acquired_at)
    stream_id = f"{frame.source_id}:{frame.node_id}:{frame.instrument_serial}:{frame.signer_key_id}"
    replay = replay_protector.accept(stream_id, frame.sequence_number)
    return ingest_bytes(
        payload=frame.payload,
        source=source,
        evidence_class=EvidenceClass.OBSERVED,
        original_name=f"{frame.node_id}-{frame.instrument_serial}-{frame.acquired_at.isoformat()}",
        media_type=frame.media_type,
        verification=IntegrityVerification(
            scheme="detached_signature",
            proof_reference=verification.verification_reference,
            expected_digest=frame.payload_digest,
        ),
        store=store,
        manifest_ledger=manifest_ledger,
        origin_uri=f"instrument://{frame.node_id}/{frame.instrument_serial}",
        transport_metadata={
            "acquired_at": frame.acquired_at.isoformat(),
            "node_id": frame.node_id,
            "instrument_serial": frame.instrument_serial,
            "sequence_number": str(frame.sequence_number),
            "sequence_gap": str(replay.gap),
            "time_policy_id": time_quality.policy_id,
            "received_at": time_quality.received_at.isoformat(),
            "transport_delay_seconds": str(time_quality.transport_delay_seconds),
            "schema_id": frame.schema_id,
            "payload_policy_id": payload_policy_id,
            "signer_key_id": frame.signer_key_id,
            "signature_digest": frame.signature_digest,
            "verifier_id": verification.verifier_id,
        },
    )
