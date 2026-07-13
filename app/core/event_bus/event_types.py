from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
from app.core.constants.events import EventCategory, EventDeliveryMode, default_priority
from app.core.event_bus.event_priority import EventPriority
from app.core.event_bus.event_context import EventContext

__all__ = [
    "EventStatus",
    "Event",
]


class EventStatus(str, Enum):

    CREATED = "created"          
    PUBLISHED = "published"      
    DISPATCHING = "dispatching"  
    HANDLED = "handled"          
    FAILED = "failed"            
    DROPPED = "dropped"          


@dataclass
class Event:
    name: str
    payload: Dict[str, Any] = field(default_factory=dict)
    category: EventCategory = EventCategory.SYSTEM
    source: Optional[str] = None
    priority: Optional[EventPriority] = None
    delivery_mode: EventDeliveryMode = EventDeliveryMode.ASYNC
    context: Optional[EventContext] = None
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex, init=False)
    timestamp: float = field(default_factory=time.time, init=False)
    status: EventStatus = field(default=EventStatus.CREATED, init=False)

    def __post_init__(self) -> None:
        if self.priority is None:
            self.priority = default_priority(self.name)
        if self.context is None:
            self.context = EventContext(source=self.source)
        elif self.source is None:
            self.source = self.context.source
    @property
    def correlation_id(self) -> str:
        assert self.context is not None  
        return self.context.correlation_id

    @property
    def age_seconds(self) -> float:
        return max(0.0, time.time() - self.timestamp)

    @property
    def is_emergency(self) -> bool:
        return self.priority is EventPriority.EMERGENCY

    def mark(self, status: EventStatus) -> "Event":
        self.status = status
        return self

    def with_payload(self, **kwargs: Any) -> "Event":
        self.payload.update(kwargs)
        return self

    def caused(self, name: str, **payload: Any) -> "Event":
        assert self.context is not None
        child_ctx = self.context.child(causation_id=self.event_id, source=self.source)
        return Event(
            name=name,
            payload=dict(payload),
            source=self.source,
            context=child_ctx,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "name": self.name,
            "category": self.category.value,
            "source": self.source,
            "priority": int(self.priority) if self.priority is not None else None,
            "delivery_mode": self.delivery_mode.value,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "context": self.context.to_dict() if self.context is not None else None,
            "payload": self.payload,
        }

    def __str__(self) -> str:
        return f"[{self.name}] id={self.event_id[:8]} status={self.status.value}"

    def __repr__(self) -> str:  
        return (
            f"Event(name={self.name!r}, id={self.event_id!r}, "
            f"category={self.category.value!r}, priority={self.priority!r}, "
            f"status={self.status.value!r})"
        )
