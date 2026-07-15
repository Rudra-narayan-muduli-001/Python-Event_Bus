from __future__ import annotations
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
from app.core.constants.events import EventDeliveryMode
from app.core.event_bus.event_types import Event, EventStatus
from app.core.event_bus.event_store import EventStore
from app.core.event_bus.middleware import Middleware, MiddlewareChain
from app.core.event_bus.subscriber import Subscriber
from app.core.exceptions.event import EventDispatchError
from app.logging.logger_factory import LoggerFactory
from app.logging.logger import Logger, LogLevel

__all__ = ["Dispatcher"]


class Dispatcher:
    def __init__(
        self,
        *,
        middleware: Optional[MiddlewareChain] = None,
        store: Optional[EventStore] = None,
        max_workers: int = 4,
        logger: Optional[Logger] = None,
        logger_factory: Optional[LoggerFactory] = None,
    ) -> None:
        self._factory = logger_factory or LoggerFactory()
        self._logger = logger or self._factory.create_console_logger(
            "core.event_bus.dispatcher", LogLevel.INFO
        )
        self._middleware = middleware or MiddlewareChain(logger=self._logger)
        self._store = store
        self._subscribers: List[Subscriber] = []
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="aios-event"
        )
        self._closed = False
    def add_subscriber(self, subscriber: Subscriber) -> Subscriber:
        with self._lock:
            self._subscribers.append(subscriber)
        subscriber.bind_unsubscribe(self._remove_subscriber)
        return subscriber

    def _remove_subscriber(self, subscriber: Subscriber) -> None:
        with self._lock:
            try:
                self._subscribers.remove(subscriber)
            except ValueError:
                pass

    def add_middleware(self, middleware: Middleware) -> None:
        self._middleware.add(middleware)

    @property
    def subscriber_count(self) -> int:
        with self._lock:
            return len(self._subscribers)

    def dispatch(self, event: Event) -> Event:
        if self._closed:
            raise EventDispatchError(
                f"Dispatcher is closed; cannot dispatch {event.name!r}"
            )

        processed = self._middleware.run(event)
        if processed is None:
            return self._finalize(event) 

        processed.mark(EventStatus.DISPATCHING)
        targets = self._select(processed)
        if not targets:
            processed.mark(EventStatus.DROPPED)
            return self._finalize(processed)

        mode = processed.delivery_mode
        if mode is EventDeliveryMode.QUEUED:
            for sub in targets:
                self._executor.submit(self._safe_invoke, sub, processed)
            return self._finalize(processed)

        try:
            for sub in targets:
                self._safe_invoke(sub, processed)
            processed.mark(EventStatus.HANDLED)
        except Exception as exc: 
            processed.mark(EventStatus.FAILED)
            raise EventDispatchError(
                f"Dispatch failed for {event.name!r}", cause=exc
            ) from exc

        return self._finalize(processed)
    async def dispatch_async(self, event: Event) -> Event:
        if self._closed:
            raise EventDispatchError(
                f"Dispatcher is closed; cannot dispatch {event.name!r}"
            )

        processed = self._middleware.run(event)
        if processed is None:
            return self._finalize(event)

        processed.mark(EventStatus.DISPATCHING)
        targets = self._select(processed)
        if not targets:
            processed.mark(EventStatus.DROPPED)
            return self._finalize(processed)

        loop = asyncio.get_running_loop()
        coros = []
        for sub in targets:
            if sub.is_async:
                coros.append(sub.invoke_async(processed))
            else:
                coros.append(loop.run_in_executor(self._executor, self._safe_invoke, sub, processed))

        results = await asyncio.gather(*coros, return_exceptions=True)
        failed = [r for r in results if isinstance(r, Exception)]
        processed.mark(EventStatus.FAILED if failed else EventStatus.HANDLED)
        if failed:
            self._logger.error(
                "Async dispatch had handler failures",
                extra={"event": processed.name, "failures": len(failed)},
            )
        return self._finalize(processed)

    def _select(self, event: Event) -> List[Subscriber]:
        with self._lock:
            matches = [s for s in self._subscribers if s.wants(event)]
        matches.sort(key=lambda s: s.priority, reverse=True)
        return matches

    def _safe_invoke(self, subscriber: Subscriber, event: Event) -> None:
        subscriber.invoke(event)

    def _finalize(self, event: Event) -> Event:
        if self._store is not None:
            try:
                self._store.record(event)
            except Exception as exc: 
                self._logger.error(
                    "Event store record failed",
                    extra={"event": event.name, "error": str(exc)},
                )
        return event
    def close(self, *, wait: bool = True) -> None:
        if self._closed:
            return
        self._closed = True
        self._executor.shutdown(wait=wait)
        self._logger.info("Dispatcher closed")

    def __repr__(self) -> str:  
        return (
            f"<Dispatcher subscribers={self.subscriber_count} "
            f"middleware={len(self._middleware)} closed={self._closed}>"
        )
