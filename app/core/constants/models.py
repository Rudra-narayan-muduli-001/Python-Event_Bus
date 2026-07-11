from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Final, Mapping, Optional

class ModelRole(str, Enum):
    INTENT = "intent"
    LOCAL_LLM = "local_llm"
    CLOUD_LLM = "cloud_llm"
    EMBEDDING = "embedding"
    MULTILINGUAL_EMBEDDING = "multilingual_embedding"
    ASR = "asr"
    LANGUAGE_DETECT = "language_detect"
    TRANSLATION = "translation"
    TTS = "tts"
    SPEAKER_VERIFICATION = "speaker_verification"
    VAD = "vad"
    WAKE_WORD = "wake_word"
    VISION_DETECT = "vision_detect"
    OCR = "ocr"
    VISION_LANGUAGE = "vision_language"


class Device(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    AUTO = "auto"


class Quantization(str, Enum):
    NONE = "none"
    FP16 = "fp16"
    INT8 = "int8"
    Q4_K_M = "q4_k_m" 
    Q5_K_M = "q5_k_m"



class ModelId(str, Enum):
    MINILM_L6_V2 = "all-MiniLM-L6-v2"
    E5_MULTILINGUAL_SMALL = "multilingual-e5-small"
    GEMMA_4_E2B = "gemma-4-e2b"         
    GROQ = "groq"                       
    WHISPER_SMALL = "whisper-small"
    META_OMNILINGUAL_CTC = "meta-omnilingual-ctc"
    MARIANMT_INT8 = "marianmt-int8" 
    KOKORO_82M = "kokoro-82m"
    PIPER = "piper"
    INDIC_TTS = "indic-tts"
    CAMPPLUSPLUS = "campplusplus"
    ECAPA_TDNN = "ecapa-tdnn"
    SILERO_VAD = "silero-vad"
    OPENWAKEWORD = "openwakeword"
    YOLOV26_MEDIUM = "yolov26-medium"
    PADDLEOCR = "paddleocr"
    GOCLICK_FLORENCE2 = "goclick-florence2"

@dataclass(frozen=True, slots=True)
class ModelSpec:
    model_id: ModelId
    role: ModelRole
    device: Device
    offline: bool
    approx_vram_mb: int = 0
    approx_ram_mb: int = 0
    quantizations: tuple[Quantization, ...] = field(default_factory=tuple)
    runtime: Optional[str] = None


MODEL_SPECS: Final[Mapping[ModelId, ModelSpec]] = MappingProxyType(
    {
        ModelId.MINILM_L6_V2: ModelSpec(
            ModelId.MINILM_L6_V2, ModelRole.INTENT, Device.CPU,
            offline=True, approx_ram_mb=120,
            quantizations=(Quantization.NONE,), runtime="sentence-transformers",
        ),
        ModelId.E5_MULTILINGUAL_SMALL: ModelSpec(
            ModelId.E5_MULTILINGUAL_SMALL, ModelRole.MULTILINGUAL_EMBEDDING, Device.GPU,
            offline=True, approx_vram_mb=300,
            quantizations=(Quantization.FP16, Quantization.NONE),
            runtime="sentence-transformers",
        ),
        ModelId.GEMMA_4_E2B: ModelSpec(
            ModelId.GEMMA_4_E2B, ModelRole.LOCAL_LLM, Device.GPU,
            offline=True, approx_vram_mb=3200, approx_ram_mb=1500,
            quantizations=(Quantization.Q4_K_M, Quantization.Q5_K_M),
            runtime="llama.cpp",
        ),
        ModelId.GROQ: ModelSpec(
            ModelId.GROQ, ModelRole.CLOUD_LLM, Device.CPU,
            offline=False, runtime="Groq API",
        ),
        ModelId.WHISPER_SMALL: ModelSpec(
            ModelId.WHISPER_SMALL, ModelRole.ASR, Device.GPU,
            offline=True, approx_vram_mb=1000,
            quantizations=(Quantization.FP16, Quantization.INT8),
            runtime="openai-whisper",
        ),
        ModelId.META_OMNILINGUAL_CTC: ModelSpec(
            ModelId.META_OMNILINGUAL_CTC, ModelRole.ASR, Device.GPU,
            offline=True, approx_vram_mb=1200,
            quantizations=(Quantization.INT8,), runtime="Sherpa-ONNX",
        ),
        ModelId.MARIANMT_INT8: ModelSpec(
            ModelId.MARIANMT_INT8, ModelRole.TRANSLATION, Device.GPU,
            offline=True, approx_vram_mb=450,
            quantizations=(Quantization.INT8,), runtime="CTranslate2",
        ),
        ModelId.KOKORO_82M: ModelSpec(
            ModelId.KOKORO_82M, ModelRole.TTS, Device.GPU,
            offline=True, approx_vram_mb=400,
            quantizations=(Quantization.FP16,), runtime="Sherpa-ONNX / Kokoro",
        ),
        ModelId.PIPER: ModelSpec(
            ModelId.PIPER, ModelRole.TTS, Device.CPU,
            offline=True, approx_ram_mb=200, runtime="Piper",
        ),
        ModelId.INDIC_TTS: ModelSpec(
            ModelId.INDIC_TTS, ModelRole.TTS, Device.GPU,
            offline=True, approx_vram_mb=400, runtime="Indic TTS",
        ),
        ModelId.CAMPPLUSPLUS: ModelSpec(
            ModelId.CAMPPLUSPLUS, ModelRole.SPEAKER_VERIFICATION, Device.GPU,
            offline=True, approx_vram_mb=200, runtime="Sherpa-ONNX",
        ),
        ModelId.ECAPA_TDNN: ModelSpec(
            ModelId.ECAPA_TDNN, ModelRole.SPEAKER_VERIFICATION, Device.GPU,
            offline=True, approx_vram_mb=250, runtime="Sherpa-ONNX",
        ),
        ModelId.SILERO_VAD: ModelSpec(
            ModelId.SILERO_VAD, ModelRole.VAD, Device.CPU,
            offline=True, approx_ram_mb=60, runtime="Silero",
        ),
        ModelId.OPENWAKEWORD: ModelSpec(
            ModelId.OPENWAKEWORD, ModelRole.WAKE_WORD, Device.CPU,
            offline=True, approx_ram_mb=80, runtime="OpenWakeWord",
        ),
        ModelId.YOLOV26_MEDIUM: ModelSpec(
            ModelId.YOLOV26_MEDIUM, ModelRole.VISION_DETECT, Device.GPU,
            offline=True, approx_vram_mb=450, runtime="Ultralytics",
        ),
        ModelId.PADDLEOCR: ModelSpec(
            ModelId.PADDLEOCR, ModelRole.OCR, Device.GPU,
            offline=True, approx_vram_mb=300, runtime="PaddleOCR",
        ),
        ModelId.GOCLICK_FLORENCE2: ModelSpec(
            ModelId.GOCLICK_FLORENCE2, ModelRole.VISION_LANGUAGE, Device.GPU,
            offline=True, approx_vram_mb=500, runtime="Florence-2",
        ),
    }
)

DEFAULT_MODEL_ROUTING: Final[Mapping[ModelRole, tuple[ModelId, ...]]] = MappingProxyType(
    {
        ModelRole.INTENT: (ModelId.MINILM_L6_V2,),
        ModelRole.LOCAL_LLM: (ModelId.GEMMA_4_E2B,),
        ModelRole.CLOUD_LLM: (ModelId.GROQ,),
        ModelRole.MULTILINGUAL_EMBEDDING: (ModelId.E5_MULTILINGUAL_SMALL,),
        ModelRole.ASR: (ModelId.WHISPER_SMALL, ModelId.META_OMNILINGUAL_CTC),
        ModelRole.LANGUAGE_DETECT: (ModelId.WHISPER_SMALL, ModelId.META_OMNILINGUAL_CTC),
        ModelRole.TRANSLATION: (ModelId.MARIANMT_INT8,),
        ModelRole.TTS: (ModelId.KOKORO_82M, ModelId.PIPER),
        ModelRole.SPEAKER_VERIFICATION: (ModelId.CAMPPLUSPLUS, ModelId.ECAPA_TDNN),
        ModelRole.VAD: (ModelId.SILERO_VAD,),
        ModelRole.WAKE_WORD: (ModelId.OPENWAKEWORD,),
        ModelRole.VISION_DETECT: (ModelId.YOLOV26_MEDIUM,),
        ModelRole.OCR: (ModelId.PADDLEOCR,),
        ModelRole.VISION_LANGUAGE: (ModelId.GOCLICK_FLORENCE2,),
    }
)

def get_spec(model_id: ModelId) -> ModelSpec:
    return MODEL_SPECS[model_id]


def primary_model(role: ModelRole) -> ModelId:
    return DEFAULT_MODEL_ROUTING[role][0]


def fallback_models(role: ModelRole) -> tuple[ModelId, ...]:
    return DEFAULT_MODEL_ROUTING[role][1:]


def models_for_role(role: ModelRole) -> tuple[ModelId, ...]:
    return DEFAULT_MODEL_ROUTING.get(role, ())


def offline_models() -> tuple[ModelId, ...]:
    return tuple(mid for mid, spec in MODEL_SPECS.items() if spec.offline)

__all__ = [
    "ModelRole",
    "Device",
    "Quantization",
    "ModelId",
    "ModelSpec",
    "MODEL_SPECS",
    "DEFAULT_MODEL_ROUTING",
    "get_spec",
    "primary_model",
    "fallback_models",
    "models_for_role",
    "offline_models",
]
