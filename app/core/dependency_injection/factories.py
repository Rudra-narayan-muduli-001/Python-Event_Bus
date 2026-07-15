from __future__ import annotations
from pathlib import Path
from typing import Any, Callable, Optional, Type, TypeVar
from app.core.constants.app import APP_SLUG
from app.core.exceptions import ProviderError
from app.core.dependency_injection.container import Container
from app.core.dependency_injection.scopes import Lifetime
from app.logging import Logger, LoggerFactory, LogLevel

__all__ = [
    "ContainerBuilder",
    "ServiceFactory",
    "build_root_container",
]

T = TypeVar("T")


class ContainerBuilder:
    def __init__(self, logger: Optional[Logger] = None) -> None:
        self._container = Container(logger=logger)
        self._built = False
    def add_instance(self, token: Any, instance: T, *, replace: bool = False) -> "ContainerBuilder":
        self._ensure_open()
        self._container.register_instance(token, instance, replace=replace)
        return self

    def add_factory(
        self,
        token: Any,
        factory: Callable[..., T],
        *,
        lifetime: Lifetime = Lifetime.TRANSIENT,
        disposer: Optional[Callable[[T], None]] = None,
        replace: bool = False,
    ) -> "ContainerBuilder":
        self._ensure_open()
        self._container.register_factory(
            token, factory, lifetime=lifetime, disposer=disposer, replace=replace
        )
        return self

    def add_singleton(
        self,
        token: Any,
        cls: Optional[Type[T]] = None,
        *,
        disposer: Optional[Callable[[T], None]] = None,
        replace: bool = False,
    ) -> "ContainerBuilder":
        self._ensure_open()
        self._container.register_class(
            token, cls, lifetime=Lifetime.SINGLETON, disposer=disposer, replace=replace
        )
        return self

    def add_transient(
        self,
        token: Any,
        cls: Optional[Type[T]] = None,
        *,
        replace: bool = False,
    ) -> "ContainerBuilder":
        self._ensure_open()
        self._container.register_class(
            token, cls, lifetime=Lifetime.TRANSIENT, replace=replace
        )
        return self

    def add_scoped(
        self,
        token: Any,
        cls: Optional[Type[T]] = None,
        *,
        disposer: Optional[Callable[[T], None]] = None,
        replace: bool = False,
    ) -> "ContainerBuilder":
        self._ensure_open()
        self._container.register_class(
            token, cls, lifetime=Lifetime.SCOPED, disposer=disposer, replace=replace
        )
        return self

    def configure(self, configurator: Callable[[Container], None]) -> "ContainerBuilder":
        self._ensure_open()
        configurator(self._container)
        return self
    def build(self) -> Container:
        if self._built:
            raise ProviderError("ContainerBuilder", reason="builder already consumed")
        self._built = True
        return self._container

    def _ensure_open(self) -> None:
        if self._built:
            raise ProviderError(
                "ContainerBuilder", reason="cannot modify a container after build()"
            )


class ServiceFactory:

    def __init__(self, container: Container) -> None:
        self._container = container

    def get(self, token: Type[T]) -> T:
        return self._container.resolve(token)

    def get_optional(self, token: Type[T], default: Optional[T] = None) -> Optional[T]:
        return self._container.try_resolve(token, default)

    def get_or_create(
        self,
        token: Any,
        factory: Callable[[], T],
        *,
        lifetime: Lifetime = Lifetime.SINGLETON,
    ) -> T:
        if not self._container.has(token):
            self._container.register_factory(token, factory, lifetime=lifetime)
        return self._container.resolve(token)

    @property
    def container(self) -> Container:
        return self._container


def build_root_container(
    *,
    log_dir: Optional[Path] = None,
    console_level: LogLevel = LogLevel.INFO,
    logger_factory: Optional[LoggerFactory] = None,
) -> Container:
    factory = logger_factory or LoggerFactory()
    if log_dir is not None:
        log_path = str(Path(log_dir) / "startup" / "bootstrap.log")
        boot_logger = factory.create_composite_logger(
            name=f"{APP_SLUG}.bootstrap",
            file_path=log_path,
            level=console_level,
        )
    else:
        boot_logger = factory.create_console_logger(
            name=f"{APP_SLUG}.bootstrap",
            level=console_level,
        )

    container = Container(logger=boot_logger)
    container.register_instance(LoggerFactory, factory)
    container.register_instance(Logger, boot_logger)

    boot_logger.info("Root DI container initialized")
    return container
