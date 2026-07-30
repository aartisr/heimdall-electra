# Project Heimdall — data sourcing and integrity strategy

## The honest rule

Heimdall must not claim that a public catalog, simulated event, or ML score is a debris detection. Only a fully traceable chain of calibrated Heimdall measurements, independently tested against plausible alternative explanations, can support that claim.

Use public and partner data in three distinct roles:

1. Prior/context: constrain the expected environment and plausible target population.
2. Calibration/validation: independently test timing, environmental interpretation, and known-object association.
3. Ground truth: only where provenance, uncertainty, and independence permit it.

Never train and evaluate a detector on labels derived from the same system or model that generated its features. Never use a catalog non-detection as proof that a sub-centimeter signal is false; catalog incompleteness is intrinsic to the problem.

## Source hierarchy

| Tier | Data source | Primary use | Authenticity rule |
|---|---|---|---|
| A | Heimdall instrument L0 raw data | primary scientific evidence | Digitally signed at the node, immutable at ingest, complete loss accounting, calibrated and replayable |
| A | Controlled laboratory/HIL injection experiments | sensor and pipeline calibration | Traceable source, independent timing reference, blinded labels for analyst evaluation |
| B | Independent in-orbit/reference observations under formal agreement | confirmation and disconfirmation | Preserve provider provenance, access terms, measurement uncertainty, and matching protocol |
| B | NASA ODPO/ORDEM data and authorized debris products | population priors, engineering benchmark, coverage/risk context | Cite exact release/version and do not treat model output as event truth |
| B | NASA SPDF/CDAWeb and mission/ground datasets | plasma, field, wave, ephemeris, and environmental context | Preserve original file, DOI/source metadata, caveats, access date, and processing level |
| B | NOAA SWPC and other authoritative space-weather products | operational environment/context and stratification | Archive source timestamp/version; use provisional products only as provisional |
| C | ESA DISCOS and other authorized object metadata | object/launch/contextual reference | Follow terms, attribution, and access restrictions; do not redistribute restricted data |
| D | Physics simulations and synthetic backgrounds | hypothesis testing, algorithm development, stress testing | Clearly mark synthetic; version seeds, assumptions, code/build, and validity range |
| E | Literature, visualizations, third-party feeds, crowd data | discovery only | Cannot create truth labels or safety products without independent verification |

NASA’s Orbital Debris Program Office describes ORDEM as an engineering debris-environment model built from radar, optical, in-situ, and laboratory measurements. It is excellent for priors and benchmark scenarios, but it is not a direct truth source for individual sub-centimeter detections. NASA SPDF/CDAWeb provides openly accessible space-physics data and metadata; provider caveats must remain attached to every ingested derivative. ESA DISCOSweb is valuable for trackable-object metadata but explicitly has access/terms constraints and does not distribute surveillance-system ephemerides.

## Acquisition workflow

1. Register every source before first use in a data-source registry: owner, purpose, authorization, license/terms, classification, collection method, clock/time basis, coordinate/unit conventions, expected latency, quality caveats, retention, and contact.
2. Fetch through a reproducible connector. Record request parameters, transport checksum, retrieval time, source release/version, source URL or agreement reference, and source metadata verbatim.
3. Deposit the original into a write-once evidence zone. Assign content hash, immutable object ID, and chain-of-custody event; never edit an original.
4. Validate signature/checksum, schema, units, ranges, time monotonicity, coordinate frame, completeness, and duplicate rate. Quarantine failures; do not silently repair them.
5. Transform only in versioned pipelines. Each derived item stores parent IDs, calibration/model/configuration/build digests, transform parameters, operator/service identity, and quality flags.
6. Release a curated, access-controlled analysis copy only after automated checks and a recorded review. Keep raw, restricted, and public zones physically/logically separate.
7. Preserve retractions, corrections, and supersessions from each provider. A downstream product must update its provenance and validity state rather than overwrite history.

## Heimdall primary-data requirements

Each node must generate L0 records containing signed waveform payloads, sample-rate and ADC configuration, sensor serial/response, calibration state, monotonic sequence number, local clock state/uncertainty, node ephemeris/attitude version, power/thermal/health state, gap/loss indicators, and edge software/configuration digest.

An independent timing/calibration reference must be present in every test campaign. Maintain raw waveform windows before and after a candidate; candidate-only snippets invite confirmation bias. Use deterministic sampling/data-priority policies that are signed, versioned, and auditable.

Calibration must include laboratory transfer functions, cross-axis coupling, noise floor, saturation, timing/phase behavior, EMC/self-noise characterization, environmental sensitivity, and post-launch/in-orbit calibration. Calibration uncertainty is an explicit input to every L3/L4 covariance.

## Building the research corpus

Create four strictly partitioned collections:

1. Development corpus: synthetic and controlled-injection data used to design detectors.
2. Locked validation corpus: unseen scenarios and injection campaigns used to choose thresholds once.
3. Blind test corpus: held by an independent custodian; accessed only after methods are frozen.
4. Operational corpus: on-orbit records, never retrospectively mixed into training without a governed version change.

Stratify all collections by plasma regime, magnetic/solar conditions, orbit/geography, baseline geometry, object proxy/material/charge assumptions, node health, data completeness, interference type, and signal-to-noise ratio. Include a large, representative negative set: lightning, aurora, known transmitters, spacecraft self-noise, clock faults, packet artifacts, and unknown background. Label uncertainty and disagreement rather than forcing a binary label.

All detector results must report detection probability, false-alarm rate, calibration error, latency, and uncertainty by stratum. Global accuracy is not an acceptable scientific metric.

## Independent validation and anti-bias controls

- Pre-register each campaign’s hypothesis, exclusion criteria, metrics, thresholds, and analysis plan before inspecting outcomes.
- Use blinding: analysts evaluating a candidate do not see truth/reference labels or favorable correlation hints until their initial decision is recorded.
- Separate development, validation, confirmation, and release authorities. A team cannot approve its own model and operational product unilaterally.
- Require a competing-hypothesis analysis for every claimed event. The release record must state what alternate explanations were tested and what evidence failed or supported them.
- Conduct independent replication using different code, analysts, and, where feasible, instrument/configuration or data source.
- Publish methods, dataset metadata, calibration limits, negative results, retractions, and uncertainty. Publish data only where law, security, privacy, and partner agreements permit; publish a citable metadata record and rationale where raw release is restricted.
- Never optimize the detector after looking at the blind-test results without declaring that set consumed and creating a new blind test.

## Data governance and security

Apply least-privilege role/attribute-based access. Protect raw operational telemetry, partner data, keys, precise operational state, and pre-release candidate products separately. Enforce encryption, short-lived credentials, access logs, export review, rate limits, malware/schema scanning, and dual approval for sensitive release.

Use a data governance board with science, flight, security, safety, legal/export-control, and independent-review representation. The board approves new sources, label policy, data release, training inclusion, retention/destruction, partner terms, and incident response. Its decisions are immutable audit events.

## Practical first actions

1. Create the data-source registry and product/data contract templates.
2. Obtain or document access to ORDEM/ODPO resources and define exactly which versions support priors and benchmark scenarios.
3. Inventory relevant SPDF/CDAWeb plasma, field, wave, orbit, and ground data; retain each provider’s caveats.
4. Establish the space-weather context feed and archive its versions/timestamps.
5. Design the signed L0 schema, node clock/calibration metadata, evidence archive, and chain-of-custody process before writing the detector.
6. Build controlled signal-injection and blind-label protocols before training any model.
7. Appoint an external validation reviewer/custodian for the blind corpus and Gate reviews.

## What excellence means

There is no honest way to guarantee a prize or infallibility. The credible standard is stronger: every conclusion is reproducible, independently challengeable, quantitatively uncertain, safely reversible, and published with its limitations. If the proposed effect is real, that discipline gives it the best possible chance of earning durable scientific recognition.

