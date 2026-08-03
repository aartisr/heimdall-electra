"""Configuration management and validation framework.

This module provides:
- Configuration schema definition and validation
- Environment-specific configuration
- Type-safe configuration access
- Configuration hot-reloading capability
- Extensible validation rules

Design principles:
- All configuration must be explicitly declared
- Validation happens at load time, not access time
- Defaults are explicit and documented
- Type safety is enforced
- Configuration errors are caught early with actionable messages
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Generic, Optional, Type, TypeVar, Union
import json
import os

from .exceptions import (
    ConfigurationError,
    create_configuration_error,
)

T = TypeVar("T")


class ConfigValueType(str, Enum):
    """Supported configuration value types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    PATH = "path"
    CHOICE = "choice"
    LIST = "list"
    DICT = "dict"


@dataclass
class ConfigConstraint:
    """Constraint on a configuration value."""
    constraint_type: str
    value: Any
    message: Optional[str] = None

    def validate(self, value: Any) -> bool:
        """Validate value against constraint."""
        if self.constraint_type == "min":
            return value >= self.value
        elif self.constraint_type == "max":
            return value <= self.value
        elif self.constraint_type == "min_length":
            return len(value) >= self.value
        elif self.constraint_type == "max_length":
            return len(value) <= self.value
        elif self.constraint_type == "in":
            return value in self.value
        elif self.constraint_type == "not_empty":
            return len(value) > 0
        elif self.constraint_type == "pattern":
            import re
            return re.match(self.value, str(value)) is not None
        return True

    def error_message(self) -> str:
        """Get constraint violation message."""
        if self.message:
            return self.message
        return f"Configuration constraint '{self.constraint_type}' violated with value {self.value}"


@dataclass
class ConfigField:
    """Declaration of a configuration field."""
    name: str
    value_type: ConfigValueType
    default: Any = None
    required: bool = False
    description: str = ""
    constraints: list[ConfigConstraint] = field(default_factory=list)
    choices: list[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.required and self.default is not None:
            raise ValueError(f"Required field {self.name} cannot have a default")
        if self.value_type == ConfigValueType.CHOICE and not self.choices:
            raise ValueError(f"Choice field {self.name} must declare choices")

    def validate(self, value: Any) -> None:
        """Validate value against field constraints."""
        if value is None and not self.required:
            return

        if value is None and self.required:
            raise ValueError(f"Required field {self.name} is missing")

        # Type validation
        if self.value_type == ConfigValueType.STRING and not isinstance(value, str):
            raise ValueError(f"Field {self.name} must be string, got {type(value)}")
        elif self.value_type == ConfigValueType.INTEGER and not isinstance(value, int):
            raise ValueError(f"Field {self.name} must be integer, got {type(value)}")
        elif self.value_type == ConfigValueType.FLOAT and not isinstance(value, (int, float)):
            raise ValueError(f"Field {self.name} must be float, got {type(value)}")
        elif self.value_type == ConfigValueType.BOOLEAN and not isinstance(value, bool):
            raise ValueError(f"Field {self.name} must be boolean, got {type(value)}")
        elif self.value_type == ConfigValueType.PATH and not isinstance(value, (str, Path)):
            raise ValueError(f"Field {self.name} must be path, got {type(value)}")
        elif self.value_type == ConfigValueType.CHOICE and value not in self.choices:
            raise ValueError(f"Field {self.name} value {value} not in {self.choices}")
        elif self.value_type == ConfigValueType.LIST and not isinstance(value, list):
            raise ValueError(f"Field {self.name} must be list, got {type(value)}")
        elif self.value_type == ConfigValueType.DICT and not isinstance(value, dict):
            raise ValueError(f"Field {self.name} must be dict, got {type(value)}")

        # Constraint validation
        for constraint in self.constraints:
            if not constraint.validate(value):
                raise ValueError(constraint.error_message())


class ConfigurationSchema:
    """Schema for configuration validation."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.fields: dict[str, ConfigField] = {}

    def add_field(self, field: ConfigField) -> ConfigurationSchema:
        """Add field to schema."""
        self.fields[field.name] = field
        return self

    def validate(self, config: dict[str, Any]) -> None:
        """Validate configuration against schema."""
        errors = []

        for field_name, field in self.fields.items():
            try:
                value = config.get(field_name, field.default)
                field.validate(value)
            except ValueError as e:
                errors.append(str(e))

        if errors:
            raise ConfigurationError(
                create_configuration_error(
                    "ConfigurationSchema",
                    "validate",
                    f"Configuration validation failed for {self.name}",
                    context_data={"errors": errors, "config": self.name},
                )
            )

    def get_field(self, name: str) -> Optional[ConfigField]:
        """Get field by name."""
        return self.fields.get(name)


class Configuration:
    """Type-safe configuration container."""

    def __init__(
        self,
        name: str,
        schema: ConfigurationSchema,
        data: Optional[dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.schema = schema
        self._data = data or {}
        self._validators: dict[str, Callable] = {}

        # Validate on construction
        self.schema.validate(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        value = self._data.get(key)
        if value is None:
            field = self.schema.get_field(key)
            value = field.default if field else default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value (with validation)."""
        field = self.schema.get_field(key)
        if not field:
            raise ConfigurationError(
                create_configuration_error(
                    "Configuration",
                    "set",
                    f"Unknown configuration key: {key}",
                    context_data={"key": key},
                )
            )
        field.validate(value)
        if key in self._validators:
            self._validators[key](value)
        self._data[key] = value

    def get_str(self, key: str) -> str:
        """Get string configuration."""
        value = self.get(key)
        if not isinstance(value, str):
            raise ConfigurationError(
                create_configuration_error(
                    "Configuration",
                    "get_str",
                    f"Configuration {key} is not a string",
                    context_data={"key": key, "type": type(value).__name__},
                )
            )
        return value

    def get_int(self, key: str) -> int:
        """Get integer configuration."""
        value = self.get(key)
        if not isinstance(value, int):
            raise ConfigurationError(
                create_configuration_error(
                    "Configuration",
                    "get_int",
                    f"Configuration {key} is not an integer",
                    context_data={"key": key, "type": type(value).__name__},
                )
            )
        return value

    def get_float(self, key: str) -> float:
        """Get float configuration."""
        value = self.get(key)
        if not isinstance(value, (int, float)):
            raise ConfigurationError(
                create_configuration_error(
                    "Configuration",
                    "get_float",
                    f"Configuration {key} is not a float",
                    context_data={"key": key, "type": type(value).__name__},
                )
            )
        return float(value)

    def get_bool(self, key: str) -> bool:
        """Get boolean configuration."""
        value = self.get(key)
        if not isinstance(value, bool):
            raise ConfigurationError(
                create_configuration_error(
                    "Configuration",
                    "get_bool",
                    f"Configuration {key} is not a boolean",
                    context_data={"key": key, "type": type(value).__name__},
                )
            )
        return value

    def get_path(self, key: str) -> Path:
        """Get path configuration."""
        value = self.get(key)
        return Path(value) if isinstance(value, str) else value

    def to_dict(self) -> dict[str, Any]:
        """Export configuration to dictionary."""
        return self._data.copy()


class ConfigurationManager:
    """Manages configuration lifecycle."""

    def __init__(self) -> None:
        self._configurations: dict[str, Configuration] = {}
        self._schemas: dict[str, ConfigurationSchema] = {}

    def register_schema(self, schema: ConfigurationSchema) -> ConfigurationManager:
        """Register a schema."""
        self._schemas[schema.name] = schema
        return self

    def load_from_dict(
        self,
        name: str,
        data: dict[str, Any],
        schema: Optional[ConfigurationSchema] = None,
    ) -> Configuration:
        """Load configuration from dictionary."""
        if schema is None:
            schema = self._schemas.get(name)
            if not schema:
                raise ConfigurationError(
                    create_configuration_error(
                        "ConfigurationManager",
                        "load_from_dict",
                        f"No schema registered for {name}",
                        context_data={"name": name},
                    )
                )
        config = Configuration(name, schema, data)
        self._configurations[name] = config
        return config

    def load_from_file(
        self,
        name: str,
        path: Path,
        schema: Optional[ConfigurationSchema] = None,
    ) -> Configuration:
        """Load configuration from JSON file."""
        if not path.exists():
            raise ConfigurationError(
                create_configuration_error(
                    "ConfigurationManager",
                    "load_from_file",
                    f"Configuration file not found: {path}",
                    context_data={"path": str(path)},
                )
            )
        try:
            with path.open("r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                create_configuration_error(
                    "ConfigurationManager",
                    "load_from_file",
                    f"Failed to parse JSON: {e}",
                    context_data={"path": str(path)},
                )
            )
        return self.load_from_dict(name, data, schema)

    def load_from_env(
        self,
        name: str,
        prefix: str,
        schema: Optional[ConfigurationSchema] = None,
    ) -> Configuration:
        """Load configuration from environment variables."""
        if schema is None:
            schema = self._schemas.get(name)
            if not schema:
                raise ConfigurationError(
                    create_configuration_error(
                        "ConfigurationManager",
                        "load_from_env",
                        f"No schema registered for {name}",
                        context_data={"name": name},
                    )
                )

        data = {}
        for key, env_var in [(f.name, f"{prefix}_{f.name.upper()}") for f in schema.fields.values()]:
            value = os.getenv(env_var)
            if value is not None:
                data[key] = value

        return self.load_from_dict(name, data, schema)

    def get(self, name: str) -> Optional[Configuration]:
        """Get loaded configuration."""
        return self._configurations.get(name)
