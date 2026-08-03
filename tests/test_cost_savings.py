"""Tests for cost_savings module."""
import unittest
from datetime import datetime, timezone

from heimdall.cost_savings import (
    CostSavingsCalculator,
    MissionClass,
    NASA_COMMERCIAL_FLEET,
    REFERENCE_MISSION_COST_PROFILES,
)
from heimdall.domain import EvidenceClass


class TestMissionCostProfile(unittest.TestCase):

    def test_all_reference_profiles_valid(self):
        for mc, profile in REFERENCE_MISSION_COST_PROFILES.items():
            self.assertEqual(profile.mission_class, mc)
            self.assertGreater(profile.spacecraft_value_usd, 0)
            self.assertGreater(profile.annual_operations_cost_usd, 0)
            self.assertTrue(profile.source_reference)

    def test_insurance_cost_computed(self):
        profile = REFERENCE_MISSION_COST_PROFILES[MissionClass.ISS_RESUPPLY]
        expected = profile.spacecraft_value_usd * profile.insurance_premium_fraction
        self.assertAlmostEqual(profile.annual_insurance_cost_usd, expected)

    def test_maneuver_cost_computed(self):
        profile = REFERENCE_MISSION_COST_PROFILES[MissionClass.ISS_RESUPPLY]
        expected = profile.annual_maneuvers_current * profile.maneuver_cost_usd
        self.assertAlmostEqual(profile.annual_maneuver_cost_usd, expected)


class TestCostSavingsCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = CostSavingsCalculator()

    def test_all_mission_classes_produce_estimate(self):
        for mc, profile in REFERENCE_MISSION_COST_PROFILES.items():
            est = self.calculator.estimate_mission_savings(profile)
            self.assertEqual(est.mission_class, mc)

    def test_total_is_sum_of_components(self):
        profile = REFERENCE_MISSION_COST_PROFILES[MissionClass.ISS_RESUPPLY]
        est = self.calculator.estimate_mission_savings(profile)
        expected = (
            est.avoided_maneuvers_usd
            + est.reduced_insurance_usd
            + est.launch_delay_reduction_usd
            + est.propellant_preserved_usd
        )
        self.assertAlmostEqual(est.total_savings_usd, expected, places=0)

    def test_savings_non_negative(self):
        for mc, profile in REFERENCE_MISSION_COST_PROFILES.items():
            est = self.calculator.estimate_mission_savings(profile)
            self.assertGreaterEqual(est.total_savings_usd, 0, f"{mc.value} savings must be >= 0")

    def test_uncertainty_low_less_than_central(self):
        profile = REFERENCE_MISSION_COST_PROFILES[MissionClass.CREWED_LEO]
        est = self.calculator.estimate_mission_savings(profile)
        self.assertLess(est.uncertainty_low_usd, est.total_savings_usd)

    def test_uncertainty_high_greater_than_central(self):
        profile = REFERENCE_MISSION_COST_PROFILES[MissionClass.CREWED_LEO]
        est = self.calculator.estimate_mission_savings(profile)
        self.assertGreater(est.uncertainty_high_usd, est.total_savings_usd)

    def test_evidence_class_is_synthetic(self):
        profile = REFERENCE_MISSION_COST_PROFILES[MissionClass.ISS_RESUPPLY]
        est = self.calculator.estimate_mission_savings(profile)
        self.assertEqual(est.evidence_class, EvidenceClass.SYNTHETIC)

    def test_limitation_string_present(self):
        profile = REFERENCE_MISSION_COST_PROFILES[MissionClass.ISS_RESUPPLY]
        est = self.calculator.estimate_mission_savings(profile)
        self.assertTrue(est.limitation)

    def test_longer_period_gives_higher_savings(self):
        profile = REFERENCE_MISSION_COST_PROFILES[MissionClass.COMMERCIAL_LEO]
        est5 = self.calculator.estimate_mission_savings(profile, 5)
        est10 = self.calculator.estimate_mission_savings(profile, 10)
        self.assertGreater(est10.total_savings_usd, est5.total_savings_usd)

    def test_to_dict_roundtrip(self):
        profile = REFERENCE_MISSION_COST_PROFILES[MissionClass.ISS_RESUPPLY]
        est = self.calculator.estimate_mission_savings(profile)
        d = est.to_dict()
        self.assertEqual(d["evidence_class"], "synthetic")
        self.assertIn("avoided_maneuvers_usd", d)
        self.assertIn("reduced_insurance_usd", d)
        self.assertIn("total_savings_usd", d)
        self.assertIsInstance(d["assumptions"], list)


class TestFleetwideSavings(unittest.TestCase):

    def setUp(self):
        self.calculator = CostSavingsCalculator()
        self.generated_at = datetime(2026, 7, 30, tzinfo=timezone.utc)

    def test_annual_savings_positive(self):
        scenario = self.calculator.build_fleetwide_scenario(
            NASA_COMMERCIAL_FLEET, generated_at=self.generated_at
        )
        self.assertGreater(scenario.annual_savings_usd, 0)

    def test_10yr_equals_10x_annual(self):
        scenario = self.calculator.build_fleetwide_scenario(
            NASA_COMMERCIAL_FLEET, analysis_period_years=10,
            generated_at=self.generated_at,
        )
        self.assertAlmostEqual(
            scenario.ten_year_savings_usd,
            scenario.annual_savings_usd * 10,
            delta=1,
        )

    def test_evidence_class_is_synthetic(self):
        scenario = self.calculator.build_fleetwide_scenario(
            NASA_COMMERCIAL_FLEET, generated_at=self.generated_at
        )
        self.assertEqual(scenario.evidence_class, EvidenceClass.SYNTHETIC)

    def test_limitation_string_present(self):
        scenario = self.calculator.build_fleetwide_scenario(
            NASA_COMMERCIAL_FLEET, generated_at=self.generated_at
        )
        self.assertTrue(scenario.limitation)

    def test_to_dict_roundtrip(self):
        scenario = self.calculator.build_fleetwide_scenario(
            NASA_COMMERCIAL_FLEET, generated_at=self.generated_at
        )
        d = scenario.to_dict()
        self.assertIn("fleet", d)
        self.assertIn("annual_savings_usd", d)
        self.assertIn("ten_year_savings_usd", d)
        self.assertEqual(d["evidence_class"], "synthetic")

    def test_savings_of_order_tens_of_millions_annually(self):
        """Conservative sanity check: fleet-wide annual savings should be $10M–$1B."""
        scenario = self.calculator.build_fleetwide_scenario(
            NASA_COMMERCIAL_FLEET, generated_at=self.generated_at
        )
        self.assertGreater(scenario.annual_savings_usd, 10_000_000)
        self.assertLess(scenario.annual_savings_usd, 1_000_000_000)


if __name__ == "__main__":
    unittest.main()
