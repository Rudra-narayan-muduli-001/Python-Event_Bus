from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Final, FrozenSet, Mapping


class LanguageCode(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    HINGLISH = "hinglish"
    ODIA = "or"
    BENGALI = "bn"
    TAMIL = "ta"
    TELUGU = "te"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    URDU = "ur"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    JAPANESE = "ja"
    UNKNOWN = "unknown"


DEFAULT_LANGUAGE: Final[LanguageCode] = LanguageCode.ENGLISH
PRIMARY_LANGUAGES: Final[FrozenSet[LanguageCode]] = frozenset(
    {
        LanguageCode.ENGLISH,
        LanguageCode.HINDI,
        LanguageCode.HINGLISH,
        LanguageCode.ODIA,
    }
)
CODE_MIXED_LANGUAGES: Final[FrozenSet[LanguageCode]] = frozenset(
    {LanguageCode.HINGLISH}
)

@dataclass(frozen=True, slots=True)
class LanguageCapabilities:

    stt: bool
    tts: bool
    translation: bool
    emotion: bool


def _caps(stt: bool, tts: bool, translation: bool, emotion: bool) -> LanguageCapabilities:
    return LanguageCapabilities(stt=stt, tts=tts, translation=translation, emotion=emotion)


LANGUAGE_CAPABILITIES: Final[Mapping[LanguageCode, LanguageCapabilities]] = MappingProxyType(
    {
        LanguageCode.ENGLISH: _caps(True, True, True, True),
        LanguageCode.HINDI: _caps(True, True, True, True),
        LanguageCode.HINGLISH: _caps(True, True, True, True),
        LanguageCode.ODIA: _caps(True, True, True, True),
        LanguageCode.BENGALI: _caps(True, True, True, False),
        LanguageCode.TAMIL: _caps(True, True, True, False),
        LanguageCode.TELUGU: _caps(True, True, True, False),
        LanguageCode.MARATHI: _caps(True, True, True, False),
        LanguageCode.GUJARATI: _caps(True, True, True, False),
        LanguageCode.KANNADA: _caps(True, True, True, False),
        LanguageCode.MALAYALAM: _caps(True, True, True, False),
        LanguageCode.PUNJABI: _caps(True, True, True, False),
        LanguageCode.URDU: _caps(True, True, True, False),
        LanguageCode.SPANISH: _caps(True, True, True, False),
        LanguageCode.FRENCH: _caps(True, True, True, False),
        LanguageCode.GERMAN: _caps(True, True, True, False),
        LanguageCode.CHINESE: _caps(True, True, True, False),
        LanguageCode.JAPANESE: _caps(True, True, True, False),
    }
)

LANGUAGE_DISPLAY_NAMES: Final[Mapping[LanguageCode, str]] = MappingProxyType(
    {
        LanguageCode.ENGLISH: "English",
        LanguageCode.HINDI: "हिन्दी",
        LanguageCode.HINGLISH: "Hinglish",
        LanguageCode.ODIA: "ଓଡ଼ିଆ",
        LanguageCode.BENGALI: "বাংলা",
        LanguageCode.TAMIL: "தமிழ்",
        LanguageCode.TELUGU: "తెలుగు",
        LanguageCode.MARATHI: "मराठी",
        LanguageCode.GUJARATI: "ગુજરાતી",
        LanguageCode.KANNADA: "ಕನ್ನಡ",
        LanguageCode.MALAYALAM: "മലയാളം",
        LanguageCode.PUNJABI: "ਪੰਜਾਬੀ",
        LanguageCode.URDU: "اردو",
        LanguageCode.SPANISH: "Español",
        LanguageCode.FRENCH: "Français",
        LanguageCode.GERMAN: "Deutsch",
        LanguageCode.CHINESE: "中文",
        LanguageCode.JAPANESE: "日本語",
        LanguageCode.UNKNOWN: "Unknown",
    }
)


class LanguageConfidence(str, Enum):
    """Confidence band produced by the Language Decision Engine."""

    VERY_HIGH = "very_high"     
    LIKELY = "likely"           
    MIXED = "mixed"             
    UNKNOWN = "unknown"       

CONFIDENCE_VERY_HIGH: Final[float] = 0.90
CONFIDENCE_LIKELY: Final[float] = 0.70
CONFIDENCE_MIXED: Final[float] = 0.50


def classify_confidence(score: float) -> LanguageConfidence:
    """Map a detection confidence score to its FG4 confidence band."""
    if score > CONFIDENCE_VERY_HIGH:
        return LanguageConfidence.VERY_HIGH
    if score >= CONFIDENCE_LIKELY:
        return LanguageConfidence.LIKELY
    if score >= CONFIDENCE_MIXED:
        return LanguageConfidence.MIXED
    return LanguageConfidence.UNKNOWN

class LanguagePolicyMode(str, Enum):
    """How the assistant chooses its reply language."""

    ADMIN = "admin"      
    NORMAL = "normal"     
    SMART = "smart"      
DEFAULT_POLICY_MODE: Final[LanguagePolicyMode] = LanguagePolicyMode.SMART

class ConversationStyle(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    MIXED = "mixed"

def capabilities_for(language: LanguageCode) -> LanguageCapabilities:
    return LANGUAGE_CAPABILITIES.get(
        language, LanguageCapabilities(False, False, False, False)
    )


def supports_stt(language: LanguageCode) -> bool:
    return capabilities_for(language).stt


def supports_tts(language: LanguageCode) -> bool:
    return capabilities_for(language).tts


def supports_translation(language: LanguageCode) -> bool:
    return capabilities_for(language).translation


def supports_emotion(language: LanguageCode) -> bool:
    return capabilities_for(language).emotion


def display_name(language: LanguageCode) -> str:
    return LANGUAGE_DISPLAY_NAMES.get(language, language.value)


def is_supported(code: str) -> bool:
    return code in {lang.value for lang in LanguageCode if lang is not LanguageCode.UNKNOWN}

__all__ = [
    "LanguageCode",
    "DEFAULT_LANGUAGE",
    "PRIMARY_LANGUAGES",
    "CODE_MIXED_LANGUAGES",
    "LanguageCapabilities",
    "LANGUAGE_CAPABILITIES",
    "LANGUAGE_DISPLAY_NAMES",
    "LanguageConfidence",
    "CONFIDENCE_VERY_HIGH",
    "CONFIDENCE_LIKELY",
    "CONFIDENCE_MIXED",
    "classify_confidence",
    "LanguagePolicyMode",
    "DEFAULT_POLICY_MODE",
    "ConversationStyle",
    "capabilities_for",
    "supports_stt",
    "supports_tts",
    "supports_translation",
    "supports_emotion",
    "display_name",
    "is_supported",
]
