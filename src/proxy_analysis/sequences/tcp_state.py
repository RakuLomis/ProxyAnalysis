"""Project-owned TCP sequence, retransmission, ordering, and RTT analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal


SEQ_MODULUS = 1 << 32
SEQ_HALF = 1 << 31
TCP_FIN = 0x001
TCP_SYN = 0x002
TCP_ACK = 0x010

SegmentClass = Literal[
    "control_only",
    "new_data",
    "full_retransmission",
    "partial_retransmission",
    "out_of_order_or_late",
]


@dataclass(frozen=True, slots=True)
class TcpPacket:
    packet_event_id: str
    timestamp_ns: int
    packet_ordinal: int
    direction: int
    seq: int
    ack: int
    flags: int
    payload_len: int
    window_raw: int = 0
    options_raw: bytes = b""

    def __post_init__(self) -> None:
        if self.direction not in (-1, 1):
            raise ValueError("TCP packet direction must be +1 or -1")
        if not 0 <= self.seq < SEQ_MODULUS or not 0 <= self.ack < SEQ_MODULUS:
            raise ValueError("TCP seq/ack must be unsigned 32-bit values")
        if self.payload_len < 0:
            raise ValueError("TCP payload_len must be non-negative")


@dataclass(frozen=True, slots=True)
class TcpSegmentAnalysis:
    packet_event_id: str
    direction: int
    seq_start_unwrapped: int
    seq_end_unwrapped: int
    sequence_space_len: int
    classification: SegmentClass
    observed_payload_bytes: int
    new_payload_bytes: int
    retransmitted_payload_bytes: int


@dataclass(frozen=True, slots=True)
class RttSample:
    ack_packet_event_id: str
    acknowledged_packet_event_id: str
    sent_direction: int
    kind: str
    rtt_ns: int


@dataclass(frozen=True, slots=True)
class TcpFlowAnalysis:
    segments: tuple[TcpSegmentAnalysis, ...]
    rtt_samples: tuple[RttSample, ...]

    @property
    def full_retransmission_count(self) -> int:
        return sum(item.classification == "full_retransmission" for item in self.segments)

    @property
    def partial_retransmission_count(self) -> int:
        return sum(item.classification == "partial_retransmission" for item in self.segments)

    @property
    def out_of_order_count(self) -> int:
        return sum(item.classification == "out_of_order_or_late" for item in self.segments)


class SequenceUnwrapper:
    """Map serial-number-space values to the closest signed 64-bit epoch."""

    def __init__(self) -> None:
        self.reference: int | None = None

    def unwrap(self, value: int, *, update: bool = True) -> int:
        if not 0 <= value < SEQ_MODULUS:
            raise ValueError("sequence value must be unsigned 32-bit")
        if self.reference is None:
            result = value
        else:
            base = self.reference & ~(SEQ_MODULUS - 1)
            result = base | value
            if result - self.reference > SEQ_HALF:
                result -= SEQ_MODULUS
            elif self.reference - result > SEQ_HALF:
                result += SEQ_MODULUS
        if update and (self.reference is None or result > self.reference):
            self.reference = result
        return result


class IntervalSet:
    """Small sorted union of half-open integer intervals."""

    def __init__(self) -> None:
        self.intervals: list[tuple[int, int]] = []

    @property
    def max_end(self) -> int | None:
        return self.intervals[-1][1] if self.intervals else None

    def covered_length(self, start: int, end: int) -> int:
        if end <= start:
            return 0
        covered = 0
        for left, right in self.intervals:
            if right <= start:
                continue
            if left >= end:
                break
            covered += max(0, min(right, end) - max(left, start))
        return covered

    def add(self, start: int, end: int) -> None:
        if end <= start:
            return
        merged: list[tuple[int, int]] = []
        inserted = False
        for left, right in self.intervals:
            if right < start:
                merged.append((left, right))
            elif end < left:
                if not inserted:
                    merged.append((start, end))
                    inserted = True
                merged.append((left, right))
            else:
                start = min(start, left)
                end = max(end, right)
        if not inserted:
            merged.append((start, end))
        self.intervals = merged


@dataclass(slots=True)
class _DirectionState:
    unwrapper: SequenceUnwrapper
    sequence_seen: IntervalSet
    payload_seen: IntervalSet


@dataclass(slots=True)
class _Outstanding:
    packet_event_id: str
    start: int
    end: int
    sent_ns: int
    kind: str
    ambiguous: bool = False


def _segment_length(packet: TcpPacket) -> int:
    return packet.payload_len + bool(packet.flags & TCP_SYN) + bool(packet.flags & TCP_FIN)


def _payload_interval(packet: TcpPacket, seq_start: int) -> tuple[int, int]:
    payload_start = seq_start + bool(packet.flags & TCP_SYN)
    return payload_start, payload_start + packet.payload_len


def _classify_segment(packet: TcpPacket, state: _DirectionState) -> TcpSegmentAnalysis:
    seq_start = state.unwrapper.unwrap(packet.seq)
    seq_len = _segment_length(packet)
    seq_end = seq_start + seq_len
    previous_max = state.sequence_seen.max_end
    sequence_covered = state.sequence_seen.covered_length(seq_start, seq_end)
    payload_start, payload_end = _payload_interval(packet, seq_start)
    payload_covered = state.payload_seen.covered_length(payload_start, payload_end)

    if seq_len == 0:
        classification: SegmentClass = "control_only"
    elif sequence_covered == seq_len:
        classification = "full_retransmission"
    elif sequence_covered > 0:
        classification = "partial_retransmission"
    elif previous_max is not None and seq_start < previous_max:
        classification = "out_of_order_or_late"
    else:
        classification = "new_data"

    state.sequence_seen.add(seq_start, seq_end)
    state.payload_seen.add(payload_start, payload_end)
    return TcpSegmentAnalysis(
        packet_event_id=packet.packet_event_id,
        direction=packet.direction,
        seq_start_unwrapped=seq_start,
        seq_end_unwrapped=seq_end,
        sequence_space_len=seq_len,
        classification=classification,
        observed_payload_bytes=packet.payload_len,
        new_payload_bytes=packet.payload_len - payload_covered,
        retransmitted_payload_bytes=payload_covered,
    )


def analyze_tcp_flow(packets: Iterable[TcpPacket]) -> TcpFlowAnalysis:
    """Analyze one bidirectional TCP entity using only raw header fields."""
    ordered = sorted(packets, key=lambda item: (item.timestamp_ns, item.packet_ordinal))
    states = {
        1: _DirectionState(SequenceUnwrapper(), IntervalSet(), IntervalSet()),
        -1: _DirectionState(SequenceUnwrapper(), IntervalSet(), IntervalSet()),
    }
    outstanding: dict[int, list[_Outstanding]] = {1: [], -1: []}
    segments: list[TcpSegmentAnalysis] = []
    rtt_samples: list[RttSample] = []

    for packet in ordered:
        # ACKs refer to sequence space in the opposite direction.
        if packet.flags & TCP_ACK:
            sent_direction = -packet.direction
            ack_unwrapper = states[sent_direction].unwrapper
            if ack_unwrapper.reference is not None:
                ack_value = ack_unwrapper.unwrap(packet.ack, update=False)
                newly_acked = [
                    item for item in outstanding[sent_direction] if item.end <= ack_value
                ]
                if newly_acked:
                    sample_candidate = next(
                        (item for item in newly_acked if not item.ambiguous), None
                    )
                    if sample_candidate is not None and packet.timestamp_ns >= sample_candidate.sent_ns:
                        rtt_samples.append(
                            RttSample(
                                ack_packet_event_id=packet.packet_event_id,
                                acknowledged_packet_event_id=sample_candidate.packet_event_id,
                                sent_direction=sent_direction,
                                kind=sample_candidate.kind,
                                rtt_ns=packet.timestamp_ns - sample_candidate.sent_ns,
                            )
                        )
                    acknowledged_ids = {id(item) for item in newly_acked}
                    outstanding[sent_direction] = [
                        item
                        for item in outstanding[sent_direction]
                        if id(item) not in acknowledged_ids
                    ]

        analysis = _classify_segment(packet, states[packet.direction])
        segments.append(analysis)
        if analysis.sequence_space_len == 0:
            continue

        if analysis.classification in ("full_retransmission", "partial_retransmission"):
            for item in outstanding[packet.direction]:
                if item.start < analysis.seq_end_unwrapped and analysis.seq_start_unwrapped < item.end:
                    item.ambiguous = True

        # Conservative Karn behavior: only an entirely new range starts an RTT timer.
        if analysis.classification in ("new_data", "out_of_order_or_late"):
            kind = "syn" if packet.flags & TCP_SYN else "fin" if packet.flags & TCP_FIN else "data"
            outstanding[packet.direction].append(
                _Outstanding(
                    packet_event_id=packet.packet_event_id,
                    start=analysis.seq_start_unwrapped,
                    end=analysis.seq_end_unwrapped,
                    sent_ns=packet.timestamp_ns,
                    kind=kind,
                )
            )

    return TcpFlowAnalysis(tuple(segments), tuple(rtt_samples))
