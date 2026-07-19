from __future__ import annotations
import json
from typing import Any, Dict, Optional
from app.core.constants.events import EventCategory, EventDeliveryMode
from app.core.event_bus.event_context import EventContext
from app.core.event_bus.event_priority import EventPriority
from app.core.event_bus.event_types import Event, EventStatus
from app.core.exceptions import EventSerializationError

__all__ = ["EventSerializer"]


class EventSerializer:
    @classmethod
    def to_dict(cls, event: Event) -> Dict[str, Any]:
        try:
            return event.to_dict()
        except Exception as exc: 
            raise EventSerializationError(
                f"Failed to serialize event {event.name!r} to dict",
                cause=exc,
            ) from exc

    @classmethod
    def serialize(cls, event: Event, *, indent: Optional[int] = None) -> str:
        try:
            return json.dumps(cls.to_dict(event), ensure_ascii=False, indent=indent)
        except (TypeError, ValueError) as exc:
            raise EventSerializationError(
                f"Failed to JSON-encode event {event.name!r}",
                cause=exc,
            ) from exc

    @classmethod
    def to_bytes(cls, event: Event) -> bytes:
        return cls.serialize(event).encode("utf-8")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Event:
        if not isinstance(data, dict):
            raise EventSerializationError(
                f"Cannot deserialize event from {type(data).__name__}; dict required"
            )
        if "name" not in data:
            raise EventSerializationError("Event payload missing required key 'name'")

        try:
            context = cls._context_from_dict(data.get("context"))

            priority_raw = data.get("priority")
            priority = EventPriority(priority_raw) if priority_raw is not None else None

            event = Event(
                name=data["name"],
                payload=dict(data.get("payload") or {}),
                category=EventCategory(data.get("category", EventCategory.SYSTEM.value)),
                source=data.get("source"),
                priority=priority,
                delivery_mode=EventDeliveryMode(
                    data.get("delivery_mode", EventDeliveryMode.ASYNC.value)
                ),
                context=context,
            )
            if data.get("event_id"):
                object.__setattr__(event, "event_id", data["event_id"])
            if data.get("timestamp") is not None:
                object.__setattr__(event, "timestamp", float(data["timestamp"]))
            if data.get("status"):
                object.__setattr__(event, "status", EventStatus(data["status"]))

            return event
        except EventSerializationError:
            raise
        except Exception as exc:  
            raise EventSerializationError(
                f"Failed to reconstruct event from dict (name={data.get('name')!r})",
                cause=exc,
            ) from exc

    @classmethod
    def deserialize(cls, raw: str | bytes) -> Event:
        try:
            if isinstance(raw, (bytes, bytearray)):
                raw = raw.decode("utf-8")
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError) as exc:
            raise EventSerializationError(
                "Failed to JSON-decode event payload",
                cause=exc,
            ) from exc
        return cls.from_dict(data)

    @staticmethod
    def _context_from_dict(raw: Optional[Dict[str, Any]]) -> Optional[EventContext]:
        if raw is None:
            return None
        context = EventContext(
            correlation_id=raw.get("correlation_id") or "",
            causation_id=raw.get("causation_id"),
            source=raw.get("source"),
            actor=raw.get("actor"),
            baggage=dict(raw.get("baggage") or {}),
        )
        if raw.get("context_id"):
            object.__setattr__(context, "context_id", raw["context_id"])
        if raw.get("created_at") is not None:
            object.__setattr__(context, "created_at", float(raw["created_at"]))
        return context
