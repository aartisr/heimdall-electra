"""Monotonic anti-replay controls for signed instrument-frame streams.

The local adapter protects cooperating ingestion processes. Its state is not a
substitute for hardware counters or a remotely anchored replay ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from json import dumps, loads
from pathlib import Path
from typing import Protocol

from .durable_storage import atomic_write_text, exclusive_file_lock


@dataclass(frozen=True)
class SequencePolicy:
    policy_id: str
    maximum_forward_gap: int

    def __post_init__(self) -> None:
        if not self.policy_id or self.maximum_forward_gap < 0:
            raise ValueError("sequence policy is invalid")


@dataclass(frozen=True)
class ReplayDecision:
    stream_id: str
    sequence_number: int
    previous_sequence_number: int | None
    gap: int


class ReplayProtector(Protocol):
    def accept(self, stream_id: str, sequence_number: int) -> ReplayDecision:
        """Atomically accept a new sequence number or reject replay/out-of-policy gaps."""


class JsonMonotonicReplayProtector:
    """Durable local sequence adapter with exclusive process locking."""

    def __init__(self, path: Path, policy: SequencePolicy) -> None:
        self.path = path
        self.policy = policy

    def accept(self, stream_id: str, sequence_number: int) -> ReplayDecision:
        if not stream_id or sequence_number < 0:
            raise ValueError("stream ID and non-negative sequence number are required")
        with exclusive_file_lock(self.path):
            state = self._read_state()
            previous = state.get(stream_id)
            if previous is not None and sequence_number <= previous:
                raise ValueError("frame sequence is replayed or out of order")
            gap = 0 if previous is None else sequence_number - previous - 1
            if gap > self.policy.maximum_forward_gap:
                raise ValueError("frame sequence gap exceeds policy")
            state[stream_id] = sequence_number
            atomic_write_text(self.path, dumps({"policy_id": self.policy.policy_id, "streams": state}, sort_keys=True) + "\n")
            return ReplayDecision(stream_id, sequence_number, previous, gap)

    def _read_state(self) -> dict[str, int]:
        if not self.path.exists():
            return {}
        document = loads(self.path.read_text(encoding="utf-8"))
        if document.get("policy_id") != self.policy.policy_id:
            raise ValueError("replay state policy does not match configured policy")
        streams = document.get("streams")
        if not isinstance(streams, dict) or any(not isinstance(value, int) or value < 0 for value in streams.values()):
            raise ValueError("replay state is invalid")
        return dict(streams)
