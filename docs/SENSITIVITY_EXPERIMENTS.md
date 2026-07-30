# Development sensitivity experiments

## Purpose

The sweep engine performs a Cartesian exploration of explicitly named SyntheticScenario fields through a selected forward model, detector, and ordered candidate gates. It is a reusable orchestration layer based on composition: scenario parameters, model strategy, detector strategy, and gate strategies remain independently replaceable.

## Integrity controls

- A sweep is hard-restricted to the development split. It refuses locked-validation use.
- Each result records scenario ID, swept parameters, model ID/version, raw score, detected state, and gate state.
- A sweep does not alter the detector threshold, gate configuration, model, or source evidence.
- Sweep outputs are hypothesis-generation artifacts, not test-set performance metrics.
- A new physics-capable model may use this engine only after it meets the model-card requirements.

## Initial sweep

The included command varies signal amplitude and background-noise amplitude under the IllustrativeBurstSineModel. The values exercise code paths only. Because the baseline score normalization has known properties, this output is specifically not evidence of a physical signal-to-noise relationship.

Run:

    PYTHONPATH=src python3 scripts/run_development_sweep.py

Do not report the output as a detection probability, sensitivity curve, or orbital-debris result.

