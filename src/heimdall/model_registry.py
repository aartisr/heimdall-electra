"""Versioned model cards and registry for synthetic forward models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from typing import Protocol


class ModelValidityTier(str, Enum):
    FIXTURE_ONLY = "fixture_only"
    ANALYTIC_UNVALIDATED = "analytic_unvalidated"
    LABORATORY_VALIDATED = "laboratory_validated"
    FLIGHT_VALIDATED = "flight_validated"


@dataclass(frozen=True)
class ModelCard:
    model_id: str
    model_version: str
    validity_tier: ModelValidityTier
    purpose: str
    assumptions: tuple[str, ...]
    excluded_claims: tuple[str, ...]
    verification_evidence: tuple[str, ...]
    card_reference: str

    def __post_init__(self) -> None:
        if not all((self.model_id, self.model_version, self.purpose, self.card_reference)):
            raise ValueError("model card identity, purpose, and reference are required")
        if not self.assumptions or not self.excluded_claims:
            raise ValueError("model card requires assumptions and excluded claims")

    @property
    def digest(self) -> str:
        value = asdict(self)
        value["validity_tier"] = self.validity_tier.value
        return sha256(dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


class ModelRegistry(Protocol):
    def resolve(self, model_id: str, model_version: str) -> ModelCard:
        """Resolve the exact model card required for a generated artifact."""


class JsonModelRegistry:
    def __init__(self, path: Path) -> None:
        self.path = path

    def resolve(self, model_id: str, model_version: str) -> ModelCard:
        document = loads(self.path.read_text(encoding="utf-8"))
        cards = document.get("models")
        if not isinstance(cards, list):
            raise ValueError("model registry models must be a list")
        matches = [
            item for item in cards
            if item.get("model_id") == model_id and item.get("model_version") == model_version
        ]
        if len(matches) != 1:
            raise ValueError("model registry must contain exactly one matching card")
        item = matches[0]
        return ModelCard(
            model_id=str(item["model_id"]),
            model_version=str(item["model_version"]),
            validity_tier=ModelValidityTier(str(item["validity_tier"])),
            purpose=str(item["purpose"]),
            assumptions=tuple(item["assumptions"]),
            excluded_claims=tuple(item["excluded_claims"]),
            verification_evidence=tuple(item["verification_evidence"]),
            card_reference=str(item["card_reference"]),
        )


def default_model_registry() -> JsonModelRegistry:
    return JsonModelRegistry(
        Path(__file__).resolve().parents[2] / "config" / "models" / "model_cards.json"
    )

