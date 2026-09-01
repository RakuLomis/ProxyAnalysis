"""TCP flags, advertised windows, raw options, and statistical handshake features."""

from __future__ import annotations

from typing import Iterable

from ..parsing.tcp_options import tcp_option_values
from ..sequences.tcp_state import TCP_ACK, TCP_FIN, TCP_SYN, TcpPacket
from .distribution import distribution_summary


FLAG_BITS = {
    "fin": 0x001,
    "syn": 0x002,
    "rst": 0x004,
    "psh": 0x008,
    "ack": 0x010,
    "urg": 0x020,
    "ece": 0x040,
    "cwr": 0x080,
    "ns": 0x100,
}


def _ordered(packets: Iterable[TcpPacket]) -> list[TcpPacket]:
    return sorted(packets, key=lambda item: (item.timestamp_ns, item.packet_ordinal))


def _flight(group: list[TcpPacket]) -> dict[str, int]:
    return {
        "direction": group[0].direction,
        "packet_count": len(group),
        "payload_bytes": sum(item.payload_len for item in group),
        "duration_ns": group[-1].timestamp_ns - group[0].timestamp_ns,
    }


def tcp_transport_features(packets: Iterable[TcpPacket]) -> dict[str, object]:
    values = _ordered(packets)
    if not values:
        return {"applicable": False, "reason": "empty_sequence"}

    flag_counts = {
        name: sum(bool(packet.flags & bit) for packet in values)
        for name, bit in FLAG_BITS.items()
    }
    by_direction = {1: [item for item in values if item.direction == 1], -1: [item for item in values if item.direction == -1]}

    initiator_syn = next(
        (item for item in values if item.direction == 1 and item.flags & TCP_SYN and not item.flags & TCP_ACK),
        None,
    )
    responder_synack = next(
        (
            item
            for item in values
            if initiator_syn is not None
            and item.timestamp_ns >= initiator_syn.timestamp_ns
            and item.direction == -1
            and item.flags & TCP_SYN
            and item.flags & TCP_ACK
            and item.ack == ((initiator_syn.seq + 1) & 0xFFFFFFFF)
        ),
        None,
    )
    final_ack = next(
        (
            item
            for item in values
            if responder_synack is not None
            and item.timestamp_ns >= responder_synack.timestamp_ns
            and item.direction == 1
            and item.flags & TCP_ACK
            and not item.flags & TCP_SYN
            and item.ack == ((responder_synack.seq + 1) & 0xFFFFFFFF)
        ),
        None,
    )

    syn_options = {
        "initiator": tcp_option_values(initiator_syn.options_raw) if initiator_syn else None,
        "responder": tcp_option_values(responder_synack.options_raw) if responder_synack else None,
    }
    scales: dict[int, int | None] = {1: None, -1: None}
    if syn_options["initiator"] is not None and syn_options["responder"] is not None:
        init_scale = syn_options["initiator"].get("window_scale")
        resp_scale = syn_options["responder"].get("window_scale")
        if isinstance(init_scale, int) and isinstance(resp_scale, int):
            if 0 <= init_scale <= 14 and 0 <= resp_scale <= 14:
                scales = {1: init_scale, -1: resp_scale}

    effective_by_direction: dict[int, list[int]] = {1: [], -1: []}
    if scales[1] is not None and scales[-1] is not None:
        for packet in values:
            if not packet.flags & TCP_SYN:
                scale = scales[packet.direction]
                assert scale is not None
                effective_by_direction[packet.direction].append(packet.window_raw << scale)

    start = next((item for item in values if item.direction == 1), values[0])
    reverse = next(
        (item for item in values if item.direction == -1 and item.timestamp_ns >= start.timestamp_ns),
        None,
    )
    nonempty_reverse = next(
        (
            item
            for item in values
            if item.direction == -1
            and item.payload_len > 0
            and item.timestamp_ns >= start.timestamp_ns
        ),
        None,
    )

    groups: list[list[TcpPacket]] = [[values[0]]]
    for packet in values[1:]:
        if packet.direction == groups[-1][-1].direction:
            groups[-1].append(packet)
        else:
            groups.append([packet])

    return {
        "applicable": True,
        "packet_count": len(values),
        "flag_counts": flag_counts,
        "raw_window": {
            "all": distribution_summary(item.window_raw for item in values),
            "up": distribution_summary(item.window_raw for item in by_direction[1]),
            "down": distribution_summary(item.window_raw for item in by_direction[-1]),
            "zero_window_count": sum(
                item.window_raw == 0 and bool(item.flags & TCP_ACK) for item in values
            ),
        },
        "effective_window": {
            "negotiated": scales[1] is not None and scales[-1] is not None,
            "initiator_scale": scales[1],
            "responder_scale": scales[-1],
            "up": distribution_summary(effective_by_direction[1]),
            "down": distribution_summary(effective_by_direction[-1]),
        },
        "handshake": {
            "complete": all(item is not None for item in (initiator_syn, responder_synack, final_ack)),
            "syn_to_synack_ns": (
                responder_synack.timestamp_ns - initiator_syn.timestamp_ns
                if initiator_syn and responder_synack
                else None
            ),
            "syn_to_final_ack_ns": (
                final_ack.timestamp_ns - initiator_syn.timestamp_ns
                if initiator_syn and final_ack
                else None
            ),
            "first_reverse_ns": reverse.timestamp_ns - start.timestamp_ns if reverse else None,
            "first_nonempty_reverse_ns": (
                nonempty_reverse.timestamp_ns - start.timestamp_ns if nonempty_reverse else None
            ),
            "syn_options": syn_options,
            "first_flight": _flight(groups[0]),
            "second_flight": _flight(groups[1]) if len(groups) > 1 else None,
        },
    }

