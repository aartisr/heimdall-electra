"""Versioned, data-driven approval registry for external Heimdall sources."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from json import loads
from pathlib import Path
from typing import Protocol

from .domain import EvidenceClass
from .ingestion import DataSource, SourceKind
from .remote_context import OfficialEndpoint


class SourcePurpose(str, Enum):
    ENVIRONMENTAL_CONTEXT = "environmental_context"
    DEBRIS_PRIOR = "debris_prior"
    INDEPENDENT_VALIDATION = "independent_validation"
    PRIMARY_MEASUREMENT = "primary_measurement"


@dataclass(frozen=True)
class RegisteredSource:
    registry_version: str
    approval_id: str
    source: DataSource
    endpoint: OfficialEndpoint
    permitted_purposes: tuple[SourcePurpose, ...]
    review_reference: str
    time_contract_status: str

    def __post_init__(self) -> None:
        if not all((
            self.registry_version, self.approval_id, self.review_reference,
            self.time_contract_status,
        )):
            raise ValueError("source registry approval metadata is required")
        if not self.source.approved:
            raise ValueError("registry cannot enable an unapproved source")
        if self.endpoint.source_id != self.source.source_id:
            raise ValueError("source and endpoint IDs must match")
        if not self.permitted_purposes:
            raise ValueError("source must declare at least one permitted purpose")


class SourceRegistry(Protocol):
    def resolve(self, source_id: str) -> RegisteredSource:
        """Return the exact reviewed record required for an integration."""


class JsonSourceRegistry:
    def __init__(self, path: Path) -> None:
        self.path = path

    def resolve(self, source_id: str) -> RegisteredSource:
        document = loads(self.path.read_text(encoding="utf-8"))
        records = document.get("sources")
        if not isinstance(records, list):
            raise ValueError("registry sources must be a list")
        matches = [record for record in records if record.get("source_id") == source_id]
        if len(matches) != 1:
            raise ValueError("source registry must contain exactly one matching source")
        return self._parse(document["registry_version"], matches[0])

    @staticmethod
    def _parse(registry_version: str, item: dict[str, object]) -> RegisteredSource:
        source = DataSource(
            source_id=str(item["source_id"]),
            kind=SourceKind(str(item["kind"])),
            owner=str(item["owner"]),
            terms_reference=str(item["terms_reference"]),
            approved=bool(item["approved"]),
            allowed_evidence_classes=tuple(
                EvidenceClass(value) for value in item["allowed_evidence_classes"]  # type: ignore[index]
            ),
            allowed_verification_schemes=tuple(item["allowed_verification_schemes"]),  # type: ignore[arg-type,index]
        )
        endpoint = OfficialEndpoint(
            endpoint_id=str(item["endpoint_id"]),
            source_id=source.source_id,
            uri=str(item["uri"]),
            allowed_hosts=tuple(item["allowed_hosts"]),  # type: ignore[arg-type,index]
            max_bytes=int(item["max_bytes"]),
            media_type=str(item["media_type"]),
        )
        return RegisteredSource(
            registry_version=registry_version,
            approval_id=str(item["approval_id"]),
            source=source,
            endpoint=endpoint,
            permitted_purposes=tuple(
                SourcePurpose(value) for value in item["permitted_purposes"]  # type: ignore[index]
            ),
            review_reference=str(item["review_reference"]),
            time_contract_status=str(item["time_contract_status"]),
        )

