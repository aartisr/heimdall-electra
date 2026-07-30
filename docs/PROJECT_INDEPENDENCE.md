# Project independence boundary

Project Heimdall Electra is an independent research project. It must not import, execute, read, write, or depend on neighbouring workspace projects.

## Enforced boundaries

- This project root is its own Git repository.
- Runtime code uses only the Python standard library at this stage.
- The project has no workspace package manager, relative sibling path, symbolic-link, service, database, or shared build dependency.
- All source, tests, scripts, fixtures, documentation, and generated research artifacts belong below this project root.
- Raw or restricted research data may be accessed only through documented, authenticated source connectors. It is never read from a neighbouring project directory.
- Cross-project reuse requires an explicit, reviewed external interface or a versioned published artifact. Direct source imports are prohibited.

## Evidence and authenticity boundary

Every data product declares evidence class: synthetic, laboratory, or observed. Synthetic data is never promoted to observed evidence. The project retains content hashes, provenance, configuration, calibration identity, and parent references for all scientific outputs.

## Verification

Run the boundary check before every release and in CI:

    PYTHONPATH=src python3 scripts/verify_independence.py

The check rejects forbidden workspace references, symbolic links, and non-standard-library imports in the current reference implementation. It complements, but does not replace, code review and dependency/SBOM review when external packages are introduced.
