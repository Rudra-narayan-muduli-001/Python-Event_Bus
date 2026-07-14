from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
T = TypeVar("T")

class IProvider(ABC, Generic[T]):
    @abstractmethod
    def resolve(self, container: "IContainer") -> T:
        ...

    @property
    @abstractmethod
    def return_type(self) -> type[T]:
        ...


class IContainer(ABC):
    @abstractmethod
    def register(self, token: Any, provider: IProvider) -> None:
        ...

    @abstractmethod
    def resolve(self, token: type[T]) -> T:
        ...

    @abstractmethod
    def has(self, token: Any) -> bool:
        ...


class ILifecycle(ABC):
    @abstractmethod
    async def on_startup(self) -> None:
        ...

    @abstractmethod
    async def on_shutdown(self) -> None:
        ...
