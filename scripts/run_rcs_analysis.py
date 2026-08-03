"""Run radar cross-section analysis and export detection gap data.

Usage:
    PYTHONPATH=src python3.11 scripts/run_rcs_analysis.py \\
        --output data/local/visualization/rcs_analysis.json \\
        --generated-at 2026-07-30T00:00:00Z
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from heimdall.radar_detectability import RadarDetectabilityAnalyzer, REFERENCE_RADAR_SYSTEMS


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RCS analysis and build detection gap")
    parser.add_argument("--output", default="data/local/visualization/rcs_analysis.json")
    parser.add_argument("--generated-at", default=None)
    args = parser.parse_args()

    generated_at = (
        datetime.fromisoformat(args.generated_at).replace(tzinfo=timezone.utc)
        if args.generated_at
        else datetime.now(timezone.utc)
    )

    analyzer = RadarDetectabilityAnalyzer()
    print(f"[run_rcs_analysis] computing detection gap for {len(REFERENCE_RADAR_SYSTEMS)} radar systems")

    gap_analysis = analyzer.build_gap_analysis(generated_at)

    for curve in gap_analysis.radar_curves:
        print(
            f"[run_rcs_analysis]   {curve.system.name}: "
            f"min detectable diameter = {curve.min_detectable_diameter_m*100:.1f} cm  "
            f"({len(curve.points)} points)"
        )

    print(
        f"[run_rcs_analysis] detection gap: "
        f"{gap_analysis.gap_min_diameter_m*1000:.1f} mm – "
        f"{gap_analysis.gap_max_diameter_m*100:.1f} cm"
    )
    print(
        f"[run_rcs_analysis] undetected population fraction: "
        f"{gap_analysis.undetected_population_fraction:.0%}"
    )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(gap_analysis.to_dict(), indent=2))
    print(f"[run_rcs_analysis] written → {out}")


if __name__ == "__main__":
    main()
