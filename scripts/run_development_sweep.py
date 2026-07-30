"""Run a development-only illustrative synthetic sensitivity sweep."""

from __future__ import annotations

from dataclasses import asdict
from json import dumps

from heimdall.forward_models import IllustrativeBurstSineModel
from heimdall.pipeline import BaselineMatchedFilter, ClockQualityGate, PeakContrastGate
from heimdall.domain import DatasetSplit
from heimdall.simulation import SyntheticScenario
from heimdall.sweeps import SweepAxis, SweepDefinition, run_sweep


def main() -> None:
    definition = SweepDefinition(
        sweep_id="illustrative-amplitude-noise/0.1.0",
        base_scenario=SyntheticScenario(
            scenario_id="development-sweep",
            seed=101,
            signal_amplitude=1.0,
            expected_signal=True,
        ),
        axes=(
            SweepAxis("signal_amplitude", (0.2, 0.5, 1.0)),
            SweepAxis("noise_amplitude", (0.1, 0.2, 0.4)),
        ),
        dataset_split=DatasetSplit.DEVELOPMENT,
        purpose="Development-only interface sensitivity exploration.",
    )
    report = run_sweep(
        definition,
        BaselineMatchedFilter(),
        (PeakContrastGate(), ClockQualityGate()),
        IllustrativeBurstSineModel(),
    )
    print(dumps({
        "scientific_status": (
            "SYNTHETIC DEVELOPMENT-ONLY SENSITIVITY FIXTURE — "
            "NOT A PHYSICS OR FLIGHT-PERFORMANCE RESULT"
        ),
        "report": asdict(report),
    }, indent=2))


if __name__ == "__main__":
    main()

