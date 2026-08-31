# Conjunction Risk Assessment & Collision Probability ($P_c$)

**Canonical Production Suite:** [https://nasa.ai-aarti.com](https://nasa.ai-aarti.com)  
**Principal Investigator & Author:** Aarti S. Ravikumar ([@aartisr](https://github.com/aartisr))  
**Repository:** [https://github.com/aartisr/heimdall-electra](https://github.com/aartisr/heimdall-electra)  

---

## 1. Conjunction Assessment on the B-Plane

When two orbital objects (Primary Operational Satellite and Secondary Orbital Debris) experience a close encounter at time $t_{\text{ca}}$, their relative position vector $\mathbf{r}_{\text{rel}} = \mathbf{r}_2 - \mathbf{r}_1$ and relative velocity vector $\mathbf{v}_{\text{rel}} = \mathbf{v}_2 - \mathbf{v}_1$ define the encounter frame.

The **Encounter B-Plane** is the 2D plane perpendicular to $\mathbf{v}_{\text{rel}}$:
- **Miss Distance:** $d_{\text{miss}} = \|\mathbf{r}_{\text{rel}}(t_{\text{ca}})\|_2$
- **Combined Hard Body Radius:** $R_{\text{hard}} = r_1 + r_2$
- **Combined Covariance:** $\mathbf{C} = \mathbf{C}_1 + \mathbf{C}_2$, projected onto the 2D B-plane.

---

## 2. 2D Gaussian Probability Integral & Foster's Series

Under standard short-encounter assumptions (rectilinear relative motion and static covariance), the collision probability $P_c$ is obtained by integrating the 2D Gaussian distribution over the hard-body collision disk of radius $R_{\text{hard}}$:

$$P_c = \frac{1}{2\pi \sigma_x \sigma_y \sqrt{1 - \rho^2}} \iint_{x^2 + y^2 \le R_{\text{hard}}^2} \exp\left( -\frac{1}{2(1-\rho^2)} \left[ \frac{(x - x_m)^2}{\sigma_x^2} - \frac{2\rho(x - x_m)(y - y_m)}{\sigma_x \sigma_y} + \frac{(y - y_m)^2}{\sigma_y^2} \right] \right) dx\, dy$$

For isotropic covariance ($\sigma_x = \sigma_y = \sigma$), Aarti implemented Foster's modified Bessel function formulation:

$$P_c(d_{\text{miss}}, \sigma) = 1 - \exp\left( -\frac{R_{\text{hard}}^2 + d_{\text{miss}}^2}{2\sigma^2} \right) \cdot I_0\left( \frac{d_{\text{miss}} R_{\text{hard}}}{\sigma^2} \right)$$

where $I_0(z) = \sum_{k=0}^\infty \frac{(z/2)^{2k}}{(k!)^2}$ is the zero-order modified Bessel function of the first kind.

---

## 3. Maneuver Decision Thresholds for Satellite Operators

In the HEIMDALL ELECTRA Analyst Console, conjunction events are color-coded based on NASA CARA thresholds:

| Collision Probability ($P_c$) | Risk Level | Recommended Action |
|---|---|---|
| $P_c \ge 10^{-4}$ | **CRITICAL** (Red) | Mandatory Collision Avoidance Maneuver (CAM) |
| $10^{-7} \le P_c < 10^{-4}$ | **WARNING** (Yellow) | Heightened Sensor Tasking & Orbit Refinement |
| $P_c < 10^{-7}$ | **NOMINAL** (Green) | Routine Monitoring |

---

## Backlinks & Exploration
* **Interactive Live Suite:** [https://nasa.ai-aarti.com](https://nasa.ai-aarti.com)
* **Wiki Home:** [Home.md](Home.md)
* **TDOA Kinematics:** [Wiki_TDOA_Kinematics.md](Wiki_TDOA_Kinematics.md)
* **Cryptographic Governance:** [Wiki_Audit_Governance.md](Wiki_Audit_Governance.md)
