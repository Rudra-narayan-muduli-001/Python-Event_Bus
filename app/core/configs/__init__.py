from __future__ import annotations

from typing import Optional

from app.core.configs.config_loader import (
    ConfigLoadError,
    load_merged_config,
    load_yaml_file,
)
from app.core.configs.config_manager import (
    ConfigError,
    ConfigManager,
    get_config,
    get_config_manager,
)
from app.core.configs.config_validator import (
    PYDANTIC_AVAILABLE,
    ConfigValidationError,
    validate_config,
)
from app.core.configs.defaults import get_default_config
from app.core.configs.environment import (
    AppEnvironment,
    EnvVarError,
    get_environment,
    is_development,
    is_production,
    is_testing,
    load_dotenv_if_present,
)
from app.core.configs.paths import ProjectPaths, get_paths, resolve_project_root

__all__ = [
    "AppEnvironment",
    "EnvVarError",
    "get_environment",
    "is_development",
    "is_production",
    "is_testing",
    "load_dotenv_if_present",
    "ProjectPaths",
    "get_paths",
    "resolve_project_root",
    "get_default_config",
    "ConfigLoadError",
    "load_merged_config",
    "load_yaml_file",
    "ConfigValidationError",
    "PYDANTIC_AVAILABLE",
    "validate_config",
    "ConfigError",
    "ConfigManager",
    "get_config",
    "get_config_manager",
    "initialize_configuration",
]


def initialize_configuration(
    *,
    explicit_root: Optional[str] = None,
    environment: Optional[AppEnvironment] = None,
    load_dotenv: bool = True,
    create_directories: bool = True,
    strict: Optional[bool] = None,
) -> ConfigManager:
    if load_dotenv:
        load_dotenv_if_present()

    from pathlib import Path

    paths = get_paths(
        explicit_root=Path(explicit_root) if explicit_root else None,
        refresh=explicit_root is not None,
    )

    manager = get_config_manager()
    return manager.bootstrap(
        paths=paths,
        environment=environment,
        create_directories=create_directories,
        strict=strict,
    )
