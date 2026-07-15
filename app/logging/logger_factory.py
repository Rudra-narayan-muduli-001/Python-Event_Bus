import logging
from enum import Enum
from app.logging.audit_logger import AuditLogger
from app.logging.formatters import (
    ConsoleFormatter,
    DetailedFileFormatter,
    JSONFormatter,
)
from app.logging.handlers import (
    CompositeHandler,
    ConsoleHandler,
    FileLogHandler,
    RotatingFileLogHandler,
)
from app.logging.logger import Logger, LoggerConfig, LogLevel
from app.logging.rotation import RotationConfig, RotationType


class LoggerType(Enum):
    CONSOLE = "console"
    FILE = "file"
    ROTATING = "rotating"
    COMPOSITE = "composite"
    JSON = "json"
    AUDIT = "audit"


class LoggerFactory:
    def __init__(self) -> None:
        self._loggers: dict[str, Logger] = {}
        self._audit_loggers: dict[str, AuditLogger] = {}

    def get(self, name: str) -> Logger | None:
        return self._loggers.get(name)
    def get_audit(self, name: str) -> AuditLogger | None:
        return self._audit_loggers.get(name)

    def register(self, name: str, logger: Logger) -> None:
        self._loggers[name] = logger
    def is_registered(self, name: str) -> bool:
        return name in self._loggers
    def unregister(self, name: str) -> None:
        logger = self._loggers.pop(name, None)
        if logger:
            logger.close()
    def clear(self) -> None:
        for name in list(self._loggers.keys()):
            self.unregister(name)
        self._audit_loggers.clear()

    @property
    def registered_names(self) -> list[str]:
        return list(self._loggers.keys())

    def create_console_logger(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        use_colors: bool = True,
        filters: list[logging.Filter] | None = None,
    ) -> Logger:
        if name in self._loggers:
            return self._loggers[name]

        handler = ConsoleHandler(
            formatter=ConsoleFormatter(use_colors=use_colors),
            filters=filters,
            use_colors=use_colors,
        )

        config = LoggerConfig(
            name=name,
            level=level,
            handlers=[handler],
        )
        logger = Logger(config)
        self._loggers[name] = logger
        return logger

    def create_file_logger(
        self,
        name: str,
        file_path: str,
        level: LogLevel = LogLevel.INFO,
        filters: list[logging.Filter] | None = None,
    ) -> Logger:
        if name in self._loggers:
            return self._loggers[name]

        handler = FileLogHandler(
            file_path=file_path,
            formatter=DetailedFileFormatter(),
            filters=filters,
        )

        config = LoggerConfig(
            name=name,
            level=level,
            handlers=[handler],
        )
        logger = Logger(config)
        self._loggers[name] = logger
        return logger

    def create_rotating_logger(
        self,
        name: str,
        file_path: str,
        level: LogLevel = LogLevel.INFO,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        rotation_type: RotationType = RotationType.SIZE,
        when: str = "midnight",
        interval: int = 1,
        compress: bool = True,
        filters: list[logging.Filter] | None = None,
    ) -> Logger:
        if name in self._loggers:
            return self._loggers[name]

        config = RotationConfig(
            rotation_type=rotation_type,
            max_bytes=max_bytes,
            backup_count=backup_count,
            when=when,
            interval=interval,
            compress=compress,
        )

        handler = RotatingFileLogHandler(
            file_path=file_path,
            config=config,
            formatter=DetailedFileFormatter(),
            filters=filters,
        )

        logger_config = LoggerConfig(
            name=name,
            level=level,
            handlers=[handler],
        )
        logger = Logger(logger_config)
        self._loggers[name] = logger
        return logger

    def create_composite_logger(
        self,
        name: str,
        file_path: str,
        level: LogLevel = LogLevel.INFO,
        use_colors: bool = True,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        compress: bool = True,
        filters: list[logging.Filter] | None = None,
    ) -> Logger:
        if name in self._loggers:
            return self._loggers[name]

        console_handler = ConsoleHandler(
            formatter=ConsoleFormatter(use_colors=use_colors),
            use_colors=use_colors,
        )

        rotation_config = RotationConfig(
            rotation_type=RotationType.SIZE,
            max_bytes=max_bytes,
            backup_count=backup_count,
            compress=compress,
        )

        file_handler = RotatingFileLogHandler(
            file_path=file_path,
            config=rotation_config,
            formatter=DetailedFileFormatter(),
        )

        composite = CompositeHandler(
            handlers=[console_handler, file_handler],
            filters=filters,
        )

        config = LoggerConfig(
            name=name,
            level=level,
            handlers=[composite],
        )
        logger = Logger(config)
        self._loggers[name] = logger
        return logger

    def create_json_logger(
        self,
        name: str,
        file_path: str,
        level: LogLevel = LogLevel.INFO,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        compress: bool = True,
        filters: list[logging.Filter] | None = None,
    ) -> Logger:
        if name in self._loggers:
            return self._loggers[name]

        rotation_config = RotationConfig(
            rotation_type=RotationType.SIZE,
            max_bytes=max_bytes,
            backup_count=backup_count,
            compress=compress,
        )

        handler = RotatingFileLogHandler(
            file_path=file_path,
            config=rotation_config,
            formatter=JSONFormatter(),
            filters=filters,
        )

        config = LoggerConfig(
            name=name,
            level=level,
            handlers=[handler],
        )
        logger = Logger(config)
        self._loggers[name] = logger
        return logger

    def create_audit_logger(
        self,
        name: str,
        file_path: str,
        hmac_key: bytes,
        level: LogLevel = LogLevel.INFO,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 10,
        compress: bool = True,
    ) -> AuditLogger:
        if name in self._audit_loggers:
            return self._audit_loggers[name]

        audit = AuditLogger(
            name=name,
            file_path=file_path,
            hmac_key=hmac_key,
            level=level,
            max_bytes=max_bytes,
            backup_count=backup_count,
            compress=compress,
        )
        self._audit_loggers[name] = audit
        return audit

    def create_logger(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        handlers: list[logging.Handler] | None = None,
        filters: list[logging.Filter] | None = None,
        propagate: bool = False,
    ) -> Logger:
        if name in self._loggers:
            return self._loggers[name]

        config = LoggerConfig(
            name=name,
            level=level,
            handlers=handlers or [],
            filters=filters or [],
            propagate=propagate,
        )
        logger = Logger(config)
        self._loggers[name] = logger
        return logger

    def shutdown(self) -> None:
        for name in list(self._loggers.keys()):
            self.unregister(name)

        for _name, audit in list(self._audit_loggers.items()):
            audit.close()
        self._audit_loggers.clear()
