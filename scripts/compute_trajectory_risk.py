"""Compute trajectory risk field and identify safe launch corridors.

Usage:
    PYTHONPATH=src python3.11 scripts/compute_trajectory_risk.py \\
        --population data/local/visualization/debris_population.json \\
        --output     data/local/visualization/risk_field.json \\
        --generated-at 2026-07-30T00:00:00Z
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from heimdall.debris_population import (
    PopulationModelConfig,
    SyntheticPowerLawModel,
)
from heimdall.trajectory_risk import (
    TrajectoryRiskEngine,
    REFERENCE_LAUNCH_PROFILES,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute trajectory risk field")
    parser.add_argument("--population", default=None,
                        help="Path to pre-built population JSON; if omitted, builds inline")
    parser.add_argument("--output", default="data/local/visualization/risk_field.json")
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--cross-section-m2", type=float, default=10.0)
    parser.add_argument("--mission-duration-years", type=float, default=5.0)
    parser.add_argument("--risk-threshold", type=float, default=1e-4)
    args = parser.parse_args()

    generated_at = (
        datetime.fromisoformat(args.generated_at).replace(tzinfo=timezone.utc)
        if args.generated_at
        else datetime.now(timezone.utc)
    )

    # Build or load population
    if args.population and Path(args.population).exists():
        print(f"[compute_trajectory_risk] population snapshot loading not yet implemented; building inline")

    print("[compute_trajectory_risk] building population snapshot")
    model = SyntheticPowerLawModel()
    config = PopulationModelConfig()
    population = model.build_snapshot(config, generated_at)
    print(f"[compute_trajectory_risk] population: {population.total_tracked_objects:,} tracked, "
          f"{population.estimated_sub_cm_total:,} sub-cm estimate")

    engine = TrajectoryRiskEngine()
    print(f"[compute_trajectory_risk] scoring {len(REFERENCE_LAUNCH_PROFILES)} reference profiles")

    report = engine.build_risk_report(
        population=population,
        profiles=REFERENCE_LAUNCH_PROFILES,
        spacecraft_cross_section_m2=args.cross_section_m2,
        mission_duration_years=args.mission_duration_years,
        risk_threshold=args.risk_threshold,
        generated_at=generated_at,
    )

    print(f"[compute_trajectory_risk] risk field cells: {len(report.risk_field)}")
    print(f"[compute_trajectory_risk] safe corridors identified: {len(report.safe_corridors)}")

    for score in report.profile_scores:
        print(
            f"[compute_trajectory_risk]   {score.profile_id}: "
            f"P={score.cumulative_collision_probability:.2e}  "
            f"dark_risk={score.dark_risk_fraction:.0%}  "
            f"level={score.risk_level.value}"
        )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_dict(), indent=2))
    print(f"[compute_trajectory_risk] written → {out}")


if __name__ == "__main__":
    main()
