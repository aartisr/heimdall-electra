from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.audit_bundle import build_audit_bundle, verify_audit_bundle, write_audit_bundle
from heimdall.governance import ExperimentPlan, JsonlExperimentLedger, PlanStatus, ThresholdPolicy, execute_pre_registered_experiment
from heimdall.pipeline import BaselineMatchedFilter, ClockQualityGate, PeakContrastGate
from heimdall.registry import reference_registry


class AuditBundleTests(unittest.TestCase):
    def _run(self, root: Path):
        detector = BaselineMatchedFilter()
        gates = (PeakContrastGate(), ClockQualityGate())
        plan = ExperimentPlan(
            plan_id="bundle-test", hypothesis="test evidence bundle", registry_version="synthetic-registry/0.2.0",
            policy=ThresholdPolicy(detector.threshold_policy_id, "0.1.0", detector.threshold,
                                   tuple(gate.gate_id for gate in gates), "test only"),
            detector_id=detector.detector_id, detector_version=detector.detector_version,
            status=PlanStatus.SEALED, sealed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        ledger = JsonlExperimentLedger(root / "ledger.jsonl")
        result = execute_pre_registered_experiment(plan, reference_registry(), detector, gates, ledger)
        artifact = root / "method.txt"
        artifact.write_text("frozen method", encoding="utf-8")
        return plan, result, ledger, artifact

    def test_bundle_binds_result_ledger_evidence_and_artifacts(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            plan, result, ledger, artifact = self._run(root)
            bundle = build_audit_bundle(
                repository_root=root, generated_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
                plan=plan, result=result, ledger=ledger, scenarios=reference_registry(),
                artifact_paths=(Path("ledger.jsonl"), Path("method.txt")),
            )
            output = root / "audit.json"
            write_audit_bundle(output, bundle)
            self.assertTrue(verify_audit_bundle(output, root))
            self.assertEqual("SYNTHETIC RESEARCH ONLY — NOT AN OBSERVED DEBRIS DETECTION", bundle.claim_boundary)

    def test_verification_detects_modified_artifact(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            plan, result, ledger, artifact = self._run(root)
            bundle = build_audit_bundle(
                repository_root=root, generated_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
                plan=plan, result=result, ledger=ledger, scenarios=reference_registry(),
                artifact_paths=(Path("ledger.jsonl"), Path("method.txt")),
            )
            output = root / "audit.json"
            write_audit_bundle(output, bundle)
            artifact.write_text("modified", encoding="utf-8")
            self.assertFalse(verify_audit_bundle(output, root))

    def test_bundle_rejects_result_not_at_tip_of_ledger(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            plan, result, ledger, _ = self._run(root)
            ledger.append("later_event", {"review": "pending"})
            with self.assertRaisesRegex(ValueError, "latest"):
                build_audit_bundle(
                    repository_root=root, generated_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
                    plan=plan, result=result, ledger=ledger, scenarios=reference_registry(),
                    artifact_paths=(Path("ledger.jsonl"),),
                )


if __name__ == "__main__":
    unittest.main()
