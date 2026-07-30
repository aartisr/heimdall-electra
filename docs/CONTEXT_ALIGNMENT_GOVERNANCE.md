# Context alignment governance

## Purpose

External environmental context becomes useful only when it can be associated with an experiment or observation without silently inventing a time basis. This layer creates an immutable ContextAlignment record; it does not alter L0, L1, L2, detector scores, labels, or evidence classification.

## Conservative default

The current NOAA parser preserves provider time tags but does not assert their time basis or clock uncertainty. Therefore, no NOAA record is currently eligible for automatic alignment to Heimdall observations.

A SourceTimeContract must be approved before joining any source. It declares:

- source ID;
- explicit time basis;
- maximum stated uncertainty;
- authority/reference supporting the interpretation;
- approval state.

The generic UTC interpreter rejects an unapproved contract and rejects a non-UTC contract. A future provider-specific interpreter may be added through the ContextTimeInterpreter port after review.

## Alignment rules

1. Retain the original observation and external-context records.
2. Restrict candidates to the source named in the approved contract.
3. Convert provider time only through the approved interpreter.
4. Select a single nearest record only if it lies inside the policy window.
5. Reject exact nearest-time ties as ambiguous.
6. Write a derived alignment record containing observation ID, context ID, source ID, offset, policy ID, and time-contract digest.
7. Never use context alignment as a detection label, candidate gate, track calculation, or evidence-class promotion.

## Current status

The alignment engine and tests are implemented. NOAA alignment remains deliberately disabled pending a reviewed source time contract. This is a correctness control, not a missing convenience feature.

