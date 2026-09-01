"""Directional packet and byte volume."""

from __future__ import annotations

import math
from typing import Iterable

from .models import PacketMeasure


def _normalized_difference(a: int, b: int) -> float | None:
    return (a - b) / (a + b) if a + b else None


def directional_volume(
    packets: Iterable[PacketMeasure], *, epsilon: float = 1.0
) -> dict[str, int | float | None]:
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    values = list(packets)
    up = [item for item in values if item.direction == 1]
    down = [item for item in values if item.direction == -1]
    result: dict[str, int | float | None] = {}
    for name, selected in (("up", up), ("down", down), ("total", values)):
        result[f"{name}_packets"] = len(selected)
        result[f"{name}_nonempty_packets"] = sum(
            item.transport_payload_len > 0 for item in selected
        )
        result[f"{name}_transport_bytes"] = sum(
            item.transport_payload_len for item in selected
        )
        result[f"{name}_ip_bytes"] = sum(item.ip_total_len for item in selected)
        result[f"{name}_captured_bytes"] = sum(item.captured_len for item in selected)
    for metric in ("packets", "transport_bytes", "ip_bytes", "captured_bytes"):
        a = int(result[f"up_{metric}"] or 0)
        b = int(result[f"down_{metric}"] or 0)
        result[f"{metric}_log_ratio"] = math.log((a + epsilon) / (b + epsilon))
        result[f"{metric}_normalized_difference"] = _normalized_difference(a, b)
    return result

