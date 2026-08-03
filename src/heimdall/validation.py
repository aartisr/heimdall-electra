"""Type-safe validation and verification framework.

This module provides:
- Type-safe validators for domain objects
- Specification pattern implementations
- Custom validator decorators
- Batch validation with comprehensive error reporting
- Extensible verification chain pattern

Design principles:
- Validators are composable and chainable
- Validation errors are collected, not short-circuiting
- Validators can be used declaratively or programmatically
- Verification can be deferred or immediate
- Validation results are auditable
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Generic, List, Optional, Protocol, Sequence, TypeVar

from .exceptions import ValidationError, create_validation_error

T = TypeVar("T")
R = TypeVar("R")


class ValidationResult(Enum):
    """Validation outcome."""
    VALID = "valid"
    INVALID = "invalid"
    PARTIAL = "partial"  # Valid but with warnings


@dataclass
class ValidationError_:
    """Single validation error."""
    field: str
    message: str
    hint: Optional[str] = None
    value: Any = None

    def __str__(self) -> str:
        parts = [f"{self.field}: {self.message}"]
        if self.hint:
            parts.append(f"(Hint: {self.hint})")
        return " ".join(parts)


@dataclass
class ValidationReport:
    """Complete validation report."""
    result: ValidationResult
    errors: List[ValidationError_]
    warnings: List[str]
    context: dict[str, Any]

    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.result == ValidationResult.VALID

    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.errors) > 0

    def add_error(
        self,
        field: str,
        message: str,
        hint: Optional[str] = None,
        value: Any = None,
    ) -> ValidationReport:
        """Add error to report."""
        self.errors.append(ValidationError_(field, message, hint, value))
        self.result = ValidationResult.INVALID
        return self

    def add_warning(self, message: str) -> ValidationReport:
        """Add warning to report."""
        self.warnings.append(message)
        if self.result == ValidationResult.VALID:
            self.result = ValidationResult.PARTIAL
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "result": self.result.value,
            "errors": [
                {
                    "field": e.field,
                    "message": e.message,
                    "hint": e.hint,
                }
                for e in self.errors
            ],
            "warnings": self.warnings,
            "context": self.context,
        }


class Validator(ABC, Generic[T]):
    """Base validator interface."""

    @abstractmethod
    def validate(self, value: T) -> ValidationReport:
        """Validate a value and return report."""
        pass

    def validate_or_raise(self, value: T) -> T:
        """Validate and raise on error."""
        report = self.validate(value)
        if not report.is_valid():
            error_messages = [str(e) for e in report.errors]
            raise create_validation_error(
                "Validator",
                "validate_or_raise",
                "Validation failed",
                context_data={"errors": error_messages},
            )
        return value

    def chain(self, other: Validator[T]) -> ChainedValidator[T]:
        """Chain validators."""
        return ChainedValidator([self, other])


class ChainedValidator(Validator[T]):
    """Validator that chains multiple validators."""

    def __init__(self, validators: Sequence[Validator[T]]) -> None:
        self.validators = validators

    def validate(self, value: T) -> ValidationReport:
        """Validate through all validators."""
        report = ValidationReport(
            result=ValidationResult.VALID,
            errors=[],
            warnings=[],
            context={},
        )
        for validator in self.validators:
            sub_report = validator.validate(value)
            report.errors.extend(sub_report.errors)
            report.warnings.extend(sub_report.warnings)
            if sub_report.result == ValidationResult.INVALID:
                report.result = ValidationResult.INVALID
            elif (
                sub_report.result == ValidationResult.PARTIAL
                and report.result != ValidationResult.INVALID
            ):
                report.result = ValidationResult.PARTIAL
        return report


class RangeValidator(Validator[float]):
    """Validator for numeric ranges."""

    def __init__(
        self,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        field_name: str = "value",
    ) -> None:
        self.min_value = min_value
        self.max_value = max_value
        self.field_name = field_name

    def validate(self, value: float) -> ValidationReport:
        """Validate value is in range."""
        report = ValidationReport(
            result=ValidationResult.VALID,
            errors=[],
            warnings=[],
            context={"min": self.min_value, "max": self.max_value},
        )
        if self.min_value is not None and value < self.min_value:
            report.add_error(
                self.field_name,
                f"Value {value} is less than minimum {self.min_value}",
                value=value,
            )
        if self.max_value is not None and value > self.max_value:
            report.add_error(
                self.field_name,
                f"Value {value} is greater than maximum {self.max_value}",
                value=value,
            )
        return report


class NotEmptyValidator(Validator[Sequence]):
    """Validator for non-empty sequences."""

    def __init__(self, field_name: str = "sequence") -> None:
        self.field_name = field_name

    def validate(self, value: Sequence) -> ValidationReport:
        """Validate sequence is not empty."""
        report = ValidationReport(
            result=ValidationResult.VALID,
            errors=[],
            warnings=[],
            context={},
        )
        if not value or len(value) == 0:
            report.add_error(
                self.field_name,
                "Sequence cannot be empty",
                value=value,
            )
        return report


class PatternValidator(Validator[str]):
    """Validator for string patterns."""

    def __init__(
        self,
        pattern: str,
        field_name: str = "value",
    ) -> None:
        import re
        self.pattern = re.compile(pattern)
        self.field_name = field_name

    def validate(self, value: str) -> ValidationReport:
        """Validate string matches pattern."""
        report = ValidationReport(
            result=ValidationResult.VALID,
            errors=[],
            warnings=[],
            context={"pattern": self.pattern.pattern},
        )
        if not self.pattern.match(value):
            report.add_error(
                self.field_name,
                f"Value '{value}' does not match pattern '{self.pattern.pattern}'",
                value=value,
            )
        return report


class CustomValidator(Validator[T]):
    """Validator using custom callable."""

    def __init__(
        self,
        check: Callable[[T], bool],
        error_message: str,
        field_name: str = "value",
    ) -> None:
        self.check = check
        self.error_message = error_message
        self.field_name = field_name

    def validate(self, value: T) -> ValidationReport:
        """Validate using custom check."""
        report = ValidationReport(
            result=ValidationResult.VALID,
            errors=[],
            warnings=[],
            context={},
        )
        if not self.check(value):
            report.add_error(
                self.field_name,
                self.error_message,
                value=value,
            )
        return report


class VerificationChain(Generic[T]):
    """Chain of responsibility pattern for verification."""

    class VerificationStep(Protocol[T]):
        """Protocol for verification step."""

        def verify(self, value: T) -> VerificationResult:
            """Execute verification step."""
            pass

    @dataclass
    class VerificationResult:
        """Result of a verification step."""
        step_name: str
        passed: bool
        message: str
        details: dict[str, Any]

    def __init__(self) -> None:
        self.steps: List[tuple[str, Callable[[T], bool]]] = []

    def add_step(
        self,
        name: str,
        check: Callable[[T], bool],
    ) -> VerificationChain[T]:
        """Add verification step."""
        self.steps.append((name, check))
        return self

    def verify(self, value: T) -> List[VerificationChain.VerificationResult]:
        """Verify through all steps."""
        results = []
        for step_name, check in self.steps:
            try:
                passed = check(value)
                results.append(
                    VerificationChain.VerificationResult(
                        step_name=step_name,
                        passed=passed,
                        message=f"{step_name}: {'PASS' if passed else 'FAIL'}",
                        details={},
                    )
                )
            except Exception as e:
                results.append(
                    VerificationChain.VerificationResult(
                        step_name=step_name,
                        passed=False,
                        message=f"{step_name}: ERROR - {str(e)}",
                        details={"error": str(e)},
                    )
                )
        return results

    def all_passed(self, results: List[VerificationChain.VerificationResult]) -> bool:
        """Check if all verifications passed."""
        return all(r.passed for r in results)


def validate_decorator(validator: Validator[T]) -> Callable:
    """Decorator for automatic validation."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if args:
                value = args[0]
                validator.validate_or_raise(value)
            return func(*args, **kwargs)
        return wrapper
    return decorator
