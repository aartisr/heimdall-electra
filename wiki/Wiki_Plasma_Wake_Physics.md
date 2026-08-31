# Ionospheric Plasma Wake Physics & Shock Wave Formulation

**Canonical Production Suite:** [https://nasa.ai-aarti.com](https://nasa.ai-aarti.com)  
**Principal Investigator & Author:** Aarti S. Ravikumar ([@aartisr](https://github.com/aartisr))  
**Repository:** [https://github.com/aartisr/heimdall-electra](https://github.com/aartisr/heimdall-electra)  

---

## 1. Physics of Hypervelocity Debris in Ionospheric Plasma

In Low Earth Orbit (LEO, $h \approx 300\text{–}1000\text{ km}$), orbital debris travels at velocities $v_{\text{rel}} \approx 7.5\text{–}10.5\text{ km/s}$ through the ionospheric F-layer plasma.

The ambient ionosphere is characterized by:
- **Electron Density:** $n_e \approx 10^{11}\text{–}10^{12}\text{ m}^{-3}$
- **Electron / Ion Temperature:** $T_e \approx 1200\text{–}2500\text{ K}$, $T_i \approx 800\text{–}1500\text{ K}$
- **Debye Screening Length:**
  $$\lambda_D = \sqrt{\frac{\epsilon_0 k_B T_e}{n_e e^2}} \approx 0.5\text{–}2\text{ cm}$$

---

## 2. Supersonic Mach Number & Ion-Acoustic Shock Waves

The ion acoustic speed $C_s$ in the collisionless ionospheric plasma is defined as:

$$C_s = \sqrt{\frac{k_B (T_e + \gamma_i T_i)}{m_i}} \approx 1.5\text{–}2.2\text{ km/s}$$

Because $v_{\text{rel}} \gg C_s$, the debris operates at high acoustic Mach numbers:

$$M_s = \frac{v_{\text{rel}}}{C_s} \approx 4\text{–}6$$

As the object moves through the ionosphere, it sweeps through the ion background faster than the ions can thermally disperse, carving out a supersonic **rarefaction wake** and driving an **ion-acoustic shock compression wave** at the Mach cone angle:

$$\theta_{\text{Mach}} = \arcsin\left(\frac{1}{M_s}\right) \approx 10^\circ\text{–}15^\circ$$

---

## 3. Effective Radar Cross-Section (RCS) Amplification

The localized plasma disturbance $\delta n_e$ increases the effective dielectric permittivity contrast in the vicinity of the object.

Aarti formulated the analytical RCS amplification model:

$$\sigma_{\text{eff}}(f_0, v_{\text{rel}}, d) = \sigma_{\text{geom}} \cdot \left[ 1 + \alpha_{\text{wake}} \cdot \left(\frac{v_{\text{rel}}}{C_s}\right)^2 \cdot \frac{f_p^2}{f_0^2 + \nu_{ei}^2} \right]$$

where:
- $\sigma_{\text{geom}} = \frac{\pi}{4} d^2$ is the optical geometric cross-section.
- $f_p = \frac{1}{2\pi}\sqrt{\frac{n_e e^2}{\epsilon_0 m_e}}$ is the plasma frequency ($\sim 5\text{–}12\text{ MHz}$).
- $\nu_{ei}$ is the electron-ion collision frequency ($\sim 10^3\text{ s}^{-1}$).
- $f_0$ is the carrier frequency of the illuminating forward-scatter RF emitter.

---

## Backlinks & Exploration
* **Interactive Live Suite:** [https://nasa.ai-aarti.com](https://nasa.ai-aarti.com)
* **Wiki Home:** [Home.md](Home.md)
* **TDOA Kinematics:** [Wiki_TDOA_Kinematics.md](Wiki_TDOA_Kinematics.md)
* **Conjunction Risk Assessment:** [Wiki_Conjunction_Risk.md](Wiki_Conjunction_Risk.md)
