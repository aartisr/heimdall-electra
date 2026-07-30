# Physics model conformance and validation

## What is implemented

The conformance harness runs a candidate PhysicsModel twice on identical typed input and checks:

- model ID and version agree with the model card;
- output is deterministic for the same input;
- output preserves the input scenario ID;
- output declares units and a validity statement;
- every numeric output is finite.

This is a software and provenance gate only.

## What it does not establish

Passing the harness does not establish governing-equation correctness, numerical convergence, conservation, plasma validity, sensor realism, calibration, uncertainty coverage, laboratory agreement, flight performance, debris detection, or operational readiness.

## Required next scientific evidence for a real model

1. A named model owner and a pre-registered physical hypothesis.
2. Governing equations and boundary/initial conditions.
3. Coordinate/time/unit conventions tied to the physics input contract.
4. Numerical method, discretization, convergence/error study, and reproducible environment.
5. Verification through limiting cases, invariants, and independent code comparison.
6. Laboratory or authorized observational validation with uncertainty propagation.
7. Independent review before changing the model-card validity tier.

Until those conditions are met, a model remains fixture-only or analytic-unvalidated, regardless of software conformance.

