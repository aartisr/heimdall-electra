from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.gate_review import GateReview, GateStatus, load_gate_reviews


class GateReviewTests(unittest.TestCase):
    def test_complete_gate_requires_evidence_reference(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires evidence"):
            GateReview(
                "gate", "Stage", GateStatus.COMPLETE, "condition", (), "limitation"
            )

    def test_project_gate_records_resolve_documented_evidence(self) -> None:
        root = Path(__file__).resolve().parents[1]
        reviews = load_gate_reviews(root)
        self.assertTrue(any(review.status is GateStatus.COMPLETE for review in reviews))
        self.assertTrue(all(review.limitation for review in reviews))

    def test_missing_evidence_reference_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "config" / "research"
            path.mkdir(parents=True)
            (path / "gates.json").write_text(
                '{"gates":[{"gate_id":"g","stage":"s","status":"complete",'
                '"condition":"c","limitation":"l","evidence_references":["missing.md"]}]}'
            )
            with self.assertRaisesRegex(ValueError, "does not exist"):
                load_gate_reviews(root)


if __name__ == "__main__":
    unittest.main()

