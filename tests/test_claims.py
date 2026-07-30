from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.claims import ClaimScope, ClaimStatus, ResearchClaim, load_claims
from heimdall.domain import EvidenceClass


class ClaimRegistryTests(unittest.TestCase):
    def test_project_claims_keep_observed_and_operational_claims_prohibited(self) -> None:
        root = Path(__file__).resolve().parents[1]
        claims = load_claims(root)
        statuses = {claim.claim_id: claim.status for claim in claims}
        self.assertEqual(ClaimStatus.SUPPORTED, statuses["synthetic-software-controls"])
        self.assertEqual(ClaimStatus.PROHIBITED, statuses["observed-debris-detection"])
        self.assertEqual(ClaimStatus.PROHIBITED, statuses["operational-safety-use"])

    def test_synthetic_evidence_cannot_support_scientific_performance_claim(self) -> None:
        with self.assertRaisesRegex(ValueError, "software claims only"):
            ResearchClaim(
                "invalid", "synthetic validates physics", ClaimScope.SCIENTIFIC, ClaimStatus.SUPPORTED,
                (EvidenceClass.SYNTHETIC,), ("docs/example.md",), "invalid test",
            )

    def test_supported_observed_claim_requires_independent_review(self) -> None:
        with self.assertRaisesRegex(ValueError, "independent review"):
            ResearchClaim(
                "invalid", "observed detection", ClaimScope.OBSERVED_DETECTION, ClaimStatus.SUPPORTED,
                (EvidenceClass.OBSERVED,), ("docs/example.md",), "invalid test",
            )

    def test_missing_claim_evidence_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config" / "research"
            config.mkdir(parents=True)
            (config / "claims.json").write_text(
                '{"claims":[{"claim_id":"x","statement":"x","scope":"software",'
                '"status":"supported","evidence_classes":["synthetic"],'
                '"evidence_references":["missing.md"],"limitation":"x"}]}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "does not exist"):
                load_claims(root)


if __name__ == "__main__":
    unittest.main()
