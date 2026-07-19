from __future__ import annotations
import threading
import time
from abc import ABC, abstractmethod
from collections import deque
from typing import Callable, Deque, Dict, Optional
from app.core.constants.events import default_priority
from app.core.event_bus.event_context import use_context
from app.core.event_bus.event_priority import resolve_priority
from app.core.event_bus.event_types import Event, EventStatus
from app.logging import Logger

__all__ = [
    "Middleware",
    "MiddlewareChain",
    "LoggingMiddleware",
    "PriorityStampMiddleware",
    "ContextPropagationMiddleware",
    "DeduplicationMiddleware",
    "RateLimitMiddleware",
    "MetricsMiddleware",
]

NextCall = Callable[[Event], Optional[Event]]


class Middleware(ABC):

    @abstractmethod
    def process(self, event: Event, next_call: NextCall) -> Optional[Event]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__


class MiddlewareChain:
    def __init__(self, logger: Optional[Logger] = None) -> None:
        self._middlewares: list[Middleware] = []
        self._logger = logger
        self._lock = threading.RLock()

    def add(self, middleware: Middleware) -> "MiddlewareChain":
        with self._lock:
            self._middlewares.append(middleware)
        return self

    def run(self, event: Event) -> Optional[Event]:
        with self._lock:
            chain = list(self._middlewares)

        def make_link(index: int) -> NextCall:
            def link(evt: Event) -> Optional[Event]:
                if index >= len(chain):
                    return evt  
                mw = chain[index]
                try:
                    return mw.process(evt, make_link(index + 1))
                except Exception as exc:  # noqa: BLE001
                    if self._logger:
                        self._logger.error(
                            "Middleware raised; dropping event",
                            extra={"middleware": mw.name, "event": evt.name, "error": str(exc)},
                        )
                    return None
            return link

        result = make_link(0)(event)
        if result is None:
            event.mark(EventStatus.DROPPED)
        return result

    def __len__(self) -> int:
        return len(self._middlewares)

class PriorityStampMiddleware(Middleware):
    def process(self, event: Event, next_call: NextCall) -> Optional[Event]:
        if event.priority is None:
            event.priority = default_priority(event.name)
        event.priority = resolve_priority(event)
        return next_call(event)


class ContextPropagationMiddleware(Middleware):
    def process(self, event: Event, next_call: NextCall) -> Optional[Event]:
        if event.context is None:
            return next_call(event)
        with use_context(event.context):
            return next_call(event)


class LoggingMiddleware(Middleware):
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    def process(self, event: Event, next_call: NextCall) -> Optional[Event]:
        self._logger.debug(
            "Event published",
            extra={
                "event": event.name,
                "event_id": event.event_id,
                "priority": event.priority.name if event.priority else None,
                "source": event.source,
                "correlation_id": event.correlation_id,
            },
        )
        result = next_call(event)
        if result is None:
            self._logger.debug(
                "Event dropped in pipeline",
                extra={"event": event.name, "event_id": event.event_id},
            )
        return result


class DeduplicationMiddleware(Middleware):
    def __init__(self, window_seconds: float = 5.0, max_tracked: int = 4096) -> None:
        self._window = window_seconds
        self._max = max_tracked
        self._seen: Dict[str, float] = {}
        self._order: Deque[str] = deque()
        self._lock = threading.Lock()

    def process(self, event: Event, next_call: NextCall) -> Optional[Event]:
        now = time.time()
        key = event.event_id
        with self._lock:
            self._evict(now)
            if key in self._seen:
                return None  
            self._seen[key] = now
            self._order.append(key)
            if len(self._order) > self._max:
                oldest = self._order.popleft()
                self._seen.pop(oldest, None)
        return next_call(event)

    def _evict(self, now: float) -> None:
        cutoff = now - self._window
        while self._order and self._seen.get(self._order[0], 0.0) < cutoff:
            stale = self._order.popleft()
            self._seen.pop(stale, None)


class RateLimitMiddleware(Middleware):
    def __init__(self, max_per_second: float = 100.0, max_tracked: int = 10000) -> None:
        self._max = max_per_second
        self._max_tracked = max_tracked
        self._counts: Dict[str, tuple[int, float]] = {}
        self._lock = threading.Lock()

    def _evict(self, now: float) -> None:
        cutoff = now - 1.0
        stale = [k for k, (_, start) in self._counts.items() if start < cutoff]
        for k in stale:
            del self._counts[k]

    def process(self, event: Event, next_call: NextCall) -> Optional[Event]:
        if event.is_emergency:
            return next_call(event)
        now = time.time()
        with self._lock:
            if len(self._counts) > self._max_tracked:
                self._evict(now)
            count, start = self._counts.get(event.name, (0, now))
            if now - start >= 1.0:
                count, start = 0, now
            if count >= self._max:
                return None
            self._counts[event.name] = (count + 1, start)
        return next_call(event)


class MetricsMiddleware(Middleware):
    def __init__(self) -> None:
        self._processed: Dict[str, int] = {}
        self._dropped: Dict[str, int] = {}
        self._lock = threading.Lock()

    def process(self, event: Event, next_call: NextCall) -> Optional[Event]:
        result = next_call(event)
        with self._lock:
            bucket = self._processed if result is not None else self._dropped
            bucket[event.name] = bucket.get(event.name, 0) + 1
        return result

    def snapshot(self) -> Dict[str, Dict[str, int]]:
        with self._lock:
            return {
                "processed": dict(self._processed),
                "dropped": dict(self._dropped),
            }
