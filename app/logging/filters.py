import logging
import re
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set


class LevelFilter(logging.Filter):
    def __init__(self, min_level: int = logging.WARNING) -> None:
        super().__init__()
        self.min_level = min_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= self.min_level


class ModuleFilter(logging.Filter):
    def __init__(
        self,
        include: Optional[list] = None,
        exclude: Optional[list] = None,
    ) -> None:
        super().__init__()
        self._include = [re.compile(p) for p in (include or [])]
        self._exclude = [re.compile(p) for p in (exclude or [])]

    def filter(self, record: logging.LogRecord) -> bool:
        name = record.name
        for pattern in self._exclude:
            if pattern.search(name):
                return False
        if not self._include:
            return True

        return any(pattern.search(name) for pattern in self._include)


@dataclass
class _RateBucket:
    maxlen: int = 1000
    timestamps: deque = field(init=False)

    def __post_init__(self):
        self.timestamps = deque(maxlen=self.maxlen)


class RateLimitFilter(logging.Filter):
    def __init__(
        self,
        max_per_window: int = 10,
        window_seconds: float = 60.0,
        cooldown_seconds: float = 30.0,
    ) -> None:
        super().__init__()
        self.max_per_window = max_per_window
        self.window_seconds = window_seconds
        self.cooldown_seconds = cooldown_seconds
        self._buckets: Dict[str, _RateBucket] = {}
        self._suppressed_until: Dict[str, float] = {}
        self._lock = threading.Lock()

    def _key(self, record: logging.LogRecord) -> str:
        return f"{record.levelno}:{record.getMessage()}"

    def filter(self, record: logging.LogRecord) -> bool:
        key = self._key(record)
        now = time.monotonic()

        with self._lock:
            suppress_until = self._suppressed_until.get(key)
            if suppress_until is not None and now < suppress_until:
                return False
            if suppress_until is not None and now >= suppress_until:
                del self._suppressed_until[key]

            bucket = self._buckets.setdefault(
                key, _RateBucket(maxlen=self.max_per_window)
            )
            cutoff = now - self.window_seconds
            while bucket.timestamps and bucket.timestamps[0] < cutoff:
                bucket.timestamps.popleft()

            if len(bucket.timestamps) >= self.max_per_window:
                self._suppressed_until[key] = now + self.cooldown_seconds
                return False

            bucket.timestamps.append(now)
            return True


class ContextFilter(logging.Filter):
    def __init__(self, **initial_context: Any) -> None:
        super().__init__()
        self._context: Dict[str, Any] = dict(initial_context)
        self._lock = threading.Lock()

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._context[key] = value

    def set_many(self, fields: Dict[str, Any]) -> None:
        with self._lock:
            self._context.update(fields)

    def remove(self, key: str) -> None:
        with self._lock:
            self._context.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._context.clear()

    def get(self, key: str, default: Any = None) -> Any:
        return self._context.get(key, default)

    @property
    def context(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._context)

    def filter(self, record: logging.LogRecord) -> bool:
        with self._lock:
            for key, value in self._context.items():
                if not hasattr(record, key):
                    setattr(record, key, value)
        return True
