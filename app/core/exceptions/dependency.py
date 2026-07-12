from __future__ import annotations
from typing import Any, Iterable, Optional
from app.core.exceptions.base import AIOSError, ErrorCategory, ErrorSeverity

__all__ = [
    "DependencyError",
    "DependencyNotFoundError",
    "DependencyResolutionError",
    "CircularDependencyError",
    "DuplicateRegistrationError",
    "ProviderError",
    "ScopeError",
]

class DependencyError(AIOSError):
    default_category = ErrorCategory.DEPENDENCY
    default_severity = ErrorSeverity.CRITICAL


class DependencyNotFoundError(DependencyError):
    def __init__(self, token: Any, **kwargs: Any) -> None:
        super().__init__(
            f"No registered dependency for token: {token!r}",
            code="DI_NOT_FOUND",
            **kwargs,
        )
        self.with_context(token=repr(token))

class DependencyResolutionError(DependencyError):
    def __init__(self, token: Any, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Failed to resolve dependency: {token!r}",
            code="DI_RESOLUTION_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(token=repr(token))

class CircularDependencyError(DependencyError):

    def __init__(self, chain: Iterable[Any], **kwargs: Any) -> None:
        chain_list = [repr(item) for item in chain]
        path = " -> ".join(chain_list) if chain_list else "<unknown>"
        super().__init__(
            f"Circular dependency detected: {path}",
            code="DI_CIRCULAR_DEPENDENCY",
            recoverable=False,
            **kwargs,
        )
        self.with_context(chain=chain_list)

class DuplicateRegistrationError(DependencyError):
    def __init__(self, token: Any, **kwargs: Any) -> None:
        super().__init__(
            f"Dependency already registered for token: {token!r}",
            code="DI_DUPLICATE_REGISTRATION",
            recoverable=False,
            **kwargs,
        )
        self.with_context(token=repr(token))


class ProviderError(DependencyError):
    def __init__(self, token: Any, reason: Optional[str] = None, **kwargs: Any) -> None:
        suffix = f": {reason}" if reason else ""
        super().__init__(
            f"Provider error for token {token!r}{suffix}",
            code="DI_PROVIDER_ERROR",
            **kwargs,
        )
        self.with_context(token=repr(token), reason=reason)


class ScopeError(DependencyError):
    def __init__(self, token: Any, scope: str, reason: Optional[str] = None, **kwargs: Any) -> None:
        suffix = f": {reason}" if reason else ""
        super().__init__(
            f"Scope error resolving {token!r} in scope '{scope}'{suffix}",
            code="DI_SCOPE_ERROR",
            **kwargs,
        )
        self.with_context(token=repr(token), scope=scope, reason=reason)
