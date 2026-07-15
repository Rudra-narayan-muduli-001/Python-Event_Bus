from __future__ import annotations
from typing import Type
from app.core.exceptions.base import (
    AIOSError,
    ErrorCategory,
    ErrorSeverity,
)
from app.core.exceptions.configuration import (
    ConfigFileNotFoundError,
    ConfigMergeError,
    ConfigParseError,
    ConfigValidationError,
    ConfigurationError,
    EnvironmentVariableError,
    InvalidConfigValueError,
    MissingConfigKeyError,
)
from app.core.exceptions.dependency import (
    CircularDependencyError,
    DependencyError,
    DependencyNotFoundError,
    DependencyResolutionError,
    DuplicateRegistrationError,
    ProviderError,
    ScopeError,
)
from app.core.exceptions.database import (
    BackupError,
    DatabaseError,
    DbConnectionError,
    EncryptionKeyError,
    IntegrityError,
    KnowledgeGraphError,
    MigrationError,
    QueryError,
    TransactionError,
    VectorStoreError,
)
from app.core.exceptions.state import (
    InvalidStateError,
    InvalidStateTransitionError,
    StateError,
    StateLockError,
    StatePersistenceError,
    StateSnapshotError,
    StateValidationError,
)
from app.core.exceptions.event import (
    EventDispatchError,
    EventError,
    EventHandlerError,
    EventPublishError,
    EventSerializationError,
    EventSubscriptionError,
    UnknownEventTypeError,
)
from app.core.exceptions.queue import (
    InvalidPriorityError,
    QueueClosedError,
    QueueEmptyError,
    QueueError,
    QueueFullError,
    QueueInterruptedError,
    QueueOverflowError,
    QueueTimeoutError,
)
from app.core.exceptions.security import (
    AuditIntegrityError,
    AuthenticationError,
    AuthorizationError,
    EncryptionError,
    FirewallBlockedError,
    PermissionDeniedError,
    PromptInjectionError,
    RiskThresholdExceededError,
    SandboxViolationError,
    SecurityError,
    SpeakerVerificationError,
)
from app.core.exceptions.validation import (
    ConstraintViolationError,
    MissingFieldError,
    ParameterValidationError,
    SchemaValidationError,
    ToolValidationError,
    TypeCoercionError,
    ValidationError,
)
from app.core.exceptions.startup import (
    BootstrapError,
    FeatureGroupInitError,
    InitializationError,
    PhaseInitializationError,
    ServiceStartupError,
    ShutdownError,
    StartupError,
    StartupTimeoutError,
)
from app.core.exceptions.runtime import (
    ExternalServiceError,
    ModelInferenceError,
    NotSupportedError,
    OperationError,
    RecoveryError,
    ResourceExhaustedError,
    RetryExhaustedError,
    RuntimeError_,
    TimeoutError_,
    ToolExecutionError,
)

_CATEGORY_BASE: dict[ErrorCategory, Type[AIOSError]] = {
    ErrorCategory.CONFIGURATION: ConfigurationError,
    ErrorCategory.DEPENDENCY: DependencyError,
    ErrorCategory.DATABASE: DatabaseError,
    ErrorCategory.STATE: StateError,
    ErrorCategory.EVENT: EventError,
    ErrorCategory.QUEUE: QueueError,
    ErrorCategory.SECURITY: SecurityError,
    ErrorCategory.VALIDATION: ValidationError,
    ErrorCategory.STARTUP: StartupError,
    ErrorCategory.RUNTIME: RuntimeError_,
    ErrorCategory.UNKNOWN: AIOSError,
}


def get_exception_for_category(category: ErrorCategory) -> Type[AIOSError]:
    return _CATEGORY_BASE.get(category, AIOSError)


def is_fatal(exc: BaseException) -> bool:
    return isinstance(exc, AIOSError) and exc.is_fatal()


def wrap_exception(
    exc: BaseException,
    *,
    category: ErrorCategory = ErrorCategory.RUNTIME,
    message: str | None = None,
) -> AIOSError:
    if isinstance(exc, AIOSError):
        return exc
    base_cls = get_exception_for_category(category)
    return base_cls(
        message or f"Unhandled {type(exc).__name__}: {exc}",
        cause=exc,
    )


__all__ = [
    "AIOSError",
    "ErrorCategory",
    "ErrorSeverity",
    "ConfigurationError",
    "ConfigFileNotFoundError",
    "ConfigParseError",
    "ConfigValidationError",
    "MissingConfigKeyError",
    "InvalidConfigValueError",
    "EnvironmentVariableError",
    "ConfigMergeError",
    "DependencyError",
    "DependencyNotFoundError",
    "DependencyResolutionError",
    "CircularDependencyError",
    "DuplicateRegistrationError",
    "ProviderError",
    "ScopeError",
    "DatabaseError",
    "DbConnectionError",
    "TransactionError",
    "MigrationError",
    "QueryError",
    "IntegrityError",
    "BackupError",
    "EncryptionKeyError",
    "VectorStoreError",
    "KnowledgeGraphError",
    "StateError",
    "InvalidStateTransitionError",
    "InvalidStateError",
    "StatePersistenceError",
    "StateSnapshotError",
    "StateValidationError",
    "StateLockError",
    "EventError",
    "EventPublishError",
    "EventSubscriptionError",
    "EventHandlerError",
    "EventSerializationError",
    "UnknownEventTypeError",
    "EventDispatchError",
    "QueueError",
    "QueueFullError",
    "QueueEmptyError",
    "QueueTimeoutError",
    "QueueClosedError",
    "InvalidPriorityError",
    "QueueInterruptedError",
    "QueueOverflowError",
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
    "ValidationError",
    "SchemaValidationError",
    "ParameterValidationError",
    "TypeCoercionError",
    "ConstraintViolationError",
    "MissingFieldError",
    "ToolValidationError",
    "StartupError",
    "InitializationError",
    "BootstrapError",
    "ServiceStartupError",
    "FeatureGroupInitError",
    "PhaseInitializationError",
    "StartupTimeoutError",
    "ShutdownError",
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
    "get_exception_for_category",
    "is_fatal",
    "wrap_exception",
]
