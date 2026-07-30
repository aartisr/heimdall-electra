# Physics-model admission

## Current status

No physics-capable forward model has been proposed or admitted. The only registered models are synthetic fixtures. They remain incapable of supporting a physical, laboratory, flight, observed-detection, or operational claim.

## Admission boundary

The `analytic_unvalidated` model-card tier is not a declaration of physical validity. It means only that a candidate has passed the documented admission prerequisites for reviewable analytic research. The admission record must bind the exact model ID and version to:

1. a named model owner and a pre-registered hypothesis;
2. governing equations and stated validity assumptions;
3. the typed unit/frame/time input contract;
4. output semantics and a numerical-method description;
5. documented verification cases; and
6. a resolvable independent-review record.

The loader verifies that every cited local record exists. The admission validator refuses drafts, identity mismatches, fixture-tier cards, and any promotion above `analytic_unvalidated`.

## What remains separate

Admission does not prove the equations, numerical convergence, calibration, experimental agreement, uncertainty coverage, laboratory validation, or flight validity. Laboratory and flight tiers require their own evidence package and independent scientific review. No code path automatically changes a model-card tier.

## How to propose a candidate

Create immutable, reviewable records under `docs/` (or an approved controlled evidence location), then add a draft to `config/models/physics_model_admissions.json`. Keep it draft until independent review is recorded. Only after review may an exact corresponding model card be considered at the analytic-unvalidated tier.
