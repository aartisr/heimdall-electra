from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.model_admission import AdmissionStatus, PhysicsModelAdmission, load_physics_model_admissions, validate_analytic_model_admission
from heimdall.model_registry import ModelCard, ModelValidityTier


class ModelAdmissionTests(unittest.TestCase):
    def _admission(self, status: AdmissionStatus = AdmissionStatus.APPROVED) -> PhysicsModelAdmission:
        return PhysicsModelAdmission(
            model_id="candidate", model_version="1.0.0", status=status,
            model_owner_reference="docs/owner.md", hypothesis_reference="docs/hypothesis.md",
            governing_equation_references=("docs/equations.md",),
            input_contract_reference="docs/input.md", output_semantics_reference="docs/output.md",
            numerical_method_reference="docs/numerics.md",
            verification_case_references=("docs/verification.md",),
            independent_review_reference="docs/review.md", limitations="test-only admission fixture",
        )

    def _card(self, tier: ModelValidityTier = ModelValidityTier.ANALYTIC_UNVALIDATED) -> ModelCard:
        return ModelCard(
            "candidate", "1.0.0", tier, "test", ("test assumption",), ("no flight claim",),
            ("test verification",), "docs/card.md",
        )

    def test_approved_admission_can_bind_analytic_unvalidated_card(self) -> None:
        validate_analytic_model_admission(self._admission(), self._card())

    def test_draft_or_fixture_card_cannot_be_admitted(self) -> None:
        with self.assertRaisesRegex(ValueError, "not approved"):
            validate_analytic_model_admission(self._admission(AdmissionStatus.DRAFT), self._card())
        with self.assertRaisesRegex(ValueError, "analytic-unvalidated"):
            validate_analytic_model_admission(self._admission(), self._card(ModelValidityTier.FIXTURE_ONLY))

    def test_approved_admission_requires_independent_review(self) -> None:
        with self.assertRaisesRegex(ValueError, "independent review"):
            PhysicsModelAdmission(
                model_id="candidate", model_version="1.0.0", status=AdmissionStatus.APPROVED,
                model_owner_reference="owner", hypothesis_reference="hypothesis",
                governing_equation_references=("equations",), input_contract_reference="input",
                output_semantics_reference="output", numerical_method_reference="method",
                verification_case_references=("verification",), independent_review_reference=None,
                limitations="test",
            )

    def test_project_has_no_admitted_physics_model(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((), load_physics_model_admissions(root))

    def test_loader_rejects_missing_reference(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config" / "models"
            config.mkdir(parents=True)
            (config / "physics_model_admissions.json").write_text(
                '{"admissions":[{"model_id":"x","model_version":"1","status":"draft",'
                '"model_owner_reference":"missing.md","hypothesis_reference":"missing.md",'
                '"governing_equation_references":[],"input_contract_reference":"missing.md",'
                '"output_semantics_reference":"missing.md","numerical_method_reference":"missing.md",'
                '"verification_case_references":[],"limitations":"test"}]}', encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "does not exist"):
                load_physics_model_admissions(root)


if __name__ == "__main__":
    unittest.main()
