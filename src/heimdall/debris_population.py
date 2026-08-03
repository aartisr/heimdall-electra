"""Orbital debris population model for visualization and risk analysis.

Builds a scientifically grounded synthetic population of orbital debris
stratified by size regime and orbital parameters.  Uses a power-law
cumulative-size-distribution extrapolation (N(>D) ∝ D^-α) consistent with
published NASA ORDEM 3.0 and ESA MASTER 2009 methodology to estimate the
untracked sub-centimetre population.

All outputs carry EvidenceClass.SYNTHETIC with explicit limitation strings.
No claim of actual debris detection or physical observation is made.

Plug-and-play design: every computation stage is implemented behind a
Protocol interface so the default synthetic model can be replaced with a
tabulated MASTER or ORDEM adapter without changing the pipeline.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, Sequence

from .domain import EvidenceClass


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class SizeRegime(str, Enum):
    """Debris size classification aligned with radar detection capability."""
    TRACKED        = "tracked"          # > 10 cm  — in USSPACECOM catalog
    NEAR_DETECTABLE = "near_detectable"  # 1–10 cm  — marginal radar visibility
    SUB_CM         = "sub_cm"           # 1 mm–1 cm — radar-dark, HEIMDALL-detectable
    SUB_MM         = "sub_mm"           # < 1 mm   — flux / surface-degradation regime


class PopulationSource(str, Enum):
    USSPACECOM_TLE    = "usspacecom_tle"
    MASTER_MODEL      = "master_model"
    ORDEM_MODEL       = "ordem_model"
    SYNTHETIC_ESTIMATE = "synthetic_estimate"


# ---------------------------------------------------------------------------
# Core domain contracts (frozen dataclasses)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OrbitalShell:
    """One discretised (altitude × inclination) bin."""
    altitude_km_min: float
    altitude_km_max: float
    inclination_deg_min: float
    inclination_deg_max: float

    def __post_init__(self) -> None:
        if self.altitude_km_min < 0 or self.altitude_km_min >= self.altitude_km_max:
            raise ValueError("altitude bin bounds are invalid")
        if not (0 <= self.inclination_deg_min < self.inclination_deg_max <= 180):
            raise ValueError("inclination bin bounds are invalid")

    @property
    def altitude_km_centre(self) -> float:
        return (self.altitude_km_min + self.altitude_km_max) / 2.0

    @property
    def volume_km3(self) -> float:
        """Approximate shell volume for density normalisation."""
        earth_radius_km = 6371.0
        r_min = earth_radius_km + self.altitude_km_min
        r_max = earth_radius_km + self.altitude_km_max
        inc_fraction = (
            (self.inclination_deg_max - self.inclination_deg_min) / 180.0
        )
        return (4.0 / 3.0) * math.pi * (r_max ** 3 - r_min ** 3) * inc_fraction


@dataclass(frozen=True)
class DebrisPopulationBin:
    """Debris count and flux statistics for one orbital shell × size regime."""
    shell: OrbitalShell
    size_regime: SizeRegime
    object_count: int
    spatial_density_per_km3: float
    flux_per_m2_per_year: float
    population_source: PopulationSource
    uncertainty_fraction: float
    evidence_class: EvidenceClass

    def __post_init__(self) -> None:
        if self.object_count < 0:
            raise ValueError("object count must be non-negative")
        if self.spatial_density_per_km3 < 0 or self.flux_per_m2_per_year < 0:
            raise ValueError("density and flux must be non-negative")
        if not 0 <= self.uncertainty_fraction <= 1:
            raise ValueError("uncertainty fraction must be in [0, 1]")


@dataclass(frozen=True)
class FragmentationEvent:
    """A known orbital fragmentation event and its estimated debris cloud."""
    event_id: str
    name: str
    year: int
    orbital_altitude_km: float
    orbital_inclination_deg: float
    raan_deg: float
    catalogued_fragment_count: int
    estimated_sub_cm_count: int
    estimation_method: str
    source_reference: str

    def __post_init__(self) -> None:
        if not self.event_id or not self.name or not self.source_reference:
            raise ValueError("event identity and source reference are required")
        if self.orbital_altitude_km <= 0 or self.catalogued_fragment_count < 0:
            raise ValueError("event altitude and fragment count must be non-negative")
        if not 0 <= self.orbital_inclination_deg <= 180:
            raise ValueError("inclination must be in [0, 180] degrees")
        if self.estimated_sub_cm_count < 0:
            raise ValueError("estimated sub-cm count must be non-negative")


@dataclass(frozen=True)
class DebrisCloud:
    """Spatial extent and density envelope of one fragmentation event cloud."""
    cloud_id: str
    event_id: str
    centroid_altitude_km: float
    centroid_inclination_deg: float
    centroid_raan_deg: float
    spread_altitude_km: float
    spread_inclination_deg: float
    peak_number_density_per_km3: float
    total_mass_estimate_kg: float
    size_regime: SizeRegime
    evidence_class: EvidenceClass
    limitation: str

    def __post_init__(self) -> None:
        if not self.cloud_id or not self.event_id:
            raise ValueError("cloud and event identity are required")
        if self.centroid_altitude_km <= 0 or self.spread_altitude_km <= 0:
            raise ValueError("altitude centroid and spread must be positive")
        if self.peak_number_density_per_km3 < 0:
            raise ValueError("number density must be non-negative")
        if not self.limitation:
            raise ValueError("limitation string is required for all evidence")

    def density_at(self, altitude_km: float, inclination_deg: float) -> float:
        """Gaussian density falloff from cloud centroid."""
        dalt = (altitude_km - self.centroid_altitude_km) / max(self.spread_altitude_km, 1e-9)
        dinc = (inclination_deg - self.centroid_inclination_deg) / max(self.spread_inclination_deg, 1e-9)
        return self.peak_number_density_per_km3 * math.exp(-0.5 * (dalt**2 + dinc**2))


@dataclass(frozen=True)
class DebrisPopulationSnapshot:
    """Complete model snapshot exported to the visualization pipeline."""
    snapshot_id: str
    generated_at: datetime
    model_version: str
    model_id: str
    source_reference: str
    shells: tuple[DebrisPopulationBin, ...]
    clouds: tuple[DebrisCloud, ...]
    events: tuple[FragmentationEvent, ...]
    total_tracked_objects: int
    estimated_sub_cm_total: int
    altitude_range_km: tuple[float, float]
    evidence_class: EvidenceClass
    limitation: str

    def __post_init__(self) -> None:
        if not self.snapshot_id or not self.model_id or not self.limitation:
            raise ValueError("snapshot identity and limitation are required")
        if self.generated_at.tzinfo is None:
            raise ValueError("generated_at must be timezone-aware")
        if self.total_tracked_objects < 0 or self.estimated_sub_cm_total < 0:
            raise ValueError("object counts must be non-negative")

    def to_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "generated_at": self.generated_at.isoformat(),
            "model_version": self.model_version,
            "model_id": self.model_id,
            "source_reference": self.source_reference,
            "total_tracked_objects": self.total_tracked_objects,
            "estimated_sub_cm_total": self.estimated_sub_cm_total,
            "altitude_range_km": list(self.altitude_range_km),
            "evidence_class": self.evidence_class.value,
            "limitation": self.limitation,
            "events": [
                {
                    "event_id": e.event_id,
                    "name": e.name,
                    "year": e.year,
                    "orbital_altitude_km": e.orbital_altitude_km,
                    "orbital_inclination_deg": e.orbital_inclination_deg,
                    "raan_deg": e.raan_deg,
                    "catalogued_fragment_count": e.catalogued_fragment_count,
                    "estimated_sub_cm_count": e.estimated_sub_cm_count,
                    "source_reference": e.source_reference,
                }
                for e in self.events
            ],
            "clouds": [
                {
                    "cloud_id": c.cloud_id,
                    "event_id": c.event_id,
                    "centroid_altitude_km": c.centroid_altitude_km,
                    "centroid_inclination_deg": c.centroid_inclination_deg,
                    "centroid_raan_deg": c.centroid_raan_deg,
                    "spread_altitude_km": c.spread_altitude_km,
                    "spread_inclination_deg": c.spread_inclination_deg,
                    "peak_number_density_per_km3": c.peak_number_density_per_km3,
                    "total_mass_estimate_kg": c.total_mass_estimate_kg,
                    "size_regime": c.size_regime.value,
                    "evidence_class": c.evidence_class.value,
                    "limitation": c.limitation,
                }
                for c in self.clouds
            ],
            "shells": [
                {
                    "altitude_km_min": b.shell.altitude_km_min,
                    "altitude_km_max": b.shell.altitude_km_max,
                    "inclination_deg_min": b.shell.inclination_deg_min,
                    "inclination_deg_max": b.shell.inclination_deg_max,
                    "size_regime": b.size_regime.value,
                    "object_count": b.object_count,
                    "spatial_density_per_km3": b.spatial_density_per_km3,
                    "flux_per_m2_per_year": b.flux_per_m2_per_year,
                    "population_source": b.population_source.value,
                    "uncertainty_fraction": b.uncertainty_fraction,
                    "evidence_class": b.evidence_class.value,
                }
                for b in self.shells
            ],
        }


# ---------------------------------------------------------------------------
# Protocol interfaces (plug-and-play adapters)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PopulationModelConfig:
    altitude_bin_km: float = 50.0
    inclination_bin_deg: float = 10.0
    altitude_min_km: float = 200.0
    altitude_max_km: float = 2000.0
    size_power_law_index: float = 2.5
    sub_cm_uncertainty_fraction: float = 0.5


class PopulationModel(Protocol):
    model_id: str
    model_version: str

    def build_snapshot(
        self,
        config: PopulationModelConfig,
        generated_at: datetime,
    ) -> DebrisPopulationSnapshot:
        ...


# ---------------------------------------------------------------------------
# Built-in fragmentation event catalog
# Sources: NASA Orbital Debris Program Office quarterly news, ESA Annual
# Space Environment Report 2024, publicly available orbital parameters.
# ---------------------------------------------------------------------------

FRAGMENTATION_EVENT_CATALOG: tuple[FragmentationEvent, ...] = (
    FragmentationEvent(
        event_id="fengyun-1c-2007",
        name="Fengyun-1C ASAT test",
        year=2007,
        orbital_altitude_km=865.0,
        orbital_inclination_deg=98.6,
        raan_deg=247.0,
        catalogued_fragment_count=3538,
        estimated_sub_cm_count=150_000,
        estimation_method="power_law_extrapolation_from_NASA_ODPO",
        source_reference="NASA Orbital Debris Quarterly News, Vol 11 No 2, 2007",
    ),
    FragmentationEvent(
        event_id="cosmos-2251-iridium-2009",
        name="Cosmos-2251 / Iridium-33 collision",
        year=2009,
        orbital_altitude_km=789.0,
        orbital_inclination_deg=86.4,
        raan_deg=169.0,
        catalogued_fragment_count=1800,
        estimated_sub_cm_count=100_000,
        estimation_method="power_law_extrapolation_from_NASA_ODPO",
        source_reference="Kelso, T.S., Collision of Iridium 33 and Cosmos 2251, 2009",
    ),
    FragmentationEvent(
        event_id="microsat-r-2019",
        name="Microsat-R ASAT test (Mission Shakti)",
        year=2019,
        orbital_altitude_km=283.0,
        orbital_inclination_deg=96.6,
        raan_deg=342.0,
        catalogued_fragment_count=400,
        estimated_sub_cm_count=10_000,
        estimation_method="power_law_extrapolation_low_altitude_fast_decay",
        source_reference="NASA Orbital Debris Quarterly News, Vol 23 No 2, 2019",
    ),
    FragmentationEvent(
        event_id="solwind-p78-1985",
        name="Solwind P78-1 ASAT test",
        year=1985,
        orbital_altitude_km=525.0,
        orbital_inclination_deg=97.9,
        raan_deg=195.0,
        catalogued_fragment_count=285,
        estimated_sub_cm_count=100_000,
        estimation_method="power_law_extrapolation_long_decay_time",
        source_reference="Johnson, N.L., History of on-orbit fragmentations, NASA/TM-2008-214779",
    ),
    FragmentationEvent(
        event_id="breeze-m-2012",
        name="Breeze-M upper stage explosion",
        year=2012,
        orbital_altitude_km=760.0,
        orbital_inclination_deg=63.4,
        raan_deg=108.0,
        catalogued_fragment_count=500,
        estimated_sub_cm_count=50_000,
        estimation_method="power_law_extrapolation_from_NASA_ODPO",
        source_reference="NASA Orbital Debris Quarterly News, Vol 16 No 4, 2012",
    ),
    FragmentationEvent(
        event_id="cosmos-1408-2021",
        name="Cosmos-1408 ASAT test (Nudol)",
        year=2021,
        orbital_altitude_km=480.0,
        orbital_inclination_deg=82.6,
        raan_deg=278.0,
        catalogued_fragment_count=1500,
        estimated_sub_cm_count=80_000,
        estimation_method="power_law_extrapolation_from_published_assessment",
        source_reference="NASA orbital debris assessment, November 2021",
    ),
)


# ---------------------------------------------------------------------------
# Default implementation: SyntheticPowerLawModel
# ---------------------------------------------------------------------------

class SyntheticPowerLawModel:
    """Power-law debris population model aligned with NASA ORDEM 3.0 methodology.

    Uses the observed cumulative size distribution N(>D) ∝ D^-α to extrapolate
    the untracked sub-centimetre population from the known tracked population.

    This is a synthetic research fixture — not a calibrated physical model.
    Sub-cm counts carry ±50% uncertainty by construction.
    """

    model_id: str = "synthetic_power_law_v1"
    model_version: str = "1.0.0"

    # Approximate tracked LEO object counts by altitude shell (from public sources)
    # Source: NASA ODPO, ESA Annual Space Environment Report 2024
    _TRACKED_DISTRIBUTION: dict[tuple[float, float], int] = {
        (200, 400):   1_200,
        (400, 600):   8_500,
        (600, 800):  14_000,
        (800, 1000):  5_200,
        (1000, 1200): 2_100,
        (1200, 1400):   900,
        (1400, 1600):   650,
        (1600, 1800):   480,
        (1800, 2000):   370,
    }

    # Grün et al. (1985) / NASA ORDEM 3.0 reference flux at 400 km for each size regime
    # Units: impacts per m² per year (order-of-magnitude reference values)
    _REFERENCE_FLUX: dict[SizeRegime, float] = {
        SizeRegime.TRACKED:         1.0e-8,
        SizeRegime.NEAR_DETECTABLE: 1.0e-6,
        SizeRegime.SUB_CM:          1.0e-4,
        SizeRegime.SUB_MM:          1.0e-2,
    }

    def build_snapshot(
        self,
        config: PopulationModelConfig,
        generated_at: datetime,
    ) -> DebrisPopulationSnapshot:
        shells: list[DebrisPopulationBin] = []
        clouds: list[DebrisCloud] = []
        total_tracked = 0
        total_sub_cm = 0

        alt = config.altitude_min_km
        while alt < config.altitude_max_km:
            alt_max = min(alt + config.altitude_bin_km, config.altitude_max_km)
            inc = 0.0
            while inc < 180.0:
                inc_max = min(inc + config.inclination_bin_deg, 180.0)
                shell = OrbitalShell(alt, alt_max, inc, inc_max)

                for regime in SizeRegime:
                    count, density, flux = self._compute_bin(
                        shell, regime, config.size_power_law_index
                    )
                    shells.append(DebrisPopulationBin(
                        shell=shell,
                        size_regime=regime,
                        object_count=count,
                        spatial_density_per_km3=density,
                        flux_per_m2_per_year=flux,
                        population_source=(
                            PopulationSource.USSPACECOM_TLE
                            if regime == SizeRegime.TRACKED
                            else PopulationSource.SYNTHETIC_ESTIMATE
                        ),
                        uncertainty_fraction=(
                            0.10 if regime == SizeRegime.TRACKED
                            else config.sub_cm_uncertainty_fraction
                        ),
                        evidence_class=EvidenceClass.SYNTHETIC,
                    ))
                    if regime == SizeRegime.TRACKED:
                        total_tracked += count
                    elif regime == SizeRegime.SUB_CM:
                        total_sub_cm += count

                inc = inc_max
            alt = alt_max

        # Build debris clouds from fragmentation event catalog
        for event in FRAGMENTATION_EVENT_CATALOG:
            cloud = DebrisCloud(
                cloud_id=f"cloud-{event.event_id}",
                event_id=event.event_id,
                centroid_altitude_km=event.orbital_altitude_km,
                centroid_inclination_deg=event.orbital_inclination_deg,
                centroid_raan_deg=event.raan_deg,
                spread_altitude_km=50.0,
                spread_inclination_deg=5.0,
                peak_number_density_per_km3=max(
                    event.estimated_sub_cm_count / 1_000.0, 0.1
                ),
                total_mass_estimate_kg=event.catalogued_fragment_count * 0.5,
                size_regime=SizeRegime.SUB_CM,
                evidence_class=EvidenceClass.SYNTHETIC,
                limitation=(
                    "Cloud parameters derived from publicly available orbital data "
                    "and power-law extrapolation. Spatial extent is modelled, not "
                    "directly observed. Sub-cm counts carry ±50% uncertainty."
                ),
            )
            clouds.append(cloud)

        snapshot_id = "pop-" + sha256(
            f"{generated_at.isoformat()}{self.model_id}{config.size_power_law_index}".encode()
        ).hexdigest()[:12]

        return DebrisPopulationSnapshot(
            snapshot_id=snapshot_id,
            generated_at=generated_at,
            model_version=self.model_version,
            model_id=self.model_id,
            source_reference=(
                "NASA ORDEM 3.0 methodology; ESA MASTER 2009 extrapolation parameters; "
                "USSPACECOM public TLE catalog distribution"
            ),
            shells=tuple(shells),
            clouds=tuple(clouds),
            events=FRAGMENTATION_EVENT_CATALOG,
            total_tracked_objects=total_tracked,
            estimated_sub_cm_total=total_sub_cm,
            altitude_range_km=(config.altitude_min_km, config.altitude_max_km),
            evidence_class=EvidenceClass.SYNTHETIC,
            limitation=(
                "Synthetic power-law extrapolation. Sub-cm counts are statistical "
                "estimates with ±50% uncertainty based on published size-distribution "
                "indices. No direct sub-cm detection is claimed. Tracked counts are "
                "approximations of publicly available catalog distributions, not live "
                "TLE data."
            ),
        )

    def _compute_bin(
        self,
        shell: OrbitalShell,
        regime: SizeRegime,
        alpha: float,
    ) -> tuple[int, float, float]:
        """Return (count, density, flux) for one shell × size-regime bin."""
        # Find tracked reference count for this altitude range
        alt_c = shell.altitude_km_centre
        tracked_ref = 0
        for (alo, ahi), cnt in self._TRACKED_DISTRIBUTION.items():
            if alo <= alt_c < ahi:
                tracked_ref = cnt
                break

        # Fraction of inclination bin vs. full sphere
        inc_frac = (shell.inclination_deg_max - shell.inclination_deg_min) / 180.0

        # Tracked count (proportional to inclination fraction)
        tracked_count = max(0, int(tracked_ref * inc_frac))

        # Power-law extrapolation: N_sub-cm = N_tracked × (D_tracked/D_sub-cm)^α
        # D_tracked ≈ 0.15 m, D_sub-cm ≈ 0.003 m → ratio ≈ 50
        # α ≈ 2.5 from published MASTER/ORDEM literature
        SIZE_RATIOS = {
            SizeRegime.TRACKED:         1.0,
            SizeRegime.NEAR_DETECTABLE: 10.0 ** alpha,
            SizeRegime.SUB_CM:          50.0 ** alpha,
            SizeRegime.SUB_MM:          500.0 ** alpha,
        }
        count = max(0, int(tracked_count * SIZE_RATIOS[regime]))

        # Spatial density from object count and shell volume
        volume = max(shell.volume_km3, 1e-9)
        density = count / volume

        # Flux: scale reference flux by altitude (drag decay factor)
        alt_decay = math.exp(-(alt_c - 400.0) / 500.0)
        flux = self._REFERENCE_FLUX[regime] * alt_decay

        return count, density, flux
