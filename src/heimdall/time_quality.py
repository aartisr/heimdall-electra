"""Explicit time-quality checks for signed instrument-frame admission."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol


@dataclass(frozen=True)
class FrameTimePolicy:
    policy_id: str
    maximum_future_skew: timedelta
    maximum_transport_delay: timedelta

    def __post_init__(self) -> None:
        if not self.policy_id or self.maximum_future_skew < timedelta(0) or self.maximum_transport_delay < timedelta(0):
            raise ValueError("frame time policy is invalid")


@dataclass(frozen=True)
class FrameTimeDecision:
    policy_id: str
    received_at: datetime
    transport_delay_seconds: float


class FrameTimeValidator(Protocol):
    def validate(self, acquired_at: datetime) -> FrameTimeDecision:
        """Validate an acquired timestamp against the trusted receive clock."""


class PolicyFrameTimeValidator:
    """Adapter with injectable trusted receive time for deterministic testing/replay."""

    def __init__(self, policy: FrameTimePolicy, receive_time: datetime | None = None) -> None:
        self.policy = policy
        self.receive_time = receive_time

    def validate(self, acquired_at: datetime) -> FrameTimeDecision:
        if acquired_at.tzinfo is None:
            raise ValueError("frame acquisition time must be timezone-aware")
        received_at = self.receive_time or datetime.now(timezone.utc)
        if received_at.tzinfo is None:
            raise ValueError("trusted receive time must be timezone-aware")
        acquired_utc = acquired_at.astimezone(timezone.utc)
        received_utc = received_at.astimezone(timezone.utc)
        if acquired_utc > received_utc + self.policy.maximum_future_skew:
            raise ValueError("frame acquisition time exceeds future-skew policy")
        delay = received_utc - acquired_utc
        if delay > self.policy.maximum_transport_delay:
            raise ValueError("frame transport delay exceeds policy")
        return FrameTimeDecision(self.policy.policy_id, received_utc, delay.total_seconds())
