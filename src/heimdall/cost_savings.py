"""Mission cost savings quantification from HEIMDALL debris data.

Estimates the economic value of HEIMDALL's sub-centimetre debris awareness
across NASA and commercial launch fleets.  Cost savings arise from:

  1. Fewer false-alarm collision-avoidance manoeuvres (radar-only generates
     many unnecessary manoeuvres; HEIMDALL density maps improve precision)
  2. Reduced in-orbit insurance premiums (better risk quantification)
  3. Reduced launch delays (tighter window computation from density maps)
  4. Preserved spacecraft propellant (avoided manoeuvres extend mission life)

All dollar estimates are modelled using publicly available cost data
(NASA Cost Estimating Handbook, ESA SSA reports, insurance industry
publications).  Uncertainty bounds span ×0.5 to ×3.0 of central estimate
— conservative and explicitly stated.

All outputs carry EvidenceClass.SYNTHETIC.  Actual savings depend on
real operational performance not yet demonstrated.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Sequence

from .domain import EvidenceClass


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class MissionClass(str, Enum):
    ISS_RESUPPLY       = "iss_resupply"
    CREWED_LEO         = "crewed_leo"
    NASA_SCIENCE_LEO   = "nasa_science_leo"
    NASA_SCIENCE_SSO   = "nasa_science_sso"
    COMMERCIAL_LEO     = "commercial_leo"       # e.g., Starlink-class
    COMMERCIAL_GEO     = "commercial_geo"
    CUBESAT            = "cubesat"


# ---------------------------------------------------------------------------
# Domain contracts
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MissionCostProfile:
    """Public-domain cost parameters for one mission class.

    Sources: NASA Cost Estimating Handbook 2015; SpaceX/ULA public filings;
    Insurance industry reports (Marsh, AON, Munich Re); ESA SSA annual reports.
    """
    mission_class: MissionClass
    spacecraft_value_usd: float
    annual_operations_cost_usd: float
    insurance_premium_fraction: float
    delay_cost_per_day_usd: float
    maneuver_cost_usd: float
    annual_maneuvers_current: float
    false_alarm_rate_current: float
    source_reference: str

    def __post_init__(self) -> None:
        if self.spacecraft_value_usd <= 0 or self.annual_operations_cost_usd <= 0:
            raise ValueError("cost values must be positive")
        if not 0 < self.insurance_premium_fraction < 1:
            raise ValueError("insurance premium fraction must be in (0, 1)")
        if not 0 <= self.false_alarm_rate_current <= 1:
            raise ValueError("false alarm rate must be in [0, 1]")

    @property
    def annual_insurance_cost_usd(self) -> float:
        return self.spacecraft_value_usd * self.insurance_premium_fraction

    @property
    def annual_maneuver_cost_usd(self) -> float:
        return self.annual_maneuvers_current * self.maneuver_cost_usd


@dataclass(frozen=True)
class CostSavingsEstimate:
    """Quantified savings from HEIMDALL data for one mission class over N years."""
    estimate_id: str
    mission_class: MissionClass
    analysis_period_years: int
    # Savings components
    avoided_maneuvers_usd: float
    reduced_insurance_usd: float
    launch_delay_reduction_usd: float
    propellant_preserved_usd: float
    total_savings_usd: float
    # Uncertainty
    uncertainty_low_usd: float
    uncertainty_high_usd: float
    # Assumptions
    maneuver_reduction_fraction: float
    insurance_reduction_fraction: float
    delay_days_saved_per_launch: float
    assumptions: tuple[str, ...]
    evidence_class: EvidenceClass
    limitation: str

    def __post_init__(self) -> None:
        if not self.estimate_id or not self.limitation:
            raise ValueError("estimate identity and limitation are required")
        if self.analysis_period_years <= 0:
            raise ValueError("analysis period must be positive")

    def to_dict(self) -> dict:
        return {
            "estimate_id": self.estimate_id,
            "mission_class": self.mission_class.value,
            "analysis_period_years": self.analysis_period_years,
            "avoided_maneuvers_usd": self.avoided_maneuvers_usd,
            "reduced_insurance_usd": self.reduced_insurance_usd,
            "launch_delay_reduction_usd": self.launch_delay_reduction_usd,
            "propellant_preserved_usd": self.propellant_preserved_usd,
            "total_savings_usd": self.total_savings_usd,
            "uncertainty_low_usd": self.uncertainty_low_usd,
            "uncertainty_high_usd": self.uncertainty_high_usd,
            "maneuver_reduction_fraction": self.maneuver_reduction_fraction,
            "insurance_reduction_fraction": self.insurance_reduction_fraction,
            "delay_days_saved_per_launch": self.delay_days_saved_per_launch,
            "assumptions": list(self.assumptions),
            "evidence_class": self.evidence_class.value,
            "limitation": self.limitation,
        }


@dataclass(frozen=True)
class FleetwideSavingsScenario:
    """Aggregate savings across a mission fleet over 10 years."""
    scenario_id: str
    generated_at: datetime
    fleet: tuple[tuple[MissionClass, int], ...]   # (class, annual count)
    per_mission_estimates: tuple[CostSavingsEstimate, ...]
    annual_savings_usd: float
    ten_year_savings_usd: float
    uncertainty_low_usd: float
    uncertainty_high_usd: float
    evidence_class: EvidenceClass
    limitation: str

    def __post_init__(self) -> None:
        if not self.scenario_id or not self.limitation:
            raise ValueError("scenario identity and limitation are required")
        if self.generated_at.tzinfo is None:
            raise ValueError("generated_at must be timezone-aware")

    def to_dict(self) -> dict:
        return {
            "scenario_id": self.scenario_id,
            "generated_at": self.generated_at.isoformat(),
            "fleet": [
                {"mission_class": mc.value, "annual_count": cnt}
                for mc, cnt in self.fleet
            ],
            "annual_savings_usd": self.annual_savings_usd,
            "ten_year_savings_usd": self.ten_year_savings_usd,
            "uncertainty_low_usd": self.uncertainty_low_usd,
            "uncertainty_high_usd": self.uncertainty_high_usd,
            "evidence_class": self.evidence_class.value,
            "limitation": self.limitation,
            "per_mission_estimates": [e.to_dict() for e in self.per_mission_estimates],
        }


# ---------------------------------------------------------------------------
# Reference mission cost profiles — from public-domain sources
# ---------------------------------------------------------------------------

REFERENCE_MISSION_COST_PROFILES: dict[MissionClass, MissionCostProfile] = {
    MissionClass.ISS_RESUPPLY: MissionCostProfile(
        mission_class=MissionClass.ISS_RESUPPLY,
        spacecraft_value_usd=300_000_000,
        annual_operations_cost_usd=150_000_000,
        insurance_premium_fraction=0.005,
        delay_cost_per_day_usd=2_000_000,
        maneuver_cost_usd=1_000_000,
        annual_maneuvers_current=3.0,
        false_alarm_rate_current=0.97,
        source_reference=(
            "NASA OIG Report IG-21-001; ISS SSA maneuver statistics 2015-2024; "
            "NASA Cost Estimating Handbook 2015"
        ),
    ),
    MissionClass.CREWED_LEO: MissionCostProfile(
        mission_class=MissionClass.CREWED_LEO,
        spacecraft_value_usd=1_000_000_000,
        annual_operations_cost_usd=400_000_000,
        insurance_premium_fraction=0.008,
        delay_cost_per_day_usd=5_000_000,
        maneuver_cost_usd=2_000_000,
        annual_maneuvers_current=4.0,
        false_alarm_rate_current=0.97,
        source_reference=(
            "NASA Crew Dragon/Orion cost references, public domain; "
            "NASA Cost Estimating Handbook 2015"
        ),
    ),
    MissionClass.NASA_SCIENCE_LEO: MissionCostProfile(
        mission_class=MissionClass.NASA_SCIENCE_LEO,
        spacecraft_value_usd=150_000_000,
        annual_operations_cost_usd=30_000_000,
        insurance_premium_fraction=0.01,
        delay_cost_per_day_usd=500_000,
        maneuver_cost_usd=500_000,
        annual_maneuvers_current=2.0,
        false_alarm_rate_current=0.95,
        source_reference=(
            "NASA Science Mission Directorate cost references; "
            "Iridium NEXT insurance cost analogues"
        ),
    ),
    MissionClass.NASA_SCIENCE_SSO: MissionCostProfile(
        mission_class=MissionClass.NASA_SCIENCE_SSO,
        spacecraft_value_usd=200_000_000,
        annual_operations_cost_usd=40_000_000,
        insurance_premium_fraction=0.012,
        delay_cost_per_day_usd=700_000,
        maneuver_cost_usd=600_000,
        annual_maneuvers_current=2.5,
        false_alarm_rate_current=0.95,
        source_reference=(
            "NASA Cost Estimating Handbook 2015; "
            "ESA SSA annual report 2024"
        ),
    ),
    MissionClass.COMMERCIAL_LEO: MissionCostProfile(
        mission_class=MissionClass.COMMERCIAL_LEO,
        spacecraft_value_usd=1_000_000,
        annual_operations_cost_usd=500_000,
        insurance_premium_fraction=0.02,
        delay_cost_per_day_usd=100_000,
        maneuver_cost_usd=50_000,
        annual_maneuvers_current=1.5,
        false_alarm_rate_current=0.90,
        source_reference=(
            "Satellite insurance market reports (Marsh 2024); "
            "SpaceX Starlink operations public references"
        ),
    ),
    MissionClass.COMMERCIAL_GEO: MissionCostProfile(
        mission_class=MissionClass.COMMERCIAL_GEO,
        spacecraft_value_usd=300_000_000,
        annual_operations_cost_usd=15_000_000,
        insurance_premium_fraction=0.015,
        delay_cost_per_day_usd=1_500_000,
        maneuver_cost_usd=800_000,
        annual_maneuvers_current=2.0,
        false_alarm_rate_current=0.95,
        source_reference=(
            "Intelsat/SES insurance cost references, public; "
            "AON space insurance market report 2024"
        ),
    ),
    MissionClass.CUBESAT: MissionCostProfile(
        mission_class=MissionClass.CUBESAT,
        spacecraft_value_usd=500_000,
        annual_operations_cost_usd=100_000,
        insurance_premium_fraction=0.025,
        delay_cost_per_day_usd=20_000,
        maneuver_cost_usd=0,  # typically no propulsion
        annual_maneuvers_current=0.0,
        false_alarm_rate_current=0.0,
        source_reference=(
            "NASA CubeSat Launch Initiative cost references; "
            "University CubeSat program cost surveys"
        ),
    ),
}


# ---------------------------------------------------------------------------
# Cost savings calculator
# ---------------------------------------------------------------------------

class CostSavingsCalculator:
    """Computes HEIMDALL cost savings across mission classes and fleet scenarios."""

    # Conservative HEIMDALL improvement assumptions
    MANEUVER_REDUCTION_FRACTION: float = 0.20   # 20% fewer false alarms
    INSURANCE_REDUCTION_FRACTION: float = 0.05  # 5% premium reduction
    DELAY_DAYS_SAVED_PER_LAUNCH: float = 0.5    # 0.5 day average delay reduction
    PROPELLANT_VALUE_FRACTION: float = 0.02     # 2% of spacecraft value

    # Uncertainty multipliers
    UNCERTAINTY_LOW_MULT: float = 0.5
    UNCERTAINTY_HIGH_MULT: float = 3.0

    def estimate_mission_savings(
        self,
        profile: MissionCostProfile,
        analysis_period_years: int = 10,
    ) -> CostSavingsEstimate:
        # Avoided false-alarm manoeuvres
        false_alarms_per_year = (
            profile.annual_maneuvers_current * profile.false_alarm_rate_current
        )
        avoided_maneuvers_per_year = false_alarms_per_year * self.MANEUVER_REDUCTION_FRACTION
        avoided_maneuvers_usd = (
            avoided_maneuvers_per_year * profile.maneuver_cost_usd * analysis_period_years
        )

        # Reduced insurance premiums
        reduced_insurance_usd = (
            profile.annual_insurance_cost_usd
            * self.INSURANCE_REDUCTION_FRACTION
            * analysis_period_years
        )

        # Launch delay reduction
        launch_delay_usd = (
            self.DELAY_DAYS_SAVED_PER_LAUNCH
            * profile.delay_cost_per_day_usd
            * analysis_period_years
        )

        # Propellant preservation (avoided manoeuvres → fuel saved)
        propellant_usd = (
            avoided_maneuvers_per_year
            * profile.spacecraft_value_usd
            * self.PROPELLANT_VALUE_FRACTION
            * analysis_period_years
        )

        total = (
            avoided_maneuvers_usd
            + reduced_insurance_usd
            + launch_delay_usd
            + propellant_usd
        )

        estimate_id = f"savings-{profile.mission_class.value}-{analysis_period_years}yr"

        return CostSavingsEstimate(
            estimate_id=estimate_id,
            mission_class=profile.mission_class,
            analysis_period_years=analysis_period_years,
            avoided_maneuvers_usd=avoided_maneuvers_usd,
            reduced_insurance_usd=reduced_insurance_usd,
            launch_delay_reduction_usd=launch_delay_usd,
            propellant_preserved_usd=propellant_usd,
            total_savings_usd=total,
            uncertainty_low_usd=total * self.UNCERTAINTY_LOW_MULT,
            uncertainty_high_usd=total * self.UNCERTAINTY_HIGH_MULT,
            maneuver_reduction_fraction=self.MANEUVER_REDUCTION_FRACTION,
            insurance_reduction_fraction=self.INSURANCE_REDUCTION_FRACTION,
            delay_days_saved_per_launch=self.DELAY_DAYS_SAVED_PER_LAUNCH,
            assumptions=(
                f"Maneuver false-alarm rate: {profile.false_alarm_rate_current:.0%}",
                f"Reduction from HEIMDALL density maps: {self.MANEUVER_REDUCTION_FRACTION:.0%}",
                f"Insurance premium reduction: {self.INSURANCE_REDUCTION_FRACTION:.0%}",
                f"Launch delay reduction: {self.DELAY_DAYS_SAVED_PER_LAUNCH:.1f} days/launch",
                f"Propellant value: {self.PROPELLANT_VALUE_FRACTION:.0%} of spacecraft value per avoided maneuver",
                f"Cost sources: {profile.source_reference}",
            ),
            evidence_class=EvidenceClass.SYNTHETIC,
            limitation=(
                "Modelled estimates based on publicly available cost data and assumed "
                "improvement fractions.  Actual savings depend on HEIMDALL detection "
                "performance not yet demonstrated.  Uncertainty range is ×0.5 to ×3.0 "
                "of central estimate.  No actual cost savings have been realised."
            ),
        )

    def build_fleetwide_scenario(
        self,
        fleet: Sequence[tuple[MissionClass, int]],
        analysis_period_years: int = 10,
        generated_at: datetime | None = None,
    ) -> FleetwideSavingsScenario:
        if generated_at is None:
            generated_at = datetime.now(timezone.utc)

        estimates: list[CostSavingsEstimate] = []
        annual_total = 0.0

        for mission_class, annual_count in fleet:
            profile = REFERENCE_MISSION_COST_PROFILES.get(mission_class)
            if profile is None:
                continue
            est = self.estimate_mission_savings(profile, analysis_period_years)
            # Scale by annual launch count
            annual_savings = est.total_savings_usd / analysis_period_years * annual_count
            annual_total += annual_savings
            estimates.append(est)

        ten_year_total = annual_total * analysis_period_years
        scenario_id = "fleet-" + sha256(
            f"{generated_at.isoformat()}{analysis_period_years}".encode()
        ).hexdigest()[:10]

        return FleetwideSavingsScenario(
            scenario_id=scenario_id,
            generated_at=generated_at,
            fleet=tuple(fleet),
            per_mission_estimates=tuple(estimates),
            annual_savings_usd=annual_total,
            ten_year_savings_usd=ten_year_total,
            uncertainty_low_usd=ten_year_total * self.UNCERTAINTY_LOW_MULT,
            uncertainty_high_usd=ten_year_total * self.UNCERTAINTY_HIGH_MULT,
            evidence_class=EvidenceClass.SYNTHETIC,
            limitation=(
                "Fleet-wide synthetic estimate.  Individual mission counts are "
                "illustrative.  All savings are modelled, not observed.  Treat "
                "as order-of-magnitude planning reference only."
            ),
        )


# ---------------------------------------------------------------------------
# Reference fleet scenarios
# ---------------------------------------------------------------------------

NASA_COMMERCIAL_FLEET: tuple[tuple[MissionClass, int], ...] = (
    (MissionClass.CREWED_LEO,       4),
    (MissionClass.ISS_RESUPPLY,     4),
    (MissionClass.NASA_SCIENCE_LEO, 6),
    (MissionClass.NASA_SCIENCE_SSO, 4),
    (MissionClass.COMMERCIAL_LEO,  30),
    (MissionClass.COMMERCIAL_GEO,  10),
)
