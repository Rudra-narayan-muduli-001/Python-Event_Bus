from __future__ import annotations
import threading
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator, List, Optional, Type, TypeVar
from app.core.exceptions import (
    CircularDependencyError,
    DependencyNotFoundError,
    DuplicateRegistrationError,
)
from app.core.dependency_injection.interfaces import IContainer, IProvider
from app.core.dependency_injection.providers import (
    ClassProvider,
    FactoryProvider,
    InstanceProvider,
)
from app.core.dependency_injection.scopes import Lifetime, Scope, ScopeManager
from app.logging import Logger

__all__ = ["Container"]

T = TypeVar("T")


class Container(IContainer):
    def __init__(self, logger: Optional[Logger] = None) -> None:
        self._logger = logger
        self._providers: Dict[Any, IProvider] = {}
        self._lock = threading.RLock()
        self._scopes = ScopeManager(logger=logger)
        self._local = threading.local()

    @property
    def scopes(self) -> ScopeManager:
        return self._scopes

    @property
    def _chain(self) -> List[Any]:
        chain = getattr(self._local, "chain", None)
        if chain is None:
            chain = []
            self._local.chain = chain
        return chain

    def register(self, token: Any, provider: IProvider, *, replace: bool = False) -> None:
        with self._lock:
            if token in self._providers and not replace:
                raise DuplicateRegistrationError(token)
            self._providers[token] = provider
        if self._logger:
            self._logger.debug(
                "Provider registered",
                extra={"token": repr(token), "provider": repr(provider)},
            )

    def register_instance(self, token: Any, instance: T, *, replace: bool = False) -> None:
        self.register(token, InstanceProvider(instance), replace=replace)

    def register_factory(
        self,
        token: Any,
        factory: Callable[..., T],
        *,
        lifetime: Lifetime = Lifetime.TRANSIENT,
        disposer: Optional[Callable[[T], None]] = None,
        replace: bool = False,
    ) -> None:
        self.register(
            token,
            FactoryProvider(token, factory, lifetime=lifetime, disposer=disposer),
            replace=replace,
        )

    def register_class(
        self,
        token: Any,
        cls: Optional[Type[T]] = None,
        *,
        lifetime: Lifetime = Lifetime.SINGLETON,
        disposer: Optional[Callable[[T], None]] = None,
        replace: bool = False,
    ) -> None:
        implementation = cls or token
        self.register(
            token,
            ClassProvider(token, implementation, lifetime=lifetime, disposer=disposer),
            replace=replace,
        )

    def resolve(self, token: Type[T] | Any) -> T:
        with self._lock:
            provider = self._providers.get(token)
        if provider is None:
            raise DependencyNotFoundError(token)

        chain = self._chain
        if token in chain:
            cycle = chain[chain.index(token):] + [token]
            raise CircularDependencyError(cycle)

        chain.append(token)
        try:
            return provider.resolve(self)
        finally:
            chain.pop()

    def try_resolve(self, token: Any, default: Any = None) -> Any:
        if not self.has(token):
            return default
        return self.resolve(token)

    def has(self, token: Any) -> bool:
        with self._lock:
            return token in self._providers

    def unregister(self, token: Any) -> None:
        with self._lock:
            self._providers.pop(token, None)

    @property
    def registered_tokens(self) -> List[Any]:
        with self._lock:
            return list(self._providers.keys())

    def create_scope(self, name: str) -> Scope:
        return self._scopes.create_scope(name)

    @contextmanager
    def scope(self, name: str) -> Iterator[Scope]:
        scope = self._scopes.create_scope(name)
        self._scopes.push_scope(scope)
        try:
            with scope:
                yield scope
        finally:
            self._scopes.pop_scope()

    def dispose(self) -> None:
        if self._logger:
            self._logger.info("Disposing DI container")
        self._scopes.dispose_singletons()
        with self._lock:
            self._providers.clear()

    def __contains__(self, token: Any) -> bool:
        return self.has(token)

    def __repr__(self) -> str:  
        return f"<Container providers={len(self._providers)}>"
