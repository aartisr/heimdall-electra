"""Analytic ionospheric plasma wake model for passive debris detection.

Implements the physics of charged-fragment wake perturbations in LEO plasma,
providing theoretical predictions for HEIMDALL's passive sensing hypothesis.

Physical basis:
    A hypervelocity charged fragment in LEO plasma leaves a transient density
    perturbation (wake) whose EM signature is detectable at ground level.
    The amplitude scales as D² (through surface charge), giving a 12 dB/octave
    advantage over radar (which scales as D⁶ in Rayleigh regime).

    Key quantities:
        Debye length:      λ_D = sqrt(ε₀ k_B T_e / n_e e²)
        Fragment charge:   Q ≈ 4π ε₀ V_s D/2   (surface potential model)
        Wake length:       L ≈ v / (α n_e)      (recombination limited)
        Peak δn/n:         ≈ Q / (4π ε₀ e λ_D² L n_e)

Model tier: analytic_unvalidated.
    No laboratory or flight measurements have been made.
    All outputs carry explicit uncertainty bounds and EvidenceClass.SYNTHETIC.

Plug-and-play: replace AnalyticWakeModel with a PIC (particle-in-cell) adapter
behind the PlasmaWakeModel Protocol without changing any pipeline code.

References:
    Trotignon et al. (1999) — ion wake studies, RPC-MIP
    Eriksson et al. (2006) — Langmuir probe wake signatures
    Lai & Murad (1988)    — spacecraft charging in LEO
    Grün et al. (1985)    — debris flux models
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol

from .domain import EvidenceClass
from .physics_contract import PlasmaEnvironment, OrbitalState, TargetAssumptions


# ---------------------------------------------------------------------------
# Physical constants (exact or NIST 2018 CODATA values)
# ---------------------------------------------------------------------------

_EPSILON_0  = 8.8541878128e-12   # F/m   — permittivity of free space
_K_B        = 1.380649e-23       # J/K   — Boltzmann constant
_E_CHARGE   = 1.602176634e-19    # C     — elementary charge
_ALPHA_O2   = 2.0e-13            # m³/s  — O₂⁺ recombination coefficient (LEO)
_ALPHA_NO   = 4.5e-13            # m³/s  — NO⁺ recombination coefficient (LEO)
_ALPHA_EFF  = (_ALPHA_O2 + _ALPHA_NO) / 2.0   # effective composite


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class SurfacePotentialModel(str, Enum):
    """Model for fragment surface potential in LEO plasma."""
    SUNLIT_PHOTOELECTRIC  = "sunlit_photoelectric"   # +5 to +20 V (photoelectric)
    SHADOW_PLASMA_CURRENT = "shadow_plasma_current"  # -0.1 to -10 V (plasma current)
    CONSERVATIVE_ESTIMATE = "conservative_estimate"  # -1 V (lower bound for detection)


class ModelTier(str, Enum):
    FIXTURE            = "fixture"           # illustrative only, not physics-capable
    ANALYTIC_UNVALIDATED = "analytic_unvalidated"  # equations admitted, not calibrated


# ---------------------------------------------------------------------------
# Domain contracts
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DebyeParameters:
    """Derived Debye-scale plasma parameters."""
    debye_length_m: float        # λ_D  (m)
    plasma_frequency_hz: float   # ω_p / 2π
    electron_thermal_velocity_m_s: float

    def __post_init__(self) -> None:
        if self.debye_length_m <= 0:
            raise ValueError("Debye length must be positive")
        if self.plasma_frequency_hz <= 0:
            raise ValueError("plasma frequency must be positive")


@dataclass(frozen=True)
class WakeGeometry:
    """Physical dimensions of the debris plasma wake."""
    length_m: float          # along-track extent (recombination limited)
    width_m: float           # cross-track extent (≈ Debye length scale)
    transit_time_s: float    # time for wake to pass a fixed observer
    evidence_class: EvidenceClass
    limitation: str

    def __post_init__(self) -> None:
        if self.length_m <= 0 or self.width_m <= 0 or self.transit_time_s <= 0:
            raise ValueError("wake dimensions must be positive")
        if not self.limitation:
            raise ValueError("limitation string required")


@dataclass(frozen=True)
class WakeSignalPrediction:
    """Predicted EM perturbation amplitude and uncertainty for one fragment."""
    fragment_diameter_m: float
    orbital_velocity_m_s: float
    peak_relative_density_perturbation: float    # |δn/n|_max
    peak_perturbation_uncertainty: float         # 1-sigma fractional uncertainty
    wake_geometry: WakeGeometry
    surface_potential_v: float
    fragment_charge_c: float
    signal_bandwidth_hz: float     # ~ 1 / transit_time
    min_detectable_snr_db: float   # estimated SNR at a nominal ground receiver
    evidence_class: EvidenceClass
    model_id: str
    model_version: str
    limitation: str

    def __post_init__(self) -> None:
        if self.fragment_diameter_m <= 0:
            raise ValueError("fragment diameter must be positive")
        if not self.limitation:
            raise ValueError("limitation string required")
        if not self.model_id:
            raise ValueError("model_id required")

    @property
    def peak_perturbation_db(self) -> float:
        """Express peak δn/n in dB relative to background."""
        if self.peak_relative_density_perturbation <= 0:
            return -999.0
        return 20.0 * math.log10(self.peak_relative_density_perturbation)

    def is_detectable_above(self, noise_floor_fraction: float = 0.001) -> bool:
        """Return True if peak perturbation exceeds the given noise floor."""
        return self.peak_relative_density_perturbation > noise_floor_fraction


@dataclass(frozen=True)
class WakeModelCard:
    """Model card for the analytic wake model — required for admission."""
    model_id: str
    model_version: str
    tier: ModelTier
    governing_equations_reference: str
    validity_range_altitude_km: tuple[float, float]
    validity_range_diameter_m: tuple[float, float]
    known_limitations: tuple[str, ...]
    created_at: datetime
    model_digest: str

    def __post_init__(self) -> None:
        if not self.model_id or not self.governing_equations_reference:
            raise ValueError("model identity and governing equations reference required")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        if not self.model_digest.startswith("sha256:"):
            raise ValueError("model_digest must be sha256: prefixed")
        if not self.known_limitations:
            raise ValueError("at least one known limitation must be declared")
        lo, hi = self.validity_range_altitude_km
        if lo >= hi or lo <= 0:
            raise ValueError("invalid altitude validity range")
        lo_d, hi_d = self.validity_range_diameter_m
        if lo_d >= hi_d or lo_d <= 0:
            raise ValueError("invalid diameter validity range")


@dataclass(frozen=True)
class SizeScalingComparison:
    """Radar vs wake signal scaling comparison at a given diameter."""
    diameter_m: float
    rcs_dbsm_rayleigh: float         # radar (D⁶ scaling)
    wake_signal_db: float            # ionospheric wake (D² scaling)
    radar_advantage_db: float        # >0 means radar is stronger at this size
    heimdall_advantage_db: float     # >0 means wake is stronger (detection gap)
    is_in_detection_gap: bool        # True if below all radar thresholds


# ---------------------------------------------------------------------------
# Protocol interface — plug-and-play model adapter
# ---------------------------------------------------------------------------

class PlasmaWakeModel(Protocol):
    """Interface for any plasma wake forward model.

    Implement this to add a new model (PIC, hybrid, empirical) without
    changing any pipeline or analysis code.
    """
    model_id: str
    model_version: str
    model_card: WakeModelCard

    def predict(
        self,
        target: TargetAssumptions,
        plasma: PlasmaEnvironment,
        orbital: OrbitalState,
        surface_potential_model: SurfacePotentialModel = SurfacePotentialModel.CONSERVATIVE_ESTIMATE,
    ) -> WakeSignalPrediction:
        """Predict the wake signal for given fragment, plasma, and orbit.

        Must return a prediction with EvidenceClass.SYNTHETIC and an
        explicit limitation string.  Must not claim physical validity beyond
        the model_card validity ranges.
        """
        ...

    def debye_parameters(self, plasma: PlasmaEnvironment) -> DebyeParameters:
        """Compute Debye-scale parameters from plasma environment."""
        ...


# ---------------------------------------------------------------------------
# Analytic wake model — default implementation
# ---------------------------------------------------------------------------

class AnalyticWakeModel:
    """First-principles analytic plasma wake model for LEO.

    Implements the quasi-static Debye-scale wake approximation:
        - Charge from surface potential model (Mott-Smith & Langmuir 1926)
        - Wake length from recombination (Schunk & Nagy 2009)
        - Peak density perturbation from charge/volume argument

    Model tier: ANALYTIC_UNVALIDATED
    No laboratory or flight measurements validate this model.
    """

    model_id: str = "analytic_wake_v1"
    model_version: str = "1.0.0"

    # Surface potential estimates by illumination condition (V)
    _SURFACE_POTENTIAL: dict[SurfacePotentialModel, float] = {
        SurfacePotentialModel.SUNLIT_PHOTOELECTRIC:  +10.0,
        SurfacePotentialModel.SHADOW_PLASMA_CURRENT: -1.0,
        SurfacePotentialModel.CONSERVATIVE_ESTIMATE: -1.0,
    }

    def __init__(self) -> None:
        card_data = {
            "model_id": self.model_id,
            "model_version": self.model_version,
            "tier": ModelTier.ANALYTIC_UNVALIDATED.value,
            "governing_equations": "Debye-scale quasi-static wake; Mott-Smith 1926 probe theory; Schunk & Nagy 2009 recombination",
        }
        digest = "sha256:" + sha256(str(sorted(card_data.items())).encode()).hexdigest()
        self.model_card = WakeModelCard(
            model_id=self.model_id,
            model_version=self.model_version,
            tier=ModelTier.ANALYTIC_UNVALIDATED,
            governing_equations_reference=(
                "Debye-scale quasi-static wake approximation. "
                "Charge: Mott-Smith & Langmuir (1926) probe theory. "
                "Wake length: Schunk & Nagy (2009) recombination. "
                "Density perturbation: charge-displacement argument."
            ),
            validity_range_altitude_km=(200.0, 1000.0),
            validity_range_diameter_m=(1e-4, 1.0),
            known_limitations=(
                "Quasi-static approximation invalid for fast (>10 km/s) objects at low altitude.",
                "Spherical fragment assumed; real debris is non-spherical.",
                "Surface potential model is order-of-magnitude estimate only.",
                "No laboratory calibration; model is analytic_unvalidated tier.",
                "Recombination coefficient varies with ion composition and solar activity.",
                "Model does not account for magnetic field effects on ion wake.",
            ),
            created_at=datetime(2026, 8, 3, tzinfo=timezone.utc),
            model_digest=digest,
        )

    def debye_parameters(self, plasma: PlasmaEnvironment) -> DebyeParameters:
        """Compute Debye length and plasma frequency from plasma environment."""
        ne = plasma.electron_density_per_m3
        te = plasma.electron_temperature_k

        # Debye length: λ_D = sqrt(ε₀ k_B T_e / (n_e e²))
        debye = math.sqrt(_EPSILON_0 * _K_B * te / (ne * _E_CHARGE ** 2))

        # Plasma frequency: ω_pe = sqrt(n_e e² / (ε₀ m_e))
        m_e = 9.10938e-31   # kg
        omega_pe = math.sqrt(ne * _E_CHARGE ** 2 / (_EPSILON_0 * m_e))
        f_pe = omega_pe / (2.0 * math.pi)

        # Electron thermal velocity: v_th = sqrt(k_B T_e / m_e)
        v_th = math.sqrt(_K_B * te / m_e)

        return DebyeParameters(
            debye_length_m=debye,
            plasma_frequency_hz=f_pe,
            electron_thermal_velocity_m_s=v_th,
        )

    def predict(
        self,
        target: TargetAssumptions,
        plasma: PlasmaEnvironment,
        orbital: OrbitalState,
        surface_potential_model: SurfacePotentialModel = SurfacePotentialModel.CONSERVATIVE_ESTIMATE,
    ) -> WakeSignalPrediction:
        d = target.characteristic_length_m
        ne = plasma.electron_density_per_m3
        vx, vy, vz = orbital.velocity_m_per_s
        v = math.sqrt(vx**2 + vy**2 + vz**2)

        # Debye parameters
        dp = self.debye_parameters(plasma)

        # Surface potential and fragment charge
        v_s = self._SURFACE_POTENTIAL[surface_potential_model]
        # Q = 4π ε₀ V_s × (D/2)  — spherical capacitance model
        charge_c = 4.0 * math.pi * _EPSILON_0 * v_s * (d / 2.0)

        # Wake length — recombination limited
        # L = v / (α_eff × n_e)  where α_eff is the effective recombination rate
        wake_length_m = v / max(_ALPHA_EFF * ne, 1e-10)
        wake_length_m = min(wake_length_m, 1e5)   # cap at 100 km (physically unreasonable beyond this)

        # Wake width — Debye length scale
        wake_width_m = max(dp.debye_length_m * 5.0, d * 2.0)

        # Transit time at a fixed receiver
        transit_time_s = wake_length_m / max(v, 100.0)

        # Peak density perturbation from shielded-Coulomb potential (Yukawa):
        #   δn/n ≈ e × |V_s| × (D/2) × exp(-1) / (λ_D × k_B × T_e)
        #
        # This follows from φ(r) = Q/(4π ε₀ r) × exp(-r/λ_D) at r = λ_D,
        # with Q = 4π ε₀ V_s (D/2) and δn/n = e φ / (k_B T_e).
        # Scales as D¹ for fixed surface potential — the relevant comparison
        # with radar (D⁶ Rayleigh) gives a large detection advantage.
        te = plasma.electron_temperature_k
        numerator = _E_CHARGE * abs(v_s) * (d / 2.0) * math.exp(-1.0)
        denominator = dp.debye_length_m * _K_B * max(te, 1.0)
        delta_n_over_n = numerator / max(denominator, 1e-40)
        delta_n_over_n = min(delta_n_over_n, 1.0)   # physical cap at 100%

        # Uncertainty: model is order-of-magnitude; assign 1-sigma = 100% (factor of 2)
        uncertainty = delta_n_over_n * 1.0

        # Signal bandwidth (~ 1 / transit time)
        bandwidth_hz = 1.0 / max(transit_time_s, 1e-6)

        # Estimated SNR at ground (very rough — propagation not modelled)
        # Use 0.1% as nominal detectable threshold; SNR = 20 log10(δn/n / threshold)
        threshold = 0.001
        snr_db = 20.0 * math.log10(max(delta_n_over_n / threshold, 1e-10))

        wake_geom = WakeGeometry(
            length_m=wake_length_m,
            width_m=wake_width_m,
            transit_time_s=transit_time_s,
            evidence_class=EvidenceClass.SYNTHETIC,
            limitation=(
                "Analytic approximation only. Wake length assumes uniform recombination; "
                "actual wake may differ by 1-2 orders of magnitude depending on ion composition."
            ),
        )

        return WakeSignalPrediction(
            fragment_diameter_m=d,
            orbital_velocity_m_s=v,
            peak_relative_density_perturbation=delta_n_over_n,
            peak_perturbation_uncertainty=uncertainty,
            wake_geometry=wake_geom,
            surface_potential_v=v_s,
            fragment_charge_c=charge_c,
            signal_bandwidth_hz=bandwidth_hz,
            min_detectable_snr_db=snr_db,
            evidence_class=EvidenceClass.SYNTHETIC,
            model_id=self.model_id,
            model_version=self.model_version,
            limitation=(
                "ANALYTIC_UNVALIDATED model — analytic_unvalidated tier. "
                "Quasi-static Debye-scale approximation; spherical fragment assumed. "
                "Surface potential is order-of-magnitude estimate. "
                "No laboratory or flight calibration. "
                "Uncertainty ≈ ×2 (100% 1-sigma). "
                "Do not interpret as a physical observation."
            ),
        )

    def size_scaling_comparison(
        self,
        diameter_m: float,
        plasma: PlasmaEnvironment,
        orbital: OrbitalState,
        radar_threshold_dbsm: float = -25.0,   # Space Fence
        radar_wavelength_m: float = 0.225,      # L-band
    ) -> SizeScalingComparison:
        """Compare radar RCS vs wake signal at a given fragment diameter."""
        from .radar_detectability import compute_rcs_sphere, rcs_to_dbsm, compute_wake_relative_signal_db

        rcs_dbsm  = rcs_to_dbsm(compute_rcs_sphere(diameter_m, radar_wavelength_m))
        wake_db   = compute_wake_relative_signal_db(diameter_m, reference_diameter_m=1.0) - 60.0

        radar_advantage = rcs_dbsm - wake_db
        heimdall_advantage = wake_db - rcs_dbsm
        in_gap = rcs_dbsm < radar_threshold_dbsm

        return SizeScalingComparison(
            diameter_m=diameter_m,
            rcs_dbsm_rayleigh=rcs_dbsm,
            wake_signal_db=wake_db,
            radar_advantage_db=radar_advantage,
            heimdall_advantage_db=heimdall_advantage,
            is_in_detection_gap=in_gap,
        )
