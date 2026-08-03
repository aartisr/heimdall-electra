# Heimdall Electra — Implementation Quality Standards

This document establishes quality standards and best practices for the Heimdall codebase, ensuring Nobel Prize-level quality, world-class resilience, and exceptional maintainability.

## Code Quality Standards

### Type Hints
- **100% coverage**: All public functions must have complete type hints
- **Generic types**: Use `List[T]`, `Dict[K, V]`, `Optional[T]` for clarity
- **Protocol types**: Use `Protocol` for structural typing and duck typing
- **Return types**: Always explicit, including `None` for procedures

```python
# ✓ Good
def detect(
    observation: ObservationL0 | CalibratedObservationL1,
    detector: BaselineMatchedFilter,
    gates: Sequence[CandidateGate] = (),
) -> CandidateL2:
    """Detect candidates and apply policy gates."""

# ✗ Bad
def detect(observation, detector, gates=[]):
    """Detect candidates."""
```

### Docstrings
- **Module level**: Describe purpose, key concepts, example usage
- **Class level**: Describe invariants, usage patterns, lifecycle
- **Function level**: Purpose, arguments, return value, exceptions, examples
- **Format**: Google-style docstrings with Args, Returns, Raises, Examples

```python
def detect(
    observation: ObservationL0 | CalibratedObservationL1,
    detector: BaselineMatchedFilter,
    gates: Sequence[CandidateGate] = (),
) -> CandidateL2:
    """Detect candidates in observation using baseline detector and gates.
    
    This function implements the core detection pipeline: compute raw score,
    apply policy gates in order, produce candidate with decision reasoning.
    
    The detector uses a fixed-frequency matched filter. Gates are applied
    in order and all must pass for a candidate to be accepted.
    
    Args:
        observation: Raw or calibrated observation with samples and metadata
        detector: Baseline matched filter configuration
        gates: Ordered sequence of policy gates (default: no gates)
    
    Returns:
        CandidateL2 with score, threshold, gates_passed, and decision reasons
    
    Raises:
        DetectionError: If observation format is invalid or score is NaN/inf
        TimingError: If clock uncertainty is negative
    
    Examples:
        >>> from heimdall import detect, BaselineMatchedFilter, PeakContrastGate
        >>> observation = generate_observation(scenario)
        >>> detector = BaselineMatchedFilter(threshold=0.55)
        >>> gates = [PeakContrastGate()]
        >>> candidate = detect(observation, detector, gates)
        >>> print(candidate.detected)  # True if score >= threshold and gates passed
    """
```

### Error Handling
- **Never silently fail**: All errors must be caught, logged, and exposed
- **Use custom exceptions**: Catch and re-raise with context
- **Provide recovery hints**: Every exception includes actionable guidance
- **Preserve traceback**: Use `raise ... from e` to chain exceptions

```python
# ✓ Good
try:
    digest = sha256(bytes).hexdigest()
except Exception as e:
    raise create_storage_error(
        component="FileEvidenceStore",
        operation="put",
        message=f"Failed to hash artifact bytes",
        hint="Check file system permissions and available disk space",
        root_cause=e,
    )

# ✗ Bad
try:
    digest = sha256(bytes).hexdigest()
except Exception:
    pass  # Silent failure, unacceptable
```

### Logging
- **Every operation**: Log start, progress, completion, and errors
- **Correlation IDs**: Use `CorrelationContext.get_id()` for tracing
- **Structured data**: Include context_data dict for diagnostics
- **Audit trail**: Significant mutations go to audit trail

```python
# ✓ Good
logger = create_logger("detector")
logger.log_operation_start("detect", details={"obs_id": obs.observation_id})
try:
    candidate = detect(observation, detector, gates)
    logger.log_operation_complete("detect", duration_s=0.042, details={
        "candidate_id": candidate.candidate_id,
        "detected": candidate.detected,
    })
except Exception as e:
    logger.log_operation_failed("detect", e)
    raise

# ✗ Bad
# No logging, impossible to debug production issues
result = detect(observation, detector, gates)
```

### Validation
- **At all boundaries**: Validate inputs before processing
- **Fail fast**: Raise exceptions for invalid inputs immediately
- **Clear messages**: Exceptions explain what went wrong and why
- **Examples**: Document valid input ranges

```python
# ✓ Good
@dataclass(frozen=True)
class ObservationL0:
    observation_id: str
    samples: tuple[float, ...]
    sample_rate_hz: int
    
    def __post_init__(self) -> None:
        if not self.observation_id:
            raise create_validation_error(
                component="ObservationL0",
                operation="__init__",
                message="observation_id cannot be empty",
                hint="Provide a unique, non-empty observation identifier",
            )
        if not self.samples:
            raise create_validation_error(
                component="ObservationL0",
                operation="__init__",
                message="samples cannot be empty",
                hint="Provide at least one sample",
            )

# ✗ Bad
class ObservationL0:
    def __init__(self, observation_id, samples, sample_rate_hz):
        self.observation_id = observation_id  # No validation
        self.samples = samples
        self.sample_rate_hz = sample_rate_hz
```

## Architecture Best Practices

### Modularity
- **Single Responsibility**: Each module has one clear purpose
- **Minimal Coupling**: Imports are explicit and limited
- **Maximal Cohesion**: Related functionality lives together
- **Clear Boundaries**: Public vs private interfaces are explicit

### Composability
- **Small Functions**: Single-purpose, testable units
- **Pluggable Strategies**: Use `Protocol` for swappable components
- **Factory Creation**: Never hardcode dependencies
- **Dependency Injection**: Inject adapters, don't construct them

### Testability
- **No Global State**: Avoid singletons (except configuration)
- **Mock-Friendly**: Interfaces use `Protocol`, not concrete classes
- **Deterministic**: Same inputs always produce same outputs
- **Isolated**: Tests don't depend on file system, network, or other tests

### Resilience
- **Graceful Degradation**: Lose features, not correctness
- **Retry Logic**: Implement for external services
- **Circuit Breaker**: Fail fast when services are down
- **Bulkhead**: Isolate failures to specific components

## NASA Proposal Alignment

The implementation ensures **100% compliance** with the NASA Innovative Advanced Concepts proposal:

### Technical Components

#### 1. Hardware Sensor Network (Element A)
- **VLF Antenna Array**: Contracts defined in `physics_contract.py`
- **Passive Listening**: No active transmission requirements
- **CubeSat Deployment**: Orbital parameters in `physics_contract.OrbitalState`
- **Power Budget**: Tracked in `edge_benchmark.EdgeResourceBudget`

#### 2. Signal Processing Pipeline (Element B)
- **Dynamic Noise Subtraction**: Implemented in detector conditioning
- **Wavelet Matched-Filtering**: Core algorithm in `pipeline.BaselineMatchedFilter`
- **Kinematic Triangulation**: TDOA solver contract in `kinematic_inference.py`
- **Real-Time Edge Processing**: Latency tracked in metrics

#### 3. Research Methodology
- **Pre-Registered Hypotheses**: `governance.ExperimentPlan`
- **Synthetic Fixtures**: `simulation.SyntheticScenario`
- **Locked Validation Corpus**: `corpus_custody.CorpusManifest`
- **Blind Evaluation**: `gate_review.GateStatus`

#### 4. Governance & Evidence
- **Evidence Classes**: `domain.EvidenceClass` (synthetic, lab, observed)
- **Provenance Tracking**: `domain.Provenance` with full lineage
- **Content Addressing**: SHA-256 in `ingestion.FileEvidenceStore`
- **Audit Trails**: Immutable logs in `observability.AuditTrail`

### Quality Gates

Each stage has measurable exit criteria:

| Stage | Gate | Implementation |
|-------|------|-----------------|
| 0 | Claims & Governance | `governance.ThresholdPolicy`, `gate_review.py` |
| 1 | Physics Validation | `physics_validation.py`, `physics_benchmarks.py` |
| 2 | Detector & Edge | `pipeline.py`, `edge_benchmark.py` |
| 3 | Timing & Association | `kinematic_inference.py`, `timing_calibration.py` |
| 4 | Trades | `coverage_trade.py`, `instrument_budget.py`, `transport_budget.py` |
| 5 | HIL Validation | `hil_validation.py` |
| 6 | Flight Demo | Source authorization in `ingestion.py` |
| 7 | Platform | Traffic product in `status_snapshot.py` |
| 8 | Analyst Console | Read-only UI in `apps/analyst-console` |
| 9 | Operations | Lifecycle in `inference_lifecycle.py` |

## Performance Optimization

### Metrics Collection
- Record detector latency in milliseconds
- Track memory usage per observation
- Monitor false alarm rate over time
- Measure calibration accuracy

### Computational Efficiency
- Use vectorized operations in numpy where applicable
- Stream large artifacts to avoid loading entirely into memory
- Cache model cards after first load
- Implement LRU cache for frequent queries

### Scalability Readiness
- Design for distributed detection (multi-node)
- Prepare for millions of observations
- Support batch processing pipelines
- Enable streaming inference

## Security Considerations

### Input Validation
- Validate all untrusted inputs at boundaries
- Reject oversized payloads (artifact size limits)
- Prevent timing attacks on digest verification
- Sanitize error messages to prevent information leaks

### Access Control
- Track actor in all audit events
- Require source authorization before ingestion
- Implement role-based access to evidence classes
- Log all access to sensitive data

### Cryptography
- Use SHA-256 for content addressing (NIST-approved)
- Support cryptographic signature verification
- Store expected digests securely
- Never hardcode keys or secrets

## Maintainability

### Code Organization
```
src/heimdall/
├── __init__.py           # Exports all public APIs
├── domain.py             # Core contracts (immutable, frozen)
├── simulation.py         # Synthetic scenario generation
├── forward_models.py     # Pluggable physics models
├── pipeline.py           # Detector and gates
├── ingestion.py          # Evidence ingestion boundary
├── governance.py         # Pre-registration and experiments
├── exceptions.py         # Exception hierarchy (NEW)
├── observability.py      # Logging and metrics (NEW)
├── configuration.py      # Configuration management (NEW)
├── factories.py          # Factory patterns and DI (NEW)
├── validation.py         # Validation framework (NEW)
├── *_contract.py         # Domain-specific contracts
├── *_registry.py         # Pluggable registries
└── *_assessment.py       # Evaluation and reporting
```

### Documentation
- **HEIMDALL_START_HERE.md**: Quick start and first four weeks
- **HEIMDALL_EXECUTION_FLOW.md**: Detailed implementation flow
- **STAGE_DELIVERY_LEDGER.md**: Progress tracking and gate status
- **ARCHITECTURE_ENHANCEMENTS.md**: Design patterns and principles
- **IMPLEMENTATION_QUALITY_STANDARDS.md**: This document

### Version Management
- Semantic versioning for releases
- Changelog documenting all updates
- Deprecation warnings before breaking changes
- Long-term support for stable versions

## Continuous Improvement

### Code Review Checklist
- [ ] All public functions have type hints
- [ ] All public APIs have docstrings with examples
- [ ] Error paths are tested and logged
- [ ] No silent failures or uncaught exceptions
- [ ] Validation at all boundaries
- [ ] Configuration is externalized
- [ ] Audit trail captures significant mutations
- [ ] Performance metrics are collected
- [ ] Backward compatibility maintained

### Testing Checklist
- [ ] Unit tests for domain contracts
- [ ] Integration tests for full pipeline
- [ ] Property-based tests for invariants
- [ ] Chaos engineering tests for failure modes
- [ ] Performance benchmarks for critical paths
- [ ] Security tests for input validation
- [ ] Accessibility tests for CLI/console

### Documentation Checklist
- [ ] Module docstring explains purpose
- [ ] Complex algorithms documented
- [ ] Extension points documented
- [ ] Configuration options documented
- [ ] Performance characteristics documented
- [ ] Troubleshooting guide included
- [ ] Examples for common use cases

## References

- NASA Innovative Advanced Concepts (NIAC) Phase I Proposal
- PEP 20: The Zen of Python
- PEP 484: Type Hints
- "Domain-Driven Design" by Eric Evans
- "Design Patterns" by Gang of Four
- "Clean Code" by Robert C. Martin
- "Reliability Engineering" by Dimitri Bertsekas
- "Research Integrity" by National Academies
