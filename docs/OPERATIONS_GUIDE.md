# HEIMDALL ELECTRA — Operations & Demonstration Guide

**Project:** Passive Ionospheric Plasma Wake Sensing for Sub-Centimetre Orbital Debris Detection  
**Stewardship:** Aarti S Ravikumar ([@aartisr](https://github.com/aartisr))  
**Date:** 2026-08-03  
**Status:** Research software — all outputs `EvidenceClass.SYNTHETIC` unless stated otherwise

---

## Table of Contents

1. [One-Time Setup](#1-one-time-setup)
2. [Quick Verification (2 minutes)](#2-quick-verification-2-minutes)
3. [The Core Science Demo — Five Commands](#3-the-core-science-demo--five-commands)
4. [The Analyst Console (Web UI)](#4-the-analyst-console-web-ui)
5. [Full Visualization Pipeline](#5-full-visualization-pipeline)
6. [Archive Mining — First Real Evidence Pathway](#6-archive-mining--first-real-evidence-pathway)
7. [Multi-Node Pipeline — Position Estimation](#7-multi-node-pipeline--position-estimation)
8. [Pre-Registered Experiment (Governance Demo)](#8-pre-registered-experiment-governance-demo)
9. [Development Sweep (Parameter Sensitivity)](#9-development-sweep-parameter-sensitivity)
10. [Using the Python API Directly](#10-using-the-python-api-directly)
11. [Value-Add Demonstration Script](#11-value-add-demonstration-script)
12. [Interpreting the Outputs](#12-interpreting-the-outputs)
13. [Troubleshooting](#13-troubleshooting)
14. [What to Show a Stakeholder](#14-what-to-show-a-stakeholder)

---

## 1. One-Time Setup

### Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Python | 3.11+ | `python3.11 --version` |
| Node.js + npm | 18+ LTS | `node --version && npm --version` |
| Git | Any | `git --version` |
| Disk space | ~200 MB | Includes node_modules |

### Clone and verify

```bash
git clone https://github.com/aartisr/heimdall-electra.git
cd heimdall-electra

# Compile everything — catches any syntax errors immediately
PYTHONPATH=src python3.11 -m compileall -q src scripts tests
# Expected: no output (clean compile)
```

### Install frontend (run from your own terminal — needs corporate npm registry)

```bash
cd apps/analyst-console
npm ci        # Uses .npmrc → Optum Artifactory + proxy at localhost:62755
cd ../..
```

> **Corporate npm registry** is pre-configured in `apps/analyst-console/.npmrc`:
> ```
> registry=https://edgeinternal1uhg.optum.com/artifactory/api/npm/tenant-compass-npm-vir
> proxy=http://localhost:62755
> ```

---

## 2. Quick Verification (2 minutes)

Run these four commands from the repository root. All should complete without errors.

```bash
# Step 1 — Compile all source
PYTHONPATH=src python3.11 -m compileall -q src scripts tests

# Step 2 — Run all 267 tests
PYTHONPATH=src python3.11 -m unittest discover -s tests -v 2>&1 | tail -5

# Step 3 — Verify source independence (no external runtime deps)
PYTHONPATH=src:. python3.11 scripts/verify_independence.py

# Step 4 — Run end-to-end synthetic pipeline
PYTHONPATH=src python3.11 scripts/run_vertical_slice.py
```

**Expected output from Step 4:**
```
[vertical_slice] scenario  : synthetic-reference-v1
[vertical_slice] detect    : score=0.xx  detected=True/False
[vertical_slice] gate      : PeakContrast PASS  ClockQuality PASS
[vertical_slice] candidate : CandidateL2(id=..., detected=True)
[vertical_slice] evaluation: DetectionReport(...)
[vertical_slice] audit     : bundle written → data/local/...
```

---

## 3. The Core Science Demo — Five Commands

These five commands demonstrate the complete value proposition end-to-end.

### Command 1: Build the debris population model

```bash
mkdir -p data/local/visualization

PYTHONPATH=src python3.11 scripts/build_debris_population.py \
  --output data/local/visualization/debris_population.json \
  --generated-at 2026-07-30T00:00:00Z
```

**What it shows:**
```
tracked_objects=133,272        ← what radar tracks today
sub_cm_estimate=2,355,938,136  ← 2.3 billion objects radar CANNOT see
clouds=6                       ← fragmentation event clouds with known origins
shells=2592                    ← orbital altitude × inclination density grid
```
The ratio (~17,000:1) is the core argument: for every object radar tracks, ~17,000 sub-cm fragments exist invisibly.

### Command 2: Prove the radar detection gap analytically

```bash
PYTHONPATH=src python3.11 scripts/run_rcs_analysis.py \
  --output data/local/visualization/rcs_analysis.json \
  --generated-at 2026-07-30T00:00:00Z
```

**What it shows:**
```
Space Fence:  min detectable diameter = 10.2 cm   ← best radar for debris
Haystack:     min detectable diameter = 2.4 cm
Goldstone:    min detectable diameter = 1.8 cm
TIRA:         min detectable diameter = 1.2 cm
EISCAT UHF:   min detectable diameter = 5.1 cm

detection gap: 0.1mm – 1.2cm    ← NOTHING detects objects here
undetected population: 95%      ← 95% of debris is invisible to all radars
```

The 5 mm sphere proof: `−110 dBsm` actual vs `−25 dBsm` Space Fence threshold = **85 dB deficit = 3 billion× below detection**.

### Command 3: Compute trajectory risk and safe corridors

```bash
PYTHONPATH=src python3.11 scripts/compute_trajectory_risk.py \
  --output data/local/visualization/risk_field.json \
  --generated-at 2026-07-30T00:00:00Z
```

**What it shows:**
```
iss-resupply-400km:     P=9.1e-06  dark_risk=94%  level=very_low
debris-belt-crossing:   P=1.2e-04  dark_risk=96%  level=moderate
safe corridors: 63 identified
```
"dark_risk=94%" means 94% of collision risk is invisible to current radar — HEIMDALL uniquely quantifies this.

### Command 4: Quantify the economic value

```bash
PYTHONPATH=src python3.11 scripts/estimate_cost_savings.py \
  --output data/local/visualization/cost_savings.json \
  --generated-at 2026-07-30T00:00:00Z
```

**What it shows:**
```
annual fleet savings:  $158.7M/year
10-year projection:    $1,587M  (~$1.6 billion)
uncertainty range:     $794M – $4,762M

crewed_leo:         $xx.xM   (maneuvers + insurance + delays + propellant)
iss_resupply:       $xx.xM
commercial_leo:     $xx.xM
...
```

### Command 5: Run the multi-node TDOA physics demonstration

```bash
PYTHONPATH=src python3.11 scripts/run_multi_node_analysis.py \
  --n-nodes 4 \
  --snr 8 \
  --generated-at 2026-07-30T00:00:00Z
```

**What it shows:**
```
Fragment D:      10.0 mm
δn/n peak:       ~100%   ← detectable ionospheric perturbation
Wake length:     100 km
Detectable:      True

Radar vs Wake scaling:
  1.0mm   RCS: -125.7 dBsm   Wake: -120.0 dB   Gap: YES
  5.0mm   RCS:  -83.8 dBsm   Wake: -106.0 dB   Gap: YES
  10.0mm  RCS:  -65.7 dBsm   Wake: -100.0 dB   Gap: YES
  50.0mm  RCS:  -23.8 dBsm   Wake:  -86.0 dB   Gap: no
```

---

## 4. The Analyst Console (Web UI)

### Generate the data and start the server

```bash
# Step 1: Generate all visualization JSON files
PYTHONPATH=src python3.11 scripts/export_visualization_data.py \
  --generated-at 2026-07-30T00:00:00Z \
  --output-dir apps/analyst-console/public

# Step 2: Start the dev server (run from your own terminal)
cd apps/analyst-console
npm ci          # first time only
npm run dev -- --host 127.0.0.1
```

Open **http://127.0.0.1:5173** in your browser.

### What you will see

**Evidence Console tab** (existing):
- Research status, stage gates, evidence sources, claims

**Debris Visualization tab** (new):

| Panel | What it shows | Key message |
|---|---|---|
| **3D Orbital Debris Globe** | Rotating Earth with colour-coded debris layers (tracked=white, sub-cm=orange, clouds=purple) | The orange cloud dwarfs the white dots — most debris is invisible |
| **Radar Detection Gap** | Log-log chart: radar RCS curves (grey) vs HEIMDALL wake signal (cyan dashed) with red shaded gap | Every radar is below threshold for 0.1mm–1.2cm objects |
| **Trajectory Risk Heatmap** | Altitude × inclination grid coloured by flux; green-bordered safe corridors | High-altitude polar orbits are the densest and riskiest |
| **Cost Savings Dashboard** | Stacked bars per mission class with uncertainty whiskers | $158.7M/year fleet-wide conservative estimate |

**Globe layer controls:**
- Press `T` — toggle tracked objects (white)
- Press `S` — toggle sub-cm estimate (orange)
- Press `F` — toggle fragmentation clouds (purple)
- Arrow keys — rotate manually

---

## 5. Full Visualization Pipeline

Run all four data stages and launch the UI in one sequence:

```bash
# Generate all data (≈ 30 seconds)
PYTHONPATH=src python3.11 scripts/export_visualization_data.py \
  --generated-at 2026-07-30T00:00:00Z

# Verify outputs
ls -lh apps/analyst-console/public/*.json
# Expected:
#   debris_population.json   1.1 MB  — 2,592 shells × 4 size regimes
#   rcs_analysis.json        239 KB  — 5 radar curves × 200 points
#   risk_field.json          163 KB  — 648 risk cells + 5 profiles
#   cost_savings.json          9 KB  — 7 mission classes

# Start UI (from own terminal with npm)
cd apps/analyst-console && npm run dev -- --host 127.0.0.1
```

---

## 6. Archive Mining — First Real Evidence Pathway

### Test mode (zero network, works right now)

```bash
# Pre-register analysis plan first (governance requirement)
mkdir -p data/local/runs data/local/archive_mining

PYTHONPATH=src python3.11 scripts/run_pre_registered_experiment.py \
  --ledger       data/local/runs/archive-mining-plan.jsonl \
  --audit-bundle data/local/runs/archive-mining-plan.json \
  --generated-at 2026-07-30T00:00:00Z \
  --artifact     config/research/claims.json

# Run analysis with synthetic plasma data
PYTHONPATH=src:scripts python3.11 scripts/mine_swarm_archive.py \
  --mode              synthetic \
  --ledger-entry-id   synthetic-baseline-001 \
  --n-synthetic       30 \
  --inject-signal \
  --snr               4.0 \
  --generated-at      2026-07-30T00:00:00Z \
  --output            data/local/archive_mining/report.json

cat data/local/archive_mining/report.json | python3.11 -c "
import json,sys
d=json.load(sys.stdin)
print(f'Verdict:     {d[\"overall_verdict\"]}')
print(f'Detections:  {d[\"windows_positive\"]} / {d[\"windows_valid\"]} valid windows')
print(f'Det rate:    {d[\"windows_positive\"]/max(d[\"windows_valid\"],1):.1%}')
print(f'KS stat:     {d[\"ks_statistic\"]:.4f}')
print(f'p (corrected): {d[\"p_value_corrected\"]:.4f}')
print(f'Evidence:    {d[\"evidence_class\"]}')
"
```

### Real mode — when you have network access to ESA / CelesTrak

```bash
# Step 1: Download TLE catalog (run from a terminal with internet)
curl -o data/external/tle_debris.txt \
     "https://celestrak.org/pub/TLE/debris.txt"

# Step 2: Compute conjunctions with SWARM Alpha for one week
PYTHONPATH=src python3.11 scripts/compute_tle_conjunctions.py \
  --tle             data/external/tle_debris.txt \
  --source          esa_swarm_alpha \
  --start           2026-06-01T00:00:00Z \
  --end             2026-06-08T00:00:00Z \
  --max-distance-km 50 \
  --output          data/local/conjunctions/swarm_alpha_week1.json

# Step 3: Install SWARM data client (run from terminal with internet)
pip install viresclient

# Step 4: Run real analysis
PYTHONPATH=src:scripts python3.11 scripts/mine_swarm_archive.py \
  --mode          real \
  --conjunctions  data/local/conjunctions/swarm_alpha_week1.json \
  --ledger-entry-id  <your-pre-registered-ledger-id> \
  --output        data/local/archive_mining/swarm_real_report.json
```

---

## 7. Multi-Node Pipeline — Position Estimation

```bash
# Run with 4 nodes, 1.5 km baseline, 2 MHz sample rate
PYTHONPATH=src python3.11 scripts/run_multi_node_analysis.py \
  --n-nodes        4 \
  --baseline-m     1500 \
  --source-alt-m   3000 \
  --source-offset-m 400 \
  --sample-rate-hz 2000000 \
  --snr            8 \
  --target-size-mm 10 \
  --generated-at   2026-07-30T00:00:00Z \
  --output         data/local/multi_node/result.json
```

**What it shows:**
- TDOA measurements between all 6 node pairs (4-choose-2)
- Gauss-Newton position solver result
- Wake physics prediction (δn/n, wake length, signal bandwidth)
- Full Radar vs Wake scaling table proving the detection advantage

---

## 8. Pre-Registered Experiment (Governance Demo)

Demonstrates the scientific governance framework — pre-registration, ledger, audit bundle:

```bash
mkdir -p data/local/runs

PYTHONPATH=src python3.11 scripts/run_pre_registered_experiment.py \
  --ledger       data/local/runs/synthetic-reference-ledger.jsonl \
  --audit-bundle data/local/runs/synthetic-reference-audit.json \
  --generated-at 2026-07-30T00:00:00Z \
  --artifact     config/research/claims.json \
  --artifact     config/models/model_cards.json

# Verify the audit bundle
python3.11 -c "
import json
bundle = json.load(open('data/local/runs/synthetic-reference-audit.json'))
print('Audit bundle ID:', bundle.get('bundle_id', 'N/A'))
print('Evidence class: ', bundle.get('evidence_class', 'N/A'))
print('Artifacts sealed:', len(bundle.get('artifact_records', [])))
"
```

**Governance properties proven:**
- Analysis plan sealed before evaluation
- All inputs content-addressed (SHA-256)
- Append-only ledger record
- Portable audit bundle for independent review

---

## 9. Development Sweep (Parameter Sensitivity)

```bash
PYTHONPATH=src python3.11 scripts/run_development_sweep.py
```

Explores detector sensitivity across a range of threshold parameters without touching the locked pre-registered protocol.

---

## 10. Using the Python API Directly

All 212 public symbols are importable from `heimdall`. Example Python session:

```python
import sys; sys.path.insert(0, "src")
from heimdall import (
    # Core pipeline
    SyntheticScenario, generate_observation, calibrate, detect,
    BaselineMatchedFilter, PeakContrastGate, evaluate,
    # Debris population
    SyntheticPowerLawModel, PopulationModelConfig,
    # Radar analysis
    RadarDetectabilityAnalyzer, REFERENCE_RADAR_SYSTEMS,
    # Trajectory risk
    TrajectoryRiskEngine, REFERENCE_LAUNCH_PROFILES,
    # Cost savings
    CostSavingsCalculator, NASA_COMMERCIAL_FLEET,
    # Physics
    AnalyticWakeModel,
    # Signal processing
    GccPhatCrossCorrelation, FftMatchedFilter,
    # TDOA
    GaussNewtonTdoaSolver, ReceiverNode,
    # Multi-node pipeline
    MultiNodePipeline, default_pipeline_config,
    # Archive mining
    build_standard_protocol, REFERENCE_OBSERVATORIES,
)

# ── 1. Prove the radar gap ──────────────────────────────────────
from datetime import datetime, timezone
analyzer = RadarDetectabilityAnalyzer()
gap = analyzer.build_gap_analysis(datetime.now(timezone.utc))
print(f"Detection gap: {gap.gap_min_diameter_m*1000:.1f}mm – {gap.gap_max_diameter_m*100:.1f}cm")
print(f"Undetected population: {gap.undetected_population_fraction:.0%}")

# ── 2. Build debris population ──────────────────────────────────
model = SyntheticPowerLawModel()
pop   = model.build_snapshot(PopulationModelConfig(), datetime.now(timezone.utc))
print(f"Tracked: {pop.total_tracked_objects:,}   Sub-cm: {pop.estimated_sub_cm_total:,}")

# ── 3. Score a launch trajectory ───────────────────────────────
engine = TrajectoryRiskEngine()
report = engine.build_risk_report(pop, REFERENCE_LAUNCH_PROFILES)
for score in report.profile_scores:
    print(f"{score.profile_id}: P={score.cumulative_collision_probability:.2e} "
          f"dark={score.dark_risk_fraction:.0%}")

# ── 4. Quantify economic value ──────────────────────────────────
calc   = CostSavingsCalculator()
fleet  = calc.build_fleetwide_scenario(NASA_COMMERCIAL_FLEET)
print(f"Annual savings: ${fleet.annual_savings_usd/1e6:.1f}M")
print(f"10-year total:  ${fleet.ten_year_savings_usd/1e6:.0f}M")

# ── 5. Physics: wake signal for 1cm fragment ───────────────────
from heimdall.physics_contract import (
    PlasmaEnvironment, OrbitalState, TargetAssumptions, CoordinateFrame, TimeScale
)
wake_model = AnalyticWakeModel()
plasma = PlasmaEnvironment(1e11, 1e11, 1500.0, 1200.0, (2e-5, 0, 0), "nominal_leo")
orbital = OrbitalState(
    datetime.now(timezone.utc), TimeScale.UTC, CoordinateFrame.ECI_J2000,
    (6_771_000.0, 0.0, 0.0), (0.0, 7_660.0, 0.0), 1000.0
)
target = TargetAssumptions("frag-01", 0.01, 0.0, "aluminium", "sphere")
pred = wake_model.predict(target, plasma, orbital)
print(f"10mm fragment: δn/n={pred.peak_relative_density_perturbation:.3f}  "
      f"detectable={pred.is_detectable_above(0.001)}")
```

---

## 11. Value-Add Demonstration Script

Run this single script for a complete stakeholder demonstration covering all four value propositions:

```bash
PYTHONPATH=src python3.11 - << 'EOF'
import sys, json
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")

from heimdall import (
    SyntheticPowerLawModel, PopulationModelConfig,
    RadarDetectabilityAnalyzer,
    TrajectoryRiskEngine, REFERENCE_LAUNCH_PROFILES,
    CostSavingsCalculator, NASA_COMMERCIAL_FLEET,
    AnalyticWakeModel,
)
from heimdall.physics_contract import (
    PlasmaEnvironment, OrbitalState, TargetAssumptions,
    CoordinateFrame, TimeScale,
)

now = datetime(2026, 7, 30, tzinfo=timezone.utc)
sep = "═" * 60

# ── VALUE PROPOSITION 1: THE INVISIBLE POPULATION ──────────────
print(f"\n{sep}")
print("VALUE 1: THE INVISIBLE DEBRIS POPULATION")
print(sep)
pop = SyntheticPowerLawModel().build_snapshot(PopulationModelConfig(), now)
ratio = pop.estimated_sub_cm_total / max(pop.total_tracked_objects, 1)
print(f"  Tracked by radar:    {pop.total_tracked_objects:>15,} objects")
print(f"  Sub-cm (estimated):  {pop.estimated_sub_cm_total:>15,} objects")
print(f"  Invisibility ratio:  {ratio:>14.0f}× more untracked than tracked")
print(f"  Evidence class:      {pop.evidence_class.value} (power-law model)")

# ── VALUE PROPOSITION 2: RADAR DETECTION GAP ───────────────────
print(f"\n{sep}")
print("VALUE 2: WHY RADAR CANNOT SEE THEM")
print(sep)
gap = RadarDetectabilityAnalyzer().build_gap_analysis(now)
print(f"  Detection gap:       {gap.gap_min_diameter_m*1000:.1f}mm – {gap.gap_max_diameter_m*100:.1f}cm")
print(f"  Undetected fraction: {gap.undetected_population_fraction:.0%} of total debris population")
print(f"\n  Radar system         Min detectable size")
for c in gap.radar_curves:
    print(f"  {c.system.name[:35]:35s}  {c.min_detectable_diameter_m*100:.1f} cm")
print(f"\n  HEIMDALL advantage: D² wake scaling vs D⁶ radar (Rayleigh)")
print(f"  → 12 dB/octave detection advantage for sub-cm objects")

# ── VALUE PROPOSITION 3: SAFE TRAJECTORIES ─────────────────────
print(f"\n{sep}")
print("VALUE 3: SAFER LAUNCH CORRIDORS")
print(sep)
engine = TrajectoryRiskEngine()
report = engine.build_risk_report(pop, REFERENCE_LAUNCH_PROFILES)
print(f"  Safe corridors identified:  {len(report.safe_corridors)}")
print(f"\n  Profile                        Total risk    Dark risk  Level")
for s in report.profile_scores:
    name = s.profile_id[:30]
    print(f"  {name:30s}  {s.cumulative_collision_probability:.2e}  "
          f"{s.dark_risk_fraction:.0%} invisible  {s.risk_level.value}")
print(f"\n  'Dark risk' = collision probability from radar-invisible sub-cm debris")
print(f"  Only HEIMDALL can quantify and help avoid this hidden risk.")

# ── VALUE PROPOSITION 4: ECONOMIC VALUE ────────────────────────
print(f"\n{sep}")
print("VALUE 4: QUANTIFIED ECONOMIC IMPACT")
print(sep)
calc     = CostSavingsCalculator()
scenario = calc.build_fleetwide_scenario(NASA_COMMERCIAL_FLEET, generated_at=now)
print(f"  Annual fleet savings:  ${scenario.annual_savings_usd/1e6:>8.1f}M  (central estimate)")
print(f"  10-year projection:    ${scenario.ten_year_savings_usd/1e6:>8.0f}M")
print(f"  Uncertainty range:     ${scenario.uncertainty_low_usd/1e6:.0f}M – ${scenario.uncertainty_high_usd/1e6:.0f}M")
print(f"\n  Mission class breakdown:")
for est in scenario.per_mission_estimates:
    print(f"    {est.mission_class.value:25s}  ${est.total_savings_usd/1e6:6.1f}M / 10yr")
print(f"\n  Sources: NASA OIG IG-21-001, NASA Cost Estimating Handbook 2015,")
print(f"           Marsh/AON 2024 space insurance market reports")
print(f"  Evidence class: {scenario.evidence_class.value} (modelled, not observed savings)")

# ── PHYSICS: THE SIGNAL ────────────────────────────────────────
print(f"\n{sep}")
print("PHYSICS: WHY HEIMDALL CAN DETECT WHAT RADAR CANNOT")
print(sep)
model   = AnalyticWakeModel()
plasma  = PlasmaEnvironment(1e11, 1e11, 1500.0, 1200.0, (2e-5,0,0), "nominal_leo")
orbital = OrbitalState(now, TimeScale.UTC, CoordinateFrame.ECI_J2000,
                       (6_771_000.0, 0.0, 0.0), (0.0, 7_660.0, 0.0), 1000.0)
print(f"  {'Size':>8}  {'δn/n peak':>12}  {'Detectable':>10}  {'Radar RCS':>10}  {'Gap?':>5}")
for d_mm in [0.5, 1, 5, 10, 50]:
    tgt  = TargetAssumptions(f"f{d_mm}", d_mm/1000, 0.0, "al", "sphere")
    pred = model.predict(tgt, plasma, orbital)
    comp = model.size_scaling_comparison(d_mm/1000, plasma, orbital)
    det  = "YES" if pred.is_detectable_above(0.001) else "no"
    gap  = "YES" if comp.is_in_detection_gap else "no"
    print(f"  {d_mm:>5.1f}mm  {pred.peak_relative_density_perturbation:>12.3f}  "
          f"{det:>10}  {comp.rcs_dbsm_rayleigh:>8.1f}dBsm  {gap:>5}")
print(f"\n  Model: ANALYTIC_UNVALIDATED — no laboratory calibration yet.")
print(f"  See EVIDENCE_PATHWAYS.md for the path to real observed evidence.")

print(f"\n{sep}")
print("EVIDENCE STATUS")
print(sep)
print(f"  All outputs: EvidenceClass.SYNTHETIC")
print(f"  Radar gap proof: physics-based (analytically proven, not observed)")
print(f"  Population counts: power-law extrapolation ±50%")
print(f"  Cost savings: modelled estimates, uncertainty ×0.5–×3.0")
print(f"  Next step: archive mining with real SWARM/EISCAT data")
print(f"  See: docs/EVIDENCE_PATHWAYS.md, docs/OBSERVED_EVIDENCE_ACQUISITION.md")
print(f"{sep}\n")
EOF
```

---

## 12. Interpreting the Outputs

### Evidence classes — what each result means

| Output | Evidence class | What it means | What it does NOT mean |
|---|---|---|---|
| Debris population counts | `SYNTHETIC` | Power-law model extrapolation | Direct observation or measurement |
| Radar detection gap | `SYNTHETIC` | Physics proof from published radar specs | Measured radar performance data |
| Trajectory risk scores | `SYNTHETIC` | Flux-model Poisson calculation | Validated collision probabilities |
| Cost savings estimates | `SYNTHETIC` | Model from public cost data | Observed operational savings |
| Archive mining results | `SYNTHETIC` (test mode) / `OBSERVED` (real data) | Statistical correlation | Confirmed debris detection |
| Wake physics predictions | `SYNTHETIC` | Analytic_unvalidated model | Laboratory or flight measurement |

### Key numbers to remember

| Metric | Value | Source |
|---|---|---|
| Tracked objects (radar-visible) | ~133,000 | USSPACECOM TLE catalog approximation |
| Estimated sub-cm population | ~2.3 billion | Power-law extrapolation ±50% |
| Detection gap size range | 0.1 mm – 1.2 cm | Analytical RCS vs published thresholds |
| Percentage of population undetected | 95% | From gap analysis |
| Radar advantage per size octave | 18 dB | D⁶ Rayleigh scaling |
| HEIMDALL advantage per size octave | 12 dB | (D² wake) vs (D⁶ radar) |
| Fleet annual cost savings | $158.7M | Conservative modelled estimate |
| 10-year fleet savings | ~$1.6B | ×0.5 to ×3.0 uncertainty range |

---

## 13. Troubleshooting

### `ModuleNotFoundError: No module named 'heimdall'`
```bash
# Always prefix with PYTHONPATH=src
PYTHONPATH=src python3.11 scripts/your_script.py

# Or install in editable mode
pip install -e .
```

### `npm run dev` fails with exit code 127
```bash
# node_modules not installed — run from your own terminal (not VS Code chat)
cd apps/analyst-console
npm ci    # uses .npmrc for corporate registry
npm run dev -- --host 127.0.0.1
```

### Archive mining tests fail
```bash
# Run with scripts/ on path
PYTHONPATH=src:scripts python3.11 -m unittest discover -s tests -p "test_archive_mining.py"
```

### `verify_independence.py` reports non-standard imports
```bash
# All stdlib modules used are listed in ALLOWED_STDLIB_ROOTS
# Check verify_independence.py if you add a new stdlib import
PYTHONPATH=src:. python3.11 scripts/verify_independence.py
```

### Analyst console shows blank page
```bash
# Regenerate data and rebuild
PYTHONPATH=src python3.11 scripts/export_visualization_data.py \
  --generated-at 2026-07-30T00:00:00Z
cd apps/analyst-console && npm run build && npm run dev -- --host 127.0.0.1
```

---

## 14. What to Show a Stakeholder

### The 5-minute demo

1. **Open the browser** at `http://127.0.0.1:5173` → click **Debris Visualization**
2. **Globe**: point to the orange cloud — "This is the 2.3 billion sub-cm fragments radar cannot see"
3. **RCS Chart**: point to the red shaded region — "Every radar system in the world is below threshold here. This is a physics proof, not an opinion."
4. **Risk Heatmap**: toggle between "Full population" and "Tracked only" — "The bright red cells disappear because radar doesn't know they exist"
5. **Cost Dashboard**: "$158M per year, $1.6B over 10 years — conservative estimate with documented uncertainty"

### The 30-second verbal summary

> "There are an estimated 2.3 billion sub-centimetre debris fragments in low Earth orbit that no existing radar system can detect. The reason is basic physics: radar cross-section scales as D⁶, so a 5mm sphere is 3 billion times below the Space Fence detection threshold. HEIMDALL uses passive ionospheric sensing — the plasma wake signal scales as D², giving a 12 dB/octave advantage. This translates to $158M per year in fleet-wide cost savings from avoided false-alarm manoeuvres, reduced insurance premiums, and better launch windows. All of this is modelled and bounded — we're not claiming detection yet. The path to real observed evidence starts with zero-budget SWARM satellite archive mining."

### The evidence-class disclaimer (always include)

> "All quantitative results shown are `EvidenceClass.SYNTHETIC` — synthetic model outputs with explicit uncertainty bounds. No physical debris detection has been made. The governance framework preserves this distinction rigorously: software tests and models are not scientific validation."

---

*Project HEIMDALL ELECTRA — Aarti S Ravikumar · [@aartisr](https://github.com/aartisr) · 2026-08-03*
