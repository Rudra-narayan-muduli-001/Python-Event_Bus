from __future__ import annotations
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Final, Mapping
from app.core.constants.app import (
    DEFAULT_ENVIRONMENT,
    DEFAULT_PERFORMANCE_MODE,
    DEFAULT_RUNTIME_MODE,
    Environment,
    PerformanceMode,
    RuntimeMode,
)

@dataclass(frozen=True, slots=True)
class VoiceSettings:
    sample_rate_hz: int = 16_000
    channels: int = 1
    chunk_duration_ms: int = 30
    wake_word: str = "assistant"
    wake_detection_target_ms: int = 200
    speaker_verification_target_ms: int = 1_500
    vad_detection_target_ms: int = 50
    stt_final_target_ms: int = 800
    tts_first_audio_target_ms: int = 400
    interrupt_response_target_ms: int = 300
    continuous_verification_interval_seconds: int = 5
    speaker_similarity_threshold: float = 0.70

VOICE: Final[VoiceSettings] = VoiceSettings()


@dataclass(frozen=True, slots=True)
class BrainSettings:
    intent_latency_target_ms: int = 15
    default_max_search_results: int = 5
    max_context_tokens: int = 8_192
    response_reserve_tokens: int = 1_024
    confidence_auto_execute: float = 0.90
    confidence_ask_user: float = 0.60
    temperature: float = 0.7
    top_p: float = 0.95
    max_output_tokens: int = 1_024
    stream_tokens: bool = True


BRAIN: Final[BrainSettings] = BrainSettings()
TOKEN_BUDGET_PRIORITY: Final[Mapping[str, int]] = MappingProxyType(
    {
        "system_prompt": 1,
        "current_conversation": 2,
        "personal_memory": 3,
        "knowledge_graph": 4,
        "qdrant_memories": 5,
        "search_results": 6,
        "older_conversation": 7,
    }
)

@dataclass(frozen=True, slots=True)
class MemorySettings:
    temporary_cache_ttl_days: int = 3          
    search_cache_ttl_days: int = 3            
    session_memory_ttl_hours: int = 12
    importance_min: int = 0
    importance_max: int = 5
    importance_discard: int = 0
    importance_permanent: int = 5
    importance_default: int = 2
    keep_memory_versions: bool = True
    long_absence_days: int = 3                 

MEMORY: Final[MemorySettings] = MemorySettings()

@dataclass(frozen=True, slots=True)
class CacheSettings:
    memory_cache_max_entries: int = 4_096
    lru_cache_max_entries: int = 2_048
    disk_cache_max_mb: int = 512
    semantic_cache_enabled: bool = True
    default_ttl_seconds: int = 3_600


CACHE: Final[CacheSettings] = CacheSettings()

@dataclass(frozen=True, slots=True)
class WindowsControlSettings:
    native_latency_target_ms: int = 15        
    vision_latency_target_ms: int = 80        
    vlm_latency_target_ms: int = 900          
    max_action_retries: int = 2
    vision_retry_limit: int = 1
    action_timeout_seconds: int = 30
    create_recovery_points: bool = True      


WINDOWS_CONTROL: Final[WindowsControlSettings] = WindowsControlSettings()

@dataclass(frozen=True, slots=True)
class SecuritySettings:
    speaker_verification_target_ms: int = 1_500
    mfa_verification_target_ms: int = 2_000
    permission_validation_target_ms: int = 5
    risk_evaluation_target_ms: int = 20
    firewall_analysis_target_ms: int = 100
    tool_validation_target_ms: int = 5
    sandbox_startup_target_ms: int = 100
    log_write_target_ms: int = 10
    recovery_init_target_ms: int = 2_000
    max_auth_attempts: int = 3
    session_ttl_minutes: int = 30
    require_mfa_for_high_risk: bool = True
    fail_secure: bool = True                


SECURITY: Final[SecuritySettings] = SecuritySettings()

@dataclass(frozen=True, slots=True)
class TelemetrySettings:
    idle_cpu_warn_percent: int = 15           
    active_cpu_warn_percent: int = 30         
    cpu_critical_percent: int = 90
    ram_warn_mb: int = 3_000                 
    ram_critical_percent: int = 90
    vram_warn_percent: int = 80
    vram_critical_percent: int = 95
    disk_warn_percent: int = 85
    disk_critical_percent: int = 95
    battery_low_percent: int = 20
    heartbeat_interval_seconds: int = 5
    monitor_poll_interval_seconds: int = 2
    wake_detection_target_ms: int = 300        
    speaker_verification_target_ms: int = 500  
    vad_detection_target_ms: int = 100         
    stt_final_target_ms: int = 1500            
    llm_first_token_target_ms: int = 800         
    llm_total_target_ms: int = 6000          
    tts_first_audio_target_ms: int = 400      
    interrupt_response_target_ms: int = 200    


TELEMETRY: Final[TelemetrySettings] = TelemetrySettings()
@dataclass(frozen=True, slots=True)
class SearchSettings:
    default_provider: str = "auto"
    allow_fallback: bool = True
    max_results: int = 5
    request_timeout_seconds: int = 10 
    provider_order: tuple[str, ...] = (
        "cache",
        "tavily",
        "brave",
        "duckduckgo",
        "gemini_grounding",
    )
    empty_result_retry_limit: int = 2


SEARCH: Final[SearchSettings] = SearchSettings()
@dataclass(frozen=True, slots=True)
class PluginSettings:
    hot_reload_enabled: bool = True
    verify_signatures: bool = True
    default_network_access: bool = False    
    execution_timeout_seconds: int = 15
    max_concurrent_plugins: int = 16
    rate_limit_per_minute: int = 120


PLUGINS: Final[PluginSettings] = PluginSettings()
@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_ms: int = 200
    max_delay_ms: int = 5_000
    backoff_multiplier: float = 2.0
    jitter: bool = True


DEFAULT_RETRY: Final[RetryPolicy] = RetryPolicy()
DEFAULT_FEATURE_FLAGS: Final[Mapping[str, bool]] = MappingProxyType(
    {
        "voice_enabled": True,
        "continuous_verification": True,
        "cloud_llm_enabled": True,
        "realtime_search_enabled": True,
        "vision_automation_enabled": True,
        "desktop_companion_enabled": True,
        "smart_cursor_enabled": True,
        "plugins_enabled": True,
        "self_learning_enabled": True,
        "telemetry_enabled": True,
        "high_load_mode_auto": True,
    }
)
DEFAULT_ENV: Final[Environment] = DEFAULT_ENVIRONMENT
DEFAULT_RUNTIME: Final[RuntimeMode] = DEFAULT_RUNTIME_MODE
DEFAULT_PERFORMANCE: Final[PerformanceMode] = DEFAULT_PERFORMANCE_MODE

__all__ = [
    "VoiceSettings",
    "VOICE",
    "BrainSettings",
    "BRAIN",
    "TOKEN_BUDGET_PRIORITY",
    "MemorySettings",
    "MEMORY",
    "CacheSettings",
    "CACHE",
    "WindowsControlSettings",
    "WINDOWS_CONTROL",
    "SecuritySettings",
    "SECURITY",
    "TelemetrySettings",
    "TELEMETRY",
    "SearchSettings",
    "SEARCH",
    "PluginSettings",
    "PLUGINS",
    "RetryPolicy",
    "DEFAULT_RETRY",
    "DEFAULT_FEATURE_FLAGS",
    "DEFAULT_ENV",
    "DEFAULT_RUNTIME",
    "DEFAULT_PERFORMANCE",
]
