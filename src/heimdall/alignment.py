"""Explicit and conservative time alignment for external context.

External context can annotate a scientific observation only after a reviewed time
contract declares how provider timestamps are interpreted. The default is to
refuse alignment rather than silently assume UTC.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from json import dumps
from typing import Protocol, Sequence

from .context import ExternalContextRecord
from .domain import ObservationL0


class TimeBasis(str, Enum):
    UTC = "utc"
    PROVIDER_UNVERIFIED = "provider_unverified"


@dataclass(frozen=True)
class SourceTimeContract:
    contract_id: str
    source_id: str
    basis: TimeBasis
    maximum_uncertainty_seconds: float
    authority_reference: str
    approved: bool

    def __post_init__(self) -> None:
        if not all((self.contract_id, self.source_id, self.authority_reference)):
            raise ValueError("time contract identifiers and authority reference are required")
        if self.maximum_uncertainty_seconds < 0:
            raise ValueError("time uncertainty must be non-negative")

    @property
    def digest(self) -> str:
        value = asdict(self)
        value["basis"] = self.basis.value
        return sha256(dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


class ContextTimeInterpreter(Protocol):
    def interpret(self, record: ExternalContextRecord, contract: SourceTimeContract) -> datetime:
        """Return a timezone-aware context time or reject the contract."""


class IsoUtcTimeInterpreter:
    """Strict ISO parser used only for explicitly approved UTC contracts."""

    def interpret(self, record: ExternalContextRecord, contract: SourceTimeContract) -> datetime:
        if not contract.approved:
            raise ValueError("time contract is not approved")
        if contract.basis is not TimeBasis.UTC:
            raise ValueError("time basis is not approved for UTC alignment")
        value = datetime.fromisoformat(record.reported_time_tag.replace("Z", "+00:00"))
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class ContextAlignmentPolicy:
    policy_id: str
    maximum_time_offset_seconds: float

    def __post_init__(self) -> None:
        if not self.policy_id or self.maximum_time_offset_seconds < 0:
            raise ValueError("alignment policy is invalid")


@dataclass(frozen=True)
class ContextAlignment:
    alignment_id: str
    observation_id: str
    context_id: str
    source_id: str
    time_offset_seconds: float
    policy_id: str
    time_contract_digest: str

    @property
    def digest(self) -> str:
        return sha256(dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def align_nearest_context(
    observation: ObservationL0,
    records: Sequence[ExternalContextRecord],
    contract: SourceTimeContract,
    policy: ContextAlignmentPolicy,
    interpreter: ContextTimeInterpreter,
) -> ContextAlignment | None:
    if observation.provenance.evidence_class.value == "observed":
        raise ValueError("observed data alignment requires a separate reviewed use case")
    eligible = [record for record in records if record.source_id == contract.source_id]
    if not eligible:
        return None

    nearest: tuple[ExternalContextRecord, float] | None = None
    for record in eligible:
        context_time = interpreter.interpret(record, contract)
        offset = abs((context_time - observation.started_at).total_seconds())
        if nearest is None or offset < nearest[1]:
            nearest = (record, offset)
        elif nearest is not None and offset == nearest[1]:
            raise ValueError("ambiguous nearest context record")

    if nearest is None or nearest[1] > policy.maximum_time_offset_seconds:
        return None
    record, offset = nearest
    key = f"{observation.observation_id}:{record.context_id}:{policy.policy_id}:{contract.digest}".encode()
    return ContextAlignment(
        alignment_id=f"alignment-{sha256(key).hexdigest()[:20]}",
        observation_id=observation.observation_id,
        context_id=record.context_id,
        source_id=record.source_id,
        time_offset_seconds=offset,
        policy_id=policy.policy_id,
        time_contract_digest=contract.digest,
    )

