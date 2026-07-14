"""
Dependency Injection Interfaces
===============================
Defines the core contracts for the AIOS DI system. These interfaces
ensure that providers, containers, and lifecycle managers remain
decoupled and follow the Dependency Inversion Principle.

Dependency rule
---------------
This module imports only from the standard library. It never imports
a concrete container or provider — that would invert the dependency
direction (``concrete → contract``, never the other way around).
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class IProvider(ABC, Generic[T]):
    """
    Contract for a dependency provider.
    A provider is responsible for the logic of creating or
    retrieving a specific instance (Singleton, Transient, etc.).
    """

    @abstractmethod
    def resolve(self, container: "IContainer") -> T:
        """Resolve and return the instance."""
        ...

    @property
    @abstractmethod
    def return_type(self) -> type[T]:
        """The type of the instance this provider returns."""
        ...


class IContainer(ABC):
    """
    Contract for the Dependency Injection Container.
    Acts as the central registry and resolution engine for the system.
    """

    @abstractmethod
    def register(self, token: Any, provider: IProvider) -> None:
        """Register a provider for a specific token."""
        ...

    @abstractmethod
    def resolve(self, token: type[T]) -> T:
        """
        Resolve a dependency by its token (Type or string).
        Raises:
            DependencyNotFoundError: If token is not registered.
            DependencyResolutionError: If construction fails.
            CircularDependencyError: If a cycle is detected.
        """
        ...

    @abstractmethod
    def has(self, token: Any) -> bool:
        """Check if a token is registered."""
        ...


class ILifecycle(ABC):
    """
    Optional contract for services that require explicit
    startup or shutdown hooks managed by the container.
    """

    @abstractmethod
    async def on_startup(self) -> None:
        """Logic to execute when the service is initialized."""
        ...

    @abstractmethod
    async def on_shutdown(self) -> None:
        """Logic to execute before the service is destroyed."""
        ...
