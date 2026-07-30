"""Auditable lifecycle for non-operational inference hypotheses."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HypothesisState(str, Enum):
    ASSOCIATED = "associated"
    INFERRED = "inferred"
    RETRACTED = "retracted"
    REJECTED = "rejected"
    ARCHIVED = "archived"


_ALLOWED_TRANSITIONS = {
    HypothesisState.ASSOCIATED: {HypothesisState.INFERRED, HypothesisState.REJECTED, HypothesisState.ARCHIVED},
    HypothesisState.INFERRED: {HypothesisState.RETRACTED, HypothesisState.REJECTED, HypothesisState.ARCHIVED},
    HypothesisState.RETRACTED: {HypothesisState.ARCHIVED},
    HypothesisState.REJECTED: {HypothesisState.ARCHIVED},
    HypothesisState.ARCHIVED: set(),
}


@dataclass(frozen=True)
class InferenceHypothesis:
    hypothesis_id: str
    association_id: str
    state: HypothesisState
    evidence_references: tuple[str, ...]
    rationale: str
    limitation: str

    def __post_init__(self) -> None:
        if not all((self.hypothesis_id, self.association_id, self.evidence_references, self.rationale, self.limitation)):
            raise ValueError("hypothesis identity, evidence, rationale, and limitation are required")


def transition_hypothesis(
    current: InferenceHypothesis,
    target: HypothesisState,
    evidence_references: tuple[str, ...],
    rationale: str,
) -> InferenceHypothesis:
    if target not in _ALLOWED_TRANSITIONS[current.state]:
        raise ValueError("hypothesis state transition is not permitted")
    if not evidence_references or not rationale:
        raise ValueError("hypothesis transition requires evidence and rationale")
    return InferenceHypothesis(
        current.hypothesis_id, current.association_id, target, evidence_references, rationale,
        "Research inference hypothesis only; not an identified object, operational track, or safety decision.",
    )
