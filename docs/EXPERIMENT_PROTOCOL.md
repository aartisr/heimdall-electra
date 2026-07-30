# Synthetic experiment protocol

## Status

The initial registry and detector are synthetic research fixtures. They are not a plasma-physics validation, hardware characterization, or flight-performance estimate. Every report must retain this statement.

## Registry rules

Each scenario has a stable ID, seed, full configuration digest, registry version, dataset split, and synthetic expected outcome. The expected outcome is available only to the experiment evaluator; it must never be added to an L0, L1, or L2 product.

Development scenarios may be used to design algorithms. Locked-validation scenarios are used only after a detector version and threshold policy are frozen. Reviewing a locked result consumes that specific fixture for threshold selection; create a new locked set before further tuning.

## Required report fields

- scientific status and evidence class;
- registry and scenario manifest digest;
- detector, threshold-policy, calibration, and configuration versions;
- true/false positive/negative counts and the strata represented;
- detection probability and false-alarm rate with denominator;
- all known confounders and alternative explanations;
- result limitations and the decision to advance, narrow, redesign, or stop.

## Current confounders

Registry 0.2 includes background noise, continuous same-frequency interference, transient same-frequency interference, off-target tone interference, and degraded-clock signal fixtures. The transient same-frequency case is intentionally expected to remain ambiguous to the current generic detector. It is evidence of a limitation, not a result to hide or tune away.
