from __future__ import annotations

from copy import deepcopy
import os
import re
from pathlib import Path
from typing import Any, Final, Optional

from app.core.configs.defaults import get_default_config
from app.core.configs.environment import (
    AppEnvironment,
    get_bool,
    get_environment,
)
from app.core.configs.paths import ProjectPaths, get_paths
from app.core.utils.dict_utils import deep_merge

__all__ = [
    "ConfigLoadError",
    "load_yaml_file",
    "load_merged_config",
    "ENV_OVERRIDE_PREFIX",
]

ENV_OVERRIDE_PREFIX: Final[str] = "AIOS_CFG__"
_ENV_PATH_SEPARATOR: Final[str] = "__"

_DOMAIN_FILES: Final[dict[str, str]] = {
    "logging.yaml": "logging",
    "feature_flags.yaml": "feature_flags",
    "model_registry.yaml": "model_registry",
    "permissions.yaml": "permissions",
    "language_policy.yaml": "language_policy",
    "paths.yaml": "paths",
}

_INTERP_PATTERN: Final[re.Pattern[str]] = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::([^}]*))?\}")

class ConfigLoadError(RuntimeError):
    pass


def _interpolate_value(value: Any) -> Any:
    if isinstance(value, str):
        def _replace(match: re.Match[str]) -> str:
            var_name, default = match.group(1), match.group(2)
            return os.environ.get(var_name, default if default is not None else match.group(0))

        return _INTERP_PATTERN.sub(_replace, value)
    if isinstance(value, dict):
        return {k: _interpolate_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_interpolate_value(item) for item in value]
    return value


def _coerce_scalar(raw: str) -> Any:
    stripped = raw.strip()
    lowered = stripped.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none", ""}:
        return None
    try:
        return int(stripped)
    except ValueError:
        pass
    try:
        return float(stripped)
    except ValueError:
        return stripped

def load_yaml_file(path: Path, *, required: bool = False) -> dict[str, Any]:

    if not path.exists():
        if required:
            raise ConfigLoadError(f"Required config file not found: {path}")
        return {}

    try:
        import yaml
    except ImportError as exc:
        raise ConfigLoadError(
            "PyYAML is required to load YAML config files. Install it with: pip install pyyaml"
        ) from exc

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ConfigLoadError(f"Failed to parse YAML file '{path}': {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigLoadError(
            f"Top-level YAML content in '{path}' must be a mapping, got {type(data).__name__}."
        )
    return data

def _apply_env_overrides(config: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(config)
    for env_key, raw_value in os.environ.items():
        if not env_key.startswith(ENV_OVERRIDE_PREFIX):
            continue
        path_str = env_key[len(ENV_OVERRIDE_PREFIX):]
        parts = [segment for segment in path_str.split(_ENV_PATH_SEPARATOR) if segment]
        if not parts:
            continue
        cursor: dict[str, Any] = result
        for segment in parts[:-1]:
            existing = cursor.get(segment)
            if not isinstance(existing, dict):
                existing = {}
                cursor[segment] = existing
            cursor = existing
        cursor[parts[-1]] = _coerce_scalar(raw_value)
    return result

def load_merged_config(
    paths: Optional[ProjectPaths] = None,
    environment: Optional[AppEnvironment] = None,
    *,
    strict: Optional[bool] = None,
) -> dict[str, Any]:
    resolved_paths = paths or get_paths()
    env = environment or get_environment()
    is_strict = strict if strict is not None else bool(get_bool("AIOS_CFG_STRICT", False))

    config = get_default_config(env)

    app_config = load_yaml_file(
        resolved_paths.core_config_file("app_config.yaml"), required=is_strict
    )
    if app_config:
        config = deep_merge(config, app_config)

    for filename, section in _DOMAIN_FILES.items():
        file_data = load_yaml_file(
            resolved_paths.core_config_file(filename), required=is_strict
        )
        if not file_data:
            continue
        body = file_data.get(section, file_data)
        config[section] = deep_merge(config.get(section, {}), body)
    env_doc = load_yaml_file(
        resolved_paths.core_config_file("environment.yaml"), required=is_strict
    )
    if env_doc:
        overlay = env_doc.get("environments", {}).get(env.value, {}) or env_doc.get(env.value, {})
        if overlay:
            config = deep_merge(config, overlay)
    config = _interpolate_value(config)
    config = _apply_env_overrides(config)
    config.setdefault("app", {})["environment"] = env.value
    return config
