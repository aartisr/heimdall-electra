"""HTTPS-only ingestion of official external context.

This connector validates HTTPS transport and configured host allowlists. It does
not prove the provider's content was signed, and it can never emit OBSERVED
Heimdall evidence. Its sole result class is EXTERNAL_CONTEXT.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .domain import EvidenceClass
from .ingestion import (
    AcquisitionManifest,
    DataSource,
    EvidenceStore,
    IntegrityVerification,
    ManifestLedger,
    ingest_bytes,
)


@dataclass(frozen=True)
class OfficialEndpoint:
    endpoint_id: str
    source_id: str
    uri: str
    allowed_hosts: tuple[str, ...]
    max_bytes: int
    media_type: str = "application/json"

    def __post_init__(self) -> None:
        parsed = urlparse(self.uri)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("official endpoint must use HTTPS with a hostname")
        if parsed.hostname not in self.allowed_hosts:
            raise ValueError("endpoint host must be allow-listed")
        if self.max_bytes <= 0:
            raise ValueError("max_bytes must be positive")


@dataclass(frozen=True)
class TransportReceipt:
    final_uri: str
    retrieved_at: datetime
    content_type: str
    payload: bytes

    def __post_init__(self) -> None:
        if self.retrieved_at.tzinfo is None:
            raise ValueError("retrieved_at must be timezone-aware")


class ContextConnector(Protocol):
    def fetch(self, endpoint: OfficialEndpoint) -> TransportReceipt:
        """Fetch context over an approved transport boundary."""


class HttpsContextConnector:
    """Standard-library HTTPS adapter with redirect-host and size controls."""

    def fetch(self, endpoint: OfficialEndpoint) -> TransportReceipt:
        request = Request(endpoint.uri, headers={"User-Agent": "Heimdall-research/0.1"})
        with urlopen(request, timeout=20) as response:
            final_uri = response.geturl()
            final_host = urlparse(final_uri).hostname
            if urlparse(final_uri).scheme != "https" or final_host not in endpoint.allowed_hosts:
                raise ValueError("redirected outside approved HTTPS host allowlist")
            payload = response.read(endpoint.max_bytes + 1)
            if len(payload) > endpoint.max_bytes:
                raise ValueError("response exceeds endpoint byte limit")
            content_type = response.headers.get_content_type() or endpoint.media_type
            if content_type != endpoint.media_type:
                raise ValueError("response media type does not match approved endpoint contract")
            return TransportReceipt(
                final_uri=final_uri,
                retrieved_at=datetime.now(timezone.utc),
                content_type=content_type,
                payload=payload,
            )


def ingest_external_context(
    endpoint: OfficialEndpoint,
    source: DataSource,
    connector: ContextConnector,
    store: EvidenceStore,
    manifest_ledger: ManifestLedger,
) -> AcquisitionManifest:
    if source.source_id != endpoint.source_id:
        raise ValueError("endpoint source does not match registered source")
    receipt = connector.fetch(endpoint)
    payload_digest = sha256(receipt.payload).hexdigest()
    return ingest_bytes(
        payload=receipt.payload,
        source=source,
        evidence_class=EvidenceClass.EXTERNAL_CONTEXT,
        original_name=endpoint.endpoint_id,
        media_type=receipt.content_type,
        verification=IntegrityVerification(
            scheme="https_tls_transport",
            proof_reference=receipt.final_uri,
            expected_digest=payload_digest,
        ),
        store=store,
        manifest_ledger=manifest_ledger,
        origin_uri=receipt.final_uri,
        transport_metadata={
            "transport": "https",
            "retrieved_at": receipt.retrieved_at.isoformat(),
            "verification_limit": "transport-authenticated retrieval; provider content not independently signed",
        },
    )
