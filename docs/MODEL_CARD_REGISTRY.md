# Model-card registry

## Purpose

The model registry is the approval boundary for every synthetic forward model. A model cannot generate Heimdall Electra synthetic data merely because it implements the ForwardModel interface. It must resolve to exactly one versioned model card.

## Required model card

A card declares model identity/version, validity tier, intended purpose, assumptions, excluded claims, verification evidence, and a durable documentation reference. Its digest is included in generated provenance.

## Validity tiers

- fixture_only: software test/control only; no physical claim.
- analytic_unvalidated: stated equations but no sufficient verification/validation.
- laboratory_validated: bounded by stated laboratory evidence; no automatic flight extrapolation.
- flight_validated: bounded by reviewed on-orbit evidence and uncertainty; still not operational approval.

## Current registry

Only two fixture-only cards are registered: the illustrative sine burst and zero-signal control. No analytic, PIC, laboratory-validated, or flight-validated model exists in this project.

## Admission process for a new model

1. Write the model card and equation/algorithm specification.
2. Define units, coordinate frames, input domain, output semantics, numerical method, and deterministic configuration.
3. Define verification tests, convergence or invariant checks, and baseline comparisons.
4. State excluded claims and invalid regimes before generating results.
5. Add the registry record and tests.
6. Run a sealed development experiment; use fresh locked validation for any gate decision.
7. Obtain independent review before changing validity tier.

