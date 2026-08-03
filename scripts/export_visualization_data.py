"""Bundle all visualization data exports for the analyst console.

Runs all four visualization pipeline stages and writes outputs to
apps/analyst-console/public/ for immediate frontend consumption.

Usage:
    PYTHONPATH=src python3.11 scripts/export_visualization_data.py \\
        --generated-at 2026-07-30T00:00:00Z \\
        --output-dir   apps/analyst-console/public
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from heimdall.debris_population import PopulationModelConfig, SyntheticPowerLawModel
from heimdall.radar_detectability import RadarDetectabilityAnalyzer
from heimdall.trajectory_risk import TrajectoryRiskEngine, REFERENCE_LAUNCH_PROFILES
from heimdall.cost_savings import CostSavingsCalculator, NASA_COMMERCIAL_FLEET
from heimdall.audit_bundle import build_audit_bundle, write_audit_bundle
from heimdall.domain import EvidenceClass


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    size_kb = path.stat().st_size / 1024
    print(f"  ✓  {path}  ({size_kb:.1f} KB)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export all visualization data")
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--output-dir", default="apps/analyst-console/public")
    parser.add_argument("--audit-bundle", default="data/local/visualization/viz-audit.json")
    args = parser.parse_args()

    generated_at = (
        datetime.fromisoformat(args.generated_at).replace(tzinfo=timezone.utc)
        if args.generated_at
        else datetime.now(timezone.utc)
    )
    out_dir = Path(args.output_dir)

    print(f"\n[export_visualization_data] generated_at={generated_at.isoformat()}")
    print(f"[export_visualization_data] output_dir={out_dir}\n")

    # -----------------------------------------------------------------------
    # Stage 1 — Debris population
    # -----------------------------------------------------------------------
    print("Stage 1 — Debris population model")
    model = SyntheticPowerLawModel()
    config = PopulationModelConfig()
    population = model.build_snapshot(config, generated_at)
    print(
        f"  tracked={population.total_tracked_objects:,}  "
        f"sub_cm={population.estimated_sub_cm_total:,}  "
        f"clouds={len(population.clouds)}  "
        f"shells={len(population.shells)}"
    )
    _write(out_dir / "debris_population.json", population.to_dict())

    # -----------------------------------------------------------------------
    # Stage 2 — RCS / radar detection gap
    # -----------------------------------------------------------------------
    print("\nStage 2 — Radar detection gap analysis")
    analyzer = RadarDetectabilityAnalyzer()
    gap_analysis = analyzer.build_gap_analysis(generated_at)
    print(
        f"  gap={gap_analysis.gap_min_diameter_m*1000:.1f}mm – "
        f"{gap_analysis.gap_max_diameter_m*100:.1f}cm  "
        f"undetected={gap_analysis.undetected_population_fraction:.0%}"
    )
    _write(out_dir / "rcs_analysis.json", gap_analysis.to_dict())

    # -----------------------------------------------------------------------
    # Stage 3 — Trajectory risk
    # -----------------------------------------------------------------------
    print("\nStage 3 — Trajectory risk field")
    engine = TrajectoryRiskEngine()
    risk_report = engine.build_risk_report(
        population=population,
        profiles=REFERENCE_LAUNCH_PROFILES,
        generated_at=generated_at,
    )
    print(
        f"  cells={len(risk_report.risk_field)}  "
        f"profiles={len(risk_report.profile_scores)}  "
        f"corridors={len(risk_report.safe_corridors)}"
    )
    _write(out_dir / "risk_field.json", risk_report.to_dict())

    # -----------------------------------------------------------------------
    # Stage 4 — Cost savings
    # -----------------------------------------------------------------------
    print("\nStage 4 — Fleet-wide cost savings")
    calculator = CostSavingsCalculator()
    savings = calculator.build_fleetwide_scenario(
        fleet=NASA_COMMERCIAL_FLEET,
        generated_at=generated_at,
    )
    print(
        f"  annual=${savings.annual_savings_usd/1e6:.1f}M  "
        f"10yr=${savings.ten_year_savings_usd/1e6:.0f}M  "
        f"range=${savings.uncertainty_low_usd/1e6:.0f}M–${savings.uncertainty_high_usd/1e6:.0f}M"
    )
    _write(out_dir / "cost_savings.json", savings.to_dict())

    # -----------------------------------------------------------------------
    # Write combined index
    # -----------------------------------------------------------------------
    index = {
        "generated_at": generated_at.isoformat(),
        "evidence_class": EvidenceClass.SYNTHETIC.value,
        "limitation": (
            "All visualization data is synthetic modelled output. "
            "No physical debris detection, radar measurement, or cost saving "
            "has been observed. Results are for research planning only."
        ),
        "files": {
            "debris_population": "debris_population.json",
            "rcs_analysis": "rcs_analysis.json",
            "risk_field": "risk_field.json",
            "cost_savings": "cost_savings.json",
        },
        "summary": {
            "total_tracked_objects": population.total_tracked_objects,
            "estimated_sub_cm_total": population.estimated_sub_cm_total,
            "fragmentation_events": len(population.events),
            "debris_clouds": len(population.clouds),
            "radar_systems_analysed": len(gap_analysis.radar_curves),
            "detection_gap_mm": round(gap_analysis.gap_min_diameter_m * 1000, 2),
            "detection_gap_max_cm": round(gap_analysis.gap_max_diameter_m * 100, 2),
            "safe_corridors": len(risk_report.safe_corridors),
            "annual_savings_usd": round(savings.annual_savings_usd),
            "ten_year_savings_usd": round(savings.ten_year_savings_usd),
        },
    }
    _write(out_dir / "visualization_index.json", index)

    # -----------------------------------------------------------------------
    # Audit bundle
    # -----------------------------------------------------------------------
    print("\nWriting audit bundle")
    audit_path = Path(args.audit_bundle)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_data = {
        "generated_at": generated_at.isoformat(),
        "stages_completed": ["debris_population", "rcs_analysis", "trajectory_risk", "cost_savings"],
        "evidence_class": EvidenceClass.SYNTHETIC.value,
        "config_artifacts": [
            "config/visualization/debris_population.json",
            "config/visualization/radar_systems.json",
            "config/visualization/trajectory_risk.json",
            "config/visualization/cost_model.json",
        ],
        "output_files": [
            str(out_dir / "debris_population.json"),
            str(out_dir / "rcs_analysis.json"),
            str(out_dir / "risk_field.json"),
            str(out_dir / "cost_savings.json"),
            str(out_dir / "visualization_index.json"),
        ],
    }
    audit_path.write_text(json.dumps(bundle_data, indent=2))
    print(f"  ✓  {audit_path}")

    print(f"\n[export_visualization_data] all outputs written to {out_dir}")
    print(f"[export_visualization_data] open apps/analyst-console and run `npm run dev` to view\n")


if __name__ == "__main__":
    main()
