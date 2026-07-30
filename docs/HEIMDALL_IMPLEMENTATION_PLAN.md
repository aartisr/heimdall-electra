# Project Heimdall — staged implementation plan

## Mission framing and design principle

Project Heimdall investigates whether passive VLF electromagnetic and electrostatic sensing can detect ionospheric plasma-wake signatures associated with charged, hypervelocity sub-10-cm orbital debris. The proposal calls for passive tri-axial electric and magnetic sensing on 3U CubeSat nodes, edge noise reduction and wavelet matched filtering, multi-node TDOA/FDOA inversion, and an ORDEM-compatible traffic-data product.

This is a high-risk research hypothesis, not an established detection modality. Every physical, detection, coverage, and latency assertion must therefore be a versioned, falsifiable claim. The system must preserve source evidence, propagate uncertainty, and return insufficient evidence safely. It must not turn a correlation into a debris track or maneuver recommendation without independently validated promotion criteria.

The design is intentionally generic: it commits to boundaries, contracts, proof obligations, and quality attributes rather than a spacecraft vendor, cloud provider, orbit, database, language, or model family.

## Architecture principles

Prioritize, in order: scientific integrity and safety; correctness and provenance; cybersecurity and mission assurance; bounded real-time performance; graceful degradation; evolvability; and operator usability.

Use a federated edge-to-ground event architecture:

1. Instrument node: acquisition, time discipline, health, and self-test.
2. Edge detection: conditioning, interference rejection, feature extraction, local candidate scoring, and priority data selection.
3. Transport: encrypted store-and-forward, acknowledgement, bandwidth policy, and loss accounting.
4. Ground science platform: ingest, immutable archive, calibration, association, state inference, and uncertainty quantification.
5. Traffic product: governed publication of candidate, tracklet, debris-cloud, and advisory risk products.
6. Mission control: command authorization, signed deployment, key management, and contingency operation.
7. Governance: promotion policy, independent review, audit, change control, and incident learning.

The control plane is always separate from the scientific data plane. No user interface, analytics workload, or partner integration can directly control spacecraft or rewrite scientific evidence.

### Product levels

- L0: signed raw waveform frames with timing/health metadata; immutable evidence.
- L1: calibrated observations with sensor response, attitude/location, timing correction, and interference/quality masks.
- L2: candidate events with bounded windows, features, detector scores, explanations, and L1 lineage.
- L3: multi-node associated events with TDOA/FDOA results, ambiguity set, residuals, and covariance.
- L4: probabilistic object state, tracklet, or debris-cloud density field.
- L5: released advisory product with validity period, assumptions, uncertainty, provenance, and release approval.

Every record includes schema version, calibration/configuration/model/build version, coordinate and time convention, quality flags, classification, and uncertainty. Reprocessing produces a new output version; it cannot mutate historic evidence.

### Patterns

- Hexagonal architecture: core science rules depend on ports, never a cloud, database, radio, UI, or SDK.
- Event sourcing and CQRS: append observation and decision events, then derive optimized read models.
- Strategy registry: use signed configuration to choose noise estimators, wavelet dictionaries, classifiers, association solvers, and coverage models.
- Pipeline: every transformation declares input/output contract, resource budget, quality check, and failure action.
- State machine and saga: promotion, release, configuration, and operational workflows are explicit, retry-safe, and auditable.
- Anti-corruption layer: isolate ORDEM and other external standards/partner interfaces from the internal domain model.
- Policy as code: authorization, thresholds, retention, release, and promotion policies are tested and versioned.
- Bulkheads, circuit breakers, backpressure, and load shedding: protect acquisition and inference from downlink, compute, and dashboard pressure.

## Security, safety, and performance baseline

Threat-model RF spoofing/interference, time manipulation, compromised spacecraft/ground endpoints, poisoned data/models, insider misuse, denial of service, supply-chain compromise, and unsafe interpretation of uncertain tracks. Re-run the assessment at every architecture change.

Use distinct identities, network zones, keys, and least-privilege roles for flight operations, scientific processing, and analysts. Require mutually authenticated encryption, signed commands/firmware/models/configuration, secure/measured boot, anti-replay controls, hardware-backed keys where feasible, SBOMs, reproducible builds, vulnerability remediation, and tested rollback. Validate every telemetry or partner input for signatures, schema, size, units, range, time, provenance, and rate. Encrypt data in transit and at rest, rotate short-lived credentials, and use dual authorization for high-consequence command actions.

Treat L5 products as advisory until a separately governed mission-safety authority accepts them. The user experience must distinguish detected signal, associated event, inferred state, independently validated state, and approved decision support.

Define SLOs for sampling continuity, L0 durability, edge candidate latency, L3 association latency, L4 update latency, and console freshness. Use bounded queues, ring buffers, streaming transforms, vectorized kernels, idempotency keys, event-time watermarks, and explicit overload policy. During pressure preserve signed health and high-value evidence first, reduce low-value waveform retention second, and never discard silently. Inject node loss, drift, packet loss/duplication/delay, corrupt configuration, detector overload, key rotation, and service outage faults continuously.

Instrument structured logs, metrics, traces, scientific-quality indicators, and audit events using globally unique observation, event, and track IDs. Preserve a tamper-evident ledger for releases, policy/config/model promotion, restricted-data access, and mission actions.

## Staged program

### Stage 0 — proof obligations and governance

Purpose: convert the concept into a measurable, accountable research program.

1. Define stakeholders, protected corridors, mission scenarios, user classes, and the boundary between research output and operational decision support.
2. Create a claims-to-evidence matrix. Each claim names its hypothesis, variables, confounders, test, statistical power, success/failure threshold, owner, and advance/narrow/stop decision.
3. Baseline measures: detection probability by object/environment class; false alarms per observing hour; position/velocity/time covariance; coverage; latency; energy; downlink; cost.
4. Publish glossary, coordinate/time/unit conventions, product schemas, candidate lifecycle, data classification/retention, responsible-use charter, and change control.
5. Complete initial safety, cyber, supply-chain, spectrum/regulatory, and export-control reviews.

Deliverables: ConOps, requirements baseline, evidence matrix, architecture decisions, risk register, threat model, safety-case outline, V&V plan, and integrated schedule.

Gate: independent review agrees that Phase I claims and thresholds are falsifiable and do not overstate expected capability.

### Stage 1 — physics and synthetic-truth foundation

Purpose: determine whether a distinguishable signal is physically plausible.

1. Build a model hierarchy: analytic scaling laws for exploration, reduced-order models for sweeps, selected high-fidelity Particle-in-Cell simulations, and a sensor/telemetry forward model.
2. Parameterize object geometry/material/charge, velocity/orbit, ambient plasma, geomagnetic/solar activity, attitude, receiver transfer functions, sensor noise, quantization, timing error, ephemeris uncertainty, interference, and loss.
3. Verify models with dimensional analysis, conservation/error checks, convergence studies, seeded reproducibility, code-to-code comparison, and documented validity ranges.
4. Make the digital twin produce L0-like waveforms, including saturation, gaps, timing drift, packet loss, and platform self-noise—not ideal labels.
5. Build versioned background/noise libraries and execute sensitivity and uncertainty analysis.

Deliverables: scenario registry, synthetic-data factory, model cards, simulation validation report, scaling report, and uncertainty budget.

Gate: signatures are distinguishable from plausible background in a predeclared nontrivial parameter region. Otherwise narrow or redesign the hypothesis before hardware work.

### Stage 2 — detection science and edge prototype

Purpose: demonstrate an honest, resource-bounded candidate detector.

1. Implement deterministic conditioning: time-quality assessment, calibration, de-spiking, anti-aliasing, gap annotation, stationarity estimation, spectral/wavelet decomposition, and interference/quality masks. Never destructively clean L0.
2. Build a detector ensemble: physics-informed wavelet matched filters, coherent cross-correlation, adaptive spatial/noise filters, and optional learned ranking. Every detector returns a calibrated score and explanation.
3. Prevent data leakage using scenario/source/seed-separated training, validation, and blind holdout datasets.
4. Evaluate ROC and precision-recall by target proxy and environment. Select thresholds from an explicit false-alarm budget, not aggregate accuracy.
5. Benchmark on representative radiation-tolerant compute or emulation: latency distribution, memory, power/thermal impact, and numerical fidelity.
6. Define data priority: health, candidates/context, adaptive background samples, then policy-limited raw forensic bursts.

Deliverables: detector contract, benchmark corpus, threshold policy, algorithm/model cards, edge resource report, and adversarial test report.

Gate: stated sensitivity, false-positive, latency, energy, memory, and explainability thresholds are met under realistic synthetic conditions.

### Stage 3 — timing, association, and kinematic inference

Purpose: establish whether multi-node observations yield useful probabilistic localization.

1. Define time-reference architecture, clock error and holdover budget, time-quality telemetry, and cross-node calibration.
2. Perform gated probabilistic association using propagation/dispersion, ephemeris, attitude, time covariance, and false-coincidence models.
3. Implement robust TDOA/FDOA inversion behind a solver port. Factor graph, Bayesian filter/smoother, or alternate implementation can evolve without changing the domain contract. Preserve multi-modal solutions.
4. Propagate sensor, clock, ephemeris, attitude, environment, feature, and association uncertainty through output covariance.
5. Implement tracklet lifecycle: initiate, confirm, update, merge, split, decay, reject, retract, and archive.
6. Run blind truth-matched campaigns stratified by geometry, baseline, environment, object proxy, and missing data.

Deliverables: timing plan, association/inference interfaces, covariance specification, lifecycle state machine, and localization performance atlas.

Gate: empirical uncertainty coverage agrees with stated confidence, and false association remains under a pre-registered budget.

### Stage 4 — constellation, instrument, and communications trade

Purpose: define a credible demonstrator while bounding operational extrapolation.

1. Model coverage, revisit, and latency in valuable corridors versus node count, orbit/baseline, duty cycle, node failures, timing quality, and environment.
2. Separate the minimum demonstrator from the minimum operational constellation. Define coverage precisely by object regime, confidence, geography, and time window.
3. Allocate sensor response, ADC range, sample rate, analog-front-end noise, EMC, magnetic cleanliness, deployment, radiation, thermal, mass, power, and attitude budgets.
4. Design delay/disruption-tolerant transport, compression/FEC, encryption, prioritization, loss accounting, and ground-contact capacity.
5. Run fault-tree, reliability, and lifecycle-cost analyses; eliminate single points of failure where justified.

Deliverables: trade study, coverage model, instrument/link/power/compute budgets, demonstrator concept, risk-retirement plan, and interface-control documents.

Gate: a feasible demonstrator can collect the evidence needed for flight validation inside credible resource and safety envelopes.

### Stage 5 — hardware-in-loop and laboratory validation

Purpose: prove the measurement chain prior to flight.

1. Build calibrated engineering test articles and signal injection/recording benches using traceable timing and reference signals.
2. Measure amplitude, phase, cross-axis coupling, dynamic range, latency, clock behavior, power, and noise.
3. Perform maturity-appropriate thermal-vacuum, vibration/shock, radiation, EMI/EMC, deployment, and magnetic-cleanliness tests.
4. Replay injected/recorded data through unmodified edge and ground pipelines and compare to controlled truth.
5. Test interruption, storage exhaustion, degraded sensor, time loss, malformed packet, unsigned artifact rejection, key rotation, safe-mode recovery, and audit behavior.
6. Produce calibration certificates, acceptance procedures, manufacturing/configuration controls, and in-orbit calibration strategy.

Gate: performance retains margin under environmental, transport, and fault conditions; model-to-hardware discrepancies are understood or formally bounded.

### Stage 6 — flight demonstration and independent science validation

Purpose: test the narrow physical claim in actual ionospheric conditions.

1. Conduct safety-reviewed, pre-registered observing campaigns with blind analysis periods, predefined exclusions, and raw-evidence preservation.
2. Calibrate in orbit and characterize interference, health, and timing continuously.
3. Correlate candidates with independently authorized reference data under a documented protocol; separate discovery and confirmation where possible.
4. Commission an independent red team to seek alternate explanations: lightning, aurora, known transmitters, platform self-noise, artifacts, timing, and geometry errors.
5. Publish performance, null results, confidence calibration, data completeness, and limits. Never extrapolate favorable windows to global capability.

Gate: independent evidence supports the precise claim being advanced across sufficient environmental diversity.

### Stage 7 — governed traffic-data platform

Purpose: productize validated outputs without losing evidence.

1. Deploy independently scalable, contract-tested L0-L5 services: immutable evidence archive, lineage catalog, stream processing, inference, and read-optimized product stores.
2. Enforce schema compatibility, consumer-driven contract tests, quarantine, idempotency, replay, watermarks, and source-to-product reconciliation.
3. Apply candidate state flow: observed, quality checked, associated, inferred, independently validated, released; include rejected, retracted, and superseded branches. Record actor, policy, evidence, and rationale at every transition.
4. Build partner/standards adapters as isolated anti-corruption layers; deliver covariance, quality, provenance, versions, and retractions.
5. Implement service SLOs/error budgets, capacity testing, backup/restore, disaster recovery, and runbooks.

Gate: authorized consumers receive timely, interpretable, secure, replayable products with intact evidence and uncertainty.

### Stage 8 — analyst and operator experience using TanStack

Purpose: deliver an accessible, high-performance, auditable web application. Mission logic stays server-side.

- TanStack Router: typed route tree, route-level authorization metadata, validated search parameters, bounded route loaders, and separate analyst/operator/approver/admin branches.
- TanStack Query: one typed query-key factory per context: observations, candidates, associations, tracks, coverage, models, audit. Query functions use typed API clients and cache according to source freshness/version: immutable evidence can cache longer; active summaries briefly; commands/audit always revalidate.
- TanStack Table: server-driven sort/filter/pagination for large catalogs. Column contracts render units, confidence, quality, and accessible labels. Never transfer waveform archives via a table.
- TanStack Form: schema-driven typed validation for saved search, calibration review, release approval, and command-preparation forms. The server repeats validation and authorization.
- TanStack Virtual: virtualize dense lists and waveform tiles with stable identity and keyboard operation.

Build role-specific views for mission health, candidate triage, evidence, track/association analysis, coverage/uncertainty, replay, model/configuration approval, audit, and incident response. URL state becomes a validated shareable research record for time range, filters, scenario, product version, and selection; never place secret or sensitive values in a URL. Live subscriptions may invalidate or narrowly patch query keys, must coalesce bursts and verify versions, fall back to polling safely, and visibly report stale/disconnected state. Optimistic updates are only for reversible low-consequence annotations; release and command workflows await authoritative acknowledgement.

Use strict CSP, trusted types where supported, safe rendering, CSRF defense for cookie sessions, short-lived credentials, secure headers, dependency scanning, and no client-side secrets or privileged calculations.

Gate: representative users can interpret uncertainty/provenance correctly and work with live, large catalogs within network, rendering, security, and accessibility budgets.

### Stage 9 — operations and continuous assurance

Purpose: preserve trust while conditions, models, and constellation evolve.

1. Promote through simulation, replay, integration, hardware-in-loop, shadow, canary, and controlled production. Every release is signed, provenance-recorded, and rollback-tested.
2. Monitor timing and calibration health, interference/data/model drift, score calibration, false alarms, association residuals, coverage, latency, energy/cost, and security posture.
3. Reprocess only through versioned pipelines; publish supersession/retraction events and preserve historical views bound to their former configuration.
4. Conduct periodic independent science review, red-team exercises, penetration tests, recovery tests, access reviews, SBOM remediation, and safety-case updates.
5. Translate every incident into a requirement, test, policy, or runbook action with owner and due date.

## Verification strategy

Use a layered evidence program:

- Unit/property tests for units, coordinate transforms, signal invariants, solvers, schemas, and authorization.
- Golden-data regression for simulated, injected, laboratory, and flight datasets; output changes require scientific review.
- Metamorphic tests based on expected physical effects of time shifts, noise increases, rotations, or polarity changes.
- Integration and contract tests across sensor/ingest, stream/archive, inference/product, external adapters, and TanStack client/API.
- Hardware-in-loop mission-rate replay, fault injection, cyber incident drills, and recovery tests.
- Validation studies using blind experiments, independent references, calibrated confidence, and uncertainty coverage, not only code coverage.

Report performance by object proxy, plasma regime, orbit/geography, geometry, sensor health, duty cycle, completeness, and confidence—never only as a global average.

## First 90 days

1. Approve the Stage 0 claims/evidence matrix and Phase I gate thresholds.
2. Publish the glossary, coordinate/time/unit conventions, L0-L5 data contracts, and provenance/version policy.
3. Establish repository boundaries: domain, simulation, edge, platform, adapters, and web; enforce typed contracts and reproducible build metadata.
4. Build one vertical slice: synthetic scenario to L0 waveform to calibration to detector score to L2 candidate to immutable provenance to analyst review.
5. Enable CI for types, linting, unit/property tests, schema compatibility, secret/dependency/SBOM scans, signed artifacts, and benchmark regression.
6. Implement scenario registry, parameter sweeps, background/noise injection, and uncertainty/sensitivity reporting.
7. Define the timing/geometry error model before triangulation.
8. Implement identity, authorization, and immutable audit events before privileged workflows.
9. Bootstrap the TanStack console with typed routing, query-key factory, server-side table contract, provenance drawer, and explicit research-only status.
10. Hold Gate 1 review that gives positive and negative evidence equal standing.

## Phase I definition of done

At the end of the proposed nine-month Phase I, success is a reviewable decision package—not a premature operational warning service:

1. PIC and forward-sensor simulations with validity range and uncertainty;
2. a benchmarked, resource-bounded detector on realistic synthetic ionospheric background;
3. constellation/coverage feasibility tied to stated assumptions;
4. an end-to-end, traceable simulation-to-probabilistic-product prototype;
5. cybersecurity, safety, and V&V evidence sufficient to decide on a Phase II demonstrator; and
6. a defensible advance, narrow, redesign, or stop recommendation supported by both positive and negative evidence.

