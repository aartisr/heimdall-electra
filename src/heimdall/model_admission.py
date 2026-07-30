"""Controlled admission records for physics-capable forward models.

This module checks whether a proposed analytic model carries the minimum
reviewable documentation. It does not solve plasma physics or certify the
scientific correctness of the supplied materials.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from json import loads
from pathlib import Path

from .model_registry import ModelCard, ModelValidityTier


class AdmissionStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"


@dataclass(frozen=True)
class PhysicsModelAdmission:
    model_id: str
    model_version: str
    status: AdmissionStatus
    model_owner_reference: str
    hypothesis_reference: str
    governing_equation_references: tuple[str, ...]
    input_contract_reference: str
    output_semantics_reference: str
    numerical_method_reference: str
    verification_case_references: tuple[str, ...]
    independent_review_reference: str | None
    limitations: str

    def __post_init__(self) -> None:
        if not all((
            self.model_id, self.model_version, self.model_owner_reference,
            self.hypothesis_reference, self.input_contract_reference,
            self.output_semantics_reference, self.numerical_method_reference,
            self.limitations,
        )):
            raise ValueError("physics-model admission identity and documentation are required")
        if self.status is AdmissionStatus.APPROVED:
            if not self.governing_equation_references or not self.verification_case_references:
                raise ValueError("approved admission requires equations and verification cases")
            if not self.independent_review_reference:
                raise ValueError("approved admission requires independent review")

    @property
    def references(self) -> tuple[str, ...]:
        return tuple(reference for reference in (
            self.model_owner_reference,
            self.hypothesis_reference,
            *self.governing_equation_references,
            self.input_contract_reference,
            self.output_semantics_reference,
            self.numerical_method_reference,
            *self.verification_case_references,
            self.independent_review_reference,
        ) if reference)


def load_physics_model_admissions(root: Path) -> tuple[PhysicsModelAdmission, ...]:
    document = loads((root / "config" / "models" / "physics_model_admissions.json").read_text(encoding="utf-8"))
    admissions = []
    for item in document.get("admissions", []):
        admission = PhysicsModelAdmission(
            model_id=str(item["model_id"]),
            model_version=str(item["model_version"]),
            status=AdmissionStatus(str(item["status"])),
            model_owner_reference=str(item["model_owner_reference"]),
            hypothesis_reference=str(item["hypothesis_reference"]),
            governing_equation_references=tuple(str(value) for value in item.get("governing_equation_references", ())),
            input_contract_reference=str(item["input_contract_reference"]),
            output_semantics_reference=str(item["output_semantics_reference"]),
            numerical_method_reference=str(item["numerical_method_reference"]),
            verification_case_references=tuple(str(value) for value in item.get("verification_case_references", ())),
            independent_review_reference=item.get("independent_review_reference"),
            limitations=str(item["limitations"]),
        )
        _verify_references(root, admission.references)
        admissions.append(admission)
    return tuple(admissions)


def validate_analytic_model_admission(admission: PhysicsModelAdmission, card: ModelCard) -> None:
    """Reject a model-card promotion unless an approved admission binds it."""
    if admission.status is not AdmissionStatus.APPROVED:
        raise ValueError("physics-model admission is not approved")
    if (admission.model_id, admission.model_version) != (card.model_id, card.model_version):
        raise ValueError("admission identity does not match model card")
    if card.validity_tier is not ModelValidityTier.ANALYTIC_UNVALIDATED:
        raise ValueError("admission workflow may approve analytic-unvalidated tier only")


def _verify_references(root: Path, references: tuple[str, ...]) -> None:
    for reference in references:
        if not (root / reference).is_file():
            raise ValueError(f"physics-model admission reference does not exist: {reference}")
