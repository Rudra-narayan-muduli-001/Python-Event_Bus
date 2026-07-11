from __future__ import annotations

import threading
from copy import deepcopy
from typing import Any, Callable, Optional

from app.core.configs.config_loader import ConfigLoadError, load_merged_config
from app.core.configs.config_validator import ConfigValidationError, validate_config
from app.core.configs.environment import AppEnvironment, get_environment
from app.core.configs.paths import ProjectPaths, get_paths

__all__ = [
    "ConfigManager",
    "ConfigError",
    "get_config",
    "get_config_manager",
]

_MISSING = object()

ChangeListener = Callable[[dict[str, Any], dict[str, Any]], None]


class ConfigError(RuntimeError):
    """Umbrella error for configuration failures surfaced by the manager."""


class ConfigManager:

    _instance: Optional["ConfigManager"] = None
    _singleton_lock: threading.Lock = threading.Lock()

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._config: dict[str, Any] = {}
        self._paths: Optional[ProjectPaths] = None
        self._environment: AppEnvironment = get_environment()
        self._loaded: bool = False
        self._listeners: list[ChangeListener] = []


    @classmethod
    def instance(cls) -> "ConfigManager":
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Drop the singleton (test-only hook)."""
        with cls._singleton_lock:
            cls._instance = None

    def bootstrap(
        self,
        paths: Optional[ProjectPaths] = None,
        environment: Optional[AppEnvironment] = None,
        *,
        create_directories: bool = True,
        strict: Optional[bool] = None,
    ) -> "ConfigManager":
        with self._lock:
            self._paths = paths or get_paths()
            self._environment = environment or get_environment()

            if create_directories:
                self._paths.ensure_directories()

            snapshot = self._build_snapshot(strict=strict)
            old = self._config
            self._config = snapshot
            self._loaded = True
            self._notify(old, snapshot)
            return self

    def reload(self, *, strict: Optional[bool] = None) -> dict[str, Any]:
       
        with self._lock:
            if self._paths is None:
                self._paths = get_paths()
            new_snapshot = self._build_snapshot(strict=strict)
            old = self._config
            self._config = new_snapshot
            self._loaded = True
            self._notify(old, new_snapshot)
            return deepcopy(new_snapshot)

    def _build_snapshot(self, *, strict: Optional[bool]) -> dict[str, Any]:
        """Run the load + validate pipeline and return an immutable-ish dict."""
        try:
            raw = load_merged_config(
                paths=self._paths, environment=self._environment, strict=strict
            )
        except ConfigLoadError as exc:
            raise ConfigError(f"Configuration load failed: {exc}") from exc

        try:
            validated = validate_config(raw)
        except ConfigValidationError as exc:
            raise ConfigError(str(exc)) from exc
        return validated


    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.bootstrap()

    def get(self, dotted_key: str, default: Any = None) -> Any:
        self._ensure_loaded()
        with self._lock:
            cursor: Any = self._config
            for segment in dotted_key.split("."):
                if isinstance(cursor, dict) and segment in cursor:
                    cursor = cursor[segment]
                else:
                    return deepcopy(default)
            return deepcopy(cursor)

    def require(self, dotted_key: str) -> Any:
        """Like :meth:`get` but raises if the key is absent."""
        value = self.get(dotted_key, _MISSING)
        if value is _MISSING:
            raise ConfigError(f"Required configuration key missing: '{dotted_key}'")
        return value

    def get_str(self, dotted_key: str, default: Optional[str] = None) -> Optional[str]:
        value = self.get(dotted_key, default)
        return None if value is None else str(value)

    def get_int(self, dotted_key: str, default: Optional[int] = None) -> Optional[int]:
        value = self.get(dotted_key, default)
        return None if value is None else int(value)

    def get_float(self, dotted_key: str, default: Optional[float] = None) -> Optional[float]:
        value = self.get(dotted_key, default)
        return None if value is None else float(value)

    def get_bool(self, dotted_key: str, default: Optional[bool] = None) -> Optional[bool]:
        value = self.get(dotted_key, default)
        if isinstance(value, bool) or value is None:
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "y", "on", "enabled"}

    def get_section(self, section: str) -> dict[str, Any]:
        """Return an entire top-level section as a deep-copied dict."""
        value = self.get(section, {})
        return value if isinstance(value, dict) else {}

    def as_dict(self) -> dict[str, Any]:
        """Return a deep copy of the entire validated configuration."""
        self._ensure_loaded()
        with self._lock:
            return deepcopy(self._config)

    def is_feature_enabled(self, flag: str, default: bool = False) -> bool:
        """Return whether a feature flag under ``feature_flags`` is enabled."""
        self._ensure_loaded()
        with self._lock:
            flags = self._config.get("feature_flags", {})
            value = flags.get(flag, default)
        return bool(value)

    @property
    def environment(self) -> AppEnvironment:
        return self._environment

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def paths(self) -> ProjectPaths:
        self._ensure_loaded()
        assert self._paths is not None  
        return self._paths

    def subscribe(self, listener: ChangeListener) -> Callable[[], None]:
        with self._lock:
            self._listeners.append(listener)

        def _unsubscribe() -> None:
            with self._lock:
                if listener in self._listeners:
                    self._listeners.remove(listener)

        return _unsubscribe

    def _notify(self, old: dict[str, Any], new: dict[str, Any]) -> None:
        with self._lock:
            listeners = list(self._listeners)
        for listener in listeners:
            try:
                listener(deepcopy(old), deepcopy(new))
            except Exception:  
                continue


def get_config_manager() -> ConfigManager:
    return ConfigManager.instance()


def get_config(dotted_key: Optional[str] = None, default: Any = None) -> Any:
    manager = ConfigManager.instance()
    if dotted_key is None:
        return manager.as_dict()
    return manager.get(dotted_key, default)
