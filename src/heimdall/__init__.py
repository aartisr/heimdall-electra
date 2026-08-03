"""Project Heimdall research reference implementation.

This package provides:
- Domain contracts for evidence (ObservationL0, CalibratedObservationL1, CandidateL2)
- Synthetic scenario generation and forward models
- Detector pipeline with pluggable gates
- Ingestion boundary with content-addressing
- Governance framework for pre-registered experiments
- Observability infrastructure (logging, audit trails, metrics)
- Exception hierarchy and error handling
- Configuration management and validation
- Factory patterns and dependency injection
"""

from .calibration import calibrate
from .audit_bundle import AuditBundle, build_audit_bundle, verify_audit_bundle, write_audit_bundle
from .domain import CalibratedObservationL1, CandidateL2, DatasetSplit, EvidenceClass, ObservationL0, Provenance
from .evaluation import DetectionReport, EvaluationRow, evaluate, evaluate_by_stratum
from .forward_models import ForwardModel, IllustrativeBurstSineModel, NullSignalModel
from .governance import (
    ExperimentPlan,
    ExperimentResult,
    JsonlExperimentLedger,
    PlanStatus,
    ThresholdPolicy,
    execute_pre_registered_experiment,
    sealed_now,
)
from .pipeline import BaselineMatchedFilter, CandidateGate, ClockQualityGate, GateDecision, PeakContrastGate, detect
from .official_sources import NOAA_SWPC_PLANETARY_K_INDEX, NOAA_SWPC_PLANETARY_K_INDEX_ENDPOINT
from .remote_context import HttpsContextConnector, OfficialEndpoint, ingest_external_context
from .registry import RegisteredScenario, reference_registry
from .simulation import SyntheticScenario, generate_observation

# New core infrastructure modules
from .exceptions import (
    ContractViolationError,
    ConfigurationError,
    DetectionError,
    ErrorContext,
    ErrorDomain,
    ErrorSeverity,
    ExternalServiceError,
    HeimdallException,
    IngestionBoundaryError,
    StorageError,
    TimingError,
    ValidationError,
    create_contract_error,
    create_detection_error,
    create_ingestion_error,
    create_storage_error,
    create_timing_error,
    create_validation_error,
    create_configuration_error,
)
from .observability import (
    AuditEvent,
    AuditTrail,
    CorrelationContext,
    EventKind,
    MetricsCollector,
    MetricValue,
    StructuredLogger,
    create_logger,
    get_metrics_collector,
)
from .configuration import (
    Configuration,
    ConfigurationError as ConfigError,
    ConfigurationField,
    ConfigurationManager,
    ConfigurationSchema,
    ConfigConstraint,
    ConfigValueType,
)
from .factories import (
    AdapterRegistry,
    DependencyContainer,
    Factory,
    LifecycleManager,
    MultitonFactory,
    SingletonFactory,
    create_instance,
    get_container,
    set_container,
)
from .validation import (
    ChainedValidator,
    CustomValidator,
    NotEmptyValidator,
    PatternValidator,
    RangeValidator,
    ValidationError as ValidErr,
    ValidationReport,
    ValidationResult,
    Validator,
    VerificationChain,
    validate_decorator,
)

__all__ = [
    # Domain contracts
    "BaselineMatchedFilter",
    "AuditBundle",
    "CandidateGate",
    "CalibratedObservationL1",
    "CandidateL2",
    "ClockQualityGate",
    "DatasetSplit",
    "DetectionReport",
    "EvidenceClass",
    "ExperimentPlan",
    "ExperimentResult",
    "EvaluationRow",
    "ForwardModel",
    "GateDecision",
    "HttpsContextConnector",
    "IllustrativeBurstSineModel",
    "JsonlExperimentLedger",
    "ObservationL0",
    "OfficialEndpoint",
    "NOAA_SWPC_PLANETARY_K_INDEX",
    "NOAA_SWPC_PLANETARY_K_INDEX_ENDPOINT",
    "NullSignalModel",
    "Provenance",
    "PeakContrastGate",
    "PlanStatus",
    "RegisteredScenario",
    "SyntheticScenario",
    "ThresholdPolicy",
    "calibrate",
    "build_audit_bundle",
    "detect",
    "evaluate",
    "evaluate_by_stratum",
    "execute_pre_registered_experiment",
    "generate_observation",
    "ingest_external_context",
    "reference_registry",
    "sealed_now",
    "verify_audit_bundle",
    "write_audit_bundle",
    # Exception hierarchy
    "ContractViolationError",
    "ConfigurationError",
    "DetectionError",
    "ErrorContext",
    "ErrorDomain",
    "ErrorSeverity",
    "ExternalServiceError",
    "HeimdallException",
    "IngestionBoundaryError",
    "StorageError",
    "TimingError",
    "ValidationError",
    "create_contract_error",
    "create_detection_error",
    "create_ingestion_error",
    "create_storage_error",
    "create_timing_error",
    "create_validation_error",
    "create_configuration_error",
    # Observability
    "AuditEvent",
    "AuditTrail",
    "CorrelationContext",
    "EventKind",
    "MetricsCollector",
    "MetricValue",
    "StructuredLogger",
    "create_logger",
    "get_metrics_collector",
    # Configuration
    "Configuration",
    "ConfigurationField",
    "ConfigurationManager",
    "ConfigurationSchema",
    "ConfigConstraint",
    "ConfigValueType",
    # Factories & DI
    "AdapterRegistry",
    "DependencyContainer",
    "Factory",
    "LifecycleManager",
    "MultitonFactory",
    "SingletonFactory",
    "create_instance",
    "get_container",
    "set_container",
    # Validation
    "ChainedValidator",
    "CustomValidator",
    "NotEmptyValidator",
    "PatternValidator",
    "RangeValidator",
    "ValidationReport",
    "ValidationResult",
    "Validator",
    "VerificationChain",
    "validate_decorator",
]
