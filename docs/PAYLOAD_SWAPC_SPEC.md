# HEIMDALL — Spacecraft Payload & SWaP-C Architecture

This document provides the full aerospace engineering specification, mass/power margins, link budget, and digital signal processing architecture for HEIMDALL payloads across three flight form factors.

---

## 1. Platform Form-Factor Comparison Matrix

| Subsystem / Metric | 3U CubeSat (Tech Demo) | 6U Sentinel (Constellation) | ESPA Hosted Payload |
| :--- | :--- | :--- | :--- |
| **Total Spacecraft Mass** | **$4.0\text{ kg}$** | **$8.5\text{ kg}$** | **$25.0\text{ kg}$** |
| **Sensor Payload Mass** | $1.25\text{ kg}$ | $2.40\text{ kg}$ | $6.20\text{ kg}$ |
| **Mass Margin Reserve (NASA Class D)** | **$+31.2\%$** (Req: $>20\%$) | **$+34.5\%$** (Req: $>20\%$) | **$+42.0\%$** (Req: $>20\%$) |
| **Peak Power Consumption** | $18.5\text{ W}$ | $35.0\text{ W}$ | $85.0\text{ W}$ |
| **Average Orbit Power** | $9.8\text{ W}$ | $16.5\text{ W}$ | $38.0\text{ W}$ |
| **Power Margin Reserve** | **$+28.4\%$** | **$+32.1\%$** | **$+45.0\%$** |
| **Deployable Boom Configuration** | 4-Boom Dipole ($1.0\text{ m}$) | 6-Boom Array ($1.5\text{ m}$) | 8-Boom Interferometer ($2.5\text{ m}$) |
| **ADC Sampling Frequency** | $250\text{ kHz}$ / 16-bit | $500\text{ kHz}$ / 16-bit | $1.0\text{ MHz}$ / 24-bit |
| **Wavelet DSP Compression** | $24:1$ Haar/Daubechies | $32:1$ Symlet Wavelet | $48:1$ Deep Adaptive |
| **Telemetry Downlink Bandwidth** | **$0.44\text{ Mbps}$** (S-Band) | **$1.85\text{ Mbps}$** (S/X-Band) | **$12.5\text{ Mbps}$** (X-Band) |
| **Detection Sensitivity Floor** | $\mathbf{0.1\text{ mm}}$ | $\mathbf{0.08\text{ mm}}$ | $\mathbf{0.05\text{ mm}}$ |
| **Target Orbit Regime** | $400 - 650\text{ km}$ (LEO) | $500 - 850\text{ km}$ (SSO) | $600 - 1200\text{ km}$ (LEO/MEO) |

---

## 2. Electrical & Sensor Front-End Architecture

```
 ┌────────────────────────────────────────────────────────┐
 │ DEPLOYABLE BOOM ARRAY (4x - 8x Spherical Probes)        │
 └──────────────────────────┬─────────────────────────────┘
                            ▼
 ┌────────────────────────────────────────────────────────┐
 │ ANALOG FRONT END (AFE)                                  │
 │ • Low-Noise Charge Sensitive Preamplifiers (< 5 nV/√Hz)│
 │ • Programmable Bandpass Filter (1 kHz - 150 kHz)       │
 └──────────────────────────┬─────────────────────────────┘
                            ▼
 ┌────────────────────────────────────────────────────────┐
 │ HIGH-SPEED ADC (16-bit / 250 kHz - 1 MHz SAR ADC)       │
 └──────────────────────────┬─────────────────────────────┘
                            ▼
 ┌────────────────────────────────────────────────────────┐
 │ ONBOARD RADIATION-TOLERANT FPGA (Microchip PolarFire)  │
 │ • Real-time Continuous Wavelet Transform (CWT)         │
 │ • Mach Shock Waveform Template Matcher                 │
 │ • Hyperbolic TDOA Triangulation Solver                 │
 └──────────────────────────┬─────────────────────────────┘
                            ▼
 ┌────────────────────────────────────────────────────────┐
 │ COMPRESSED TELEMETRY ENGINE ──▶ S/X-Band Downlink      │
 └────────────────────────────────────────────────────────┘
```

---

## 3. NASA GEVS & Environmental Qualification Standards

The HEIMDALL payload hardware design complies with **NASA General Environmental Verification Standard (GSFC-STD-7000B)** for Class D missions:

1. **Random Vibration**: Tested to $14.1\text{ g}_\text{rms}$ (Qual level) across $20 - 2000\text{ Hz}$.
2. **Thermal Vacuum (TVAC)**: 4 operational thermal cycles from $-30^\circ\text{C}$ to $+60^\circ\text{C}$ at pressures $< 10^{-5}\text{ Torr}$.
3. **Total Ionizing Dose (TID)**: Rad-tolerant components rated for $> 15\text{ krad}(\text{Si})$, providing $> 3\text{ years}$ lifetime at $600\text{ km}$.
4. **Single Event Effects (SEE)**: Latchup immune to $> 60\text{ MeV}\cdot\text{cm}^2/\text{mg}$ using PolarFire Flash-based FPGA architecture.
