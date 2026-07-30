# Claim governance

## Purpose

Every statement that could be used to describe Heimdall Electra’s capability is placed in a versioned, machine-checked claim registry. The registry separates what the repository can support from what remains unsupported or prohibited. The TanStack evidence console displays the derived read-only view so the caveats travel with the work.

## Claim statuses

- **supported** requires at least one resolvable evidence reference and a declared evidence class.
- **unsupported** records an important statement that current evidence does not establish.
- **prohibited** records a statement that must not be made under the present project state.

Synthetic evidence may support only a software claim. A supported observed-detection or operational claim additionally requires a resolvable independent-review reference. This is a minimum process check, not automatic proof that a review or result is scientifically valid.

## Current boundary

The current implementation supports only a synthetic-software-control claim. Physical performance is unsupported; observed-debris detection and operational-safety use are prohibited. The authoritative records are in `config/research/claims.json`.

## Advancement

To change a claim responsibly, add controlled evidence, preserve provenance and audit bundles, obtain the required independent review, and update the corresponding stage gate. Never relabel synthetic evidence as observed, and never use this registry as a substitute for peer review or mission authorization.
