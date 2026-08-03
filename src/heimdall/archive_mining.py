"""Archive mining domain contracts for the observed evidence acquisition pathway.

This module defines the governance-compliant types for the zero-budget
archive mining approach described in EVIDENCE_PATHWAYS.md (Pathway A).

Pipeline:
    1. ConjunctionPrediction  — predicted close approach (TLE + observatory)
    2. PlasmaWindow            — extracted plasma data around conjunction time
    3. WindowAnalysisResult    — statistical test result for one window
    4. ArchiveMiningCampaign   — pre-registered campaign record (sealed before analysis)
    5. ArchiveMiningReport     — complete governed report with all results + audit

Design principles:
    - All results — including null results — must flow through these contracts.
    - Pre-registration is enforced: a campaign cannot be created after analysis.
    - Evidence class ceiling is OBSERVED for real instrument data, SYNTHETIC for
      simulated test data.
    - Plug-and-play adapters: any data source can be substituted behind the
      PlasmaDataAdapter Protocol without changing analysis code.
    - Zero third-party runtime dependencies.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, Sequence

from .domain import EvidenceClass


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class AnalysisVerdict(str, Enum):
    """Outcome of a single conjunction window analysis."""
    SIGNAL_DETECTED    = "signal_detected"     # above significance threshold
    NO_SIGNAL          = "no_signal"           # below threshold (null result)
    INCONCLUSIVE       = "inconclusive"        # borderline / insufficient data
    DATA_QUALITY_FAIL  = "data_quality_fail"   # window excluded due to data quality
    RFI_CONTAMINATED   = "rfi_contaminated"    # excluded — radio frequency interference
    ANALYSIS_ERROR     = "analysis_error"      # processing failure (excluded)


class CampaignStatus(str, Enum):
    PLANNED    = "planned"     # pre-registered, data not yet collected
    RUNNING    = "running"     # data collection in progress
    COMPLETE   = "complete"    # all windows analysed
    HALTED     = "halted"      # stopped early (stopping rule triggered)
    RETRACTED  = "retracted"   # evidence invalidated after review


class DataSource(str, Enum):
    """Instrument source for plasma data."""
    ESA_SWARM_ALPHA   = "esa_swarm_alpha"
    ESA_SWARM_BRAVO   = "esa_swarm_bravo"
    ESA_SWARM_CHARLIE = "esa_swarm_charlie"
    EISCAT_UHF        = "eiscat_uhf"
    EISCAT_VHF        = "eiscat_vhf"
    MILLSTONE_HILL    = "millstone_hill"
    GIRO_DIGISONDE    = "giro_digisonde"
    SYNTHETIC_TEST    = "synthetic_test"       # for testing only


# ---------------------------------------------------------------------------
# Domain contracts (all frozen dataclasses)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TleObject:
    """A tracked orbital object from the TLE catalog."""
    catalog_number: int
    name: str
    tle_line1: str
    tle_line2: str
    catalog_source: str    # "celestrak" | "space-track" | etc.

    def __post_init__(self) -> None:
        if self.catalog_number <= 0:
            raise ValueError("catalog number must be positive")
        if not self.tle_line1.startswith("1 ") or not self.tle_line2.startswith("2 "):
            raise ValueError("TLE lines must start with '1 ' and '2 '")
        if not self.catalog_source:
            raise ValueError("catalog_source is required")


@dataclass(frozen=True)
class ObservatorySpec:
    """Specification of the observing instrument / beam centre."""
    source: DataSource
    name: str
    latitude_deg: float
    longitude_deg: float
    altitude_m: float
    beam_halfwidth_deg: float     # half-angle of the beam cone
    time_resolution_s: float      # native time resolution of data product
    frequency_hz: float           # operating frequency (0 for in-situ)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("observatory name is required")
        if not -90 <= self.latitude_deg <= 90:
            raise ValueError("latitude must be in [-90, 90]")
        if not -180 <= self.longitude_deg <= 180:
            raise ValueError("longitude must be in [-180, 180]")
        if self.beam_halfwidth_deg < 0 or self.time_resolution_s <= 0:
            raise ValueError("beam half-width and time resolution must be positive")


@dataclass(frozen=True)
class ConjunctionPrediction:
    """A predicted close approach between a debris object and an observatory beam.

    Computed deterministically from TLE propagation — no observed data yet.
    """
    conjunction_id: str
    tle_object: TleObject
    observatory: ObservatorySpec
    predicted_transit_utc: datetime
    closest_approach_km: float
    elevation_deg: float
    relative_velocity_km_s: float
    transit_duration_s: float
    propagator_id: str           # "sgp4" | "j2" | etc.
    evidence_class: EvidenceClass

    def __post_init__(self) -> None:
        if not self.conjunction_id or not self.propagator_id:
            raise ValueError("conjunction identity and propagator ID are required")
        if self.predicted_transit_utc.tzinfo is None:
            raise ValueError("predicted_transit_utc must be timezone-aware")
        if self.closest_approach_km < 0 or self.relative_velocity_km_s <= 0:
            raise ValueError("approach distance and velocity must be non-negative/positive")
        if self.transit_duration_s <= 0:
            raise ValueError("transit duration must be positive")


@dataclass(frozen=True)
class PlasmaWindow:
    """A time-series extract of plasma measurements around a conjunction.

    Contains raw data values — no analysis applied yet.  The raw_artifact_digest
    links back to the original source file for full provenance traceability.
    """
    window_id: str
    conjunction_id: str
    source: DataSource
    window_start_utc: datetime
    window_end_utc: datetime
    time_step_s: float
    electron_density_per_m3: tuple[float, ...]    # Ne at each time step
    data_quality_flags: tuple[int, ...]           # 0=good, nonzero=flagged
    raw_artifact_digest: str                      # sha256 of source file
    acquisition_manifest_digest: str             # sha256 of custody record
    evidence_class: EvidenceClass

    def __post_init__(self) -> None:
        if not self.window_id or not self.conjunction_id:
            raise ValueError("window and conjunction IDs are required")
        if self.window_start_utc.tzinfo is None or self.window_end_utc.tzinfo is None:
            raise ValueError("window timestamps must be timezone-aware")
        if self.window_start_utc >= self.window_end_utc:
            raise ValueError("window start must precede end")
        if len(self.electron_density_per_m3) != len(self.data_quality_flags):
            raise ValueError("electron density and quality flag arrays must have equal length")
        if len(self.electron_density_per_m3) == 0:
            raise ValueError("plasma window must contain at least one sample")
        if not self.raw_artifact_digest.startswith("sha256:"):
            raise ValueError("raw_artifact_digest must be a sha256: prefixed digest")
        if not self.acquisition_manifest_digest.startswith("sha256:"):
            raise ValueError("acquisition_manifest_digest must be a sha256: prefixed digest")

    @property
    def n_good_samples(self) -> int:
        return sum(1 for q in self.data_quality_flags if q == 0)

    @property
    def good_fraction(self) -> float:
        if not self.data_quality_flags:
            return 0.0
        return self.n_good_samples / len(self.data_quality_flags)

    @property
    def median_ne(self) -> float:
        good = [v for v, q in zip(self.electron_density_per_m3, self.data_quality_flags) if q == 0]
        if not good:
            return float("nan")
        s = sorted(good)
        n = len(s)
        return (s[n // 2] + s[(n - 1) // 2]) / 2.0


@dataclass(frozen=True)
class WindowAnalysisResult:
    """Statistical analysis result for one plasma window.

    Records the pre-registered test outcome, the computed statistics, and
    an explicit verdict — including null results and excluded windows.
    """
    result_id: str
    window_id: str
    conjunction_id: str
    # Pre-registered test parameters (must match campaign protocol)
    test_name: str             # "kolmogorov_smirnov" | "mann_whitney" | "z_score"
    significance_threshold: float
    baseline_window_s: float   # duration of pre-conjunction baseline
    # Computed statistics
    peak_delta_ne_fraction: float     # max |δNe/Ne| in window
    baseline_mean_ne: float
    baseline_std_ne: float
    test_statistic: float
    p_value: float
    # Outcome
    verdict: AnalysisVerdict
    verdict_reason: str
    evidence_class: EvidenceClass
    limitation: str

    def __post_init__(self) -> None:
        if not self.result_id or not self.window_id or not self.conjunction_id:
            raise ValueError("result, window, and conjunction IDs are required")
        if not 0 < self.significance_threshold < 1:
            raise ValueError("significance threshold must be in (0, 1)")
        if not self.verdict_reason:
            raise ValueError("verdict reason is required")
        if not self.limitation:
            raise ValueError("limitation string is required for all evidence")

    @property
    def is_positive_detection(self) -> bool:
        return self.verdict == AnalysisVerdict.SIGNAL_DETECTED

    @property
    def is_valid_observation(self) -> bool:
        """True if the window was analysed (not excluded for data quality)."""
        return self.verdict not in (
            AnalysisVerdict.DATA_QUALITY_FAIL,
            AnalysisVerdict.RFI_CONTAMINATED,
            AnalysisVerdict.ANALYSIS_ERROR,
        )


@dataclass(frozen=True)
class AnalysisProtocol:
    """Pre-registered analysis protocol — sealed before any data is viewed.

    This must be created and its digest recorded in the governance ledger
    *before* any plasma windows are extracted or analysed.  Any deviation
    from this protocol invalidates the evidential status of results.
    """
    protocol_id: str
    hypothesis: str                   # The falsifiable primary hypothesis
    null_hypothesis: str              # Explicit null hypothesis
    primary_metric: str               # What is measured (e.g. "peak_delta_ne_fraction")
    statistical_test: str             # Which test is applied
    significance_threshold: float     # α level
    multiple_comparison_correction: str  # "bonferroni" | "fdr_bh" | "none"
    minimum_window_count: int         # Minimum valid windows for conclusion
    null_result_criterion: str        # Explicit statement of what counts as null
    stopping_rule: str                # When to halt early
    confounder_list: tuple[str, ...]  # Pre-declared confounders
    control_analysis: str             # How control (non-conjunction) windows are used
    analysis_window_s: float          # Width of conjunction analysis window
    baseline_window_s: float          # Width of pre-conjunction baseline
    minimum_good_fraction: float      # Minimum fraction of good-quality samples
    created_at: datetime
    protocol_digest: str              # sha256 of the protocol itself (excluding this field)

    def __post_init__(self) -> None:
        if not self.protocol_id or not self.hypothesis or not self.null_hypothesis:
            raise ValueError("protocol identity and hypotheses are required")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        if not 0 < self.significance_threshold < 1:
            raise ValueError("significance threshold must be in (0, 1)")
        if self.minimum_window_count < 1:
            raise ValueError("minimum window count must be at least 1")
        if not self.confounder_list:
            raise ValueError("at least one confounder must be declared")
        if self.analysis_window_s <= 0 or self.baseline_window_s <= 0:
            raise ValueError("analysis and baseline window durations must be positive")
        if not 0 < self.minimum_good_fraction <= 1:
            raise ValueError("minimum good fraction must be in (0, 1]")
        if not self.protocol_digest.startswith("sha256:"):
            raise ValueError("protocol_digest must be a sha256: prefixed digest")


@dataclass(frozen=True)
class ArchiveMiningCampaign:
    """A complete pre-registered archive mining campaign.

    Records the instrument, TLE population, protocol, conjunction list,
    and status.  Must be created before any analysis and sealed via the
    governance ledger.
    """
    campaign_id: str
    name: str
    observatory: ObservatorySpec
    tle_catalog_digest: str       # sha256 of TLE file used for conjunction computation
    tle_catalog_source: str       # where the TLE was obtained
    protocol: AnalysisProtocol
    conjunctions: tuple[ConjunctionPrediction, ...]
    status: CampaignStatus
    created_at: datetime
    ledger_entry_id: str          # ID in the governance ledger (from run_pre_registered_experiment.py)
    evidence_class: EvidenceClass

    def __post_init__(self) -> None:
        if not self.campaign_id or not self.name:
            raise ValueError("campaign identity is required")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        if not self.tle_catalog_digest.startswith("sha256:"):
            raise ValueError("tle_catalog_digest must be a sha256: prefixed digest")
        if not self.conjunctions:
            raise ValueError("campaign must have at least one conjunction prediction")
        if not self.ledger_entry_id:
            raise ValueError("ledger_entry_id is required — pre-register before creating campaign")


@dataclass(frozen=True)
class ArchiveMiningReport:
    """Complete governed report of a finished archive mining campaign.

    Contains every result — positive, negative, excluded, failed.
    A null result is preserved and presented with the same care as a detection.
    """
    report_id: str
    campaign: ArchiveMiningCampaign
    windows_analysed: tuple[WindowAnalysisResult, ...]
    windows_total: int
    windows_valid: int
    windows_positive: int
    windows_null: int
    windows_excluded: int
    overall_verdict: AnalysisVerdict
    ks_statistic: float          # KS test across all valid windows
    p_value_corrected: float     # After multiple-comparison correction
    effect_size: float           # Cohen's d or normalised peak δNe
    generated_at: datetime
    independent_reviewer_id: str   # "" if not yet reviewed
    audit_bundle_digest: str       # sha256 of the audit bundle
    evidence_class: EvidenceClass
    limitation: str

    def __post_init__(self) -> None:
        if not self.report_id or not self.limitation:
            raise ValueError("report identity and limitation are required")
        if self.generated_at.tzinfo is None:
            raise ValueError("generated_at must be timezone-aware")
        if not self.audit_bundle_digest.startswith("sha256:"):
            raise ValueError("audit_bundle_digest must be a sha256: prefixed digest")
        n = self.windows_valid + self.windows_excluded
        if n != self.windows_total and self.windows_total > 0:
            raise ValueError("windows_valid + windows_excluded must equal windows_total")
        if self.windows_positive > self.windows_valid:
            raise ValueError("positive count cannot exceed valid window count")

    @property
    def detection_rate(self) -> float:
        if self.windows_valid == 0:
            return 0.0
        return self.windows_positive / self.windows_valid

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "campaign_id": self.campaign.campaign_id,
            "generated_at": self.generated_at.isoformat(),
            "overall_verdict": self.overall_verdict.value,
            "windows_total": self.windows_total,
            "windows_valid": self.windows_valid,
            "windows_positive": self.windows_positive,
            "windows_null": self.windows_null,
            "windows_excluded": self.windows_excluded,
            "detection_rate": self.detection_rate,
            "ks_statistic": self.ks_statistic,
            "p_value_corrected": self.p_value_corrected,
            "effect_size": self.effect_size,
            "independent_reviewer_id": self.independent_reviewer_id,
            "audit_bundle_digest": self.audit_bundle_digest,
            "evidence_class": self.evidence_class.value,
            "limitation": self.limitation,
            "individual_results": [
                {
                    "result_id": r.result_id,
                    "conjunction_id": r.conjunction_id,
                    "verdict": r.verdict.value,
                    "peak_delta_ne_fraction": r.peak_delta_ne_fraction,
                    "p_value": r.p_value,
                    "test_statistic": r.test_statistic,
                    "verdict_reason": r.verdict_reason,
                }
                for r in self.windows_analysed
            ],
        }


# ---------------------------------------------------------------------------
# Plug-and-play data source Protocol
# ---------------------------------------------------------------------------

class PlasmaDataAdapter(Protocol):
    """Adapter for any plasma data source.

    Implement this to add a new observatory (SWARM, EISCAT, Digisonde, etc.)
    without changing any analysis code.
    """
    source: DataSource

    def fetch_window(
        self,
        conjunction: ConjunctionPrediction,
        window_s: float,
        baseline_s: float,
    ) -> PlasmaWindow:
        """Fetch electron density time series around a conjunction time.

        Returns a PlasmaWindow with raw bytes preserved and custody records.
        For synthetic test data, evidence_class must be SYNTHETIC.
        For real instrument data, evidence_class must be OBSERVED.
        """
        ...


# ---------------------------------------------------------------------------
# Reference observatories
# ---------------------------------------------------------------------------

REFERENCE_OBSERVATORIES: dict[DataSource, ObservatorySpec] = {
    DataSource.ESA_SWARM_ALPHA: ObservatorySpec(
        source=DataSource.ESA_SWARM_ALPHA,
        name="ESA SWARM Alpha (Sat A)",
        latitude_deg=0.0,            # polar-orbiting — latitude changes continuously
        longitude_deg=0.0,
        altitude_m=460_000.0,
        beam_halfwidth_deg=0.0,      # in-situ measurement — no beam
        time_resolution_s=0.5,       # LP_HM product: 2 Hz
        frequency_hz=0.0,            # in-situ, not radar
    ),
    DataSource.EISCAT_UHF: ObservatorySpec(
        source=DataSource.EISCAT_UHF,
        name="EISCAT UHF Tromsø",
        latitude_deg=69.583,
        longitude_deg=19.217,
        altitude_m=86.0,
        beam_halfwidth_deg=0.3,      # ~0.6° full-width beam
        time_resolution_s=1.0,
        frequency_hz=930e6,
    ),
    DataSource.MILLSTONE_HILL: ObservatorySpec(
        source=DataSource.MILLSTONE_HILL,
        name="Millstone Hill ISR (MIT Haystack)",
        latitude_deg=42.619,
        longitude_deg=-71.492,
        altitude_m=130.0,
        beam_halfwidth_deg=0.3,
        time_resolution_s=1.0,
        frequency_hz=440e6,
    ),
}


# ---------------------------------------------------------------------------
# Standard pre-registered protocol template
# ---------------------------------------------------------------------------

def build_standard_protocol(
    hypothesis: str = (
        "A statistically significant transient electron density perturbation "
        "correlated with the transit of a known TLE object within 10 km of the "
        "instrument beam is detectable above the 3-sigma noise floor."
    ),
) -> AnalysisProtocol:
    """Build the standard pre-registered analysis protocol.

    Seal this into the governance ledger BEFORE loading any instrument data.
    """
    protocol_data = {
        "protocol_id": "standard-archive-mining-v1",
        "hypothesis": hypothesis,
        "null_hypothesis": (
            "No statistically significant plasma perturbation is detectable "
            "within the conjunction windows."
        ),
        "primary_metric": "peak_delta_ne_fraction",
        "statistical_test": "kolmogorov_smirnov",
        "significance_threshold": 0.05,
        "multiple_comparison_correction": "bonferroni",
        "minimum_window_count": 20,
        "null_result_criterion": (
            "KS statistic < 0.15 or corrected p-value > 0.10 "
            "after analysis of >= 20 valid windows."
        ),
        "stopping_rule": (
            "Halt if first 10 windows show mean peak_delta_ne_fraction < 0.01 "
            "(below practical detection limit)."
        ),
        "confounder_list": [
            "ionospheric_scintillation",
            "meteor_ablation",
            "radio_frequency_interference",
            "calibration_drift",
            "solar_energetic_particle_events",
            "auroral_substorm",
            "spacecraft_charging",
        ],
        "control_analysis": (
            "Identical analysis applied to 100 randomly selected non-conjunction "
            "windows from the same observing session."
        ),
        "analysis_window_s": 30.0,
        "baseline_window_s": 300.0,
        "minimum_good_fraction": 0.8,
    }

    # Compute deterministic digest over protocol content
    digest_input = str(sorted(protocol_data.items())).encode()
    protocol_digest = "sha256:" + sha256(digest_input).hexdigest()

    return AnalysisProtocol(
        protocol_id=protocol_data["protocol_id"],
        hypothesis=protocol_data["hypothesis"],
        null_hypothesis=protocol_data["null_hypothesis"],
        primary_metric=protocol_data["primary_metric"],
        statistical_test=protocol_data["statistical_test"],
        significance_threshold=protocol_data["significance_threshold"],
        multiple_comparison_correction=protocol_data["multiple_comparison_correction"],
        minimum_window_count=protocol_data["minimum_window_count"],
        null_result_criterion=protocol_data["null_result_criterion"],
        stopping_rule=protocol_data["stopping_rule"],
        confounder_list=tuple(protocol_data["confounder_list"]),
        control_analysis=protocol_data["control_analysis"],
        analysis_window_s=protocol_data["analysis_window_s"],
        baseline_window_s=protocol_data["baseline_window_s"],
        minimum_good_fraction=protocol_data["minimum_good_fraction"],
        created_at=datetime.now(timezone.utc),
        protocol_digest=protocol_digest,
    )
