"""Build and export the debris population snapshot.

Usage:
    PYTHONPATH=src python3.11 scripts/build_debris_population.py \\
        --output data/local/visualization/debris_population.json \\
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Build debris population snapshot")
    parser.add_argument("--output", default="data/local/visualization/debris_population.json")
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--altitude-bin-km", type=float, default=50.0)
    parser.add_argument("--inclination-bin-deg", type=float, default=10.0)
    parser.add_argument("--power-law-index", type=float, default=2.5)
    args = parser.parse_args()

    generated_at = (
        datetime.fromisoformat(args.generated_at).replace(tzinfo=timezone.utc)
        if args.generated_at
        else datetime.now(timezone.utc)
    )

    config = PopulationModelConfig(
        altitude_bin_km=args.altitude_bin_km,
        inclination_bin_deg=args.inclination_bin_deg,
        size_power_law_index=args.power_law_index,
    )

    model = SyntheticPowerLawModel()
    print(f"[build_debris_population] building snapshot with model={model.model_id}")
    snapshot = model.build_snapshot(config, generated_at)

    print(f"[build_debris_population] shells={len(snapshot.shells)}")
    print(f"[build_debris_population] clouds={len(snapshot.clouds)}")
    print(f"[build_debris_population] events={len(snapshot.events)}")
    print(f"[build_debris_population] tracked_objects={snapshot.total_tracked_objects:,}")
    print(f"[build_debris_population] sub_cm_estimate={snapshot.estimated_sub_cm_total:,}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot.to_dict(), indent=2))
    print(f"[build_debris_population] written → {out}")


if __name__ == "__main__":
    main()
