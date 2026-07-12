from __future__ import annotations
from typing import Any, Optional
from app.core.exceptions.base import AIOSError, ErrorCategory, ErrorSeverity

__all__ = [
    "RuntimeError_",
    "OperationError",
    "TimeoutError_",
    "RetryExhaustedError",
    "ResourceExhaustedError",
    "ToolExecutionError",
    "ModelInferenceError",
    "ExternalServiceError",
    "NotSupportedError",
    "RecoveryError",
]


class RuntimeError_(AIOSError):
    default_category = ErrorCategory.RUNTIME
    default_severity = ErrorSeverity.ERROR


class OperationError(RuntimeError_):
    def __init__(self, operation: str, reason: Optional[str] = None, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        suffix = f": {reason}" if reason else ""
        super().__init__(
            f"Operation '{operation}' failed{suffix}",
            code="RUNTIME_OPERATION_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(operation=operation, reason=reason)


class TimeoutError_(RuntimeError_):
    def __init__(self, operation: str, timeout_seconds: Optional[float] = None, **kwargs: Any) -> None:
        detail = f" after {timeout_seconds}s" if timeout_seconds is not None else ""
        super().__init__(
            f"Operation '{operation}' timed out{detail}",
            code="RUNTIME_TIMEOUT",
            severity=ErrorSeverity.WARNING,
            **kwargs,
        )
        self.with_context(operation=operation, timeout_seconds=timeout_seconds)


class RetryExhaustedError(RuntimeError_):
    def __init__(self, operation: str, attempts: int, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Operation '{operation}' failed after {attempts} attempt(s)",
            code="RUNTIME_RETRY_EXHAUSTED",
            recoverable=False,
            cause=cause,
            **kwargs,
        )
        self.with_context(operation=operation, attempts=attempts)


class ResourceExhaustedError(RuntimeError_):
    def __init__(self, resource: str, detail: Optional[str] = None, **kwargs: Any) -> None:
        suffix = f": {detail}" if detail else ""
        super().__init__(
            f"Resource exhausted: {resource}{suffix}",
            code="RUNTIME_RESOURCE_EXHAUSTED",
            severity=ErrorSeverity.CRITICAL,
            **kwargs,
        )
        self.with_context(resource=resource, detail=detail)


class ToolExecutionError(RuntimeError_):
    def __init__(self, tool: str, reason: Optional[str] = None, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        suffix = f": {reason}" if reason else ""
        super().__init__(
            f"Tool '{tool}' execution failed{suffix}",
            code="RUNTIME_TOOL_EXECUTION_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(tool=tool, reason=reason)


class ModelInferenceError(RuntimeError_):
    def __init__(self, model: str, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Model inference failed for '{model}'",
            code="RUNTIME_MODEL_INFERENCE_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(model=model)


class ExternalServiceError(RuntimeError_):
    def __init__(self, service: str, status_code: Optional[int] = None, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        detail = f" (status={status_code})" if status_code is not None else ""
        super().__init__(
            f"External service '{service}' call failed{detail}",
            code="RUNTIME_EXTERNAL_SERVICE_ERROR",
            severity=ErrorSeverity.WARNING,
            cause=cause,
            **kwargs,
        )
        self.with_context(service=service, status_code=status_code)


class NotSupportedError(RuntimeError_):
    def __init__(self, feature: str, reason: Optional[str] = None, **kwargs: Any) -> None:
        suffix = f": {reason}" if reason else ""
        super().__init__(
            f"Not supported: {feature}{suffix}",
            code="RUNTIME_NOT_SUPPORTED",
            recoverable=False,
            **kwargs,
        )
        self.with_context(feature=feature, reason=reason)


class RecoveryError(RuntimeError_):
    def __init__(self, subsystem: str, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Recovery failed for subsystem '{subsystem}'",
            code="RUNTIME_RECOVERY_ERROR",
            severity=ErrorSeverity.FATAL,
            recoverable=False,
            cause=cause,
            **kwargs,
        )
        self.with_context(subsystem=subsystem)
