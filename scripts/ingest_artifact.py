"""Ingest a known-hash artifact through the Heimdall evidence boundary."""

from __future__ import annotations

from argparse import ArgumentParser
from hashlib import sha256
from json import dumps
from pathlib import Path

from heimdall.domain import EvidenceClass
from heimdall.ingestion import (
    DataSource,
    FileEvidenceStore,
    IntegrityVerification,
    JsonlManifestLedger,
    SourceKind,
    ingest_bytes,
)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--evidence-class", choices=[item.value for item in EvidenceClass], required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--verification-scheme", default="sha256")
    parser.add_argument("--proof-reference", required=True)
    parser.add_argument("--media-type", default="application/octet-stream")
    args = parser.parse_args()

    evidence_class = EvidenceClass(args.evidence_class)
    source = DataSource(
        source_id=args.source_id,
        kind=SourceKind.SYNTHETIC_GENERATOR,
        owner="local research operator",
        terms_reference="local synthetic fixture",
        approved=True,
        allowed_evidence_classes=(EvidenceClass.SYNTHETIC,),
        allowed_verification_schemes=("sha256",),
    )
    payload = args.input.read_bytes()
    manifest = ingest_bytes(
        payload=payload,
        source=source,
        evidence_class=evidence_class,
        original_name=args.input.name,
        media_type=args.media_type,
        verification=IntegrityVerification(
            scheme=args.verification_scheme,
            proof_reference=args.proof_reference,
            expected_digest=args.expected_sha256,
        ),
        store=FileEvidenceStore(args.store),
        manifest_ledger=JsonlManifestLedger(args.store / "manifests.jsonl"),
    )
    print(dumps({
        "scientific_status": "INGESTION PRESERVES BYTES; IT DOES NOT VALIDATE PHYSICS",
        "manifest_digest": manifest.digest,
        "artifact_digest": manifest.artifact_digest,
        "input_digest_check": sha256(payload).hexdigest() == manifest.artifact_digest,
    }, indent=2))


if __name__ == "__main__":
    main()

