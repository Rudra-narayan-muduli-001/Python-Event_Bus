from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Callable, Pattern
import re
from app.core.constants.events import EventCategory
from app.core.event_bus.event_priority import EventPriority, resolve_priority
from app.core.event_bus.event_types import Event

__all__ = [
    "EventFilter",
    "AcceptAllFilter",
    "NameFilter",
    "NamePrefixFilter",
    "NamePatternFilter",
    "CategoryFilter",
    "PriorityFilter",
    "SourceFilter",
    "PayloadFilter",
    "PredicateFilter",
    "AndFilter",
    "OrFilter",
    "NotFilter",
]


class EventFilter(ABC):

    @abstractmethod
    def matches(self, event: Event) -> bool:
        raise NotImplementedError
    def accepts(self, event: Event) -> bool:
        try:
            return self.matches(event)
        except Exception:  
            return False

    def __and__(self, other: "EventFilter") -> "EventFilter":
        return AndFilter(self, other)

    def __or__(self, other: "EventFilter") -> "EventFilter":
        return OrFilter(self, other)

    def __invert__(self) -> "EventFilter":
        return NotFilter(self)

    @staticmethod
    def all_of(*filters: "EventFilter") -> "EventFilter":
        return AndFilter(*filters)

    @staticmethod
    def any_of(*filters: "EventFilter") -> "EventFilter":
        return OrFilter(*filters)


class AcceptAllFilter(EventFilter):

    def matches(self, event: Event) -> bool:
        return True

    def __repr__(self) -> str:  
        return "<AcceptAll>"


class NameFilter(EventFilter):

    def __init__(self, *names: str) -> None:
        self._names = frozenset(names)

    def matches(self, event: Event) -> bool:
        return event.name in self._names

    def __repr__(self) -> str:  
        return f"<Name in {sorted(self._names)}>"


class NamePrefixFilter(EventFilter):
    def __init__(self, *prefixes: str) -> None:
        self._prefixes = tuple(prefixes)

    def matches(self, event: Event) -> bool:
        return event.name.startswith(self._prefixes)

    def __repr__(self) -> str:  
        return f"<NamePrefix {self._prefixes}>"


class NamePatternFilter(EventFilter):
    def __init__(self, pattern: str | Pattern[str]) -> None:
        self._pattern: Pattern[str] = (
            pattern if isinstance(pattern, re.Pattern) else re.compile(pattern)
        )

    def matches(self, event: Event) -> bool:
        return self._pattern.search(event.name) is not None

    def __repr__(self) -> str:  
        return f"<NamePattern {self._pattern.pattern!r}>"


class CategoryFilter(EventFilter):
    def __init__(self, *categories: EventCategory) -> None:
        self._categories = frozenset(categories)

    def matches(self, event: Event) -> bool:
        return event.category in self._categories

    def __repr__(self) -> str:  
        return f"<Category in {[c.value for c in self._categories]}>"


class PriorityFilter(EventFilter):
    def __init__(self, minimum: EventPriority) -> None:
        self._minimum = minimum

    def matches(self, event: Event) -> bool:
        return resolve_priority(event) >= self._minimum

    def __repr__(self) -> str:  
        return f"<Priority >= {self._minimum.name}>"


class SourceFilter(EventFilter):
    def __init__(self, *sources: str) -> None:
        self._sources = frozenset(sources)

    def matches(self, event: Event) -> bool:
        return event.source in self._sources

    def __repr__(self) -> str:  
        return f"<Source in {sorted(self._sources)}>"


class PayloadFilter(EventFilter):
    _MISSING = object()

    def __init__(self, key: str, expected: Any = _MISSING) -> None:
        self._key = key
        self._expected = expected

    def matches(self, event: Event) -> bool:
        if self._key not in event.payload:
            return False
        if self._expected is PayloadFilter._MISSING:
            return True
        return event.payload[self._key] == self._expected

    def __repr__(self) -> str:  
        return f"<Payload {self._key!r}>"


class PredicateFilter(EventFilter):
    def __init__(self, predicate: Callable[[Event], bool]) -> None:
        if not callable(predicate):
            raise TypeError("PredicateFilter requires a callable")
        self._predicate = predicate

    def matches(self, event: Event) -> bool:
        return bool(self._predicate(event))

    def __repr__(self) -> str:  
        name = getattr(self._predicate, "__name__", repr(self._predicate))
        return f"<Predicate {name}>"


class AndFilter(EventFilter):
    def __init__(self, *filters: EventFilter) -> None:
        self._filters = tuple(filters)

    def matches(self, event: Event) -> bool:
        return all(f.accepts(event) for f in self._filters)

    def __repr__(self) -> str:  
        return f"({' AND '.join(repr(f) for f in self._filters)})"


class OrFilter(EventFilter):
    def __init__(self, *filters: EventFilter) -> None:
        self._filters = tuple(filters)

    def matches(self, event: Event) -> bool:
        return any(f.accepts(event) for f in self._filters)

    def __repr__(self) -> str: 
        return f"({' OR '.join(repr(f) for f in self._filters)})"


class NotFilter(EventFilter):
    def __init__(self, inner: EventFilter) -> None:
        self._inner = inner

    def matches(self, event: Event) -> bool:
        return not self._inner.accepts(event)

    def __repr__(self) -> str:  
        return f"(NOT {self._inner!r})"
