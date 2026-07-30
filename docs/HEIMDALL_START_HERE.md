# Heimdall Electra — start here

## The best first implementation

Start with a scientific vertical slice, not a CubeSat, dashboard, or production constellation:

1. One versioned plasma-wake scenario.
2. A forward sensor model that emits a synthetic raw waveform.
3. Calibration and quality metadata.
4. A deterministic baseline matched-filter detector.
5. A candidate record with uncertainty and complete provenance.
6. A small analyst view that exposes the evidence and limitations.

This directly tests the central proposal claim and establishes contracts that later hardware, algorithms, and services must honor. It is repeatable, inexpensive to falsify, secure by design, and useful whether the outcome is positive or negative.

## First milestone definition

The first milestone is complete only when a reviewer can select an immutable scenario ID, reproduce its L0 waveform from a clean environment, see every simulation/calibration/algorithm/configuration/build version, run the detector, inspect score/threshold/uncertainty/source windows, compare candidate and non-candidate cases, and replay the analysis without editing an original record.

A synthetic detection does not prove the physical concept. It proves only that the assumed instrument and algorithm can be tested transparently.

## First four weeks

### Week 1 — scientific contract

- Approve the claim-to-evidence matrix and select one narrow hypothesis.
- Select coordinate frames, time scale, units, L0-L2 schemas, quality flags, and uncertainty representation.
- Create the data-source registry, source-caveat policy, chain-of-custody rules, and immutable experiment registry.
- Pre-register detection probability, false alarms per observing hour, latency, score calibration, and applicability range.
- Threat-model the prototype and require signed inputs/artifacts and least-privilege access from the outset.

Exit: an architecture review can state exactly what the prototype may and may not claim.

### Week 2 — synthetic truth

- Implement the smallest credible forward model: parameterized wake signal, instrument transfer function, noise, timing metadata, and known confounders.
- Produce raw-like L0 waveform segments, sensor/health data, clock quality, calibration reference, and source hashes.
- Add deterministic seeds and parameter-sweep scenarios.
- Include representative negatives: noise-only, interference, timing fault, data gap, and self-noise.

Exit: a clean environment reproduces every scenario exactly, or within a documented numerical tolerance.

### Week 3 — honest baseline detector

- Implement transparent conditioning and wavelet/matched-filter baseline before any learned model.
- Record each transformation and preserve original raw input.
- Use scenario-separated development and locked-validation datasets. Do not tune after looking at locked results.
- Produce calibration curves and per-stratum results, not global accuracy alone.
- Benchmark latency, memory, and false-alarm behavior under load.

Exit: every candidate has score, threshold policy ID, explanation/features, quality state, uncertainty, and complete L0 lineage.

### Week 4 — review and replay

- Expose the vertical slice through a minimal TanStack application: typed route/search state, versioned query keys, server-side table contract, candidate-evidence page, and provenance drawer.
- Keep all science, inference, and authorization server-side. The UI renders approved product views only.
- Add audit events, failed-input quarantine, replay, and a short reviewer guide.
- Hold a Gate 1 review with a blind scenario subset and document limitations or failure modes.

Exit: an independent reviewer reproduces and challenges a result without developer assistance.

## Recommended repository shape

Keep bounded areas independent: domain contracts; simulation; processing; platform ingest/archive/lineage/audit; analyst web application; controlled test fixtures; and documentation. A monorepo is appropriate only if it makes shared contracts easier.

Avoid a microservice split until the vertical slice is stable. Modular components with explicit ports are enough initially. Extract a service only when a distinct deployment, scaling, trust, or lifecycle boundary justifies it.

## Minimum contracts before UI work

- ObservationL0: waveform reference, sample configuration, timing/clock quality, sensor/calibration identity, sequence/gap state, health, signature, provenance.
- CalibratedObservationL1: L0 reference, calibration result/uncertainty, quality/interference flags, engineering units.
- CandidateL2: bounded evidence window, detector/version/configuration, score and threshold policy, features, quality state, uncertainty, parent IDs.
- ExperimentRun: hypothesis, scenarios, code/build/configuration, metrics, pre-registration reference, reviewer, and decision.
- AuditEvent: actor/service, action, target, policy version, time, result, and immutable reason.

All writes are idempotent, authenticated, schema-validated, and append-only in scientific effect.

## First technology choices

- Use typed contracts and unit-aware domain types to prevent coordinate, time, and unit errors.
- Use content-addressed object storage for raw evidence and a catalog store for metadata and lineage.
- Add a queue/stream only after the synchronous slice is correct; preserve event IDs and ordering semantics from day one.
- Keep the reference detector easily inspectable; deploy optimized edge code only after equivalence benchmarks.
- Use TanStack for client concerns: Router for typed navigation, Query for server-state synchronization, Table for server-backed catalogs, Form for validated human workflows, and Virtual for dense large views.

## Do not do first

- Do not claim individual sub-centimeter tracking from simulation.
- Do not train a black-box model before a transparent baseline and locked validation corpus exist.
- Do not procure a constellation before signal, timing, coverage, and resource assumptions pass gates.
- Do not make the dashboard the system of record.
- Do not rely on a single catalog, analyst, or favorable data window.
- Do not discard negative results, raw evidence, caveats, or failed associations.

## First gate question

At the first review ask: Is there a reproducible, distinguishable signal under stated assumptions, with honest uncertainty and a plausible route to independent validation?

If not, narrow or change the physics/model. That is a productive outcome and protects scientific credibility.

