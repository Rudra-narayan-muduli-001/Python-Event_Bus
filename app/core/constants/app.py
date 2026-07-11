from __future__ import annotations

import sys
from enum import Enum
from types import MappingProxyType
from typing import Final, Mapping

APP_NAME: Final[str] = "AIOS"
APP_FULL_NAME: Final[str] = "Personal AI Operating System"
APP_SLUG: Final[str] = "aios"
APP_VENDOR: Final[str] = "AIOS Team"
APP_DESCRIPTION: Final[str] = (
    "Offline-first, privacy-first, voice-driven personal AI operating system "
    "with modular feature groups and plugin-based extensibility."
)
VERSION_MAJOR: Final[int] = 1
VERSION_MINOR: Final[int] = 0
VERSION_PATCH: Final[int] = 0
VERSION_STAGE: Final[str] = "alpha"  

APP_VERSION: Final[str] = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
APP_VERSION_FULL: Final[str] = (
    APP_VERSION if VERSION_STAGE == "stable" else f"{APP_VERSION}-{VERSION_STAGE}"
)
APP_VERSION_TUPLE: Final[tuple[int, int, int]] = (
    VERSION_MAJOR,
    VERSION_MINOR,
    VERSION_PATCH,
)
DATABASE_SCHEMA_VERSION: Final[int] = 1
CONFIG_SCHEMA_VERSION: Final[int] = 1
PLUGIN_API_VERSION: Final[int] = 1

class Environment(str, Enum):

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


DEFAULT_ENVIRONMENT: Final[Environment] = Environment.DEVELOPMENT


class RuntimeMode(str, Enum):
    """High-level operating mode for the assistant runtime."""

    ONLINE = "online"       
    OFFLINE = "offline"    
    HYBRID = "hybrid"      
DEFAULT_RUNTIME_MODE: Final[RuntimeMode] = RuntimeMode.HYBRID


class PerformanceMode(str, Enum):
    POWER_SAVER = "power_saver"
    BALANCED = "balanced"
    HIGH_PERFORMANCE = "high_performance"
    HIGH_LOAD = "high_load"  

DEFAULT_PERFORMANCE_MODE: Final[PerformanceMode] = PerformanceMode.BALANCED
SUPPORTED_PLATFORMS: Final[frozenset[str]] = frozenset({"win32"})
CURRENT_PLATFORM: Final[str] = sys.platform
IS_WINDOWS: Final[bool] = sys.platform == "win32"

MIN_PYTHON_VERSION: Final[tuple[int, int]] = (3, 11)
CURRENT_PYTHON_VERSION: Final[tuple[int, int, int]] = (
    sys.version_info.major,
    sys.version_info.minor,
    sys.version_info.micro,
)
REFERENCE_CPU: Final[str] = "AMD Ryzen 7"
REFERENCE_GPU: Final[str] = "NVIDIA RTX 5050"
REFERENCE_GPU_VRAM_GB: Final[int] = 8

HARDWARE_TARGETS: Final[Mapping[str, object]] = MappingProxyType(
    {
        "cpu": REFERENCE_CPU,
        "gpu": REFERENCE_GPU,
        "gpu_vram_gb": REFERENCE_GPU_VRAM_GB,
        "cuda_required": False,      
        "gpu_accelerated": True,
    }
)

class FeatureGroup(str, Enum):

    FG1_VOICE = "fg1_voice_system"
    FG2_BRAIN = "fg2_ai_brain"
    FG3_WINDOWS_CONTROL = "fg3_windows_control"
    FG4_LANGUAGE = "fg4_language_intelligence"
    FG5_GUI = "fg5_gui"
    FG6_SECURITY = "fg6_security"
    FG7_PLUGINS = "fg7_plugins"
    FG8_PRODUCTIVITY = "fg8_productivity"
    FG9_AGENTS = "fg9_agent_system"
    FG10_SELF_LEARNING = "fg10_self_learning"

FEATURE_GROUP_LABELS: Final[Mapping[FeatureGroup, str]] = MappingProxyType(
    {
        FeatureGroup.FG1_VOICE: "Voice Interaction System",
        FeatureGroup.FG2_BRAIN: "AI Brain & Intelligence",
        FeatureGroup.FG3_WINDOWS_CONTROL: "Windows System Control",
        FeatureGroup.FG4_LANGUAGE: "Language Intelligence & Speech Adaptation",
        FeatureGroup.FG5_GUI: "GUI & User Experience",
        FeatureGroup.FG6_SECURITY: "Security & Permission System",
        FeatureGroup.FG7_PLUGINS: "Plugin & Extension System",
        FeatureGroup.FG8_PRODUCTIVITY: "Productivity System",
        FeatureGroup.FG9_AGENTS: "Agent System",
        FeatureGroup.FG10_SELF_LEARNING: "Self-Learning System",
    }
)
FEATURE_GROUP_STARTUP_ORDER: Final[tuple[FeatureGroup, ...]] = (
    FeatureGroup.FG1_VOICE,
    FeatureGroup.FG2_BRAIN,
    FeatureGroup.FG6_SECURITY,
    FeatureGroup.FG3_WINDOWS_CONTROL,
    FeatureGroup.FG4_LANGUAGE,
    FeatureGroup.FG8_PRODUCTIVITY,
    FeatureGroup.FG7_PLUGINS,
    FeatureGroup.FG9_AGENTS,
    FeatureGroup.FG5_GUI,
    FeatureGroup.FG10_SELF_LEARNING,
)
DEFAULT_ENCODING: Final[str] = "utf-8"
DEFAULT_TIMEZONE: Final[str] = "UTC"
DEFAULT_LOCALE: Final[str] = "en_US"
WAKE_WORD_DEFAULT: Final[str] = "assistant"
STARTUP_BANNER: Final[str] = (
    f"{APP_NAME} v{APP_VERSION_FULL} — {APP_FULL_NAME}"
)
__all__ = [
    "APP_NAME",
    "APP_FULL_NAME",
    "APP_SLUG",
    "APP_VENDOR",
    "APP_DESCRIPTION",
    "VERSION_MAJOR",
    "VERSION_MINOR",
    "VERSION_PATCH",
    "VERSION_STAGE",
    "APP_VERSION",
    "APP_VERSION_FULL",
    "APP_VERSION_TUPLE",
    "DATABASE_SCHEMA_VERSION",
    "CONFIG_SCHEMA_VERSION",
    "PLUGIN_API_VERSION",
    "Environment",
    "DEFAULT_ENVIRONMENT",
    "RuntimeMode",
    "DEFAULT_RUNTIME_MODE",
    "PerformanceMode",
    "DEFAULT_PERFORMANCE_MODE",
    "SUPPORTED_PLATFORMS",
    "CURRENT_PLATFORM",
    "IS_WINDOWS",
    "MIN_PYTHON_VERSION",
    "CURRENT_PYTHON_VERSION",
    "REFERENCE_CPU",
    "REFERENCE_GPU",
    "REFERENCE_GPU_VRAM_GB",
    "HARDWARE_TARGETS",
    "FeatureGroup",
    "FEATURE_GROUP_LABELS",
    "FEATURE_GROUP_STARTUP_ORDER",
    "DEFAULT_ENCODING",
    "DEFAULT_TIMEZONE",
    "DEFAULT_LOCALE",
    "WAKE_WORD_DEFAULT",
    "STARTUP_BANNER",
]
