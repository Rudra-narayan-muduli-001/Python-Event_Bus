from __future__ import annotations
from typing import Any, Iterable, Optional
from app.core.exceptions.base import AIOSError, ErrorCategory, ErrorSeverity

__all__ = [
    "StateError",
    "InvalidStateTransitionError",
    "InvalidStateError",
    "StatePersistenceError",
    "StateSnapshotError",
    "StateValidationError",
    "StateLockError",
]


class StateError(AIOSError):
    default_category = ErrorCategory.STATE
    default_severity = ErrorSeverity.ERROR


class InvalidStateTransitionError(StateError):
    def __init__(
        self,
        from_state: Any,
        to_state: Any,
        *,
        allowed: Optional[Iterable[Any]] = None,
        **kwargs: Any,
    ) -> None:
        allowed_list = [str(s) for s in allowed] if allowed is not None else None
        super().__init__(
            f"Illegal state transition: {from_state} -> {to_state}",
            code="STATE_INVALID_TRANSITION",
            recoverable=False,
            **kwargs,
        )
        self.with_context(
            from_state=str(from_state),
            to_state=str(to_state),
            allowed=allowed_list,
        )


class InvalidStateError(StateError):
    def __init__(self, current_state: Any, operation: str, **kwargs: Any) -> None:
        super().__init__(
            f"Operation '{operation}' is not allowed in state '{current_state}'",
            code="STATE_INVALID_OPERATION",
            **kwargs,
        )
        self.with_context(current_state=str(current_state), operation=operation)


class StatePersistenceError(StateError):
    def __init__(self, operation: str, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"State {operation} failed",
            code="STATE_PERSISTENCE_ERROR",
            severity=ErrorSeverity.CRITICAL,
            cause=cause,
            **kwargs,
        )
        self.with_context(operation=operation)


class StateSnapshotError(StateError):
    def __init__(self, operation: str = "snapshot", cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"State {operation} operation failed",
            code="STATE_SNAPSHOT_ERROR",
            severity=ErrorSeverity.CRITICAL,
            cause=cause,
            **kwargs,
        )
        self.with_context(operation=operation)


class StateValidationError(StateError):
    def __init__(self, reason: str, **kwargs: Any) -> None:
        super().__init__(
            f"State validation failed: {reason}",
            code="STATE_VALIDATION_ERROR",
            **kwargs,
        )
        self.with_context(reason=reason)


class StateLockError(StateError):
    def __init__(self, timeout_seconds: Optional[float] = None, **kwargs: Any) -> None:
        detail = f" after {timeout_seconds}s" if timeout_seconds is not None else ""
        super().__init__(
            f"Failed to acquire state lock{detail}",
            code="STATE_LOCK_ERROR",
            severity=ErrorSeverity.CRITICAL,
            **kwargs,
        )
        self.with_context(timeout_seconds=timeout_seconds)
