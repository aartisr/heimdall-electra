# Project Heimdall

A research implementation of the Project Heimdall proposal: passive ionospheric plasma-wake sensing for orbital-debris research.

## Scientific status

This repository starts with a reproducible synthetic vertical slice. It is not a validated physical model, a debris tracker, or an operational safety product. Every generated record carries a declared evidence class and provenance so that synthetic evidence cannot be mistaken for observed flight data.

Read the project documentation in docs. Start with docs/HEIMDALL_START_HERE.md.

## Quick start

Run the reference tests:

    python3 -m unittest discover -s tests -v

Run the synthetic vertical slice:

    PYTHONPATH=src python3 scripts/run_vertical_slice.py

The output is an L0-like synthetic observation and a baseline candidate decision. It exists to exercise the evidence contract and detector interface, not to claim detection capability.

For a content-addressed, locally verifiable record of a sealed run, see [audit-bundle governance](docs/AUDIT_BUNDLES.md). An audit bundle detects changes and supports review; it is not a substitute for external signing, immutable retention, or independent scientific validation.
