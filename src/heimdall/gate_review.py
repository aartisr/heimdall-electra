"""Evidence-backed stage-gate review model.

A complete gate is a governance assertion, not an automated proof of scientific
truth. This module ensures that asserted completion cites existing evidence and
a stated limitation before it reaches the project status read model.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from json import loads
from pathlib import Path
from typing import Sequence


class GateStatus(str, Enum):
    COMPLETE = "complete"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class GateReview:
    gate_id: str
    stage: str
    status: GateStatus
    condition: str
    evidence_references: tuple[str, ...]
    limitation: str

    def __post_init__(self) -> None:
        if not all((self.gate_id, self.stage, self.condition, self.limitation)):
            raise ValueError("gate review metadata is required")
        if self.status is GateStatus.COMPLETE and not self.evidence_references:
            raise ValueError("a complete gate requires evidence references")


def load_gate_reviews(root: Path) -> tuple[GateReview, ...]:
    document = loads((root / "config" / "research" / "gates.json").read_text(encoding="utf-8"))
    reviews = []
    for item in document["gates"]:
        review = GateReview(
            gate_id=str(item["gate_id"]),
            stage=str(item["stage"]),
            status=GateStatus(str(item["status"])),
            condition=str(item["condition"]),
            evidence_references=tuple(item.get("evidence_references", ())),
            limitation=str(item["limitation"]),
        )
        for reference in review.evidence_references:
            candidate = root / reference
            if not candidate.is_file():
                raise ValueError(f"gate evidence reference does not exist: {reference}")
        reviews.append(review)
    return tuple(reviews)

