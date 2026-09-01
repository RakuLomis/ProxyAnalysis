"""Half-open interval concurrency with deterministic boundary ordering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Interval:
    entity_id: str
    start_ns: int
    end_ns: int

    def __post_init__(self) -> None:
        if self.end_ns < self.start_ns:
            raise ValueError("interval end must be >= start")


@dataclass(frozen=True, slots=True)
class ConcurrencyFeatures:
    interval_count: int
    zero_duration_count: int
    max_active: int
    time_weighted_mean_active: float | None
    window_start_ns: int | None
    window_end_ns: int | None


def concurrency_features(intervals: Iterable[Interval]) -> ConcurrencyFeatures:
    values = list(intervals)
    if not values:
        return ConcurrencyFeatures(0, 0, 0, None, None, None)
    positive = [item for item in values if item.end_ns > item.start_ns]
    zero_count = len(values) - len(positive)
    if not positive:
        point = min(item.start_ns for item in values)
        return ConcurrencyFeatures(len(values), zero_count, 0, None, point, point)

    # end (-1) sorts before start (+1), implementing [start, end).
    events = sorted(
        [(item.start_ns, 1) for item in positive]
        + [(item.end_ns, -1) for item in positive],
        key=lambda item: (item[0], item[1]),
    )
    active = 0
    maximum = 0
    area = 0
    previous_time = events[0][0]
    index = 0
    while index < len(events):
        timestamp = events[index][0]
        area += active * (timestamp - previous_time)
        while index < len(events) and events[index][0] == timestamp:
            active += events[index][1]
            maximum = max(maximum, active)
            index += 1
        previous_time = timestamp
    start = events[0][0]
    end = events[-1][0]
    return ConcurrencyFeatures(
        interval_count=len(values),
        zero_duration_count=zero_count,
        max_active=maximum,
        time_weighted_mean_active=area / (end - start) if end > start else None,
        window_start_ns=start,
        window_end_ns=end,
    )

