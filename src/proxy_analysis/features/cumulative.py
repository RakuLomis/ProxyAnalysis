"""Fixed-grid cumulative traffic shapes using previous/step interpolation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

import numpy as np

from .models import PacketMeasure, ordered_packets


@dataclass(frozen=True, slots=True)
class CumulativeShape:
    axis: str
    grid: tuple[float, ...]
    signed_transport_bytes: tuple[float, ...]
    absolute_transport_bytes: tuple[float, ...]
    up_transport_bytes: tuple[float, ...]
    down_transport_bytes: tuple[float, ...]


def cumulative_shape(
    packets: Iterable[PacketMeasure],
    *,
    axis: Literal["normalized_time", "normalized_packet_index"],
    grid_points: int = 101,
) -> CumulativeShape:
    if grid_points < 2:
        raise ValueError("grid_points must be >= 2")
    values = ordered_packets(tuple(packets))
    grid = np.linspace(0.0, 1.0, grid_points)
    if not values:
        zeros = tuple(float(0) for _ in grid)
        return CumulativeShape(axis, tuple(grid), zeros, zeros, zeros, zeros)

    if axis == "normalized_packet_index":
        coordinates = np.arange(1, len(values) + 1, dtype=np.float64) / len(values)
    elif axis == "normalized_time":
        first = values[0].timestamp_ns
        duration = values[-1].timestamp_ns - first
        if duration == 0:
            coordinates = np.zeros(len(values), dtype=np.float64)
        else:
            coordinates = np.asarray(
                [(item.timestamp_ns - first) / duration for item in values], dtype=np.float64
            )
    else:
        raise ValueError(f"unsupported cumulative axis: {axis}")

    payload = np.asarray([item.transport_payload_len for item in values], dtype=np.float64)
    direction = np.asarray([item.direction for item in values], dtype=np.float64)
    curves = (
        np.cumsum(payload * direction),
        np.cumsum(payload),
        np.cumsum(payload * (direction == 1)),
        np.cumsum(payload * (direction == -1)),
    )
    positions = np.searchsorted(coordinates, grid, side="right") - 1

    def sample(curve: np.ndarray) -> tuple[float, ...]:
        return tuple(float(curve[index]) if index >= 0 else 0.0 for index in positions)

    return CumulativeShape(
        axis,
        tuple(float(item) for item in grid),
        sample(curves[0]),
        sample(curves[1]),
        sample(curves[2]),
        sample(curves[3]),
    )

