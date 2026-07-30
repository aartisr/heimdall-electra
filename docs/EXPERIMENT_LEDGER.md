# Pre-registered experiment ledger

## Purpose

The experiment layer freezes the detector threshold and candidate-gate configuration before execution, then records plan execution and results in an append-only, hash-chained JSON Lines ledger.

It uses Ports and Adapters: the experiment service depends on the ExperimentLedger port, while JsonlExperimentLedger is a replaceable local-file adapter. A future adapter may use independently operated WORM storage or a signed institutional ledger without changing the experiment service.

## Integrity properties and limits

The file adapter detects edits, deletions, reordering, and chain breaks after the fact. It is tamper-evident, not tamper-proof or independently signed. It does not establish a timestamp authority, reviewer independence, access control, or physical-data authenticity.

Before laboratory or flight use, replace or augment it with signed events, key management, WORM/object-lock retention, authenticated identities, replicated storage, external timestamps, and independent review.

## Execution rules

- A plan must be sealed with a hypothesis, registry version, detector identity/version, threshold policy, gate IDs, and time.
- Execution rejects a mismatched registry, detector, threshold, or gate configuration.
- Results retain raw scores, gate decisions, stratum, metrics, and a chained ledger event digest.
- Running a locked corpus produces a record; it does not authorize tuning against that result.
- Every post-result configuration change requires a new plan and a fresh locked or blind corpus.

Run the synthetic reference experiment with:

    PYTHONPATH=src python3 scripts/run_pre_registered_experiment.py --ledger /tmp/heimdall-ledger.jsonl

