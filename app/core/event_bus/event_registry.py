from __future__ import annotations
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Optional
from app.core.constants.events import (
    EVENT_ENUM_BY_CATEGORY,
    EventCategory,
    EventPriority,
    default_priority,
)
from app.core.exceptions import UnknownEventTypeError

__all__ = ["EventDescriptor", "EventRegistry"]


@dataclass(frozen=True)
class EventDescriptor:
    name: str
    category: EventCategory
    default_priority: EventPriority
    member: Optional[Enum] = None
    dynamic: bool = False


class EventRegistry:
    def __init__(self, *, load_catalog: bool = True) -> None:
        self._descriptors: Dict[str, EventDescriptor] = {}
        self._lock = threading.RLock()
        if load_catalog:
            self._load_catalog()
    def _load_catalog(self) -> None:
        for category, enum_cls in EVENT_ENUM_BY_CATEGORY.items():
            for member in enum_cls:
                descriptor = EventDescriptor(
                    name=member.value,
                    category=category,
                    default_priority=default_priority(member.value),
                    member=member,
                    dynamic=False,
                )
                self._descriptors[member.value] = descriptor
    def register(
        self,
        name: str,
        category: EventCategory,
        *,
        priority: Optional[EventPriority] = None,
        replace: bool = False,
    ) -> EventDescriptor:
        if not name:
            raise ValueError("Event name must be a non-empty string")

        with self._lock:
            existing = self._descriptors.get(name)
            if existing is not None:
                if not existing.dynamic:
                    raise UnknownEventTypeError(
                        f"Cannot override first-party event name {name!r}"
                    )
                if not replace:
                    return existing  

            descriptor = EventDescriptor(
                name=name,
                category=category,
                default_priority=priority or default_priority(name),
                member=None,
                dynamic=True,
            )
            self._descriptors[name] = descriptor
            return descriptor

    def register_many(
        self, names: Iterable[str], category: EventCategory
    ) -> List[EventDescriptor]:
        return [self.register(name, category) for name in names]

    def unregister(self, name: str) -> None:
        with self._lock:
            existing = self._descriptors.get(name)
            if existing is None:
                return
            if not existing.dynamic:
                raise UnknownEventTypeError(
                    f"Cannot unregister first-party event name {name!r}"
                )
            self._descriptors.pop(name, None)
    def is_known(self, name: str) -> bool:
        with self._lock:
            return name in self._descriptors

    def validate(self, name: str) -> None:
        if not self.is_known(name):
            raise UnknownEventTypeError(f"Unknown event name: {name!r}")

    def get(self, name: str) -> Optional[EventDescriptor]:
        with self._lock:
            return self._descriptors.get(name)

    def require(self, name: str) -> EventDescriptor:
        descriptor = self.get(name)
        if descriptor is None:
            raise UnknownEventTypeError(f"Unknown event name: {name!r}")
        return descriptor

    def category_of(self, name: str) -> EventCategory:
        return self.require(name).category

    def default_priority_of(self, name: str) -> EventPriority:
        return self.require(name).default_priority

    def names(self, category: Optional[EventCategory] = None) -> List[str]:
        with self._lock:
            if category is None:
                return sorted(self._descriptors.keys())
            return sorted(
                d.name for d in self._descriptors.values() if d.category is category
            )

    def descriptors(self) -> List[EventDescriptor]:
        with self._lock:
            return list(self._descriptors.values())

    def __contains__(self, name: str) -> bool:
        return self.is_known(name)

    def __len__(self) -> int:
        with self._lock:
            return len(self._descriptors)

    def __repr__(self) -> str:  
        with self._lock:
            dynamic = sum(1 for d in self._descriptors.values() if d.dynamic)
        return f"<EventRegistry total={len(self)} dynamic={dynamic}>"
