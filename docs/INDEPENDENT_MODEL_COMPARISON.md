# Independent-model comparison contract

## Purpose

`heimdall.model_comparison` records a sealed numerical comparison between a primary future physics implementation and a separately identified reference implementation. It tests both with the exact same typed input cases and compares output units and values within predeclared tolerances.

## Sealed evidence

A suite binds the distinct primary/reference model identities, implementation digests, ordered case digests, independence-review reference, seal time, and limitation. A case binds its typed input, expected output unit, numeric tolerance, evidence references, and limitation. Execution requires approved analytic admissions and conforming model cards for both sides, retains all differences, and records the full outcome in the experiment ledger.

Distinct IDs and digests do **not** prove technical, organizational, or intellectual independence. The required review reference must document the actual independence basis: separate code lineage, independent numerical approach, separate authorship/review, or another defensible basis. The suite never makes that inference itself.

## Boundary

Agreement shows only that these specified implementations agree within the declared cases and tolerances. It does not establish governing-equation correctness, numerical convergence, physical validity, sensor realism, calibration, laboratory/flight agreement, a plasma wake, or debris detection. It is one required input to—not a replacement for—the broader physics-model admission and independent scientific review process.
