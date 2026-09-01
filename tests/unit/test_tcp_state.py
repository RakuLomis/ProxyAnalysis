from proxy_analysis.sequences.tcp_state import (
    SEQ_MODULUS,
    SequenceUnwrapper,
    TcpPacket,
    analyze_tcp_flow,
)


def packet(
    event_id: str,
    ts: int,
    ordinal: int,
    direction: int,
    seq: int,
    *,
    ack: int = 0,
    flags: int = 0,
    payload: int = 0,
) -> TcpPacket:
    return TcpPacket(event_id, ts, ordinal, direction, seq, ack, flags, payload)


def test_sequence_unwrap_crosses_32_bit_boundary() -> None:
    unwrapper = SequenceUnwrapper()
    assert unwrapper.unwrap(SEQ_MODULUS - 5) == SEQ_MODULUS - 5
    assert unwrapper.unwrap(3) == SEQ_MODULUS + 3


def test_retransmission_partial_overlap_and_out_of_order() -> None:
    packets = [
        packet("a", 1, 1, 1, 100, payload=10),
        packet("gap", 2, 2, 1, 120, payload=10),
        packet("late", 3, 3, 1, 110, payload=10),
        packet("full", 4, 4, 1, 100, payload=10),
        packet("partial", 5, 5, 1, 125, payload=10),
    ]
    result = analyze_tcp_flow(packets)
    assert [item.classification for item in result.segments] == [
        "new_data",
        "new_data",
        "out_of_order_or_late",
        "full_retransmission",
        "partial_retransmission",
    ]
    assert result.segments[-1].new_payload_bytes == 5
    assert result.segments[-1].retransmitted_payload_bytes == 5


def test_ack_rtt_for_handshake_and_data() -> None:
    packets = [
        packet("syn", 0, 1, 1, 100, flags=0x002),
        packet("synack", 10, 2, -1, 500, ack=101, flags=0x012),
        packet("ack", 20, 3, 1, 101, ack=501, flags=0x010),
        packet("data", 30, 4, 1, 101, ack=501, flags=0x018, payload=100),
        packet("data-ack", 80, 5, -1, 501, ack=201, flags=0x010),
    ]
    result = analyze_tcp_flow(packets)
    assert [(sample.kind, sample.rtt_ns) for sample in result.rtt_samples] == [
        ("syn", 10),
        ("syn", 10),
        ("data", 50),
    ]


def test_karn_rule_suppresses_retransmitted_range_rtt() -> None:
    packets = [
        packet("data", 0, 1, 1, 100, payload=10),
        packet("retry", 50, 2, 1, 100, payload=10),
        packet("ack", 100, 3, -1, 900, ack=110, flags=0x010),
    ]
    result = analyze_tcp_flow(packets)
    assert result.full_retransmission_count == 1
    assert result.rtt_samples == ()

