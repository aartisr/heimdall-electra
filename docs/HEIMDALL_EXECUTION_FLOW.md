# Project Heimdall Electra — detailed implementation and evidence flow

## Purpose and current position

This document is the authoritative execution map for Project Heimdall Electra. It orders work so that scientific evidence, safety, provenance, and independent validation always precede scale, automation, or operational claims.

Current position: the project has a reproducible synthetic vertical slice, L0-to-L1 calibration lineage, a transparent candidate detector with plug-in gates, stratified synthetic fixtures, pre-registered experiment controls, a tamper-evident local experiment ledger, a content-addressed ingestion boundary, and contract foundations for timing/association, trade budgets, HIL validation, and a read-only TanStack console. It has **no validated physical wake model, hardware measurement, external observed data, empirical multi-node association, orbital track, operational traffic product, or maneuver authority**. The authoritative implementation status and remaining work are maintained in [the stage delivery ledger](STAGE_DELIVERY_LEDGER.md).

The next implementation stage is Source Authorization and Verification Readiness. It will define approved source records and a replaceable signature-verification port. It must not ingest or label data as observed until an authorized source, terms, integrity method, and independent review are available.

## Governing flow

~~~mermaid
flowchart TD
    A[Mission need: reduce uncertainty about small debris] --> B[Stage 0: claims and evidence matrix]
    B --> C{Hypothesis, metric, confounders, and stop criteria pre-registered?}
    C -- No --> B
    C -- Yes --> D[Stage 1: synthetic physics and forward-model experiments]
    D --> E{Synthetic signature distinguishable within stated assumptions?}
    E -- No --> F[Narrow, redesign, or stop hypothesis]
    E -- Yes --> G[Stage 1A: transparent detector and interference controls]
    G --> H{Locked synthetic validation complete without post-hoc tuning?}
    H -- No --> I[Freeze configuration and create fresh locked corpus]
    I --> H
    H -- Yes --> J[Stage 1B: authorized source and evidence ingestion readiness]
    J --> K{Source, terms, provenance, and strong integrity verification approved?}
    K -- No --> L[Remain synthetic or laboratory only]
    K -- Yes --> M[Stage 2: laboratory and hardware-in-loop calibration]
    M --> N{Measurement chain calibrated and uncertainty bounded?}
    N -- No --> M
    N -- Yes --> O[Stage 3: multi-node time and association research]
    O --> P{Confidence calibration and false association budget satisfied?}
    P -- No --> O
    P -- Yes --> Q[Stage 4: flight demonstration]
    Q --> R{Independent replication and alternate-explanation review support claim?}
    R -- No --> S[Report limitations and iterate or stop]
    R -- Yes --> T[Stage 5: governed advisory data product]
    T --> U{Safety authority approves constrained operational use?}
    U -- No --> T
    U -- Yes --> V[Constrained decision support only]
~~~

No arrow allows a result to bypass a gate. A negative result, a failed gate, or inability to establish an authentic source is a valid outcome that prevents unsupported advancement.

## Current implementation flow

~~~mermaid
flowchart LR
    subgraph Synthetic truth
        S1[Versioned SyntheticScenario]
        S2[Deterministic seed and scenario digest]
        S3[Raw-like waveform, clock, health metadata]
        S1 --> S2 --> S3
    end

    subgraph Scientific data plane
        L0[ObservationL0: immutable input contract]
        L1[CalibratedObservationL1: non-destructive transform]
        D[Baseline matched filter: raw score]
        G1[PeakContrastGate]
        G2[ClockQualityGate]
        L2[CandidateL2: score, gate metrics, decision reasons]
        S3 --> L0 --> L1 --> D
        D --> G1 --> G2 --> L2
    end

    subgraph Research governance
        R1[ThresholdPolicy]
        R2[Sealed ExperimentPlan]
        R3[Execute only matching registry, detector, threshold, gates]
        R4[Hash-chained experiment ledger]
        R1 --> R2 --> R3 --> R4
        R3 -. controls .-> D
        R3 -. controls .-> G1
        R3 -. controls .-> G2
    end

    subgraph Evidence ingestion
        I1[Registered and approved source]
        I2[Expected digest or stronger verification]
        I3[Content-addressed original bytes]
        I4[Append-only acquisition manifest]
        I1 --> I2 --> I3 --> I4
    end
~~~

### What each implemented layer may honestly claim

| Layer | Current capability | It may claim | It must not claim |
|---|---|---|---|
| Synthetic generator | Repeatable test fixtures | A deterministic fixture was generated from stated assumptions | Plasma wake physics is proven |
| L0/L1 contracts | Preserved lineage and calibration metadata | The transform and parent artifact are traceable | A sensor has been calibrated in flight |
| Baseline detector | Transparent signal-score calculation | A fixture matches its mathematical template | A debris object was detected |
| Candidate gates | Explicit policy rejection | A fixture passes/fails stated synthetic policies | Interference is solved generally |
| Stratified evaluation | Fixture-level TP/FP/TN/FN accounting | Performance on named fixtures | Generalized laboratory or orbital performance |
| Experiment ledger | Chained, tamper-evident local record | A recorded local chain verifies after write | Independent signing, timestamp authority, or non-repudiation |
| Ingestion boundary | Byte preservation and expected-digest check | Ingested bytes match approved expected digest | Source identity, measurement authenticity, or physics validity |

## Detailed evidence lifecycle

~~~mermaid
flowchart TD
    A[Source proposal or generated artifact] --> B[Source registry review]
    B --> C{Owner, terms, classification, purpose, retention, and permitted evidence class complete?}
    C -- No --> D[Reject or request source clarification]
    C -- Yes --> E[Integrity method review]
    E --> F{Approved method available?}
    F -- Synthetic --> G[Known expected SHA-256 from controlled generator]
    F -- Laboratory or observed --> H[Verified instrument/provider signature or equivalent approved method]
    F -- No --> I[Do not ingest as evidence]
    G --> J[Retrieve or produce bytes]
    H --> J
    J --> K[Verify expected digest or signature]
    K --> L{Verification passes?}
    L -- No --> M[Quarantine: preserve failure event, do not create product]
    L -- Yes --> N[Content-addressed immutable raw object]
    N --> O[Acquisition manifest: source, proof, time, media, digest, class]
    O --> P[Access and retention policy]
    P --> Q[Create L0 reference, never alter original]
    Q --> R[Calibrate to L1]
    R --> S[Quality checks and detector]
    S --> T[Candidate, association, or rejected decision with lineage]
    T --> U[Experiment/release ledger]
    U --> V[Authorized review or publication]
~~~

### Required authenticity controls by evidence class

| Evidence class | Entry condition | Minimum verification | Promotion rule |
|---|---|---|---|
| Synthetic | Controlled generator and versioned scenario | Deterministic scenario/configuration digest and output SHA-256 | Never promote beyond synthetic |
| Laboratory | Calibrated test setup with traceable log | Instrument/configuration identity, expected digest, signed or controlled acquisition record | Independent replication and calibration review |
| Observed | Approved instrument or provider with authority to provide data | Cryptographically verified source/instrument signature, time/clock quality, acquisition chain, access review | Independent alternate-explanation analysis and defined validation policy |
| Derived | Parent evidence already preserved | All parent IDs plus transformation/calibration/model/configuration/build versions | Inherits the weakest parent evidence class unless separately validated |

## Candidate decision flow

~~~mermaid
flowchart TD
    A[L0 raw reference] --> B[Verify payload digest and schema]
    B --> C{Valid and complete enough?}
    C -- No --> C1[Quality-rejected record with reason]
    C -- Yes --> D[L1 calibration without changing L0]
    D --> E[Detector Strategy computes raw score and window features]
    E --> F{Raw score meets sealed threshold?}
    F -- No --> G[No candidate; retain score and provenance]
    F -- Yes --> H[Run ordered CandidateGate strategies]
    H --> I{Every gate passes?}
    I -- No --> J[Rejected high-score candidate; retain raw score, metrics, and reasons]
    I -- Yes --> K[L2 accepted candidate]
    K --> L{Multi-node association and uncertainty gate available and passed?}
    L -- Not implemented or no --> M[Candidate only; no orbital state claim]
    L -- Yes --> N[L3 associated event with covariance and ambiguity set]
    N --> O{Independent validation and release policy pass?}
    O -- No --> P[Restricted research result]
    O -- Yes --> Q[Approved advisory L5 product]
~~~

The current code reaches L2 only. It deliberately has no L3, L4, or L5 implementation.

## Plug-in architecture and extension points

~~~mermaid
classDiagram
    class SyntheticScenario {
        +scenario_id
        +seed
        +parameters
        +expected_signal synthetic-only
    }
    class EvidenceStore {
        <<Protocol>>
        +put(payload) digest
        +read(digest) bytes
    }
    class ManifestLedger {
        <<Protocol>>
        +append(manifest) digest
    }
    class CandidateGate {
        <<Protocol>>
        +assess(context) GateDecision
    }
    class ExperimentLedger {
        <<Protocol>>
        +append(event_type, payload) LedgerEvent
        +verify() bool
    }
    class FileEvidenceStore
    class JsonlManifestLedger
    class PeakContrastGate
    class ClockQualityGate
    class JsonlExperimentLedger

    EvidenceStore <|.. FileEvidenceStore
    ManifestLedger <|.. JsonlManifestLedger
    CandidateGate <|.. PeakContrastGate
    CandidateGate <|.. ClockQualityGate
    ExperimentLedger <|.. JsonlExperimentLedger
    SyntheticScenario --> ObservationL0
    ObservationL0 --> CalibratedObservationL1
    CalibratedObservationL1 --> CandidateL2
~~~

Stable ports enable replacement without rewriting science logic:

- Replace FileEvidenceStore with object-lock or mission archive storage.
- Replace JsonlManifestLedger with a signed data catalog.
- Replace JsonlExperimentLedger with an independently operated WORM/signed ledger.
- Add source-specific signature verifiers behind a verification port.
- Add new CandidateGate strategies only through sealed policy and fresh validation.
- Add alternate detector strategies without changing L0/L1/L2 contracts.
- Add future multi-node association only as a separate bounded context consuming accepted L2 evidence.

## Stage-by-stage execution plan

### Stage 0 — claims, governance, and contracts

Status: partial foundation implemented; formal approval and independent review remain open. See the stage delivery ledger.

Complete only when claims, metrics, stop conditions, product levels, data classification, provenance, and security boundaries are approved.

### Stage 1 — synthetic vertical slice and transparent baseline

Status: synthetic vertical-slice milestone complete; the broader physics/synthetic-truth stage remains in progress. See the stage delivery ledger.

Complete only when deterministic synthetic generation, L0/L1 lineage, detector, gate interfaces, stratified evaluation, and replay work without external data.

### Stage 1A — locked synthetic validation

Status: fixture-level controls are implemented; an independently held, sufficiently diverse locked corpus is not yet available.

Complete only when an independently held, sufficiently diverse locked corpus exists; the pre-registered policy is evaluated once; performance intervals and strata are reported; and any tuning uses a new corpus.

### Stage 1B — source authorization and verification readiness

Status: source registry, verification, custody, signed-frame, time-quality, and observed-provenance controls are implemented. No approved observed Heimdall Electra source or reviewed time contract exists.

Implement in this order:

1. Define a versioned source-registry record: owner, terms, purpose, classification, retention, evidence class, verification scheme, authorized reviewer, and status.
2. Add a VerificationStrategy port with a no-op prohibition: only approved implementations can return verified.
3. Keep the present SHA-256 expected-digest path limited to synthetic fixtures.
4. Add a source-specific adapter only after its terms and verification documentation are reviewed.
5. Add independent source/clock/quality review before any Laboratory or Observed class is accepted.
6. Store raw bytes and manifest in durable access-controlled storage.
7. Create a pre-registered ingestion and validation campaign; no algorithm tuning from first observed data.

Gate: an independent reviewer can reproduce the source authorization, byte verification, raw preservation, and provenance chain. Until then remain synthetic-only.

### Stage 2 — laboratory and hardware-in-the-loop

Partial foundation implemented: HIL test-plan/result, calibration, and ingestion contracts exist. No hardware or laboratory measurement has been performed.

Use controlled injection, traceable timing, sensor transfer-function characterization, clock/error budgets, EMC/self-noise tests, and replay through unchanged software. Compare to controlled truth and publish discrepancies.

Gate: hardware behavior, calibration, and uncertainty are bounded within pre-registered limits.

### Stage 3 — multi-node association and kinematic inference

Partial foundation implemented: timing, association, covariance, solver-neutral TDOA, and inference-lifecycle contracts exist. No empirical association or localization result exists.

Add a separate association context that consumes L2 records, verifies time/ephemeris/attitude quality, produces TDOA/FDOA residuals, tracks ambiguity, and propagates covariance. An association score is not object identity.

Gate: empirical uncertainty coverage agrees with stated confidence and false association remains below budget.

### Stage 4 — demonstrator and independent flight validation

Partial foundation implemented: coverage, instrument, and transport budget contracts exist. No validated demonstrator or flight campaign exists.

Use pre-registered observing campaigns, preserved raw data, blind analysis, independent references, red-team alternate-explanation review, and publication of negative results.

Gate: independent evidence supports only the precise, bounded claim earned by the data.

### Stage 5 — governed advisory product

Partial foundation implemented: durable evidence, audit, lifecycle, and read-only TanStack status-console controls exist. No validated product, authorization service, or advisory release exists.

Only after validated L3/L4 products: build standards adapters, role-specific TanStack views, release/retraction state machine, SLOs, audit, and safety-authority approval. The browser never becomes the system of record or spacecraft command path.

## Required review checkpoints

~~~mermaid
flowchart LR
    R0[Gate 0: claims and safety] --> R1[Gate 1: synthetic physics]
    R1 --> R1A[Gate 1A: locked corpus]
    R1A --> R1B[Gate 1B: source authenticity]
    R1B --> R2[Gate 2: laboratory/HIL]
    R2 --> R3[Gate 3: association]
    R3 --> R4[Gate 4: flight validation]
    R4 --> R5[Gate 5: advisory release]

    R0 -. independent review .-> X[Advance, narrow, redesign, or stop]
    R1 -. independent review .-> X
    R1A -. independent review .-> X
    R1B -. independent review .-> X
    R2 -. independent review .-> X
    R3 -. independent review .-> X
    R4 -. independent review .-> X
    R5 -. ongoing assurance .-> X
~~~

## Immediate next actions

1. Create the versioned source-registry contract and source-approval workflow.
2. Define the VerificationStrategy port and tests that prohibit observed classification with only a digest.
3. Add an approved signature-verifier adapter only once a real, authorized source and verification format are selected.
4. Expand the synthetic corpus independently of detector tuning and record confidence intervals rather than fixture-only fractions.
5. Do not add ML, multi-node tracking, hardware procurement, or a production TanStack console before the above gates are completed.

## Non-negotiable stop rules

- Do not label synthetic or laboratory records observed.
- Do not use a checksum as proof of provider or instrument identity.
- Do not tune against a consumed locked or blind corpus.
- Do not remove high-score rejected candidates from evidence or metrics.
- Do not derive orbital tracks, collision probabilities, or maneuver recommendations from L2 candidates.
- Do not promote a local hash chain into a claim of external audit, cryptographic signing, or non-repudiation.
