# Physics benchmark harness

## Purpose

The benchmark harness supplies a repeatable, plug-in test seam for a future admitted analytic forward model. Each predeclared case binds an exact model identity, typed physics input, expected output units and values, numerical tolerance, evidence references, and limitation.

Before it runs a benchmark, the harness requires the model’s approved analytic-unvalidated admission and performs the existing deterministic conformance check. It then reports every unit, dimensionality, and numerical-tolerance failure without changing the model, benchmark, or registry.

## Sealed suite control

Benchmark cases must be grouped into a sealed suite before execution. The suite content digest binds its ID, exact model ID/version, ordered case digests, review reference, and timezone-aware seal time. A run rejects a model with a different identity and cannot select an alternate case set at run time. Changing a case produces a different suite digest and therefore a distinct experiment.

Every execution appends its sealed-suite digest, model-card digest, model-admission identity, complete per-case failures, verdict, and result digest to the experiment ledger. The ledger makes a recorded run tamper-evident within the local-storage boundary; it does not confer external non-repudiation.

## Required benchmark families

A real candidate must contribute reviewable cases appropriate to its equations, including limiting cases, dimensional/unit checks, invariants or conservation relations where applicable, mesh/time-step convergence cases, and comparison against an independent implementation or trusted analytic solution. The exact families must be selected by the named model owner and independent reviewers—not invented by this repository.

## Scientific boundary

Passing benchmark fixtures means only that the implementation agrees with those declared fixtures within declared tolerances. It does not prove governing-equation correctness, plasma-wake applicability, laboratory agreement, uncertainty coverage, flight performance, or debris detection. Those require independent scientific evidence in subsequent gates.

## Current status

No benchmark cases are registered because no physics-capable model is admitted. The included test fixture exists solely to verify the harness behavior.
