"""Read-only research-status snapshot derived from governed project records."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from json import dumps, loads
from pathlib import Path
from typing import Sequence

from .model_registry import JsonModelRegistry
from .source_registry import JsonSourceRegistry
from .gate_review import load_gate_reviews
from .claims import load_claims
from .model_admission import load_physics_model_admissions


@dataclass(frozen=True)
class StatusSource:
    id: str
    evidence_class: str
    purpose: str
    status: str
    limitation: str


@dataclass(frozen=True)
class StatusGate:
    stage: str
    status: str
    condition: str


@dataclass(frozen=True)
class StatusClaim:
    statement: str
    scope: str
    status: str
    limitation: str


@dataclass(frozen=True)
class ResearchStatusSnapshot:
    generated_at: str
    scientific_status: str
    limitation: str
    sources: tuple[StatusSource, ...]
    gates: tuple[StatusGate, ...]
    claims: tuple[StatusClaim, ...]

    def to_ui_json(self) -> str:
        return dumps({
            "generatedAt": self.generated_at,
            "scientificStatus": self.scientific_status,
            "limitation": self.limitation,
            "sources": [asdict(source) for source in self.sources],
            "gates": [asdict(gate) for gate in self.gates],
            "claims": [asdict(claim) for claim in self.claims],
        }, indent=2) + "\n"


def build_snapshot(root: Path, generated_at: datetime | None = None) -> ResearchStatusSnapshot:
    registry = JsonSourceRegistry(root / "config" / "sources" / "registered_sources.json")
    source_document = loads((root / "config" / "sources" / "registered_sources.json").read_text())
    configured_sources = []
    for item in source_document["sources"]:
        registered = registry.resolve(str(item["source_id"]))
        purpose = ", ".join(value.value for value in registered.permitted_purposes)
        configured_sources.append(StatusSource(
            id=registered.source.source_id,
            evidence_class=", ".join(value.value for value in registered.source.allowed_evidence_classes),
            purpose=purpose,
            status="active" if registered.source.approved else "inactive",
            limitation=registered.time_contract_status,
        ))

    model_document = loads((root / "config" / "models" / "model_cards.json").read_text())
    model_registry = JsonModelRegistry(root / "config" / "models" / "model_cards.json")
    fixture_cards = [
        model_registry.resolve(str(item["model_id"]), str(item["model_version"]))
        for item in model_document["models"]
    ]
    admissions = load_physics_model_admissions(root)
    configured_sources.append(StatusSource(
        id="synthetic forward-model registry",
        evidence_class="synthetic",
        purpose="development and locked-fixture evaluation",
        status="active",
        limitation=(
            f"{len(fixture_cards)} registered model cards; all are fixture_only and "
            f"cannot support physical or flight claims; {len(admissions)} physics-model admissions"
        ),
    ))

    calibration_document = loads((root / "config" / "research" / "calibration_certificates.json").read_text())
    certificates = calibration_document.get("certificates", [])
    configured_sources.append(StatusSource(
        id="calibration certificate registry",
        evidence_class="laboratory, observed",
        purpose="traceable L0-to-L1 measurement-chain calibration",
        status="active" if certificates else "inactive",
        limitation=str(calibration_document["status"]),
    ))

    gate_document = loads((root / "config" / "research" / "gates.json").read_text())
    gates = tuple(
        StatusGate(
            stage=review.stage,
            status=review.status.value,
            condition=f"{review.condition} Limitation: {review.limitation}",
        )
        for review in load_gate_reviews(root)
    )
    claims = tuple(
        StatusClaim(
            statement=claim.statement,
            scope=claim.scope.value,
            status=claim.status.value,
            limitation=claim.limitation,
        )
        for claim in load_claims(root)
    )
    stamp = generated_at or datetime.now(timezone.utc)
    return ResearchStatusSnapshot(
        generated_at=stamp.isoformat().replace("+00:00", "Z"),
        scientific_status=str(gate_document["scientific_status"]),
        limitation=str(gate_document["limitation"]),
        sources=tuple(configured_sources),
        gates=gates,
        claims=claims,
    )
