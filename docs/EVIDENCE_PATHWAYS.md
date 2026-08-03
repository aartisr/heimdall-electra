# HEIMDALL ELECTRA — Real Observed Evidence: Pathways & Quick-Start Guide

**Author:** Aarti S Ravikumar ([@aartisr](https://github.com/aartisr))
**Date:** 2026-08-03
**Purpose:** Practical guide to acquiring the first real observed evidence — ordered by cost and speed
**Full governance detail:** [OBSERVED_EVIDENCE_ACQUISITION.md](OBSERVED_EVIDENCE_ACQUISITION.md)

---

## The Evidence Promotion Ladder

Every result in the repository today is `EvidenceClass.SYNTHETIC`. To make a bounded scientific claim, evidence must climb this ladder. Each rung requires **new, independent physical evidence** — not better software, not a stronger argument.

```
┌─────────────────────────────────────────────────────────────────────┐
│  SYNTHETIC                                                          │
│  Deterministic fixtures, model outputs, versioned scenarios         │
│  Permitted: software verification, sensitivity analysis             │
│  Prohibited: physical claim, hardware performance assertion         │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ New evidence:
                            │ Controlled measurement with traceable calibration
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LABORATORY                                                         │
│  Calibrated controlled measurement, preserved raw data              │
│  Permitted: measurement chain characterization, controlled tests    │
│  Prohibited: flight performance claim, uncontrolled observation     │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ New evidence:
                            │ Authorized real instrument, raw bytes,
                            │ manifest, timing, provenance, independent QA
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│  OBSERVED                                                           │
│  Authorized real-world instrument with full lineage                 │
│  Permitted: carefully bounded scientific analysis                   │
│  Prohibited: object identity claim, operational action              │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ New evidence:
                            │ Blinded protocol, independent reference,
                            │ alternative explanations examined, peer review
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│  INDEPENDENTLY REVIEWED                                             │
│  Peer-reviewed, documented dissent, alternatives examined           │
│  Permitted: bounded scientific claim with stated limitations        │
│  Prohibited: operational traffic product, maneuver authority        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Before Touching Any Real Data — Three Non-Negotiable Steps

**1. Pre-register the analysis plan** using the existing governance infrastructure:
```bash
mkdir -p data/local/runs
PYTHONPATH=src python3.11 scripts/run_pre_registered_experiment.py \
  --ledger      data/local/runs/observed-campaign-ledger.jsonl \
  --audit-bundle data/local/runs/observed-campaign-plan.json \
  --generated-at <ISO-8601 timestamp BEFORE you open any data file> \
  --artifact    config/research/claims.json
```
The plan must declare: primary hypothesis, null result criterion, statistical test, confounders list, stopping rules. Seal it before analysis. This is not optional.

**2. Register the instrument source** in `config/sources/source_registry.json` before ingesting any data from it.

**3. Appoint an independent reviewer** — someone with no stake in a positive result — before beginning.

---

## Pathway A — Archive Mining ★ ZERO BUDGET, START TODAY ★

**Evidence class achievable:** `OBSERVED`
**Cost:** $0
**Time to first result:** 4–12 weeks
**What you need:** Python, internet connection, nothing else

### Why this works

Three world-class ionospheric instruments have already been measuring the plasma at LEO altitudes for years. Known debris objects' orbital positions are independently verified by USSPACECOM. The only new work is computing *when* a known object was overhead a given instrument, then checking whether the instrument saw anything unusual at that exact time.

### Source 1 — ESA SWARM Satellites (Best first target)

Three satellites at 460–510 km measuring electron density in situ at 16 Hz. Free, no registration, no agreement needed for basic products.

```bash
pip install viresclient
```

```python
from viresclient import SwarmClient
import datetime

client = SwarmClient()

# Download one hour of Swarm Alpha electron density data
request = client.get_between(
    collection="SW_OPER_EFIA_LP_1B",        # Swarm Alpha Langmuir probe
    start_time=datetime.datetime(2026, 6, 15, 12, 0, 0),
    end_time=datetime.datetime(2026, 6, 15, 13, 0, 0),
    measurements=["Ne", "Te", "Latitude", "Longitude", "Radius"],
)
df = request.as_dataframe()
df.to_csv("data/external/swarm/swarm_alpha_20260615.csv")
```

**What to look for:** A transient dip or spike in `Ne` (electron density) lasting 0.1–2 seconds — consistent with a debris fragment transiting at 7.5 km/s relative velocity. Correlate timing against TLE conjunction predictions.

**Portal:** https://vires.services/ — free account, immediate access

### Source 2 — EISCAT Madrigal Archive

The world's most sensitive ionospheric radar network (Norway/Sweden/Finland). Raw plasma parameter data free for research use.

```bash
pip install madrigalWeb
```

```python
import madrigalWeb.madrigalWeb as madrigal

mad = madrigal.MadrigalData("https://portal.eiscat.se/madrigal")

# List all EISCAT UHF (instrument code 30) experiments in 2025
exps = mad.getExperiments(
    30,                    # EISCAT UHF Tromsø
    2025, 1, 1, 0, 0, 0,  # start: 2025-01-01
    2025, 12, 31, 23, 59, 59  # end: 2025-12-31
)
for exp in exps[:5]:
    print(f"{exp.starttime}  {exp.name}")
```

**Portal:** https://portal.eiscat.se/madrigal

### Source 3 — GIRO Digisonde Network

60+ global ionosondes. Long continuous archives. Free.

```python
import madrigalWeb.madrigalWeb as madrigal

# Connect to the global Cedar Madrigal server
mad = madrigal.MadrigalData("http://cedar.openmadrigal.org/")

# List all ionosondes worldwide
instruments = mad.getAllInstruments()
digisondes = [i for i in instruments if "digisonde" in i.name.lower()]
for d in digisondes[:10]:
    print(f"{d.code}: {d.name}  lat={d.latitude:.1f}  lon={d.longitude:.1f}")
```

**Portal:** https://giro.uml.edu/

### Computing TLE Conjunctions

```bash
pip install sgp4 skyfield
```

```python
from sgp4.api import Satrec, jday
from skyfield.api import load, EarthSatellite, wgs84
import urllib.request, datetime

# Download current debris TLE catalog
url = "https://celestrak.org/pub/TLE/debris.txt"
urllib.request.urlretrieve(url, "data/external/tle_debris.txt")

# Load TLEs
ts = load.timescale()
with open("data/external/tle_debris.txt") as f:
    lines = f.read().splitlines()

# Group into 3-line sets (name + TLE line 1 + TLE line 2)
objects = []
for i in range(0, len(lines) - 2, 3):
    name, l1, l2 = lines[i], lines[i+1], lines[i+2]
    try:
        objects.append(EarthSatellite(l1, l2, name, ts))
    except Exception:
        pass

# Find objects that pass over EISCAT Tromsø (69.6°N, 19.2°E, 86 m alt)
EISCAT_LAT, EISCAT_LON = 69.6, 19.2
t_start = ts.utc(2026, 6, 15, 0, 0, 0)
t_end   = ts.utc(2026, 6, 16, 0, 0, 0)

conjunctions = []
for sat in objects[:500]:   # process first 500 for demo; run all for production
    t, events = sat.find_events(
        wgs84.latlon(EISCAT_LAT, EISCAT_LON),
        t_start, t_end,
        altitude_degrees=70.0,   # EISCAT beam points near zenith
    )
    if len(events) > 0:
        for ti, event in zip(t, events):
            if event == 1:   # culmination (highest elevation)
                conjunctions.append({
                    "name": sat.name,
                    "time_utc": ti.utc_iso(),
                    "catalog_number": sat.model.satnum,
                })

print(f"Found {len(conjunctions)} predicted transits in 24 hours")
for c in conjunctions[:5]:
    print(f"  {c['time_utc']}  {c['name']}")
```

### Analysis Protocol (Pre-register before running)

```python
# Analysis parameters — seal in ledger BEFORE loading any instrument data
analysis_config = {
    "primary_hypothesis": (
        "A statistically significant plasma perturbation correlated with "
        "the transit of a known TLE object is detectable above the noise floor"
    ),
    "null_result_criterion": (
        "KS statistic < 0.15 or p-value > 0.10 after N >= 20 conjunction events"
    ),
    "analysis_window_seconds": 30,
    "baseline_window_seconds": 300,  # 5-min pre-conjunction baseline
    "statistical_test": "two_sample_ks",
    "significance_threshold": 0.05,
    "multiple_comparison_correction": "bonferroni",
    "confounders": [
        "ionospheric_scintillation",
        "meteor_ablation",
        "radio_frequency_interference",
        "calibration_drift",
        "solar_energetic_particle_events",
    ],
}

# Seal this in the pre-registered ledger. Then and only then, load the data.
```

**For each conjunction event:**
1. Extract 30-second window of plasma data centered on predicted transit time
2. Subtract 5-minute pre-conjunction baseline
3. Compute peak `δNe/Ne` (normalized density perturbation)
4. Repeat for 100 random non-conjunction control windows from the same day
5. Apply KS test: conjunction distribution vs. control distribution
6. Report p-value, KS statistic, and full result — positive OR negative

---

## Pathway B — Low-Cost SDR Array (~$1,500)

**Evidence class:** LABORATORY first → OBSERVED after field campaign
**Cost:** ~$1,500–$2,000 in commodity hardware
**Time:** 8–24 weeks from purchase to first observed result

### Hardware (Full Bill of Materials)

| Item | Part | Qty | Cost |
|------|------|-----|------|
| SDR receivers | RTL-SDR V4 (0.5–1.75 GHz) | 4 | $160 |
| GPS-disciplined oscillator | Leo Bodnar mini GPSDO | 1 | $160 |
| GPSDO distribution amp | Mini-Circuits ZFSC-4-1+ | 1 | $30 |
| Low-noise amplifiers | Nooelec LaNA (0.6 dB NF) | 4 | $180 |
| Directional antennas | LPDA 50–1300 MHz | 4 | $320 |
| Coaxial cables (3 m SMA) | LMR-195 | 8 | $96 |
| Acquisition computers | Raspberry Pi 4 (4 GB) | 4 | $220 |
| Storage | 128 GB microSD | 4 | $60 |
| Network switch | Gigabit, unmanaged | 1 | $25 |
| Signal generator (calibration) | Rigol DSG815 | 1 | $350 |
| Weatherproof enclosures | IP67 | 4 | $80 |
| **Total** | | | **~$1,681** |

The signal generator is used once for the LABORATORY calibration step, then set aside. All other hardware runs the ongoing observing campaign.

### Key design principle — Phase coherence

All four RTL-SDR V4 units accept an external 10 MHz reference input. The Leo Bodnar GPSDO outputs a GPS-disciplined 10 MHz tone (< 1 ppb stability). Distributing this to all four receivers gives a common phase reference locked to GPS time — enabling nanosecond-class TDOA measurements across the array.

### Software

```bash
pip install pyrtlsdr    # RTL-SDR Python bindings
pip install gpsd-py3    # GPS timing
pip install numpy scipy # signal processing (adapter layer only)
pip install h5py        # HDF5 data format (matches EISCAT standard)
# GNU Radio via system package manager:
sudo apt install gnuradio   # Raspberry Pi OS / Ubuntu
```

### Step 1: LABORATORY evidence (calibration)

Connect the signal generator → 60 dB attenuator → antenna port of receiver #1. Inject a 150 MHz CW tone swept through a Doppler profile simulating an overhead LEO pass (0–500 Hz/s). Verify the pipeline recovers the correct profile. Characterize false alarm rate on noise-only windows. This produces `EvidenceClass.LABORATORY`.

### Step 2: OBSERVED evidence (field campaign)

Deploy outdoors (low-RFI site, clear sky view). Run continuously for 14 days. Use the TLE conjunction script to target specific events. Extract 60-second IQ windows around each predicted transit. Run the pre-registered detection pipeline on every window including all non-detections.

---

## Pathway C — Observatory Partnership (Low Direct Cost)

**Evidence class:** OBSERVED with institutional credibility
**Cost:** $0–$35,000 (instrument time)
**Time:** 3–9 months

Contact an established ionospheric observatory and propose a joint campaign. They provide hardware, spectrum licenses, calibration, and institutional credibility. HEIMDALL provides the analysis protocol and co-authorship.

### Primary Targets

| Institution | Instrument | Why | Contact |
|---|---|---|---|
| **EISCAT** (Norway/Sweden) | Incoherent scatter radar, 930 MHz | World's most sensitive ionospheric radar | director@eiscat.se |
| **Millstone Hill** (MIT) | ISR, 440 MHz, US-based | MIT/Space Force adjacency, SSA experience | haystack.mit.edu |
| **SuperDARN** (global) | HF radar network, 35 stations | Multi-static geometry, huge archive | superdarn.ca |
| **Jicamarca** (Peru) | ISR, 50 MHz, magnetic equator | Unique geometry for equatorial plasma | jro.igp.gob.pe |

### Proposal (send a 2-page letter of intent first)

State in one falsifiable sentence: what you will measure, with what instrument, for what duration, and what constitutes a null result. Offer co-authorship on any publication. Commit explicitly to publishing negative results.

Example opening sentence:
> "We propose a pre-registered 7-day observing campaign to test whether a statistically significant transient electron density perturbation — consistent with a plasma wake — can be detected in EISCAT UHF data within ±15 seconds of predicted transits of catalogued debris objects larger than 50 cm diameter at 300–600 km altitude."

---

## Pathway D — Dedicated Flight Instrument ($1M–$10M, Years)

**Evidence class:** OBSERVED in situ (highest quality, closes Stage 6 gate)
**Cost:** $1M–$10M depending on scope
**Time:** 3–7 years

### 3U CubeSat Concept

- **Langmuir probe** — in-situ electron density, 100 Hz sampling
- **VHF passive SDR** — 50–300 MHz receive, 10 MSPS, duty-cycled on conjunctions
- **GPS-PNT receiver** — precise orbit + UTC timing (< 10 m position, < 100 ns timing)
- **Onboard TLE propagator** — autonomous conjunction prediction, SDR triggering

### Launch Pathways

| Pathway | Cost | Timeline | Link |
|---|---|---|---|
| NASA CubeSat Launch Initiative (CSLI) | Launch cost waived | 2–4 years | nasa.gov/directorates/heo/home/CubeSats_initiative.html |
| SpaceX Transporter rideshare | ~$5,500/kg to SSO | 12–18 months | spacex.com/rideshare |
| NSF CubeSat program | Up to $1.5M instrument | 3–5 years | nsf.gov |
| ESA Education CubeSat | Launch waived (university) | 3–4 years | esa.int/Education |
| ISS NanoRacks deployment | ~$50K/U | 12–24 months | nanoracks.com |

**First action for this pathway:** Submit a 2-page concept to NASA CSLI (applications accepted annually). This costs nothing and opens the launch queue.

---

## Pathway Comparison at a Glance

| | A: Archive Mining | B: SDR Array | C: Observatory | D: CubeSat |
|---|---|---|---|---|
| **Cost** | **$0** | ~$1,500 | $0–$35K | $1M–$10M |
| **Time to result** | **4–12 weeks** | 8–24 weeks | 3–9 months | 3–7 years |
| **Evidence class** | OBSERVED | LAB → OBS | OBSERVED | OBSERVED in-situ |
| **New hardware** | None | Yes | None | Yes (full spacecraft) |
| **Partnership needed** | No | No | Yes | Varies |
| **Gate impact** | 1B, 5 partial | 5 full | 5 full + 6 path | 6 full |
| **Start today?** | **Yes** | After purchase | After proposal | After funding |

---

## Ingesting Real Data Into the Repository

When you have real data, the existing codebase is ready to receive it. The `domain.py` contract enforces the evidence chain in code — you cannot create an `ObservationL0` with `EvidenceClass.OBSERVED` without both a `source_artifact_digest` and `source_manifest_digest`. There is no workaround.

```bash
# Ingest a raw data file as observed evidence
PYTHONPATH=src python3.11 scripts/ingest_artifact.py \
  --artifact  data/external/swarm/swarm_alpha_20260615.csv \
  --evidence-class observed \
  --store-root data/local/evidence

# Ingest the analysis result (positive or negative)
PYTHONPATH=src python3.11 scripts/ingest_artifact.py \
  --artifact  data/local/analysis/conjunction_result_20260615.json \
  --evidence-class observed \
  --store-root data/local/evidence
```

The pipeline from "real data" to "governed evidence record" is already built. What is needed is the adapter layer for each instrument format (`frame_validation.py` verifier + `instrument_decoder.py` decoder). Templates and examples are in [OBSERVED_EVIDENCE_ACQUISITION.md](OBSERVED_EVIDENCE_ACQUISITION.md).

---

## One-Page Action Plan — Starting Today

```
Week 1
  □ Seal pre-registration plan (run_pre_registered_experiment.py)
  □ pip install viresclient sgp4 skyfield madrigalWeb
  □ Download 30 days of SWARM Alpha electron density data
  □ Download TLE debris catalog from CelesTrak

Week 2
  □ Run TLE conjunction computation for SWARM orbit vs. debris catalog
  □ Extract conjunction windows from SWARM Ne data
  □ Run statistical analysis (KS test, per pre-registered protocol)
  □ Record result — positive, negative, or inconclusive — in audit trail

Week 3
  □ Order SDR array hardware ($1,500)
  □ Repeat archive analysis for EISCAT Madrigal archive
  □ Draft EISCAT observing proposal (letter of intent, 1 page)

Week 4–8
  □ Deploy and calibrate SDR array (LABORATORY step)
  □ Begin 14-day observing campaign (OBSERVED step)
  □ Submit EISCAT proposal

Ongoing
  □ Compile full evidence package (positive or negative)
  □ Engage independent reviewer
  □ Submit arXiv preprint — results section must be honest about null results
```

---

## The Most Important Rule

**A null result is a valid, valuable, publishable scientific result.**

If the archive mining shows no detectable correlation, that is not a failure — it is a measurement. It tells you the plasma wake amplitude is below the SWARM/EISCAT noise floor for the observed object size range. That constrains the physics. It narrows the parameter space. It is scientifically honest. It must be preserved in the audit trail and published.

The governance framework is built for honesty, not confirmation.

---

*Project HEIMDALL ELECTRA — Aarti S Ravikumar · [@aartisr](https://github.com/aartisr) · 2026-08-03*
*Full governance detail: [OBSERVED_EVIDENCE_ACQUISITION.md](OBSERVED_EVIDENCE_ACQUISITION.md)*
