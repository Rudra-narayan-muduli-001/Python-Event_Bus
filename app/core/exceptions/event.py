from __future__ import annotations
from typing import Any, Optional
from app.core.exceptions.base import AIOSError, ErrorCategory, ErrorSeverity

__all__ = [
    "EventError",
    "EventPublishError",
    "EventSubscriptionError",
    "EventHandlerError",
    "EventSerializationError",
    "UnknownEventTypeError",
    "EventDispatchError",
]

class EventError(AIOSError):
    default_category = ErrorCategory.EVENT
    default_severity = ErrorSeverity.ERROR


class EventPublishError(EventError):
    def __init__(self, event_type: str, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Failed to publish event '{event_type}'",
            code="EVENT_PUBLISH_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(event_type=event_type)


class EventSubscriptionError(EventError):
    def __init__(self, event_type: str, reason: Optional[str] = None, **kwargs: Any) -> None:
        suffix = f": {reason}" if reason else ""
        super().__init__(
            f"Event subscription failed for '{event_type}'{suffix}",
            code="EVENT_SUBSCRIPTION_ERROR",
            **kwargs,
        )
        self.with_context(event_type=event_type, reason=reason)


class EventHandlerError(EventError):
    def __init__(
        self,
        event_type: str,
        handler: Any,
        cause: Optional[BaseException] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            f"Handler {handler!r} failed while processing event '{event_type}'",
            code="EVENT_HANDLER_ERROR",
            severity=ErrorSeverity.WARNING,
            cause=cause,
            **kwargs,
        )
        self.with_context(event_type=event_type, handler=repr(handler))


class EventSerializationError(EventError):
    def __init__(self, event_type: str, operation: str = "serialize", cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Failed to {operation} event '{event_type}'",
            code="EVENT_SERIALIZATION_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(event_type=event_type, operation=operation)


class UnknownEventTypeError(EventError):
    def __init__(self, event_type: str, **kwargs: Any) -> None:
        super().__init__(
            f"Unknown event type: '{event_type}'",
            code="EVENT_UNKNOWN_TYPE",
            **kwargs,
        )
        self.with_context(event_type=event_type)


class EventDispatchError(EventError):

    def __init__(self, reason: Optional[str] = None, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        suffix = f": {reason}" if reason else ""
        super().__init__(
            f"Event dispatch failure{suffix}",
            code="EVENT_DISPATCH_ERROR",
            severity=ErrorSeverity.CRITICAL,
            cause=cause,
            **kwargs,
        )
        self.with_context(reason=reason)
