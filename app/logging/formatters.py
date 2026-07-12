import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

class ColorCodes:

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BG_RED = "\033[41m"
    BG_YELLOW = "\033[43m"

LEVEL_COLORS: Dict[int, str] = {
    logging.DEBUG: ColorCodes.CYAN,
    logging.INFO: ColorCodes.GREEN,
    logging.WARNING: ColorCodes.YELLOW,
    logging.ERROR: ColorCodes.RED,
    logging.CRITICAL: ColorCodes.BG_RED + ColorCodes.WHITE + ColorCodes.BOLD,
}
_STANDARD_RECORD_FIELDS = frozenset({
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "asctime", "taskName",
})


class BaseFormatter(logging.Formatter):
    def __init__(self, use_colors: bool = True) -> None:
        super().__init__()
        self.use_colors = use_colors

    def _color_for_level(self, levelno: int) -> str:
        return LEVEL_COLORS.get(levelno, "")

    def _format_timestamp(self, record: logging.LogRecord) -> str:
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "Z"

    def _extract_extras(self, record: logging.LogRecord) -> Dict[str, Any]:
        return {
            key: value
            for key, value in record.__dict__.items()
            if key not in _STANDARD_RECORD_FIELDS and not key.startswith("_")
        }


class ConsoleFormatter(BaseFormatter):
    def __init__(self, use_colors: bool = True) -> None:
        super().__init__(use_colors=use_colors)

    def format(self, record: logging.LogRecord) -> str:
        ts = self._format_timestamp(record)
        level = record.levelname
        module = record.module
        func = record.funcName
        line = record.lineno
        message = record.getMessage()

        if self.use_colors:
            c = self._color_for_level(record.levelno)
            r = ColorCodes.RESET
            d = ColorCodes.DIM
            b = ColorCodes.BOLD
            line_out = (
                f"{d}{ts}{r}  "
                f"{c}{b}{level:<8}{r}  "
                f"{d}{module}.{func}:{line}{r}  "
                f"{message}"
            )
        else:
            line_out = f"{ts}  {level:<8}  {module}.{func}:{line}  {message}"
        extras = self._extract_extras(record)
        if extras:
            extra_str = " ".join(f"{k}={v}" for k, v in extras.items())
            line_out += f"  {ColorCodes.DIM}[{extra_str}]{ColorCodes.RESET}" \
                if self.use_colors else f"  [{extra_str}]"
        if record.exc_info:
            line_out += "\n" + self.formatException(record.exc_info)

        return line_out


class JSONFormatter(BaseFormatter):
    def __init__(self, use_colors: bool = False, pretty: bool = False) -> None:
        super().__init__(use_colors=use_colors)
        self.pretty = pretty

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": self._format_timestamp(record),
            "level": record.levelname,
            "level_no": record.levelno,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "process_id": record.process,
            "process_name": record.processName,
            "thread_id": record.thread,
            "thread_name": record.threadName,
        }

        extras = self._extract_extras(record)
        if extras:
            payload["extra"] = extras

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        if self.pretty:
            return json.dumps(payload, indent=2, default=str, ensure_ascii=False)
        return json.dumps(payload, default=str, ensure_ascii=False)


class DetailedFileFormatter(BaseFormatter):
    def __init__(self, use_colors: bool = False) -> None:
        super().__init__(use_colors=False)

    def format(self, record: logging.LogRecord) -> str:
        ts = self._format_timestamp(record)
        parts = [
            f"[{ts}]",
            f"[{record.levelname}]",
            f"[{record.name}]",
            f"[{record.module}.{record.funcName}:{record.lineno}]",
            f"[pid:{record.process}|{record.processName}]",
            f"[tid:{record.thread}|{record.threadName}]",
            f"- {record.getMessage()}",
        ]

        extras = self._extract_extras(record)
        if extras:
            extra_str = " ".join(f"{k}={v}" for k, v in extras.items())
            parts.append(f"| {extra_str}")

        line = " ".join(parts)

        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)

        return line
