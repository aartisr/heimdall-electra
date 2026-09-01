# HEIMDALL — Live Demonstration & Pitch Walkthrough Script

This script provides an exact, minute-by-minute protocol for pitching and demonstrating the HEIMDALL interactive evaluation suite to NASA review panels, US Space Force / AFWERX judges, aerospace primes, and private space investors.

---

## ⏱️ Recommended 15-Minute Demonstration Protocol

```
 ┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
 │ MIN 00 - 03   │ ──▶ │ MIN 03 - 07   │ ──▶ │ MIN 07 - 11   │ ──▶ │ MIN 11 - 15   │
 │ Executive     │     │ Physics &     │     │ Payload SWaP  │     │ Economic ROI, │
 │ Pitch Deck    │     │ 3D Spatial    │     │ & Ionosphere  │     │ Grants & Q&A  │
 └───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
```

---

### Step 1: Open the Executive Pitch Deck (Minutes 00:00 – 03:00)
- **Navigation**: Click on the **`Executive Pitch Deck`** tab (highlighted in gold in the top bar).
- **What to say**:
  > *"Good morning committee members. Today we are presenting Project HEIMDALL—an in-situ space domain awareness technology that solves the lethal 0.1 mm to 1 cm untracked orbital debris gap in Low Earth Orbit."*
- **Action**:
  - Show **Slide 1 ("The Critical Threat")**: Emphasize that **95% of lethal kinetic impactors** are uncataloged because ground radar sensitivity decays exponentially below target wavelength ($D^6$).
  - Advance to **Slide 2 ("The Physics Breakthrough")**: Explain the $D^2$ plasma wake scaling vs $D^6$ Rayleigh radar scaling.
  - Point to the **Speaker Notes Drawer** to demonstrate transparency of claims and technical rigor.

---

### Step 2: Prove the Radar Detection Gap & 3D Globe (Minutes 03:00 – 07:00)
- **Navigation**: Click the button on Slide 1 or open the **`Debris & ROI Charts`** tab.
- **Actions & Demonstrations**:
  1. **3D Interactive Debris Globe**:
     - Drag the globe 360° to show real-time orbital vector projection.
     - Toggle on the **Historical Breakup Clouds** (*Fengyun-1C*, *Cosmos-1408*, *Iridium-33*).
     - Filter layers to isolate the **Sub-cm ($<1\text{ cm}$) Cloud ($2.4\text{B}$ particles)**.
     - *Key Talking Point*: *"Notice that cataloged satellites represent less than 1% of the collision risk in the 500 to 800 km altitude bands."*
  2. **Radar Detection Gap Chart**:
     - Scroll down to the analytical **$D^2$ vs $D^6$ Scattering Curve**.
     - Highlight the benchmarked detection floors:
       - Space Fence cutoff: $\sim 3\text{ cm}$
       - Haystack LRIR cutoff: $\sim 5\text{ mm}$
       - HEIMDALL Plasma Wake floor: $\mathbf{0.08\text{ mm}}$
     - *Key Talking Point*: *"Every octave reduction in debris diameter drops radar cross-section by 36 dB, while HEIMDALL’s wake drops by only 12 dB. This 24 dB/octave margin is why in-situ plasma sensing breaks through the physical barrier."*
  3. **Trajectory Risk Heatmap**:
     - Toggle between **Tracked Only** vs **Full HEIMDALL Population**.
     - Show that high-inclination (SSO $97^\circ$ and Polar $88^\circ$) launch corridors have a **100% dark risk fraction**.

---

### Step 3: Demonstrate Spacecraft Payload & SWaP-C Budgets (Minutes 07:00 – 09:30)
- **Navigation**: Open the **`Payload & SWaP-C`** tab.
- **Actions & Demonstrations**:
  1. Click through the three form-factor presets:
     - **Dedicated 3U CubeSat** ($4.0\text{ kg}, 18\text{ W}$)
     - **Constellation 6U Sentinel** ($8.5\text{ kg}, 35\text{ W}$)
     - **ESPA Ring Hosted Payload** ($25\text{ kg}, 85\text{ W}$)
  2. Adjust the interactive controls:
     - Drag **Deployable Boom Length** from $0.5\text{ m}$ to $1.5\text{ m}$ and show the sensitivity floor drop to **$0.08\text{ mm}$**.
     - Show the **FPGA ADC Sampling Rate ($250\text{ kHz}$)** and **Wavelet Compression ($24:1$)** resulting in just **$0.44\text{ Mbps}$** downlink bandwidth.
  3. Point to the **NASA GSFC Margin Metrics**:
     - Mass Margin: **$+31\%$ Reserve** (exceeds NASA Class D requirement of $>20\%$).
     - Power Margin: **$+28\%$ Margin**.
  4. Click **"Export SWaP-C Spec (JSON)"** to show proposal readiness.

---

### Step 4: Validate Ionospheric 24/7 Robustness (Minutes 09:30 – 11:30)
- **Navigation**: Open the **`Ionospheric Physics`** tab.
- **Actions & Demonstrations**:
  1. Switch diurnal phases from **Noon** to **Eclipse (Orbital Night)**.
  2. Show how electron density $n_e$ shifts while **Mach number remains supersonic ($M = 3.8 - 7.5$)**.
  3. Show the resulting Signal-to-Noise Ratio: **$\text{SNR} = +14.2\text{ dB}$**, remaining well above the $+6\text{ dB}$ detection threshold.
  4. Point to the live SVG electron density profile curve and current state marker.
  5. *Key Talking Point*: *"Because orbital debris transits at 8 to 14 km/s, supersonic shock amplification compensates for lower night-side plasma density, ensuring continuous 24/7 LEO coverage."*

---

### Step 5: Present Economic Value & Grant Proposals (Minutes 11:30 – 15:00)
- **Navigation**: Open the **`NASA & DoD Grants`** tab.
- **Actions & Demonstrations**:
  1. Review the **NASA SBIR Subtopic Z1.03** ($98\%$ Match, $\$150\text{K} - \$850\text{K}$) and **NASA NIAC Phase I/II** ($95\%$ Match) alignment cards.
  2. Show the itemized **Requirements vs Capability** verification matrix.
  3. Click **"Copy Text"** or **"Download Grant Package"** to show complete proposal documentation.
  4. Return to the **Fleet Cost Savings Chart** to close on the **$\$159\text{M/year}$** fleet-wide operational ROI and **$\$1.6\text{B}$** 10-year cumulative value.

---

## 🎯 Handling Common Reviewer Questions (Q&A Cheat Sheet)

### Q1: *"Can Langmuir probes survive hypervelocity impacts?"*
- **Answer**: *"The deployable booms do not intercept the debris directly. They are passive electrostatic sensors offset by 0.5 to 1.5 meters that detect the passing Debye sheath shockwave. Direct physical impact with the probe has an extremely low probability ($< 10^{-6}$ per year per unit)."*

### Q2: *"How does HEIMDALL distinguish spacecraft charging from real debris wakes?"*
- **Answer**: *"Spacecraft charging occurs on orbital timescales (seconds to minutes) or geomagnetic storm frequencies ($< 1\text{ Hz}$). Hypervelocity debris wakes generate characteristic high-frequency bipolar Mach cone shock transients ($10\text{ kHz} - 100\text{ kHz}$) with rapid rise times ($< 50\ \mu\text{s}$), allowing our onboard FPGA wavelet transform to reject background charging."*

### Q3: *"What is your path to orbit?"*
- **Answer**: *"Our 18-month roadmap begins with Particle-In-Cell (PIC) simulation benchmarks and vacuum chamber plasma wind-tunnel tests (TRL 4), followed by a 3U CubeSat hosted flight experiment via NASA’s CubeSat Launch Initiative (CSLI) / TechEdSat program (TRL 6)."*
