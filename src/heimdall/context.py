"""Schema-validated external environmental context derived from preserved bytes.

Context records are annotations for analysis stratification. They are never
candidate labels, primary measurements, or debris truth.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from typing import Protocol, Sequence

from .domain import EvidenceClass


@dataclass(frozen=True)
class ExternalContextRecord:
    context_id: str
    source_id: str
    source_manifest_digest: str
    source_artifact_digest: str
    parser_id: str
    parser_version: str
    reported_time_tag: str
    time_interpretation: str
    variable_id: str
    value: float
    unit: str
    provider_qualifier: str

    def __post_init__(self) -> None:
        if not all((
            self.context_id, self.source_id, self.source_manifest_digest,
            self.source_artifact_digest, self.parser_id, self.parser_version,
            self.reported_time_tag, self.time_interpretation, self.variable_id,
            self.unit,
        )):
            raise ValueError("context record fields are required")


class ContextParser(Protocol):
    def parse(
        self,
        payload: bytes,
        *,
        source_id: str,
        source_manifest_digest: str,
        source_artifact_digest: str,
        evidence_class: EvidenceClass,
    ) -> Sequence[ExternalContextRecord]:
        """Parse a preserved external-context artifact without reclassifying it."""


@dataclass(frozen=True)
class NoaaPlanetaryKIndexParser:
    parser_id: str = "noaa-swpc-planetary-k-index-parser"
    parser_version: str = "0.1.0"

    def parse(
        self,
        payload: bytes,
        *,
        source_id: str,
        source_manifest_digest: str,
        source_artifact_digest: str,
        evidence_class: EvidenceClass,
    ) -> Sequence[ExternalContextRecord]:
        if evidence_class is not EvidenceClass.EXTERNAL_CONTEXT:
            raise ValueError("NOAA context parser accepts external_context artifacts only")
        if source_id != "noaa-swpc-planetary-k-index":
            raise ValueError("unexpected source for NOAA planetary K-index parser")
        data = loads(payload.decode("utf-8"))
        if not isinstance(data, list) or not data:
            raise ValueError("expected NOAA K-index JSON list")
        records = []
        for index, item in enumerate(data):
            if not isinstance(item, dict) or not {"time_tag", "kp_index", "estimated_kp", "kp"} <= item.keys():
                raise ValueError(f"record {index} does not match expected NOAA K-index fields")
            value = float(item["estimated_kp"])
            if not 0.0 <= value <= 9.0:
                raise ValueError(f"record {index} has a K-index outside [0, 9]")
            raw_time = str(item["time_tag"])
            if "T" not in raw_time:
                raise ValueError(f"record {index} does not contain an ISO-like provider time tag")
            context_key = (
                f"{source_manifest_digest}:{self.parser_version}:{index}:{raw_time}:{value}"
            ).encode("utf-8")
            records.append(ExternalContextRecord(
                context_id=f"context-{sha256(context_key).hexdigest()[:20]}",
                source_id=source_id,
                source_manifest_digest=source_manifest_digest,
                source_artifact_digest=source_artifact_digest,
                parser_id=self.parser_id,
                parser_version=self.parser_version,
                reported_time_tag=raw_time,
                time_interpretation="provider time tag preserved; UTC conversion not asserted by this parser",
                variable_id="geomagnetic.planetary_k_index",
                value=value,
                unit="K-index",
                provider_qualifier=str(item["kp"]),
            ))
        return tuple(records)


class ContextStore(Protocol):
    def append(self, records: Sequence[ExternalContextRecord]) -> int:
        """Append derived records without replacing their parent artifact."""


class JsonlContextStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, records: Sequence[ExternalContextRecord]) -> int:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            for record in records:
                stream.write(dumps(asdict(record), sort_keys=True, separators=(",", ":")) + "\n")
        return len(records)
