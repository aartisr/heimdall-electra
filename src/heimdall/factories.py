"""Factory patterns and dependency injection framework.

This module provides:
- Factory pattern implementations for domain objects
- Dependency injection container for adapters
- Lifecycle management for created objects
- Plugin/extension point management
- Configuration-driven object creation

Design principles:
- Factories encapsulate complex creation logic
- Dependencies are explicit and validated
- Adapters can be swapped without changing core logic
- Lifecycle hooks for setup/teardown
- Type-safe factory creation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar

from .exceptions import create_configuration_error, ConfigurationError

T = TypeVar("T")


class Factory(ABC, Generic[T]):
    """Base factory pattern interface."""

    @abstractmethod
    def create(self, **kwargs: Any) -> T:
        """Create an instance."""
        pass

    @abstractmethod
    def can_create(self, spec: str) -> bool:
        """Check if this factory can create the requested specification."""
        pass


class SingletonFactory(Factory[T]):
    """Factory that creates and caches a single instance."""

    def __init__(self, creator: Callable[..., T]) -> None:
        self.creator = creator
        self._instance: Optional[T] = None

    def create(self, **kwargs: Any) -> T:
        """Create or return cached instance."""
        if self._instance is None:
            self._instance = self.creator(**kwargs)
        return self._instance

    def can_create(self, spec: str) -> bool:
        return True

    def reset(self) -> None:
        """Reset singleton (useful for testing)."""
        self._instance = None


class MultitonFactory(Factory[T]):
    """Factory that creates and caches multiple named instances."""

    def __init__(self, creator: Callable[..., T]) -> None:
        self.creator = creator
        self._instances: Dict[str, T] = {}

    def create(self, key: str, **kwargs: Any) -> T:
        """Create or return cached instance by key."""
        if key not in self._instances:
            self._instances[key] = self.creator(**kwargs)
        return self._instances[key]

    def can_create(self, spec: str) -> bool:
        return spec in self._instances

    def get_cached(self, key: str) -> Optional[T]:
        """Get cached instance without creating."""
        return self._instances.get(key)

    def clear(self) -> None:
        """Clear all cached instances."""
        self._instances.clear()


class AdapterRegistry(Generic[T]):
    """Registry for pluggable adapter implementations."""

    def __init__(self, adapter_type: Type[T]) -> None:
        self.adapter_type = adapter_type
        self._adapters: Dict[str, Type[T]] = {}

    def register(self, name: str, adapter_class: Type[T]) -> AdapterRegistry[T]:
        """Register an adapter implementation."""
        if not issubclass(adapter_class, self.adapter_type):
            raise ConfigurationError(
                create_configuration_error(
                    "AdapterRegistry",
                    "register",
                    f"{adapter_class} is not a subclass of {self.adapter_type}",
                    context_data={
                        "adapter_class": adapter_class.__name__,
                        "base_type": self.adapter_type.__name__,
                    },
                )
            )
        self._adapters[name] = adapter_class
        return self

    def create(self, name: str, **kwargs: Any) -> T:
        """Create an adapter instance."""
        adapter_class = self._adapters.get(name)
        if not adapter_class:
            raise ConfigurationError(
                create_configuration_error(
                    "AdapterRegistry",
                    "create",
                    f"No adapter registered as '{name}'",
                    context_data={"name": name, "available": list(self._adapters.keys())},
                )
            )
        return adapter_class(**kwargs)

    def is_registered(self, name: str) -> bool:
        """Check if adapter is registered."""
        return name in self._adapters

    def list_adapters(self) -> list[str]:
        """List all registered adapter names."""
        return list(self._adapters.keys())


class DependencyContainer:
    """Inversion-of-control container for managing dependencies."""

    def __init__(self) -> None:
        self._factories: Dict[str, Factory] = {}
        self._singletons: Dict[Type, Any] = {}
        self._adapters: Dict[str, AdapterRegistry] = {}

    def register_factory(
        self,
        key: str,
        factory: Factory,
    ) -> DependencyContainer:
        """Register a factory."""
        self._factories[key] = factory
        return self

    def register_singleton(
        self,
        key: str,
        instance: Any,
    ) -> DependencyContainer:
        """Register a pre-created singleton."""
        self._singletons[key] = instance
        return self

    def register_adapter_registry(
        self,
        key: str,
        registry: AdapterRegistry,
    ) -> DependencyContainer:
        """Register an adapter registry."""
        self._adapters[key] = registry
        return self

    def get_factory(self, key: str) -> Optional[Factory]:
        """Get a registered factory."""
        return self._factories.get(key)

    def get_singleton(self, key: str) -> Any:
        """Get a registered singleton."""
        singleton = self._singletons.get(key)
        if singleton is None:
            raise ConfigurationError(
                create_configuration_error(
                    "DependencyContainer",
                    "get_singleton",
                    f"No singleton registered as '{key}'",
                    context_data={"key": key},
                )
            )
        return singleton

    def get_adapter_registry(self, key: str) -> AdapterRegistry:
        """Get an adapter registry."""
        registry = self._adapters.get(key)
        if registry is None:
            raise ConfigurationError(
                create_configuration_error(
                    "DependencyContainer",
                    "get_adapter_registry",
                    f"No adapter registry registered as '{key}'",
                    context_data={"key": key},
                )
            )
        return registry

    def create(self, key: str, **kwargs: Any) -> Any:
        """Create instance using registered factory."""
        factory = self.get_factory(key)
        if factory is None:
            raise ConfigurationError(
                create_configuration_error(
                    "DependencyContainer",
                    "create",
                    f"No factory registered for '{key}'",
                    context_data={"key": key},
                )
            )
        return factory.create(**kwargs)


class LifecycleManager:
    """Manages object lifecycle with setup/teardown hooks."""

    @dataclass
    class Lifecycle:
        """Lifecycle information for an object."""
        object_id: str
        object_type: Type
        created_at: float
        setup_hooks: list[Callable[[], None]]
        teardown_hooks: list[Callable[[], None]]

    def __init__(self) -> None:
        self._objects: Dict[str, Any] = {}
        self._lifecycles: Dict[str, LifecycleManager.Lifecycle] = {}
        self._setup_callbacks: Dict[Type, Callable] = {}
        self._teardown_callbacks: Dict[Type, Callable] = {}

    def register_setup(self, obj_type: Type, callback: Callable) -> LifecycleManager:
        """Register setup callback for type."""
        self._setup_callbacks[obj_type] = callback
        return self

    def register_teardown(
        self,
        obj_type: Type,
        callback: Callable,
    ) -> LifecycleManager:
        """Register teardown callback for type."""
        self._teardown_callbacks[obj_type] = callback
        return self

    def track(
        self,
        object_id: str,
        obj: Any,
    ) -> LifecycleManager:
        """Track object lifecycle."""
        import time
        obj_type = type(obj)
        setup_hooks = []
        teardown_hooks = []

        if obj_type in self._setup_callbacks:
            setup_hooks.append(self._setup_callbacks[obj_type])
        if obj_type in self._teardown_callbacks:
            teardown_hooks.append(self._teardown_callbacks[obj_type])

        self._objects[object_id] = obj
        self._lifecycles[object_id] = LifecycleManager.Lifecycle(
            object_id=object_id,
            object_type=obj_type,
            created_at=time.time(),
            setup_hooks=setup_hooks,
            teardown_hooks=teardown_hooks,
        )

        # Run setup hooks
        for hook in setup_hooks:
            hook()

        return self

    def cleanup(self, object_id: str) -> LifecycleManager:
        """Cleanup tracked object."""
        lifecycle = self._lifecycles.get(object_id)
        if lifecycle:
            for hook in lifecycle.teardown_hooks:
                hook()
            del self._objects[object_id]
            del self._lifecycles[object_id]

        return self

    def cleanup_all(self) -> LifecycleManager:
        """Cleanup all tracked objects."""
        for object_id in list(self._objects.keys()):
            self.cleanup(object_id)
        return self


# Global dependency container
_global_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get global dependency container."""
    global _global_container
    if _global_container is None:
        _global_container = DependencyContainer()
    return _global_container


def set_container(container: DependencyContainer) -> None:
    """Set global dependency container."""
    global _global_container
    _global_container = container


def create_instance(key: str, **kwargs: Any) -> Any:
    """Create instance using global container."""
    return get_container().create(key, **kwargs)
