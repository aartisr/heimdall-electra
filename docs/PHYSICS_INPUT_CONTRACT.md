# Physics input contract

## Purpose

This contract is the entry boundary for future analytic, reduced-order, and Particle-in-Cell physics models. It does not contain a solver. It makes the assumptions that a solver needs explicit, typed, and reviewable.

## Required input groups

| Group | Required declaration |
|---|---|
| Time and state | timezone-aware reference time, declared time scale, coordinate frame, position in meters, velocity in meters per second, state uncertainty in meters |
| Plasma environment | electron/ion density in per cubic meter, electron/ion temperature in kelvin, magnetic field vector in tesla, source reference |
| Target | declared target ID, characteristic size in meters, net charge in coulombs, material and shape assumptions |
| Validity | scenario ID and reference to the stated model-validity assumptions |

## Design rules

- Values without an attached documented SI unit do not cross this boundary.
- A timestamp without time scale and timezone does not cross this boundary.
- A position/velocity without a declared frame does not cross this boundary.
- A plasma environment without a source/provenance reference does not cross this boundary.
- A target model without material, geometry, and charge assumptions does not cross this boundary.
- Solver output must identify model/version, input scenario, units, and validity statement.

## Current state

The contract is implemented and tested. It has no physical solver behind it. The current illustrative waveform fixture does not satisfy or claim this physics-model interface. A future physical model must first obtain a model card, then implement the PhysicsModel port and pass the verification/validation requirements in MODEL_CARD_REGISTRY.md.

