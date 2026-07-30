"""Plug-in source registration and content-addressed evidence ingestion.

A SHA-256 digest proves byte integrity only when its expected value originates
from a trusted source. It does not prove source identity. Observed evidence
therefore requires a source-approved stronger verifier such as a future verified
signature adapter.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from json import dumps
import os
from pathlib import Path
from typing import Mapping, Protocol

from .domain import EvidenceClass
from .durable_storage import append_durable_line, exclusive_file_lock
from .governance import digest_value


class SourceKind(str, Enum):
    INSTRUMENT = "instrument"
    PARTNER = "partner"
    PUBLIC_ARCHIVE = "public_archive"
    SYNTHETIC_GENERATOR = "synthetic_generator"


@dataclass(frozen=True)
class DataSource:
    source_id: str
    kind: SourceKind
    owner: str
    terms_reference: str
    approved: bool
    allowed_evidence_classes: tuple[EvidenceClass, ...]
    allowed_verification_schemes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all((self.source_id, self.owner, self.terms_reference)):
            raise ValueError("source ID, owner, and terms reference are required")
        if not self.allowed_evidence_classes or not self.allowed_verification_schemes:
            raise ValueError("source must declare evidence classes and verification schemes")


@dataclass(frozen=True)
class IntegrityVerification:
    scheme: str
    proof_reference: str
    expected_digest: str

    def __post_init__(self) -> None:
        if not all((self.scheme, self.proof_reference, self.expected_digest)):
            raise ValueError("integrity verification fields are required")


@dataclass(frozen=True)
class AcquisitionManifest:
    source_id: str
    evidence_class: EvidenceClass
    artifact_digest: str
    byte_count: int
    original_name: str
    media_type: str
    retrieved_at: datetime
    verification: IntegrityVerification
    origin_uri: str = "local://unspecified"
    transport_metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.retrieved_at.tzinfo is None:
            raise ValueError("retrieved_at must be timezone-aware")
        if self.byte_count < 0 or not self.original_name or not self.media_type or not self.origin_uri:
            raise ValueError("artifact manifest is incomplete")

    @property
    def digest(self) -> str:
        return digest_value({
            **asdict(self),
            "evidence_class": self.evidence_class.value,
            "retrieved_at": self.retrieved_at.isoformat(),
            "verification": asdict(self.verification),
            "origin_uri": self.origin_uri,
            "transport_metadata": dict(self.transport_metadata),
        })


class EvidenceStore(Protocol):
    def put(self, payload: bytes) -> str:
        """Persist bytes by content digest without overwriting prior evidence."""

    def read(self, digest: str) -> bytes:
        """Read preserved original bytes."""


class FileEvidenceStore:
    """Content-addressed local adapter; replaceable with object-lock storage."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def put(self, payload: bytes) -> str:
        digest = sha256(payload).hexdigest()
        path = self.root / "objects" / digest[:2] / digest
        path.parent.mkdir(parents=True, exist_ok=True)
        with exclusive_file_lock(path):
            if not path.exists():
                with path.open("xb") as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(stream.fileno())
            elif sha256(path.read_bytes()).hexdigest() != digest:
                raise RuntimeError("content-addressed store contains corrupt bytes for requested digest")
        return digest

    def read(self, digest: str) -> bytes:
        payload = (self.root / "objects" / digest[:2] / digest).read_bytes()
        if sha256(payload).hexdigest() != digest:
            raise RuntimeError("content-addressed store integrity check failed")
        return payload


class ManifestLedger(Protocol):
    def append(self, manifest: AcquisitionManifest) -> str:
        """Append a manifest and return its content digest."""


class JsonlManifestLedger:
    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, manifest: AcquisitionManifest) -> str:
        item: Mapping[str, object] = {
            "source_id": manifest.source_id,
            "evidence_class": manifest.evidence_class.value,
            "artifact_digest": manifest.artifact_digest,
            "byte_count": manifest.byte_count,
            "original_name": manifest.original_name,
            "media_type": manifest.media_type,
            "retrieved_at": manifest.retrieved_at.isoformat(),
            "verification": asdict(manifest.verification),
            "origin_uri": manifest.origin_uri,
            "transport_metadata": dict(manifest.transport_metadata),
            "manifest_digest": manifest.digest,
        }
        with exclusive_file_lock(self.path):
            append_durable_line(self.path, dumps(item, sort_keys=True, separators=(",", ":")) + "\n")
        return manifest.digest


def ingest_bytes(
    payload: bytes,
    source: DataSource,
    evidence_class: EvidenceClass,
    original_name: str,
    media_type: str,
    verification: IntegrityVerification,
    store: EvidenceStore,
    manifest_ledger: ManifestLedger,
    origin_uri: str = "local://unspecified",
    transport_metadata: Mapping[str, str] | None = None,
) -> AcquisitionManifest:
    if not source.approved:
        raise ValueError("source is not approved")
    if evidence_class not in source.allowed_evidence_classes:
        raise ValueError("source is not approved for this evidence class")
    if verification.scheme not in source.allowed_verification_schemes:
        raise ValueError("verification scheme is not approved for this source")

    artifact_digest = sha256(payload).hexdigest()
    if artifact_digest != verification.expected_digest:
        raise ValueError("payload digest does not match expected digest")
    persisted_digest = store.put(payload)
    if persisted_digest != artifact_digest:
        raise RuntimeError("content-addressed store returned an unexpected digest")

    manifest = AcquisitionManifest(
        source_id=source.source_id,
        evidence_class=evidence_class,
        artifact_digest=artifact_digest,
        byte_count=len(payload),
        original_name=original_name,
        media_type=media_type,
        retrieved_at=datetime.now(timezone.utc),
        verification=verification,
        origin_uri=origin_uri,
        transport_metadata=transport_metadata or {},
    )
    manifest_ledger.append(manifest)
    return manifest
