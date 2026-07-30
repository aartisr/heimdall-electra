"""Fetch NOAA SWPC K-index context through the approved Heimdall connector."""

from __future__ import annotations

from argparse import ArgumentParser
from json import dumps
from pathlib import Path

from heimdall import (
    HttpsContextConnector,
    ingest_external_context,
)
from heimdall.ingestion import FileEvidenceStore, JsonlManifestLedger
from heimdall.source_registry import JsonSourceRegistry


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("config/sources/registered_sources.json"),
    )
    args = parser.parse_args()
    registered = JsonSourceRegistry(args.registry).resolve("noaa-swpc-planetary-k-index")
    manifest = ingest_external_context(
        registered.endpoint,
        registered.source,
        HttpsContextConnector(),
        FileEvidenceStore(args.store),
        JsonlManifestLedger(args.store / "manifests.jsonl"),
    )
    print(dumps({
        "scientific_status": (
            "AUTHENTIC EXTERNAL GEOMAGNETIC CONTEXT ONLY — "
            "NOT HEIMDALL OBSERVED DEBRIS EVIDENCE"
        ),
        "source_id": manifest.source_id,
        "evidence_class": manifest.evidence_class.value,
        "origin_uri": manifest.origin_uri,
        "artifact_digest": manifest.artifact_digest,
        "manifest_digest": manifest.digest,
        "transport_metadata": manifest.transport_metadata,
    }, indent=2))


if __name__ == "__main__":
    main()
