"""Custody and one-time consumption controls for validation corpora.

A corpus is only genuinely locked when its labels/cases are held independently
from detector development. This module cannot create independence by itself; it
records custody assertions and prevents re-use once a fresh corpus is consumed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from typing import Protocol, Sequence

from .domain import DatasetSplit
from .durable_storage import append_durable_line, exclusive_file_lock
from .governance import ExperimentPlan, digest_value
from .registry import RegisteredScenario


@dataclass(frozen=True)
class CorpusManifest:
    corpus_id: str
    registry_version: str
    split: DatasetSplit
    scenario_manifest_digests: tuple[str, ...]
    custody_reference: str
    independently_held: bool
    fresh: bool

    def __post_init__(self) -> None:
        if not all((
            self.corpus_id, self.registry_version, self.scenario_manifest_digests,
            self.custody_reference,
        )):
            raise ValueError("corpus manifest metadata is required")

    @property
    def digest(self) -> str:
        value = asdict(self)
        value["split"] = self.split.value
        return digest_value(value)


@dataclass(frozen=True)
class CorpusConsumptionEvent:
    corpus_digest: str
    experiment_plan_digest: str
    consumed_at: str
    digest: str


class CorpusConsumptionLedger(Protocol):
    def consume(self, corpus: CorpusManifest, plan: ExperimentPlan) -> CorpusConsumptionEvent:
        """Consume a fresh independently held locked corpus exactly once."""


class JsonlCorpusConsumptionLedger:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _events(self) -> tuple[CorpusConsumptionEvent, ...]:
        if not self.path.exists():
            return ()
        return tuple(
            CorpusConsumptionEvent(
                corpus_digest=item["corpus_digest"],
                experiment_plan_digest=item["experiment_plan_digest"],
                consumed_at=item["consumed_at"],
                digest=item["digest"],
            )
            for item in (
                loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line
            )
        )

    def consume(self, corpus: CorpusManifest, plan: ExperimentPlan) -> CorpusConsumptionEvent:
        if corpus.split is not DatasetSplit.LOCKED_VALIDATION:
            raise ValueError("only locked-validation corpora may be consumed")
        if not corpus.independently_held or not corpus.fresh:
            raise ValueError("corpus is not a fresh independently held validation corpus")
        if corpus.registry_version != plan.registry_version:
            raise ValueError("corpus registry version does not match experiment plan")
        with exclusive_file_lock(self.path):
            if any(event.corpus_digest == corpus.digest for event in self._events()):
                raise ValueError("corpus has already been consumed")
            consumed_at = datetime.now(timezone.utc).isoformat()
            event = CorpusConsumptionEvent(
                corpus_digest=corpus.digest,
                experiment_plan_digest=plan.digest,
                consumed_at=consumed_at,
                digest=digest_value({
                    "corpus_digest": corpus.digest,
                    "experiment_plan_digest": plan.digest,
                    "consumed_at": consumed_at,
                }),
            )
            append_durable_line(self.path, dumps(asdict(event), sort_keys=True, separators=(",", ":")) + "\n")
        return event


def build_corpus_manifest(
    corpus_id: str,
    scenarios: Sequence[RegisteredScenario],
    custody_reference: str,
    independently_held: bool,
    fresh: bool,
) -> CorpusManifest:
    if not scenarios:
        raise ValueError("corpus requires scenarios")
    splits = {scenario.split for scenario in scenarios}
    versions = {scenario.registry_version for scenario in scenarios}
    if len(splits) != 1 or len(versions) != 1:
        raise ValueError("corpus scenarios must share one split and registry version")
    return CorpusManifest(
        corpus_id=corpus_id,
        registry_version=next(iter(versions)),
        split=next(iter(splits)),
        scenario_manifest_digests=tuple(sorted(scenario.manifest_digest for scenario in scenarios)),
        custody_reference=custody_reference,
        independently_held=independently_held,
        fresh=fresh,
    )
