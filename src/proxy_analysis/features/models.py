"""Minimal immutable packet values consumed by feature code."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PacketMeasure:
    packet_event_id: str
    timestamp_ns: int
    packet_ordinal: int
    direction: int
    transport_payload_len: int
    ip_total_len: int
    captured_len: int
    tcp_classification: str | None = None

    def __post_init__(self) -> None:
        if self.direction not in (-1, 1):
            raise ValueError("PacketMeasure direction must be +1 or -1")
        if min(self.transport_payload_len, self.ip_total_len, self.captured_len) < 0:
            raise ValueError("packet lengths must be non-negative")


def ordered_packets(packets: list[PacketMeasure] | tuple[PacketMeasure, ...]) -> list[PacketMeasure]:
    return sorted(packets, key=lambda item: (item.timestamp_ns, item.packet_ordinal))

