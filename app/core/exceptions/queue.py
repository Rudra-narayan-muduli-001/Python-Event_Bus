from __future__ import annotations
from typing import Any, Optional
from app.core.exceptions.base import AIOSError, ErrorCategory, ErrorSeverity

__all__ = [
    "QueueError",
    "QueueFullError",
    "QueueEmptyError",
    "QueueTimeoutError",
    "QueueClosedError",
    "InvalidPriorityError",
    "QueueInterruptedError",
    "QueueOverflowError",
]


class QueueError(AIOSError):
    default_category = ErrorCategory.QUEUE
    default_severity = ErrorSeverity.ERROR


class QueueFullError(QueueError):
    def __init__(self, queue_name: str, maxsize: Optional[int] = None, **kwargs: Any) -> None:
        detail = f" (maxsize={maxsize})" if maxsize is not None else ""
        super().__init__(
            f"Queue '{queue_name}' is full{detail}",
            code="QUEUE_FULL",
            severity=ErrorSeverity.WARNING,
            **kwargs,
        )
        self.with_context(queue_name=queue_name, maxsize=maxsize)


class QueueEmptyError(QueueError):
    def __init__(self, queue_name: str, **kwargs: Any) -> None:
        super().__init__(
            f"Queue '{queue_name}' is empty",
            code="QUEUE_EMPTY",
            severity=ErrorSeverity.DEBUG,
            **kwargs,
        )
        self.with_context(queue_name=queue_name)


class QueueTimeoutError(QueueError):
    def __init__(self, queue_name: str, operation: str, timeout_seconds: Optional[float] = None, **kwargs: Any) -> None:
        detail = f" after {timeout_seconds}s" if timeout_seconds is not None else ""
        super().__init__(
            f"Queue '{queue_name}' {operation} timed out{detail}",
            code="QUEUE_TIMEOUT",
            severity=ErrorSeverity.WARNING,
            **kwargs,
        )
        self.with_context(queue_name=queue_name, operation=operation, timeout_seconds=timeout_seconds)


class QueueClosedError(QueueError):
    def __init__(self, queue_name: str, operation: str = "operation", **kwargs: Any) -> None:
        super().__init__(
            f"Queue '{queue_name}' is closed; cannot perform {operation}",
            code="QUEUE_CLOSED",
            recoverable=False,
            **kwargs,
        )
        self.with_context(queue_name=queue_name, operation=operation)


class InvalidPriorityError(QueueError):
    def __init__(self, priority: Any, queue_name: Optional[str] = None, **kwargs: Any) -> None:
        where = f" for queue '{queue_name}'" if queue_name else ""
        super().__init__(
            f"Invalid priority {priority!r}{where}",
            code="QUEUE_INVALID_PRIORITY",
            **kwargs,
        )
        self.with_context(priority=repr(priority), queue_name=queue_name)


class QueueInterruptedError(QueueError):
    def __init__(self, queue_name: str, **kwargs: Any) -> None:
        super().__init__(
            f"Queue '{queue_name}' operation interrupted",
            code="QUEUE_INTERRUPTED",
            severity=ErrorSeverity.INFO,
            **kwargs,
        )
        self.with_context(queue_name=queue_name)


class QueueOverflowError(QueueError):
    def __init__(self, queue_name: str, dropped: int = 1, maxsize: Optional[int] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Queue '{queue_name}' overflowed; dropped {dropped} item(s)",
            code="QUEUE_OVERFLOW",
            severity=ErrorSeverity.ERROR,
            **kwargs,
        )
        self.with_context(queue_name=queue_name, maxsize=maxsize, dropped=dropped)
