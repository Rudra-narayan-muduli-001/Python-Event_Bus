from __future__ import annotations
from typing import Any, Callable, Dict, Optional
from app.core.constants.events import EventCategory, EventDeliveryMode
from app.core.event_bus.event_context import EventContext, current_context
from app.core.event_bus.event_priority import EventPriority
from app.core.event_bus.event_types import Event
from app.core.exceptions import EventPublishError
from app.logging import Logger

__all__ = ["Publisher", "ScopedPublisher"]

EventSink = Callable[[Event], Optional[Event]]


class Publisher:
    def __init__(
        self,
        sink: EventSink,
        *,
        default_source: Optional[str] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        if not callable(sink):
            raise TypeError("Publisher sink must be callable")
        self._sink = sink
        self._default_source = default_source
        self._logger = logger

    def emit(
        self,
        name: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        category: EventCategory = EventCategory.SYSTEM,
        source: Optional[str] = None,
        priority: Optional[EventPriority] = None,
        delivery_mode: EventDeliveryMode = EventDeliveryMode.ASYNC,
        context: Optional[EventContext] = None,
        **payload_kwargs: Any,
    ) -> Optional[Event]:
        merged: Dict[str, Any] = dict(payload or {})
        merged.update(payload_kwargs)

        event = Event(
            name=name,
            payload=merged,
            category=category,
            source=source or self._default_source,
            priority=priority,
            delivery_mode=delivery_mode,
            context=context or current_context(),
        )
        return self.publish(event)

    def publish(self, event: Event) -> Optional[Event]:
        if event.source is None and self._default_source is not None:
            event.source = self._default_source
            if event.context is not None and event.context.source is None:
                event.context.source = self._default_source

        try:
            accepted = self._sink(event)
        except Exception as exc:  
            raise EventPublishError(
                f"Failed to publish event {event.name!r}",
                cause=exc,
            ) from exc

        if accepted is None and self._logger:
            self._logger.debug(
                "Event dropped by bus pipeline",
                extra={"event": event.name, "event_id": event.event_id},
            )
        return accepted

    def emit_from(self, parent: Event, name: str, **payload: Any) -> Optional[Event]:
        child = parent.caused(name, **payload)
        return self.publish(child)

    def scoped(self, source: str) -> "ScopedPublisher":
        return ScopedPublisher(self._sink, source=source, logger=self._logger)

    def __repr__(self) -> str:  
        return f"<Publisher source={self._default_source!r}>"


class ScopedPublisher(Publisher):
    def __init__(
        self,
        sink: EventSink,
        *,
        source: str,
        logger: Optional[Logger] = None,
    ) -> None:
        super().__init__(sink, default_source=source, logger=logger)
        self._source = source

    @property
    def source(self) -> str:
        return self._source

    def emit(self, name: str, payload: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Optional[Event]:
        kwargs.pop("source", None)
        return super().emit(name, payload, source=self._source, **kwargs)

    def __repr__(self) -> str:  
        return f"<ScopedPublisher source={self._source!r}>"
