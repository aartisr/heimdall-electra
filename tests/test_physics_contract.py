from __future__ import annotations

from datetime import datetime, timezone
import unittest

from heimdall.physics_contract import (
    CoordinateFrame,
    OrbitalState,
    PhysicsModelInput,
    PlasmaEnvironment,
    TargetAssumptions,
    TimeScale,
)


class PhysicsContractTests(unittest.TestCase):
    def test_physics_input_requires_explicit_units_frames_time_and_lineage(self) -> None:
        state = OrbitalState(
            reference_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            time_scale=TimeScale.UTC,
            frame=CoordinateFrame.ECI_J2000,
            position_m=(6_800_000.0, 0.0, 0.0),
            velocity_m_per_s=(0.0, 7_600.0, 0.0),
            state_uncertainty_m=10.0,
        )
        environment = PlasmaEnvironment(
            electron_density_per_m3=1e11,
            ion_density_per_m3=1e11,
            electron_temperature_k=1000.0,
            ion_temperature_k=1000.0,
            magnetic_field_t=(0.0, 0.0, 5e-5),
            environment_source_reference="synthetic environment fixture",
        )
        target = TargetAssumptions(
            target_id="synthetic-target",
            characteristic_length_m=0.005,
            net_charge_c=-1e-12,
            material_assumption="synthetic conductive shard",
            shape_assumption="synthetic sphere-equivalent",
        )
        model_input = PhysicsModelInput(
            "physics-contract-test", state, environment, target,
            "fixture assumptions only",
        )
        self.assertEqual("physics-contract-test", model_input.scenario_id)
        self.assertEqual(CoordinateFrame.ECI_J2000, model_input.state.frame)

    def test_contract_rejects_naive_time_and_invalid_units(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            OrbitalState(
                reference_time=datetime(2026, 1, 1),
                time_scale=TimeScale.UTC,
                frame=CoordinateFrame.ECI_J2000,
                position_m=(0.0, 0.0, 0.0),
                velocity_m_per_s=(0.0, 0.0, 0.0),
                state_uncertainty_m=0.0,
            )
        with self.assertRaisesRegex(ValueError, "positive"):
            PlasmaEnvironment(
                electron_density_per_m3=0.0,
                ion_density_per_m3=1.0,
                electron_temperature_k=1.0,
                ion_temperature_k=1.0,
                magnetic_field_t=(0.0, 0.0, 0.0),
                environment_source_reference="test",
            )


if __name__ == "__main__":
    unittest.main()

