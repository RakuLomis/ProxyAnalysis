"""Threshold-versioned active and idle periods."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import PacketMeasure, ordered_packets


@dataclass(frozen=True, slots=True)
class ActiveIdlePeriods:
    threshold_ns: int
    active_durations_ns: tuple[int, ...]
    idle_durations_ns: tuple[int, ...]


def active_idle_periods(
    packets: Iterable[PacketMeasure], threshold_ns: int
) -> ActiveIdlePeriods:
    if threshold_ns < 0:
        raise ValueError("threshold_ns must be non-negative")
    values = ordered_packets(tuple(packets))
    if not values:
        return ActiveIdlePeriods(threshold_ns, (), ())
    active_starts = [values[0].timestamp_ns]
    active_ends: list[int] = []
    idle: list[int] = []
    previous = values[0].timestamp_ns
    for packet in values[1:]:
        gap = packet.timestamp_ns - previous
        if gap > threshold_ns:
            active_ends.append(previous)
            idle.append(gap)
            active_starts.append(packet.timestamp_ns)
        previous = packet.timestamp_ns
    active_ends.append(previous)
    active = tuple(end - start for start, end in zip(active_starts, active_ends))
    return ActiveIdlePeriods(threshold_ns, active, tuple(idle))

