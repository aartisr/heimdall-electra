# TDOA inference contract

## Purpose

The TDOA contract defines the solver boundary without selecting an algorithm. An input binds one association, its exact candidates, one declared time scale, node geometry in one coordinate frame, node-position uncertainty, and model-assumption lineage. A solver must return all plausible modes, each with a position, time residual, and a finite symmetric positive-semidefinite 3×3 covariance—not silently select one mode.

## Deliberate limit

No TDOA/FDOA solver is implemented. The test solver is only a contract fixture. Neither a valid input nor a contract-conforming result is a physical localization, object identification, track, or safety assessment.

## Admission prerequisites

Before a real solver can be admitted, it needs a reviewed propagation/dispersion model, ephemeris and attitude inputs, cross-node timing evidence, numerical verification cases, ambiguity handling, covariance coverage tests, and an independent false-association study. Its results must then be evaluated on an independently held corpus before any claim may be advanced.
