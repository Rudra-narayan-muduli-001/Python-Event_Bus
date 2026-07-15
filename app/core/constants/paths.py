from __future__ import annotations
import os
from pathlib import Path
from types import MappingProxyType
from typing import Final, Mapping, Iterable
from app.core.constants.app import APP_SLUG, FeatureGroup

_ENV_ROOT_VAR: Final[str] = "AIOS_ROOT"

def _resolve_project_root() -> Path:
    env_root = os.environ.get(_ENV_ROOT_VAR, "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve()
    raise RuntimeError(
        f"{_ENV_ROOT_VAR} environment variable is not set. "
        f"Set it to the absolute path of the project root."
    )


PROJECT_ROOT: Final[Path] = _resolve_project_root()
APP_DIR: Final[Path] = PROJECT_ROOT / "app"
CORE_DIR: Final[Path] = APP_DIR / "core"
FEATURE_GROUPS_DIR: Final[Path] = APP_DIR / "feature_groups"
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
RESOURCES_DIR: Final[Path] = PROJECT_ROOT / "resources"
SCRIPTS_DIR: Final[Path] = PROJECT_ROOT / "scripts"
DOCS_DIR: Final[Path] = PROJECT_ROOT / "docs"
TESTS_DIR: Final[Path] = PROJECT_ROOT / "tests"
LOGS_DIR: Final[Path] = PROJECT_ROOT / "logs"
DATA_CONFIGS_DIR: Final[Path] = DATA_DIR / "configs"
CACHE_DIR: Final[Path] = DATA_DIR / "cache"
RUNTIME_DIR: Final[Path] = DATA_DIR / "runtime"
TEMP_DIR: Final[Path] = DATA_DIR / "temp"
BACKUPS_DIR: Final[Path] = DATA_DIR / "backups"
EXPERIENCE_DIR: Final[Path] = DATA_DIR / "experience"
LEARNING_DIR: Final[Path] = DATA_DIR / "learning"
BENCHMARK_DIR: Final[Path] = DATA_DIR / "benchmark"
MEMORY_DIR: Final[Path] = DATA_DIR / "memory"
GRAPHS_DIR: Final[Path] = DATA_DIR / "graphs"
EXPERIMENTS_DIR: Final[Path] = DATA_DIR / "experiments"
PATCHES_DIR: Final[Path] = DATA_DIR / "patches"
ROLLBACK_DIR: Final[Path] = DATA_DIR / "rollback"
ANALYTICS_DIR: Final[Path] = DATA_DIR / "analytics"
ARCHIVE_DIR: Final[Path] = DATA_DIR / "archive"
RECOVERY_DIR: Final[Path] = BACKUPS_DIR / "recovery"
AI_MODELS_DIR: Final[Path] = RESOURCES_DIR / "ai_models"
PROMPTS_DIR: Final[Path] = RESOURCES_DIR / "prompts"
TEMPLATES_DIR: Final[Path] = RESOURCES_DIR / "templates"
DICTIONARIES_DIR: Final[Path] = RESOURCES_DIR / "dictionaries"
SCHEMAS_DIR: Final[Path] = RESOURCES_DIR / "schemas"
CONFIG_DIR: Final[Path] = CORE_DIR / "configs"
APP_CONFIG_FILE: Final[Path] = CONFIG_DIR / "app_config.yaml"
LOGGING_CONFIG_FILE: Final[Path] = CONFIG_DIR / "logging.yaml"
ENVIRONMENT_CONFIG_FILE: Final[Path] = CONFIG_DIR / "environment.yaml"
FEATURE_FLAGS_FILE: Final[Path] = CONFIG_DIR / "feature_flags.yaml"
MODEL_REGISTRY_FILE: Final[Path] = CONFIG_DIR / "model_registry.yaml"
PERMISSIONS_FILE: Final[Path] = CONFIG_DIR / "permissions.yaml"
LANGUAGE_POLICY_FILE: Final[Path] = CONFIG_DIR / "language_policy.yaml"
PATHS_CONFIG_FILE: Final[Path] = CONFIG_DIR / "paths.yaml"
METADATA_DB_FILE: Final[Path] = DATA_DIR / "aios_metadata.db"          
SECURE_DB_FILE: Final[Path] = DATA_DIR / "aios_secure.db"              
SEARCH_CACHE_DB_FILE: Final[Path] = CACHE_DIR / "search_cache.db"
SEMANTIC_CACHE_DB_FILE: Final[Path] = CACHE_DIR / "semantic_cache.db"
QDRANT_DIR: Final[Path] = MEMORY_DIR / "qdrant"
KNOWLEDGE_GRAPH_DIR: Final[Path] = GRAPHS_DIR / "knowledge_graph"
LOG_SYSTEM_DIR: Final[Path] = LOGS_DIR / "system"
LOG_STARTUP_DIR: Final[Path] = LOGS_DIR / "startup"
LOG_EVENTS_DIR: Final[Path] = LOGS_DIR / "events"
LOG_ERRORS_DIR: Final[Path] = LOGS_DIR / "errors"
LOG_AUDIT_DIR: Final[Path] = LOGS_DIR / "audit"
LOG_SECURITY_DIR: Final[Path] = LOGS_DIR / "security"
LOG_PLUGINS_DIR: Final[Path] = LOGS_DIR / "plugins"
LOG_AGENTS_DIR: Final[Path] = LOGS_DIR / "agents"
LOG_CRASHES_DIR: Final[Path] = LOGS_DIR / "crashes"

_MANAGED_DIRS: Final[tuple[Path, ...]] = (
    DATA_DIR,
    DATA_CONFIGS_DIR,
    CACHE_DIR,
    RUNTIME_DIR,
    TEMP_DIR,
    BACKUPS_DIR,
    RECOVERY_DIR,
    EXPERIENCE_DIR,
    LEARNING_DIR,
    BENCHMARK_DIR,
    MEMORY_DIR,
    QDRANT_DIR,
    GRAPHS_DIR,
    KNOWLEDGE_GRAPH_DIR,
    EXPERIMENTS_DIR,
    PATCHES_DIR,
    ROLLBACK_DIR,
    ANALYTICS_DIR,
    ARCHIVE_DIR,
    RESOURCES_DIR,
    AI_MODELS_DIR,
    PROMPTS_DIR,
    TEMPLATES_DIR,
    DICTIONARIES_DIR,
    SCHEMAS_DIR,
    LOGS_DIR,
    LOG_SYSTEM_DIR,
    LOG_STARTUP_DIR,
    LOG_EVENTS_DIR,
    LOG_ERRORS_DIR,
    LOG_AUDIT_DIR,
    LOG_SECURITY_DIR,
    LOG_PLUGINS_DIR,
    LOG_AGENTS_DIR,
    LOG_CRASHES_DIR,
)

MANAGED_DIRECTORIES: Final[tuple[Path, ...]] = _MANAGED_DIRS

def feature_group_dir(fg: FeatureGroup) -> Path:
    return FEATURE_GROUPS_DIR / fg.value


def feature_group_log_dir(fg: FeatureGroup) -> Path:
    return LOGS_DIR / fg.value


def model_path(*parts: str) -> Path:
    return AI_MODELS_DIR.joinpath(*parts)


def prompt_path(name: str) -> Path:
    return PROMPTS_DIR / name


def dictionary_path(name: str) -> Path:
    return DICTIONARIES_DIR / name


def config_path(name: str) -> Path:
    return CONFIG_DIR / name


def temp_path(*parts: str) -> Path:
    return TEMP_DIR.joinpath(*parts)


def ensure_dirs(extra: Iterable[Path] | None = None) -> None:
    for directory in _MANAGED_DIRS:
        directory.mkdir(parents=True, exist_ok=True)
    if extra:
        for directory in extra:
            Path(directory).mkdir(parents=True, exist_ok=True)

ROOT_PATHS: Final[Mapping[str, Path]] = MappingProxyType(
    {
        "project_root": PROJECT_ROOT,
        "app": APP_DIR,
        "data": DATA_DIR,
        "resources": RESOURCES_DIR,
        "logs": LOGS_DIR,
        "config": CONFIG_DIR,
    }
)

__all__ = [
    "PROJECT_ROOT",
    "APP_DIR",
    "CORE_DIR",
    "FEATURE_GROUPS_DIR",
    "DATA_DIR",
    "RESOURCES_DIR",
    "SCRIPTS_DIR",
    "DOCS_DIR",
    "TESTS_DIR",
    "LOGS_DIR",
    "DATA_CONFIGS_DIR",
    "CACHE_DIR",
    "RUNTIME_DIR",
    "TEMP_DIR",
    "BACKUPS_DIR",
    "RECOVERY_DIR",
    "EXPERIENCE_DIR",
    "LEARNING_DIR",
    "BENCHMARK_DIR",
    "MEMORY_DIR",
    "GRAPHS_DIR",
    "EXPERIMENTS_DIR",
    "PATCHES_DIR",
    "ROLLBACK_DIR",
    "ANALYTICS_DIR",
    "ARCHIVE_DIR",
    "AI_MODELS_DIR",
    "PROMPTS_DIR",
    "TEMPLATES_DIR",
    "DICTIONARIES_DIR",
    "SCHEMAS_DIR",
    "CONFIG_DIR",
    "APP_CONFIG_FILE",
    "LOGGING_CONFIG_FILE",
    "ENVIRONMENT_CONFIG_FILE",
    "FEATURE_FLAGS_FILE",
    "MODEL_REGISTRY_FILE",
    "PERMISSIONS_FILE",
    "LANGUAGE_POLICY_FILE",
    "PATHS_CONFIG_FILE",
    "METADATA_DB_FILE",
    "SECURE_DB_FILE",
    "SEARCH_CACHE_DB_FILE",
    "SEMANTIC_CACHE_DB_FILE",
    "QDRANT_DIR",
    "KNOWLEDGE_GRAPH_DIR",
    "LOG_SYSTEM_DIR",
    "LOG_STARTUP_DIR",
    "LOG_EVENTS_DIR",
    "LOG_ERRORS_DIR",
    "LOG_AUDIT_DIR",
    "LOG_SECURITY_DIR",
    "LOG_PLUGINS_DIR",
    "LOG_AGENTS_DIR",
    "LOG_CRASHES_DIR",
    "MANAGED_DIRECTORIES",
    "ROOT_PATHS",
    "feature_group_dir",
    "feature_group_log_dir",
    "model_path",
    "prompt_path",
    "dictionary_path",
    "config_path",
    "temp_path",
    "ensure_dirs",
]
