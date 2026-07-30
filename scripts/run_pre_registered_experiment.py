"""Execute the frozen synthetic reference configuration and emit a ledger record."""

from __future__ import annotations

from argparse import ArgumentParser
from dataclasses import asdict
from datetime import datetime
from json import dumps
from pathlib import Path

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
    sealed_now,
)
from heimdall.audit_bundle import build_audit_bundle, write_audit_bundle


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--audit-bundle", type=Path)
    parser.add_argument(
        "--generated-at",
        help="Timezone-aware ISO-8601 timestamp, required when creating an audit bundle.",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        action="append",
        default=[],
        help="Repository-relative artifact to content-address in the audit bundle; repeatable.",
    )
    args = parser.parse_args()
    if bool(args.audit_bundle) != bool(args.generated_at):
        parser.error("--audit-bundle and --generated-at must be supplied together")

    detector = BaselineMatchedFilter()
    gates = (PeakContrastGate(), ClockQualityGate())
    policy = ThresholdPolicy(
        policy_id=detector.threshold_policy_id,
        version="0.1.0",
        threshold=detector.threshold,
        required_gate_ids=tuple(gate.gate_id for gate in gates),
        rationale="Frozen synthetic reference configuration; no flight use.",
    )
    plan = ExperimentPlan(
        plan_id="synthetic-reference-plan-001",
        hypothesis="The frozen reference pipeline is evaluated without post-hoc tuning.",
        registry_version="synthetic-registry/0.2.0",
        policy=policy,
        detector_id=detector.detector_id,
        detector_version=detector.detector_version,
        status=PlanStatus.SEALED,
        sealed_at=sealed_now(),
    )
    result = execute_pre_registered_experiment(
        plan, reference_registry(), detector, gates, JsonlExperimentLedger(args.ledger)
    )
    output = {
        "scientific_status": "SYNTHETIC RESEARCH ONLY — NOT AN OBSERVED DEBRIS DETECTION",
        "result": asdict(result),
    }
    if args.audit_bundle:
        root = Path(__file__).resolve().parents[1]
        generated_at = datetime.fromisoformat(args.generated_at.replace("Z", "+00:00"))
        ledger = JsonlExperimentLedger(args.ledger)
        try:
            ledger_artifact = args.ledger.resolve().relative_to(root)
        except ValueError:
            parser.error("--ledger must be inside the NASA repository when creating an audit bundle")
        artifacts = [ledger_artifact, *args.artifact]
        bundle = build_audit_bundle(
            repository_root=root,
            generated_at=generated_at,
            plan=plan,
            result=result,
            ledger=ledger,
            scenarios=reference_registry(),
            artifact_paths=artifacts,
        )
        write_audit_bundle(args.audit_bundle, bundle)
        output["audit_bundle"] = {
            "path": str(args.audit_bundle),
            "digest": bundle.digest,
            "claim_boundary": bundle.claim_boundary,
        }
    print(dumps(output, default=str, indent=2))


if __name__ == "__main__":
    main()
