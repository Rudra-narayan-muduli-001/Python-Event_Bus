from __future__ import annotations
import inspect
from typing import Any, Callable, Dict, Optional, Type, TypeVar, get_type_hints
from app.core.exceptions import ProviderError, DependencyResolutionError
from app.core.dependency_injection.interfaces import IContainer, IProvider
from app.core.dependency_injection.scopes import Lifetime

__all__ = [
    "InstanceProvider",
    "FactoryProvider",
    "ClassProvider",
]

T = TypeVar("T")


class _LifetimeMixin:
    _lifetime: Lifetime
    _token: Any
    _disposer: Optional[Callable[[Any], None]]

    def _create(self, container: IContainer) -> Any:  
        raise NotImplementedError

    def _resolve_with_lifetime(self, container: IContainer) -> Any:
        scopes = container.scopes  

        if self._lifetime is Lifetime.TRANSIENT:
            return self._create(container)

        if self._lifetime is Lifetime.SINGLETON:
            if scopes.has_singleton(self._token):
                return scopes.get_singleton(self._token)
            instance = self._create(container)
            scopes.set_singleton(self._token, instance, self._disposer)
            return instance
        scope = scopes.require_current_scope(self._token)
        if scope.has(self._token):
            return scope.get(self._token)
        instance = self._create(container)
        scope.set(self._token, instance, self._disposer)
        return instance


class InstanceProvider(IProvider[T]):
    def __init__(self, instance: T) -> None:
        if instance is None:
            raise ProviderError(type(None), reason="instance must not be None")
        self._instance = instance

    def resolve(self, container: IContainer) -> T:
        return self._instance

    @property
    def return_type(self) -> Type[T]:
        return type(self._instance)

    def __repr__(self) -> str:  
        return f"<InstanceProvider type={type(self._instance).__name__}>"


class FactoryProvider(_LifetimeMixin, IProvider[T]):
    def __init__(
        self,
        token: Any,
        factory: Callable[..., T],
        *,
        lifetime: Lifetime = Lifetime.TRANSIENT,
        return_type: Optional[Type[T]] = None,
        disposer: Optional[Callable[[T], None]] = None,
    ) -> None:
        if not callable(factory):
            raise ProviderError(token, reason="factory must be callable")
        self._token = token
        self._factory = factory
        self._lifetime = lifetime
        self._disposer = disposer
        self._return_type = return_type or self._infer_return_type(factory)
        self._wants_container = self._factory_wants_container(factory)

    def resolve(self, container: IContainer) -> T:
        return self._resolve_with_lifetime(container)

    def _create(self, container: IContainer) -> T:
        try:
                instance = self._factory(container) if self._wants_container else self._factory()
        except Exception as exc: 
            raise DependencyResolutionError(self._token, cause=exc) from exc
        if instance is None:
            raise ProviderError(self._token, reason="factory returned None")
        return instance

    @property
    def return_type(self) -> Type[T]:
        return self._return_type

    @staticmethod
    def _factory_wants_container(factory: Callable[..., Any]) -> bool:
        try:
            sig = inspect.signature(factory)
        except (ValueError, TypeError):
            return False
        params = [
            p
            for p in sig.parameters.values()
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]
        return len(params) >= 1

    @staticmethod
    def _infer_return_type(factory: Callable[..., Any]) -> Type[Any]:
        try:
            hints = get_type_hints(factory)
            return hints.get("return", object)
        except (TypeError, NameError):
            return object

    def __repr__(self) -> str:  
        return (
            f"<FactoryProvider token={self._token!r} "
            f"lifetime={self._lifetime.value}>"
        )


class ClassProvider(_LifetimeMixin, IProvider[T]):
    def __init__(
        self,
        token: Any,
        cls: Type[T],
        *,
        lifetime: Lifetime = Lifetime.SINGLETON,
        disposer: Optional[Callable[[T], None]] = None,
    ) -> None:
        if not inspect.isclass(cls):
            raise ProviderError(token, reason="expected a class")
        self._token = token
        self._cls = cls
        self._lifetime = lifetime
        self._disposer = disposer

    def resolve(self, container: IContainer) -> T:
        return self._resolve_with_lifetime(container)

    def _create(self, container: IContainer) -> T:
        kwargs = self._build_kwargs(container)
        try:
            return self._cls(**kwargs)
        except Exception as exc:  
            raise DependencyResolutionError(self._token, cause=exc) from exc

    def _build_kwargs(self, container: IContainer) -> Dict[str, Any]:
        try:
            sig = inspect.signature(self._cls.__init__)
            hints = get_type_hints(self._cls.__init__)
        except (ValueError, TypeError) as exc:
            raise ProviderError(
                self._token, reason=f"cannot introspect constructor: {exc}"
            ) from exc

        kwargs: Dict[str, Any] = {}
        for name, param in sig.parameters.items():
            if name in ("self", "args", "kwargs"):
                continue
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue

            annotation = hints.get(name, param.annotation)
            has_default = param.default is not inspect.Parameter.empty

            if annotation is inspect.Parameter.empty:
                if has_default:
                    continue
                raise ProviderError(
                    self._token,
                    reason=f"parameter '{name}' has no annotation and no default",
                )

            if container.has(annotation):
                kwargs[name] = container.resolve(annotation)
            elif not has_default:
                raise ProviderError(
                    self._token,
                    reason=f"unresolvable dependency '{name}: {annotation}'",
                )
        return kwargs

    @property
    def return_type(self) -> Type[T]:
        return self._cls

    def __repr__(self) -> str:  
        return (
            f"<ClassProvider token={self._token!r} "
            f"cls={self._cls.__name__} lifetime={self._lifetime.value}>"
        )
