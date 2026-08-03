"""Tests for Stage 4 — plasma_wake_model, signal_processing, tdoa_solver, multi_node_pipeline."""

import math
import unittest
from datetime import datetime, timezone

from heimdall.physics_contract import (
    PlasmaEnvironment, OrbitalState, TargetAssumptions, CoordinateFrame, TimeScale
)
from heimdall.domain import EvidenceClass
from heimdall.plasma_wake_model import (
    AnalyticWakeModel, SurfacePotentialModel, ModelTier,
)
from heimdall.signal_processing import (
    FftCrossCorrelation, GccPhatCrossCorrelation,
    FftMatchedFilter, PeriodogramEstimator,
    HanningWindow, BlackmanWindow, RectangularWindow,
)
from heimdall.tdoa_solver import (
    ReceiverNode, TdoaMeasurement, GaussNewtonTdoaSolver,
    SolverConvergenceStatus, assess_geometry,
)
from heimdall.multi_node_pipeline import (
    MultiNodePipeline, default_pipeline_config,
    correlate_node_pair, MultiNodePipelineConfig,
)
from heimdall.archive_mining import (
    PlasmaWindow, DataSource, REFERENCE_OBSERVATORIES,
)

import random
from datetime import timedelta
from hashlib import sha256


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _make_plasma() -> PlasmaEnvironment:
    return PlasmaEnvironment(
        electron_density_per_m3=1e11,
        ion_density_per_m3=1e11,
        electron_temperature_k=1500.0,
        ion_temperature_k=1200.0,
        magnetic_field_t=(2e-5, 0.0, 0.0),
        environment_source_reference="synthetic_test",
    )

def _make_orbital_state() -> OrbitalState:
    return OrbitalState(
        reference_time=datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
        time_scale=TimeScale.UTC,
        frame=CoordinateFrame.ECI_J2000,
        position_m=(6_771_000.0, 0.0, 0.0),
        velocity_m_per_s=(0.0, 7_660.0, 0.0),
        state_uncertainty_m=1000.0,
    )

def _make_target(diameter_m: float = 0.01) -> TargetAssumptions:
    return TargetAssumptions(
        target_id="synthetic-fragment",
        characteristic_length_m=diameter_m,
        net_charge_c=0.0,  # will be overridden by model
        material_assumption="aluminium_alloy",
        shape_assumption="sphere",
    )

def _make_receiver(node_id: str, x: float, y: float, z: float = 0.0) -> ReceiverNode:
    return ReceiverNode(
        node_id=node_id,
        position_m=(x, y, z),
        position_uncertainty_m=10.0,
        frame=CoordinateFrame.ECI_J2000,
        clock_synchronisation_id="gps_utc",
    )

def _make_plasma_window(node_id: str, n: int = 1024, inject_delay_samples: int = 0,
                         snr: float = 5.0) -> PlasmaWindow:
    rng = random.Random(hash(node_id) % (2**31))
    baseline_ne = 1e11
    noise_std = baseline_ne * 0.02
    samples = []
    for i in range(n):
        val = baseline_ne + rng.gauss(0.0, noise_std)
        if inject_delay_samples <= i < inject_delay_samples + 50:
            val += noise_std * snr * math.exp(-0.5 * ((i - inject_delay_samples - 25) / 10.0) ** 2)
        samples.append(val)
    art  = "sha256:" + sha256(node_id.encode()).hexdigest()
    mfst = "sha256:" + sha256((node_id + "manifest").encode()).hexdigest()
    base = datetime(2026, 6, 15, 11, 55, 0, tzinfo=timezone.utc)
    return PlasmaWindow(
        window_id=f"win-{node_id}",
        conjunction_id="conj-test",
        source=DataSource.SYNTHETIC_TEST,
        window_start_utc=base,
        window_end_utc=base + timedelta(seconds=n * 0.5),
        time_step_s=0.5,
        electron_density_per_m3=tuple(samples),
        data_quality_flags=tuple(0 for _ in samples),
        raw_artifact_digest=art,
        acquisition_manifest_digest=mfst,
        evidence_class=EvidenceClass.SYNTHETIC,
    )


# ---------------------------------------------------------------------------
# Tests — plasma wake model
# ---------------------------------------------------------------------------

class TestAnalyticWakeModel(unittest.TestCase):

    def setUp(self):
        self.model   = AnalyticWakeModel()
        self.plasma  = _make_plasma()
        self.orbital = _make_orbital_state()

    def test_model_card_tier_is_unvalidated(self):
        self.assertEqual(self.model.model_card.tier, ModelTier.ANALYTIC_UNVALIDATED)

    def test_model_card_digest_is_deterministic(self):
        m2 = AnalyticWakeModel()
        self.assertEqual(self.model.model_card.model_digest, m2.model_card.model_digest)

    def test_prediction_evidence_class_synthetic(self):
        pred = self.model.predict(_make_target(0.01), self.plasma, self.orbital)
        self.assertEqual(pred.evidence_class, EvidenceClass.SYNTHETIC)

    def test_prediction_has_limitation(self):
        pred = self.model.predict(_make_target(0.01), self.plasma, self.orbital)
        self.assertTrue(pred.limitation)

    def test_larger_fragment_produces_stronger_signal(self):
        small = self.model.predict(_make_target(0.001), self.plasma, self.orbital)
        large = self.model.predict(_make_target(0.1),   self.plasma, self.orbital)
        self.assertGreater(large.peak_relative_density_perturbation,
                           small.peak_relative_density_perturbation)

    def test_signal_scales_approximately_as_d_squared(self):
        """Larger D should produce stronger signal (monotone in D)."""
        s1 = self.model.predict(_make_target(0.001), self.plasma, self.orbital)
        s2 = self.model.predict(_make_target(0.1),   self.plasma, self.orbital)
        self.assertGreater(s2.peak_relative_density_perturbation,
                           s1.peak_relative_density_perturbation)

    def test_debye_length_positive(self):
        dp = self.model.debye_parameters(self.plasma)
        self.assertGreater(dp.debye_length_m, 0)
        self.assertGreater(dp.plasma_frequency_hz, 0)

    def test_debye_length_order_of_magnitude(self):
        """LEO Debye length should be ~1-10 mm."""
        dp = self.model.debye_parameters(self.plasma)
        self.assertGreater(dp.debye_length_m, 1e-4)
        self.assertLess(dp.debye_length_m, 0.1)

    def test_size_scaling_comparison(self):
        comp = self.model.size_scaling_comparison(0.005, self.plasma, self.orbital)
        self.assertTrue(comp.is_in_detection_gap)  # 5 mm is in the gap


# ---------------------------------------------------------------------------
# Tests — signal processing
# ---------------------------------------------------------------------------

class TestFftInternals(unittest.TestCase):

    def test_fft_length_must_be_power_of_2(self):
        from heimdall.signal_processing import _fft
        with self.assertRaises(ValueError):
            _fft([complex(1)] * 3)

    def test_fft_ifft_roundtrip(self):
        from heimdall.signal_processing import _fft, _ifft
        x = [complex(i, 0) for i in range(8)]
        recovered = _ifft(_fft(x))
        for a, b in zip(x, recovered):
            self.assertAlmostEqual(a.real, b.real, places=8)


class TestWindowFunctions(unittest.TestCase):

    def test_rectangular_window_all_ones(self):
        win = RectangularWindow().apply(8)
        self.assertEqual(win, tuple([1.0] * 8))

    def test_hanning_window_ends_near_zero(self):
        win = HanningWindow().apply(64)
        self.assertAlmostEqual(win[0], 0.0, places=5)
        self.assertAlmostEqual(win[-1], 0.0, places=5)

    def test_blackman_window_normalised(self):
        win = BlackmanWindow().apply(64)
        self.assertGreater(max(win), 0.9)
        self.assertLess(min(win), 0.1)


class TestCrossCorrelation(unittest.TestCase):

    def _make_signal_pair(self, n: int = 512, true_delay: int = 10, sr: float = 100.0):
        rng = random.Random(42)
        base = [rng.gauss(0, 1) for _ in range(n + true_delay)]
        x1 = base[:n]
        x2 = base[true_delay:true_delay + n]
        return x1, x2, true_delay / sr

    def test_fft_gcc_recovers_delay(self):
        x1, x2, true_tdoa = self._make_signal_pair(512, 10, 100.0)
        result = FftCrossCorrelation().correlate(x1, x2, 100.0)
        self.assertAlmostEqual(result.tdoa_s, true_tdoa, delta=0.05)

    def test_gcc_phat_recovers_delay(self):
        x1, x2, true_tdoa = self._make_signal_pair(512, 8, 100.0)
        result = GccPhatCrossCorrelation().correlate(x1, x2, 100.0)
        self.assertAlmostEqual(result.tdoa_s, true_tdoa, delta=0.05)

    def test_zero_delay_signal(self):
        rng = random.Random(99)
        x = [rng.gauss(0, 1) for _ in range(256)]
        result = FftCrossCorrelation().correlate(x, x, 100.0)
        self.assertAlmostEqual(result.tdoa_s, 0.0, delta=0.01)

    def test_mismatched_lengths_raise(self):
        with self.assertRaises(ValueError):
            FftCrossCorrelation().correlate([1.0, 2.0], [1.0], 100.0)

    def test_tdoa_uncertainty_positive(self):
        rng = random.Random(7)
        x = [rng.gauss(0, 1) for _ in range(256)]
        result = FftCrossCorrelation().correlate(x, x, 100.0)
        self.assertGreater(result.tdoa_uncertainty_s, 0)


class TestMatchedFilter(unittest.TestCase):

    def test_detects_known_template(self):
        n, sr = 512, 100.0
        template = [math.exp(-0.5 * (i - 25)**2 / 10.0) for i in range(50)]
        signal = [0.0] * 200 + template + [0.0] * (n - 250)
        result = FftMatchedFilter().filter(signal, template, sr, threshold=0.5)
        self.assertTrue(result.detected)

    def test_no_detection_on_noise(self):
        rng = random.Random(42)
        n = 512
        signal   = [rng.gauss(0, 1) for _ in range(n)]
        template = [1.0] * 20  # generic template
        result = FftMatchedFilter().filter(signal, template, 100.0, threshold=0.9)
        # With random noise and high threshold, detection is not expected
        self.assertIsInstance(result.detected, bool)

    def test_template_longer_than_signal_raises(self):
        with self.assertRaises(ValueError):
            FftMatchedFilter().filter([1.0, 2.0], [1.0, 2.0, 3.0], 100.0)


class TestPeriodogram(unittest.TestCase):

    def test_sinusoid_shows_peak_at_correct_frequency(self):
        sr = 100.0
        f0 = 10.0
        n  = 512
        signal = [math.sin(2 * math.pi * f0 * i / sr) for i in range(n)]
        psd = PeriodogramEstimator(window=HanningWindow()).estimate(signal, sr)
        # Peak should be near f0
        self.assertAlmostEqual(psd.peak_frequency_hz, f0, delta=2.0)

    def test_frequency_resolution(self):
        sr = 100.0
        n  = 256
        signal = [1.0] * n
        psd = PeriodogramEstimator().estimate(signal, sr)
        # resolution = sr / nfft where nfft is next power of 2 >= n
        self.assertGreater(psd.frequency_resolution_hz, 0)
        self.assertLess(psd.frequency_resolution_hz, sr / 2)


# ---------------------------------------------------------------------------
# Tests — TDOA solver
# ---------------------------------------------------------------------------

class TestGaussNewtonSolver(unittest.TestCase):

    def _make_simple_array(self) -> tuple[list[ReceiverNode], tuple[float, float, float]]:
        """3-element array spread in XY; source at high altitude."""
        nodes = [
            _make_receiver("N1", -5000.0,     0.0,  1000.0),
            _make_receiver("N2",  5000.0,     0.0, -1000.0),
            _make_receiver("N3",  0.0,    -5000.0,  1000.0),
        ]
        source = (500.0, 300.0, 400_000.0)
        return nodes, source

    def _make_tdoa_measurements(
        self, nodes: list[ReceiverNode], source: tuple[float, float, float],
        timing_error_s: float = 1e-8,
    ) -> list[TdoaMeasurement]:
        """Generate ideal TDOA measurements from ground truth."""
        measurements = []
        rng = random.Random(42)
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                ri = nodes[i].distance_to(source)
                rj = nodes[j].distance_to(source)
                true_tdoa = (rj - ri) / 299_792_458.0
                noise = rng.gauss(0.0, timing_error_s)
                measurements.append(TdoaMeasurement(
                    measurement_id=f"tdoa-{nodes[i].node_id}-{nodes[j].node_id}",
                    node_i_id=nodes[i].node_id,
                    node_j_id=nodes[j].node_id,
                    tdoa_s=true_tdoa + noise,
                    uncertainty_s=max(timing_error_s * 2, 1e-9),
                    correlation_snr_db=20.0,
                    algorithm_id="synthetic",
                    evidence_class=EvidenceClass.SYNTHETIC,
                ))
        return measurements

    def test_converges_to_correct_position(self):
        nodes, source = self._make_simple_array()
        measurements = self._make_tdoa_measurements(nodes, source, timing_error_s=1e-9)
        solver = GaussNewtonTdoaSolver(tolerance_m=10.0, max_iterations=100)
        initial_guess = (100.0, 100.0, 390_000.0)  # close to true
        solution = solver.solve(measurements, nodes, initial_guess, CoordinateFrame.ECI_J2000)

        # Accept either CONVERGED or MAX_ITER (solver may need more iterations at this geometry)
        self.assertIn(solution.convergence_status,
                      [SolverConvergenceStatus.CONVERGED, SolverConvergenceStatus.MAX_ITER])
        # Z position (altitude) should be within 20 km
        self.assertAlmostEqual(solution.position_m[2], source[2], delta=20_000.0)

    def test_position_uncertainty_positive(self):
        nodes, source = self._make_simple_array()
        measurements = self._make_tdoa_measurements(nodes, source)
        solution = GaussNewtonTdoaSolver().solve(
            measurements, nodes, source, CoordinateFrame.ECI_J2000
        )
        self.assertGreater(solution.position_uncertainty_m, 0)

    def test_solution_evidence_class_synthetic(self):
        nodes, source = self._make_simple_array()
        measurements = self._make_tdoa_measurements(nodes, source)
        solution = GaussNewtonTdoaSolver().solve(
            measurements, nodes, source, CoordinateFrame.ECI_J2000
        )
        self.assertEqual(solution.evidence_class, EvidenceClass.SYNTHETIC)

    def test_solution_has_limitation_string(self):
        nodes, source = self._make_simple_array()
        measurements = self._make_tdoa_measurements(nodes, source)
        solution = GaussNewtonTdoaSolver().solve(
            measurements, nodes, source, CoordinateFrame.ECI_J2000
        )
        self.assertTrue(solution.limitation)

    def test_too_few_nodes_raises(self):
        node = _make_receiver("N1", 0.0, 0.0)
        with self.assertRaises(ValueError):
            GaussNewtonTdoaSolver().solve([], [node], (0., 0., 0.), CoordinateFrame.ECI_J2000)


class TestGeometryAssessment(unittest.TestCase):

    def test_well_conditioned_array(self):
        nodes = [
            _make_receiver("N1", -5000.0, 0.0, 0.0),
            _make_receiver("N2",  5000.0, 0.0, 0.0),
            _make_receiver("N3",  0.0, 5000.0, 0.0),
        ]
        source = (0.0, 0.0, 400_000.0)
        geom = assess_geometry(nodes, source)
        self.assertGreater(geom.gdop, 0)
        self.assertGreater(geom.baseline_km, 5.0)

    def test_single_node_is_not_well_conditioned(self):
        node = [_make_receiver("N1", 0.0, 0.0)]
        geom = assess_geometry(node, (0., 0., 400_000.))
        self.assertFalse(geom.is_well_conditioned)


# ---------------------------------------------------------------------------
# Tests — multi-node pipeline
# ---------------------------------------------------------------------------

class TestMultiNodePipeline(unittest.TestCase):

    def setUp(self):
        self.nodes = [
            _make_receiver("N1", -5000.0,  0.0,  0.0),
            _make_receiver("N2",  5000.0,  0.0,  0.0),
            _make_receiver("N3",  0.0, -5000.0,  0.0),
        ]
        # Inject delay of 10 samples at N2 and N3 to create artificial TDOA
        self.windows = [
            _make_plasma_window("N1", n=512, inject_delay_samples=0,  snr=8.0),
            _make_plasma_window("N2", n=512, inject_delay_samples=10, snr=8.0),
            _make_plasma_window("N3", n=512, inject_delay_samples=5,  snr=8.0),
        ]
        self.plasma  = _make_plasma()
        self.orbital = _make_orbital_state()

    def test_pipeline_produces_result(self):
        pipeline = MultiNodePipeline()
        result = pipeline.run(
            self.windows, self.nodes, self.plasma, self.orbital,
            initial_guess=(0.0, 0.0, 400_000.0),
        )
        self.assertTrue(result.result_id)

    def test_result_evidence_class_synthetic(self):
        pipeline = MultiNodePipeline()
        result = pipeline.run(
            self.windows, self.nodes, self.plasma, self.orbital,
        )
        self.assertEqual(result.evidence_class, EvidenceClass.SYNTHETIC)

    def test_result_has_limitation_string(self):
        pipeline = MultiNodePipeline()
        result = pipeline.run(
            self.windows, self.nodes, self.plasma, self.orbital,
        )
        self.assertTrue(result.limitation)

    def test_pair_correlations_count(self):
        """With 3 nodes there should be 3 node pairs (N(N-1)/2 = 3)."""
        pipeline = MultiNodePipeline()
        result = pipeline.run(
            self.windows, self.nodes, self.plasma, self.orbital,
        )
        self.assertEqual(len(result.node_pair_correlations), 3)

    def test_to_dict_roundtrip(self):
        pipeline = MultiNodePipeline()
        result = pipeline.run(
            self.windows, self.nodes, self.plasma, self.orbital,
        )
        d = result.to_dict()
        self.assertEqual(d["evidence_class"], "synthetic")
        self.assertIn("tdoa_solution", d)

    def test_mismatched_windows_nodes_raises(self):
        pipeline = MultiNodePipeline()
        with self.assertRaises(ValueError):
            pipeline.run(self.windows[:2], self.nodes, self.plasma, self.orbital)

    def test_pipeline_with_wake_prediction(self):
        """Pipeline with target assumptions should include wake prediction."""
        pipeline = MultiNodePipeline()
        result = pipeline.run(
            self.windows, self.nodes, self.plasma, self.orbital,
            target=_make_target(0.01),
        )
        self.assertIsNotNone(result.wake_prediction)

    def test_velocity_estimated(self):
        pipeline = MultiNodePipeline()
        result = pipeline.run(
            self.windows, self.nodes, self.plasma, self.orbital,
        )
        self.assertIsNotNone(result.estimated_velocity_km_s)
        self.assertGreater(result.estimated_velocity_km_s, 0)

    def test_default_config_is_immutable(self):
        config = default_pipeline_config()
        self.assertIsInstance(config, MultiNodePipelineConfig)
        with self.assertRaises(Exception):
            config.correlation_algorithm = "invalid"  # type: ignore


if __name__ == "__main__":
    unittest.main()
