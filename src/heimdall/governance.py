"""Pre-registered experiment controls and append-only tamper-evident ledger.

This module provides research-process integrity, not cryptographic non-repudiation.
A production ledger must additionally use externally managed signing keys, access
control, immutable storage, and independent review.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from typing import Mapping, Protocol, Sequence

from .calibration import calibrate
from .durable_storage import append_durable_line, exclusive_file_lock
from .evaluation import DetectionReport, EvaluationRow, evaluate, evaluate_by_stratum
from .pipeline import BaselineMatchedFilter, CandidateGate, detect
from .registry import RegisteredScenario
from .simulation import generate_observation


class PlanStatus(str, Enum):
    SEALED = "sealed"


@dataclass(frozen=True)
class ThresholdPolicy:
    policy_id: str
    version: str
    threshold: float
    required_gate_ids: tuple[str, ...]
    rationale: str

    def __post_init__(self) -> None:
        if not self.policy_id or not self.version or not self.rationale:
            raise ValueError("policy ID, version, and rationale are required")
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("threshold must be normalized")

    @property
    def digest(self) -> str:
        return digest_value(asdict(self))


@dataclass(frozen=True)
class ExperimentPlan:
    plan_id: str
    hypothesis: str
    registry_version: str
    policy: ThresholdPolicy
    detector_id: str
    detector_version: str
    status: PlanStatus
    sealed_at: datetime

    def __post_init__(self) -> None:
        if not all((self.plan_id, self.hypothesis, self.registry_version, self.detector_id, self.detector_version)):
            raise ValueError("plan fields are required")
        if self.status is not PlanStatus.SEALED or self.sealed_at.tzinfo is None:
            raise ValueError("only timezone-aware sealed plans can execute")

    @property
    def digest(self) -> str:
        return digest_value({
            "plan_id": self.plan_id,
            "hypothesis": self.hypothesis,
            "registry_version": self.registry_version,
            "policy_digest": self.policy.digest,
            "detector_id": self.detector_id,
            "detector_version": self.detector_version,
            "status": self.status.value,
            "sealed_at": self.sealed_at.isoformat(),
        })


@dataclass(frozen=True)
class LedgerEvent:
    sequence: int
    event_type: str
    payload: Mapping[str, object]
    previous_digest: str
    digest: str


class ExperimentLedger(Protocol):
    def append(self, event_type: str, payload: Mapping[str, object]) -> LedgerEvent:
        """Append an immutable research-process event."""

    def verify(self) -> bool:
        """Verify chain integrity."""

    def latest_digest(self) -> str:
        """Return the newest chain digest, or GENESIS for an empty ledger."""


class JsonlExperimentLedger:
    """File adapter for a deterministic chained JSON Lines ledger."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _events(self) -> list[LedgerEvent]:
        if not self.path.exists():
            return []
        events = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            item = loads(line)
            events.append(LedgerEvent(
                sequence=item["sequence"],
                event_type=item["event_type"],
                payload=item["payload"],
                previous_digest=item["previous_digest"],
                digest=item["digest"],
            ))
        return events

    def append(self, event_type: str, payload: Mapping[str, object]) -> LedgerEvent:
        with exclusive_file_lock(self.path):
            events = self._events()
            sequence = len(events)
            previous_digest = events[-1].digest if events else "GENESIS"
            digest = digest_value({
                "sequence": sequence,
                "event_type": event_type,
                "payload": payload,
                "previous_digest": previous_digest,
            })
            event = LedgerEvent(sequence, event_type, payload, previous_digest, digest)
            append_durable_line(self.path, dumps(asdict(event), sort_keys=True, separators=(",", ":")) + "\n")
        return event

    def verify(self) -> bool:
        with exclusive_file_lock(self.path):
            previous_digest = "GENESIS"
            for expected_sequence, event in enumerate(self._events()):
                if event.sequence != expected_sequence or event.previous_digest != previous_digest:
                    return False
                if event.digest != digest_value({
                    "sequence": event.sequence,
                    "event_type": event.event_type,
                    "payload": event.payload,
                    "previous_digest": event.previous_digest,
                }):
                    return False
                previous_digest = event.digest
            return True

    def latest_digest(self) -> str:
        with exclusive_file_lock(self.path):
            events = self._events()
            return events[-1].digest if events else "GENESIS"


@dataclass(frozen=True)
class ExperimentResult:
    plan_id: str
    plan_digest: str
    registry_digest: str
    report: DetectionReport
    report_by_stratum: Mapping[str, DetectionReport]
    result_digest: str
    ledger_event_digest: str


def execute_pre_registered_experiment(
    plan: ExperimentPlan,
    scenarios: Sequence[RegisteredScenario],
    detector: BaselineMatchedFilter,
    gates: Sequence[CandidateGate],
    ledger: ExperimentLedger,
) -> ExperimentResult:
    validate_plan(plan, scenarios, detector, gates)
    ledger.append("plan_executed", {
        "plan_id": plan.plan_id,
        "plan_digest": plan.digest,
        "registry_digest": registry_digest(scenarios),
        "policy_digest": plan.policy.digest,
    })

    rows = []
    candidate_summaries = []
    for registered in scenarios:
        observation = generate_observation(registered.scenario)
        candidate = detect(calibrate(observation), detector, gates=gates)
        rows.append(EvaluationRow(
            scenario_id=registered.scenario.scenario_id,
            stratum=registered.stratum,
            expected_signal=registered.scenario.expected_signal,
            detected=candidate.detected,
            score=candidate.score,
        ))
        candidate_summaries.append({
            "scenario_id": registered.scenario.scenario_id,
            "stratum": registered.stratum,
            "detected": candidate.detected,
            "score": candidate.score,
            "gates_passed": candidate.gates_passed,
            "decision_reasons": candidate.decision_reasons,
        })

    report = evaluate(rows)
    by_stratum = evaluate_by_stratum(rows)
    result_payload = {
        "plan_id": plan.plan_id,
        "registry_digest": registry_digest(scenarios),
        "policy_digest": plan.policy.digest,
        "report": asdict(report),
        "candidates": candidate_summaries,
    }
    event = ledger.append("experiment_result", result_payload)
    return ExperimentResult(
        plan_id=plan.plan_id,
        plan_digest=plan.digest,
        registry_digest=registry_digest(scenarios),
        report=report,
        report_by_stratum=by_stratum,
        result_digest=digest_value(result_payload),
        ledger_event_digest=event.digest,
    )


def validate_plan(
    plan: ExperimentPlan,
    scenarios: Sequence[RegisteredScenario],
    detector: BaselineMatchedFilter,
    gates: Sequence[CandidateGate],
) -> None:
    if not scenarios:
        raise ValueError("an experiment requires scenarios")
    versions = {item.registry_version for item in scenarios}
    if versions != {plan.registry_version}:
        raise ValueError("scenario registry does not match sealed plan")
    if detector.detector_id != plan.detector_id or detector.detector_version != plan.detector_version:
        raise ValueError("detector does not match sealed plan")
    if detector.threshold != plan.policy.threshold:
        raise ValueError("detector threshold does not match sealed policy")
    gate_ids = tuple(gate.gate_id for gate in gates)
    if gate_ids != plan.policy.required_gate_ids:
        raise ValueError("gate configuration does not match sealed policy")


def registry_digest(scenarios: Sequence[RegisteredScenario]) -> str:
    return digest_value([item.manifest_digest for item in scenarios])


def digest_value(value: object) -> str:
    return sha256(dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()


def sealed_now() -> datetime:
    return datetime.now(timezone.utc)
