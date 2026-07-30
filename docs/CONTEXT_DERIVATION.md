# External-context derivation

## Purpose

The context derivation layer converts preserved official bytes into validated environmental annotations. It is a separate bounded context from science detection. Its output supports later experiment stratification and confounder analysis; it cannot create a Heimdall detection, a debris label, a track, or a risk product.

## Current NOAA adapter

The NOAA SWPC planetary K-index parser accepts only artifacts classified as EXTERNAL_CONTEXT from the registered NOAA source. It validates the expected JSON fields, requires a non-empty sequence, bounds estimated K-index values to 0 through 9, and preserves parent artifact and manifest digests in every derived record.

The source time string is retained verbatim. This parser deliberately does not assert UTC conversion or synchronization accuracy because that must come from a reviewed source-contract statement, not an assumption inferred from a field format.

## Output contract

Every record includes:

- source ID, raw artifact digest, and acquisition manifest digest;
- parser ID and version;
- raw provider time tag and explicit time-interpretation limit;
- canonical variable ID and units;
- numeric value and provider qualifier;
- deterministic context-record ID.

## Run

    PYTHONPATH=src python3 scripts/parse_noaa_context.py --store data/external/noaa-swpc

The output is appended to data/external/noaa-swpc/derived/planetary-k-index.jsonl. Re-running the same parser may append duplicate deterministic records; a production context store will add an idempotent uniqueness constraint without replacing prior lineage.

