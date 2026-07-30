"""Parse the archived NOAA artifact into lineage-preserving context records."""

from __future__ import annotations

from argparse import ArgumentParser
from json import loads, dumps
from pathlib import Path

from heimdall.context import JsonlContextStore, NoaaPlanetaryKIndexParser
from heimdall.domain import EvidenceClass
from heimdall.ingestion import FileEvidenceStore


def latest_noaa_manifest(path: Path) -> dict[str, object]:
    items = [
        loads(line) for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    matches = [item for item in items if item["source_id"] == "noaa-swpc-planetary-k-index"]
    if not matches:
        raise ValueError("no NOAA SWPC K-index manifest found")
    return matches[-1]


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--store", type=Path, required=True)
    args = parser.parse_args()
    manifest = latest_noaa_manifest(args.store / "manifests.jsonl")
    payload = FileEvidenceStore(args.store).read(str(manifest["artifact_digest"]))
    records = NoaaPlanetaryKIndexParser().parse(
        payload,
        source_id=str(manifest["source_id"]),
        source_manifest_digest=str(manifest["manifest_digest"]),
        source_artifact_digest=str(manifest["artifact_digest"]),
        evidence_class=EvidenceClass(str(manifest["evidence_class"])),
    )
    written = JsonlContextStore(args.store / "derived" / "planetary-k-index.jsonl").append(records)
    print(dumps({
        "scientific_status": (
            "DERIVED EXTERNAL GEOMAGNETIC CONTEXT ONLY — "
            "NOT HEIMDALL OBSERVED DEBRIS EVIDENCE"
        ),
        "records_written": written,
        "source_manifest_digest": manifest["manifest_digest"],
        "parser": "noaa-swpc-planetary-k-index-parser/0.1.0",
        "time_interpretation": records[0].time_interpretation,
    }, indent=2))


if __name__ == "__main__":
    main()

