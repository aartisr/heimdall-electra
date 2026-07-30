"""Bounded schema and payload admission for instrument frames."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class FrameEnvelope(Protocol):
    schema_id: str
    media_type: str
    payload: bytes


@dataclass(frozen=True)
class FramePayloadPolicy:
    policy_id: str
    allowed_schema_ids: tuple[str, ...]
    allowed_media_types: tuple[str, ...]
    maximum_payload_bytes: int

    def __post_init__(self) -> None:
        if not self.policy_id or not self.allowed_schema_ids or not self.allowed_media_types or self.maximum_payload_bytes <= 0:
            raise ValueError("frame payload policy is incomplete")


class FramePayloadValidator(Protocol):
    def validate(self, frame: FrameEnvelope) -> str:
        """Reject unrecognized or oversized frames and return governing policy ID."""


class PolicyFramePayloadValidator:
    """Basic fail-closed envelope validator; binary decoding remains an adapter seam."""

    def __init__(self, policy: FramePayloadPolicy) -> None:
        self.policy = policy

    def validate(self, frame: FrameEnvelope) -> str:
        if frame.schema_id not in self.policy.allowed_schema_ids:
            raise ValueError("frame schema is not approved")
        if frame.media_type not in self.policy.allowed_media_types:
            raise ValueError("frame media type is not approved")
        if not frame.payload or len(frame.payload) > self.policy.maximum_payload_bytes:
            raise ValueError("frame payload violates configured byte limit")
        return self.policy.policy_id
