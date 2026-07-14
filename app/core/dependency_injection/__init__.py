from __future__ import annotations
from app.dependency_injection.interfaces import (
    IContainer,
    ILifecycle,
    IProvider,
)

from app.dependency_injection.scopes import (
    Lifetime,
    Scope,
    ScopeManager,
)
from app.dependency_injection.providers import (
    ClassProvider,
    FactoryProvider,
    InstanceProvider,
)
from app.dependency_injection.container import Container
from app.dependency_injection.factories import (
    ContainerBuilder,
    ServiceFactory,
    build_root_container,
)

__all__ = [
    "IContainer",
    "IProvider",
    "ILifecycle",
    "Lifetime",
    "Scope",
    "ScopeManager",
    "InstanceProvider",
    "FactoryProvider",
    "ClassProvider",
    "Container",
    "ContainerBuilder",
    "ServiceFactory",
    "build_root_container",
]

__version__ = "1.0.0"
