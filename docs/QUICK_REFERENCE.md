# Heimdall Electra — Quick Reference Guide

Fast lookup reference for new infrastructure modules.

## Module Quick Links

| Module | Purpose | Key Classes | Typical Import |
|--------|---------|-------------|-----------------|
| **exceptions.py** | Rich error handling | HeimdallException, ErrorContext | `from heimdall import ContractViolationError, create_detection_error` |
| **observability.py** | Logging & audit trails | StructuredLogger, AuditTrail | `from heimdall import create_logger, CorrelationContext` |
| **configuration.py** | Config management | Configuration, ConfigurationSchema | `from heimdall import ConfigurationManager, ConfigField` |
| **factories.py** | Dependency injection | DependencyContainer, AdapterRegistry | `from heimdall import get_container, SingletonFactory` |
| **validation.py** | Validators | Validator, ChainedValidator | `from heimdall import RangeValidator, PatternValidator` |

## Exception Handling Patterns

### Basic Exception Raising
```python
from heimdall import create_detection_error, DetectionError

try:
    # ... operation ...
    if not valid:
        raise create_detection_error(
            component="BaselineMatchedFilter",
            operation="detect",
            message="Filter failed on observation",
            hint="Check input observation for corruption",
        )
except DetectionError as e:
    print(f"Hint: {e.context.hint}")
    raise
```

### Exception Catching with Context
```python
from heimdall import ContractViolationError, ErrorSeverity

try:
    obs = ObservationL0(...)
except ContractViolationError as e:
    if e.context.severity == ErrorSeverity.FATAL:
        # Critical error - don't proceed
        sys.exit(1)
    else:
        # Degraded - continue with caution
        logger.warning(e.context.hint)
```

## Logging Patterns

### Structured Logging
```python
from heimdall import create_logger, CorrelationContext

logger = create_logger("detector")
CorrelationContext.set_id("550e8400-e29b-41d4-a716-446655440000")

logger.log_operation_start("detect", actor="service", details={"count": 100})
try:
    result = detector.detect(obs)
    logger.log_operation_complete("detect", duration_s=0.042)
except Exception as e:
    logger.log_operation_failed("detect", e)
    raise
```

### Automatic Timing
```python
from heimdall.observability import timed_operation

@logger.timed_operation("detect")
def my_detect_function(obs, detector):
    # Automatically logs start, duration, completion
    return detect(obs, detector)
```

### Event Logging
```python
from heimdall import EventKind

logger.log_validation("validate_obs", passed=True, message="All checks passed")
logger.log_validation("validate_obs", passed=False, message="Saturation detected")
```

## Configuration Patterns

### Define Schema
```python
from heimdall import ConfigurationSchema, ConfigField, ConfigValueType, ConfigConstraint

schema = ConfigurationSchema("detector")
schema.add_field(ConfigField(
    name="threshold",
    value_type=ConfigValueType.FLOAT,
    constraints=[ConfigConstraint("min", 0.0), ConfigConstraint("max", 1.0)],
    required=True,
))
schema.add_field(ConfigField(
    name="window_size",
    value_type=ConfigValueType.INTEGER,
    constraints=[ConfigConstraint("min", 1)],
    default=256,
))
```

### Load Configuration
```python
from heimdall import ConfigurationManager
from pathlib import Path

manager = ConfigurationManager()
config = manager.load_from_file("detector", Path("detector.json"), schema)

# Type-safe access
threshold = config.get_float("threshold")  # Returns float
window = config.get_int("window_size")     # Returns int
```

### Load from Environment
```python
# With environment variables HEIMDALL_DETECTOR_THRESHOLD=0.65, etc.
config = manager.load_from_env("detector", prefix="HEIMDALL_DETECTOR", schema=schema)
threshold = config.get_float("threshold")  # 0.65
```

## Dependency Injection Patterns

### Create Singleton
```python
from heimdall import get_container

container = get_container()

# Register singleton
metrics = MetricsCollector()
container.register_singleton("metrics", metrics)

# Retrieve in other components
retrieved = container.get_singleton("metrics")
assert retrieved is metrics  # Same instance
```

### Register Adapter Registry
```python
from heimdall import AdapterRegistry, Detector

registry = AdapterRegistry(Detector)
registry.register("baseline", BaselineMatchedFilter)
registry.register("ml", MLDetector)

container.register_adapter_registry("detector", registry)

# Later, create instances
detector = container.get_adapter_registry("detector").create("baseline")
```

### Custom Factory
```python
from heimdall import Factory, SingletonFactory

class LoggerFactory(Factory):
    def __init__(self):
        self._loggers = {}
    
    def create(self, name: str):
        if name not in self._loggers:
            from heimdall import create_logger
            self._loggers[name] = create_logger(name)
        return self._loggers[name]

container.register_factory("logger", LoggerFactory())
```

## Validation Patterns

### Chain Validators
```python
from heimdall import RangeValidator, PatternValidator

validator = (
    RangeValidator(0.0, 1.0, "score")
    .chain(RangeValidator(0, 100, "count"))
    .chain(PatternValidator(r"[a-z0-9-]+", "id"))
)

report = validator.validate(candidate)
if not report.is_valid():
    for error in report.errors:
        print(f"{error.field}: {error.message}")
        print(f"  Hint: {error.hint}")
```

### Custom Validator
```python
from heimdall import CustomValidator, ValidationReport

def validate_no_saturation(obs):
    """Check that no samples are saturated."""
    max_sample = max(obs.samples)
    if max_sample > 100:
        return ValidationReport(
            result=ValidationResult.INVALID,
            errors=[ValidationError(
                field="samples",
                message=f"Saturation detected: max={max_sample}",
                hint="Check input signal levels",
            )]
        )
    return ValidationReport(result=ValidationResult.VALID)

validator = CustomValidator(validate_no_saturation)
report = validator.validate(obs)
```

### Automatic Validation Decorator
```python
from heimdall import validate_decorator, RangeValidator

@validate_decorator(RangeValidator(0.0, 1.0, "score"))
def process_score(score):
    # score is guaranteed to be in [0.0, 1.0]
    return score ** 2
```

## Common Usage Scenarios

### Scenario 1: New Detector Function
```python
from heimdall import (
    create_logger, CorrelationContext, create_detection_error,
    RangeValidator, ValidationReport
)

def my_new_detector(obs, params):
    """Detect candidates with error handling and logging."""
    logger = create_logger("my_detector")
    logger.log_operation_start("detect")
    
    try:
        # Validate inputs
        validator = RangeValidator(0.0, 1.0, "threshold")
        report = validator.validate(params.threshold)
        if not report.is_valid():
            raise create_detection_error(
                component="my_detector",
                operation="detect",
                message="Invalid parameters",
                hint=report.errors[0].hint,
            )
        
        # Execute detection
        result = detect_impl(obs, params)
        
        logger.log_operation_complete("detect", duration_s=0.05)
        return result
        
    except Exception as e:
        logger.log_operation_failed("detect", e)
        raise
```

### Scenario 2: Configurable Service
```python
from heimdall import (
    ConfigurationManager, ConfigurationSchema, ConfigField,
    ConfigValueType, get_container
)

class DetectorService:
    def __init__(self, config_path):
        # Load configuration
        schema = ConfigurationSchema("service")
        schema.add_field(ConfigField("port", ConfigValueType.INTEGER))
        schema.add_field(ConfigField("timeout_ms", ConfigValueType.INTEGER))
        
        manager = ConfigurationManager()
        self.config = manager.load_from_file("service", config_path, schema)
        
        # Set up dependency container
        self.container = get_container()
        
    def run(self):
        port = self.config.get_int("port")
        timeout = self.config.get_int("timeout_ms")
        # ... run service ...
```

### Scenario 3: Pluggable Implementation
```python
from heimdall import DependencyContainer, AdapterRegistry

# Register all gate implementations
container = get_container()
registry = AdapterRegistry(CandidateGate)

registry.register("peak_contrast", PeakContrastGate)
registry.register("clock_quality", ClockQualityGate)
registry.register("custom", CustomGate)

container.register_adapter_registry("gates", registry)

# Later, load which gates to use from config
gates_to_use = config.get_list("active_gates")  # ["peak_contrast", "clock_quality"]
gate_registry = container.get_adapter_registry("gates")
gates = [gate_registry.create(name) for name in gates_to_use]
```

## Error Recovery Patterns

### Catch and Log
```python
from heimdall import StorageError

try:
    store.put(evidence)
except StorageError as e:
    logger.error(f"Storage failed: {e.context.message}")
    logger.info(f"Recovery: {e.context.hint}")
    # Implement recovery
    return fallback_result
```

### Raise with Context
```python
from heimdall import create_ingestion_error

try:
    validate_observation(obs)
except ValueError as e:
    raise create_ingestion_error(
        component="ingestion",
        operation="validate",
        message=str(e),
        hint="Verify observation format matches schema",
        context_data={"input": obs},
    )
```

### Graceful Degradation
```python
from heimdall import ExternalServiceError

try:
    context = remote_service.get_context()
except ExternalServiceError as e:
    logger.warning(f"External service unavailable: {e.context.hint}")
    context = load_cached_context()  # Fallback
```

## Testing Patterns

### Mock Logger
```python
from unittest.mock import Mock
from heimdall import StructuredLogger

def test_operation():
    logger = Mock(spec=StructuredLogger)
    # ... run code with mocked logger ...
    logger.log_operation_complete.assert_called_once()
```

### Mock Configuration
```python
from unittest.mock import Mock
from heimdall import Configuration

def test_with_config():
    config = Mock(spec=Configuration)
    config.get_float.return_value = 0.65
    # ... test code using config ...
```

### Mock Container
```python
from unittest.mock import Mock
from heimdall import DependencyContainer

def test_with_mocks():
    container = Mock(spec=DependencyContainer)
    detector = Mock()
    container.get_adapter_registry.return_value.create.return_value = detector
    # ... test code ...
```

## Performance Tips

### Avoid Repeated Logger Creation
```python
# ❌ Bad: Creates new logger every call
def process(data):
    logger = create_logger("processor")  # SLOW
    logger.info("Processing")

# ✅ Good: Create once, reuse
logger = create_logger("processor")
def process(data):
    logger.info("Processing")  # FAST
```

### Use Correlation ID Once Per Request
```python
# ✅ Good: Set once at request start
CorrelationContext.set_id(request.id)
# ... all operations use same ID ...
CorrelationContext.clear()
```

### Batch Configuration Access
```python
# ❌ Slower: Multiple lookups
x = config.get_float("threshold")
y = config.get_int("window")
z = config.get_bool("enabled")

# ✅ Faster: Load once if used frequently
threshold = config.get_float("threshold")
window = config.get_int("window")
enabled = config.get_bool("enabled")
```

## Debugging Tips

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

logger = create_logger("debug_test")
logger.log_operation_start("test")
# Detailed logs emitted
```

### Inspect Error Context
```python
try:
    # ... operation ...
except HeimdallException as e:
    print(f"Domain: {e.context.domain}")
    print(f"Severity: {e.context.severity}")
    print(f"Component: {e.context.component}")
    print(f"Message: {e.context.message}")
    print(f"Hint: {e.context.hint}")
    print(f"Context: {e.context.context_data}")
```

### Validate Validator Chain
```python
from heimdall import ValidationReport

validator = RangeValidator(0, 100).chain(PatternValidator(r"\d+"))
report = validator.validate(test_value)

print(f"Valid: {report.is_valid()}")
print(f"Errors: {len(report.errors)}")
for error in report.errors:
    print(f"  - {error.field}: {error.message}")
```

## FAQ

### Q: Should I use new modules in legacy code?
**A**: New modules are opt-in. Use them when adding new functionality or refactoring. No rush to migrate everything.

### Q: Can I use old imports with new modules?
**A**: Yes! 100% backward compatible. Old code works unchanged.

### Q: How do I test code using dependency injection?
**A**: Mock the container or register test implementations in it.

### Q: Should I log every operation?
**A**: Log significant operations (start, completion, errors). Skip trivial helper functions.

### Q: How much configuration should I externalize?
**A**: Anything that changes per environment (dev/staging/prod) or per deployment.

### Q: What's the performance impact of structured logging?
**A**: ~0.1-0.2ms per event. Negligible for most applications.

### Q: Can I use multiple correlation IDs?
**A**: No - one per request. Nested operations share the same ID.

---

**For More Information**:
- See ARCHITECTURE_ENHANCEMENTS.md for design patterns
- See TESTING_STRATEGY.md for test examples
- See DEPLOYMENT_OPERATIONS.md for production deployment
- See IMPLEMENTATION_QUALITY_STANDARDS.md for code standards
