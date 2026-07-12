from __future__ import annotations
import enum
import traceback
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

__all__ = [
    "ErrorSeverity",
    "ErrorCategory",
    "AIOSError",
]


class ErrorSeverity(str, enum.Enum):
    DEBUG = "debug"
    INFO = "info"              
    WARNING = "warning"        
    ERROR = "error"            
    CRITICAL = "critical"     
    FATAL = "fatal"          

class ErrorCategory(str, enum.Enum):

    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    DATABASE = "database"
    STATE = "state"
    EVENT = "event"
    QUEUE = "queue"
    SECURITY = "security"
    VALIDATION = "validation"
    STARTUP = "startup"
    RUNTIME = "runtime"
    UNKNOWN = "unknown"


class AIOSError(Exception):
    default_severity: ErrorSeverity = ErrorSeverity.ERROR
    default_category: ErrorCategory = ErrorCategory.UNKNOWN

    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None,
        context: Optional[Mapping[str, Any]] = None,
        cause: Optional[BaseException] = None,
        recoverable: bool = True,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        self.severity = severity or self.default_severity
        self.category = category or self.default_category
        self.context: dict[str, Any] = dict(context) if context else {}
        self.cause = cause
        self.recoverable = recoverable
        self.timestamp = datetime.now(timezone.utc)

        if cause is not None:
            self.__cause__ = cause

    def with_context(self, **kwargs: Any) -> "AIOSError":
        self.context.update(kwargs)
        return self

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "type": self.__class__.__name__,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
        }
        if self.cause is not None:
            payload["cause"] = {
                "type": type(self.cause).__name__,
                "message": str(self.cause),
            }
        return payload

    def format_traceback(self) -> str:
        return "".join(
            traceback.format_exception(type(self), self, self.__traceback__)
        )

    def is_fatal(self) -> bool:
        return self.severity is ErrorSeverity.FATAL

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def __repr__(self) -> str:  
        return (
            f"{self.__class__.__name__}(code={self.code!r}, "
            f"severity={self.severity.value!r}, category={self.category.value!r}, "
            f"message={self.message!r})"
        )
