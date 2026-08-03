"""Trajectory risk scoring and safe launch corridor identification.

Models the collision probability for a launch trajectory through the orbital
debris environment using the Poisson flux model.  Identifies altitude ×
inclination windows where the cumulative risk is below a specified threshold.

Physics:
    P_collision = 1 - exp(-F × A × T)
    where:
        F = debris flux (objects/m²/year) at the target orbit
        A = spacecraft cross-section (m²)
        T = mission duration (years)

The HEIMDALL advantage is quantified as the ratio between:
    - Risk using only the tracked (radar-visible) population
    - Risk using the full estimated population (tracked + sub-cm)

The difference is the "dark risk" — real but currently invisible.

All outputs carry EvidenceClass.SYNTHETIC with explicit limitation strings.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, Sequence

from .domain import EvidenceClass
from .debris_population import (
    DebrisPopulationSnapshot,
    DebrisPopulationBin,
    SizeRegime,
    OrbitalShell,
)


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class AscentType(str, Enum):
    DIRECT    = "direct"
    HOHMANN   = "hohmann"
    LOW_ENERGY = "low_energy"


class RiskLevel(str, Enum):
    VERY_LOW  = "very_low"   # < 1e-5
    LOW       = "low"        # 1e-5 – 1e-4
    MODERATE  = "moderate"   # 1e-4 – 1e-3
    HIGH      = "high"       # 1e-3 – 1e-2
    VERY_HIGH = "very_high"  # > 1e-2


# ---------------------------------------------------------------------------
# Domain contracts
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LaunchProfile:
    """One candidate launch trajectory specification."""
    profile_id: str
    target_altitude_km: float
    target_inclination_deg: float
    raan_deg: float
    ascent_type: AscentType
    spacecraft_cross_section_m2: float
    mission_duration_years: float

    def __post_init__(self) -> None:
        if not self.profile_id:
            raise ValueError("profile_id is required")
        if self.target_altitude_km <= 0:
            raise ValueError("target altitude must be positive")
        if not 0 <= self.target_inclination_deg <= 180:
            raise ValueError("inclination must be in [0, 180] degrees")
        if self.spacecraft_cross_section_m2 <= 0:
            raise ValueError("cross-section must be positive")
        if self.mission_duration_years <= 0:
            raise ValueError("mission duration must be positive")


@dataclass(frozen=True)
class TrajectoryRiskScore:
    """Collision probability and debris encounter statistics for one trajectory."""
    profile_id: str
    cumulative_collision_probability: float
    collision_probability_tracked_only: float
    collision_probability_full_population: float
    dark_risk_fraction: float          # fraction of total risk that is radar-invisible
    expected_encounters_per_year: float
    peak_flux_altitude_km: float
    risk_level: RiskLevel
    evidence_class: EvidenceClass
    limitation: str

    def __post_init__(self) -> None:
        if not self.profile_id or not self.limitation:
            raise ValueError("profile identity and limitation are required")
        if not 0 <= self.cumulative_collision_probability <= 1:
            raise ValueError("collision probability must be in [0, 1]")

    def to_dict(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "cumulative_collision_probability": self.cumulative_collision_probability,
            "collision_probability_tracked_only": self.collision_probability_tracked_only,
            "collision_probability_full_population": self.collision_probability_full_population,
            "dark_risk_fraction": self.dark_risk_fraction,
            "expected_encounters_per_year": self.expected_encounters_per_year,
            "peak_flux_altitude_km": self.peak_flux_altitude_km,
            "risk_level": self.risk_level.value,
            "evidence_class": self.evidence_class.value,
            "limitation": self.limitation,
        }


@dataclass(frozen=True)
class SafeLaunchCorridor:
    """An altitude × inclination band with below-threshold risk."""
    corridor_id: str
    altitude_min_km: float
    altitude_max_km: float
    inclination_min_deg: float
    inclination_max_deg: float
    max_collision_probability: float
    risk_margin_factor: float
    evidence_class: EvidenceClass
    limitation: str

    def __post_init__(self) -> None:
        if not self.corridor_id or not self.limitation:
            raise ValueError("corridor identity and limitation are required")
        if self.altitude_min_km >= self.altitude_max_km:
            raise ValueError("altitude bounds must be ordered")
        if self.max_collision_probability < 0:
            raise ValueError("collision probability must be non-negative")

    def to_dict(self) -> dict:
        return {
            "corridor_id": self.corridor_id,
            "altitude_min_km": self.altitude_min_km,
            "altitude_max_km": self.altitude_max_km,
            "inclination_min_deg": self.inclination_min_deg,
            "inclination_max_deg": self.inclination_max_deg,
            "max_collision_probability": self.max_collision_probability,
            "risk_margin_factor": self.risk_margin_factor,
            "evidence_class": self.evidence_class.value,
            "limitation": self.limitation,
        }


@dataclass(frozen=True)
class RiskFieldCell:
    """One cell of the altitude × inclination risk grid."""
    altitude_km: float
    inclination_deg: float
    flux_tracked_per_m2_per_year: float
    flux_full_per_m2_per_year: float
    dark_risk_fraction: float

    def to_dict(self) -> dict:
        return {
            "altitude_km": self.altitude_km,
            "inclination_deg": self.inclination_deg,
            "flux_tracked": self.flux_tracked_per_m2_per_year,
            "flux_full": self.flux_full_per_m2_per_year,
            "dark_risk_fraction": self.dark_risk_fraction,
            "log10_flux_full": (
                math.log10(max(self.flux_full_per_m2_per_year, 1e-20))
            ),
        }


@dataclass(frozen=True)
class TrajectoryRiskReport:
    """Full risk analysis output: field, scores, corridors, and metadata."""
    report_id: str
    generated_at: datetime
    population_snapshot_id: str
    risk_field: tuple[RiskFieldCell, ...]
    profile_scores: tuple[TrajectoryRiskScore, ...]
    safe_corridors: tuple[SafeLaunchCorridor, ...]
    risk_threshold: float
    spacecraft_cross_section_m2: float
    mission_duration_years: float
    evidence_class: EvidenceClass
    limitation: str

    def __post_init__(self) -> None:
        if not self.report_id or not self.limitation:
            raise ValueError("report identity and limitation are required")
        if self.generated_at.tzinfo is None:
            raise ValueError("generated_at must be timezone-aware")

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at.isoformat(),
            "population_snapshot_id": self.population_snapshot_id,
            "risk_threshold": self.risk_threshold,
            "spacecraft_cross_section_m2": self.spacecraft_cross_section_m2,
            "mission_duration_years": self.mission_duration_years,
            "evidence_class": self.evidence_class.value,
            "limitation": self.limitation,
            "risk_field": [c.to_dict() for c in self.risk_field],
            "profile_scores": [s.to_dict() for s in self.profile_scores],
            "safe_corridors": [c.to_dict() for c in self.safe_corridors],
        }


# ---------------------------------------------------------------------------
# Protocol interface
# ---------------------------------------------------------------------------

class RiskModel(Protocol):
    def compute_risk(
        self,
        profile: LaunchProfile,
        population: DebrisPopulationSnapshot,
    ) -> TrajectoryRiskScore:
        ...


# ---------------------------------------------------------------------------
# Risk computation helpers
# ---------------------------------------------------------------------------

def _poisson_collision_probability(
    flux_per_m2_per_year: float,
    cross_section_m2: float,
    duration_years: float,
) -> float:
    """Compute collision probability using the Poisson flux model.

    P = 1 - exp(-F × A × T)
    """
    exponent = flux_per_m2_per_year * cross_section_m2 * duration_years
    return 1.0 - math.exp(-exponent)


def _classify_risk(probability: float) -> RiskLevel:
    if probability < 1e-5:
        return RiskLevel.VERY_LOW
    if probability < 1e-4:
        return RiskLevel.LOW
    if probability < 1e-3:
        return RiskLevel.MODERATE
    if probability < 1e-2:
        return RiskLevel.HIGH
    return RiskLevel.VERY_HIGH


def _find_flux_for_shell(
    bins: Sequence[DebrisPopulationBin],
    altitude_km: float,
    inclination_deg: float,
    tracked_only: bool,
) -> float:
    """Sum flux contributions from matching population bins."""
    total_flux = 0.0
    target_regimes = (
        {SizeRegime.TRACKED}
        if tracked_only
        else {SizeRegime.TRACKED, SizeRegime.NEAR_DETECTABLE, SizeRegime.SUB_CM}
    )
    for b in bins:
        if (
            b.shell.altitude_km_min <= altitude_km < b.shell.altitude_km_max
            and b.shell.inclination_deg_min <= inclination_deg < b.shell.inclination_deg_max
            and b.size_regime in target_regimes
        ):
            total_flux += b.flux_per_m2_per_year
    return total_flux


# ---------------------------------------------------------------------------
# Trajectory risk engine
# ---------------------------------------------------------------------------

class TrajectoryRiskEngine:
    """Computes the full trajectory risk report for a debris population snapshot."""

    _RISK_THRESHOLD_DEFAULT = 1e-4  # 0.01% collision probability over mission life

    def build_risk_report(
        self,
        population: DebrisPopulationSnapshot,
        profiles: Sequence[LaunchProfile],
        spacecraft_cross_section_m2: float = 10.0,
        mission_duration_years: float = 5.0,
        risk_threshold: float = _RISK_THRESHOLD_DEFAULT,
        generated_at: datetime | None = None,
    ) -> TrajectoryRiskReport:
        if generated_at is None:
            generated_at = datetime.now(timezone.utc)

        # Build risk field: altitude × inclination grid
        risk_field = self._build_risk_field(population)

        # Score each provided launch profile
        scores = tuple(
            self._score_profile(
                profile, population, spacecraft_cross_section_m2, mission_duration_years
            )
            for profile in profiles
        )

        # Identify safe corridors
        corridors = self._find_safe_corridors(
            population,
            spacecraft_cross_section_m2,
            mission_duration_years,
            risk_threshold,
        )

        report_id = "risk-" + sha256(
            f"{generated_at.isoformat()}{population.snapshot_id}".encode()
        ).hexdigest()[:10]

        return TrajectoryRiskReport(
            report_id=report_id,
            generated_at=generated_at,
            population_snapshot_id=population.snapshot_id,
            risk_field=tuple(risk_field),
            profile_scores=scores,
            safe_corridors=corridors,
            risk_threshold=risk_threshold,
            spacecraft_cross_section_m2=spacecraft_cross_section_m2,
            mission_duration_years=mission_duration_years,
            evidence_class=EvidenceClass.SYNTHETIC,
            limitation=(
                "Model-based flux computation using synthetic power-law population. "
                "Actual collision probability requires validated flux data from real "
                "observations. Results are for comparative analysis only. Safe "
                "corridors are not operationally certified launch windows."
            ),
        )

    def _build_risk_field(
        self,
        population: DebrisPopulationSnapshot,
    ) -> list[RiskFieldCell]:
        cells: list[RiskFieldCell] = []
        seen: set[tuple[float, float]] = set()

        for b in population.shells:
            alt = b.shell.altitude_km_centre
            inc = (b.shell.inclination_deg_min + b.shell.inclination_deg_max) / 2.0
            key = (round(alt, 1), round(inc, 1))
            if key in seen:
                continue
            seen.add(key)

            flux_tracked = _find_flux_for_shell(population.shells, alt, inc, tracked_only=True)
            flux_full = _find_flux_for_shell(population.shells, alt, inc, tracked_only=False)
            dark_frac = (
                (flux_full - flux_tracked) / max(flux_full, 1e-30)
                if flux_full > 0 else 0.0
            )
            cells.append(RiskFieldCell(
                altitude_km=alt,
                inclination_deg=inc,
                flux_tracked_per_m2_per_year=flux_tracked,
                flux_full_per_m2_per_year=flux_full,
                dark_risk_fraction=min(max(dark_frac, 0.0), 1.0),
            ))

        return cells

    def _score_profile(
        self,
        profile: LaunchProfile,
        population: DebrisPopulationSnapshot,
        cross_section_m2: float,
        duration_years: float,
    ) -> TrajectoryRiskScore:
        flux_tracked = _find_flux_for_shell(
            population.shells,
            profile.target_altitude_km,
            profile.target_inclination_deg,
            tracked_only=True,
        )
        flux_full = _find_flux_for_shell(
            population.shells,
            profile.target_altitude_km,
            profile.target_inclination_deg,
            tracked_only=False,
        )

        p_tracked = _poisson_collision_probability(flux_tracked, cross_section_m2, duration_years)
        p_full = _poisson_collision_probability(flux_full, cross_section_m2, duration_years)
        dark_frac = (p_full - p_tracked) / max(p_full, 1e-30) if p_full > 0 else 0.0

        # Find altitude of peak flux along ascent
        peak_alt = profile.target_altitude_km  # simplified: target altitude
        peak_flux = flux_full
        for b in population.shells:
            if (
                b.shell.inclination_deg_min <= profile.target_inclination_deg < b.shell.inclination_deg_max
                and b.flux_per_m2_per_year > peak_flux
            ):
                peak_flux = b.flux_per_m2_per_year
                peak_alt = b.shell.altitude_km_centre

        return TrajectoryRiskScore(
            profile_id=profile.profile_id,
            cumulative_collision_probability=p_full,
            collision_probability_tracked_only=p_tracked,
            collision_probability_full_population=p_full,
            dark_risk_fraction=min(max(dark_frac, 0.0), 1.0),
            expected_encounters_per_year=flux_full * cross_section_m2,
            peak_flux_altitude_km=peak_alt,
            risk_level=_classify_risk(p_full),
            evidence_class=EvidenceClass.SYNTHETIC,
            limitation=(
                "Poisson flux model using synthetic population estimate. "
                "Risk is indicative and not operationally validated."
            ),
        )

    def _find_safe_corridors(
        self,
        population: DebrisPopulationSnapshot,
        cross_section_m2: float,
        duration_years: float,
        threshold: float,
    ) -> tuple[SafeLaunchCorridor, ...]:
        corridors: list[SafeLaunchCorridor] = []
        corridor_idx = 0

        # Sample altitude × inclination grid at coarse resolution
        altitudes = [225, 300, 350, 400, 450, 500, 600, 700, 750, 800, 900, 1000, 1200, 1400]
        inclinations = [28, 45, 51, 53, 63, 72, 82, 90, 98]

        for alt in altitudes:
            for inc in inclinations:
                flux_full = _find_flux_for_shell(population.shells, float(alt), float(inc), False)
                p = _poisson_collision_probability(flux_full, cross_section_m2, duration_years)
                if p < threshold:
                    margin = threshold / max(p, 1e-30)
                    cid = f"corridor-{corridor_idx:03d}"
                    corridors.append(SafeLaunchCorridor(
                        corridor_id=cid,
                        altitude_min_km=float(alt - 25),
                        altitude_max_km=float(alt + 25),
                        inclination_min_deg=max(0.0, float(inc - 5)),
                        inclination_max_deg=min(180.0, float(inc + 5)),
                        max_collision_probability=p,
                        risk_margin_factor=min(margin, 1000.0),
                        evidence_class=EvidenceClass.SYNTHETIC,
                        limitation=(
                            "Model-derived safe corridor — not an operationally "
                            "certified launch window. Based on synthetic population "
                            "flux model only."
                        ),
                    ))
                    corridor_idx += 1

        return tuple(corridors)


# ---------------------------------------------------------------------------
# Standard reference launch profiles
# ---------------------------------------------------------------------------

REFERENCE_LAUNCH_PROFILES: tuple[LaunchProfile, ...] = (
    LaunchProfile(
        profile_id="iss-resupply-400km",
        target_altitude_km=400.0,
        target_inclination_deg=51.6,
        raan_deg=0.0,
        ascent_type=AscentType.DIRECT,
        spacecraft_cross_section_m2=10.0,
        mission_duration_years=0.5,
    ),
    LaunchProfile(
        profile_id="sun-sync-600km",
        target_altitude_km=600.0,
        target_inclination_deg=97.8,
        raan_deg=0.0,
        ascent_type=AscentType.DIRECT,
        spacecraft_cross_section_m2=5.0,
        mission_duration_years=3.0,
    ),
    LaunchProfile(
        profile_id="leo-megaconstellation-550km",
        target_altitude_km=550.0,
        target_inclination_deg=53.0,
        raan_deg=0.0,
        ascent_type=AscentType.DIRECT,
        spacecraft_cross_section_m2=3.0,
        mission_duration_years=5.0,
    ),
    LaunchProfile(
        profile_id="polar-science-800km",
        target_altitude_km=800.0,
        target_inclination_deg=98.6,
        raan_deg=0.0,
        ascent_type=AscentType.DIRECT,
        spacecraft_cross_section_m2=8.0,
        mission_duration_years=2.0,
    ),
    LaunchProfile(
        profile_id="debris-belt-crossing-750km",
        target_altitude_km=750.0,
        target_inclination_deg=86.4,
        raan_deg=169.0,
        ascent_type=AscentType.DIRECT,
        spacecraft_cross_section_m2=10.0,
        mission_duration_years=1.0,
    ),
)
