# HEIMDALL ELECTRA — Observed Evidence Acquisition Guide

**Author:** Aarti S Ravikumar ([@aartisr](https://github.com/aartisr))
**Date:** 2026-08-03
**Evidence class of this document:** Research plan — not itself evidence
**Prerequisite reading:** [STAGE_DELIVERY_LEDGER.md](STAGE_DELIVERY_LEDGER.md), [REAL_WORLD_GATE_ACQUISITION_PLAYBOOK.md](REAL_WORLD_GATE_ACQUISITION_PLAYBOOK.md), [HEIMDALL_FALSIFIABLE_RESEARCH_PROTOCOL.md](HEIMDALL_FALSIFIABLE_RESEARCH_PROTOCOL.md)

---

## Purpose

This document provides concrete, actionable instructions for acquiring real observed evidence — the transition from `EvidenceClass.SYNTHETIC` to `EvidenceClass.OBSERVED`. It covers four pathways ordered by cost and speed, the governance steps required at each stage, hardware and software specifics, partnership targets, and the exact repository ingestion path that real data must follow to become governed evidence.

No pathway here guarantees a positive scientific result. A null result, a detection below threshold, or a failed correlation is a valid and valuable outcome. The governance framework is designed to preserve negative results with the same care as positive ones.

---

## Table of Contents

1. [Where We Are Today](#1-where-we-are-today)
2. [The Evidence Promotion Ladder](#2-the-evidence-promotion-ladder)
3. [Governance Prerequisites Before Any Real Data Collection](#3-governance-prerequisites-before-any-real-data-collection)
4. [Pathway A — Archive Mining (Weeks, ~$0)](#4-pathway-a--archive-mining-weeks-0)
5. [Pathway B — Low-Cost SDR Array (~$1,500, Weeks to Months)](#5-pathway-b--low-cost-sdr-array-1500-weeks-to-months)
6. [Pathway C — Observatory Partnership (Months, Low Direct Cost)](#6-pathway-c--observatory-partnership-months-low-direct-cost)
7. [Pathway D — Dedicated Flight Instrument (Years, $1M–$10M)](#7-pathway-d--dedicated-flight-instrument-years-1m10m)
8. [Ingesting Real Data Into the Repository](#8-ingesting-real-data-into-the-repository)
9. [Pre-Registration Checklist](#9-pre-registration-checklist)
10. [Independent Review Requirements](#10-independent-review-requirements)
11. [Regulatory and Legal Checklist](#11-regulatory-and-legal-checklist)
12. [Failure Modes and How to Handle Them](#12-failure-modes-and-how-to-handle-them)
13. [Evidence Package Templates](#13-evidence-package-templates)
14. [Resource and Timeline Summary](#14-resource-and-timeline-summary)

---

## 1. Where We Are Today

The Stage Delivery Ledger is unambiguous: **zero primary stage gates are closed**. Every result in the repository is `EvidenceClass.SYNTHETIC`. This is scientifically honest and correct. It means:

- No physical wake model has been admitted
- No calibrated hardware result exists
- No observed HEIMDALL ELECTRA measurement exists
- No debris track, collision prediction, or maneuver authority exists

The software foundation — contracts, governance, ingestion boundary, audit trails, pre-registration framework — is complete and ready to receive real evidence. What is missing is the evidence itself.

The dependency-safe path from the ledger:

```
Stage 1 physics model evidence  ──►  Stage 2 detector assessment
        ──►  Stage 3 timing/association  ──►  Stage 5 HIL/laboratory
                ──►  Stage 6 flight demonstration
```

This guide addresses Stages 1 (physics model validation) and 5 (laboratory/hardware-in-loop) as the two gates most immediately actionable with real observed data.

---

## 2. The Evidence Promotion Ladder

```
SYNTHETIC ──────────────────────────────────────────────────────────
  Deterministic fixture, model output, versioned scenario, seed.
  Permitted: software verification, sensitivity analysis, development.
  Prohibited: physical claim, hardware performance, flight assertion.

        │  New evidence: controlled measurement with traceable calibration
        ▼
LABORATORY ──────────────────────────────────────────────────────────
  Calibrated controlled measurement with preserved raw data.
  Permitted: measurement-chain characterization, controlled validation.
  Prohibited: flight performance claim, uncontrolled debris observation.

        │  New evidence: authorized source/instrument with raw bytes,
        │  manifest, timing, provenance review, and independent QA
        ▼
OBSERVED ────────────────────────────────────────────────────────────
  Authorized real-world instrument record with full lineage.
  Permitted: carefully bounded scientific analysis.
  Prohibited: object identity claim, operational action without
              additional independent validation.

        │  New evidence: blinded protocol, independent reference,
        │  alternative explanations examined, independent review
        ▼
INDEPENDENTLY REVIEWED ──────────────────────────────────────────────
  Peer-reviewed with documented dissent and alternative explanations.
  Permitted: bounded scientific claim with stated limitations.
  Prohibited: operational traffic product, maneuver authority.
```

Each arrow requires **new, independent evidence**. A software improvement, a better visualization, or a stronger argument does not move the ladder.

---

## 3. Governance Prerequisites Before Any Real Data Collection

**These must be completed before any real instrument is switched on or any archive data is analyzed for HEIMDALL purposes. Skipping any step makes the resulting evidence inadmissible under the project's own governance rules.**

### 3.1 Pre-Register the Analysis Plan

Before touching real data, create and seal a pre-registered experiment plan using the existing governance infrastructure:

```bash
mkdir -p data/local/runs

PYTHONPATH=src python3.11 scripts/run_pre_registered_experiment.py \
  --ledger      data/local/runs/observed-campaign-ledger.jsonl \
  --audit-bundle data/local/runs/observed-campaign-plan.json \
  --generated-at <ISO-8601 timestamp before analysis begins> \
  --artifact    config/research/claims.json \
  --artifact    config/research/gates.json
```

The plan must declare:
- The exact primary hypothesis ("A transient electron density perturbation correlated with the transit of TLE object X within Y km at time T is detectable above noise threshold Z at confidence P")
- The primary metric (detection threshold, correlation significance)
- The null result criterion (below what correlation coefficient do we declare no detection)
- The stopping rule (if X% of observations show no signal, we halt)
- The analysis method (cross-correlation window, frequency band, statistical test)
- The confounders list (ionospheric scintillation, RFI, meteor ablation, calibration errors)

### 3.2 Establish Data Management Plan

Before receiving any real data from a partner or instrument:

- Designate a **data steward** independent of the PI
- Define the storage location, access controls, and retention period
- Define what constitutes a "raw artifact" (the exact bytes from the instrument, before any processing)
- Create a custody record template matching the `Provenance` dataclass in `domain.py`

### 3.3 Register the Instrument Source

Real instruments must be registered before data from them is ingested. Create an entry in `config/sources/source_registry.json` for the planned source with:

```json
{
  "source_id": "eiscat_uhf_tromso_2026",
  "source_type": "ionospheric_radar",
  "provider": "EISCAT Scientific Association",
  "data_agreement_reference": "<agreement ID or URL>",
  "classification": "unclassified",
  "permitted_purpose": "scientific_research",
  "retention_policy": "retain_5_years",
  "retraction_path": "contact eiscat-data@eiscat.se",
  "calibration_reference": "EISCAT UHF system manual v3.2",
  "timing_reference": "UTC via GPS, ±100ns",
  "evidence_class_ceiling": "observed"
}
```

The `instrument_ingestion.py` and `signed_instrument_ingestion.py` contracts enforce that data can only enter the `observed` class from a pre-registered, approved source.

### 3.4 Appoint Independent Reviewer

Identify a person with no stake in a positive result who will review the evidence package after collection. This person must:
- Have relevant expertise (plasma physics, radio instrumentation, or ionospheric science)
- Have no financial or professional incentive tied to a positive result
- Be willing to produce a written review accepting, narrowing, or rejecting the gate

Document their name, affiliation, and conflict-of-interest declaration before analysis begins.

---

## 4. Pathway A — Archive Mining (Weeks, ~$0)

### What It Is

Re-analyze publicly available ionospheric observatory data for plasma perturbations correlated with known debris transits. The debris objects' orbital parameters are independently verified by USSPACECOM. The instruments' calibration is independently maintained by the observatories. The only new work is the conjunction computation and statistical correlation.

### What Evidence Class It Can Produce

`EvidenceClass.OBSERVED` — provided the data agreement with the observatory explicitly permits this use, the raw bytes are preserved with full provenance, and the analysis is pre-registered.

### Step-by-Step Instructions

#### Step A1 — Get the TLE Catalog

```bash
# Download current TLE catalog from CelesTrak (free, public domain)
curl -o data/external/tle_catalog.txt \
  "https://celestrak.org/SOCRATES/query.php?CODE=ALL&FORMAT=TLE"

# Or for all objects > 1 m (higher SNR potential):
curl -o data/external/tle_debris_large.txt \
  "https://celestrak.org/pub/TLE/debris.txt"
```

The TLE format gives semi-major axis, eccentricity, inclination, RAAN, and mean motion for every tracked object. Use these to compute ground tracks and predict when each object was overhead any given observatory.

#### Step A2 — Install the SGP4 Propagator

```bash
pip install sgp4        # Brandon Rhodes' Python implementation (BSD license)
pip install skyfield    # Higher-level wrapper, also uses SGP4
```

No other third-party dependencies needed for orbital propagation.

#### Step A3 — Compute Conjunctions

Write a script (using the `trajectory_risk.py` module planned in DEBRIS_VISUALIZATION_PLAN.md) that:

1. Loads TLE elements for all tracked objects
2. Propagates each object through the observation epoch at 1-second time steps
3. Computes the object's position in geodetic (lat/lon/alt) coordinates
4. Checks whether the object's ground track passes within the field of view of the target observatory
5. Records the conjunction time, object ID, altitude, azimuth, elevation, and relative velocity

**Observatory fields of view to target:**

| Observatory | Lat | Lon | Instrument | Beam width | HEO altitude range |
|---|---|---|---|---|---|
| EISCAT UHF Tromsø | 69.6°N | 19.2°E | Incoherent scatter radar | ~0.6° | 100–1,500 km |
| EISCAT VHF Tromsø | 69.6°N | 19.2°E | Incoherent scatter radar | ~3° | 100–2,000 km |
| Millstone Hill | 42.6°N | 288.5°E | ISR | ~0.6° | 100–1,000 km |
| Jicamarca | -12.0°N | 283.2°E | ISR | ~1° | 100–1,500 km |

For EISCAT UHF: an object at 400 km altitude must pass within ~2 km of the beam center to be within the 0.6° beam. This constrains the effective angular cross-section. Compute the fraction of known debris objects that transit within beam each day — typically 5–50 events per 24-hour period for a 400 km altitude shell.

#### Step A4 — Request EISCAT Data

**Contact:** data@eiscat.se

**What to request:**
- Raw alternating-code or long-pulse data products (not summary plots)
- Specifically: raw complex voltage samples at the receiver output, or at minimum the raw plasma parameter estimates at 1-second or sub-second time resolution
- For each identified conjunction window: 5 minutes of data centered on the predicted transit time

**Access pathway:**
- EISCAT data is available to researchers affiliated with EISCAT member countries (Norway, Sweden, Finland, UK, Germany, France, Japan, China, associate members)
- Non-member institutions apply for Associate Membership (~€5,000/year) or negotiate a Data Use Agreement
- The EU RIRIS (Research Infrastructure for Radio Instrumentation Science) program provides open access pathways
- A letter from a university or research institution affirming the scientific purpose typically suffices

**Data format:** EISCAT delivers data in Madrigal HDF5 format. The `madrigalWeb` Python client retrieves it programmatically:

```python
import madrigalWeb.madrigalWeb as madrigal

# Connect to EISCAT Madrigal server
mad_obj = madrigal.MadrigalData("https://portal.eiscat.se/madrigal")

# List available experiments for a date range
exps = mad_obj.getExperiments(30, 2026, 1, 1, 0, 0, 0,  # instrument 30 = EISCAT UHF
                               2026, 12, 31, 23, 59, 59)

# Download raw data files
for exp in exps:
    files = mad_obj.getExperimentFiles(exp.id)
    for file in files:
        mad_obj.downloadFile(file.name, "data/external/eiscat/", "anonymous", "anonymous", "anonymous", "hdf5")
```

#### Step A5 — Request SWARM In-Situ Data

ESA's SWARM constellation (three satellites at ~460–510 km) carries Langmuir probes measuring electron density at 2 Hz (LP_HM product) and 16 Hz (LP_FP product). This is in-situ plasma measurement, not radar — it measures the plasma directly at satellite altitude.

**Access:** ESA Earth Online, free, no registration required for most products.

```bash
# Install ESA SWARM access client
pip install viresclient

# Download electron density data
python3 << 'EOF'
from viresclient import SwarmClient
import datetime

client = SwarmClient()

# Request 1 hour of LP fast-pace data around a known conjunction time
request = client.get_between(
    collection="SW_OPER_EFIA_LP_1B",   # Swarm Alpha Langmuir probe
    start_time=datetime.datetime(2026, 6, 15, 12, 0, 0),
    end_time=datetime.datetime(2026, 6, 15, 13, 0, 0),
    measurements=["Ne", "Te", "U_orbit", "Latitude", "Longitude", "Radius"],
)
df = request.as_dataframe()
df.to_csv("data/external/swarm/swarm_alpha_20260615_1200.csv")
EOF
```

**What to look for:** A transient dip or enhancement in electron density (`Ne`) lasting 0.1–2 seconds (consistent with a debris object passing through the plasma at ~7.5 km/s relative velocity). Correlate the timing with TLE conjunction predictions.

#### Step A6 — Statistical Analysis Protocol

**Pre-register before executing:**

```python
# Analysis plan — seal this before looking at data
analysis_plan = {
    "primary_hypothesis": "plasma_perturbation_correlated_with_ttle_conjunction",
    "primary_metric": "pearson_correlation_conjunction_time_vs_delta_ne",
    "significance_threshold": 0.05,
    "minimum_conjunction_count": 20,
    "confounders": [
        "ionospheric_scintillation",
        "meteor_ablation",
        "radio_frequency_interference",
        "calibration_drift",
        "cosmic_ray_events",
    ],
    "null_result_criterion": "correlation < 0.1 with p > 0.2 after N >= 20 events",
    "stopping_rule": "halt if first 10 events show mean SNR < 0 dB",
    "analysis_window_s": 30,
    "pre_conjunction_baseline_s": 300,
}
```

**Analysis steps:**
1. For each conjunction event, extract a 30-second window of plasma data centered on the predicted transit time
2. Subtract the 5-minute pre-conjunction baseline (mean ± std)
3. Compute the peak normalized perturbation δNe/Ne in the window
4. Repeat for 100 random non-conjunction windows from the same day (control set)
5. Compare the distribution of δNe/Ne between conjunction and control sets
6. Apply a two-sample Kolmogorov-Smirnov test; report the KS statistic and p-value
7. Apply a Bonferroni correction for multiple conjunctions

#### Step A7 — Ingest Into the Repository

Once analysis is complete (positive or negative), ingest the raw data and results:

```bash
# Ingest the raw EISCAT data file as external_context evidence
PYTHONPATH=src python3.11 scripts/ingest_artifact.py \
  --artifact data/external/eiscat/eiscat_uhf_20260615_1200.hdf5 \
  --evidence-class observed \
  --store-root data/local/evidence

# Ingest the analysis result
PYTHONPATH=src python3.11 scripts/ingest_artifact.py \
  --artifact data/local/analysis/conjunction_correlation_result.json \
  --evidence-class observed \
  --store-root data/local/evidence
```

---

## 5. Pathway B — Low-Cost SDR Array (~$1,500, Weeks to Months)

### What It Is

Deploy a coherent multi-receiver array using commodity software-defined radio hardware on the ground. Use a GPS-disciplined oscillator (GPSDO) to maintain phase coherence across all receivers. This exercises the full HEIMDALL signal chain — from raw RF to calibrated observation — with controllable hardware.

This pathway first produces `EvidenceClass.LABORATORY` (with signal injection) and then `EvidenceClass.OBSERVED` (with real sky data correlated against TLE transits).

### Hardware Bill of Materials

| Component | Model | Quantity | Unit Cost (USD) | Subtotal | Purpose |
|---|---|---|---|---|---|
| SDR receiver | RTL-SDR V4 (0.5–1.75 GHz) | 4 | $40 | $160 | Four-element passive receive array |
| GPS-disciplined oscillator | Leo Bodnar mini GPSDO | 1 | $160 | $160 | 10 MHz phase reference, <1 ppb stability |
| GPSDO distribution amp | Mini-Circuits ZFSC-4-1+ | 1 | $30 | $30 | Distribute 10 MHz to all four receivers |
| Low-noise amplifier | Nooelec LaNA (0.1–2 GHz, 0.6 dB NF) | 4 | $45 | $180 | Preamplification before receiver |
| Antenna | LPDA (50–1300 MHz, 6 dBi, outdoor) | 4 | $80 | $320 | Directional receive (point toward zenith) |
| SMA coaxial cable (3 m) | LMR-195, SMA-SMA | 8 | $12 | $96 | LNA-to-receiver connections |
| Raspberry Pi 4 (4 GB) | Standard | 4 | $55 | $220 | Per-node data acquisition |
| MicroSD card (128 GB) | Samsung EVO | 4 | $15 | $60 | Local per-node buffer |
| Gigabit ethernet switch | Unmanaged, 8-port | 1 | $25 | $25 | Inter-node synchronization |
| Power over Ethernet injector | Standard PoE | 4 | $12 | $48 | Power Raspberry Pi and LNA from cable |
| Weatherproof enclosure | Standard IP67 | 4 | $20 | $80 | Outdoor deployment |
| Signal generator (calibration) | Rigol DSG815 or similar | 1 | $350 | $350 | Inject known test signals for LABORATORY step |
| **Total** | | | | **~$1,729** | |

The signal generator is only needed for the LABORATORY evidence step. The rest supports ongoing OBSERVED data collection.

### Receiver Array Configuration

**Phase coherence approach:**
The four RTL-SDR V4 units each have a 10 MHz TCXO reference input. By driving all four from the same GPSDO 10 MHz output (via the distribution amplifier), all four receivers share a common phase reference locked to GPS time. This enables:
- Coherent cross-correlation between receivers
- TDOA measurements with nanosecond-class precision (limited by cable length calibration)
- Direction finding (AOA — angle of arrival) from the inter-receiver phase differences

**Antenna baseline:**
For a four-element array with ~10 m baselines, the angular resolution at 150 MHz (1.95 m wavelength) is approximately:
```
θ_resolution ≈ λ / D ≈ 1.95 m / 10 m ≈ 11°
```
Sufficient to distinguish overhead events from ground-level RFI by elevation angle.

**Frequency selection:**
The ionospheric plasma frequency at 300 km altitude (typical daytime electron density 10¹¹ m⁻³) is approximately 2.8 MHz. For HF signals to penetrate to this altitude, the receiver must operate above the plasma frequency. The VHF range (30–300 MHz) is the primary target band:
- 50 MHz (6 m amateur band): good ionospheric penetration, internationally allocated
- 144–148 MHz (2 m amateur band): standard for ionospheric sounding
- The RTL-SDR V4 covers 500 kHz–1.75 GHz — fully adequate

### Software Stack

All open source:

```bash
# Core SDR drivers
pip install pyrtlsdr      # RTL-SDR Python bindings

# GNU Radio (Raspberry Pi): install via apt
sudo apt install gnuradio python3-gnuradio

# GPS disciplined timing
pip install gpsd-py3

# Signal processing
pip install numpy scipy    # for isolation in adapter modules only
pip install h5py           # HDF5 data format (matches EISCAT format)
```

### Step-by-Step: LABORATORY Evidence

The LABORATORY step uses a controlled signal injection to characterize the receiver chain's response before exposing it to real sky data.

**Laboratory test protocol:**

1. Connect the signal generator output through a 60 dB attenuator to the antenna port of receiver #1
2. Configure the signal generator to output a 150 MHz CW tone at −80 dBm (typical plasma signal level)
3. Sweep the signal through a known Doppler profile (0–500 Hz/s, simulating an overhead LEO pass)
4. Record the raw IQ samples from all four receivers simultaneously
5. Process the data through the planned detection pipeline
6. Verify that the injected signal is recovered with the correct Doppler profile and timing
7. Characterize the false alarm rate by running the pipeline on 100 noise-only windows

This produces `EvidenceClass.LABORATORY` — a controlled measurement with traceable calibration.

**Ingest the calibration result:**

```bash
# Record the signal generator settings and calibration certificate
PYTHONPATH=src python3.11 scripts/ingest_artifact.py \
  --artifact data/local/calibration/sdr_array_lab_cal_20260815.json \
  --evidence-class laboratory \
  --store-root data/local/evidence
```

### Step-by-Step: OBSERVED Evidence

**Deployment site selection:**
- Site with low local RFI (rural, >10 km from major roads and buildings)
- Open sky view to zenith (no obstructions above 30° elevation)
- GPS signal available
- Internet access for time sync and data upload

**Observing campaign:**
1. Deploy the array and verify phase coherence (all four receivers locked to GPSDO)
2. Run the array continuously for a minimum of 14 days
3. During this time, use the TLE conjunction computation (Step A3) to identify predicted overhead transits
4. For each predicted transit: extract a 60-second raw IQ data window
5. Run the pre-registered detection pipeline on each window
6. Record all results — detections, non-detections, noise-dominated windows equally

**Key: a non-detection is as valid as a detection.** If the signal is below threshold for all predicted transits, that is a scientifically valuable result and must be preserved with the same governance as a positive detection.

---

## 6. Pathway C — Observatory Partnership (Months, Low Direct Cost)

### What It Is

Approach an established ionospheric observatory and propose a joint observing campaign. They provide the hardware, spectrum licenses, calibration infrastructure, and institutional credibility. HEIMDALL provides the analysis protocol, conjunction computation, and governance framework.

### Target Institutions and Contact Approach

#### EISCAT Scientific Association

**Why:** The world's most sensitive ionospheric radar network. The Tromsø UHF system at 930 MHz has a minimum detectable density perturbation of ~0.1% — potentially sufficient to detect wake signatures from objects >10 cm diameter.

**How to approach:**
1. Write a 2-page letter of intent to the EISCAT Director (director@eiscat.se) describing:
   - The narrow measurement question (not the full HEIMDALL vision)
   - The specific observing geometry (altitude, beam direction, target population)
   - The required data products (raw plasma parameter estimates, not reduced summary data)
   - The proposed duration (minimum 1 week for statistical validity)
   - The pre-registration and governance framework
   - The explicit null result publication commitment
2. Submit a formal observing proposal through the EISCAT proposal portal (proposals.eiscat.se)
3. Proposals reviewed three times per year; allow 4–8 weeks for review

**Collaboration model:** EISCAT provides instrument time (measured in "EISCAT Units" or "ILTs"), data, and technical support. HEIMDALL contributes the analysis protocol and co-authorship on any publication. Data is jointly owned with negotiated terms.

**Instrument time cost:** Standard EISCAT time is allocated to member-country institutions. For non-member access, typical cost is €1,000–€5,000 per day of observing time. A 7-day campaign costs approximately €7,000–€35,000 — modest by research standards.

#### Millstone Hill Observatory (MIT Haystack)

**Why:** US-based incoherent scatter radar facility with extensive experience in space situational awareness adjacent research. MIT Haystack has published debris detection studies.

**Contact:** Director, Millstone Hill Observatory, via https://www.haystack.mit.edu/

**Special advantage:** MIT Haystack has existing relationships with MIT Lincoln Laboratory and the US Space Force Space Surveillance Network — potential pathway to correlated independent tracking data.

#### SuperDARN (Super Dual Auroral Radar Network)

**Why:** 35 HF radar stations globally, operating 8–20 MHz. Covers both polar regions with large spatial extent. Existing real-time data access for research purposes.

**Contact:** SuperDARN Principal Investigators group, via superdarn.ca/contact

**Special advantage:** Multiple stations allow multi-static correlation across large baselines — stronger evidence than any single observatory.

#### NOAA National Centers for Environmental Information (NCEI)

**Why:** NOAA maintains the Digisonde network and archives ionospheric data globally. The GIRO (Global Ionosphere Radio Observatory) portal provides access to 60+ Digisonde stations with long continuous archives.

**Access:** Entirely free, no partnership needed.

```bash
# Access GIRO data via the Madrigal client
pip install madrigalWeb

python3 << 'EOF'
import madrigalWeb.madrigalWeb as madrigal
mad = madrigal.MadrigalData("http://cedar.openmadrigal.org/")
# List all ionospheric sounders worldwide
instruments = mad.getAllInstruments()
for inst in instruments:
    if "digisonde" in inst.name.lower() or "ionosonde" in inst.name.lower():
        print(f"{inst.code}: {inst.name} ({inst.latitude:.1f}°, {inst.longitude:.1f}°)")
EOF
```

### Proposal Template

A strong partnership proposal includes:

```
Title: Correlation of Ionospheric Plasma Perturbations With LEO Debris Transits:
       A Pre-Registered Observational Study

1. Scientific Question (1 paragraph, falsifiable, bounded)
   - Primary: Can a coherent plasma perturbation be detected above the noise
     floor of [instrument] for predicted transits of known TLE objects >50 cm
     diameter at 300–600 km altitude?
   - Pre-declared null result: No detection above 0.5σ noise floor in ≥15
     predicted conjunction events.

2. Methodology (1 page)
   - Conjunction computation method (SGP4 + instrument beam geometry)
   - Data products required (raw vs. processed, time resolution needed)
   - Statistical analysis plan (pre-registered before data access)
   - Confounder list and mitigation (scintillation, meteor, RFI)
   - Control analysis (identical analysis on non-conjunction windows)

3. Governance (0.5 page)
   - Pre-registration reference (sealed ledger entry)
   - Data stewardship plan (raw byte preservation, custody chain)
   - Null result publication commitment
   - Independent review plan

4. Team and resources (0.5 page)
   - PI and data steward (separate roles)
   - Independent reviewer commitment
   - Requested instrument time and data products
   - Co-authorship terms

5. Timeline
   - Week 1-2: Pre-registration and data agreement
   - Week 3-8: Observing campaign
   - Week 9-16: Blinded analysis
   - Week 17-20: Results review and publication preparation
```

---

## 7. Pathway D — Dedicated Flight Instrument (Years, $1M–$10M)

### What It Is

A dedicated receiver payload flown on a CubeSat or attached to an existing platform (ISS, Cygnus, ESPA ring) that makes in-situ ionospheric measurements while simultaneously receiving GPS-synchronized timing from the ground network.

This is the highest-quality evidence pathway and the only one that can definitively close Stage 6 in the gate ledger. It is also the most expensive and time-consuming.

### CubeSat-Class Instrument Concept

**Form factor:** 3U CubeSat (10 × 10 × 34 cm, ~4 kg)

**Payload:**
- Langmuir probe (electron density, temperature, in situ): ~100 g, 0.5 W
- HF/VHF passive dipole antenna (25 MHz–300 MHz receive): ~200 g, deployable
- GPS receiver (precise orbit determination + UTC timing): ~50 g, 0.5 W
- Software-defined radio payload (50 MHz–300 MHz, 10 MSPS): ~200 g, 2 W
- FPGA for onboard processing: ~150 g, 3 W
- Total payload mass: ~700 g
- Total power: ~6 W

**Orbit:** Sun-synchronous, 450–550 km altitude, 97° inclination — maximum debris density, maximum solar illumination for power, known SWARM orbit altitude for corroboration.

**Operational concept:**
1. GPS receiver maintains precise UTC time and orbit (±10 m position)
2. Langmuir probe continuously monitors in-situ Ne, Te at 100 Hz
3. SDR payload monitors HF/VHF spectrum passively at 10 MSPS
4. When the onboard TLE propagator predicts a close conjunction (<10 km), SDR duty-cycles to full record mode
5. Candidate events flagged onboard; raw IQ data downlinked for ground analysis

### Flight Opportunity Pathways

| Pathway | Cost | Timeline | Flight opportunity |
|---|---|---|---|
| **NASA CubeSat Launch Initiative (CSLI)** | Launch cost waived | 2–4 years | ELaNa missions, ISS deployment |
| **NASA Small Innovative Missions for Planetary Exploration (SIMPLEx)** | Up to $55M | 5–7 years | Dedicated launch |
| **NSF CubeSat program** | Up to $1.5M (instrument only) | 3–5 years | Rideshare |
| **ESA Education CubeSat** | Launch cost waived for university teams | 3–4 years | Vega/Ariane rideshare |
| **Commercial rideshare (SpaceX Transporter)** | ~$5,500/kg to SSO | 12–18 months | Quarterly Transporter missions |
| **ISS NanoRacks** | ~$50,000/U deployment | 12–24 months | ISS to ~400 km |

**Recommended first step:** Submit to NASA CSLI (https://www.nasa.gov/directorates/heo/home/CubeSats_initiative.html). The application is two pages and requires only a concept description and science justification. Applications accepted annually.

### Key Regulatory Requirements for Flight

These must be addressed before any flight proposal is submitted:

1. **FCC or equivalent spectrum license:** Passive receive does not require a transmit license, but active calibration tones do. Consult FCC (US) or ITU (international).
2. **ITAR/EAR export control assessment:** SDR hardware and software may require export licenses. Consult institutional export control office.
3. **NASA debris mitigation standard:** Must demonstrate end-of-life disposal within 25 years per NASA-STD-8719.14. At 500 km, atmospheric drag achieves this within ~3 years naturally.
4. **Launch safety review:** Every launch provider requires a Payload Safety Review. Prepare a Payload Safety Data Package covering containment, orbital debris, RF emissions, and battery handling.
5. **ITU frequency coordination:** Even passive receivers must coordinate with ITU if operating in specific bands (e.g., radio astronomy bands).

---

## 8. Ingesting Real Data Into the Repository

### The Signed-Frame Boundary

All real observed data must enter the repository through the signed-frame ingestion boundary defined in `src/heimdall/instrument_ingestion.py` and `src/heimdall/frame_validation.py`. These contracts are already specified. What is needed for real data is:

1. **A registered source:** Entry in `config/sources/source_registry.json` (see Section 3.3)
2. **A verifier adapter:** An implementation of the `InstrumentVerifier` Protocol in `frame_validation.py` for the specific instrument format (e.g., EISCAT HDF5, SWARM CDF, raw IQ samples)
3. **A decoder adapter:** An implementation of the `InstrumentDecoder` Protocol in `instrument_decoder.py` that converts raw frames to `ObservationL0`

### Implementing the Verifier Adapter (Example: EISCAT HDF5)

```python
# src/heimdall/adapters/eiscat_verifier.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from hashlib import sha256
import h5py
from heimdall.frame_validation import InstrumentVerifier, VerifiedFrame

@dataclass(frozen=True)
class EiscatUhfVerifier:
    """Verifier adapter for EISCAT UHF Madrigal HDF5 data files.
    
    Evidence class ceiling: OBSERVED.
    This verifier checks structural integrity and source identity.
    It does NOT perform scientific calibration — that is the decoder's role.
    """
    source_id: str = "eiscat_uhf_tromso"
    approved_stations: tuple[str, ...] = ("ESR", "UHF", "VHF")

    def verify(self, raw_bytes: bytes, metadata: dict) -> VerifiedFrame:
        # 1. Compute content hash of raw bytes
        payload_digest = "sha256:" + sha256(raw_bytes).hexdigest()
        
        # 2. Parse HDF5 header (structural check only, no scientific interpretation)
        # h5py.File operates on the raw bytes via BytesIO
        import io
        with h5py.File(io.BytesIO(raw_bytes), "r") as f:
            station = f.attrs.get("station", "")
            if station not in self.approved_stations:
                raise IngestionBoundaryError(
                    f"Station {station!r} not in approved list {self.approved_stations}"
                )
            epoch = f.attrs.get("timeStart", None)
            if epoch is None:
                raise IngestionBoundaryError("EISCAT file missing timeStart attribute")
        
        # 3. Verify the source identity matches the registered source
        if metadata.get("source_id") != self.source_id:
            raise IngestionBoundaryError("Source ID mismatch")
        
        return VerifiedFrame(
            payload_digest=payload_digest,
            source_id=self.source_id,
            acquisition_time=epoch,
            schema_id="eiscat_madrigal_hdf5_v1",
            verifier_id="EiscatUhfVerifier",
        )
```

### Provenance Chain for Real Observations

For a real observation to reach `ObservationL0` with `EvidenceClass.OBSERVED`, the full provenance chain must be preserved:

```python
# Required provenance for real observed data (from domain.py)
provenance = Provenance(
    evidence_class=EvidenceClass.OBSERVED,
    scenario_id="eiscat_conjunction_campaign_2026",
    generator_version="heimdall-research-0.2.0",
    configuration_digest="sha256:<hash of config used>",
    model_card_digest="sha256:<hash of model card used>",
    created_at=datetime.now(timezone.utc),
    # These two are REQUIRED for OBSERVED class — domain contract enforces it:
    source_artifact_digest="sha256:<hash of raw EISCAT HDF5 file>",
    source_manifest_digest="sha256:<hash of acquisition manifest JSON>",
)
```

The `Provenance.__post_init__` method in `domain.py` raises `ValueError` if `source_artifact_digest` or `source_manifest_digest` are missing for observed evidence. This is a hard contract — it is impossible to create an `ObservationL0` with `EvidenceClass.OBSERVED` without preserving the raw source bytes.

---

## 9. Pre-Registration Checklist

Complete this checklist before analyzing any real data. Seal it using `run_pre_registered_experiment.py`.

```
PRE-REGISTRATION CHECKLIST
===========================
Date sealed: _______________
Ledger entry ID: _______________

HYPOTHESIS
□ Primary hypothesis stated in one falsifiable sentence
□ Null hypothesis stated explicitly
□ Predicted effect size and direction stated (or "exploratory" declared)
□ Physical mechanism cited (ionospheric plasma wake, not "general anomaly")

DATA
□ Instrument source registered in config/sources/source_registry.json
□ Data agreement or access terms documented
□ Raw data preservation plan documented (where, how long, who has access)
□ Calibration reference documented (instrument manual, calibration campaign)

ANALYSIS
□ Primary metric defined (e.g., "peak δNe/Ne in 30-second conjunction window")
□ Statistical test specified (e.g., "two-sample KS test, α = 0.05")
□ Multiple comparison correction specified (Bonferroni, FDR, or pre-specified count)
□ Minimum sample size for adequate statistical power computed (or exploratory declared)
□ Confounder list completed (ionospheric scintillation, meteors, RFI, calibration drift)
□ Control analysis defined (identical analysis on non-conjunction windows)
□ Exclusion criteria defined (e.g., "exclude windows with RFI power > threshold")

STOPPING RULES
□ Null result criterion: "We conclude no detection if..."
□ Early stopping criterion: "We halt collection if..."
□ Contamination criterion: "We exclude and re-run if..."

GOVERNANCE
□ Independent reviewer identified and committed (name, affiliation, CoI declaration)
□ Data steward appointed (separate from PI)
□ Null result publication commitment documented
□ ITAR/export control assessment completed (or not applicable)
□ Spectrum authorization confirmed (passive receive only, or transmit license held)
```

---

## 10. Independent Review Requirements

Per the [REAL_WORLD_GATE_ACQUISITION_PLAYBOOK.md](REAL_WORLD_GATE_ACQUISITION_PLAYBOOK.md), a stage gate is not closed until an independent reviewer has accepted the evidence package.

### Reviewer Qualifications

For Stage 5 (laboratory/HIL) evidence:
- Expertise in radio instrumentation OR ionospheric physics OR space environment measurements
- No financial stake in a positive result (no equity in any HEIMDALL derivative)
- No co-authorship on the specific paper being reviewed

For Stage 6 (flight) evidence:
- The above, plus expertise specifically in space debris detection OR ionospheric radar
- Ideally affiliated with an institution operating relevant instrumentation (EISCAT, ISR network)

### Review Package Contents

Prepare a package containing:

1. **Pre-registration record** — sealed plan with hash, ledger entry, and timestamp
2. **Raw data provenance** — source agreement, data access logs, raw artifact hashes
3. **Analysis code** — version-controlled, reproducible, with environment specification
4. **Results — ALL results** — positive, negative, excluded, failed windows
5. **Uncertainty budget** — noise characterization, calibration uncertainty, statistical uncertainty
6. **Alternative explanations** — at least three plausible alternative sources for any signal
7. **Limitation statement** — explicit list of what the result does NOT show
8. **Audit bundle** — generated via `write_audit_bundle()` from the existing codebase

### Finding Reviewers

| Community | How to find reviewers |
|---|---|
| EISCAT community | EISCAT Scientific Advisory Committee members |
| ISR community | NSF CEDAR (Coupling, Energetics and Dynamics of Atmospheric Regions) program |
| Space debris community | NASA Orbital Debris Program Office publications, ESA Space Debris Office |
| Radio instrumentation | IEEE Geoscience and Remote Sensing Society |
| Statistics | University statistics departments offering statistical consulting services |

Offer co-authorship on the methodology paper (not the results paper) as compensation for review time.

---

## 11. Regulatory and Legal Checklist

This checklist applies to any real hardware deployment or data collection from a partner instrument.

### Spectrum and RF

```
□ Confirm passive receive operation (receive-only, no transmission)
□ If any calibration tone is transmitted: obtain FCC experimental license
  (US: fcc.gov/licensing-databases/experimental-licensing)
  (Non-US: consult national spectrum authority)
□ If operating in radio astronomy protected bands (e.g., 1400–1427 MHz):
  coordinate with local radio telescope operators
□ Document operating frequency range, power level, and antenna characteristics
```

### Export Control (US Researchers)

```
□ Determine if hardware (SDR, FPGA, GPS) is controlled under EAR (Export Administration Regulations)
□ Determine if software (signal processing algorithms) is controlled under EAR
□ If sharing hardware or software with foreign collaborators: consult institutional
  export control office for license determination
□ SDR hardware is often controlled under ECCN 5A002 — verify with manufacturer
□ For international observatory partnerships: data sharing may require data transfer agreement
```

### Institutional Requirements

```
□ Research involving human subjects (N/A for instrumentation research)
□ Institutional safety review (for any RF-emitting equipment)
□ Animal welfare (N/A)
□ Fieldwork safety review (for deployed outdoor hardware)
□ Cybersecurity review (for internet-connected instruments)
□ IP and publication rights (especially if partnering with government lab or industry)
```

### For Flight Hardware

```
□ ITAR (International Traffic in Arms Regulations) assessment
  — Any spacecraft hardware or technology may be ITAR-controlled
  — Consult ITAR counsel before beginning design
□ NASA CubeSat payload safety review requirements (if using NASA launch)
□ End-of-life disposal compliance (NASA-STD-8719.14: 25-year de-orbit rule)
□ ITU frequency coordination (even for passive receivers in some bands)
□ Launch country export control (separate from ITAR for non-US launches)
```

---

## 12. Failure Modes and How to Handle Them

| Failure Mode | What It Means | Correct Response |
|---|---|---|
| No detectable signal in conjunction windows | Signal is below instrument threshold | Pre-declared null result — publish with full uncertainty characterization |
| Signal detected but not correlated with TLE | Likely RFI or natural ionospheric process | Document as negative result; classify candidate as background; expand confounder analysis |
| Correlation found but below significance threshold | Trend is present but not conclusive | Report exact statistics; do not claim detection; plan larger sample size |
| Calibration failure mid-campaign | Data quality compromised | Halt; document failure; restart after recalibration; do not mix pre/post-failure data |
| Observatory equipment failure | Loss of data | Document; report what was collected; do not impute missing data |
| Data agreement withdrawn by partner | Loss of access | Return or destroy data per agreement; report in audit trail; do not use data obtained before agreement |
| Positive detection later found to be RFI | False detection | Retract; document in ledger; update source registry with known interference source; governance retraction process |
| Independent reviewer rejects the evidence | Review found methodological flaw | Do not publish; fix the flaw; re-run with corrected protocol; the original failed attempt is preserved in the audit trail |

**The most important rule:** Every outcome — including failure, null result, and retraction — must be preserved in the audit trail with the same care as a positive result. The governance framework is designed for honesty, not for confirmation.

---

## 13. Evidence Package Templates

### Template 1: Archive Mining Evidence Package

```json
{
  "evidence_package_id": "HEIM-OBS-2026-001",
  "type": "archive_mining_result",
  "pre_registration_ledger_entry": "sha256:<hash>",
  "pre_registration_timestamp": "2026-08-01T00:00:00Z",
  "instruments": [
    {
      "source_id": "eiscat_uhf_tromso",
      "data_product": "electron_density_1hz",
      "archive_url": "https://portal.eiscat.se/...",
      "data_access_agreement": "EISCAT-DUA-2026-0103",
      "raw_artifact_digest": "sha256:...",
      "acquisition_manifest_digest": "sha256:..."
    }
  ],
  "conjunction_events": {
    "total_computed": 47,
    "meeting_inclusion_criteria": 23,
    "excluded": 24,
    "exclusion_reasons": ["beam_miss_>1km", "data_gap", "rfi_contaminated"]
  },
  "analysis_result": {
    "ks_statistic": 0.18,
    "p_value": 0.31,
    "conclusion": "null_result",
    "effect_size": 0.08,
    "null_criterion_met": true
  },
  "limitation": "No statistically significant correlation between plasma perturbations and TLE object transits was detected at the EISCAT UHF sensitivity level for the 23 analyzed events. This does not exclude weaker signals below the instrument noise floor or signals from sub-cm objects for which no TLE reference exists.",
  "evidence_class": "observed",
  "independent_reviewer": {
    "name": "<Reviewer Name>",
    "affiliation": "<Institution>",
    "coi_declaration": "No financial interest in outcome",
    "review_date": "2026-11-15",
    "decision": "accepted_null_result"
  }
}
```

### Template 2: SDR Array Campaign Evidence Package

```json
{
  "evidence_package_id": "HEIM-LAB-2026-001",
  "type": "sdr_array_campaign",
  "evidence_class_achieved": "laboratory",
  "hardware_configuration": {
    "receiver": "RTL-SDR V4 × 4",
    "gpsdo": "Leo Bodnar mini GPSDO, serial #...",
    "antennas": "LPDA 50-1300 MHz × 4",
    "baseline_m": [10.2, 9.8, 14.1],
    "calibration_certificate_digest": "sha256:..."
  },
  "calibration_results": {
    "phase_coherence_rms_deg": 2.3,
    "timing_accuracy_ns": 15,
    "noise_figure_db": 4.2,
    "minimum_detectable_signal_dbm": -115
  },
  "false_alarm_characterization": {
    "noise_only_windows_analyzed": 1000,
    "false_alarms_at_3sigma": 0,
    "false_alarm_rate_upper_bound_95pct": 0.003
  },
  "limitation": "Laboratory characterization only. No real sky data or debris correlation claimed. Signal generator used to simulate debris transit Doppler profile. Results establish measurement chain sensitivity and false alarm rate under controlled conditions only."
}
```

---

## 14. Resource and Timeline Summary

### Pathway Comparison

| Pathway | Direct Cost | Time to First Observed Result | Evidence Class Achievable | Gate Impact |
|---|---|---|---|---|
| **A: Archive mining** | ~$0 | 4–12 weeks | OBSERVED (if positive) | Stage 5 partial, Gate 1B |
| **B: SDR array** | ~$1,500–$2,000 | 8–24 weeks | LAB → OBSERVED | Stage 5 full |
| **C: Observatory partnership** | $0–$35,000 | 3–9 months | OBSERVED with institutional credibility | Stage 5 full + Stage 6 pathway |
| **D: CubeSat flight** | $1M–$10M | 3–7 years | OBSERVED (in-situ) | Stage 6 |

### Recommended Sequence

**Months 1–2:**
1. Complete governance prerequisites (Section 3)
2. Write pre-registration plan and seal in ledger
3. Begin SWARM archive mining (immediate, no cost, no partnership needed)
4. Submit EISCAT observing proposal
5. Order SDR array hardware

**Months 3–6:**
1. Run archive mining analysis (SWARM, GIRO Digisonde network)
2. Deploy and calibrate SDR array (LABORATORY step)
3. Begin 14-day SDR observing campaign
4. Process and analyze results (positive or negative)

**Months 6–12:**
1. If EISCAT proposal accepted: conduct observing campaign
2. Compile full evidence package for independent review
3. Submit pre-print to arXiv (results section, positive or negative)
4. Identify CubeSat funding pathway (CSLI application or NSF proposal)

**Year 2+:**
1. If archives/ground campaign negative: use results to refine sensitivity requirements for hardware
2. Pursue CubeSat flight opportunity with validated instrument design
3. If archives/ground campaign positive: pursue Stage 6 flight validation with strong preliminary evidence in hand

---

## Summary

The path from synthetic to observed evidence does not require a large budget or a flight mission to begin. The SWARM archive mining pathway requires only a Python environment and internet access. The SDR array pathway requires $1,500 and a few weeks. Both can produce `EvidenceClass.OBSERVED` results within weeks to months, and both directly exercise the governance infrastructure already built into this repository.

The single most important action is completing the governance prerequisites in Section 3 before touching any real data. The pre-registration requirement is not bureaucratic overhead — it is the difference between science and storytelling.

---

*Project HEIMDALL ELECTRA — Aarti S Ravikumar · [@aartisr](https://github.com/aartisr) · 2026-08-03*
