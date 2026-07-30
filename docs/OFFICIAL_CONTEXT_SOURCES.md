# Official external context sources

## Active integration: NOAA SWPC planetary K-index

The first live connector is NOAA Space Weather Prediction Center’s one-minute planetary K-index JSON product:

- Source URL: https://services.swpc.noaa.gov/json/planetary_k_index_1m.json
- Use: geomagnetic-context stratification, experiment annotations, and future noise/environment analysis.
- Not used for: debris labels, Heimdall signal truth, candidate promotion, orbital state, collision risk, or maneuver advice.

NOAA SWPC publishes the product through its official services directory, and its K-index documentation explains the index as a geomagnetic-disturbance measure. The connector uses HTTPS, an exact host allowlist, redirect-host validation, response-size limit, captured final URL, retrieval timestamp, and SHA-256 content address.

## Authenticity limit

HTTPS protects the retrieval channel to the configured official host. The current endpoint does not provide a separately verified content signature through this connector, so the result is classified as EXTERNAL_CONTEXT. It is not OBSERVED Heimdall evidence and cannot be promoted by code path or policy.

## NASA SPDF/CDAWeb next candidate

NASA SPDF/CDAWeb is the next approved research target for space-physics context and mission data metadata. Its data and access method must be selected only after identifying a precise dataset, data level, provider caveats, terms, coordinate/time convention, and verifiable acquisition approach. The project will register this source and adapter separately; no generic CDAWeb output will be treated as debris truth.

## Run

    PYTHONPATH=src python3 scripts/ingest_noaa_context.py --store /tmp/heimdall-noaa-context

The command creates content-addressed raw bytes plus an acquisition manifest. Review the manifest’s source ID, origin URI, evidence class, transport limits, and digest before any downstream analysis.
