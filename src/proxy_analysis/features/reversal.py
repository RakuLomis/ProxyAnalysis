"""Flow Reversals from non-empty packet direction runs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import PacketMeasure


@dataclass(frozen=True, slots=True)
class ReversalFeatures:
    nonempty_packet_count: int
    payload_bytes: int
    duration_ns: int | None
    fr_runs: int
    fr_reversals: int
    fr_norm_packets: float | None
    fr_per_second: float | None
    fr_per_kib: float | None


def reversal_features(
    packets: Iterable[PacketMeasure], *, unique_seq: bool = False
) -> ReversalFeatures:
    selected = [
        item
        for item in packets
        if item.transport_payload_len > 0
        and not (unique_seq and item.tcp_classification == "full_retransmission")
    ]
    selected.sort(key=lambda item: (item.timestamp_ns, item.packet_ordinal))
    count = len(selected)
    payload_bytes = sum(item.transport_payload_len for item in selected)
    if count == 0:
        return ReversalFeatures(0, 0, None, 0, 0, None, None, None)
    reversals = sum(
        current.direction != previous.direction
        for previous, current in zip(selected, selected[1:])
    )
    duration_ns = selected[-1].timestamp_ns - selected[0].timestamp_ns
    return ReversalFeatures(
        nonempty_packet_count=count,
        payload_bytes=payload_bytes,
        duration_ns=duration_ns,
        fr_runs=1 + reversals,
        fr_reversals=reversals,
        fr_norm_packets=reversals / (count - 1) if count > 1 else None,
        fr_per_second=(reversals * 1_000_000_000 / duration_ns) if duration_ns > 0 else None,
        fr_per_kib=(reversals / (payload_bytes / 1024)) if payload_bytes > 0 else None,
    )

