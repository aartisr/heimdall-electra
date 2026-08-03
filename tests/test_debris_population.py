"""Tests for debris_population module."""
import unittest
import math
from datetime import datetime, timezone

from heimdall.debris_population import (
    OrbitalShell,
    DebrisPopulationBin,
    FragmentationEvent,
    DebrisCloud,
    DebrisPopulationSnapshot,
    PopulationModelConfig,
    SyntheticPowerLawModel,
    SizeRegime,
    PopulationSource,
    FRAGMENTATION_EVENT_CATALOG,
)
from heimdall.domain import EvidenceClass


class TestOrbitalShell(unittest.TestCase):

    def test_valid_shell(self):
        shell = OrbitalShell(400, 450, 0, 90)
        self.assertAlmostEqual(shell.altitude_km_centre, 425.0)

    def test_invalid_altitude_order(self):
        with self.assertRaises(ValueError):
            OrbitalShell(500, 400, 0, 90)

    def test_invalid_altitude_negative(self):
        with self.assertRaises(ValueError):
            OrbitalShell(-100, 400, 0, 90)

    def test_invalid_inclination(self):
        with self.assertRaises(ValueError):
            OrbitalShell(400, 450, 90, 10)

    def test_volume_positive(self):
        shell = OrbitalShell(400, 450, 0, 180)
        self.assertGreater(shell.volume_km3, 0)


class TestFragmentationEvent(unittest.TestCase):

    def test_valid_event(self):
        event = FragmentationEvent(
            event_id="test-event",
            name="Test Event",
            year=2020,
            orbital_altitude_km=500.0,
            orbital_inclination_deg=98.0,
            raan_deg=45.0,
            catalogued_fragment_count=100,
            estimated_sub_cm_count=10000,
            estimation_method="test",
            source_reference="Test Reference 2020",
        )
        self.assertEqual(event.event_id, "test-event")

    def test_missing_source_reference(self):
        with self.assertRaises(ValueError):
            FragmentationEvent(
                event_id="e1", name="N", year=2020,
                orbital_altitude_km=500, orbital_inclination_deg=90,
                raan_deg=0, catalogued_fragment_count=10,
                estimated_sub_cm_count=100,
                estimation_method="x", source_reference="",
            )

    def test_negative_altitude(self):
        with self.assertRaises(ValueError):
            FragmentationEvent(
                event_id="e1", name="N", year=2020,
                orbital_altitude_km=-100, orbital_inclination_deg=90,
                raan_deg=0, catalogued_fragment_count=10,
                estimated_sub_cm_count=100,
                estimation_method="x", source_reference="ref",
            )


class TestDebrisCloud(unittest.TestCase):

    def test_density_at_centroid_is_peak(self):
        cloud = DebrisCloud(
            cloud_id="c1", event_id="e1",
            centroid_altitude_km=500.0,
            centroid_inclination_deg=98.0,
            centroid_raan_deg=0.0,
            spread_altitude_km=50.0,
            spread_inclination_deg=5.0,
            peak_number_density_per_km3=1.0,
            total_mass_estimate_kg=100.0,
            size_regime=SizeRegime.SUB_CM,
            evidence_class=EvidenceClass.SYNTHETIC,
            limitation="test limitation",
        )
        self.assertAlmostEqual(cloud.density_at(500.0, 98.0), 1.0)

    def test_density_falls_off_from_centroid(self):
        cloud = DebrisCloud(
            cloud_id="c1", event_id="e1",
            centroid_altitude_km=500.0,
            centroid_inclination_deg=98.0,
            centroid_raan_deg=0.0,
            spread_altitude_km=50.0,
            spread_inclination_deg=5.0,
            peak_number_density_per_km3=1.0,
            total_mass_estimate_kg=100.0,
            size_regime=SizeRegime.SUB_CM,
            evidence_class=EvidenceClass.SYNTHETIC,
            limitation="test limitation",
        )
        density_off = cloud.density_at(600.0, 98.0)
        self.assertLess(density_off, 1.0)

    def test_missing_limitation_raises(self):
        with self.assertRaises(ValueError):
            DebrisCloud(
                cloud_id="c1", event_id="e1",
                centroid_altitude_km=500, centroid_inclination_deg=90,
                centroid_raan_deg=0, spread_altitude_km=50,
                spread_inclination_deg=5, peak_number_density_per_km3=1.0,
                total_mass_estimate_kg=100,
                size_regime=SizeRegime.SUB_CM,
                evidence_class=EvidenceClass.SYNTHETIC,
                limitation="",
            )


class TestFragmentationEventCatalog(unittest.TestCase):

    def test_catalog_not_empty(self):
        self.assertGreater(len(FRAGMENTATION_EVENT_CATALOG), 3)

    def test_all_events_have_source_references(self):
        for event in FRAGMENTATION_EVENT_CATALOG:
            self.assertTrue(event.source_reference, f"{event.event_id} missing source_reference")

    def test_all_events_have_positive_altitude(self):
        for event in FRAGMENTATION_EVENT_CATALOG:
            self.assertGreater(event.orbital_altitude_km, 0)

    def test_all_events_have_estimated_sub_cm(self):
        for event in FRAGMENTATION_EVENT_CATALOG:
            self.assertGreaterEqual(event.estimated_sub_cm_count, 0)


class TestSyntheticPowerLawModel(unittest.TestCase):

    def setUp(self):
        self.model = SyntheticPowerLawModel()
        self.generated_at = datetime(2026, 7, 30, tzinfo=timezone.utc)
        self.config = PopulationModelConfig(
            altitude_bin_km=100.0,
            inclination_bin_deg=30.0,
        )

    def test_snapshot_has_required_fields(self):
        snap = self.model.build_snapshot(self.config, self.generated_at)
        self.assertIsNotNone(snap.snapshot_id)
        self.assertGreater(len(snap.shells), 0)
        self.assertGreater(len(snap.clouds), 0)
        self.assertGreater(len(snap.events), 0)

    def test_evidence_class_is_synthetic(self):
        snap = self.model.build_snapshot(self.config, self.generated_at)
        self.assertEqual(snap.evidence_class, EvidenceClass.SYNTHETIC)
        for shell in snap.shells:
            self.assertEqual(shell.evidence_class, EvidenceClass.SYNTHETIC)

    def test_limitation_string_present(self):
        snap = self.model.build_snapshot(self.config, self.generated_at)
        self.assertTrue(len(snap.limitation) > 10)

    def test_sub_cm_count_exceeds_tracked(self):
        snap = self.model.build_snapshot(self.config, self.generated_at)
        self.assertGreater(snap.estimated_sub_cm_total, snap.total_tracked_objects)

    def test_all_density_values_non_negative(self):
        snap = self.model.build_snapshot(self.config, self.generated_at)
        for b in snap.shells:
            self.assertGreaterEqual(b.spatial_density_per_km3, 0)
            self.assertGreaterEqual(b.flux_per_m2_per_year, 0)

    def test_to_dict_round_trips_evidence_class(self):
        snap = self.model.build_snapshot(self.config, self.generated_at)
        d = snap.to_dict()
        self.assertEqual(d["evidence_class"], "synthetic")

    def test_clouds_have_limitation_strings(self):
        snap = self.model.build_snapshot(self.config, self.generated_at)
        for cloud in snap.clouds:
            self.assertTrue(cloud.limitation)

    def test_snapshot_id_is_deterministic(self):
        snap1 = self.model.build_snapshot(self.config, self.generated_at)
        snap2 = self.model.build_snapshot(self.config, self.generated_at)
        self.assertEqual(snap1.snapshot_id, snap2.snapshot_id)


if __name__ == "__main__":
    unittest.main()
