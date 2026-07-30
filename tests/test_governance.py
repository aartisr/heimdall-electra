from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor
import unittest

from heimdall import (
    BaselineMatchedFilter,
    ClockQualityGate,
    ExperimentPlan,
    JsonlExperimentLedger,
    PeakContrastGate,
    PlanStatus,
    ThresholdPolicy,
    execute_pre_registered_experiment,
    reference_registry,
)
from heimdall.governance import sealed_now


class GovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = BaselineMatchedFilter()
        self.gates = (PeakContrastGate(), ClockQualityGate())
        self.policy = ThresholdPolicy(
            policy_id=self.detector.threshold_policy_id,
            version="0.1.0",
            threshold=self.detector.threshold,
            required_gate_ids=tuple(gate.gate_id for gate in self.gates),
            rationale="test only",
        )

    def test_execution_records_a_verifiable_append_only_chain(self) -> None:
        plan = ExperimentPlan(
            plan_id="test-plan",
            hypothesis="frozen configuration test",
            registry_version="synthetic-registry/0.2.0",
            policy=self.policy,
            detector_id=self.detector.detector_id,
            detector_version=self.detector.detector_version,
            status=PlanStatus.SEALED,
            sealed_at=sealed_now(),
        )
        with TemporaryDirectory() as directory:
            ledger = JsonlExperimentLedger(Path(directory) / "ledger.jsonl")
            result = execute_pre_registered_experiment(
                plan, reference_registry(), self.detector, self.gates, ledger
            )
            self.assertTrue(ledger.verify())
            self.assertTrue(result.ledger_event_digest)
            self.assertEqual(1, result.report.false_positive)
            self.assertEqual(1, result.report.false_negative)

    def test_execution_rejects_post_hoc_threshold_change(self) -> None:
        plan = ExperimentPlan(
            plan_id="threshold-mismatch",
            hypothesis="must reject changed threshold",
            registry_version="synthetic-registry/0.2.0",
            policy=self.policy,
            detector_id=self.detector.detector_id,
            detector_version=self.detector.detector_version,
            status=PlanStatus.SEALED,
            sealed_at=sealed_now(),
        )
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "threshold"):
                execute_pre_registered_experiment(
                    plan,
                    reference_registry(),
                    BaselineMatchedFilter(threshold=0.60),
                    self.gates,
                    JsonlExperimentLedger(Path(directory) / "ledger.jsonl"),
                )

    def test_tampering_breaks_ledger_verification(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.jsonl"
            ledger = JsonlExperimentLedger(path)
            ledger.append("test", {"value": 1})
            path.write_text(path.read_text(encoding="utf-8").replace('"value":1', '"value":2'), encoding="utf-8")
            self.assertFalse(ledger.verify())

    def test_concurrent_appends_remain_a_single_verifiable_chain(self) -> None:
        with TemporaryDirectory() as directory:
            ledger = JsonlExperimentLedger(Path(directory) / "ledger.jsonl")
            with ThreadPoolExecutor(max_workers=8) as executor:
                events = list(executor.map(
                    lambda value: ledger.append("concurrent", {"value": value}), range(24)
                ))
            self.assertEqual(list(range(24)), sorted(event.sequence for event in events))
            self.assertTrue(ledger.verify())


if __name__ == "__main__":
    unittest.main()
