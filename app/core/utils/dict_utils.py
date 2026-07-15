from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def deep_merge(base: dict[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, overlay_value in overlay.items():
        base_value = result.get(key)
        if isinstance(base_value, dict) and isinstance(overlay_value, Mapping):
            result[key] = deep_merge(base_value, dict(overlay_value))
        else:
            result[key] = deepcopy(overlay_value)
    return result


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))


def within(value: int, high: int, low: int = 0) -> bool:
    return low <= value <= high
