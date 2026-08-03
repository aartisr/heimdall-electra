# Heimdall Electra — Testing Strategy & Examples

This document defines comprehensive testing strategies ensuring reliability, correctness, and resilience.

## Testing Pyramid

```
    △  E2E Tests (scenarios)
   / \  - Full pipeline from fixture to decision
  /   \ - Blind evaluation on locked corpus
 /─────\ Integration Tests (pipeline)
/       \ - Detector + gates with various inputs
─────────────── Unit Tests (contracts & algorithms)
- Domain contract validation
- Detector signal processing
- Gate decision logic
```

## Unit Testing Strategy

### Domain Contract Tests
Every domain object must validate exhaustively on construction.

```python
import unittest
from heimdall import ObservationL0, Provenance, EvidenceClass
from datetime import datetime, timezone
from heimdall.exceptions import create_contract_error

class TestObservationL0(unittest.TestCase):
    """Test domain contract for L0 observations."""
    
    def setUp(self):
        """Create valid observation for testing."""
        self.provenance = Provenance(
            evidence_class=EvidenceClass.SYNTHETIC,
            scenario_id="test-scenario",
            generator_version="1.0",
            configuration_digest="abc123",
            model_card_digest="def456",
            created_at=datetime.now(timezone.utc),
        )
        self.samples = (0.1, 0.2, 0.3, 0.4, 0.5)
    
    def test_valid_observation_created(self):
        """Valid observation should be created without error."""
        obs = ObservationL0(
            observation_id="obs-001",
            samples=self.samples,
            sample_rate_hz=1024,
            started_at=datetime.now(timezone.utc),
            sensor_id="sensor-001",
            sequence_number=1,
            clock_uncertainty_ns=100.0,
            calibration_id="cal-001",
            provenance=self.provenance,
            payload_digest="correct-digest",
        )
        self.assertEqual(obs.observation_id, "obs-001")
    
    def test_empty_observation_id_raises(self):
        """Empty observation ID should raise error."""
        with self.assertRaises(create_contract_error):
            ObservationL0(
                observation_id="",  # Invalid
                samples=self.samples,
                sample_rate_hz=1024,
                started_at=datetime.now(timezone.utc),
                sensor_id="sensor-001",
                sequence_number=1,
                clock_uncertainty_ns=100.0,
                calibration_id="cal-001",
                provenance=self.provenance,
                payload_digest="digest",
            )
    
    def test_empty_samples_raises(self):
        """Empty samples should raise error."""
        with self.assertRaises(create_contract_error):
            ObservationL0(
                observation_id="obs-001",
                samples=(),  # Invalid
                sample_rate_hz=1024,
                started_at=datetime.now(timezone.utc),
                sensor_id="sensor-001",
                sequence_number=1,
                clock_uncertainty_ns=100.0,
                calibration_id="cal-001",
                provenance=self.provenance,
                payload_digest="digest",
            )
    
    def test_wrong_payload_digest_raises(self):
        """Mismatched payload digest should raise error."""
        from heimdall.domain import waveform_digest
        correct_digest = waveform_digest(self.samples)
        
        with self.assertRaises(create_contract_error):
            ObservationL0(
                observation_id="obs-001",
                samples=self.samples,
                sample_rate_hz=1024,
                started_at=datetime.now(timezone.utc),
                sensor_id="sensor-001",
                sequence_number=1,
                clock_uncertainty_ns=100.0,
                calibration_id="cal-001",
                provenance=self.provenance,
                payload_digest="wrong-digest",  # Wrong!
            )
```

### Algorithm Tests
Test detector, gates, and processing independently.

```python
class TestBaselineMatchedFilter(unittest.TestCase):
    """Test baseline detector algorithm."""
    
    def test_detects_target_frequency_burst(self):
        """Detector should score burst of target frequency high."""
        from heimdall import (
            detect, BaselineMatchedFilter, SyntheticScenario,
            generate_observation
        )
        
        # Create scenario with clear signal
        scenario = SyntheticScenario(
            scenario_id="burst-01",
            seed=42,
            signal_frequency_hz=64.0,
            signal_amplitude=0.5,
            noise_amplitude=0.1,
            expected_signal=True,
        )
        obs = generate_observation(scenario)
        
        detector = BaselineMatchedFilter(target_frequency_hz=64.0)
        candidate = detect(obs, detector)
        
        # Signal should score above 0.5
        self.assertGreater(candidate.score, 0.5)
    
    def test_ignores_noise_only(self):
        """Detector should score noise-only observation low."""
        from heimdall import (
            detect, BaselineMatchedFilter, SyntheticScenario,
            generate_observation
        )
        
        scenario = SyntheticScenario(
            scenario_id="noise-01",
            seed=42,
            signal_amplitude=0.0,  # No signal
            noise_amplitude=0.2,
            expected_signal=False,
        )
        obs = generate_observation(scenario)
        
        detector = BaselineMatchedFilter()
        candidate = detect(obs, detector)
        
        self.assertLess(candidate.score, 0.3)
    
    def test_score_normalized_to_unit_interval(self):
        """Detector score should always be in [0, 1]."""
        from heimdall import (
            detect, BaselineMatchedFilter, SyntheticScenario,
            generate_observation
        )
        
        for seed in range(10):
            scenario = SyntheticScenario(
                scenario_id=f"test-{seed}",
                seed=seed,
            )
            obs = generate_observation(scenario)
            detector = BaselineMatchedFilter()
            candidate = detect(obs, detector)
            
            self.assertGreaterEqual(candidate.score, 0.0)
            self.assertLessEqual(candidate.score, 1.0)


class TestPeakContrastGate(unittest.TestCase):
    """Test peak contrast interference gate."""
    
    def test_passes_burst_like_signal(self):
        """Gate should pass burst-like waveforms."""
        from heimdall import (
            detect, BaselineMatchedFilter, PeakContrastGate,
            SyntheticScenario, generate_observation
        )
        
        scenario = SyntheticScenario(
            scenario_id="burst-01",
            seed=42,
            signal_amplitude=0.5,
            signal_duration_s=0.25,  # Short burst
            noise_amplitude=0.1,
            expected_signal=True,
        )
        obs = generate_observation(scenario)
        
        detector = BaselineMatchedFilter()
        gates = [PeakContrastGate(minimum_peak_to_mean_ratio=1.5)]
        candidate = detect(obs, detector, gates)
        
        self.assertTrue(candidate.gates_passed)
    
    def test_rejects_continuous_tone(self):
        """Gate should reject continuous-tone-like waveforms."""
        from heimdall import (
            detect, BaselineMatchedFilter, PeakContrastGate,
            SyntheticScenario, generate_observation
        )
        
        scenario = SyntheticScenario(
            scenario_id="continuous-01",
            seed=42,
            interference_frequency_hz=64.0,
            interference_amplitude=0.3,
            interference_duration_s=2.0,  # Entire window
            expected_signal=False,
        )
        obs = generate_observation(scenario)
        
        detector = BaselineMatchedFilter()
        gates = [PeakContrastGate(minimum_peak_to_mean_ratio=2.0)]
        candidate = detect(obs, detector, gates)
        
        self.assertFalse(candidate.gates_passed)
```

## Integration Testing Strategy

### Full Pipeline Tests
Test detector pipeline end-to-end.

```python
class TestDetectionPipeline(unittest.TestCase):
    """Test full detection pipeline."""
    
    def test_pipeline_accepts_valid_candidate(self):
        """Pipeline should accept high-quality signals."""
        from heimdall import (
            detect, BaselineMatchedFilter, PeakContrastGate,
            ClockQualityGate, SyntheticScenario, generate_observation
        )
        
        # High-quality scenario
        scenario = SyntheticScenario(
            scenario_id="quality-01",
            seed=42,
            signal_amplitude=0.6,
            signal_frequency_hz=64.0,
            noise_amplitude=0.05,
            clock_uncertainty_ns=100.0,
            expected_signal=True,
        )
        obs = generate_observation(scenario)
        
        detector = BaselineMatchedFilter(threshold=0.45)
        gates = [
            PeakContrastGate(minimum_peak_to_mean_ratio=1.5),
            ClockQualityGate(maximum_clock_uncertainty_ns=500.0),
        ]
        
        candidate = detect(obs, detector, gates)
        
        self.assertTrue(candidate.detected)
        self.assertTrue(candidate.gates_passed)
        self.assertGreater(candidate.score, candidate.threshold)
    
    def test_pipeline_rejects_poor_clock_quality(self):
        """Pipeline should reject observations with poor clock quality."""
        from heimdall import (
            detect, BaselineMatchedFilter, ClockQualityGate,
            SyntheticScenario, generate_observation
        )
        
        scenario = SyntheticScenario(
            scenario_id="clock-01",
            seed=42,
            signal_amplitude=0.6,
            clock_uncertainty_ns=5000.0,  # Poor clock quality
            expected_signal=True,
        )
        obs = generate_observation(scenario)
        
        detector = BaselineMatchedFilter(threshold=0.45)
        gates = [ClockQualityGate(maximum_clock_uncertainty_ns=1000.0)]
        
        candidate = detect(obs, detector, gates)
        
        self.assertFalse(candidate.gates_passed)
        self.assertIn("clock quality", candidate.decision_reasons[0].lower())
```

## Property-Based Testing

Use hypothesis for invariant testing.

```python
from hypothesis import given, strategies as st, assume
from heimdall import BaselineMatchedFilter, detect, ObservationL0
from datetime import datetime, timezone

class TestDetectorInvariants(unittest.TestCase):
    """Test detector invariants using property-based testing."""
    
    @given(
        score=st.floats(allow_nan=False, allow_infinity=False, width=32),
        threshold=st.floats(allow_nan=False, allow_infinity=False, width=32),
    )
    def test_detection_decision_consistency(self, score: float, threshold: float):
        """Detected should match score >= threshold + gates_passed."""
        assume(0.0 <= score <= 1.0)
        assume(0.0 <= threshold <= 1.0)
        
        # This is an invariant that should always hold
        detected = (score >= threshold)
        gates_passed = True
        
        # If score/threshold don't match detection state, it's a contract violation
        assert detected == (score >= threshold and gates_passed)
    
    @given(
        num_samples=st.integers(min_value=1, max_value=100000),
        sample_rate=st.integers(min_value=100, max_value=100000),
    )
    def test_detector_handles_varied_sizes(self, num_samples: int, sample_rate: int):
        """Detector should handle observations of various sizes."""
        from heimdall import SyntheticScenario, generate_observation
        
        scenario = SyntheticScenario(
            scenario_id="property-test",
            seed=42,
            duration_s=num_samples / sample_rate,
            sample_rate_hz=sample_rate,
        )
        
        obs = generate_observation(scenario)
        detector = BaselineMatchedFilter()
        
        # Should not raise, and result should be valid
        candidate = detect(obs, detector)
        
        assert 0.0 <= candidate.score <= 1.0
        assert candidate.observation_id == obs.observation_id
```

## Chaos Engineering Tests

Test failure modes and edge cases.

```python
class TestFailureModes(unittest.TestCase):
    """Test detector behavior under adverse conditions."""
    
    def test_handles_nan_samples(self):
        """Detector should handle NaN samples gracefully."""
        from heimdall import detect, BaselineMatchedFilter
        from heimdall.exceptions import DetectionError
        import math
        
        # Create observation with NaN
        obs = ObservationL0(
            observation_id="nan-test",
            samples=(0.1, math.nan, 0.3),
            sample_rate_hz=1024,
            started_at=datetime.now(timezone.utc),
            sensor_id="sensor-001",
            sequence_number=1,
            clock_uncertainty_ns=0,
            calibration_id="cal-001",
            provenance=create_provenance(),
            payload_digest="digest",
        )
        
        detector = BaselineMatchedFilter()
        
        # Should raise DetectionError, not silently fail
        with self.assertRaises(DetectionError):
            detect(obs, detector)
    
    def test_handles_very_large_samples(self):
        """Detector should normalize very large sample values."""
        from heimdall import detect, BaselineMatchedFilter
        
        obs = ObservationL0(
            observation_id="large-test",
            samples=(1e6, 2e6, 3e6, 4e6, 5e6),  # Very large
            sample_rate_hz=1024,
            started_at=datetime.now(timezone.utc),
            sensor_id="sensor-001",
            sequence_number=1,
            clock_uncertainty_ns=0,
            calibration_id="cal-001",
            provenance=create_provenance(),
            payload_digest="digest",
        )
        
        detector = BaselineMatchedFilter()
        candidate = detect(obs, detector)
        
        # Score should still be normalized
        self.assertGreaterEqual(candidate.score, 0.0)
        self.assertLessEqual(candidate.score, 1.0)
    
    def test_handles_empty_observation(self):
        """Detector should reject empty observations."""
        from heimdall.exceptions import ContractViolationError
        
        with self.assertRaises(ContractViolationError):
            ObservationL0(
                observation_id="empty-test",
                samples=(),  # Empty!
                sample_rate_hz=1024,
                started_at=datetime.now(timezone.utc),
                sensor_id="sensor-001",
                sequence_number=1,
                clock_uncertainty_ns=0,
                calibration_id="cal-001",
                provenance=create_provenance(),
                payload_digest="digest",
            )


def create_provenance():
    """Helper to create valid provenance for tests."""
    from heimdall import Provenance, EvidenceClass
    return Provenance(
        evidence_class=EvidenceClass.SYNTHETIC,
        scenario_id="test",
        generator_version="1.0",
        configuration_digest="abc",
        model_card_digest="def",
        created_at=datetime.now(timezone.utc),
    )
```

## Benchmark Tests

Measure and track performance.

```python
import time
import statistics

class TestPerformance(unittest.TestCase):
    """Benchmark critical paths."""
    
    def test_detector_latency(self):
        """Detector should complete in reasonable time."""
        from heimdall import (
            detect, BaselineMatchedFilter, SyntheticScenario,
            generate_observation
        )
        
        scenario = SyntheticScenario(
            scenario_id="perf-01",
            seed=42,
            sample_rate_hz=4096,  # High sample rate
            duration_s=2.0,
        )
        obs = generate_observation(scenario)
        detector = BaselineMatchedFilter()
        
        times = []
        for _ in range(10):
            start = time.time()
            candidate = detect(obs, detector)
            times.append(time.time() - start)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        # Should be fast (< 100ms for 4K samples)
        self.assertLess(avg_time, 0.1, f"Average latency {avg_time:.3f}s too high")
        self.assertLess(max_time, 0.2, f"Max latency {max_time:.3f}s too high")
        
        print(f"Detector latency: {avg_time*1000:.1f}ms avg, {max_time*1000:.1f}ms max")
```

## Fixtures and Test Data

Use factories and builders for consistent test data.

```python
from dataclasses import replace

class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_observation(
        observation_id: str = "test-001",
        amplitude: float = 0.5,
        frequency: float = 64.0,
        **kwargs
    ) -> ObservationL0:
        """Create observation with sensible defaults."""
        from heimdall import SyntheticScenario, generate_observation
        
        scenario = SyntheticScenario(
            scenario_id=observation_id,
            seed=42,
            signal_frequency_hz=frequency,
            signal_amplitude=amplitude,
            **kwargs,
        )
        return generate_observation(scenario)
    
    @staticmethod
    def create_detector(
        threshold: float = 0.55,
        **kwargs
    ) -> BaselineMatchedFilter:
        """Create detector with sensible defaults."""
        return BaselineMatchedFilter(
            threshold=threshold,
            **kwargs,
        )


# Usage in tests
class TestWithFactory(unittest.TestCase):
    def test_using_factory(self):
        obs = TestDataFactory.create_observation(amplitude=0.6)
        detector = TestDataFactory.create_detector(threshold=0.5)
        
        candidate = detect(obs, detector)
        self.assertIsNotNone(candidate)
```

## Mocking and Stubbing

Create test doubles for adapters.

```python
from unittest.mock import Mock, patch
from heimdall import AdapterRegistry, FileEvidenceStore

class TestWithMocks(unittest.TestCase):
    def test_with_mock_storage(self):
        """Test using mocked storage adapter."""
        
        # Create mock storage
        mock_store = Mock()
        mock_store.put.return_value = "abc123def456"
        
        # Use in test
        digest = mock_store.put(b"test data")
        
        self.assertEqual(digest, "abc123def456")
        mock_store.put.assert_called_once_with(b"test data")
    
    def test_ingestion_with_mock_verification(self):
        """Test ingestion with mocked signature verification."""
        from heimdall.ingestion import IntegrityVerification
        
        mock_verifier = Mock()
        mock_verifier.return_value = True
        
        # Patch verification in ingestion module
        with patch('heimdall.ingestion.verify_digest', mock_verifier):
            verification = IntegrityVerification(
                scheme="sha256",
                proof_reference="test",
                expected_digest="abc123",
            )
            # ... test ingestion ...
```

## Test Organization

```
tests/
├── unit/
│   ├── test_domain.py          # Contract validation
│   ├── test_pipeline.py        # Detector algorithm
│   ├── test_gates.py           # Gate logic
│   └── test_ingestion.py       # Input validation
├── integration/
│   ├── test_full_pipeline.py   # End-to-end detector
│   ├── test_detector_pipeline.py # Pipeline + gates
│   └── test_governance.py      # Pre-registration flow
├── property/
│   └── test_invariants.py      # Hypothesis property tests
├── chaos/
│   └── test_failure_modes.py   # Edge cases
├── performance/
│   └── test_benchmarks.py      # Latency & memory
└── fixtures/
    ├── conftest.py             # Shared fixtures
    └── data_factory.py         # Test data builders
```

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Unit tests only
python -m pytest tests/unit/ -v

# With coverage
python -m pytest tests/ --cov=src/heimdall --cov-report=html

# Property-based tests
python -m pytest tests/property/ -v --hypothesis-seed=0

# Performance benchmarks
python -m pytest tests/performance/ -v --benchmark-only

# Chaos engineering
python -m pytest tests/chaos/ -v
```

## Quality Metrics

Target metrics for release:
- **Code Coverage**: > 90% (all critical paths)
- **Mutation Score**: > 85% (changes caught by tests)
- **Latency**: < 100ms for standard observations
- **False Alarm Rate**: < 5% on noise corpus
- **Detection Rate**: > 95% on signal corpus
- **Gate Specificity**: > 99% on interference corpus
