# Physics relation verification

## Purpose

`heimdall.physics_relations` records predeclared metamorphic and limiting-case checks for a future admitted analytic model. Instead of asking whether one output equals a stored number, a case tests whether the outputs from two declared inputs obey an explicitly justified relationship:

- `equal` — transformed output should equal baseline output;
- `opposite` — transformed output should reverse sign;
- `scaled` — transformed output should equal a declared finite multiplier times baseline output.

The physical justification, input transformation, validity range, and limitations belong in the case evidence references. The framework does not infer them.

## Integrity controls

Each case binds exact model identity, both typed inputs, expected units, relation, tolerance, evidence references, and limitation. A sealed suite binds the ordered case digests, reviewer reference, and timezone-aware sealing time. Execution rejects a different model identity, requires an approved analytic admission, validates output conformance for both inputs, preserves every failure, and appends the full outcome to the experiment ledger.

## Scientific boundary

Passing demonstrates agreement with the supplied relation cases only. It does **not** demonstrate that the governing equations are correct, that the relation applies to the real ionosphere, conservation, numerical convergence, sensor realism, calibration, laboratory agreement, flight performance, or debris detection. It must be combined with convergence studies, benchmark evidence, independent implementation comparison, and external review before any physics-model gate can advance.
