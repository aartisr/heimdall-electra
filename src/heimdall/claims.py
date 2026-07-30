"""Machine-checkable claim boundaries for research communications.

The registry prevents software artifacts from silently becoming stronger
scientific or operational claims. It validates only declared process rules;
it does not establish truth, peer review, or regulatory approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from json import loads
from pathlib import Path

from .domain import EvidenceClass


class ClaimStatus(str, Enum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    PROHIBITED = "prohibited"


class ClaimScope(str, Enum):
    SOFTWARE = "software"
    SCIENTIFIC = "scientific"
    OBSERVED_DETECTION = "observed_detection"
    OPERATIONAL = "operational"


@dataclass(frozen=True)
class ResearchClaim:
    claim_id: str
    statement: str
    scope: ClaimScope
    status: ClaimStatus
    evidence_classes: tuple[EvidenceClass, ...]
    evidence_references: tuple[str, ...]
    limitation: str
    independent_review_reference: str | None = None

    def __post_init__(self) -> None:
        if not all((self.claim_id, self.statement, self.limitation)):
            raise ValueError("claim ID, statement, and limitation are required")
        if self.status is ClaimStatus.SUPPORTED and not self.evidence_references:
            raise ValueError("a supported claim requires evidence references")
        if self.status is ClaimStatus.SUPPORTED and not self.evidence_classes:
            raise ValueError("a supported claim requires evidence classes")
        if self.scope in (ClaimScope.OBSERVED_DETECTION, ClaimScope.OPERATIONAL):
            if self.status is ClaimStatus.SUPPORTED and not self.independent_review_reference:
                raise ValueError("observed or operational supported claims require independent review")
        if self.status is ClaimStatus.SUPPORTED and EvidenceClass.SYNTHETIC in self.evidence_classes:
            if self.scope is not ClaimScope.SOFTWARE:
                raise ValueError("synthetic evidence may support software claims only")


def load_claims(root: Path) -> tuple[ResearchClaim, ...]:
    document = loads((root / "config" / "research" / "claims.json").read_text(encoding="utf-8"))
    claims = []
    for item in document["claims"]:
        claim = ResearchClaim(
            claim_id=str(item["claim_id"]),
            statement=str(item["statement"]),
            scope=ClaimScope(str(item["scope"])),
            status=ClaimStatus(str(item["status"])),
            evidence_classes=tuple(EvidenceClass(value) for value in item.get("evidence_classes", ())),
            evidence_references=tuple(str(value) for value in item.get("evidence_references", ())),
            limitation=str(item["limitation"]),
            independent_review_reference=item.get("independent_review_reference"),
        )
        for reference in claim.evidence_references:
            if not (root / reference).is_file():
                raise ValueError(f"claim evidence reference does not exist: {reference}")
        if claim.independent_review_reference and not (root / claim.independent_review_reference).is_file():
            raise ValueError("claim independent review reference does not exist")
        claims.append(claim)
    return tuple(claims)
