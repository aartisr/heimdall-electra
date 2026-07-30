from __future__ import annotations

import unittest

from heimdall.inference_lifecycle import HypothesisState, InferenceHypothesis, transition_hypothesis


class InferenceLifecycleTests(unittest.TestCase):
    def test_only_explicit_evidence_backed_transitions_are_allowed(self) -> None:
        hypothesis = InferenceHypothesis("hypothesis", "association", HypothesisState.ASSOCIATED, ("evidence",), "initial", "research only")
        inferred = transition_hypothesis(hypothesis, HypothesisState.INFERRED, ("solver result",), "validated contract")
        retracted = transition_hypothesis(inferred, HypothesisState.RETRACTED, ("counterevidence",), "alternative explanation")
        self.assertEqual(HypothesisState.RETRACTED, retracted.state)
        with self.assertRaisesRegex(ValueError, "not permitted"):
            transition_hypothesis(retracted, HypothesisState.INFERRED, ("evidence",), "retry")

    def test_transition_requires_evidence_and_rationale(self) -> None:
        hypothesis = InferenceHypothesis("hypothesis", "association", HypothesisState.ASSOCIATED, ("evidence",), "initial", "research only")
        with self.assertRaisesRegex(ValueError, "requires"):
            transition_hypothesis(hypothesis, HypothesisState.INFERRED, (), "")


if __name__ == "__main__":
    unittest.main()
