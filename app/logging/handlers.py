import logging
import sys
from pathlib import Path
from typing import List, Optional
from app.logging.formatters import BaseFormatter, ConsoleFormatter, DetailedFileFormatter
from app.logging.rotation import RotationConfig, create_rotating_handler

class ConsoleHandler(logging.StreamHandler):
    def __init__(
        self,
        formatter: Optional[logging.Formatter] = None,
        filters: Optional[List[logging.Filter]] = None,
        use_colors: bool = True,
    ) -> None:
        super().__init__(stream=sys.stdout)
        self._use_colors = use_colors
        self._stderr = sys.stderr

        if formatter is None:
            formatter = ConsoleFormatter(use_colors=use_colors)
        self.setFormatter(formatter)

        if filters:
            for f in filters:
                self.addFilter(f)

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno >= logging.WARNING:
            self.stream = self._stderr
        else:
            self.stream = sys.stdout
        super().emit(record)


class FileLogHandler(logging.FileHandler):
    def __init__(
        self,
        file_path: str,
        formatter: Optional[logging.Formatter] = None,
        filters: Optional[List[logging.Filter]] = None,
        encoding: str = "utf-8",
        delay: bool = True,
    ) -> None:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        super().__init__(
            filename=file_path,
            mode="a",
            encoding=encoding,
            delay=delay,
        )

        if formatter is None:
            formatter = DetailedFileFormatter()
        self.setFormatter(formatter)

        if filters:
            for f in filters:
                self.addFilter(f)


class RotatingFileLogHandler(logging.Handler):
    def __init__(
        self,
        file_path: str,
        config: Optional[RotationConfig] = None,
        formatter: Optional[logging.Formatter] = None,
        filters: Optional[List[logging.Filter]] = None,
    ) -> None:
        super().__init__()
        if config is None:
            config = RotationConfig()
        if formatter is None:
            formatter = DetailedFileFormatter()

        self._delegate = create_rotating_handler(
            file_path=file_path,
            config=config,
            formatter=formatter,
        )

        if filters:
            for f in filters:
                self.addFilter(f)

    def setFormatter(self, fmt: logging.Formatter) -> None:
        super().setFormatter(fmt)
        self._delegate.setFormatter(fmt)

    def emit(self, record: logging.LogRecord) -> None:
        self._delegate.emit(record)

    def close(self) -> None:
        self._delegate.close()
        super().close()

    def flush(self) -> None:
        self._delegate.flush()


class CompositeHandler(logging.Handler):
    def __init__(
        self,
        handlers: List[logging.Handler],
        filters: Optional[List[logging.Filter]] = None,
    ) -> None:
        super().__init__()
        self._handlers = list(handlers)

        if filters:
            for f in filters:
                self.addFilter(f)

    @property
    def handlers(self) -> List[logging.Handler]:
        return list(self._handlers)

    def add_handler(self, handler: logging.Handler) -> None:
        self._handlers.append(handler)

    def remove_handler(self, handler: logging.Handler) -> None:
        self._handlers.remove(handler)

    def setFormatter(self, fmt: logging.Formatter) -> None:
        super().setFormatter(fmt)
        for h in self._handlers:
            h.setFormatter(fmt)

    def emit(self, record: logging.LogRecord) -> None:
        for handler in self._handlers:
            try:
                handler.handle(record)
            except Exception:
                self.handleError(record)

    def close(self) -> None:
        for h in self._handlers:
            try:
                h.close()
            except Exception:
                pass
        super().close()

    def flush(self) -> None:
        for h in self._handlers:
            try:
                h.flush()
            except Exception:
                pass
