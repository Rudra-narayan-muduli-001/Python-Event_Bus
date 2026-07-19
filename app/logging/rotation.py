import gzip
import logging
import os
import shutil
from dataclasses import dataclass, field
from enum import Enum
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Callable, List, Optional


class RotationType(Enum):
    SIZE = "size"
    TIME = "time"


@dataclass
class RotationConfig:
    rotation_type: RotationType = RotationType.SIZE
    max_bytes: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    when: str = "midnight"
    interval: int = 1
    compress: bool = True
    encoding: str = "utf-8"

    def __post_init__(self) -> None:
        if self.backup_count < 0:
            raise ValueError("backup_count must be >= 0")
        if self.rotation_type == RotationType.SIZE and self.max_bytes <= 0:
            raise ValueError("max_bytes must be > 0 for size-based rotation")
        if self.rotation_type == RotationType.TIME and self.interval <= 0:
            raise ValueError("interval must be > 0 for time-based rotation")


class _CompressingRotatingFileHandler(RotatingFileHandler):
    compress: bool = True

    def rotate(self, source: str, dest: str) -> None:
        _rotate_with_compression(source, dest, self.compress, super().rotate)


class _CompressingTimedRotatingFileHandler(TimedRotatingFileHandler):
    compress: bool = True

    def rotate(self, source: str, dest: str) -> None:
        _rotate_with_compression(source, dest, self.compress, super().rotate)


def _rotate_with_compression(
    source: str, dest: str, compress: bool, fallback_rotate: Callable[[str, str], None]
) -> None:
    if compress and dest and not dest.endswith(".gz"):
        dest_gz = dest + ".gz"
        with open(source, "rb") as f_in:
            with gzip.open(dest_gz, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(source)
    else:
        fallback_rotate(source, dest)


def create_rotating_handler(
    file_path: str,
    config: RotationConfig,
    formatter: Optional[logging.Formatter] = None,
) -> logging.Handler:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    handler: logging.Handler
    if config.rotation_type == RotationType.SIZE:
        handler = _CompressingRotatingFileHandler(
            filename=file_path,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count,
            encoding=config.encoding,
            delay=True,
        )
    else:
        handler = _CompressingTimedRotatingFileHandler(
            filename=file_path,
            when=config.when,
            interval=config.interval,
            backupCount=config.backup_count,
            encoding=config.encoding,
            delay=True,
            utc=True,
        )

    setattr(handler, "compress", config.compress)

    if formatter is not None:
        handler.setFormatter(formatter)

    return handler
