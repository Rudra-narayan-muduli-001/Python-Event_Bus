from __future__ import annotations

import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Iterable, Optional

from app.core.configs.environment import get_path

__all__ = ["ProjectPaths", "get_paths", "resolve_project_root"]


_ROOT_MARKERS: Final[tuple[str, ...]] = ("pyproject.toml", "main.py", "launcher.py")


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

    raise RuntimeError(
        f"Could not determine project root. Set AIOS_ROOT environment variable "
        f"or ensure a marker file {_ROOT_MARKERS} exists in a parent directory."
    )


_PATH_SPEC: Final[list[tuple[str, str]]] = [
    ("app_dir", "app"),
    ("data_dir", "data"),
    ("resources_dir", "resources"),
    ("scripts_dir", "scripts"),
    ("docs_dir", "docs"),
    ("tests_dir", "tests"),
    ("logs_dir", "logs"),
    ("core_configs_dir", "app/core/configs"),
    ("data_configs_dir", "data/configs"),
    ("data_cache_dir", "data/cache"),
    ("data_runtime_dir", "data/runtime"),
    ("data_temp_dir", "data/temp"),
    ("data_backups_dir", "data/backups"),
    ("data_experience_dir", "data/experience"),
    ("data_learning_dir", "data/learning"),
    ("data_benchmark_dir", "data/benchmark"),
    ("data_memory_dir", "data/memory"),
    ("data_graphs_dir", "data/graphs"),
    ("data_experiments_dir", "data/experiments"),
    ("data_patches_dir", "data/patches"),
    ("data_rollback_dir", "data/rollback"),
    ("data_analytics_dir", "data/analytics"),
    ("data_archive_dir", "data/archive"),
    ("ai_models_dir", "resources/ai_models"),
    ("prompts_dir", "resources/prompts"),
    ("templates_dir", "resources/templates"),
    ("dictionaries_dir", "resources/dictionaries"),
    ("schemas_dir", "resources/schemas"),
    ("logs_system_dir", "logs/system"),
    ("logs_startup_dir", "logs/startup"),
    ("logs_events_dir", "logs/events"),
    ("logs_errors_dir", "logs/errors"),
    ("logs_audit_dir", "logs/audit"),
    ("logs_security_dir", "logs/security"),
    ("logs_plugins_dir", "logs/plugins"),
    ("logs_agents_dir", "logs/agents"),
    ("logs_crashes_dir", "logs/crashes"),
]


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

        for attr, rel in _PATH_SPEC:
            segments = rel.split("/")
            _set(attr, root.joinpath(*segments))

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
