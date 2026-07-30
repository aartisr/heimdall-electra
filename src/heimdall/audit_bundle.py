"""Portable integrity bundles for reproducible research review.

An audit bundle is a content-addressed statement of *what was run* and the
local artifacts required to review it.  It is not a digital signature, an
independent audit, or scientific validation.  External signing, immutable
storage, and independent review remain required for those claims.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from typing import Sequence

from .corpus_custody import CorpusConsumptionEvent, CorpusManifest
from .durable_storage import atomic_write_text
from .domain import EvidenceClass
from .governance import ExperimentPlan, ExperimentResult, JsonlExperimentLedger, digest_value
from .registry import RegisteredScenario


AUDIT_BUNDLE_SCHEMA = "heimdall.audit-bundle/v1"


@dataclass(frozen=True)
class ArtifactDigest:
    relative_path: str
    sha256: str
    byte_count: int


@dataclass(frozen=True)
class AuditBundle:
    schema: str
    generated_at: str
    plan_digest: str
    result_digest: str
    registry_digest: str
    experiment_ledger_digest: str
    evidence_classes: tuple[str, ...]
    claim_boundary: str
    artifacts: tuple[ArtifactDigest, ...]
    corpus_digest: str | None = None
    corpus_consumption_event_digest: str | None = None

    def __post_init__(self) -> None:
        if self.schema != AUDIT_BUNDLE_SCHEMA:
            raise ValueError("unsupported audit-bundle schema")
        if datetime.fromisoformat(self.generated_at.replace("Z", "+00:00")).tzinfo is None:
            raise ValueError("generated_at must be timezone-aware")
        if not all((self.plan_digest, self.result_digest, self.registry_digest, self.experiment_ledger_digest)):
            raise ValueError("audit bundle requires plan, result, registry, and ledger digests")
        if not self.evidence_classes or not self.claim_boundary:
            raise ValueError("audit bundle requires evidence classes and a claim boundary")
        if (self.corpus_digest is None) != (self.corpus_consumption_event_digest is None):
            raise ValueError("corpus and consumption event digests must be present together")

    def payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "generated_at": self.generated_at,
            "plan_digest": self.plan_digest,
            "result_digest": self.result_digest,
            "registry_digest": self.registry_digest,
            "experiment_ledger_digest": self.experiment_ledger_digest,
            "evidence_classes": list(self.evidence_classes),
            "claim_boundary": self.claim_boundary,
            "artifacts": [asdict(item) for item in self.artifacts],
            "corpus_digest": self.corpus_digest,
            "corpus_consumption_event_digest": self.corpus_consumption_event_digest,
        }

    @property
    def digest(self) -> str:
        return digest_value(self.payload())

    def serializable(self) -> dict[str, object]:
        return {**self.payload(), "bundle_digest": self.digest}


def build_audit_bundle(
    *,
    repository_root: Path,
    generated_at: datetime,
    plan: ExperimentPlan,
    result: ExperimentResult,
    ledger: JsonlExperimentLedger,
    scenarios: Sequence[RegisteredScenario],
    artifact_paths: Sequence[Path],
    corpus: CorpusManifest | None = None,
    corpus_consumption: CorpusConsumptionEvent | None = None,
) -> AuditBundle:
    """Build a local, re-verifiable bundle after validating all bindings."""
    if generated_at.tzinfo is None:
        raise ValueError("generated_at must be timezone-aware")
    if plan.digest != result.plan_digest:
        raise ValueError("result does not belong to the supplied plan")
    if not ledger.verify():
        raise ValueError("experiment ledger integrity verification failed")
    if ledger.latest_digest() != result.ledger_event_digest:
        raise ValueError("result is not the latest event in the supplied ledger")
    if (corpus is None) != (corpus_consumption is None):
        raise ValueError("corpus and consumption event must be supplied together")
    if corpus is not None and corpus_consumption is not None:
        if corpus.digest != corpus_consumption.corpus_digest:
            raise ValueError("consumption event does not belong to supplied corpus")
        if plan.digest != corpus_consumption.experiment_plan_digest:
            raise ValueError("consumption event does not belong to supplied plan")

    evidence_classes = tuple(sorted({item.evidence_class.value for item in scenarios}))
    if not evidence_classes:
        raise ValueError("at least one scenario is required")
    return AuditBundle(
        schema=AUDIT_BUNDLE_SCHEMA,
        generated_at=generated_at.isoformat(),
        plan_digest=plan.digest,
        result_digest=result.result_digest,
        registry_digest=result.registry_digest,
        experiment_ledger_digest=result.ledger_event_digest,
        evidence_classes=evidence_classes,
        claim_boundary=_claim_boundary(evidence_classes),
        artifacts=_artifact_digests(repository_root, artifact_paths),
        corpus_digest=corpus.digest if corpus else None,
        corpus_consumption_event_digest=corpus_consumption.digest if corpus_consumption else None,
    )


def write_audit_bundle(path: Path, bundle: AuditBundle) -> None:
    atomic_write_text(path, dumps(bundle.serializable(), sort_keys=True, indent=2) + "\n")


def verify_audit_bundle(path: Path, repository_root: Path) -> bool:
    """Verify bundle self-digest and every referenced local artifact digest."""
    raw = loads(path.read_text(encoding="utf-8"))
    expected_digest = raw.pop("bundle_digest", None)
    artifacts = tuple(ArtifactDigest(**item) for item in raw["artifacts"])
    bundle = AuditBundle(
        schema=raw["schema"], generated_at=raw["generated_at"], plan_digest=raw["plan_digest"],
        result_digest=raw["result_digest"], registry_digest=raw["registry_digest"],
        experiment_ledger_digest=raw["experiment_ledger_digest"],
        evidence_classes=tuple(raw["evidence_classes"]), claim_boundary=raw["claim_boundary"],
        artifacts=artifacts, corpus_digest=raw.get("corpus_digest"),
        corpus_consumption_event_digest=raw.get("corpus_consumption_event_digest"),
    )
    return expected_digest == bundle.digest and all(
        _digest_file(_inside_root(repository_root, item.relative_path)) == item.sha256
        and _inside_root(repository_root, item.relative_path).stat().st_size == item.byte_count
        for item in artifacts
    )


def _artifact_digests(repository_root: Path, artifact_paths: Sequence[Path]) -> tuple[ArtifactDigest, ...]:
    root = repository_root.resolve()
    resolved = tuple(_inside_root(root, str(path)) for path in artifact_paths)
    if len(set(resolved)) != len(resolved):
        raise ValueError("audit artifacts must be unique")
    return tuple(
        ArtifactDigest(str(path.relative_to(root)), _digest_file(path), path.stat().st_size)
        for path in sorted(resolved)
    )


def _inside_root(repository_root: Path, relative_path: str) -> Path:
    root = repository_root.resolve()
    candidate = (root / relative_path).resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file():
        raise ValueError("audit artifact must be an existing regular file inside repository root")
    return candidate


def _digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _claim_boundary(evidence_classes: Sequence[str]) -> str:
    classes = set(evidence_classes)
    if classes == {EvidenceClass.SYNTHETIC.value}:
        return "SYNTHETIC RESEARCH ONLY — NOT AN OBSERVED DEBRIS DETECTION"
    if EvidenceClass.OBSERVED.value not in classes:
        return "RESEARCH EVIDENCE ONLY — NOT AN OBSERVED DEBRIS DETECTION"
    return "OBSERVED-EVIDENCE CLAIMS REQUIRE INDEPENDENT SCIENTIFIC REVIEW"
