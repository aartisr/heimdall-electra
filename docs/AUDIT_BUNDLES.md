# Reproducible audit bundles

## Purpose

An audit bundle is a portable, content-addressed record that binds one sealed experiment plan, its result, the tip of its verified experiment ledger, its declared evidence classes, and selected local artifacts. It makes a result reviewable and detects local artifact modification after export.

It is deliberately **not** a digital signature, an immutable archive, independent review, physical-model validation, or proof of an observed debris detection. Those claims require separately managed signing keys, immutable storage, controlled access, and independent scientific review.

## Required checks

The exporter refuses to package a result unless:

1. the result digest belongs to the supplied sealed plan;
2. the experiment ledger verifies and the result is its latest event;
3. every artifact is an existing regular file inside the independent project repository;
4. each artifact has a path, SHA-256 digest, and byte count; and
5. when a corpus is named, its one-time consumption event is bound to the same plan and corpus.

The verifier recomputes the bundle digest and each artifact digest. Any change to a referenced file makes verification fail.

## Synthetic reference example

Run from the project repository after choosing an output directory inside the repository:

```sh
PYTHONPATH=src python3 scripts/run_pre_registered_experiment.py \
  --ledger data/research-ledgers/synthetic-reference.jsonl \
  --audit-bundle data/audit-bundles/synthetic-reference.json \
  --generated-at 2026-07-30T00:00:00Z \
  --artifact config/models/model_cards.json \
  --artifact config/research/gates.json
```

This example remains synthetic research only. The declared claim boundary is carried inside the bundle and must not be removed or softened.

## Operational next step

Before producing audit bundles for any independently held corpus, establish an external custodian, externally managed signing credentials, an immutable retention location, and an independent-review procedure. Only then may the bundle serve as input to a formal review process.
