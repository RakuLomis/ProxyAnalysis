import struct

from proxy_analysis.features.tcp_transport import tcp_transport_features
from proxy_analysis.parsing.tcp_options import parse_tcp_options, tcp_option_values
from proxy_analysis.sequences.tcp_state import TcpPacket


def test_tcp_option_parser_reads_mss_scale_sack_and_timestamps() -> None:
    raw = (
        b"\x02\x04" + struct.pack("!H", 1460)
        + b"\x01"
        + b"\x03\x03\x07"
        + b"\x04\x02"
        + b"\x08\x0a" + struct.pack("!II", 10, 20)
        + b"\x00"
    )
    parsed = parse_tcp_options(raw)
    assert all(item.valid for item in parsed)
    values = tcp_option_values(raw)
    assert values["mss"] == 1460
    assert values["window_scale"] == 7
    assert values["sack_permitted"] is True
    assert values["timestamps"] == (10, 20)


def test_tcp_transport_complete_handshake_and_scaled_windows() -> None:
    ws7 = b"\x03\x03\x07\x00"
    ws8 = b"\x03\x03\x08\x00"
    packets = [
        TcpPacket("syn", 0, 1, 1, 100, 0, 0x002, 0, 1000, ws7),
        TcpPacket("synack", 10, 2, -1, 500, 101, 0x012, 0, 2000, ws8),
        TcpPacket("ack", 20, 3, 1, 101, 501, 0x010, 0, 100, b""),
        TcpPacket("data", 30, 4, 1, 101, 501, 0x018, 10, 50, b""),
        TcpPacket("reply", 50, 5, -1, 501, 111, 0x018, 5, 60, b""),
    ]
    result = tcp_transport_features(packets)
    assert result["handshake"]["complete"] is True
    assert result["handshake"]["syn_to_synack_ns"] == 10
    assert result["effective_window"]["negotiated"] is True
    assert result["effective_window"]["up"]["max"] == 100 * (1 << 7)
    assert result["effective_window"]["down"]["max"] == 60 * (1 << 8)


def test_incomplete_handshake_does_not_invent_scaled_window() -> None:
    result = tcp_transport_features(
        [TcpPacket("midstream", 0, 1, 1, 100, 200, 0x010, 0, 1234, b"")]
    )
    assert result["handshake"]["complete"] is False
    assert result["effective_window"]["negotiated"] is False
    assert result["effective_window"]["up"]["count"] is None

