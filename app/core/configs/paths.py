
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Iterable, Optional

from app.core.configs.environment import get_path

__all__ = ["ProjectPaths", "get_paths", "resolve_project_root"]


_ROOT_MARKERS: Final[tuple[str, ...]] = ("pyproject.toml", "main.py", "launcher.py")


_THIS_FILE_ROOT_DEPTH: Final[int] = 4


def resolve_project_root(explicit: Optional[Path] = None) -> Path:
    
    if explicit is not None:
        return Path(explicit).expanduser().resolve()

    
    env_root = get_path("AIOS_ROOT")
    if env_root is not None:
        return env_root.resolve()

    
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        if candidate.is_dir() and any((candidate / marker).exists() for marker in _ROOT_MARKERS):
            return candidate

    
    try:
        return here.parents[_THIS_FILE_ROOT_DEPTH - 1]
    except IndexError:  
        return here.parent


@dataclass(frozen=True)
class ProjectPaths:
  

    root: Path

    
    app_dir: Path = field(init=False)
    data_dir: Path = field(init=False)
    resources_dir: Path = field(init=False)
    scripts_dir: Path = field(init=False)
    docs_dir: Path = field(init=False)
    tests_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)

    core_configs_dir: Path = field(init=False)

    data_configs_dir: Path = field(init=False)
    data_cache_dir: Path = field(init=False)
    data_runtime_dir: Path = field(init=False)
    data_temp_dir: Path = field(init=False)
    data_backups_dir: Path = field(init=False)
    data_experience_dir: Path = field(init=False)
    data_learning_dir: Path = field(init=False)
    data_benchmark_dir: Path = field(init=False)
    data_memory_dir: Path = field(init=False)
    data_graphs_dir: Path = field(init=False)
    data_experiments_dir: Path = field(init=False)
    data_patches_dir: Path = field(init=False)
    data_rollback_dir: Path = field(init=False)
    data_analytics_dir: Path = field(init=False)
    data_archive_dir: Path = field(init=False)


    ai_models_dir: Path = field(init=False)
    prompts_dir: Path = field(init=False)
    templates_dir: Path = field(init=False)
    dictionaries_dir: Path = field(init=False)
    schemas_dir: Path = field(init=False)


    logs_system_dir: Path = field(init=False)
    logs_startup_dir: Path = field(init=False)
    logs_events_dir: Path = field(init=False)
    logs_errors_dir: Path = field(init=False)
    logs_audit_dir: Path = field(init=False)
    logs_security_dir: Path = field(init=False)
    logs_plugins_dir: Path = field(init=False)
    logs_agents_dir: Path = field(init=False)
    logs_crashes_dir: Path = field(init=False)

    def __post_init__(self) -> None:
       
        root = self.root

        def _set(name: str, path: Path) -> None:
            object.__setattr__(self, name, path)

        # Top-level
        _set("app_dir", root / "app")
        _set("data_dir", root / "data")
        _set("resources_dir", root / "resources")
        _set("scripts_dir", root / "scripts")
        _set("docs_dir", root / "docs")
        _set("tests_dir", root / "tests")
        _set("logs_dir", root / "logs")
        _set("core_configs_dir", root / "app" / "core" / "configs")
        data = root / "data"
        _set("data_configs_dir", data / "configs")
        _set("data_cache_dir", data / "cache")
        _set("data_runtime_dir", data / "runtime")
        _set("data_temp_dir", data / "temp")
        _set("data_backups_dir", data / "backups")
        _set("data_experience_dir", data / "experience")
        _set("data_learning_dir", data / "learning")
        _set("data_benchmark_dir", data / "benchmark")
        _set("data_memory_dir", data / "memory")
        _set("data_graphs_dir", data / "graphs")
        _set("data_experiments_dir", data / "experiments")
        _set("data_patches_dir", data / "patches")
        _set("data_rollback_dir", data / "rollback")
        _set("data_analytics_dir", data / "analytics")
        _set("data_archive_dir", data / "archive")
        resources = root / "resources"
        _set("ai_models_dir", resources / "ai_models")
        _set("prompts_dir", resources / "prompts")
        _set("templates_dir", resources / "templates")
        _set("dictionaries_dir", resources / "dictionaries")
        _set("schemas_dir", resources / "schemas")
        logs = root / "logs"
        _set("logs_system_dir", logs / "system")
        _set("logs_startup_dir", logs / "startup")
        _set("logs_events_dir", logs / "events")
        _set("logs_errors_dir", logs / "errors")
        _set("logs_audit_dir", logs / "audit")
        _set("logs_security_dir", logs / "security")
        _set("logs_plugins_dir", logs / "plugins")
        _set("logs_agents_dir", logs / "agents")
        _set("logs_crashes_dir", logs / "crashes")

    def core_config_file(self, filename: str) -> Path:
        return self.core_configs_dir / filename

    def writable_dirs(self) -> tuple[Path, ...]:
        return (
            self.data_dir,
            self.data_configs_dir,
            self.data_cache_dir,
            self.data_runtime_dir,
            self.data_temp_dir,
            self.data_backups_dir,
            self.data_experience_dir,
            self.data_learning_dir,
            self.data_benchmark_dir,
            self.data_memory_dir,
            self.data_graphs_dir,
            self.data_experiments_dir,
            self.data_patches_dir,
            self.data_rollback_dir,
            self.data_analytics_dir,
            self.data_archive_dir,
            self.logs_dir,
            self.logs_system_dir,
            self.logs_startup_dir,
            self.logs_events_dir,
            self.logs_errors_dir,
            self.logs_audit_dir,
            self.logs_security_dir,
            self.logs_plugins_dir,
            self.logs_agents_dir,
            self.logs_crashes_dir,
        )

    def ensure_directories(self, extra: Optional[Iterable[Path]] = None) -> None:
       
        targets = list(self.writable_dirs())
        if extra:
            targets.extend(extra)
        for directory in targets:
            directory.mkdir(parents=True, exist_ok=True)

_paths_lock = threading.Lock()
_paths_instance: Optional[ProjectPaths] = None


def get_paths(explicit_root: Optional[Path] = None, *, refresh: bool = False) -> ProjectPaths:

    global _paths_instance

    if _paths_instance is not None and not refresh and explicit_root is None:
        return _paths_instance

    with _paths_lock:
        if _paths_instance is None or refresh or explicit_root is not None:
            root = resolve_project_root(explicit_root)
            _paths_instance = ProjectPaths(root=root)
        return _paths_instance
