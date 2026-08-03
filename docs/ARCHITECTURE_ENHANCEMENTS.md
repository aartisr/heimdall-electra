# Heimdall Electra — Enhanced Architecture & Patterns

This document describes the enhanced software architecture, design patterns, and best practices implemented across the Heimdall research codebase.

## Core Principles

1. **Type Safety**: All public APIs use complete type hints
2. **Immutability**: Domain objects are frozen dataclasses where appropriate
3. **Fail Fast**: Validation happens at boundaries with clear error messages
4. **Observability**: Every operation is logged and traceable
5. **Composability**: Components are loosely coupled and highly composable
6. **Testability**: All interfaces have test doubles available
7. **Resilience**: Graceful degradation and comprehensive error handling

## Architecture Layers

### 1. Domain Layer (`domain.py`, `*_contract.py`)
**Purpose**: Immutable contracts for scientific evidence

Core contracts:
- `ObservationL0`: Raw instrument measurements with provenance
- `CalibratedObservationL1`: Calibrated measurements with quality metadata
- `CandidateL2`: Detector output with decision and uncertainty
- `Provenance`: Complete lineage tracking for evidence

Key principles:
- Frozen dataclasses prevent accidental mutation
- `__post_init__` validation is exhaustive
- All fields are required (no optional without reason)
- Content is immutable after construction

### 2. Processing Layer (`pipeline.py`, `detector.py`)
**Purpose**: Stateless scientific algorithms

Patterns:
- **Strategy Pattern**: `CandidateGate` interface for pluggable gates
- **Factory Pattern**: Detectors constructed with explicit configuration
- **Dependency Injection**: Gates injected into detector

Example:
```python
detector = BaselineMatchedFilter(
    detector_id="my-detector-v1",
    threshold=0.65,
)
gates = [PeakContrastGate(minimum_peak_to_mean_ratio=1.75)]
candidate = detect(observation, detector, gates)
```

### 3. Governance Layer (`governance.py`, `ingestion.py`)
**Purpose**: Evidence authorization and chain-of-custody

Key concepts:
- **Source Registry**: Approved sources with allowed evidence classes
- **Integrity Verification**: Digest/signature validation
- **Content Addressing**: SHA-256 immutable storage
- **Manifest Ledger**: Append-only acquisition records
- **Experiment Plan**: Pre-registered hypothesis and metrics

Patterns:
- **Adapter Pattern**: Pluggable verification schemes
- **Repository Pattern**: Persistent ledger access
- **Builder Pattern**: Complex configuration objects

### 4. Infrastructure Layer

#### Exception Handling (`exceptions.py`)
**Purpose**: Rich, actionable error context

Hierarchy:
```
HeimdallException
├── ContractViolationError (FATAL)
├── IngestionBoundaryError (VALIDATION/RECOVERABLE)
├── StorageError (FATAL)
├── DetectionError (RECOVERABLE)
├── TimingError (FATAL)
├── ConfigurationError (FATAL)
├── ValidationError (VALIDATION)
└── ExternalServiceError (RECOVERABLE)
```

Each exception includes:
- `ErrorContext` with domain, severity, component, operation
- Actionable hints for remediation
- Context data for diagnostics
- Root cause chain

#### Observability (`observability.py`)
**Purpose**: Structured logging, auditing, and metrics

Components:
- **StructuredLogger**: JSON-ready logging with correlation IDs
- **AuditTrail**: Append-only event log for regulatory compliance
- **CorrelationContext**: Thread-local request tracing
- **MetricsCollector**: Non-blocking performance metrics

Usage:
```python
logger = create_logger("detector")
logger.log_operation_start("detect", details={"observation_id": obs.observation_id})
# ... operation ...
logger.log_operation_complete("detect", duration_s=0.042)
```

#### Configuration Management (`configuration.py`)
**Purpose**: Type-safe, validated configuration

Key classes:
- **ConfigurationSchema**: Declarative field validation
- **ConfigField**: Type, constraints, defaults
- **Configuration**: Type-safe accessor with validation
- **ConfigurationManager**: Lifecycle and loading

Example:
```python
schema = ConfigurationSchema("detector-config")
schema.add_field(ConfigField(
    name="threshold",
    value_type=ConfigValueType.FLOAT,
    constraints=[ConfigConstraint("min", 0.0), ConfigConstraint("max", 1.0)],
    required=True,
))
config = manager.load_from_dict("detector-config", {"threshold": 0.65})
threshold = config.get_float("threshold")
```

#### Factories & Dependency Injection (`factories.py`)
**Purpose**: Composable object creation and lifecycle

Patterns:
- **SingletonFactory**: Create once, reuse
- **MultitonFactory**: Multiple named instances
- **AdapterRegistry**: Pluggable implementations by name
- **DependencyContainer**: IoC container for all factories
- **LifecycleManager**: Setup/teardown hooks

Example:
```python
container = get_container()

# Register adapter implementations
registry = AdapterRegistry(Detector)
registry.register("baseline", BaselineMatchedFilter)
registry.register("ml-v1", MLDetector)
container.register_adapter_registry("detector", registry)

# Create instances
detector = container.get_adapter_registry("detector").create("baseline")
```

#### Validation & Verification (`validation.py`)
**Purpose**: Composable validation and verification chains

Key concepts:
- **Validator**: Composes into chains
- **ValidationReport**: Comprehensive error reporting
- **VerificationChain**: Chain of responsibility for checks

Example:
```python
validator = (
    RangeValidator(0.0, 1.0, "score")
    .chain(PatternValidator(r"[a-z0-9-]+", "detector_id"))
)
report = validator.validate(candidate)
if not report.is_valid():
    for error in report.errors:
        print(f"{error.field}: {error.message}")
```

## Design Patterns Used

| Pattern | Module | Purpose |
|---------|--------|---------|
| **Adapter** | ingestion, factories | Pluggable implementations |
| **Factory** | factories | Object creation |
| **Builder** | simulation, domain | Complex configuration |
| **Strategy** | pipeline, governance | Swappable algorithms |
| **Chain of Responsibility** | validation, gates | Sequential processing |
| **Repository** | ingestion, governance | Data access abstraction |
| **Specification** | validation | Query/filter definition |
| **Observer** | observability | Event notification |
| **Singleton** | factories, configuration | Single shared instance |
| **Decorator** | observability, validation | Behavior enhancement |

## Resilience & Error Handling

### Fail-Fast Validation
```python
# All contract violations detected immediately
try:
    obs = ObservationL0(
        observation_id="",  # Empty ID
        samples=(),  # Empty samples
        ...
    )
except ContractViolationError as e:
    print(e.context.message)  # Clear error message
    print(e.context.hint)  # Recovery suggestion
```

### Graceful Degradation
```python
# Detection continues even if a gate fails
gates = [PeakContrastGate(), ClockQualityGate()]
candidate = detect(observation, detector, gates)
# candidate.gates_passed indicates which gates passed
# candidate.decision_reasons explains rejections
```

### Comprehensive Logging
```python
# Every significant operation is traced
logger = create_logger("detector", audit_trail_path=Path("audit.jsonl"))
logger.log_event(
    EventKind.DETECTION,
    "detect",
    "Detector executed successfully",
    details={"score": 0.78, "threshold": 0.65},
)
# audit.jsonl contains immutable record for compliance
```

## Testing Strategy

### Unit Testing
- Mock all external adapters
- Test domain contracts exhaustively
- Validate error paths

### Integration Testing
- Use real file-based adapters for storage
- Test full pipeline with fixtures
- Verify audit trail integrity

### Property-Based Testing
- Generate random inputs
- Verify invariants hold
- Catch edge cases

## Extension Points

### Adding a New Detector
```python
class MyDetector:
    detector_id = "my-detector"
    detector_version = "1.0.0"
    
    def detect(self, observation, **kwargs):
        # ... implementation ...
        return CandidateL2(...)

# Register with container
registry = container.get_adapter_registry("detector")
registry.register("my-detector", MyDetector)
```

### Adding a New Gate
```python
class MyGate:
    gate_id = "my-gate/1.0.0"
    
    def assess(self, context: DetectionContext) -> GateDecision:
        passed = self._my_check(context)
        return GateDecision(
            gate_id=self.gate_id,
            passed=passed,
            reason="..." if passed else "...",
            metrics={},
        )

# Use in pipeline
gates = [MyGate()]
candidate = detect(observation, detector, gates)
```

### Adding a New Verification Source
```python
class MySource(DataSource):
    def __init__(self):
        super().__init__(
            source_id="my-source",
            kind=SourceKind.PARTNER,
            owner="my-org",
            terms_reference="https://...",
            approved=False,  # Requires review
            allowed_evidence_classes=(EvidenceClass.OBSERVED,),
            allowed_verification_schemes=("my-signature", "sha256"),
        )

# Register and use
registry.register("my-source", MySource())
```

## Performance Considerations

### Metrics Collection
- Non-blocking metric collection
- Metrics never block detector operations
- Periodic aggregation and export

### Memory Efficiency
- Use generators for large sequences
- Stream ingestion for large artifacts
- Content addressing prevents duplicates

### Computational Efficiency
- Vectorize detector operations where possible
- Use FFT for frequency-domain filtering
- Cache model cards and calibration data

## Backward Compatibility

All enhancements maintain backward compatibility:
- Domain contracts are unchanged
- Core functions have same signatures
- New features are opt-in via imports
- Existing code continues to work

## Future Enhancements

Planned improvements:
1. **Async/Await**: Non-blocking I/O for external services
2. **Distributed Tracing**: OpenTelemetry integration
3. **Plugin System**: Dynamic loading of extensions
4. **GraphQL API**: Flexible query interface
5. **Caching Layer**: Redis-backed result caching
6. **Rate Limiting**: Backpressure control
7. **Circuit Breaker**: Fault tolerance for external services
8. **Event Streaming**: Kafka/NATS integration for multi-node

## Migration Guide

Updating existing code:
```python
# Old approach (still works)
from heimdall import detect, BaselineMatchedFilter
candidate = detect(observation, BaselineMatchedFilter())

# Enhanced approach (recommended)
from heimdall import (
    detect, BaselineMatchedFilter, PeakContrastGate,
    create_logger, get_container
)
logger = create_logger("my-app")
logger.log_operation_start("detect")
gates = [PeakContrastGate()]
candidate = detect(observation, BaselineMatchedFilter(), gates)
logger.log_operation_complete("detect", 0.042)
```

## References

- **Design Patterns**: Gamma et al., "Design Patterns: Elements of Reusable Object-Oriented Software"
- **Domain-Driven Design**: Evans, "Domain-Driven Design: Tackling Complexity in the Heart of Software"
- **Python Best Practices**: PEP 20, PEP 484, PEP 586
- **Research Ethics**: "Falsifiability and Research Integrity in ML"
