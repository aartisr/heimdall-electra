"""Exception hierarchy for Heimdall research domain.

This module defines a comprehensive exception hierarchy that enables
rich error context, recovery hints, and structured error handling
across the entire system.

Design principles:
- Each exception class maps to a specific error condition
- Context fields provide actionable diagnostic information
- Exceptions preserve lineage for root-cause analysis
- Recovery suggestions guide remediation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ErrorSeverity(str, Enum):
    """Error severity levels for priority and routing."""
    RECOVERABLE = "recoverable"
    DEGRADED = "degraded"
    FATAL = "fatal"
    VALIDATION = "validation"


class ErrorDomain(str, Enum):
    """Error domain classification for categorization."""
    DOMAIN_CONTRACT = "domain_contract"
    DATA_INGESTION = "data_ingestion"
    DETECTOR = "detector"
    TIMING = "timing"
    STORAGE = "storage"
    CONFIGURATION = "configuration"
    EXTERNAL_SERVICE = "external_service"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Rich error context for diagnostics and recovery."""
    domain: ErrorDomain
    severity: ErrorSeverity
    component: str
    operation: str
    message: str
    hint: Optional[str] = None
    context_data: dict[str, Any] = field(default_factory=dict)
    root_cause: Optional[Exception] = None

    def __str__(self) -> str:
        parts = [
            f"[{self.domain.value}/{self.severity.value}]",
            f"{self.component}.{self.operation}:",
            self.message,
        ]
        if self.hint:
            parts.append(f"(Hint: {self.hint})")
        return " ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Serialize context to dictionary for logging."""
        return {
            "domain": self.domain.value,
            "severity": self.severity.value,
            "component": self.component,
            "operation": self.operation,
            "message": self.message,
            "hint": self.hint,
            "context": self.context_data,
            "root_cause": (
                str(self.root_cause) if self.root_cause else None
            ),
        }


class HeimdallException(Exception):
    """Base exception for all Heimdall domain errors."""

    def __init__(
        self,
        context: ErrorContext,
        *args: Any,
    ) -> None:
        self.context = context
        super().__init__(str(context), *args)


class ContractViolationError(HeimdallException):
    """Raised when a domain contract is violated.

    Examples:
    - ObservationL0 payload_digest doesn't match samples
    - CandidateL2 detected state contradicts score/threshold
    - Provenance missing required fields for evidence class
    """

    pass


class IngestionBoundaryError(HeimdallException):
    """Raised when data ingestion fails validation.

    Examples:
    - Source not registered or approved
    - Integrity verification fails (bad digest)
    - Evidence class not allowed by source
    - Bytes corrupt or incomplete
    """

    pass


class StorageError(HeimdallException):
    """Raised when persistent storage operations fail.

    Examples:
    - Content-addressed store corruption detected
    - Exclusive lock acquisition timeout
    - File system I/O failure
    - Manifest ledger append failure
    """

    pass


class DetectionError(HeimdallException):
    """Raised when detector pipeline fails.

    Examples:
    - Invalid observation format
    - Gate assessment error
    - Threshold policy not found
    - Score calculation NaN/inf
    """

    pass


class TimingError(HeimdallException):
    """Raised when timing/association constraints are violated.

    Examples:
    - Clock uncertainty invalid
    - Time scale mismatch
    - TDOA solver geometry inconsistency
    - Sequence number gap detected
    """

    pass


class ConfigurationError(HeimdallException):
    """Raised when configuration is invalid.

    Examples:
    - Missing required configuration
    - Configuration values out of valid range
    - Incompatible configuration combination
    - Configuration schema validation failed
    """

    pass


class ExternalServiceError(HeimdallException):
    """Raised when external service calls fail.

    Examples:
    - Remote context fetch timeout
    - Model registry lookup failure
    - Source registry unavailable
    - Instrument signature verification fails
    """

    pass


class ValidationError(HeimdallException):
    """Raised when data validation fails.

    Examples:
    - Schema validation error
    - Value out of valid range
    - Type mismatch
    - Required field missing
    """

    pass


def create_contract_error(
    component: str,
    operation: str,
    message: str,
    context_data: Optional[dict[str, Any]] = None,
    hint: Optional[str] = None,
) -> ContractViolationError:
    """Factory for contract violation errors."""
    ctx = ErrorContext(
        domain=ErrorDomain.DOMAIN_CONTRACT,
        severity=ErrorSeverity.FATAL,
        component=component,
        operation=operation,
        message=message,
        hint=hint,
        context_data=context_data or {},
    )
    return ContractViolationError(ctx)


def create_ingestion_error(
    component: str,
    operation: str,
    message: str,
    context_data: Optional[dict[str, Any]] = None,
    hint: Optional[str] = None,
    severity: ErrorSeverity = ErrorSeverity.VALIDATION,
) -> IngestionBoundaryError:
    """Factory for ingestion boundary errors."""
    ctx = ErrorContext(
        domain=ErrorDomain.DATA_INGESTION,
        severity=severity,
        component=component,
        operation=operation,
        message=message,
        hint=hint,
        context_data=context_data or {},
    )
    return IngestionBoundaryError(ctx)


def create_storage_error(
    component: str,
    operation: str,
    message: str,
    context_data: Optional[dict[str, Any]] = None,
    hint: Optional[str] = None,
    root_cause: Optional[Exception] = None,
) -> StorageError:
    """Factory for storage errors."""
    ctx = ErrorContext(
        domain=ErrorDomain.STORAGE,
        severity=ErrorSeverity.FATAL,
        component=component,
        operation=operation,
        message=message,
        hint=hint,
        context_data=context_data or {},
        root_cause=root_cause,
    )
    return StorageError(ctx)


def create_detection_error(
    component: str,
    operation: str,
    message: str,
    context_data: Optional[dict[str, Any]] = None,
    hint: Optional[str] = None,
    severity: ErrorSeverity = ErrorSeverity.RECOVERABLE,
) -> DetectionError:
    """Factory for detector pipeline errors."""
    ctx = ErrorContext(
        domain=ErrorDomain.DETECTOR,
        severity=severity,
        component=component,
        operation=operation,
        message=message,
        hint=hint,
        context_data=context_data or {},
    )
    return DetectionError(ctx)


def create_timing_error(
    component: str,
    operation: str,
    message: str,
    context_data: Optional[dict[str, Any]] = None,
    hint: Optional[str] = None,
) -> TimingError:
    """Factory for timing errors."""
    ctx = ErrorContext(
        domain=ErrorDomain.TIMING,
        severity=ErrorSeverity.FATAL,
        component=component,
        operation=operation,
        message=message,
        hint=hint,
        context_data=context_data or {},
    )
    return TimingError(ctx)


def create_configuration_error(
    component: str,
    operation: str,
    message: str,
    context_data: Optional[dict[str, Any]] = None,
    hint: Optional[str] = None,
) -> ConfigurationError:
    """Factory for configuration errors."""
    ctx = ErrorContext(
        domain=ErrorDomain.CONFIGURATION,
        severity=ErrorSeverity.FATAL,
        component=component,
        operation=operation,
        message=message,
        hint=hint,
        context_data=context_data or {},
    )
    return ConfigurationError(ctx)


def create_validation_error(
    component: str,
    operation: str,
    message: str,
    context_data: Optional[dict[str, Any]] = None,
    hint: Optional[str] = None,
) -> ValidationError:
    """Factory for validation errors."""
    ctx = ErrorContext(
        domain=ErrorDomain.UNKNOWN,
        severity=ErrorSeverity.VALIDATION,
        component=component,
        operation=operation,
        message=message,
        hint=hint,
        context_data=context_data or {},
    )
    return ValidationError(ctx)
