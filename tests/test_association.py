from __future__ import annotations

import unittest

from heimdall.association import AssociationPolicy, TimedCandidate, associate_candidates
from heimdall.domain import EvidenceClass
from heimdall.physics_contract import TimeScale


def candidate(candidate_id: str, node_id: str, offset_ns: int = 0, evidence: EvidenceClass = EvidenceClass.SYNTHETIC) -> TimedCandidate:
    return TimedCandidate(
        candidate_id, f"observation-{candidate_id}", node_id,
        1_704_067_200_000_000_000 + offset_ns, TimeScale.TAI,
        100.0, 0.9, evidence, f"payload-{candidate_id}",
    )


class AssociationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = AssociationPolicy("association/1", 2, 0.8, 1_000.0)

    def test_association_preserves_evidence_and_explicit_limit(self) -> None:
        result = associate_candidates((candidate("b", "node-b", 500), candidate("a", "node-a")), self.policy)
        self.assertEqual(("a", "b"), result.candidate_ids)
        self.assertEqual(EvidenceClass.SYNTHETIC, result.evidence_class)
        self.assertIn("no TDOA", result.limitation)

    def test_association_rejects_mixed_evidence_same_node_and_excessive_timing(self) -> None:
        with self.assertRaisesRegex(ValueError, "mix"):
            associate_candidates((candidate("a", "node-a"), candidate("b", "node-b", evidence=EvidenceClass.OBSERVED)), self.policy)
        with self.assertRaisesRegex(ValueError, "distinct"):
            associate_candidates((candidate("a", "node-a"), candidate("b", "node-a")), self.policy)
        with self.assertRaisesRegex(ValueError, "separation"):
            associate_candidates((candidate("a", "node-a"), candidate("b", "node-b", 2_000)), self.policy)


if __name__ == "__main__":
    unittest.main()
