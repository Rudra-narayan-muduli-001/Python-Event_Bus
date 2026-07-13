from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING, Tuple
import itertools
from app.core.constants.events import (
    EMERGENCY_EVENTS,
    EventPriority,
    default_priority,
)

if TYPE_CHECKING:  
    from app.core.event_bus.event_types import Event

__all__ = [
    "EventPriority",
    "PriorityClass",
    "resolve_priority",
    "PrioritizedEvent",
    "PriorityAgingPolicy",
]


class PriorityClass(IntEnum):
    BACKGROUND = 0   
    STANDARD = 1     
    ELEVATED = 2    
    IMMEDIATE = 3  

    @classmethod
    def from_priority(cls, priority: EventPriority) -> "PriorityClass":
        if priority >= EventPriority.EMERGENCY:
            return cls.IMMEDIATE
        if priority >= EventPriority.HIGH:
            return cls.ELEVATED
        if priority >= EventPriority.NORMAL:
            return cls.STANDARD
        return cls.BACKGROUND


def resolve_priority(event: "Event") -> EventPriority:
    if event.name in EMERGENCY_EVENTS:
        return EventPriority.EMERGENCY
    if event.priority is not None:
        return event.priority
    return default_priority(event.name)

_sequence = itertools.count()


@dataclass(order=True)
class PrioritizedEvent:
    sort_key: Tuple[int, int] = field(init=False)
    event: "Event" = field(compare=False)

    def __init__(self, event: "Event") -> None:
        self.event = event
        priority = resolve_priority(event)
        object.__setattr__(self, "sort_key", (-int(priority), next(_sequence)))

    @property
    def priority(self) -> EventPriority:
        return EventPriority(-self.sort_key[0])

    @property
    def priority_class(self) -> PriorityClass:
        return PriorityClass.from_priority(self.priority)

    def __repr__(self) -> str: 
        return (
            f"<PrioritizedEvent name={self.event.name!r} "
            f"priority={self.priority.name} seq={self.sort_key[1]}>"
        )


@dataclass
class PriorityAgingPolicy:
    enabled: bool = True
    step_seconds: float = 5.0
    max_priority: EventPriority = EventPriority.HIGH

    def effective_priority(self, event: "Event") -> EventPriority:
        base = resolve_priority(event)
        if not self.enabled or base >= EventPriority.EMERGENCY:
            return base
        if self.step_seconds <= 0:
            return base

        bumps = int(event.age_seconds // self.step_seconds)
        if bumps <= 0:
            return base

        aged_value = min(int(base) + (bumps * 10), int(self.max_priority))
        candidates = [p for p in EventPriority if int(p) <= aged_value]
        return max(candidates) if candidates else base
