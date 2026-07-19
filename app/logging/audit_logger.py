import hashlib
import hmac
import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.logging.formatters import BaseFormatter
from app.logging.logger import LogLevel
from app.logging.rotation import RotationConfig, RotationType, create_rotating_handler

@dataclass
class AuditEntry:
    seq: int
    timestamp: str
    level: str
    logger: str
    event: str
    user: str = "system"
    action: str = ""
    result: str = ""
    risk_level: str = "low"
    details: Dict[str, Any] = field(default_factory=dict)
    prev_hmac: str = "0" * 64
    hmac: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seq": self.seq,
            "timestamp": self.timestamp,
            "level": self.level,
            "logger": self.logger,
            "event": self.event,
            "user": self.user,
            "action": self.action,
            "result": self.result,
            "risk_level": self.risk_level,
            "details": self.details,
            "prev_hmac": self.prev_hmac,
            "hmac": self.hmac,
        }

    def to_json_line(self) -> str:
        return json.dumps(self.to_dict(), default=str, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEntry":
        return cls(
            seq=data.get("seq", 0),
            timestamp=data.get("timestamp", ""),
            level=data.get("level", "INFO"),
            logger=data.get("logger", ""),
            event=data.get("event", ""),
            user=data.get("user", "system"),
            action=data.get("action", ""),
            result=data.get("result", ""),
            risk_level=data.get("risk_level", "low"),
            details=data.get("details", {}),
            prev_hmac=data.get("prev_hmac", "0" * 64),
            hmac=data.get("hmac", ""),
        )


@dataclass
class VerificationResult:
    is_valid: bool = True
    total_entries: int = 0
    verified_entries: int = 0
    broken_at: Optional[int] = None
    broken_reason: str = ""
    errors: List[str] = field(default_factory=list)

class AuditFormatter(BaseFormatter):
    def __init__(self, use_colors: bool = False) -> None:
        super().__init__(use_colors=False)

    def format(self, record: logging.LogRecord) -> str:
        entry: Optional[AuditEntry] = getattr(record, "audit_entry", None)
        if entry is not None:
            return entry.to_json_line()
        payload: dict[str, Any] = {
            "timestamp": self._format_timestamp(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extras = self._extract_extras(record)
        if extras:
            payload["details"] = extras
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)

class AuditLogger:
    _GENESIS_HMAC = "0" * 64

    def __init__(
        self,
        name: str,
        file_path: str,
        hmac_key: bytes,
        level: LogLevel = LogLevel.INFO,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 10,
        compress: bool = True,
    ) -> None:
        if not hmac_key or len(hmac_key) < 16:
            raise ValueError(
                "hmac_key must be at least 16 bytes for adequate security"
            )

        self._name = name
        self._file_path = file_path
        self._hmac_key = hmac_key
        self._level = int(level)
        self._closed = False
        self._lock = threading.Lock()
        self._seq: int = 0
        self._last_hmac: str = self._GENESIS_HMAC
        self._init_chain_from_existing()
        self._logger = logging.getLogger(name)
        self._logger.setLevel(self._level)
        self._logger.propagate = False
        self._logger.handlers.clear()

        rotation_config = RotationConfig(
            rotation_type=RotationType.SIZE,
            max_bytes=max_bytes,
            backup_count=backup_count,
            compress=compress,
        )

        handler = create_rotating_handler(
            file_path=file_path,
            config=rotation_config,
            formatter=AuditFormatter(),
        )
        self._logger.addHandler(handler)

    def _init_chain_from_existing(self) -> None:
        path = Path(self._file_path)
        if not path.exists() or path.stat().st_size == 0:
            return

        last_seq = 0
        last_hmac = self._GENESIS_HMAC

        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        last_seq = data.get("seq", last_seq)
                        last_hmac = data.get("hmac", last_hmac)
                    except (json.JSONDecodeError, KeyError):
                        # Skip malformed lines
                        continue
        except OSError:
            pass

        self._seq = last_seq
        self._last_hmac = last_hmac

    def _compute_hmac(self, entry: AuditEntry) -> str:
        return self._compute_hmac_static(entry, self._hmac_key)

    def log(
        self,
        event: str,
        user: str = "system",
        action: str = "",
        result: str = "",
        risk_level: str = "low",
        details: Optional[Dict[str, Any]] = None,
        level: LogLevel = LogLevel.INFO,
    ) -> AuditEntry:
        if self._closed:
            raise RuntimeError("AuditLogger is closed")

        with self._lock:
            self._seq += 1
            now = datetime.now(timezone.utc)
            timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

            entry = AuditEntry(
                seq=self._seq,
                timestamp=timestamp,
                level=level.name,
                logger=self._name,
                event=event,
                user=user,
                action=action,
                result=result,
                risk_level=risk_level,
                details=details or {},
                prev_hmac=self._last_hmac,
            )
            entry.hmac = self._compute_hmac(entry)
            self._last_hmac = entry.hmac
            self._logger.info(
                entry.to_json_line(),
                extra={"audit_entry": entry},
            )

            return entry

    def auth_success(
        self,
        user: str,
        method: str = "",
        confidence: float = 0.0,
        **extra: Any,
    ) -> AuditEntry:
        details = {"method": method, "confidence": confidence, **extra}
        return self.log(
            event="AUTH_SUCCESS",
            user=user,
            action="authenticate",
            result="success",
            risk_level="low",
            details=details,
        )

    def auth_failure(
        self,
        user: str,
        method: str = "",
        reason: str = "",
        **extra: Any,
    ) -> AuditEntry:
        details = {"method": method, "reason": reason, **extra}
        return self.log(
            event="AUTH_FAILURE",
            user=user,
            action="authenticate",
            result="failure",
            risk_level="medium",
            details=details,
            level=LogLevel.WARNING,
        )

    def permission_denied(
        self,
        user: str,
        resource: str = "",
        permission: str = "",
        **extra: Any,
    ) -> AuditEntry:
        details = {
            "resource": resource,
            "permission": permission,
            **extra,
        }
        return self.log(
            event="PERMISSION_DENIED",
            user=user,
            action="access_resource",
            result="denied",
            risk_level="medium",
            details=details,
            level=LogLevel.WARNING,
        )

    def risk_escalation(
        self,
        user: str,
        command: str = "",
        risk_level: str = "high",
        **extra: Any,
    ) -> AuditEntry:
        details = {"command": command, **extra}
        return self.log(
            event="RISK_ESCALATION",
            user=user,
            action="evaluate_risk",
            result="escalated",
            risk_level=risk_level,
            details=details,
            level=LogLevel.WARNING,
        )

    def prompt_blocked(
        self,
        user: str,
        reason: str = "",
        **extra: Any,
    ) -> AuditEntry:
        details = {"reason": reason, **extra}
        return self.log(
            event="PROMPT_BLOCKED",
            user=user,
            action="firewall_check",
            result="blocked",
            risk_level="high",
            details=details,
            level=LogLevel.WARNING,
        )

    def tool_execution(
        self,
        user: str,
        tool: str = "",
        status: str = "",
        execution_time: float = 0.0,
        **extra: Any,
    ) -> AuditEntry:
        details = {
            "tool": tool,
            "status": status,
            "execution_time": execution_time,
            **extra,
        }
        return self.log(
            event="TOOL_EXECUTED",
            user=user,
            action="execute_tool",
            result=status,
            risk_level="low",
            details=details,
        )

    def rollback(
        self,
        user: str,
        action_id: str = "",
        reason: str = "",
        **extra: Any,
    ) -> AuditEntry:
        details = {"action_id": action_id, "reason": reason, **extra}
        return self.log(
            event="ROLLBACK_EXECUTED",
            user=user,
            action="rollback",
            result="success",
            risk_level="medium",
            details=details,
        )

    @staticmethod
    def verify_log_file(
        file_path: str,
        hmac_key: bytes,
    ) -> VerificationResult:
        result = VerificationResult()
        path = Path(file_path)

        if not path.exists():
            result.is_valid = False
            result.broken_reason = f"File not found: {file_path}"
            return result

        expected_prev = AuditLogger._GENESIS_HMAC
        expected_seq = 0

        try:
            with open(path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    result.total_entries += 1

                    failure = AuditLogger._verify_entry(
                        line, line_num, expected_seq, expected_prev, hmac_key
                    )
                    if failure is not None:
                        result.is_valid = False
                        result.broken_at = failure["at"]
                        result.broken_reason = failure["reason"]
                        result.errors.append(failure["error"])
                        return result

                    data = json.loads(line)
                    expected_prev = data.get("hmac", expected_prev)
                    expected_seq += 1
                    result.verified_entries += 1

        except OSError as e:
            result.is_valid = False
            result.broken_reason = f"File read error: {e}"
            return result

        return result

    @staticmethod
    def _verify_entry(
        line: str,
        line_num: int,
        expected_seq: int,
        expected_prev: str,
        hmac_key: bytes,
    ) -> Optional[dict]:
        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            return {
                "at": expected_seq + 1,
                "reason": f"Line {line_num}: JSON parse error: {e}",
                "error": f"Line {line_num}: malformed JSON",
            }

        entry = AuditEntry.from_dict(data)
        if entry.seq != expected_seq + 1:
            return {
                "at": entry.seq,
                "reason": f"Sequence gap: expected {expected_seq + 1}, got {entry.seq}",
                "error": f"Entry seq={entry.seq}: sequence discontinuity",
            }

        if entry.prev_hmac != expected_prev:
            return {
                "at": entry.seq,
                "reason": f"Chain broken at seq={entry.seq}: prev_hmac mismatch "
                          f"(expected {expected_prev[:16]}..., got {entry.prev_hmac[:16]}...)",
                "error": f"Entry seq={entry.seq}: prev_hmac does not match previous entry's hmac",
            }

        recomputed = AuditLogger._compute_hmac_static(entry, hmac_key)
        if not hmac.compare_digest(recomputed, entry.hmac):
            return {
                "at": entry.seq,
                "reason": f"HMAC verification failed at seq={entry.seq}: entry may have been modified",
                "error": f"Entry seq={entry.seq}: HMAC mismatch "
                         f"(expected {recomputed[:16]}..., got {entry.hmac[:16]}...)",
            }

        return None

    @staticmethod
    def _compute_hmac_static(entry: AuditEntry, hmac_key: bytes) -> str:
        payload_dict = {
            "seq": entry.seq,
            "timestamp": entry.timestamp,
            "level": entry.level,
            "logger": entry.logger,
            "event": entry.event,
            "user": entry.user,
            "action": entry.action,
            "result": entry.result,
            "risk_level": entry.risk_level,
            "details": entry.details,
            "prev_hmac": entry.prev_hmac,
        }
        payload = json.dumps(
            payload_dict,
            sort_keys=True,
            default=str,
            ensure_ascii=False,
        )
        return hmac.new(
            hmac_key,
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @property
    def name(self) -> str:
        return self._name

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def sequence(self) -> int:
        with self._lock:
            return self._seq

    @property
    def last_hmac(self) -> str:
        with self._lock:
            return self._last_hmac

    @property
    def is_closed(self) -> bool:
        return self._closed

    def flush(self) -> None:
        for handler in self._logger.handlers:
            try:
                handler.flush()
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to flush audit handler %s", handler
                )

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        for handler in self._logger.handlers[:]:
            try:
                handler.flush()
                handler.close()
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to close audit handler %s", handler
                )
            self._logger.removeHandler(handler)

    def __repr__(self) -> str:
        return (
            f"<AuditLogger name={self._name!r} "
            f"seq={self._seq} closed={self._closed}>"
        )
