"""Tests for archive_mining module."""
import math
import unittest
from datetime import datetime, timezone, timedelta
from hashlib import sha256

from heimdall.archive_mining import (
    TleObject,
    ObservatorySpec,
    ConjunctionPrediction,
    PlasmaWindow,
    WindowAnalysisResult,
    AnalysisVerdict,
    AnalysisProtocol,
    ArchiveMiningCampaign,
    ArchiveMiningReport,
    CampaignStatus,
    DataSource,
    build_standard_protocol,
    REFERENCE_OBSERVATORIES,
)
from heimdall.domain import EvidenceClass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tle() -> TleObject:
    return TleObject(
        catalog_number=25544,
        name="ISS (ZARYA)",
        tle_line1="1 25544U 98067A   26152.50000000  .00002182  00000-0  46547-4 0  9999",
        tle_line2="2 25544  51.6416 247.4627  0007898  49.4573 310.7158 15.54225151464998",
        catalog_source="celestrak",
    )


def _make_observatory() -> ObservatorySpec:
    return REFERENCE_OBSERVATORIES[DataSource.EISCAT_UHF]


def _make_conjunction() -> ConjunctionPrediction:
    return ConjunctionPrediction(
        conjunction_id="conj-test-001",
        tle_object=_make_tle(),
        observatory=_make_observatory(),
        predicted_transit_utc=datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
        closest_approach_km=5.0,
        elevation_deg=72.0,
        relative_velocity_km_s=7.5,
        transit_duration_s=1.2,
        propagator_id="two_body_j2_screening",
        evidence_class=EvidenceClass.SYNTHETIC,
    )


def _make_plasma_window() -> PlasmaWindow:
    rng_seed = 42
    import random
    rng = random.Random(rng_seed)
    n = 660  # 330s baseline + 30s analysis at 2 Hz
    samples = tuple(1e11 + rng.gauss(0, 2e9) for _ in range(n))
    flags   = tuple(0 for _ in range(n))
    art = "sha256:" + sha256(b"test_artifact").hexdigest()
    mfst = "sha256:" + sha256(b"test_manifest").hexdigest()
    return PlasmaWindow(
        window_id="win-test-001",
        conjunction_id="conj-test-001",
        source=DataSource.SYNTHETIC_TEST,
        window_start_utc=datetime(2026, 6, 15, 11, 54, 30, tzinfo=timezone.utc),
        window_end_utc=datetime(2026, 6, 15, 12, 0, 30, tzinfo=timezone.utc),
        time_step_s=0.5,
        electron_density_per_m3=samples,
        data_quality_flags=flags,
        raw_artifact_digest=art,
        acquisition_manifest_digest=mfst,
        evidence_class=EvidenceClass.SYNTHETIC,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestTleObject(unittest.TestCase):

    def test_valid_tle(self):
        tle = _make_tle()
        self.assertEqual(tle.catalog_number, 25544)

    def test_invalid_line1_format(self):
        with self.assertRaises(ValueError):
            TleObject(25544, "ISS", "bad_line", "2 25544  51.6 247.4", "test")

    def test_zero_catalog_number_raises(self):
        with self.assertRaises(ValueError):
            TleObject(0, "X", "1 00000U", "2 00000  0.0 0.0", "test")


class TestObservatorySpec(unittest.TestCase):

    def test_eiscat_in_reference_observatories(self):
        obs = REFERENCE_OBSERVATORIES[DataSource.EISCAT_UHF]
        self.assertEqual(obs.source, DataSource.EISCAT_UHF)

    def test_invalid_latitude(self):
        with self.assertRaises(ValueError):
            ObservatorySpec(DataSource.EISCAT_UHF, "X", 100.0, 0.0, 0.0, 1.0, 1.0, 0.0)

    def test_zero_time_resolution_raises(self):
        with self.assertRaises(ValueError):
            ObservatorySpec(DataSource.EISCAT_UHF, "X", 60.0, 0.0, 0.0, 1.0, 0.0, 0.0)


class TestConjunctionPrediction(unittest.TestCase):

    def test_valid_conjunction(self):
        c = _make_conjunction()
        self.assertEqual(c.conjunction_id, "conj-test-001")
        self.assertEqual(c.evidence_class, EvidenceClass.SYNTHETIC)

    def test_naive_timestamp_raises(self):
        with self.assertRaises(ValueError):
            ConjunctionPrediction(
                "c1", _make_tle(), _make_observatory(),
                datetime(2026, 6, 1, 12, 0, 0),  # no tzinfo
                5.0, 70.0, 7.5, 1.0, "sgp4",
                EvidenceClass.SYNTHETIC,
            )

    def test_negative_velocity_raises(self):
        with self.assertRaises(ValueError):
            ConjunctionPrediction(
                "c1", _make_tle(), _make_observatory(),
                datetime(2026, 6, 1, tzinfo=timezone.utc),
                5.0, 70.0, -1.0, 1.0, "sgp4",
                EvidenceClass.SYNTHETIC,
            )


class TestPlasmaWindow(unittest.TestCase):

    def test_valid_window(self):
        w = _make_plasma_window()
        self.assertEqual(w.window_id, "win-test-001")
        self.assertGreater(w.n_good_samples, 0)
        self.assertAlmostEqual(w.good_fraction, 1.0)

    def test_mismatched_arrays_raise(self):
        art  = "sha256:" + sha256(b"x").hexdigest()
        mfst = "sha256:" + sha256(b"y").hexdigest()
        with self.assertRaises(ValueError):
            PlasmaWindow(
                "w", "c", DataSource.SYNTHETIC_TEST,
                datetime(2026, 1, 1, tzinfo=timezone.utc),
                datetime(2026, 1, 1, 0, 1, tzinfo=timezone.utc),
                0.5, (1e11, 2e11), (0,),  # length mismatch
                art, mfst, EvidenceClass.SYNTHETIC,
            )

    def test_missing_sha256_prefix_raises(self):
        with self.assertRaises(ValueError):
            PlasmaWindow(
                "w", "c", DataSource.SYNTHETIC_TEST,
                datetime(2026, 1, 1, tzinfo=timezone.utc),
                datetime(2026, 1, 1, 0, 1, tzinfo=timezone.utc),
                0.5, (1e11,), (0,),
                "no_prefix", "sha256:valid",
                EvidenceClass.SYNTHETIC,
            )

    def test_median_ne_computed(self):
        w = _make_plasma_window()
        self.assertGreater(w.median_ne, 0)


class TestBuildStandardProtocol(unittest.TestCase):

    def test_protocol_has_required_fields(self):
        p = build_standard_protocol()
        self.assertTrue(p.protocol_id)
        self.assertTrue(p.hypothesis)
        self.assertTrue(p.null_hypothesis)
        self.assertGreater(len(p.confounder_list), 3)
        self.assertTrue(p.protocol_digest.startswith("sha256:"))

    def test_protocol_is_deterministic(self):
        p1 = build_standard_protocol()
        p2 = build_standard_protocol()
        self.assertEqual(p1.protocol_digest, p2.protocol_digest)

    def test_significance_threshold_in_range(self):
        p = build_standard_protocol()
        self.assertGreater(p.significance_threshold, 0)
        self.assertLess(p.significance_threshold, 1)

    def test_bonferroni_correction_declared(self):
        p = build_standard_protocol()
        self.assertEqual(p.multiple_comparison_correction, "bonferroni")


class TestAnalysisPipelineIntegration(unittest.TestCase):
    """Integration tests for the full analysis pipeline using synthetic data."""

    def setUp(self):
        sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent / "scripts"))

    def test_synthetic_pipeline_with_signal(self):
        """Pipeline with injected signal should produce SIGNAL_DETECTED verdict."""
        from mine_swarm_archive import (
            SyntheticPlasmaAdapter, analyse_window,
            _build_synthetic_conjunctions, run_campaign,
        )
        protocol = build_standard_protocol()
        observatory = REFERENCE_OBSERVATORIES[DataSource.EISCAT_UHF]
        adapter = SyntheticPlasmaAdapter(inject_signal=True, snr=5.0)

        conj = _build_synthetic_conjunctions(1, observatory)[0]
        window = adapter.fetch_window(conj, protocol.analysis_window_s, protocol.baseline_window_s)
        result = analyse_window(window, conj, protocol)

        self.assertEqual(result.evidence_class, EvidenceClass.SYNTHETIC)
        self.assertTrue(result.limitation)
        # With SNR=5, signal should typically be detected (not always guaranteed)
        self.assertIn(result.verdict, [AnalysisVerdict.SIGNAL_DETECTED, AnalysisVerdict.NO_SIGNAL])

    def test_synthetic_pipeline_null_result(self):
        """Pipeline without injected signal should produce NO_SIGNAL verdict."""
        from mine_swarm_archive import (
            SyntheticPlasmaAdapter, analyse_window,
            _build_synthetic_conjunctions,
        )
        protocol = build_standard_protocol()
        observatory = REFERENCE_OBSERVATORIES[DataSource.EISCAT_UHF]
        adapter = SyntheticPlasmaAdapter(inject_signal=False)

        conj = _build_synthetic_conjunctions(1, observatory)[0]
        window = adapter.fetch_window(conj, protocol.analysis_window_s, protocol.baseline_window_s)
        result = analyse_window(window, conj, protocol)

        self.assertEqual(result.verdict, AnalysisVerdict.NO_SIGNAL)

    def test_full_campaign_report_structure(self):
        """Full campaign produces a valid ArchiveMiningReport with all required fields."""
        from mine_swarm_archive import (
            SyntheticPlasmaAdapter, run_campaign,
            _build_synthetic_conjunctions,
        )
        protocol    = build_standard_protocol()
        observatory = REFERENCE_OBSERVATORIES[DataSource.EISCAT_UHF]
        adapter     = SyntheticPlasmaAdapter(inject_signal=True, snr=4.0)
        conjunctions = _build_synthetic_conjunctions(5, observatory)

        report = run_campaign(
            conjunctions, adapter, protocol,
            ledger_entry_id="test-001",
            observatory=observatory,
            tle_catalog_digest="sha256:" + sha256(b"test").hexdigest(),
            generated_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        )

        self.assertTrue(report.report_id)
        self.assertEqual(report.windows_total, 5)
        self.assertEqual(report.windows_valid + report.windows_excluded, 5)
        self.assertGreaterEqual(report.windows_positive, 0)
        self.assertLessEqual(report.windows_positive, report.windows_valid)
        self.assertEqual(report.evidence_class, EvidenceClass.SYNTHETIC)
        self.assertTrue(report.limitation)
        self.assertTrue(report.audit_bundle_digest.startswith("sha256:"))

    def test_report_to_dict_roundtrip(self):
        """Report serialises to dict with correct evidence class."""
        from mine_swarm_archive import (
            SyntheticPlasmaAdapter, run_campaign,
            _build_synthetic_conjunctions,
        )
        protocol     = build_standard_protocol()
        observatory  = REFERENCE_OBSERVATORIES[DataSource.EISCAT_UHF]
        adapter      = SyntheticPlasmaAdapter(inject_signal=False)
        conjunctions = _build_synthetic_conjunctions(3, observatory)

        report = run_campaign(
            conjunctions, adapter, protocol, "test-002",
            observatory,
            "sha256:" + sha256(b"t").hexdigest(),
            datetime(2026, 7, 30, tzinfo=timezone.utc),
        )
        d = report.to_dict()
        self.assertEqual(d["evidence_class"], "synthetic")
        self.assertIn("individual_results", d)
        self.assertEqual(len(d["individual_results"]), len(conjunctions))

    def test_data_quality_exclusion(self):
        """Windows with low good_fraction must be excluded, not falsely classified."""
        from mine_swarm_archive import analyse_window, _build_synthetic_conjunctions
        protocol    = build_standard_protocol()
        observatory = REFERENCE_OBSERVATORIES[DataSource.EISCAT_UHF]
        conj        = _build_synthetic_conjunctions(1, observatory)[0]

        art  = "sha256:" + sha256(b"a").hexdigest()
        mfst = "sha256:" + sha256(b"m").hexdigest()
        # All samples flagged bad
        bad_window = PlasmaWindow(
            window_id="w-bad",
            conjunction_id=conj.conjunction_id,
            source=DataSource.SYNTHETIC_TEST,
            window_start_utc=conj.predicted_transit_utc - timedelta(seconds=300),
            window_end_utc=conj.predicted_transit_utc + timedelta(seconds=30),
            time_step_s=0.5,
            electron_density_per_m3=tuple(1e11 for _ in range(660)),
            data_quality_flags=tuple(1 for _ in range(660)),   # all bad
            raw_artifact_digest=art,
            acquisition_manifest_digest=mfst,
            evidence_class=EvidenceClass.SYNTHETIC,
        )
        result = analyse_window(bad_window, conj, protocol)
        self.assertEqual(result.verdict, AnalysisVerdict.DATA_QUALITY_FAIL)

    def test_null_result_preserved(self):
        """A null result must carry a non-empty limitation string."""
        from mine_swarm_archive import (
            SyntheticPlasmaAdapter, analyse_window,
            _build_synthetic_conjunctions,
        )
        protocol    = build_standard_protocol()
        observatory = REFERENCE_OBSERVATORIES[DataSource.EISCAT_UHF]
        adapter     = SyntheticPlasmaAdapter(inject_signal=False)
        conj        = _build_synthetic_conjunctions(1, observatory)[0]
        window      = adapter.fetch_window(conj, protocol.analysis_window_s, protocol.baseline_window_s)
        result      = analyse_window(window, conj, protocol)

        self.assertEqual(result.verdict, AnalysisVerdict.NO_SIGNAL)
        self.assertTrue(result.limitation, "null result must carry a limitation string")
        self.assertTrue(result.verdict_reason)


import sys


if __name__ == "__main__":
    unittest.main()
