from __future__ import annotations
from typing import Any, Iterable, Optional
from app.core.exceptions.base import AIOSError, ErrorCategory, ErrorSeverity

__all__ = [
    "ValidationError",
    "SchemaValidationError",
    "ParameterValidationError",
    "TypeCoercionError",
    "ConstraintViolationError",
    "MissingFieldError",
    "ToolValidationError",
]


class ValidationError(AIOSError):
    default_category = ErrorCategory.VALIDATION
    default_severity = ErrorSeverity.WARNING


class SchemaValidationError(ValidationError):
    def __init__(self, errors: Iterable[str], *, schema: Optional[str] = None, **kwargs: Any) -> None:
        error_list = list(errors)
        joined = "; ".join(error_list) if error_list else "unknown validation error"
        where = f" against schema '{schema}'" if schema else ""
        super().__init__(
            f"Schema validation failed{where}: {joined}",
            code="VALIDATION_SCHEMA_ERROR",
            **kwargs,
        )
        self.errors = error_list
        self.with_context(errors=error_list, schema=schema)


class ParameterValidationError(ValidationError):
    def __init__(
        self,
        parameter: str,
        value: Any,
        *,
        expected: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        detail = f" (expected {expected})" if expected else ""
        super().__init__(
            f"Invalid value for parameter '{parameter}'{detail}",
            code="VALIDATION_PARAMETER_ERROR",
            **kwargs,
        )
        self.with_context(parameter=parameter, value=repr(value)[:200], expected=expected)


class TypeCoercionError(ValidationError):
    def __init__(self, field: str, value: Any, target_type: str, **kwargs: Any) -> None:
        super().__init__(
            f"Cannot coerce field '{field}' to {target_type}",
            code="VALIDATION_TYPE_COERCION_ERROR",
            **kwargs,
        )
        self.with_context(field=field, value=repr(value)[:200], target_type=target_type)


class ConstraintViolationError(ValidationError):
    def __init__(self, field: str, constraint: str, **kwargs: Any) -> None:
        super().__init__(
            f"Constraint violated on '{field}': {constraint}",
            code="VALIDATION_CONSTRAINT_ERROR",
            **kwargs,
        )
        self.with_context(field=field, constraint=constraint)


class MissingFieldError(ValidationError):
    def __init__(self, field: str, **kwargs: Any) -> None:
        super().__init__(
            f"Required field is missing: '{field}'",
            code="VALIDATION_MISSING_FIELD",
            **kwargs,
        )
        self.with_context(field=field)


class ToolValidationError(ValidationError):
    def __init__(self, tool: str, reason: str, **kwargs: Any) -> None:
        super().__init__(
            f"Tool '{tool}' request validation failed: {reason}",
            code="VALIDATION_TOOL_ERROR",
            severity=ErrorSeverity.ERROR,
            **kwargs,
        )
        self.with_context(tool=tool, reason=reason)
