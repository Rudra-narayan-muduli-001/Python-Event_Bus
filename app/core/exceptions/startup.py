from __future__ import annotations
from typing import Any, Optional
from app.core.exceptions.base import AIOSError, ErrorCategory, ErrorSeverity

__all__ = [
    "StartupError",
    "InitializationError",
    "BootstrapError",
    "ServiceStartupError",
    "FeatureGroupInitError",
    "PhaseInitializationError",
    "StartupTimeoutError",
    "ShutdownError",
]


class StartupError(AIOSError):
    default_category = ErrorCategory.STARTUP
    default_severity = ErrorSeverity.FATAL

    def __init__(self, message: str, **kwargs: Any) -> None:
        # A failed boot must not silently continue.
        kwargs.setdefault("recoverable", False)
        super().__init__(message, **kwargs)


class InitializationError(StartupError):
    def __init__(self, component: str, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Failed to initialize component '{component}'",
            code="STARTUP_INIT_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(component=component)


class BootstrapError(StartupError):
    def __init__(self, stage: str, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Bootstrap failed at stage '{stage}'",
            code="STARTUP_BOOTSTRAP_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(stage=stage)


class ServiceStartupError(StartupError):
    def __init__(self, service: str, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Service '{service}' failed to start",
            code="STARTUP_SERVICE_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(service=service)


class FeatureGroupInitError(StartupError):
    def __init__(
        self,
        feature_group: str,
        cause: Optional[BaseException] = None,
        *,
        optional: bool = False,
        **kwargs: Any,
    ) -> None:
        if optional:
            kwargs.setdefault("severity", ErrorSeverity.WARNING)
            kwargs["recoverable"] = True
        super().__init__(
            f"Feature group '{feature_group}' failed to initialize"
            + (" (optional; continuing degraded)" if optional else ""),
            code="STARTUP_FEATURE_GROUP_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(feature_group=feature_group, optional=optional)


class PhaseInitializationError(StartupError):
    def __init__(self, phase: Any, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Initialization phase '{phase}' failed",
            code="STARTUP_PHASE_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(phase=str(phase))


class StartupTimeoutError(StartupError):
    def __init__(
        self,
        component: str,
        timeout_seconds: Optional[float] = None,
        *,
        cause: Optional[BaseException] = None,
        **kwargs: Any,
    ) -> None:
        detail = f" after {timeout_seconds}s" if timeout_seconds is not None else ""
        super().__init__(
            f"Startup of '{component}' timed out{detail}",
            code="STARTUP_TIMEOUT",
            cause=cause,
            **kwargs,
        )
        self.with_context(component=component, timeout_seconds=timeout_seconds)


class ShutdownError(StartupError):
    default_severity = ErrorSeverity.WARNING

    def __init__(self, component: str, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        kwargs["recoverable"] = True
        super().__init__(
            f"Component '{component}' failed to shut down cleanly",
            code="STARTUP_SHUTDOWN_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(component=component)
