# app/core/exceptions/security.py
from __future__ import annotations
from typing import Any, Optional
from app.core.exceptions.base import AIOSError, ErrorCategory, ErrorSeverity

__all__ = [
    "SecurityError",
    "AuthenticationError",
    "AuthorizationError",
    "PermissionDeniedError",
    "SpeakerVerificationError",
    "RiskThresholdExceededError",
    "FirewallBlockedError",
    "PromptInjectionError",
    "SandboxViolationError",
    "EncryptionError",
    "AuditIntegrityError",
]


class SecurityError(AIOSError):
    default_category = ErrorCategory.SECURITY
    default_severity = ErrorSeverity.CRITICAL

    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("recoverable", False)
        super().__init__(message, **kwargs)


class AuthenticationError(SecurityError):
    def __init__(self, reason: str = "authentication failed", **kwargs: Any) -> None:
        super().__init__(
            f"Authentication failed: {reason}",
            code="SEC_AUTHENTICATION_FAILED",
            **kwargs,
        )
        self.with_context(reason=reason)


class AuthorizationError(SecurityError):
    def __init__(self, reason: str = "authorization failed", **kwargs: Any) -> None:
        super().__init__(
            f"Authorization failed: {reason}",
            code="SEC_AUTHORIZATION_FAILED",
            **kwargs,
        )
        self.with_context(reason=reason)


class PermissionDeniedError(SecurityError):
    def __init__(self, action: str, role: Optional[str] = None, **kwargs: Any) -> None:
        who = f" for role '{role}'" if role else ""
        super().__init__(
            f"Permission denied: '{action}'{who}",
            code="SEC_PERMISSION_DENIED",
            **kwargs,
        )
        self.with_context(action=action, role=role)


class SpeakerVerificationError(SecurityError):
    def __init__(self, reason: str = "voice identity mismatch", **kwargs: Any) -> None:
        super().__init__(
            f"Speaker verification failed: {reason}",
            code="SEC_SPEAKER_VERIFICATION_FAILED",
            **kwargs,
        )
        self.with_context(reason=reason)


class RiskThresholdExceededError(SecurityError):
    def __init__(self, risk_level: str, action: Optional[str] = None, **kwargs: Any) -> None:
        what = f" for action '{action}'" if action else ""
        super().__init__(
            f"Risk threshold exceeded (level={risk_level}){what}",
            code="SEC_RISK_THRESHOLD_EXCEEDED",
            **kwargs,
        )
        self.with_context(risk_level=risk_level, action=action)


class FirewallBlockedError(SecurityError):
    def __init__(self, reason_category: str, **kwargs: Any) -> None:
        super().__init__(
            f"Request blocked by AI firewall (category={reason_category})",
            code="SEC_FIREWALL_BLOCKED",
            **kwargs,
        )
        self.with_context(reason_category=reason_category)


class PromptInjectionError(SecurityError):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            "Prompt injection attempt detected and blocked",
            code="SEC_PROMPT_INJECTION",
            **kwargs,
        )


class SandboxViolationError(SecurityError):
    def __init__(self, violation: str, **kwargs: Any) -> None:
        super().__init__(
            f"Sandbox violation: {violation}",
            code="SEC_SANDBOX_VIOLATION",
            severity=ErrorSeverity.FATAL,
            **kwargs,
        )
        self.with_context(violation=violation)


class EncryptionError(SecurityError):
    def __init__(self, operation: str = "encryption", cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Cryptographic operation '{operation}' failed",
            code="SEC_ENCRYPTION_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(operation=operation)


class AuditIntegrityError(SecurityError):
    def __init__(self, reason: str = "audit chain verification failed", **kwargs: Any) -> None:
        super().__init__(
            f"Audit integrity failure: {reason}",
            code="SEC_AUDIT_INTEGRITY_ERROR",
            severity=ErrorSeverity.FATAL,
            **kwargs,
        )
        self.with_context(reason=reason)
