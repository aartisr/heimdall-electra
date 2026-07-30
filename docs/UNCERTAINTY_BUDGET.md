# Uncertainty budget

## Purpose

Heimdall Electra must treat uncertainty as a first-class product, not a note added after a result. This contract records the nominal quantity, unit, each standard-uncertainty component, uncertainty type, assumed distribution, evidence reference, correlation status, and output interval.

## Current capability

The implementation supports root-sum-square combination only for explicitly independent standard uncertainties of the same quantity and unit. It refuses duplicated correlation groups. A future covariance-aware method must be selected and documented before correlated components can be combined.

## Required components by future product

| Product | Minimum uncertainty sources |
|---|---|
| L1 calibrated observation | sensor response, calibration, ADC/measurement noise, timing, environment |
| L2 candidate | L1 uncertainty, detection threshold/score calibration, interference classification |
| L3 association | node timing, ephemeris, attitude, propagation/environment, feature extraction, association ambiguity |
| L4 track or field | L3 covariance, model-form error, update/filter assumptions, data completeness |
| L5 advisory | all parent uncertainty, validity window, forecast model, product-release policy |

## Honesty rules

- Never mix units or quantities in one budget.
- Never combine known correlated terms as independent.
- Never publish a point estimate without its budget, evidence references, and coverage factor.
- A coverage interval is not automatically a probability guarantee; its interpretation depends on stated distributions, calibration, and validation.
- The current budget code is a generic contract. It contains no physical, sensor, or orbital uncertainty values.

