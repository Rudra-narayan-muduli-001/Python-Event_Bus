from __future__ import annotations
from typing import Any, Iterable, Mapping, Optional
from app.core.exceptions.base import AIOSError, ErrorCategory, ErrorSeverity
__all__ = [
    "ConfigurationError",
    "ConfigFileNotFoundError",
    "ConfigParseError",
    "ConfigValidationError",
    "MissingConfigKeyError",
    "InvalidConfigValueError",
    "EnvironmentVariableError",
    "ConfigMergeError",
]


class ConfigurationError(AIOSError):
    default_category = ErrorCategory.CONFIGURATION
    default_severity = ErrorSeverity.CRITICAL


class ConfigFileNotFoundError(ConfigurationError):
    def __init__(self, path: Any, **kwargs: Any) -> None:
        super().__init__(
            f"Configuration file not found: {path}",
            code="CONFIG_FILE_NOT_FOUND",
            **kwargs,
        )
        self.with_context(path=str(path))


class ConfigParseError(ConfigurationError):
    def __init__(self, path: Any, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Failed to parse configuration file: {path}",
            code="CONFIG_PARSE_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(path=str(path))


class ConfigValidationError(ConfigurationError):

    default_severity = ErrorSeverity.FATAL

    def __init__(self, errors: Iterable[str], **kwargs: Any) -> None:
        error_list = list(errors)
        joined = "; ".join(error_list) if error_list else "unknown validation error"
        super().__init__(
            f"Configuration validation failed: {joined}",
            code="CONFIG_VALIDATION_ERROR",
            recoverable=False,
            **kwargs,
        )
        self.errors = error_list
        self.with_context(errors=error_list)


class MissingConfigKeyError(ConfigurationError):
    def __init__(self, key: str, **kwargs: Any) -> None:
        super().__init__(
            f"Required configuration key is missing: '{key}'",
            code="CONFIG_MISSING_KEY",
            **kwargs,
        )
        self.with_context(key=key)


class InvalidConfigValueError(ConfigurationError):
    def __init__(
        self,
        key: str,
        value: Any,
        *,
        expected: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        detail = f" (expected {expected})" if expected else ""
        super().__init__(
            f"Invalid configuration value for '{key}': {value!r}{detail}",
            code="CONFIG_INVALID_VALUE",
            **kwargs,
        )
        self.with_context(key=key, value=repr(value), expected=expected)


class EnvironmentVariableError(ConfigurationError):

    def __init__(self, variable: str, reason: Optional[str] = None, **kwargs: Any) -> None:
        suffix = f": {reason}" if reason else ""
        super().__init__(
            f"Environment variable error for '{variable}'{suffix}",
            code="CONFIG_ENV_VAR_ERROR",
            **kwargs,
        )
        self.with_context(variable=variable, reason=reason)


class ConfigMergeError(ConfigurationError):
    def __init__(self, message: str, *, layers: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(message, code="CONFIG_MERGE_ERROR", **kwargs)
        if layers:
            self.with_context(layers=dict(layers))
