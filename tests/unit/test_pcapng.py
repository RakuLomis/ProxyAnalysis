from __future__ import annotations

from io import BytesIO
import struct

from proxy_analysis.parsing.pcapng import PcapNgReader


def _option(code: int, value: bytes) -> bytes:
    padding = b"\x00" * ((-len(value)) % 4)
    return struct.pack("<HH", code, len(value)) + value + padding


def _block(block_type: int, body: bytes) -> bytes:
    length = 12 + len(body)
    assert length % 4 == 0
    return struct.pack("<II", block_type, length) + body + struct.pack("<I", length)


def _capture() -> bytes:
    section_body = struct.pack("<IHHq", 0x1A2B3C4D, 1, 0, -1)
    section = _block(0x0A0D0D0A, section_body)
    options = _option(2, b"Meta") + _option(9, b"\x09") + _option(0, b"")
    interface = _block(1, struct.pack("<HHI", 101, 0, 262144) + options)
    packet = b"\x45" + b"\x00" * 19
    epb_body = struct.pack("<IIIII", 0, 0, 123456789, len(packet), len(packet))
    epb_body += packet + b"\x00" * ((-len(packet)) % 4)
    packet_block = _block(6, epb_body)
    return section + interface + packet_block


def test_pcapng_preserves_integer_nanoseconds_and_interface() -> None:
    reader = PcapNgReader(BytesIO(_capture()))
    records = list(reader)
    assert len(records) == 1
    assert records[0].timestamp_ns == 123456789
    assert records[0].link_type == 101
    assert records[0].captured_len == 20
    assert reader.interfaces[0].name == "Meta"
    assert reader.interfaces[0].timestamp_units_per_second == 1_000_000_000

