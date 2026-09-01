from __future__ import annotations

import ipaddress
import struct

from proxy_analysis.parsing.packet_decoder import DLT_EN10MB, DLT_RAW, decode_packet


def _ipv4_tcp(payload: bytes = b"hello", flags: int = 0x018) -> bytes:
    tcp = struct.pack("!HHIIHHHH", 12345, 443, 100, 200, (5 << 12) | flags, 4096, 0, 0)
    total_len = 20 + len(tcp) + len(payload)
    ip = struct.pack(
        "!BBHHHBBH4s4s",
        0x45,
        0,
        total_len,
        1,
        0,
        64,
        6,
        0,
        ipaddress.IPv4Address("192.0.2.1").packed,
        ipaddress.IPv4Address("198.51.100.2").packed,
    )
    return ip + tcp + payload


def test_decode_raw_ipv4_tcp_fields() -> None:
    parsed = decode_packet(DLT_RAW, _ipv4_tcp())
    assert parsed.decode_status == "ok"
    assert parsed.ip_src == "192.0.2.1"
    assert parsed.src_port == 12345
    assert parsed.dst_port == 443
    assert parsed.transport_payload_len == 5
    assert parsed.tcp_flags_raw == 0x018
    assert parsed.tcp_window_raw == 4096


def test_ethernet_length_does_not_change_ip_or_transport_lengths() -> None:
    packet = _ipv4_tcp(b"abc")
    ethernet = b"\x00" * 12 + struct.pack("!H", 0x0800) + packet
    raw = decode_packet(DLT_RAW, packet)
    framed = decode_packet(DLT_EN10MB, ethernet)
    assert framed.ip_total_len == raw.ip_total_len
    assert framed.transport_payload_len == raw.transport_payload_len == 3


def test_non_initial_fragment_is_not_decoded_as_tcp() -> None:
    packet = bytearray(_ipv4_tcp())
    packet[6:8] = struct.pack("!H", 1)
    parsed = decode_packet(DLT_RAW, bytes(packet))
    assert parsed.decode_status == "ip_only"
    assert parsed.decode_reason == "non_initial_fragment"
    assert parsed.transport_protocol is None

