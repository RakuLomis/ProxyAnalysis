"""Direction-run and time-gap burst definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import PacketMeasure, ordered_packets


@dataclass(frozen=True, slots=True)
class Burst:
    direction: int
    start_ns: int
    end_ns: int
    duration_ns: int
    packet_count: int
    transport_payload_bytes: int
    ip_bytes: int


def _make_burst(group: list[PacketMeasure]) -> Burst:
    return Burst(
        direction=group[0].direction,
        start_ns=group[0].timestamp_ns,
        end_ns=group[-1].timestamp_ns,
        duration_ns=group[-1].timestamp_ns - group[0].timestamp_ns,
        packet_count=len(group),
        transport_payload_bytes=sum(item.transport_payload_len for item in group),
        ip_bytes=sum(item.ip_total_len for item in group),
    )


def direction_run_bursts(packets: Iterable[PacketMeasure]) -> list[Burst]:
    ordered = ordered_packets(tuple(packets))
    if not ordered:
        return []
    groups: list[list[PacketMeasure]] = [[ordered[0]]]
    for packet in ordered[1:]:
        if packet.direction == groups[-1][-1].direction:
            groups[-1].append(packet)
        else:
            groups.append([packet])
    return [_make_burst(group) for group in groups]


def time_gap_bursts(packets: Iterable[PacketMeasure], threshold_ns: int) -> list[Burst]:
    if threshold_ns < 0:
        raise ValueError("threshold_ns must be non-negative")
    ordered = ordered_packets(tuple(packets))
    if not ordered:
        return []
    groups: list[list[PacketMeasure]] = [[ordered[0]]]
    for packet in ordered[1:]:
        previous = groups[-1][-1]
        same_burst = (
            packet.direction == previous.direction
            and packet.timestamp_ns - previous.timestamp_ns <= threshold_ns
        )
        if same_burst:
            groups[-1].append(packet)
        else:
            groups.append([packet])
    return [_make_burst(group) for group in groups]

