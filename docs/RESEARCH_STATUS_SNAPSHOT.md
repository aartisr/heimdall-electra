# Research-status snapshot

## Purpose

The TanStack console no longer relies on a manually authored research-status fixture. A generator derives its read-only JSON from:

- the versioned external-source registry;
- the versioned model-card registry;
- versioned research gate configuration.

This is a query/read-model pattern: governed configuration is the source of status declarations, while the UI snapshot is a derived, replaceable read model.

## Run

    PYTHONPATH=src python3 scripts/export_research_status.py \
      --output apps/analyst-console/public/research-status.json

Use an explicit generated-at value for reproducible fixtures:

    PYTHONPATH=src python3 scripts/export_research_status.py \
      --generated-at 2026-07-30T00:00:00Z \
      --output apps/analyst-console/public/research-status.json

## Security and honesty

The generated status is read-only. It cannot create, edit, approve, release, or suppress scientific evidence. It does not contain raw data, secrets, commands, detector logic, or operational decisions.

A future authenticated API may expose the same schema, but it must build the response server-side from governed records, enforce authorization, and provide freshness/provenance metadata. The browser snapshot remains non-authoritative.

