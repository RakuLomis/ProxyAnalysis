"""Connect an entity capture to direction/IAT and project-owned TCP analysis."""

from __future__ import annotations

from dataclasses import dataclass

from ..indexing.identities import EntityDescriptor
from ..parsing import PcapNgReader, decode_packet
from ..sequences.direction import SequenceEvent, enrich_sequence
from ..sequences.tcp_state import TcpFlowAnalysis, TcpPacket, analyze_tcp_flow
from ..features.models import PacketMeasure


@dataclass(frozen=True, slots=True)
class EntityAnalysis:
    descriptor: EntityDescriptor
    packet_count: int
    decoded_transport_count: int
    unknown_direction_count: int
    sequence_events: tuple[SequenceEvent, ...]
    packet_measures: tuple[PacketMeasure, ...]
    tcp_packets: tuple[TcpPacket, ...]
    tcp: TcpFlowAnalysis | None


def analyze_entity_capture(descriptor: EntityDescriptor) -> EntityAnalysis:
    raw_events: list[SequenceEvent] = []
    parsed_by_id = {}
    for record in PcapNgReader(descriptor.capture_path):
        parsed = decode_packet(record.link_type, record.packet_data)
        event_id = f"{descriptor.artifact_id}:{record.interface_id}:{record.packet_ordinal}"
        event = SequenceEvent(
            event_id,
            record.timestamp_ns,
            record.packet_ordinal,
            parsed.ip_src,
            parsed.ip_dst,
            parsed.src_port,
            parsed.dst_port,
        )
        raw_events.append(event)
        parsed_by_id[event_id] = (parsed, record.captured_len)

    events = enrich_sequence(raw_events, descriptor.initiator, descriptor.responder,
                             physical_paths=descriptor.physical_paths)
    tcp_packets: list[TcpPacket] = []
    decoded_transport_count = 0
    for event in events:
        parsed, _captured_len = parsed_by_id[event.packet_event_id]
        if parsed.transport_protocol is not None:
            decoded_transport_count += 1
        if (
            parsed.transport_protocol == "tcp"
            and event.direction in (-1, 1)
            and parsed.tcp_seq is not None
            and parsed.tcp_ack is not None
            and parsed.tcp_flags_raw is not None
            and parsed.transport_payload_len is not None
        ):
            tcp_packets.append(
                TcpPacket(
                    event.packet_event_id,
                    event.timestamp_ns,
                    event.packet_ordinal,
                    event.direction,
                    parsed.tcp_seq,
                    parsed.tcp_ack,
                    parsed.tcp_flags_raw,
                    parsed.transport_payload_len,
                    parsed.tcp_window_raw or 0,
                    parsed.tcp_options_raw or b"",
                )
            )
    tcp = analyze_tcp_flow(tcp_packets) if tcp_packets else None
    classifications = (
        {item.packet_event_id: item.classification for item in tcp.segments} if tcp else {}
    )
    measures: list[PacketMeasure] = []
    for event in events:
        parsed, captured_len = parsed_by_id[event.packet_event_id]
        if (
            event.direction in (-1, 1)
            and parsed.transport_payload_len is not None
            and parsed.ip_total_len is not None
        ):
            measures.append(
                PacketMeasure(
                    event.packet_event_id,
                    event.timestamp_ns,
                    event.packet_ordinal,
                    event.direction,
                    parsed.transport_payload_len,
                    parsed.ip_total_len,
                    captured_len,
                    classifications.get(event.packet_event_id),
                )
            )
    return EntityAnalysis(
        descriptor=descriptor,
        packet_count=len(events),
        decoded_transport_count=decoded_transport_count,
        unknown_direction_count=sum(event.direction is None for event in events),
        sequence_events=tuple(events),
        packet_measures=tuple(measures),
        tcp_packets=tuple(tcp_packets),
        tcp=tcp,
    )
