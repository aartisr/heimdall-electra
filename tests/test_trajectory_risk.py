"""Tests for trajectory_risk module."""
import math
import unittest
from datetime import datetime, timezone

from heimdall.trajectory_risk import (
    AscentType,
    LaunchProfile,
    RiskLevel,
    TrajectoryRiskEngine,
    REFERENCE_LAUNCH_PROFILES,
    _poisson_collision_probability,
    _classify_risk,
)
from heimdall.debris_population import PopulationModelConfig, SyntheticPowerLawModel
from heimdall.domain import EvidenceClass


def _make_population():
    model = SyntheticPowerLawModel()
    config = PopulationModelConfig(altitude_bin_km=100.0, inclination_bin_deg=30.0)
    return model.build_snapshot(config, datetime(2026, 7, 30, tzinfo=timezone.utc))


class TestPoissonModel(unittest.TestCase):

    def test_zero_flux_gives_zero_probability(self):
        p = _poisson_collision_probability(0, 10, 5)
        self.assertAlmostEqual(p, 0.0)

    def test_high_flux_approaches_one(self):
        p = _poisson_collision_probability(1e6, 100, 100)
        self.assertGreater(p, 0.999)

    def test_probability_in_unit_interval(self):
        p = _poisson_collision_probability(1e-5, 10, 5)
        self.assertGreaterEqual(p, 0.0)
        self.assertLessEqual(p, 1.0)

    def test_longer_mission_increases_probability(self):
        p1 = _poisson_collision_probability(1e-5, 10, 1)
        p2 = _poisson_collision_probability(1e-5, 10, 10)
        self.assertGreater(p2, p1)

    def test_larger_cross_section_increases_probability(self):
        p1 = _poisson_collision_probability(1e-5, 1, 5)
        p2 = _poisson_collision_probability(1e-5, 100, 5)
        self.assertGreater(p2, p1)


class TestRiskClassification(unittest.TestCase):

    def test_very_low(self):
        self.assertEqual(_classify_risk(1e-6), RiskLevel.VERY_LOW)

    def test_low(self):
        self.assertEqual(_classify_risk(5e-5), RiskLevel.LOW)

    def test_moderate(self):
        self.assertEqual(_classify_risk(5e-4), RiskLevel.MODERATE)

    def test_high(self):
        self.assertEqual(_classify_risk(5e-3), RiskLevel.HIGH)

    def test_very_high(self):
        self.assertEqual(_classify_risk(0.05), RiskLevel.VERY_HIGH)


class TestLaunchProfile(unittest.TestCase):

    def test_valid_profile(self):
        p = LaunchProfile(
            profile_id="test", target_altitude_km=400,
            target_inclination_deg=51.6, raan_deg=0,
            ascent_type=AscentType.DIRECT,
            spacecraft_cross_section_m2=10, mission_duration_years=1,
        )
        self.assertEqual(p.profile_id, "test")

    def test_negative_altitude_raises(self):
        with self.assertRaises(ValueError):
            LaunchProfile(
                profile_id="test", target_altitude_km=-100,
                target_inclination_deg=51.6, raan_deg=0,
                ascent_type=AscentType.DIRECT,
                spacecraft_cross_section_m2=10, mission_duration_years=1,
            )

    def test_zero_cross_section_raises(self):
        with self.assertRaises(ValueError):
            LaunchProfile(
                profile_id="test", target_altitude_km=400,
                target_inclination_deg=51.6, raan_deg=0,
                ascent_type=AscentType.DIRECT,
                spacecraft_cross_section_m2=0, mission_duration_years=1,
            )


class TestTrajectoryRiskEngine(unittest.TestCase):

    def setUp(self):
        self.population = _make_population()
        self.engine = TrajectoryRiskEngine()
        self.generated_at = datetime(2026, 7, 30, tzinfo=timezone.utc)

    def test_report_has_risk_field(self):
        report = self.engine.build_risk_report(
            self.population, REFERENCE_LAUNCH_PROFILES,
            generated_at=self.generated_at,
        )
        self.assertGreater(len(report.risk_field), 0)

    def test_report_scores_all_profiles(self):
        report = self.engine.build_risk_report(
            self.population, REFERENCE_LAUNCH_PROFILES,
            generated_at=self.generated_at,
        )
        self.assertEqual(len(report.profile_scores), len(REFERENCE_LAUNCH_PROFILES))

    def test_all_probabilities_in_unit_interval(self):
        report = self.engine.build_risk_report(
            self.population, REFERENCE_LAUNCH_PROFILES,
            generated_at=self.generated_at,
        )
        for score in report.profile_scores:
            self.assertGreaterEqual(score.cumulative_collision_probability, 0)
            self.assertLessEqual(score.cumulative_collision_probability, 1)

    def test_full_population_risk_geq_tracked_only(self):
        """Full population must always have >= risk than tracked-only."""
        report = self.engine.build_risk_report(
            self.population, REFERENCE_LAUNCH_PROFILES,
            generated_at=self.generated_at,
        )
        for score in report.profile_scores:
            self.assertGreaterEqual(
                score.collision_probability_full_population,
                score.collision_probability_tracked_only,
                f"{score.profile_id}: full risk must be >= tracked-only risk",
            )

    def test_dark_risk_fraction_in_unit_interval(self):
        report = self.engine.build_risk_report(
            self.population, REFERENCE_LAUNCH_PROFILES,
            generated_at=self.generated_at,
        )
        for score in report.profile_scores:
            self.assertGreaterEqual(score.dark_risk_fraction, 0.0)
            self.assertLessEqual(score.dark_risk_fraction, 1.0)

    def test_evidence_class_is_synthetic(self):
        report = self.engine.build_risk_report(
            self.population, REFERENCE_LAUNCH_PROFILES,
            generated_at=self.generated_at,
        )
        self.assertEqual(report.evidence_class, EvidenceClass.SYNTHETIC)
        for score in report.profile_scores:
            self.assertEqual(score.evidence_class, EvidenceClass.SYNTHETIC)

    def test_limitation_strings_present(self):
        report = self.engine.build_risk_report(
            self.population, REFERENCE_LAUNCH_PROFILES,
            generated_at=self.generated_at,
        )
        self.assertTrue(report.limitation)
        for score in report.profile_scores:
            self.assertTrue(score.limitation)

    def test_safe_corridors_all_below_threshold(self):
        threshold = 1e-4
        report = self.engine.build_risk_report(
            self.population, REFERENCE_LAUNCH_PROFILES,
            risk_threshold=threshold,
            generated_at=self.generated_at,
        )
        for corridor in report.safe_corridors:
            self.assertLess(corridor.max_collision_probability, threshold)

    def test_to_dict_roundtrip(self):
        report = self.engine.build_risk_report(
            self.population, REFERENCE_LAUNCH_PROFILES,
            generated_at=self.generated_at,
        )
        d = report.to_dict()
        self.assertIn("risk_field", d)
        self.assertIn("profile_scores", d)
        self.assertIn("safe_corridors", d)
        self.assertEqual(d["evidence_class"], "synthetic")


class TestReferenceLaunchProfiles(unittest.TestCase):

    def test_all_profiles_have_positive_altitude(self):
        for p in REFERENCE_LAUNCH_PROFILES:
            self.assertGreater(p.target_altitude_km, 0)

    def test_all_profiles_have_valid_inclination(self):
        for p in REFERENCE_LAUNCH_PROFILES:
            self.assertGreaterEqual(p.target_inclination_deg, 0)
            self.assertLessEqual(p.target_inclination_deg, 180)


if __name__ == "__main__":
    unittest.main()
