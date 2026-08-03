"""Structured logging and observability framework for Heimdall research.

This module provides:
- Structured logging with correlation IDs for request tracing
- Audit trail for all significant state mutations
- Performance metrics collection
- Integration points for monitoring systems
- Correlation context for distributed tracing

Design principles:
- All logs are structured JSON when used with a JSON formatter
- Every significant operation has a correlation ID
- Audit trail is append-only and immutable
- Metrics are collected without blocking main operations
- All logging is configurable and can be disabled for performance
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional
from uuid import uuid4
from threading import local


class EventKind(str, Enum):
    """Classification of logged events."""
    OPERATION_START = "operation_start"
    OPERATION_COMPLETE = "operation_complete"
    OPERATION_FAILED = "operation_failed"
    VALIDATION = "validation"
    VERIFICATION = "verification"
    GATE_DECISION = "gate_decision"
    CANDIDATE_CREATED = "candidate_created"
    ARTIFACT_INGESTED = "artifact_ingested"
    STATE_MUTATION = "state_mutation"
    CONFIGURATION_LOADED = "configuration_loaded"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class MetricValue:
    """A single measured metric."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    component: str
    correlation_id: str
    dimensions: dict[str, str] = None

    def __post_init__(self) -> None:
        if self.dimensions is None:
            self.dimensions = {}
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "component": self.component,
            "correlation_id": self.correlation_id,
            "dimensions": self.dimensions,
        }


@dataclass
class AuditEvent:
    """Immutable record of a significant event."""
    event_id: str
    kind: EventKind
    timestamp: datetime
    correlation_id: str
    component: str
    operation: str
    actor: str
    status: str  # "success" | "failed" | "partial"
    message: str
    details: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        if self.details is None:
            self.details = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "kind": self.kind.value,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "component": self.component,
            "operation": self.operation,
            "actor": self.actor,
            "status": self.status,
            "message": self.message,
            "details": self.details,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


class CorrelationContext:
    """Thread-local correlation context for request tracing."""

    _context = local()

    @classmethod
    def generate_id(cls) -> str:
        """Generate a new correlation ID."""
        return str(uuid4())

    @classmethod
    def get_id(cls) -> str:
        """Get current correlation ID, generating if needed."""
        if not hasattr(cls._context, "correlation_id"):
            cls._context.correlation_id = cls.generate_id()
        return cls._context.correlation_id

    @classmethod
    def set_id(cls, correlation_id: str) -> None:
        """Set correlation ID explicitly."""
        cls._context.correlation_id = correlation_id

    @classmethod
    def clear(cls) -> None:
        """Clear correlation context."""
        if hasattr(cls._context, "correlation_id"):
            delattr(cls._context, "correlation_id")


class AuditTrail:
    """Append-only audit trail for state mutations."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: AuditEvent) -> None:
        """Append event to audit trail."""
        with self.path.open("a") as f:
            f.write(event.to_json() + "\n")
            f.flush()

    def read(self, limit: Optional[int] = None) -> list[AuditEvent]:
        """Read audit trail events (optionally limited to last N)."""
        if not self.path.exists():
            return []
        events = []
        with self.path.open("r") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        events.append(AuditEvent(
                            event_id=data["event_id"],
                            kind=EventKind(data["kind"]),
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            correlation_id=data["correlation_id"],
                            component=data["component"],
                            operation=data["operation"],
                            actor=data["actor"],
                            status=data["status"],
                            message=data["message"],
                            details=data.get("details", {}),
                        ))
                    except (json.JSONDecodeError, ValueError) as e:
                        logging.warning(f"Failed to parse audit event: {e}")
        return events[-limit:] if limit else events


class MetricsCollector:
    """Collects and aggregates metrics without blocking operations."""

    def __init__(self) -> None:
        self.metrics: list[MetricValue] = []
        self._lock_count = 0

    def collect(self, metric: MetricValue) -> None:
        """Collect a metric."""
        self.metrics.append(metric)

    def record_duration(
        self,
        name: str,
        component: str,
        duration_s: float,
        correlation_id: Optional[str] = None,
        dimensions: Optional[dict[str, str]] = None,
    ) -> None:
        """Record operation duration."""
        metric = MetricValue(
            name=name,
            value=duration_s,
            unit="seconds",
            timestamp=datetime.now(timezone.utc),
            component=component,
            correlation_id=correlation_id or CorrelationContext.get_id(),
            dimensions=dimensions or {},
        )
        self.collect(metric)

    def get_all(self) -> list[MetricValue]:
        """Get all collected metrics."""
        return self.metrics.copy()

    def clear(self) -> None:
        """Clear collected metrics."""
        self.metrics.clear()


class StructuredLogger:
    """Structured logging with correlation context."""

    def __init__(
        self,
        name: str,
        audit_trail: Optional[AuditTrail] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ) -> None:
        self.name = name
        self.logger = logging.getLogger(name)
        self.audit_trail = audit_trail
        self.metrics = metrics_collector or MetricsCollector()

    def log_event(
        self,
        kind: EventKind,
        operation: str,
        message: str,
        status: str = "success",
        actor: str = "system",
        details: Optional[dict[str, Any]] = None,
    ) -> AuditEvent:
        """Log a structured event to audit trail."""
        event = AuditEvent(
            event_id=str(uuid4()),
            kind=kind,
            timestamp=datetime.now(timezone.utc),
            correlation_id=CorrelationContext.get_id(),
            component=self.name,
            operation=operation,
            actor=actor,
            status=status,
            message=message,
            details=details or {},
        )
        if self.audit_trail:
            self.audit_trail.append(event)
        self.logger.info(json.dumps(event.to_dict()))
        return event

    def log_operation_start(
        self,
        operation: str,
        actor: str = "system",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log operation start."""
        self.log_event(
            EventKind.OPERATION_START,
            operation,
            f"Starting {operation}",
            actor=actor,
            details=details,
        )

    def log_operation_complete(
        self,
        operation: str,
        duration_s: float,
        actor: str = "system",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log operation completion."""
        details_with_duration = {**(details or {}), "duration_s": duration_s}
        self.log_event(
            EventKind.OPERATION_COMPLETE,
            operation,
            f"Completed {operation}",
            actor=actor,
            details=details_with_duration,
        )
        self.metrics.record_duration(
            operation,
            self.name,
            duration_s,
            dimensions={"status": "success"},
        )

    def log_operation_failed(
        self,
        operation: str,
        error: Exception,
        actor: str = "system",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log operation failure."""
        details_with_error = {
            **(details or {}),
            "error_type": type(error).__name__,
            "error_message": str(error),
        }
        self.log_event(
            EventKind.OPERATION_FAILED,
            operation,
            f"Failed {operation}: {error}",
            status="failed",
            actor=actor,
            details=details_with_error,
        )
        self.logger.error(f"{operation} failed", exc_info=error)

    def log_validation(
        self,
        operation: str,
        passed: bool,
        message: str,
        actor: str = "system",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log validation result."""
        self.log_event(
            EventKind.VALIDATION,
            operation,
            message,
            status="success" if passed else "failed",
            actor=actor,
            details=details,
        )

    def timed_operation(
        self,
        operation: str,
        actor: str = "system",
    ) -> Callable:
        """Decorator for timing and logging operations."""
        def decorator(func: Callable) -> Callable:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                self.log_operation_start(operation, actor=actor)
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start
                    self.log_operation_complete(
                        operation,
                        duration,
                        actor=actor,
                        details={"function": func.__name__},
                    )
                    return result
                except Exception as e:
                    self.log_operation_failed(
                        operation,
                        e,
                        actor=actor,
                        details={"function": func.__name__},
                    )
                    raise
            return wrapper
        return decorator


# Global metrics collector singleton
_global_metrics = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    return _global_metrics


def create_logger(
    name: str,
    audit_trail_path: Optional[Path] = None,
) -> StructuredLogger:
    """Factory for structured logger instances."""
    audit_trail = (
        AuditTrail(audit_trail_path) if audit_trail_path else None
    )
    return StructuredLogger(name, audit_trail, _global_metrics)
