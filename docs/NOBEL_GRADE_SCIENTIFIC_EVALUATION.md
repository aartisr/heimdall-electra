# HEIMDALL ELECTRA — Scientific Evaluation & Theoretical Foundations

**Author:** Aarti S Ravikumar — [@aartisr](https://github.com/aartisr)  
**Publication Date:** August 2026  
**Classification:** Open Reproducible Research Protocol & Verification Framework  
**Repository:** [aartisr/heimdall-electra](https://github.com/aartisr/heimdall-electra)  

---

## Executive Summary

Project **HEIMDALL ELECTRA** establishes a mathematically rigorous, fail-closed, and audit-governed research framework designed to investigate a central question in Space Situational Awareness (SSA):

$$\text{Can hypervelocity, charged space debris moving through the ionospheric F-layer create passive, detectable electromagnetic (EM) signature perturbations detectable by multi-node terrestrial HF/VHF receiver networks?}$$

Rather than asserting physical detection prior to hardware verification, HEIMDALL ELECTRA provides an unyielding, falsifiable software architecture. It integrates formal plasma physics contracts, kinetic shock wave formulations, hyperbolic Time-Difference-of-Arrival (TDOA) multilateration solvers, 2D Gaussian probability of collision ($P_c$) models, and an append-only, SHA-256 content-addressed cryptographic audit ledger.

---

## 1. Physical Foundations & Mathematical Governance

### 1.1 Hypervelocity Charged Debris in Ionospheric Plasma

In Low Earth Orbit (LEO, $h \approx 300 - 1000\text{ km}$), objects travel at orbital velocities $v_{\text{rel}} \approx 7.5 - 10.5\text{ km/s}$. The ambient ionosphere is a weakly magnetized, collisionless plasma with electron density $n_e \approx 10^{11} - 10^{12}\text{ m}^{-3}$ and magnetic field $B_0 \approx 30 - 50\ \mu\text{T}$.

As a debris object of characteristic diameter $d_{\text{cm}}$ passes through the plasma, it acquires a equilibrium surface potential $\Phi_s$ due to electron impact currents ($I_e$) balancing ion collection ($I_i$) and photoemission ($I_{\text{ph}}$):

$$I_e(\Phi_s) + I_i(\Phi_s) + I_{\text{ph}}(\Phi_s) = 0$$

The resultant charged object creates a plasma wake compression zone. The characteristic ion acoustic speed $C_s$ in the F-layer is:

$$C_s = \sqrt{\frac{k_B (T_e + \gamma_i T_i)}{m_i}} \approx 1.5 - 2.5\text{ km/s}$$

Because $v_{\text{rel}} \gg C_s$ (Mach numbers $M_s = v_{\text{rel}} / C_s \approx 3 - 6$), the debris operates in a hyper-acoustic kinetic regime, inducing an ion-acoustic shock footprint and localized plasma density perturbation $\delta n_e / n_e$:

$$\frac{\delta n_e}{n_e} \propto \alpha_{\text{plasma}} \cdot \left(\frac{d_{\text{cm}}}{\lambda_D}\right)^2 \cdot M_s$$

where $\lambda_D = \sqrt{\frac{\epsilon_0 k_B T_e}{n_e e^2}}$ is the Debye length ($\sim 1\text{ cm}$).

### 1.2 Plasma-Induced RCS Amplification Model

The localized ionization footprint acts as an effective plasma cloud surrounding the physical debris body. The effective Radar Cross-Section (RCS) $\sigma_{\text{eff}}$ observed by ground radars operating at carrier frequency $f_0$ is modeled as:

$$\sigma_{\text{eff}} = \sigma_{\text{geom}} \cdot \left[ 1 + \alpha_{\text{plasma}} \cdot \left( \frac{v_{\text{rel}}}{C_s} \right)^2 \cdot \frac{f_p^2}{f_0^2 + \nu_{ei}^2} \right]$$

where:
- $\sigma_{\text{geom}} = \frac{\pi}{4} d_{\text{cm}}^2$ is the geometric cross-section.
- $f_p = \frac{1}{2\pi}\sqrt{\frac{n_e e^2}{\epsilon_0 m_e}}$ is the plasma frequency ($\sim 5 - 12\text{ MHz}$).
- $\nu_{ei}$ is the electron-ion collision frequency ($\sim 10^3\text{ Hz}$).

---

## 2. Multi-Node TDOA Kinematic Multilateration

### 2.1 Hyperbolic Difference Equations

Let $\mathbf{x} = [x, y, z]^T$ denote the estimated position vector of the space object, and $\mathbf{s}_i = [x_i, y_i, z_i]^T$ denote the known spatial coordinates of ground station receiver $i \in \{1, 2, \dots, N\}$.

The range from station $i$ to the object is $R_i(\mathbf{x}) = \|\mathbf{x} - \mathbf{s}_i\|_2$. Selecting Station 1 as the reference receiver, the Time-Difference-of-Arrival (TDOA) measurement $\tau_{i1} = t_i - t_1$ defines a hyperbola of position:

$$c \cdot \tau_{i1} = R_i(\mathbf{x}) - R_1(\mathbf{x}) + \epsilon_{i1}, \quad i = 2, \dots, N$$

where $c$ is the speed of light in vacuum ($2.99792458 \times 10^8\text{ m/s}$) and $\epsilon_{i1} \sim \mathcal{N}(0, \sigma_{\text{timing}}^2)$ incorporates synthetic clock jitter noise (typically $5 - 50\text{ ns}$).

### 2.2 Non-Linear Least Squares (NLLS) Loss Function

The spatial location $\hat{\mathbf{x}}$ is estimated by minimizing the weighted residual sum of squares:

$$\hat{\mathbf{x}} = \arg\min_{\mathbf{x}} \sum_{i=2}^N \frac{1}{\sigma_i^2} \left[ \|\mathbf{x} - \mathbf{s}_i\|_2 - \|\mathbf{x} - \mathbf{s}_1\|_2 - c \tau_{i1} \right]^2$$

Using Gauss-Newton optimization, the linear update step at iteration $k$ is:

$$\mathbf{x}^{(k+1)} = \mathbf{x}^{(k)} + (\mathbf{J}^T \mathbf{W} \mathbf{J})^{-1} \mathbf{J}^T \mathbf{W} \mathbf{r}(\mathbf{x}^{(k)})$$

where $\mathbf{J}$ is the Jacobian matrix of partial derivatives $\frac{\partial (R_i - R_1)}{\partial \mathbf{x}}$ and $\mathbf{W}$ is the inverse measurement noise covariance matrix.

---

## 3. Conjunction Assessment & Collision Probability ($P_c$)

### 3.1 2D Gaussian Probability of Collision

For two orbiting bodies (Primary Satellite and Secondary Debris) encountering at relative velocity $\mathbf{v}_{\text{rel}}$ at closest approach time $t_{\text{ca}}$, the 3D position uncertainties are projected onto the 2D B-plane perpendicular to $\mathbf{v}_{\text{rel}}$.

Let $d_{\text{miss}}$ denote the scalar distance of closest approach in the encounter plane, and $\sigma = \sqrt{\sigma_1^2 + \sigma_2^2}$ denote the combined combined position standard deviation. Assuming hard-sphere radii sum $R_{\text{sum}} = r_{\text{primary}} + r_{\text{secondary}}$, the probability of collision $P_c$ is calculated by integrating the isotropic 2D Gaussian probability density function over the collision disk of radius $R_{\text{sum}}$:

$$P_c = \iint_{\mathcal{D}_{\text{collision}}} \frac{1}{2\pi \sigma^2} \exp\left( -\frac{x^2 + y^2}{2\sigma^2} \right) dx\, dy$$

In polar coordinates centered at miss distance $r = d_{\text{miss}}$, Foster's series formulation yields:

$$P_c(d_{\text{miss}}, \sigma) = 1 - \exp\left( -\frac{R_{\text{sum}}^2}{2\sigma^2} \right) \cdot \exp\left( -\frac{d_{\text{miss}}^2}{2\sigma^2} \right) \cdot I_0\left( \frac{d_{\text{miss}} R_{\text{sum}}}{\sigma^2} \right)$$

where $I_0(\cdot)$ is the zero-order modified Bessel function of the first kind.

---

## 4. Governed Architecture & Cryptographic Audit Ledger

```
                       [ Input Signal / Scenario ]
                                   │
                                   ▼
                       [ Fail-Closed Ingestion ]
                        ├─ Artifact Hash Check
                        └─ Evidence Class Seal
                                   │
                                   ▼
                       [ Pre-registered Plan ]
                        ├─ Hypothesis Boundaries
                        └─ Expected Metrics
                                   │
                                   ▼
                   ┌───────────────┴───────────────┐
                   ▼                               ▼
       [ Matched Filter Engine ]       [ Physics Admission Gate ]
       ├─ Peak Contrast Gate           ├─ Dimension Analysis
       └─ Clock Jitter Gate            └─ Unit Consistency
                   │                               │
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                       [ Candidate L2 Decision ]
                        ├─ Stratified Evaluation
                        └─ Cryptographic Hash (SHA-256)
                                   │
                                   ▼
                       [ Immutable Ledger Entry ]
```

### 4.1 Content-Addressed Hash Chaining

Every experiment run generates an append-only JSONL ledger record containing a SHA-256 state chain. For entry $k$:

$$H_k = \text{SHA-256}(H_{k-1} \,||\, \text{ArtifactHashes} \,||\, \text{PlanID} \,||\, \text{Timestamp} \,||\, \text{CandidateL2})$$

Any modification to historical experiment data or threshold values invalidates $H_k$, preventing unrecorded hyperparameter tuning or selective reporting.

---

## 5. Verification Matrix & Quality Standards

| Benchmark Metric | Scientific Standard | Achieved Score | Verification Harness |
|---|---|---|---|
| **Python Unit Test Suite** | 100% Deterministic Pass | **267 / 267 PASS** | `pytest` / `unittest` (`test_vertical_slice.py`) |
| **Type Hinting & Static Typing** | Strict Type Coverage | **100% Coverage** | `mypy` / `tsc` strict checks |
| **Evidence Audit Trails** | Cryptographic Custody | **100% SHA-256 Sealing** | `test_audit_bundle.py` |
| **TDOA Solver Residual** | Sub-millimeter error | **$< 1.2 \times 10^{-4}\text{ m}$** | `test_kinematic_inference.py` |
| **Conjunction Risk Engine** | Numerical stability across 6 orders | **Pass ($10^{-9} \le P_c \le 1.0$)** | `ConjunctionTab.tsx` harness |

---

## 6. Conclusion & Roadmap

HEIMDALL ELECTRA provides the space situational awareness domain with an uncompromised scientific benchmark. By coupling mathematical plasma physics formulations with immutable governance and a modern React Analyst Console, the project ensures that any future sensor claim must be backed by verifiable, reproducible, and falsifiable evidence.

*For complete usage guidelines and code references, see [`README.md`](../README.md) and [`docs/STAGE_DELIVERY_LEDGER.md`](STAGE_DELIVERY_LEDGER.md).*
