# Forward-model governance

## Purpose

A forward model maps stated scenario assumptions to a synthetic signal before instrument noise, interference, timing metadata, or data transport effects are added. It is a replaceable Strategy port. The synthetic scenario generator owns noise and confounders; the forward model owns only the asserted signal.

## Current models

- IllustrativeBurstSineModel: a legacy sine-burst fixture for pipeline and regression testing.
- NullSignalModel: a no-signal control.

Neither models a plasma wake or supports a physical detection claim. Both must remain classified as synthetic.

## Requirements for a physics-capable model

Before a model can be called analytic, reduced-order, PIC, or physically validated, it must have:

1. a model card with governing equations, assumptions, units, coordinates, input domain, output semantics, numerical methods, and known invalid domains;
2. code/build version, parameter/configuration digest, deterministic seed policy, and convergence/error evidence;
3. verification tests for units, conservation or invariants where applicable, limiting cases, and independent code comparison;
4. calibration/validation against laboratory or authorized observations, with uncertainty propagation;
5. a pre-registered experiment plan and independent review.

The generator includes model ID and version in provenance/configuration digest. Switching models always creates a distinct L0 identity and cannot overwrite prior evidence.

