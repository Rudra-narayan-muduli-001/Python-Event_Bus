from __future__ import annotations
import asyncio
import enum
import inspect
import threading
import uuid
import weakref
from typing import Any, Awaitable, Callable, Optional, Union
from app.core.event_bus.event_filter import AcceptAllFilter, EventFilter
from app.core.event_bus.event_types import Event
from app.core.exceptions import EventHandlerError
from app.logging import Logger

__all__ = [
    "ErrorPolicy",
    "SubscriptionState",
    "Subscriber",
]

SyncHandler = Callable[[Event], Any]
AsyncHandler = Callable[[Event], Awaitable[Any]]
EventHandler = Union[SyncHandler, AsyncHandler]


class ErrorPolicy(str, enum.Enum):

    ISOLATE = "isolate"      
    PROPAGATE = "propagate"  
    DISABLE = "disable"      


class SubscriptionState(str, enum.Enum):

    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"     
    UNSUBSCRIBED = "unsubscribed"


class Subscriber:
    def __init__(
        self,
        handler: EventHandler,
        *,
        event_filter: Optional[EventFilter] = None,
        priority: int = 0,
        once: bool = False,
        error_policy: ErrorPolicy = ErrorPolicy.ISOLATE,
        weak: bool = False,
        name: Optional[str] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        if not callable(handler):
            raise TypeError("Subscriber handler must be callable")

        self.id = uuid.uuid4().hex
        self.filter = event_filter or AcceptAllFilter()
        self.priority = priority
        self.once = once
        self.error_policy = error_policy
        self.name = name or getattr(handler, "__name__", f"subscriber-{self.id[:8]}")
        self._logger = logger
        self._is_async = inspect.iscoroutinefunction(handler)
        self._state = SubscriptionState.ACTIVE
        self._lock = threading.Lock()
        self._call_count = 0
        self._on_unsubscribe: Optional[Callable[["Subscriber"], None]] = None

        self._weak = weak
        self._handler_ref = self._make_ref(handler, weak)

    @property
    def is_async(self) -> bool:
        return self._is_async

    @property
    def state(self) -> SubscriptionState:
        return self._state

    @property
    def active(self) -> bool:
        return self._state is SubscriptionState.ACTIVE

    @property
    def call_count(self) -> int:
        return self._call_count

    def wants(self, event: Event) -> bool:
        if self._state is not SubscriptionState.ACTIVE:
            return False
        return self.filter.accepts(event)

    def invoke(self, event: Event) -> Any:
        handler = self._resolve_handler()
        if handler is None:
            return None

        try:
            if self._is_async:
                coro = handler(event)
                try:
                    asyncio.get_running_loop()
                    return coro
                except RuntimeError:
                    return asyncio.run(coro) if inspect.iscoroutine(coro) else coro
            result = handler(event)
            self._after_success()
            return result
        except Exception as exc:  # noqa: BLE001
            return self._handle_error(event, exc)

    async def invoke_async(self, event: Event) -> Any:
        handler = self._resolve_handler()
        if handler is None:
            return None

        try:
            if self._is_async:
                result = await handler(event)
            else:
                result = handler(event)
            self._after_success()
            return result
        except Exception as exc:  # noqa: BLE001
            return self._handle_error(event, exc)

    def pause(self) -> None:
        with self._lock:
            if self._state is SubscriptionState.ACTIVE:
                self._state = SubscriptionState.PAUSED

    def resume(self) -> None:
        with self._lock:
            if self._state is SubscriptionState.PAUSED:
                self._state = SubscriptionState.ACTIVE

    def unsubscribe(self) -> None:
        with self._lock:
            if self._state is SubscriptionState.UNSUBSCRIBED:
                return
            self._state = SubscriptionState.UNSUBSCRIBED
        if self._on_unsubscribe is not None:
            self._on_unsubscribe(self)

    def bind_unsubscribe(self, callback: Callable[["Subscriber"], None]) -> None:
        self._on_unsubscribe = callback

    def _after_success(self) -> None:
        with self._lock:
            self._call_count += 1
            should_close = self.once
        if should_close:
            self.unsubscribe()

    def _handle_error(self, event: Event, exc: Exception) -> Any:
        if self._logger:
            self._logger.error(
                "Event handler raised",
                extra={
                    "subscriber": self.name,
                    "event": event.name,
                    "policy": self.error_policy.value,
                    "error": str(exc),
                },
            )
        if self.error_policy is ErrorPolicy.PROPAGATE:
            raise EventHandlerError(
                event_type=event.name,
                handler=self.name,
                cause=exc,
            ) from exc
        if self.error_policy is ErrorPolicy.DISABLE:
            with self._lock:
                self._state = SubscriptionState.DISABLED
        return None

    def _make_ref(
        self, handler: EventHandler, weak: bool
    ) -> Callable[[], Optional[EventHandler]]:
        if not weak:
            return lambda: handler
        try:
            return weakref.WeakMethod(handler)
        except TypeError:
            return weakref.ref(handler)

    def _resolve_handler(self) -> Optional[EventHandler]:
        handler = self._handler_ref()
        if handler is None:
            with self._lock:
                self._state = SubscriptionState.DISABLED
            if self._logger:
                self._logger.debug(
                    "Subscriber handler was garbage-collected; disabling",
                    extra={"subscriber": self.name},
                )
        return handler

    def __repr__(self) -> str:  
        return (
            f"<Subscriber name={self.name!r} state={self._state.value} "
            f"async={self._is_async} once={self.once} calls={self._call_count}>"
        )
