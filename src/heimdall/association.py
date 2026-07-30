"""Evidence-preserving time-gated association for multi-node candidates.

This module forms only a candidate association. It does not estimate position,
velocity, an object identity, or a debris track.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence

from .domain import EvidenceClass
from .physics_contract import TimeScale


@dataclass(frozen=True)
class TimedCandidate:
    candidate_id: str
    observation_id: str
    node_id: str
    observed_at_ns: int
    time_scale: TimeScale
    time_uncertainty_ns: float
    score: float
    evidence_class: EvidenceClass
    source_payload_digest: str

    def __post_init__(self) -> None:
        if not all((self.candidate_id, self.observation_id, self.node_id, self.source_payload_digest)):
            raise ValueError("timed candidate identity and source lineage are required")
        if not isinstance(self.observed_at_ns, int) or self.time_uncertainty_ns < 0 or not 0 <= self.score <= 1:
            raise ValueError("timed candidate time, uncertainty, or score is invalid")


@dataclass(frozen=True)
class AssociationPolicy:
    policy_id: str
    minimum_nodes: int
    minimum_candidate_score: float
    maximum_time_separation_ns: float

    def __post_init__(self) -> None:
        if not self.policy_id or self.minimum_nodes < 2 or not 0 <= self.minimum_candidate_score <= 1:
            raise ValueError("association policy is invalid")
        if self.maximum_time_separation_ns < 0:
            raise ValueError("maximum time separation must be non-negative")


@dataclass(frozen=True)
class CandidateAssociation:
    association_id: str
    policy_id: str
    candidate_ids: tuple[str, ...]
    node_ids: tuple[str, ...]
    evidence_class: EvidenceClass
    time_scale: TimeScale
    maximum_pairwise_time_separation_ns: float
    maximum_pairwise_time_uncertainty_ns: float
    limitation: str


def associate_candidates(
    candidates: Sequence[TimedCandidate],
    policy: AssociationPolicy,
) -> CandidateAssociation:
    """Associate candidates only when all declared evidence and timing bounds agree."""
    if len(candidates) < policy.minimum_nodes:
        raise ValueError("insufficient candidates for association policy")
    if len({candidate.candidate_id for candidate in candidates}) != len(candidates):
        raise ValueError("association candidates must be unique")
    node_ids = {candidate.node_id for candidate in candidates}
    if len(node_ids) < policy.minimum_nodes:
        raise ValueError("association requires candidates from distinct nodes")
    if any(candidate.score < policy.minimum_candidate_score for candidate in candidates):
        raise ValueError("candidate score is below association policy")
    evidence_classes = {candidate.evidence_class for candidate in candidates}
    if len(evidence_classes) != 1:
        raise ValueError("association cannot mix evidence classes")
    time_scales = {candidate.time_scale for candidate in candidates}
    if len(time_scales) != 1:
        raise ValueError("association cannot mix time scales")

    pairwise_separations = []
    pairwise_uncertainties = []
    ordered = tuple(sorted(candidates, key=lambda item: item.candidate_id))
    for index, left in enumerate(ordered):
        for right in ordered[index + 1:]:
            separation_ns = abs(left.observed_at_ns - right.observed_at_ns)
            uncertainty_ns = left.time_uncertainty_ns + right.time_uncertainty_ns
            pairwise_separations.append(separation_ns)
            pairwise_uncertainties.append(uncertainty_ns)
            if separation_ns > policy.maximum_time_separation_ns + uncertainty_ns:
                raise ValueError("candidate timing separation exceeds association policy")

    candidate_ids = tuple(candidate.candidate_id for candidate in ordered)
    digest_input = f"{policy.policy_id}:{':'.join(candidate_ids)}".encode()
    return CandidateAssociation(
        association_id=f"association-{sha256(digest_input).hexdigest()[:20]}",
        policy_id=policy.policy_id,
        candidate_ids=candidate_ids,
        node_ids=tuple(sorted(node_ids)),
        evidence_class=next(iter(evidence_classes)),
        time_scale=next(iter(time_scales)),
        maximum_pairwise_time_separation_ns=max(pairwise_separations, default=0.0),
        maximum_pairwise_time_uncertainty_ns=max(pairwise_uncertainties, default=0.0),
        limitation="Association only; no TDOA/FDOA inversion, localization, object identity, or track claim.",
    )
