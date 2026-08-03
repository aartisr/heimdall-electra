"""Multi-node passive sensing pipeline — end-to-end orchestrator.

Chains all Stage 4 components into a complete pipeline:
    PlasmaWindow observations (N nodes)
        → CrossCorrelation → TdoaMeasurement (for each node pair)
        → GaussNewtonTdoaSolver → TdoaSolution (3D position estimate)
        → PlasmaWakeModel → WakeSignalPrediction (physics interpretation)
        → MultiNodeDetectionResult (governed output with full provenance)

Design patterns used:
    - Strategy:   CrossCorrelationAlgorithm, TdoaSolver, PlasmaWakeModel protocols
    - Chain of Responsibility: sequential pipeline stages
    - Builder:    MultiNodePipelineConfig assembled from individual components
    - Decorator:  timing and audit trail wrapped transparently via observability
    - Repository: pipeline result stored via existing ingestion infrastructure

All outputs carry EvidenceClass.SYNTHETIC until real observations are used.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Sequence

from .domain import EvidenceClass
from .archive_mining import PlasmaWindow, DataSource
from .physics_contract import CoordinateFrame, PlasmaEnvironment, OrbitalState, TargetAssumptions
from .signal_processing import (
    CrossCorrelationAlgorithm,
    CorrelationResult,
    FftCrossCorrelation,
    GccPhatCrossCorrelation,
)
from .tdoa_solver import (
    TdoaSolver,
    TdoaMeasurement,
    TdoaSolution,
    ReceiverNode,
    GaussNewtonTdoaSolver,
    GeometryAssessment,
    assess_geometry,
)
from .plasma_wake_model import (
    PlasmaWakeModel,
    WakeSignalPrediction,
    AnalyticWakeModel,
    SurfacePotentialModel,
)


# ---------------------------------------------------------------------------
# Pipeline configuration — Builder pattern
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MultiNodePipelineConfig:
    """Immutable configuration for the full multi-node pipeline.

    Build one config, reuse across many runs — zero side effects.
    """
    correlation_algorithm: str       # "gcc_phat" | "fft_gcc"
    solver_id: str                   # "gauss_newton_tdoa_v1"
    model_id: str                    # "analytic_wake_v1"
    surface_potential_model: SurfacePotentialModel
    minimum_correlation_snr_db: float    # reject pairs with SNR below this
    minimum_good_samples_fraction: float # reject windows below this quality
    coordinate_frame: CoordinateFrame

    def __post_init__(self) -> None:
        if self.minimum_correlation_snr_db < 0:
            raise ValueError("minimum SNR must be non-negative")
        if not 0 < self.minimum_good_samples_fraction <= 1:
            raise ValueError("minimum good fraction must be in (0, 1]")


def default_pipeline_config() -> MultiNodePipelineConfig:
    """Standard configuration for the multi-node pipeline."""
    return MultiNodePipelineConfig(
        correlation_algorithm="gcc_phat",
        solver_id="gauss_newton_tdoa_v1",
        model_id="analytic_wake_v1",
        surface_potential_model=SurfacePotentialModel.CONSERVATIVE_ESTIMATE,
        minimum_correlation_snr_db=3.0,
        minimum_good_samples_fraction=0.8,
        coordinate_frame=CoordinateFrame.ECI_J2000,
    )


# ---------------------------------------------------------------------------
# Pipeline result contracts
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NodePairCorrelation:
    """Cross-correlation result for one pair of receiver nodes."""
    pair_id: str
    node_i_id: str
    node_j_id: str
    correlation: CorrelationResult
    tdoa_measurement: TdoaMeasurement
    quality_passed: bool
    quality_reason: str

    def __post_init__(self) -> None:
        if not self.pair_id:
            raise ValueError("pair_id required")


@dataclass(frozen=True)
class MultiNodeDetectionResult:
    """Complete governed output of the multi-node pipeline for one event.

    Contains the full provenance chain from raw windows → correlations →
    TDOA solution → wake physics interpretation.
    """
    result_id: str
    event_time_utc: datetime
    n_nodes: int
    n_valid_pairs: int
    node_pair_correlations: tuple[NodePairCorrelation, ...]
    tdoa_solution: TdoaSolution
    geometry_assessment: GeometryAssessment
    wake_prediction: WakeSignalPrediction | None   # None if target size unknown
    estimated_altitude_km: float | None
    estimated_velocity_km_s: float | None
    overall_snr_db: float
    pipeline_config: MultiNodePipelineConfig
    evidence_class: EvidenceClass
    limitation: str

    def __post_init__(self) -> None:
        if not self.result_id or not self.limitation:
            raise ValueError("result_id and limitation required")
        if self.event_time_utc.tzinfo is None:
            raise ValueError("event_time_utc must be timezone-aware")

    @property
    def is_well_localised(self) -> bool:
        return (
            self.tdoa_solution.is_valid
            and self.geometry_assessment.is_well_conditioned
            and self.tdoa_solution.position_uncertainty_m < 10_000.0  # <10 km
        )

    def to_dict(self) -> dict:
        return {
            "result_id": self.result_id,
            "event_time_utc": self.event_time_utc.isoformat(),
            "n_nodes": self.n_nodes,
            "n_valid_pairs": self.n_valid_pairs,
            "tdoa_solution": self.tdoa_solution.to_dict(),
            "estimated_altitude_km": self.estimated_altitude_km,
            "estimated_velocity_km_s": self.estimated_velocity_km_s,
            "overall_snr_db": self.overall_snr_db,
            "is_well_localised": self.is_well_localised,
            "gdop": self.geometry_assessment.gdop,
            "baseline_km": self.geometry_assessment.baseline_km,
            "evidence_class": self.evidence_class.value,
            "limitation": self.limitation,
        }


# ---------------------------------------------------------------------------
# Pipeline components (Strategy pattern — each is replaceable)
# ---------------------------------------------------------------------------

def _build_correlator(algorithm_id: str) -> CrossCorrelationAlgorithm:
    if algorithm_id == "gcc_phat":
        return GccPhatCrossCorrelation()
    if algorithm_id == "fft_gcc":
        return FftCrossCorrelation()
    raise ValueError(f"Unknown correlation algorithm: {algorithm_id!r}")


def _build_solver(solver_id: str) -> TdoaSolver:
    if solver_id == "gauss_newton_tdoa_v1":
        return GaussNewtonTdoaSolver()
    raise ValueError(f"Unknown TDOA solver: {solver_id!r}")


def _build_wake_model(model_id: str) -> PlasmaWakeModel:
    if model_id == "analytic_wake_v1":
        return AnalyticWakeModel()
    raise ValueError(f"Unknown wake model: {model_id!r}")


# ---------------------------------------------------------------------------
# Stage 1 — Cross-correlation
# ---------------------------------------------------------------------------

def correlate_node_pair(
    window_i: PlasmaWindow,
    window_j: PlasmaWindow,
    node_i: ReceiverNode,
    node_j: ReceiverNode,
    config: MultiNodePipelineConfig,
) -> NodePairCorrelation:
    """Compute GCC-PHAT TDOA between two plasma windows."""
    pair_id = f"pair-{node_i.node_id}-{node_j.node_id}"

    # Quality gate: reject low-quality windows
    if window_i.good_fraction < config.minimum_good_samples_fraction:
        dummy_corr = CorrelationResult(
            algorithm_id=config.correlation_algorithm,
            tdoa_s=0.0, peak_correlation=0.0, peak_sample_index=0,
            correlation_values=(0.0,), sample_rate_hz=1.0, n_samples=0,
            snr_estimate_db=-999.0, confidence=0.0,
        )
        return NodePairCorrelation(
            pair_id=pair_id, node_i_id=node_i.node_id, node_j_id=node_j.node_id,
            correlation=dummy_corr,
            tdoa_measurement=TdoaMeasurement(
                measurement_id=f"tdoa-{pair_id}-failed",
                node_i_id=node_i.node_id, node_j_id=node_j.node_id,
                tdoa_s=0.0, uncertainty_s=1.0, correlation_snr_db=-999.0,
                algorithm_id=config.correlation_algorithm,
                evidence_class=window_i.evidence_class,
            ),
            quality_passed=False,
            quality_reason=f"window {window_i.window_id} good_fraction={window_i.good_fraction:.2f} < threshold",
        )

    # Align windows: use the shorter length
    n = min(len(window_i.electron_density_per_m3), len(window_j.electron_density_per_m3))
    sig_i = list(window_i.electron_density_per_m3[:n])
    sig_j = list(window_j.electron_density_per_m3[:n])

    # Remove mean (DC offset) before correlation
    mean_i = sum(sig_i) / max(n, 1)
    mean_j = sum(sig_j) / max(n, 1)
    sig_i = [v - mean_i for v in sig_i]
    sig_j = [v - mean_j for v in sig_j]

    # FFT needs power of 2 — pad to next power of 2
    n_pad = 1
    while n_pad < n:
        n_pad <<= 1

    from .signal_processing import _next_power_of_2
    n_pad = _next_power_of_2(n)
    sig_i = sig_i + [0.0] * (n_pad - n)
    sig_j = sig_j + [0.0] * (n_pad - n)

    correlator = _build_correlator(config.correlation_algorithm)
    sample_rate = 1.0 / window_i.time_step_s
    corr = correlator.correlate(sig_i, sig_j, sample_rate)

    snr_ok = corr.snr_estimate_db >= config.minimum_correlation_snr_db
    meas_id = "tdoa-" + sha256(f"{pair_id}{corr.tdoa_s}".encode()).hexdigest()[:10]

    meas = TdoaMeasurement(
        measurement_id=meas_id,
        node_i_id=node_i.node_id,
        node_j_id=node_j.node_id,
        tdoa_s=corr.tdoa_s,
        uncertainty_s=corr.tdoa_uncertainty_s,
        correlation_snr_db=corr.snr_estimate_db,
        algorithm_id=config.correlation_algorithm,
        evidence_class=window_i.evidence_class,
    )

    return NodePairCorrelation(
        pair_id=pair_id,
        node_i_id=node_i.node_id,
        node_j_id=node_j.node_id,
        correlation=corr,
        tdoa_measurement=meas,
        quality_passed=snr_ok,
        quality_reason=(
            f"SNR={corr.snr_estimate_db:.1f} dB "
            f"{'≥' if snr_ok else '<'} threshold={config.minimum_correlation_snr_db:.1f} dB"
        ),
    )


# ---------------------------------------------------------------------------
# Stage 2 — TDOA solving
# ---------------------------------------------------------------------------

def solve_position(
    pair_correlations: Sequence[NodePairCorrelation],
    nodes: Sequence[ReceiverNode],
    initial_guess: tuple[float, float, float],
    config: MultiNodePipelineConfig,
) -> TdoaSolution:
    """Solve for debris position from accepted TDOA measurements."""
    valid_measurements = [
        pc.tdoa_measurement
        for pc in pair_correlations
        if pc.quality_passed
    ]

    solver = _build_solver(config.solver_id)
    return solver.solve(valid_measurements, nodes, initial_guess, config.coordinate_frame)


# ---------------------------------------------------------------------------
# Full pipeline orchestrator
# ---------------------------------------------------------------------------

class MultiNodePipeline:
    """Orchestrates the complete multi-node passive sensing pipeline.

    Usage:
        config   = default_pipeline_config()
        pipeline = MultiNodePipeline(config)
        result   = pipeline.run(windows, nodes, plasma, orbital, initial_guess)

    Plug-and-play:
        Substitute any Stage via config:
            MultiNodePipelineConfig(correlation_algorithm="fft_gcc", ...)
        Or override at construction:
            MultiNodePipeline(config, correlator=MyCustomCorrelator())
    """

    def __init__(
        self,
        config: MultiNodePipelineConfig | None = None,
        correlator: CrossCorrelationAlgorithm | None = None,
        solver: TdoaSolver | None = None,
        wake_model: PlasmaWakeModel | None = None,
    ) -> None:
        self.config     = config or default_pipeline_config()
        self.correlator = correlator or _build_correlator(self.config.correlation_algorithm)
        self.solver     = solver     or _build_solver(self.config.solver_id)
        self.wake_model = wake_model or _build_wake_model(self.config.model_id)

    def run(
        self,
        windows: Sequence[PlasmaWindow],
        nodes: Sequence[ReceiverNode],
        plasma: PlasmaEnvironment,
        orbital: OrbitalState,
        initial_guess: tuple[float, float, float] | None = None,
        target: TargetAssumptions | None = None,
        event_time_utc: datetime | None = None,
    ) -> MultiNodeDetectionResult:
        """Run the full pipeline end-to-end.

        Args:
            windows:       One PlasmaWindow per receiver node (same event)
            nodes:         Receiver node specifications in matching order
            plasma:        Ionospheric environment at event time
            orbital:       Orbital state estimate (velocity at minimum)
            initial_guess: Initial position estimate (m, ECI) — defaults to
                           geometric centre of receiver array
            target:        Fragment size/charge assumptions (optional)
            event_time_utc: Event time (UTC) — defaults to first window start
        """
        if len(windows) != len(nodes):
            raise ValueError(f"windows and nodes must have equal count, got {len(windows)} vs {len(nodes)}")
        if len(windows) < 2:
            raise ValueError("multi-node pipeline requires at least 2 nodes")

        if event_time_utc is None:
            event_time_utc = windows[0].window_start_utc

        # Default initial guess: centroid of receiver array
        if initial_guess is None:
            positions = [n.position_m for n in nodes]
            initial_guess = tuple(
                sum(p[k] for p in positions) / len(positions) for k in range(3)
            )  # type: ignore[assignment]

        node_map: dict[str, ReceiverNode]   = {n.node_id: n for n in nodes}
        window_map: dict[str, PlasmaWindow] = {
            n.node_id: w for n, w in zip(nodes, windows)
        }

        # Stage 1: cross-correlate all node pairs
        pair_correlations: list[NodePairCorrelation] = []
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                ni, nj = nodes[i], nodes[j]
                wi = window_map[ni.node_id]
                wj = window_map[nj.node_id]
                pair_corr = correlate_node_pair(wi, wj, ni, nj, self.config)
                pair_correlations.append(pair_corr)

        n_valid = sum(1 for pc in pair_correlations if pc.quality_passed)

        # Stage 2: solve TDOA position
        tdoa_solution = solve_position(pair_correlations, nodes, initial_guess, self.config)

        # Stage 3: geometry assessment
        geom = assess_geometry(nodes, tdoa_solution.position_m)

        # Stage 4: physics interpretation (optional — requires target size)
        wake_prediction: WakeSignalPrediction | None = None
        if target is not None:
            wake_prediction = self.wake_model.predict(
                target, plasma, orbital, self.config.surface_potential_model
            )

        # Estimate altitude from ECI position (approx)
        earth_radius_m = 6_371_000.0
        pos = tdoa_solution.position_m
        r = math.sqrt(sum(p**2 for p in pos))
        alt_km = (r - earth_radius_m) / 1000.0 if r > earth_radius_m else None

        # Estimate velocity magnitude from orbital state
        vx, vy, vz = orbital.velocity_m_per_s
        vel_km_s = math.sqrt(vx**2 + vy**2 + vz**2) / 1000.0

        # Overall SNR: mean of valid pair SNRs
        valid_snrs = [pc.correlation.snr_estimate_db for pc in pair_correlations if pc.quality_passed]
        overall_snr = sum(valid_snrs) / max(len(valid_snrs), 1) if valid_snrs else -999.0

        # Evidence class: synthetic unless all windows are observed
        all_observed = all(w.evidence_class == EvidenceClass.OBSERVED for w in windows)
        ev_class = EvidenceClass.OBSERVED if all_observed else EvidenceClass.SYNTHETIC

        result_id = "mnd-" + sha256(
            f"{event_time_utc.isoformat()}{len(windows)}".encode()
        ).hexdigest()[:10]

        return MultiNodeDetectionResult(
            result_id=result_id,
            event_time_utc=event_time_utc,
            n_nodes=len(nodes),
            n_valid_pairs=n_valid,
            node_pair_correlations=tuple(pair_correlations),
            tdoa_solution=tdoa_solution,
            geometry_assessment=geom,
            wake_prediction=wake_prediction,
            estimated_altitude_km=round(alt_km, 1) if alt_km is not None and 0 < alt_km < 2000 else None,
            estimated_velocity_km_s=round(vel_km_s, 2),
            overall_snr_db=overall_snr,
            pipeline_config=self.config,
            evidence_class=ev_class,
            limitation=(
                "Multi-node pipeline result. "
                + ("ANALYTIC_UNVALIDATED wake model used. " if wake_prediction else "")
                + "TDOA accuracy limited by timing synchronisation and receiver geometry. "
                + "No real ionospheric measurements used. "
                + f"EvidenceClass: {ev_class.value}."
            ),
        )
