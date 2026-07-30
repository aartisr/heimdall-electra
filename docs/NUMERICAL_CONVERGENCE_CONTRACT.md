# Numerical convergence contract

## Purpose

Before a future analytic, reduced-order, or high-fidelity forward model is considered as evidence, its numerical behavior must be examined under a sealed refinement study. `heimdall.numerical_convergence` provides the solver-neutral contract for that record. It supplies no plasma equation, model, or result.

## Sealed study plan

A `ConvergenceStudyPlan` binds model ID/version; implementation, execution-environment, and input digests; one named scalar quantity/unit; at least three strictly finer positive resolution scales; a predeclared maximum relative change between the two finest levels; a review reference; and a limitation.

Changing any of those fields produces a new study digest. A resolution scale is intentionally abstract: mesh spacing, time step, inverse particle count, inverse spectral cutoff, or another documented discretization control. The model owner must define its meaning in the study evidence.

## Run and assessment rules

Every `ConvergenceRun` preserves the exact model/build/environment/input bindings, designated resolution scale, finite quantity value, output-artifact digest, and measurement reference. Assessment rejects a different run count, binding, or refinement sequence. It reports the final relative change without filtering runs.

For equally ratio-refined final three levels, it also reports an observed order estimated from successive absolute differences. The value remains undefined whenever that calculation is unsupported; it is never invented.

Passing only says the supplied, plan-bound quantity met its declared final-change threshold. It does **not** establish governing-equation correctness, physical validity, calibration, sensor realism, uncertainty coverage, laboratory agreement, flight performance, a plasma wake, or debris detection.

## Required companion evidence

Retain raw outputs with the implementation/environment attestations, benchmark suite, limiting-case or invariant checks, independent-code comparison, and independent review. These separate evidence streams remain mandatory under the physics-model admission process.
