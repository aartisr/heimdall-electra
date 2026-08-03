"""TDOA-based debris position estimation — hyperbolic solver.

Implements Time Difference of Arrival (TDOA) positioning, the same
technique used in GPS, lightning networks, and passive acoustic arrays.

Given N receivers at known positions r_i and time delay measurements
Δt_ij = (arrival at node j) - (arrival at node i), find debris position p:

    c × Δt_ij = |p - r_j| - |p - r_i|          (hyperbola equation)

This is a non-linear system; we linearise around an initial estimate and
solve iteratively using Gauss-Newton least squares.

Uncertainty propagation:
    The timing uncertainty σ_τ propagates to position via the Fisher
    Information Matrix:
        Σ_pos = (J^T W J)^{-1} σ_τ²
    where J is the Jacobian of the measurement model.

Design:
    - TdoaSolver Protocol — any solver (closed-form, ML, MCMC) can be plugged in
    - GaussNewtonSolver — default iterative solver (converges in 5-10 iterations)
    - Covariance propagation via 3×3 matrix algebra (pure Python)
    - All results carry explicit uncertainty bounds and EvidenceClass

References:
    Foy (1976) — hyperbolic TDOA positioning
    Smith & Abel (1987) — TDOA Cramér-Rao bound
    Knapp & Carter (1976) — GCC-PHAT correlation (used for Δt estimation)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, Sequence

from .domain import EvidenceClass
from .physics_contract import CoordinateFrame


# Speed of light (m/s) — exact
_C = 299_792_458.0

Vector3 = tuple[float, float, float]


# ---------------------------------------------------------------------------
# Domain contracts
# ---------------------------------------------------------------------------

class SolverConvergenceStatus(str, Enum):
    CONVERGED    = "converged"
    MAX_ITER     = "max_iterations_reached"
    DEGENERATE   = "degenerate_geometry"
    FAILED       = "failed"


@dataclass(frozen=True)
class ReceiverNode:
    """A ground receiver node with known position."""
    node_id: str
    position_m: Vector3                  # ECI or ECEF (specified by frame)
    position_uncertainty_m: float
    frame: CoordinateFrame
    clock_synchronisation_id: str        # identifies the timing reference

    def __post_init__(self) -> None:
        if not self.node_id or not self.clock_synchronisation_id:
            raise ValueError("node_id and clock_synchronisation_id are required")
        if self.position_uncertainty_m < 0:
            raise ValueError("position uncertainty must be non-negative")

    def distance_to(self, point: Vector3) -> float:
        """Euclidean distance from this node to a 3D point (m)."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.position_m, point)))


@dataclass(frozen=True)
class TdoaMeasurement:
    """One TDOA measurement between a pair of receiver nodes.

    Δt = t_j - t_i (positive means signal arrived at j after i)
    """
    measurement_id: str
    node_i_id: str
    node_j_id: str
    tdoa_s: float               # Δt_{ij} = t_j - t_i (seconds)
    uncertainty_s: float        # 1-sigma timing uncertainty
    correlation_snr_db: float   # SNR of the cross-correlation peak
    algorithm_id: str           # cross-correlation algorithm used
    evidence_class: EvidenceClass

    def __post_init__(self) -> None:
        if not self.measurement_id:
            raise ValueError("measurement_id is required")
        if self.uncertainty_s <= 0:
            raise ValueError("timing uncertainty must be positive")
        if self.node_i_id == self.node_j_id:
            raise ValueError("TDOA measurement requires two distinct nodes")

    @property
    def range_difference_m(self) -> float:
        """Convert TDOA to range difference: Δr = c × Δt."""
        return _C * self.tdoa_s

    @property
    def range_difference_uncertainty_m(self) -> float:
        return _C * self.uncertainty_s


@dataclass(frozen=True)
class TdoaSolution:
    """Position estimate from TDOA solver with full uncertainty characterisation."""
    solution_id: str
    position_m: Vector3
    velocity_m_s: Vector3 | None        # estimated if Doppler shifts available; else None
    covariance_m2: tuple[float, ...]    # 3×3 flattened position covariance (m²)
    position_uncertainty_m: float       # 1-sigma marginal (sqrt of trace/3)
    residuals_m: tuple[float, ...]      # one residual per measurement
    rms_residual_m: float
    n_measurements: int
    n_iterations: int
    convergence_status: SolverConvergenceStatus
    solver_id: str
    frame: CoordinateFrame
    evidence_class: EvidenceClass
    limitation: str

    def __post_init__(self) -> None:
        if not self.solution_id or not self.limitation:
            raise ValueError("solution_id and limitation are required")
        if len(self.covariance_m2) != 9:
            raise ValueError("covariance_m2 must have 9 elements (3×3 flattened)")

    @property
    def is_valid(self) -> bool:
        return self.convergence_status == SolverConvergenceStatus.CONVERGED

    @property
    def horizontal_uncertainty_m(self) -> float:
        """1-sigma horizontal (x-y plane) uncertainty."""
        # sqrt( (σ_xx + σ_yy) / 2 )
        c = self.covariance_m2
        return math.sqrt((c[0] + c[4]) / 2.0)

    def to_dict(self) -> dict:
        return {
            "solution_id": self.solution_id,
            "position_m": list(self.position_m),
            "position_uncertainty_m": self.position_uncertainty_m,
            "rms_residual_m": self.rms_residual_m,
            "n_measurements": self.n_measurements,
            "convergence": self.convergence_status.value,
            "evidence_class": self.evidence_class.value,
            "limitation": self.limitation,
        }


# ---------------------------------------------------------------------------
# 3×3 matrix operations (pure Python)
# ---------------------------------------------------------------------------

def _mat3x3_add(A: list[float], B: list[float]) -> list[float]:
    return [a + b for a, b in zip(A, B)]

def _mat3x3_mult(A: list[float], B: list[float]) -> list[float]:
    C = [0.0] * 9
    for i in range(3):
        for j in range(3):
            C[i * 3 + j] = sum(A[i * 3 + k] * B[k * 3 + j] for k in range(3))
    return C

def _mat3x3_transpose(A: list[float]) -> list[float]:
    return [A[j * 3 + i] for i in range(3) for j in range(3)]

def _mat3x3_det(A: list[float]) -> float:
    a = A
    return (a[0] * (a[4]*a[8] - a[5]*a[7])
          - a[1] * (a[3]*a[8] - a[5]*a[6])
          + a[2] * (a[3]*a[7] - a[4]*a[6]))

def _mat3x3_inv(A: list[float]) -> list[float]:
    det = _mat3x3_det(A)
    if abs(det) < 1e-30:
        raise ValueError("Matrix is singular — degenerate receiver geometry")
    a = A
    inv = [
         (a[4]*a[8]-a[5]*a[7])/det, -(a[1]*a[8]-a[2]*a[7])/det,  (a[1]*a[5]-a[2]*a[4])/det,
        -(a[3]*a[8]-a[5]*a[6])/det,  (a[0]*a[8]-a[2]*a[6])/det, -(a[0]*a[5]-a[2]*a[3])/det,
         (a[3]*a[7]-a[4]*a[6])/det, -(a[0]*a[7]-a[1]*a[6])/det,  (a[0]*a[4]-a[1]*a[3])/det,
    ]
    return inv

def _matvec3(A: list[float], v: list[float]) -> list[float]:
    return [sum(A[i*3+k]*v[k] for k in range(3)) for i in range(3)]

def _vec3_add(a: list[float], b: list[float]) -> list[float]:
    return [x + y for x, y in zip(a, b)]

def _vec3_norm(v: list[float]) -> float:
    return math.sqrt(sum(x**2 for x in v))


# ---------------------------------------------------------------------------
# Protocol interface
# ---------------------------------------------------------------------------

class TdoaSolver(Protocol):
    """Interface for TDOA position solvers.

    Implement this to substitute any solver (Fang closed-form, ML, MCMC)
    without changing the pipeline.
    """
    solver_id: str

    def solve(
        self,
        measurements: Sequence[TdoaMeasurement],
        nodes: Sequence[ReceiverNode],
        initial_guess: Vector3,
        frame: CoordinateFrame,
    ) -> TdoaSolution:
        ...


# ---------------------------------------------------------------------------
# Gauss-Newton iterative solver
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GaussNewtonTdoaSolver:
    """Iterative TDOA solver using Gauss-Newton least squares.

    Linearises the hyperbolic measurement model around the current estimate
    and refines iteratively until convergence.

    Convergence criterion: ‖Δp‖ < tolerance_m
    Typical convergence: 5–10 iterations at 1 m tolerance.
    """
    solver_id: str = "gauss_newton_tdoa_v1"
    max_iterations: int = 50
    tolerance_m: float = 1.0
    regularisation: float = 1e-6   # Tikhonov regularisation for ill-conditioned geometry

    def solve(
        self,
        measurements: Sequence[TdoaMeasurement],
        nodes: Sequence[ReceiverNode],
        initial_guess: Vector3,
        frame: CoordinateFrame,
    ) -> TdoaSolution:
        if len(measurements) < 1:
            raise ValueError("at least one TDOA measurement required")
        if len(nodes) < 2:
            raise ValueError("at least two receiver nodes required")

        node_map = {n.node_id: n for n in nodes}

        # Build index pairs — each measurement corresponds to one hyperbola
        pairs: list[tuple[ReceiverNode, ReceiverNode, TdoaMeasurement]] = []
        for m in measurements:
            ni = node_map.get(m.node_i_id)
            nj = node_map.get(m.node_j_id)
            if ni is None or nj is None:
                continue
            pairs.append((ni, nj, m))

        if not pairs:
            return self._failed_solution(frame)

        # Iterative Gauss-Newton
        p = list(initial_guess)
        n_iter = 0
        status = SolverConvergenceStatus.MAX_ITER

        for iteration in range(self.max_iterations):
            n_iter = iteration + 1
            J: list[list[float]] = []  # Jacobian rows
            r: list[float] = []        # residuals
            W: list[float] = []        # weights (1 / uncertainty²)

            for ni, nj, m in pairs:
                ri_m = ni.distance_to(tuple(p))  # type: ignore[arg-type]
                rj_m = nj.distance_to(tuple(p))  # type: ignore[arg-type]

                # Predicted range difference
                pred_dr = rj_m - ri_m
                # Measured range difference
                meas_dr = _C * m.tdoa_s
                # Residual
                res = meas_dr - pred_dr
                r.append(res)

                # Jacobian: ∂(r_j - r_i)/∂p = (p - r_j)/r_j - (p - r_i)/r_i
                grad = [(p[k] - nj.position_m[k]) / max(rj_m, 1e-3)
                      - (p[k] - ni.position_m[k]) / max(ri_m, 1e-3)
                        for k in range(3)]
                J.append(grad)
                W.append(1.0 / max(m.uncertainty_s ** 2, 1e-20))

            # Build J^T W J  and J^T W r  (3×3 and 3×1)
            JtWJ = [0.0] * 9
            JtWr = [0.0] * 3
            for k, (jrow, res, w) in enumerate(zip(J, r, W)):
                for i in range(3):
                    JtWr[i] += jrow[i] * res * w
                    for j in range(3):
                        JtWJ[i * 3 + j] += jrow[i] * jrow[j] * w

            # Tikhonov regularisation: JtWJ += λI
            for i in range(3):
                JtWJ[i * 3 + i] += self.regularisation

            try:
                JtWJ_inv = _mat3x3_inv(JtWJ)
            except ValueError:
                status = SolverConvergenceStatus.DEGENERATE
                break

            dp = _matvec3(JtWJ_inv, JtWr)
            p = _vec3_add(p, dp)

            if _vec3_norm(dp) < self.tolerance_m:
                status = SolverConvergenceStatus.CONVERGED
                break

        # Compute final residuals and covariance
        final_residuals = []
        for ni, nj, m in pairs:
            ri_m = ni.distance_to(tuple(p))  # type: ignore[arg-type]
            rj_m = nj.distance_to(tuple(p))  # type: ignore[arg-type]
            pred = rj_m - ri_m
            meas = _C * m.tdoa_s
            final_residuals.append(meas - pred)

        rms = math.sqrt(sum(r ** 2 for r in final_residuals) / max(len(final_residuals), 1))

        # Covariance: Σ = (J^T W J)^{-1} × σ²_noise
        # Use mean timing uncertainty as noise level
        mean_sigma_t = sum(m.uncertainty_s for m in measurements) / max(len(measurements), 1)
        mean_sigma_r = _C * mean_sigma_t
        JtWJ_regular = [v for v in JtWJ]
        try:
            cov = [v * mean_sigma_r ** 2 for v in _mat3x3_inv(JtWJ_regular)]
        except ValueError:
            cov = [1e12] * 9

        pos_unc = math.sqrt(sum(cov[i * 3 + i] for i in range(3)) / 3.0)

        solution_id = "tdoa-" + sha256(
            f"{tuple(p)}{n_iter}".encode()
        ).hexdigest()[:10]

        return TdoaSolution(
            solution_id=solution_id,
            position_m=tuple(p),  # type: ignore[arg-type]
            velocity_m_s=None,
            covariance_m2=tuple(cov),
            position_uncertainty_m=pos_unc,
            residuals_m=tuple(final_residuals),
            rms_residual_m=rms,
            n_measurements=len(pairs),
            n_iterations=n_iter,
            convergence_status=status,
            solver_id=self.solver_id,
            frame=frame,
            evidence_class=EvidenceClass.SYNTHETIC,
            limitation=(
                "Gauss-Newton linearised TDOA solver. Accuracy limited by timing "
                "synchronisation uncertainty and receiver geometry. "
                "Assumes straight-line (free-space) propagation. "
                "Ionospheric refraction and multi-path not modelled. "
                "Results are EvidenceClass.SYNTHETIC until real measurements are made."
            ),
        )

    def _failed_solution(self, frame: CoordinateFrame) -> TdoaSolution:
        return TdoaSolution(
            solution_id="tdoa-failed",
            position_m=(0.0, 0.0, 0.0),
            velocity_m_s=None,
            covariance_m2=tuple([1e12] * 9),
            position_uncertainty_m=1e6,
            residuals_m=(),
            rms_residual_m=float("inf"),
            n_measurements=0,
            n_iterations=0,
            convergence_status=SolverConvergenceStatus.FAILED,
            solver_id=self.solver_id,
            frame=frame,
            evidence_class=EvidenceClass.SYNTHETIC,
            limitation="Solver failed — insufficient measurements or incompatible node IDs.",
        )


# ---------------------------------------------------------------------------
# Geometric dilution of precision (GDOP)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GeometryAssessment:
    """Assessment of receiver array geometry quality for TDOA."""
    gdop: float                  # Geometric Dilution of Precision
    hdop: float                  # Horizontal DOP
    vdop: float                  # Vertical DOP
    baseline_km: float           # maximum inter-node baseline
    n_nodes: int
    is_well_conditioned: bool    # GDOP < 5 is generally considered good


def assess_geometry(
    nodes: Sequence[ReceiverNode],
    source_position: Vector3,
) -> GeometryAssessment:
    """Compute GDOP for the given receiver geometry and source position."""
    if len(nodes) < 2:
        return GeometryAssessment(gdop=1e6, hdop=1e6, vdop=1e6,
                                   baseline_km=0.0, n_nodes=len(nodes),
                                   is_well_conditioned=False)

    # Build H matrix (unit vectors from source to each node)
    H: list[list[float]] = []
    for node in nodes:
        d = [node.position_m[k] - source_position[k] for k in range(3)]
        dist = max(math.sqrt(sum(x**2 for x in d)), 1.0)
        H.append([d[k] / dist for k in range(3)])

    # G = (H^T H)^{-1}
    HtH = [0.0] * 9
    for row in H:
        for i in range(3):
            for j in range(3):
                HtH[i * 3 + j] += row[i] * row[j]
    try:
        G = _mat3x3_inv(HtH)
    except ValueError:
        return GeometryAssessment(gdop=1e6, hdop=1e6, vdop=1e6,
                                   baseline_km=0.0, n_nodes=len(nodes),
                                   is_well_conditioned=False)

    gdop = math.sqrt(max(G[0] + G[4] + G[8], 0.0))
    hdop = math.sqrt(max(G[0] + G[4], 0.0))
    vdop = math.sqrt(max(G[8], 0.0))

    # Maximum baseline
    max_b = max(
        math.sqrt(sum((nodes[i].position_m[k] - nodes[j].position_m[k])**2 for k in range(3)))
        for i in range(len(nodes)) for j in range(i + 1, len(nodes))
    ) / 1000.0

    return GeometryAssessment(
        gdop=gdop, hdop=hdop, vdop=vdop,
        baseline_km=max_b, n_nodes=len(nodes),
        is_well_conditioned=gdop < 5.0,
    )
