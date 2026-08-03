"""End-to-end Stage 4 demo: multi-node passive sensing pipeline.

Demonstrates the complete pipeline from synthetic observations through
cross-correlation, TDOA solving, and physics interpretation.

Usage:
    PYTHONPATH=src python3.11 scripts/run_multi_node_analysis.py \\
        --n-nodes 4 \\
        --generated-at 2026-07-30T00:00:00Z \\
        --output data/local/multi_node/result.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from heimdall.multi_node_pipeline import MultiNodePipeline, default_pipeline_config
from heimdall.tdoa_solver import ReceiverNode
from heimdall.archive_mining import PlasmaWindow, DataSource
from heimdall.physics_contract import (
    PlasmaEnvironment, OrbitalState, TargetAssumptions,
    CoordinateFrame, TimeScale,
)
from heimdall.domain import EvidenceClass
from heimdall.plasma_wake_model import AnalyticWakeModel


def _make_receiver_array(n_nodes: int, baseline_m: float = 500.0) -> list[ReceiverNode]:
    """Build a circular ground receiver array."""
    nodes = []
    for i in range(n_nodes):
        angle = 2 * math.pi * i / n_nodes
        nodes.append(ReceiverNode(
            node_id=f"RX{i+1:02d}",
            position_m=(baseline_m * math.cos(angle), baseline_m * math.sin(angle), 0.0),
            position_uncertainty_m=5.0,
            frame=CoordinateFrame.ECI_J2000,
            clock_synchronisation_id="gps_utc_ref",
        ))
    return nodes


def _make_synthetic_windows(
    nodes: list[ReceiverNode],
    source_pos: tuple[float, float, float],
    n_samples: int = 1024,
    sample_rate_hz: float = 10_000.0,
    snr: float = 6.0,
    rng_seed: int = 42,
) -> list[PlasmaWindow]:
    """Generate synthetic plasma windows with physically consistent TDOAs.

    NOTE: sample_rate_hz must be >> c / baseline_m to resolve TDOAs.
    For a 500 m baseline, min sample rate = 2 × c / 500 ≈ 1.2 MHz for 1-sample
    resolution.  10 kHz is used for demo speed; real deployments use MHz rates.
    """
    c = 299_792_458.0
    rng = Random(rng_seed)
    windows = []
    base_time = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    baseline_ne = 1e11
    noise_std = baseline_ne * 0.02

    # Compute arrival times at each node (seconds after event at node 0)
    dists = [math.sqrt(sum((source_pos[k] - node.position_m[k])**2 for k in range(3)))
             for node in nodes]
    t_arrivals = [(d - dists[0]) / c for d in dists]

    for node, t_arr in zip(nodes, t_arrivals):
        delay_samples = int(t_arr * sample_rate_hz)
        samples = []
        for i in range(n_samples):
            val = baseline_ne + rng.gauss(0.0, noise_std)
            # Inject Gaussian wake transient at arrival time
            rel = i - (n_samples // 4 + delay_samples)
            if abs(rel) < 30:
                val += noise_std * snr * math.exp(-0.5 * (rel / 8.0)**2)
            samples.append(val)

        art  = "sha256:" + sha256(node.node_id.encode()).hexdigest()
        mfst = "sha256:" + sha256((node.node_id + "manifest").encode()).hexdigest()
        w = PlasmaWindow(
            window_id=f"win-{node.node_id}",
            conjunction_id="conj-demo",
            source=DataSource.SYNTHETIC_TEST,
            window_start_utc=base_time,
            window_end_utc=base_time + timedelta(seconds=n_samples / sample_rate_hz),
            time_step_s=1.0 / sample_rate_hz,
            electron_density_per_m3=tuple(samples),
            data_quality_flags=tuple(0 for _ in samples),
            raw_artifact_digest=art,
            acquisition_manifest_digest=mfst,
            evidence_class=EvidenceClass.SYNTHETIC,
        )
        windows.append(w)
    return windows


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-node passive sensing pipeline demo")
    parser.add_argument("--n-nodes",         type=int,   default=4)
    parser.add_argument("--baseline-m",      type=float, default=1_500.0,
                        help="Array baseline radius (m).")
    parser.add_argument("--source-alt-m",    type=float, default=3_000.0,
                        help="Source altitude above array (m). "
                             "At 1500m baseline, 3000m alt → TDOAs ~ 1-2 µs.")
    parser.add_argument("--source-offset-m", type=float, default=400.0,
                        help="Source horizontal offset from array centre (m)")
    parser.add_argument("--target-size-mm",  type=float, default=10.0)
    parser.add_argument("--snr",             type=float, default=8.0)
    parser.add_argument("--n-samples",       type=int,   default=2048)
    parser.add_argument("--sample-rate-hz",  type=float, default=2_000_000.0,
                        help="Sample rate (Hz). 2 MHz gives 0.5 µs resolution — "
                             "resolves ~1 µs TDOAs from 1.5 km baseline/3 km alt.")
    parser.add_argument("--generated-at",    default=None)
    parser.add_argument("--output",          default="data/local/multi_node/result.json")
    args = parser.parse_args()

    generated_at = (
        datetime.fromisoformat(args.generated_at).replace(tzinfo=timezone.utc)
        if args.generated_at
        else datetime.now(timezone.utc)
    )

    print(f"\n[run_multi_node_analysis] ═══════════════════════════════")
    print(f"  N nodes:         {args.n_nodes}")
    print(f"  Baseline:        {args.baseline_m:.0f} m")
    print(f"  Source altitude: {args.source_alt_m:.0f} m")
    print(f"  Source offset:   {args.source_offset_m:.0f} m")
    print(f"  Sample rate:     {args.sample_rate_hz/1e6:.1f} MHz")
    print(f"  Target diameter: {args.target_size_mm:.1f} mm")
    print(f"  SNR:             {args.snr:.1f} dB")
    print(f"  Evidence class:  SYNTHETIC (no real observations)")
    # Compute expected TDOA for display
    max_tdoa_us = (args.baseline_m / 299_792_458.0) * 1e6
    print(f"  Expected TDOAs:  ~ {max_tdoa_us:.2f} µs → "
          f"~ {max_tdoa_us * args.sample_rate_hz / 1e6:.1f} samples at this rate")

    # Build array and source position
    nodes = _make_receiver_array(args.n_nodes, args.baseline_m)
    source_pos = (args.source_offset_m, 0.0, args.source_alt_m)
    initial_guess = (args.source_offset_m * 0.8, 0.0, args.source_alt_m * 0.9)

    # Generate synthetic observations with correct sample rate for geometry
    sample_rate = args.sample_rate_hz
    windows = _make_synthetic_windows(
        nodes, source_pos, args.n_samples, sample_rate, snr=args.snr,
    )

    # Physics inputs
    plasma = PlasmaEnvironment(
        electron_density_per_m3=1e11,
        ion_density_per_m3=1e11,
        electron_temperature_k=1500.0,
        ion_temperature_k=1200.0,
        magnetic_field_t=(2e-5, 0.0, 0.0),
        environment_source_reference="synthetic_representative_leo_daytime",
    )
    orbital = OrbitalState(
        reference_time=generated_at,
        time_scale=TimeScale.UTC,
        frame=CoordinateFrame.ECI_J2000,
        position_m=source_pos,
        velocity_m_per_s=(0.0, 7_660.0, 0.0),
        state_uncertainty_m=100.0,
    )
    target = TargetAssumptions(
        target_id="synthetic-fragment",
        characteristic_length_m=args.target_size_mm / 1000.0,
        net_charge_c=0.0,
        material_assumption="aluminium_alloy",
        shape_assumption="sphere",
    )

    # Run pipeline
    print(f"\n[run_multi_node_analysis] Running pipeline...")
    pipeline = MultiNodePipeline()
    result   = pipeline.run(windows, nodes, plasma, orbital,
                            initial_guess=initial_guess, target=target,
                            event_time_utc=generated_at)

    # Print results
    print(f"\n[run_multi_node_analysis] ═══ RESULTS ═══════════════════")
    sol = result.tdoa_solution
    err = math.sqrt(sum((sol.position_m[k] - source_pos[k])**2 for k in range(3)))
    print(f"  Convergence:     {sol.convergence_status.value}")
    print(f"  Position (m):    ({sol.position_m[0]:.1f}, {sol.position_m[1]:.1f}, {sol.position_m[2]:.1f})")
    print(f"  Ground truth:    ({source_pos[0]:.1f}, {source_pos[1]:.1f}, {source_pos[2]:.1f})")
    print(f"  Position error:  {err:.1f} m")
    print(f"  Uncertainty:     {sol.position_uncertainty_m:.1f} m (1σ)")
    print(f"  RMS residual:    {sol.rms_residual_m:.1f} m")
    print(f"  GDOP:            {result.geometry_assessment.gdop:.2f}")
    print(f"  Baseline:        {result.geometry_assessment.baseline_km:.1f} km")
    print(f"  Valid pairs:     {result.n_valid_pairs} / {len(result.node_pair_correlations)}")
    print(f"  Overall SNR:     {result.overall_snr_db:.1f} dB")

    if result.wake_prediction:
        wp = result.wake_prediction
        print(f"\n  ─── Wake physics (analytic_unvalidated model) ───")
        print(f"  Fragment D:      {wp.fragment_diameter_m*1000:.1f} mm")
        print(f"  δn/n peak:       {wp.peak_relative_density_perturbation:.2e}")
        print(f"  δn/n (dB):       {wp.peak_perturbation_db:.1f} dB")
        print(f"  Wake length:     {wp.wake_geometry.length_m/1000:.1f} km")
        print(f"  Signal BW:       {wp.signal_bandwidth_hz:.3f} Hz")
        print(f"  Detectable:      {wp.is_detectable_above(0.001)}")

    # Wake model — size scaling table
    print(f"\n[run_multi_node_analysis] ─── Radar vs Wake scaling ─────")
    model = AnalyticWakeModel()
    print(f"  {'D':>12}  {'RCS (dBsm)':>12}  {'Wake (dB)':>10}  {'Gap?':>6}")
    for d_mm in [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0]:
        comp = model.size_scaling_comparison(d_mm/1000.0, plasma, orbital)
        print(f"  {d_mm:>10.1f}mm  {comp.rcs_dbsm_rayleigh:>12.1f}  "
              f"{comp.wake_signal_db:>10.1f}  {'YES' if comp.is_in_detection_gap else 'no':>6}")

    print(f"\n  Evidence class:  {result.evidence_class.value.upper()}")
    print(f"  Limitation:      {result.limitation[:80]}...")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result.to_dict(), indent=2))
    print(f"\n[run_multi_node_analysis] result written → {out}")


if __name__ == "__main__":
    main()
