from __future__ import annotations

import unittest

from heimdall.association import AssociationPolicy, TimedCandidate, associate_candidates
from heimdall.domain import EvidenceClass
from heimdall.kinematic_inference import NodeGeometry, TdoaInferenceInput, TdoaInferenceResult, TdoaMode, validate_tdoa_result
from heimdall.physics_contract import CoordinateFrame, TimeScale


def candidates() -> tuple[TimedCandidate, ...]:
    return (
        TimedCandidate("a", "oa", "node-a", 1000, TimeScale.TAI, 10, 0.9, EvidenceClass.SYNTHETIC, "pa"),
        TimedCandidate("b", "ob", "node-b", 1050, TimeScale.TAI, 10, 0.9, EvidenceClass.SYNTHETIC, "pb"),
    )


def inference_input() -> TdoaInferenceInput:
    association = associate_candidates(candidates(), AssociationPolicy("association/1", 2, 0.8, 100))
    return TdoaInferenceInput(
        association, candidates(),
        (NodeGeometry("node-a", (0, 0, 0), 1, CoordinateFrame.ECI_J2000), NodeGeometry("node-b", (1, 0, 0), 1, CoordinateFrame.ECI_J2000)),
        CoordinateFrame.ECI_J2000, TimeScale.TAI, "synthetic solver-contract fixture",
    )


class FakeSolver:
    solver_id = "fixture-solver"
    solver_version = "1.0.0"


class KinematicInferenceTests(unittest.TestCase):
    def test_contract_preserves_association_geometry_and_mode_ambiguity(self) -> None:
        value = inference_input()
        result = TdoaInferenceResult(
            value.association.association_id, "fixture-solver", "1.0.0", value.model_assumption_reference,
            (TdoaMode("mode-a", (1, 2, 3), 2.0, (1, 0, 0, 0, 1, 0, 0, 0, 1)), TdoaMode("mode-b", (4, 5, 6), 3.0, (1, 0, 0, 0, 1, 0, 0, 0, 1))),
            "Contract fixture only; not a physical localization.",
        )
        validate_tdoa_result(result, value, FakeSolver())
        self.assertEqual(2, len(result.modes))

    def test_contract_rejects_missing_geometry_or_assumption_lineage(self) -> None:
        value = inference_input()
        with self.assertRaisesRegex(ValueError, "map exactly"):
            TdoaInferenceInput(value.association, value.candidates, (NodeGeometry("node-a", (0, 0, 0), 1, CoordinateFrame.ECI_J2000),), CoordinateFrame.ECI_J2000, TimeScale.TAI, "assumption")
        invalid = TdoaInferenceResult(value.association.association_id, "fixture-solver", "1.0.0", "other", (TdoaMode("mode", (1, 2, 3), 2, (1, 0, 0, 0, 1, 0, 0, 0, 1)),), "limit")
        with self.assertRaisesRegex(ValueError, "assumption"):
            validate_tdoa_result(invalid, value, FakeSolver())


if __name__ == "__main__":
    unittest.main()
