# HEIMDALL / Electra — Orbital Debris Assessment & Physics Suite

[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-blue.svg)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-19.0-61dafb.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4.0-38bdf8.svg)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Vite-6.2-646cff.svg)](https://vitejs.dev/)

An advanced, interactive orbital debris analytics, physics modeling, and evaluation suite for the **HEIMDALL** project. This suite visualizes the low-Earth orbit (LEO) sub-centimeter debris population, models the radar detection gap physics ($D^2$ wake scaling vs $D^6$ Rayleigh radar scaling), evaluates launch trajectory flux fields, and projects fleet-wide economic savings.

---

## 🚀 Quick Start (Run Locally)

### Prerequisites
Make sure you have **Node.js (v18+ or v20+ recommended)** and **npm** (or `pnpm`, `yarn`, `bun`) installed on your system.
- Check Node version:
  ```bash
  node -v  # Should be v18.0.0 or higher
  ```

---

### Step 1: Clone the Repository
Clone the repository and checkout the `develop` branch:
```bash
git clone -b develop https://github.com/aartisr/heimdall-electra.git
cd heimdall-electra
```

---

### Step 2: Install Dependencies
Install all project dependencies:
```bash
npm install
```
*(Alternative package managers: `pnpm install`, `yarn install`, or `bun install`)*

---

### Step 3: Start the Development Server
Run the local Vite development server:
```bash
npm run dev
```

The application will start on **`http://localhost:3000`** (or the port specified in terminal output).
Open [http://localhost:3000](http://localhost:3000) in your web browser.

---

### Step 4: Available Scripts

| Command | Description |
| :--- | :--- |
| `npm run dev` | Starts the Vite local development server on port `3000` |
| `npm run build` | Compiles TypeScript and builds optimized production assets in `/dist` |
| `npm run preview` | Locally serves the built production bundle for staging verification |
| `npm run lint` | Runs `tsc --noEmit` to validate complete TypeScript type safety |
| `npm run clean` | Cleans up previous build artifacts and distribution files |

---

## 🛰️ Key Features & Interactive Modules

### 1. Executive Pitch & Grant Review Deck
- **Interactive 6-Stage Narrative**: Seamless presentation mode designed for NASA review boards, DoD evaluators, and private investors.
- **Embedded Visual Proofs & Speaker Notes**: Instant walkthrough covering the $0.1\text{ mm}$ threat, $D^2$ wake scaling, CubeSat SWaP-C budget, ionospheric robustness, $\$1.6\text{B}$ fleet value, and proposal milestones.

### 2. Satellite Payload Engineering & SWaP-C Budget
- **Interactive Form-Factor Sizing**: Full parametric budget for 3U CubeSat, 6U Constellation Sentinel, and ESPA Ring secondary hosted payloads.
- **Subsystem Telemetry**: Real-time mass margins (&gt;31% reserve), power consumption (&lt;12 W average), S/X-Band downlink link budgets, deployable boom lengths ($0.5\text{ m} - 2.5\text{ m}$), and FPGA wavelet DSP compression.
- **NASA GEVS & Class D Compliance**: Automated JSON export of complete payload specifications.

### 3. Ionospheric Diurnal & Solar Activity Engine
- **Atmospheric Model Integration**: Benchmarked against **IRI-2020** (International Reference Ionosphere) and **NRLMSISE-00** neutral atmosphere models.
- **24/7 Detection Proof**: Models solar radio flux ($F_{10.7} = 70 - 220\text{ sfu}$), geomagnetic latitude, and diurnal day/eclipse phases, proving that supersonic Mach cone shock amplification ($M = 3 - 8$) maintains $\text{SNR} &gt; 12\text{ dB}$ even during orbital night.

### 4. NASA & DoD Grant Alignment Dashboard
- **Federal Solicitation Coverage**: Comprehensive alignment matrices for **NASA NIAC (Phase I/II)**, **NASA SBIR/STTR Subtopic Z1.03**, and **US Space Force Space Prime (SDA)**.
- **Proposal Generation**: One-click download of formatted proposal packages, technical abstracts, requirements compliance tables, and TRL 2 ➔ 4 transition roadmaps.

### 5. 3D Rotating Orbital Debris Globe
- **Custom 3D HTML5 Canvas Engine**: Real-time vector-projected orbital mechanics simulating over 2,400 sub-cm particle swarms ($2.4\text{B}$ statistical cloud) and cataloged debris.
- **Historical Breakup Clouds**: Visualizes concentrated fragmentation clusters from *Fengyun-1C*, *Iridium-33*, *Cosmos-2251*, *Cosmos-1408 ASAT*, and upper stage breakups.
- **Interactive Controls**: 360° mouse drag rotation, zoom in/out, orbital propagation toggle, and dynamic layer filters for Tracked ($>10\text{ cm}$), Near-detectable ($1-10\text{ cm}$), Sub-cm (HEIMDALL domain), and Fragmentation clouds.

### 6. Radar Detection Gap — Physics Proof
- **$D^2$ vs $D^6$ Analytical Scaling Model**: Visualizes the Rayleigh-to-Mie scattering transition across radar cross sections ($\text{RCS}$) from $0.1\text{ mm}$ to $1\text{ m}$.
- **Radar Comparisons**: Benchmarks published limits for **Space Fence**, **Haystack LRIR**, **Goldstone Solar System Radar**, and **TIRA** against HEIMDALL plasma wake detection.
- **Detection Gap Isolation**: Highlights the $0.1\text{ mm} - 0.3\text{ cm}$ radar-dark regime where ~95% of lethal kinetic impactors remain invisible to terrestrial tracking.

### 7. Trajectory Risk Field — Safe Launch Corridors
- **2D Orbital Flux Heatmap**: Maps orbital inclination ($0^\circ - 180^\circ$) against orbital altitude ($200\text{ km} - 2000\text{ km}$).
- **Mission Scoring**: Evaluates orbital insertion risk profiles for Crewed ISS Resupply, LEO Megaconstellations, Sun-Synchronous (SSO), and Polar Science corridors.
- **Dual Population View**: Toggle between *Full population (HEIMDALL)* and *Tracked only (Radar)* to identify dark risk fractions.

### 8. Fleet-Wide Cost Savings — HEIMDALL Economic Value
- **10-Year Cumulative Savings Engine**: Quantifies avoided collision avoidance maneuvers ($\Delta V$ conservation), launch window hold reductions, insurance risk credits, and mission life extensions.
- **Mission Category Breakdown**: Granular economics for Crewed LEO ($\$200\text{M}$), ISS Resupply ($\$51\text{M}$), NASA Science SSO ($\$27\text{M}$), Commercial GEO ($\$36\text{M}$), and LEO Constellations.
- **Uncertainty Bounds**: Full parametric sensitivity modeling across $\times 0.5$ to $\times 3.0$ uncertainty ranges.

### 9. Multi-Station TDOA Triangulation & Conjunction Simulator
- **Plasma Wake Triangulation**: Interactive hyperbolic time-difference-of-arrival (TDOA) solver for multiple receiver craft.
- **Probability of Collision ($\text{PoC}$)**: Covariance intersection and B-plane collision probability calculator.

### 10. Elevation Engine & Governance Verification
- **Scientific Falsifiability Matrix**: Claim verification framework distinguishing empirical evidence from synthetic modeling.
- **6-Dimension Evaluation Framework**: Rigorous tracking across Physics Soundness, Algorithm Maturity, Engineering Feasibility, Commercial Viability, Testing Rigor, and Mission Architecture.

---

## 🏗️ Project Architecture & Directory Structure

```text
heimdall-electra/
├── index.html                   # HTML entry point with metadata tags
├── metadata.json                # Project metadata & permissions
├── package.json                 # Dependencies and execution scripts
├── tsconfig.json                # TypeScript compiler configuration
├── vite.config.ts               # Vite bundler & Tailwind v4 plugin setup
│
└── src/
    ├── App.tsx                  # Main application orchestrator & tab navigation
    ├── main.tsx                 # React 19 root DOM mount
    ├── index.css                # Tailwind CSS v4 styling entry
    ├── types.ts                 # Global TypeScript interfaces & domain types
    │
    ├── components/              # Self-contained, modular UI components
    │   ├── Header.tsx                   # Top navigation & system status badge
    │   ├── Footer.tsx                   # System disclaimers & footer
    │   ├── ScorecardOverview.tsx        # Executive 6-dimension evaluation dashboard
    │   ├── RotatingDebrisGlobeCanvas.tsx# 3D interactive rotating Earth & debris cloud
    │   ├── RadarDetectionGapChart.tsx   # Radar detection gap & D² vs D⁶ physics curves
    │   ├── TrajectoryRiskFieldChart.tsx # 2D launch corridor risk heatmap
    │   ├── FleetCostSavingsChart.tsx    # Horizontal stacked bar fleet ROI chart
    │   ├── DebrisRiskEconomicCharts.tsx # Full debris analytics & economic workbench
    │   ├── PhysicsTdoaSim.tsx           # Multi-sensor TDOA triangulation simulator
    │   ├── ConjunctionRiskSim.tsx       # Collision probability & B-plane simulator
    │   ├── DimensionDeepDives.tsx       # Deep dive analysis across all 6 dimensions
    │   ├── ClaimGovernanceViewer.tsx    # Falsifiable claims & governance ledger
    │   ├── ElevationEngine.tsx          # Upgrade recommendations & roadmap elevator
    │   ├── CustomScoreCalculator.tsx    # Interactive weighted scoring matrix
    │   ├── CodeSpecExplorer.tsx         # Specification document browser
    │   ├── StrategicRoadmap.tsx         # Milestone execution phases
    │   └── TestSuiteInspector.tsx       # Unit test and verification suite explorer
    │
    └── data/                    # Static datasets, analytics models & specs
        ├── debrisAnalyticsData.ts       # Fleet economics & debris flux parameters
        ├── elevationUpgrades.ts         # Upgrade specifications & roadmap items
        ├── evaluationData.ts            # Scorecard dimensions & SWOT metrics
        └── specData.ts                  # Mathematical formulations & code specs
```

---

## 🛠️ Tech Stack & Dependencies

- **Frontend Framework**: [React 19](https://react.dev/) + [TypeScript 5.8](https://www.typescriptlang.org/)
- **Build Tool**: [Vite 6.2](https://vitejs.dev/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/) with `@tailwindcss/vite`
- **Icons**: [Lucide React](https://lucide.dev/)
- **Motion & Interactions**: [Motion](https://motion.dev/)
- **Rendering Engines**: HTML5 Canvas 2D/3D Vector Projections & Responsive SVGs

---

## 🔬 Scientific & Evidence Disclaimers

- **Evidence Class (Synthetic)**: Debris flux distributions, sub-cm count estimates ($2.4\text{B}$), and radar detection curves are derived from published theoretical indices (e.g., standard power-law size distributions, Mie scattering theory, and NASA ORDEM/ESA MASTER models).
- **Comparative Reference**: Economic savings and safe corridors are modeled comparative benchmarks intended for mission architecture planning.

---

## 📄 License
Internal Evaluation & Research Suite. Distributed under standard project repository guidelines.
