"""Deterministic entity direction and IAT enrichment."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Endpoint:
    ip: str
    port: int | None = None

    def matches(self, ip: str | None, port: int | None) -> bool:
        return ip == self.ip and (self.port is None or port == self.port)


@dataclass(frozen=True, slots=True)
class SequenceEvent:
    packet_event_id: str
    timestamp_ns: int
    packet_ordinal: int
    ip_src: str | None
    ip_dst: str | None
    src_port: int | None
    dst_port: int | None
    direction: int | None = None
    relative_time_ns: int | None = None
    packet_iat_ns: int | None = None


def packet_direction(
    event: SequenceEvent, initiator: Endpoint, responder: Endpoint
) -> int | None:
    if initiator.matches(event.ip_src, event.src_port) and responder.matches(
        event.ip_dst, event.dst_port
    ):
        return 1
    if responder.matches(event.ip_src, event.src_port) and initiator.matches(
        event.ip_dst, event.dst_port
    ):
        return -1
    # Non-initial IP fragments do not carry transport ports. Once a packet is
    # bound to an indexed entity capture, endpoint IPs are sufficient to retain
    # direction without asking a dissector to reassemble the datagram.
    if event.src_port is None and event.dst_port is None:
        if event.ip_src == initiator.ip and event.ip_dst == responder.ip:
            return 1
        if event.ip_src == responder.ip and event.ip_dst == initiator.ip:
            return -1
    return None


def enrich_sequence(
    events: Iterable[SequenceEvent], initiator: Endpoint, responder: Endpoint
) -> list[SequenceEvent]:
    """Stable-sort and add entity-global direction, relative time, and IAT."""
    ordered = sorted(events, key=lambda item: (item.timestamp_ns, item.packet_ordinal))
    if not ordered:
        return []
    first_timestamp = ordered[0].timestamp_ns
    previous_timestamp: int | None = None
    enriched: list[SequenceEvent] = []
    for event in ordered:
        iat = None if previous_timestamp is None else event.timestamp_ns - previous_timestamp
        if iat is not None and iat < 0:
            raise AssertionError("stable timestamp ordering produced a negative IAT")
        enriched.append(
            replace(
                event,
                direction=packet_direction(event, initiator, responder),
                relative_time_ns=event.timestamp_ns - first_timestamp,
                packet_iat_ns=iat,
            )
        )
        previous_timestamp = event.timestamp_ns
    return enriched
