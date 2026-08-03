"""Estimate fleet-wide cost savings from HEIMDALL debris awareness.

Usage:
    PYTHONPATH=src python3.11 scripts/estimate_cost_savings.py \\
        --output data/local/visualization/cost_savings.json \\
        --generated-at 2026-07-30T00:00:00Z
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from heimdall.cost_savings import (
    CostSavingsCalculator,
    NASA_COMMERCIAL_FLEET,
    REFERENCE_MISSION_COST_PROFILES,
    MissionClass,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate HEIMDALL cost savings")
    parser.add_argument("--output", default="data/local/visualization/cost_savings.json")
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--analysis-period-years", type=int, default=10)
    args = parser.parse_args()

    generated_at = (
        datetime.fromisoformat(args.generated_at).replace(tzinfo=timezone.utc)
        if args.generated_at
        else datetime.now(timezone.utc)
    )

    calculator = CostSavingsCalculator()

    print(f"[estimate_cost_savings] computing {args.analysis_period_years}-year fleet-wide savings")
    scenario = calculator.build_fleetwide_scenario(
        fleet=NASA_COMMERCIAL_FLEET,
        analysis_period_years=args.analysis_period_years,
        generated_at=generated_at,
    )

    print(f"[estimate_cost_savings] annual savings: ${scenario.annual_savings_usd/1e6:.1f}M")
    print(f"[estimate_cost_savings] 10-year total: ${scenario.ten_year_savings_usd/1e6:.0f}M")
    print(f"[estimate_cost_savings] uncertainty range: "
          f"${scenario.uncertainty_low_usd/1e6:.0f}M – "
          f"${scenario.uncertainty_high_usd/1e6:.0f}M")

    print("\n[estimate_cost_savings] per-mission breakdown:")
    for est in scenario.per_mission_estimates:
        print(
            f"  {est.mission_class.value:25s}  "
            f"total={est.total_savings_usd/1e6:6.1f}M  "
            f"(maneuvers={est.avoided_maneuvers_usd/1e6:.1f}M  "
            f"insurance={est.reduced_insurance_usd/1e6:.1f}M  "
            f"delay={est.launch_delay_reduction_usd/1e6:.1f}M)"
        )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scenario.to_dict(), indent=2))
    print(f"\n[estimate_cost_savings] written → {out}")


if __name__ == "__main__":
    main()
