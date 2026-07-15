import logging
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional


class LogLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def from_string(cls, name: str) -> "LogLevel":
        try:
            return cls[name.upper()]
        except KeyError:
            valid = ", ".join(m.name for m in cls)
            raise ValueError(
                f"Unknown log level '{name}'. Valid levels: {valid}"
            ) from None


@dataclass
class LoggerConfig:
    name: str
    level: LogLevel = LogLevel.INFO
    handlers: List[logging.Handler] = field(default_factory=list)
    filters: List[logging.Filter] = field(default_factory=list)
    propagate: bool = False


class Logger:
    def __init__(self, config: LoggerConfig) -> None:
        self._config = config
        self._logger = logging.getLogger(config.name)
        self._logger.setLevel(int(config.level))
        self._logger.propagate = config.propagate
        self._logger.handlers.clear()

        for handler in config.handlers:
            self._logger.addHandler(handler)

        for flt in config.filters:
            self._logger.addFilter(flt)

        self._bound_context: Dict[str, Any] = {}

    @property
    def name(self) -> str:
        return self._logger.name

    @property
    def level(self) -> LogLevel:
        return LogLevel(self._logger.level)

    @property
    def handlers(self) -> List[logging.Handler]:
        return list(self._logger.handlers)

    @property
    def effective_level(self) -> LogLevel:
        return LogLevel(self._logger.getEffectiveLevel())
    def set_level(self, level: LogLevel) -> None:
        self._logger.setLevel(int(level))
        self._config.level = level
    def bind(self, **context: Any) -> "Logger":
        bound = Logger.__new__(Logger)
        bound._config = self._config
        bound._logger = self._logger
        bound._bound_context = {**self._bound_context, **context}
        return bound

    def _merge_extras(self, extra: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        merged = dict(self._bound_context)
        if extra:
            merged.update(extra)
        return merged
    def child(self, suffix: str) -> "Logger":
        child_name = f"{self.name}.{suffix}" if self.name else suffix
        child_config = LoggerConfig(
            name=child_name,
            level=self.level,
            handlers=[],  
            propagate=True,
        )
        return Logger(child_config)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        extra = self._merge_extras(kwargs.pop("extra", None))
        self._logger.debug(msg, *args, extra=extra or None, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        extra = self._merge_extras(kwargs.pop("extra", None))
        self._logger.info(msg, *args, extra=extra or None, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        extra = self._merge_extras(kwargs.pop("extra", None))
        self._logger.warning(msg, *args, extra=extra or None, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        extra = self._merge_extras(kwargs.pop("extra", None))
        self._logger.error(msg, *args, extra=extra or None, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        extra = self._merge_extras(kwargs.pop("extra", None))
        self._logger.critical(msg, *args, extra=extra or None, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an ERROR with exception traceback attached."""
        extra = self._merge_extras(kwargs.pop("extra", None))
        self._logger.exception(msg, *args, extra=extra or None, **kwargs)

    def log(self, level: LogLevel, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log at a specific level."""
        extra = self._merge_extras(kwargs.pop("extra", None))
        self._logger.log(int(level), msg, *args, extra=extra or None, **kwargs)
    def add_handler(self, handler: logging.Handler) -> None:
        self._logger.addHandler(handler)
        self._config.handlers.append(handler)
    def remove_handler(self, handler: logging.Handler) -> None:
        self._logger.removeHandler(handler)
        if handler in self._config.handlers:
            self._config.handlers.remove(handler)
    def add_filter(self, flt: logging.Filter) -> None:
        self._logger.addFilter(flt)
        self._config.filters.append(flt)
    def remove_filter(self, flt: logging.Filter) -> None:
        self._logger.removeFilter(flt)
        if flt in self._config.filters:
            self._config.filters.remove(flt)
    def close(self) -> None:
        for handler in self._logger.handlers[:]:
            try:
                handler.flush()
                handler.close()
            except Exception:
                pass
            self._logger.removeHandler(handler)
    def __repr__(self) -> str:
        return f"<Logger name={self.name!r} level={self.level.name}>"
