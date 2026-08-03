"""Tests for radar_detectability module."""
import math
import unittest
from datetime import datetime, timezone

from heimdall.radar_detectability import (
    RadarSystem,
    RcsPoint,
    ScatteringRegime,
    RadarDetectabilityAnalyzer,
    REFERENCE_RADAR_SYSTEMS,
    compute_rcs_sphere,
    rcs_to_dbsm,
    compute_wake_relative_signal_db,
    _classify_regime,
)
from heimdall.domain import EvidenceClass


class TestRegimeClassification(unittest.TestCase):

    def test_sub_mm_is_rayleigh_for_all_radars(self):
        for radar in REFERENCE_RADAR_SYSTEMS:
            regime = _classify_regime(0.001, radar.wavelength_m)
            self.assertEqual(regime, ScatteringRegime.RAYLEIGH,
                             f"{radar.system_id}: 1mm should be Rayleigh")

    def test_large_object_is_optical(self):
        regime = _classify_regime(1.0, 0.03)   # 1 m at 10 GHz
        self.assertEqual(regime, ScatteringRegime.OPTICAL)

    def test_resonance_region(self):
        regime = _classify_regime(0.03, 0.03)  # D ≈ λ
        self.assertEqual(regime, ScatteringRegime.MIE)


class TestRcsComputation(unittest.TestCase):

    def test_optical_regime_equals_geometric(self):
        d = 1.0    # 1 m diameter
        lam = 0.001  # 1 mm wavelength — deep optical
        rcs = compute_rcs_sphere(d, lam)
        expected = math.pi * (d / 2) ** 2
        self.assertAlmostEqual(rcs, expected, places=3)

    def test_rayleigh_scales_as_d6(self):
        """Doubling D in Rayleigh regime should increase RCS by 64× (D⁶)."""
        lam = 0.225  # Space Fence L-band
        rcs1 = compute_rcs_sphere(0.001, lam)
        rcs2 = compute_rcs_sphere(0.002, lam)
        ratio = rcs2 / rcs1
        # D⁶ scaling: 2⁶ = 64
        self.assertAlmostEqual(ratio, 64.0, delta=5.0)

    def test_rcs_positive_for_all_regimes(self):
        diameters = [0.0001, 0.001, 0.01, 0.1, 1.0]
        wavelength = 0.03
        for d in diameters:
            rcs = compute_rcs_sphere(d, wavelength)
            self.assertGreater(rcs, 0, f"RCS must be positive for d={d}")

    def test_invalid_diameter_raises(self):
        with self.assertRaises(ValueError):
            compute_rcs_sphere(0, 0.03)

    def test_invalid_wavelength_raises(self):
        with self.assertRaises(ValueError):
            compute_rcs_sphere(0.01, 0)

    def test_sub_mm_below_space_fence_threshold(self):
        """5mm sphere must be far below Space Fence detection threshold."""
        space_fence = next(r for r in REFERENCE_RADAR_SYSTEMS if r.system_id == "space_fence")
        rcs = compute_rcs_sphere(0.005, space_fence.wavelength_m)
        rcs_db = rcs_to_dbsm(rcs)
        self.assertLess(rcs_db, space_fence.min_detectable_rcs_dbsm - 30,
                        "5mm sphere should be at least 30 dB below Space Fence threshold")

    def test_sub_mm_below_all_radar_thresholds(self):
        """1mm sphere must be below all reference radar thresholds."""
        for radar in REFERENCE_RADAR_SYSTEMS:
            rcs = compute_rcs_sphere(0.001, radar.wavelength_m)
            rcs_db = rcs_to_dbsm(rcs)
            self.assertLess(rcs_db, radar.min_detectable_rcs_dbsm,
                            f"1mm sphere should be below {radar.system_id} threshold, "
                            f"got {rcs_db:.1f} dBsm vs threshold {radar.min_detectable_rcs_dbsm} dBsm")


class TestWakeSignalScaling(unittest.TestCase):

    def test_reference_object_is_0db(self):
        signal = compute_wake_relative_signal_db(1.0, reference_diameter_m=1.0)
        self.assertAlmostEqual(signal, 0.0, places=6)

    def test_half_diameter_loses_6db(self):
        """Halving D reduces wake signal by 6 dB (D² scaling: 20 log10(0.5) = -6 dB)."""
        signal = compute_wake_relative_signal_db(0.5, reference_diameter_m=1.0)
        self.assertAlmostEqual(signal, -6.021, delta=0.01)

    def test_wake_scales_better_than_radar_rayleigh(self):
        """Wake loses 6 dB when D halves; Rayleigh radar loses 18 dB.
        Wake has a 12 dB/octave advantage over radar in the Rayleigh regime."""
        lam = 0.225  # Space Fence
        d1, d2 = 0.01, 0.005

        radar_loss = rcs_to_dbsm(compute_rcs_sphere(d2, lam)) - rcs_to_dbsm(compute_rcs_sphere(d1, lam))
        wake_loss = compute_wake_relative_signal_db(d2) - compute_wake_relative_signal_db(d1)

        # Radar loses ~18 dB; wake loses ~6 dB → advantage is radar_loss - wake_loss ≈ -12 dB
        self.assertLess(radar_loss, wake_loss,
                        "Radar must lose more signal than wake when D halves")
        # radar_loss is negative (signal decreases), wake_loss is less negative
        # The advantage = wake_loss - radar_loss should be ~+12 dB
        self.assertAlmostEqual(wake_loss - radar_loss, 12.0, delta=3.0)

    def test_invalid_diameter_raises(self):
        with self.assertRaises(ValueError):
            compute_wake_relative_signal_db(0)


class TestRadarDetectabilityAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = RadarDetectabilityAnalyzer()
        self.generated_at = datetime(2026, 7, 30, tzinfo=timezone.utc)

    def test_gap_analysis_has_all_radars(self):
        gap = self.analyzer.build_gap_analysis(self.generated_at)
        self.assertEqual(len(gap.radar_curves), len(REFERENCE_RADAR_SYSTEMS))

    def test_gap_analysis_evidence_class_synthetic(self):
        gap = self.analyzer.build_gap_analysis(self.generated_at)
        self.assertEqual(gap.evidence_class, EvidenceClass.SYNTHETIC)

    def test_gap_analysis_has_limitation(self):
        gap = self.analyzer.build_gap_analysis(self.generated_at)
        self.assertTrue(len(gap.limitation) > 20)

    def test_gap_min_less_than_gap_max(self):
        gap = self.analyzer.build_gap_analysis(self.generated_at)
        self.assertLess(gap.gap_min_diameter_m, gap.gap_max_diameter_m)

    def test_haystack_detects_smaller_than_space_fence(self):
        gap = self.analyzer.build_gap_analysis(self.generated_at)
        space_fence = next(c for c in gap.radar_curves if c.system.system_id == "space_fence")
        haystack = next(c for c in gap.radar_curves if c.system.system_id == "haystack")
        self.assertLess(haystack.min_detectable_diameter_m,
                        space_fence.min_detectable_diameter_m)

    def test_all_curves_have_limitation_strings(self):
        gap = self.analyzer.build_gap_analysis(self.generated_at)
        for curve in gap.radar_curves:
            self.assertTrue(curve.limitation)

    def test_to_dict_roundtrip(self):
        gap = self.analyzer.build_gap_analysis(self.generated_at)
        d = gap.to_dict()
        self.assertIn("radar_curves", d)
        self.assertIn("wake_curve", d)
        self.assertEqual(d["evidence_class"], "synthetic")

    def test_undetected_fraction_is_high(self):
        """Most of the debris population should be in the detection gap."""
        gap = self.analyzer.build_gap_analysis(self.generated_at)
        self.assertGreater(gap.undetected_population_fraction, 0.5)


class TestReferenceRadarSystems(unittest.TestCase):

    def test_all_systems_have_positive_frequency(self):
        for r in REFERENCE_RADAR_SYSTEMS:
            self.assertGreater(r.frequency_hz, 0, f"{r.system_id} frequency must be positive")

    def test_all_systems_have_source_references(self):
        for r in REFERENCE_RADAR_SYSTEMS:
            self.assertTrue(r.source_reference, f"{r.system_id} missing source_reference")

    def test_wavelength_matches_frequency(self):
        c = 299_792_458.0
        for r in REFERENCE_RADAR_SYSTEMS:
            expected_wavelength = c / r.frequency_hz
            self.assertAlmostEqual(r.wavelength_m, expected_wavelength, places=6)


if __name__ == "__main__":
    unittest.main()
