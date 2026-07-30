"""Reviewed source definitions. These are context feeds, never debris truth."""

from __future__ import annotations

from .domain import EvidenceClass
from .ingestion import DataSource, SourceKind
from .remote_context import OfficialEndpoint


NOAA_SWPC_PLANETARY_K_INDEX = DataSource(
    source_id="noaa-swpc-planetary-k-index",
    kind=SourceKind.PUBLIC_ARCHIVE,
    owner="NOAA Space Weather Prediction Center",
    terms_reference="https://services.swpc.noaa.gov/json/planetary_k_index_1m.json",
    approved=True,
    allowed_evidence_classes=(EvidenceClass.EXTERNAL_CONTEXT,),
    allowed_verification_schemes=("https_tls_transport",),
)

NOAA_SWPC_PLANETARY_K_INDEX_ENDPOINT = OfficialEndpoint(
    endpoint_id="planetary_k_index_1m.json",
    source_id=NOAA_SWPC_PLANETARY_K_INDEX.source_id,
    uri="https://services.swpc.noaa.gov/json/planetary_k_index_1m.json",
    allowed_hosts=("services.swpc.noaa.gov",),
    max_bytes=2_000_000,
)
