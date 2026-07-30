from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.corpus_custody import JsonlCorpusConsumptionLedger, build_corpus_manifest
from heimdall.domain import DatasetSplit
from heimdall.governance import ExperimentPlan, PlanStatus, ThresholdPolicy, sealed_now
from heimdall.pipeline import BaselineMatchedFilter, ClockQualityGate, PeakContrastGate
from heimdall.registry import reference_registry


def plan() -> ExperimentPlan:
    detector = BaselineMatchedFilter()
    gates = (PeakContrastGate(), ClockQualityGate())
    return ExperimentPlan(
        plan_id="custody-test-plan",
        hypothesis="test custody",
        registry_version="synthetic-registry/0.2.0",
        policy=ThresholdPolicy(
            detector.threshold_policy_id, "0.1.0", detector.threshold,
            tuple(gate.gate_id for gate in gates), "test only",
        ),
        detector_id=detector.detector_id,
        detector_version=detector.detector_version,
        status=PlanStatus.SEALED,
        sealed_at=sealed_now(),
    )


class CorpusCustodyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.locked = tuple(
            item for item in reference_registry()
            if item.split is DatasetSplit.LOCKED_VALIDATION
        )

    def test_fresh_independently_held_corpus_can_be_consumed_once(self) -> None:
        corpus = build_corpus_manifest(
            "fresh-corpus", self.locked, "independent custodian test fixture", True, True
        )
        with TemporaryDirectory() as directory:
            ledger = JsonlCorpusConsumptionLedger(Path(directory) / "consumption.jsonl")
            event = ledger.consume(corpus, plan())
            self.assertEqual(corpus.digest, event.corpus_digest)
            with self.assertRaisesRegex(ValueError, "already"):
                ledger.consume(corpus, plan())

    def test_nonfresh_or_nonindependent_corpus_is_refused(self) -> None:
        corpus = build_corpus_manifest(
            "consumed-demo", self.locked, "in-repository fixture", False, False
        )
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "fresh independently"):
                JsonlCorpusConsumptionLedger(Path(directory) / "ledger.jsonl").consume(corpus, plan())


if __name__ == "__main__":
    unittest.main()

