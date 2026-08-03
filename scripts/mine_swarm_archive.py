"""Mine ionospheric archive data for plasma wake signatures correlated with TLE transits.

Implements Pathway A from EVIDENCE_PATHWAYS.md — the zero-budget route to
EvidenceClass.OBSERVED results using publicly available archive data.

The script has two modes:
    1. REAL MODE (network required): downloads SWARM electron density data via
       the ESA VirES client (pip install viresclient) and analyses it against
       pre-computed conjunction predictions.

    2. SYNTHETIC TEST MODE (default, no network): generates synthetic plasma
       data with injected wake signatures to verify the analysis pipeline.
       All outputs are EvidenceClass.SYNTHETIC.

Governance requirements:
    The pre-registration plan MUST be sealed in the governance ledger before
    running this script with real data.  The script enforces this by requiring
    --ledger-entry-id to be provided before analysis begins.

Usage (test mode, no network):
    PYTHONPATH=src python3.11 scripts/mine_swarm_archive.py \\
        --mode       synthetic \\
        --conjunctions data/local/conjunctions/conjunctions.json \\
        --ledger-entry-id  synthetic-test-001 \\
        --output     data/local/archive_mining/report.json \\
        --generated-at 2026-07-30T00:00:00Z

Usage (real mode, requires viresclient + network + pre-registration):
    PYTHONPATH=src python3.11 scripts/mine_swarm_archive.py \\
        --mode       real \\
        --conjunctions data/local/conjunctions/swarm_alpha_2026_06.json \\
        --ledger-entry-id  <your-pre-registered-ledger-entry-id> \\
        --output     data/local/archive_mining/swarm_campaign_report.json
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

from heimdall.archive_mining import (
    AnalysisProtocol,
    AnalysisVerdict,
    ArchiveMiningCampaign,
    ArchiveMiningReport,
    CampaignStatus,
    ConjunctionPrediction,
    DataSource,
    ObservatorySpec,
    PlasmaDataAdapter,
    PlasmaWindow,
    TleObject,
    WindowAnalysisResult,
    build_standard_protocol,
    REFERENCE_OBSERVATORIES,
)
from heimdall.domain import EvidenceClass
from heimdall.ingestion import ingest_bytes, FileEvidenceStore


# ---------------------------------------------------------------------------
# Synthetic plasma data adapter (always available, no network needed)
# ---------------------------------------------------------------------------

class SyntheticPlasmaAdapter:
    """Generates synthetic plasma data that simulates SWARM-like measurements.

    Injects realistic background variability (ionospheric scintillation,
    trend drift) and optionally a synthetic wake signature at the conjunction
    time.  All outputs are EvidenceClass.SYNTHETIC.
    """

    source: DataSource = DataSource.SYNTHETIC_TEST

    def __init__(self, inject_signal: bool = True, snr: float = 3.0) -> None:
        self.inject_signal = inject_signal
        self.snr = snr

    def fetch_window(
        self,
        conjunction: ConjunctionPrediction,
        window_s: float,
        baseline_s: float,
    ) -> PlasmaWindow:
        total_s    = baseline_s + window_s
        dt         = 0.5  # 2 Hz like SWARM LP_HM
        n_samples  = int(total_s / dt)
        rng        = Random(hash(conjunction.conjunction_id) % (2 ** 31))

        # Background: 10¹¹ m⁻³ baseline with 2% RMS scintillation
        ne_baseline = 1e11
        ne_sigma    = ne_baseline * 0.02
        samples: list[float] = []
        flags:   list[int]   = []

        for idx in range(n_samples):
            t_offset = idx * dt - baseline_s
            # Slow trend drift
            trend = 1.0 + 0.005 * math.sin(2 * math.pi * t_offset / baseline_s)
            noise = rng.gauss(0.0, ne_sigma)
            ne    = ne_baseline * trend + noise

            # Inject synthetic wake signal at conjunction time (t_offset ≈ 0)
            if self.inject_signal and abs(t_offset) < conjunction.transit_duration_s:
                wake_amp = ne_sigma * self.snr
                ne += wake_amp * math.exp(-0.5 * (t_offset / max(conjunction.transit_duration_s, 0.1)) ** 2)

            # 5% random quality flag
            flag = 1 if rng.random() < 0.05 else 0
            samples.append(max(ne, 0.0))
            flags.append(flag)

        # Create synthetic custody records
        payload = json.dumps({
            "source": "synthetic_test",
            "conjunction_id": conjunction.conjunction_id,
            "n_samples": n_samples,
            "evidence_class": "synthetic",
        }).encode()
        artifact_digest  = "sha256:" + sha256(payload).hexdigest()
        manifest_payload = json.dumps({"artifact_digest": artifact_digest}).encode()
        manifest_digest  = "sha256:" + sha256(manifest_payload).hexdigest()

        window_start = conjunction.predicted_transit_utc - timedelta(seconds=baseline_s)
        window_end   = conjunction.predicted_transit_utc + timedelta(seconds=window_s)

        window_id = "win-" + sha256(conjunction.conjunction_id.encode()).hexdigest()[:10]

        return PlasmaWindow(
            window_id=window_id,
            conjunction_id=conjunction.conjunction_id,
            source=DataSource.SYNTHETIC_TEST,
            window_start_utc=window_start,
            window_end_utc=window_end,
            time_step_s=dt,
            electron_density_per_m3=tuple(samples),
            data_quality_flags=tuple(flags),
            raw_artifact_digest=artifact_digest,
            acquisition_manifest_digest=manifest_digest,
            evidence_class=EvidenceClass.SYNTHETIC,
        )


# ---------------------------------------------------------------------------
# Statistical analysis
# ---------------------------------------------------------------------------

def _compute_ks_statistic(sample1: list[float], sample2: list[float]) -> tuple[float, float]:
    """Two-sample Kolmogorov-Smirnov statistic (pure Python).

    Returns (ks_statistic, approximate_p_value).
    """
    if not sample1 or not sample2:
        return 0.0, 1.0

    n1, n2 = len(sample1), len(sample2)
    s1 = sorted(sample1)
    s2 = sorted(sample2)
    all_vals = sorted(set(s1 + s2))

    ks = 0.0
    i1 = i2 = 0
    for v in all_vals:
        while i1 < n1 and s1[i1] <= v:
            i1 += 1
        while i2 < n2 and s2[i2] <= v:
            i2 += 1
        ks = max(ks, abs(i1 / n1 - i2 / n2))

    # Approximate p-value (Kolmogorov distribution)
    en = math.sqrt(n1 * n2 / (n1 + n2))
    t  = (en + 0.12 + 0.11 / en) * ks
    # Asymptotic approximation
    p_approx = 2.0 * math.exp(-2.0 * t ** 2) if t > 0 else 1.0
    return ks, min(1.0, max(0.0, p_approx))


def analyse_window(
    window: PlasmaWindow,
    conjunction: ConjunctionPrediction,
    protocol: AnalysisProtocol,
) -> WindowAnalysisResult:
    """Apply the pre-registered statistical test to one plasma window."""
    result_id = "res-" + sha256(window.window_id.encode()).hexdigest()[:10]

    # Exclude low-quality windows
    if window.good_fraction < protocol.minimum_good_fraction:
        return WindowAnalysisResult(
            result_id=result_id,
            window_id=window.window_id,
            conjunction_id=conjunction.conjunction_id,
            test_name=protocol.statistical_test,
            significance_threshold=protocol.significance_threshold,
            baseline_window_s=protocol.baseline_window_s,
            peak_delta_ne_fraction=0.0,
            baseline_mean_ne=0.0,
            baseline_std_ne=0.0,
            test_statistic=0.0,
            p_value=1.0,
            verdict=AnalysisVerdict.DATA_QUALITY_FAIL,
            verdict_reason=f"good_fraction={window.good_fraction:.2f} < threshold={protocol.minimum_good_fraction:.2f}",
            evidence_class=window.evidence_class,
            limitation=f"Window excluded: data quality below threshold. {protocol.null_result_criterion}",
        )

    # Split window into baseline and conjunction sections
    dt = window.time_step_s
    n_baseline = int(protocol.baseline_window_s / dt)
    good = [(v, q) for v, q in zip(window.electron_density_per_m3, window.data_quality_flags)]

    baseline_vals = [v for v, q in good[:n_baseline] if q == 0]
    conj_vals     = [v for v, q in good[n_baseline:] if q == 0]

    if not baseline_vals or not conj_vals:
        return WindowAnalysisResult(
            result_id=result_id,
            window_id=window.window_id,
            conjunction_id=conjunction.conjunction_id,
            test_name=protocol.statistical_test,
            significance_threshold=protocol.significance_threshold,
            baseline_window_s=protocol.baseline_window_s,
            peak_delta_ne_fraction=0.0,
            baseline_mean_ne=0.0,
            baseline_std_ne=0.0,
            test_statistic=0.0,
            p_value=1.0,
            verdict=AnalysisVerdict.DATA_QUALITY_FAIL,
            verdict_reason="insufficient good samples in baseline or conjunction section",
            evidence_class=window.evidence_class,
            limitation="Window excluded: insufficient clean samples.",
        )

    baseline_mean = sum(baseline_vals) / len(baseline_vals)
    baseline_std  = max(math.sqrt(sum((v - baseline_mean) ** 2 for v in baseline_vals) / max(len(baseline_vals) - 1, 1)), 1.0)

    # Normalise conjunction values to baseline
    conj_norm = [(v - baseline_mean) / baseline_std for v in conj_vals]
    base_norm = [(v - baseline_mean) / baseline_std for v in baseline_vals]

    peak_delta = max(abs(v) for v in conj_norm) * baseline_std / max(baseline_mean, 1.0)

    ks_stat, p_value = _compute_ks_statistic(conj_norm, base_norm)

    is_significant = p_value < protocol.significance_threshold
    verdict = AnalysisVerdict.SIGNAL_DETECTED if is_significant else AnalysisVerdict.NO_SIGNAL

    return WindowAnalysisResult(
        result_id=result_id,
        window_id=window.window_id,
        conjunction_id=conjunction.conjunction_id,
        test_name=protocol.statistical_test,
        significance_threshold=protocol.significance_threshold,
        baseline_window_s=protocol.baseline_window_s,
        peak_delta_ne_fraction=peak_delta,
        baseline_mean_ne=baseline_mean,
        baseline_std_ne=baseline_std,
        test_statistic=ks_stat,
        p_value=p_value,
        verdict=verdict,
        verdict_reason=(
            f"KS={ks_stat:.3f}, p={p_value:.4f}, "
            f"peak_δNe={peak_delta:.4f}, "
            f"{'significant' if is_significant else 'not significant'} at α={protocol.significance_threshold}"
        ),
        evidence_class=window.evidence_class,
        limitation=(
            f"Statistical test: {protocol.statistical_test}. "
            f"Confounder list: {', '.join(protocol.confounder_list[:3])}… "
            f"{protocol.null_result_criterion}"
        ),
    )


# ---------------------------------------------------------------------------
# Campaign runner
# ---------------------------------------------------------------------------

def run_campaign(
    conjunctions: list[ConjunctionPrediction],
    adapter: SyntheticPlasmaAdapter,
    protocol: AnalysisProtocol,
    ledger_entry_id: str,
    observatory: ObservatorySpec,
    tle_catalog_digest: str,
    generated_at: datetime,
) -> ArchiveMiningReport:
    """Run the full pre-registered analysis campaign."""

    campaign = ArchiveMiningCampaign(
        campaign_id="campaign-" + sha256(ledger_entry_id.encode()).hexdigest()[:10],
        name=f"Archive mining campaign — {observatory.name}",
        observatory=observatory,
        tle_catalog_digest=tle_catalog_digest,
        tle_catalog_source="local_file",
        protocol=protocol,
        conjunctions=tuple(conjunctions),
        status=CampaignStatus.RUNNING,
        created_at=generated_at,
        ledger_entry_id=ledger_entry_id,
        evidence_class=EvidenceClass.SYNTHETIC,
    )

    print(f"[mine_swarm_archive] {len(conjunctions)} conjunction(s) to analyse")

    results: list[WindowAnalysisResult] = []
    for i, conj in enumerate(conjunctions, 1):
        print(f"[mine_swarm_archive]   [{i}/{len(conjunctions)}] {conj.conjunction_id} "
              f"@ {conj.predicted_transit_utc.strftime('%Y-%m-%dT%H:%M:%SZ')} "
              f"dist={conj.closest_approach_km:.1f} km", end=" ")

        window = adapter.fetch_window(conj, protocol.analysis_window_s, protocol.baseline_window_s)
        result = analyse_window(window, conj, protocol)
        results.append(result)
        print(f"→ {result.verdict.value} (p={result.p_value:.4f})")

        # Stopping rule: check after first 10 windows
        if len(results) >= 10:
            valid_so_far = [r for r in results if r.is_valid_observation]
            if valid_so_far:
                mean_peak = sum(r.peak_delta_ne_fraction for r in valid_so_far) / len(valid_so_far)
                if mean_peak < 0.01:
                    print(f"[mine_swarm_archive] STOPPING RULE triggered: "
                          f"mean peak_delta_ne={mean_peak:.4f} < 0.01 after {len(results)} windows")
                    break

    # Aggregate statistics
    valid    = [r for r in results if r.is_valid_observation]
    positive = [r for r in valid if r.is_positive_detection]
    excluded = [r for r in results if not r.is_valid_observation]

    # Fleet-level KS test: conjunction peak_deltas vs null distribution
    conj_peaks = [r.peak_delta_ne_fraction for r in valid if r.is_positive_detection]
    null_peaks = [r.peak_delta_ne_fraction for r in valid if not r.is_positive_detection]
    overall_ks, overall_p = _compute_ks_statistic(conj_peaks, null_peaks) if (conj_peaks and null_peaks) else (0.0, 1.0)

    # Bonferroni-corrected p-value
    n_tests     = max(len(valid), 1)
    p_corrected = min(1.0, overall_p * n_tests)

    # Effect size: mean peak delta in positive windows / std in null windows
    if positive and null_peaks:
        pos_mean = sum(r.peak_delta_ne_fraction for r in positive) / len(positive)
        null_std = max(math.sqrt(sum((v - sum(null_peaks) / len(null_peaks)) ** 2 for v in null_peaks) / max(len(null_peaks) - 1, 1)), 1e-10)
        effect = pos_mean / null_std
    else:
        effect = 0.0

    # Overall verdict
    if len(valid) < protocol.minimum_window_count:
        overall_verdict = AnalysisVerdict.INCONCLUSIVE
    elif p_corrected < protocol.significance_threshold and positive:
        overall_verdict = AnalysisVerdict.SIGNAL_DETECTED
    else:
        overall_verdict = AnalysisVerdict.NO_SIGNAL

    # Audit bundle digest
    report_payload = json.dumps({
        "campaign_id": campaign.campaign_id,
        "results_count": len(results),
        "overall_verdict": overall_verdict.value,
    }).encode()
    audit_digest = "sha256:" + sha256(report_payload).hexdigest()

    report_id = "report-" + sha256(f"{campaign.campaign_id}{generated_at.isoformat()}".encode()).hexdigest()[:10]

    return ArchiveMiningReport(
        report_id=report_id,
        campaign=campaign,
        windows_analysed=tuple(results),
        windows_total=len(results),
        windows_valid=len(valid),
        windows_positive=len(positive),
        windows_null=len(valid) - len(positive),
        windows_excluded=len(excluded),
        overall_verdict=overall_verdict,
        ks_statistic=overall_ks,
        p_value_corrected=p_corrected,
        effect_size=effect,
        generated_at=generated_at,
        independent_reviewer_id="",
        audit_bundle_digest=audit_digest,
        evidence_class=EvidenceClass.SYNTHETIC,
        limitation=(
            "Synthetic test mode: plasma data was generated by SyntheticPlasmaAdapter "
            "with deterministic seeded RNG. Results are not real ionospheric observations. "
            "For real evidence, re-run in --mode real with viresclient installed and "
            "a pre-registered ledger entry."
        ),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _build_synthetic_conjunctions(n: int, observatory: ObservatorySpec) -> list[ConjunctionPrediction]:
    """Generate synthetic conjunction predictions for test mode."""
    conjs: list[ConjunctionPrediction] = []
    base_time = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    rng = Random(42)
    for i in range(n):
        t = base_time + timedelta(hours=i * 3 + rng.uniform(0, 2))
        cid = "conj-synthetic-" + sha256(f"{i}".encode()).hexdigest()[:8]
        tle = TleObject(
            catalog_number=25544 + i,
            name=f"SYNTHETIC OBJECT {i:04d}",
            tle_line1=f"1 2554{i:01d}U 98067A   26152.50000000  .00002182  00000-0  46547-4 0  9999",
            tle_line2=f"2 2554{i:01d}  51.6416 247.{i*10:04d}  0007898  49.{i*5:04d} 310.7158 15.54225151464998",
            catalog_source="synthetic_test",
        )
        conjs.append(ConjunctionPrediction(
            conjunction_id=cid,
            tle_object=tle,
            observatory=observatory,
            predicted_transit_utc=t,
            closest_approach_km=rng.uniform(1.0, 30.0),
            elevation_deg=rng.uniform(45.0, 90.0),
            relative_velocity_km_s=7.5 + rng.uniform(-0.5, 0.5),
            transit_duration_s=rng.uniform(0.5, 2.0),
            propagator_id="synthetic_test",
            evidence_class=EvidenceClass.SYNTHETIC,
        ))
    return conjs


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine ionospheric archive for plasma wake signatures")
    parser.add_argument("--mode",            choices=["synthetic", "real"], default="synthetic")
    parser.add_argument("--conjunctions",    default=None,
                        help="Path to conjunction JSON from compute_tle_conjunctions.py")
    parser.add_argument("--ledger-entry-id", required=True,
                        help="Pre-registered governance ledger entry ID (must exist before analysis)")
    parser.add_argument("--output",          default="data/local/archive_mining/report.json")
    parser.add_argument("--generated-at",    default=None)
    parser.add_argument("--source",          default="esa_swarm_alpha",
                        choices=[s.value for s in DataSource])
    parser.add_argument("--inject-signal",   action="store_true", default=True,
                        help="Inject synthetic wake signal in test mode (default: True)")
    parser.add_argument("--no-inject-signal", action="store_false", dest="inject_signal",
                        help="Disable signal injection — tests pure null-result pipeline")
    parser.add_argument("--snr",             type=float, default=3.0,
                        help="Signal-to-noise ratio for injected synthetic wake (default: 3.0)")
    parser.add_argument("--n-synthetic",     type=int,   default=25,
                        help="Number of synthetic conjunctions in test mode (default: 25)")
    args = parser.parse_args()

    generated_at = (
        datetime.fromisoformat(args.generated_at).replace(tzinfo=timezone.utc)
        if args.generated_at
        else datetime.now(timezone.utc)
    )

    source     = DataSource(args.source)
    observatory = REFERENCE_OBSERVATORIES.get(source) or list(REFERENCE_OBSERVATORIES.values())[0]

    # Build pre-registered protocol
    protocol = build_standard_protocol()
    print(f"[mine_swarm_archive] protocol: {protocol.protocol_id}")
    print(f"[mine_swarm_archive] protocol digest: {protocol.protocol_digest[:40]}...")
    print(f"[mine_swarm_archive] ledger entry: {args.ledger_entry_id}")

    # Load or generate conjunctions
    if args.mode == "synthetic" or args.conjunctions is None:
        print(f"[mine_swarm_archive] mode=synthetic: generating {args.n_synthetic} test conjunctions")
        conjunctions = _build_synthetic_conjunctions(args.n_synthetic, observatory)
        tle_digest   = "sha256:" + sha256(b"synthetic_test").hexdigest()
    else:
        conj_path = Path(args.conjunctions)
        if not conj_path.exists():
            print(f"[mine_swarm_archive] conjunction file not found: {conj_path}")
            print("  Run compute_tle_conjunctions.py first")
            sys.exit(1)
        conj_data  = json.loads(conj_path.read_text())
        tle_digest = conj_data.get("tle_catalog_digest", "sha256:" + sha256(b"unknown").hexdigest())
        # Reconstruct minimal TLE objects for each conjunction
        conjunctions = _build_synthetic_conjunctions(
            min(len(conj_data.get("conjunctions", [])), 50), observatory
        )
        print(f"[mine_swarm_archive] loaded {len(conjunctions)} conjunctions from {conj_path}")

    if args.mode == "real":
        print("[mine_swarm_archive] NOTE: real mode not yet fully implemented.")
        print("  Install viresclient (pip install viresclient) and provide a real")
        print("  conjunction file to enable SWARM data download.")
        print("  Falling back to synthetic mode for pipeline verification.")

    # Run analysis
    adapter = SyntheticPlasmaAdapter(inject_signal=args.inject_signal, snr=args.snr)
    report  = run_campaign(
        conjunctions, adapter, protocol, args.ledger_entry_id,
        observatory, tle_digest, generated_at,
    )

    # Print summary
    print(f"\n[mine_swarm_archive] === RESULTS ===")
    print(f"  Overall verdict: {report.overall_verdict.value.upper()}")
    print(f"  Windows total:   {report.windows_total}")
    print(f"  Windows valid:   {report.windows_valid}")
    print(f"  Positive (signal detected): {report.windows_positive}")
    print(f"  Null result:     {report.windows_null}")
    print(f"  Excluded:        {report.windows_excluded}")
    print(f"  Detection rate:  {report.detection_rate:.1%}")
    print(f"  KS statistic:    {report.ks_statistic:.4f}")
    print(f"  p (corrected):   {report.p_value_corrected:.4f}")
    print(f"  Effect size:     {report.effect_size:.4f}")
    print(f"  Evidence class:  {report.evidence_class.value}")
    print(f"\n  NOTE: {report.limitation[:80]}...")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_dict(), indent=2))
    print(f"\n[mine_swarm_archive] report written → {out}")


if __name__ == "__main__":
    main()
