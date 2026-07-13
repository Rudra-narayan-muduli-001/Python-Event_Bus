from __future__ import annotations
import contextvars
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, Optional

__all__ = [
    "EventContext",
    "current_context",
    "set_current_context",
    "use_context",
    "get_or_create_context",
]

_CURRENT: contextvars.ContextVar[Optional["EventContext"]] = contextvars.ContextVar(
    "aios_event_context", default=None
)


@dataclass
class EventContext:
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    causation_id: Optional[str] = None
    source: Optional[str] = None
    actor: Optional[str] = None
    baggage: Dict[str, Any] = field(default_factory=dict)

    context_id: str = field(default_factory=lambda: uuid.uuid4().hex, init=False)
    created_at: float = field(default_factory=time.time, init=False)

    def child(
        self,
        *,
        causation_id: Optional[str] = None,
        source: Optional[str] = None,
        actor: Optional[str] = None,
        **extra_baggage: Any,
    ) -> "EventContext":
        merged = dict(self.baggage)
        merged.update(extra_baggage)
        return EventContext(
            correlation_id=self.correlation_id,
            causation_id=causation_id if causation_id is not None else self.causation_id,
            source=source if source is not None else self.source,
            actor=actor if actor is not None else self.actor,
            baggage=merged,
        )

    def with_baggage(self, **kwargs: Any) -> "EventContext":
        self.baggage.update(kwargs)
        return self

    def get(self, key: str, default: Any = None) -> Any:
        return self.baggage.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_id": self.context_id,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "source": self.source,
            "actor": self.actor,
            "created_at": self.created_at,
            "baggage": dict(self.baggage),
        }

    def __repr__(self) -> str:  
        return (
            f"<EventContext corr={self.correlation_id[:8]} "
            f"ctx={self.context_id[:8]} source={self.source!r}>"
        )

def current_context() -> Optional[EventContext]:
    return _CURRENT.get()


def set_current_context(context: Optional[EventContext]) -> contextvars.Token:
    return _CURRENT.set(context)


def get_or_create_context(**kwargs: Any) -> EventContext:
    ctx = _CURRENT.get()
    if ctx is None:
        ctx = EventContext(**kwargs)
        _CURRENT.set(ctx)
    return ctx


@contextmanager
def use_context(context: EventContext) -> Iterator[EventContext]:
    token = _CURRENT.set(context)
    try:
        yield context
    finally:
        _CURRENT.reset(token)
