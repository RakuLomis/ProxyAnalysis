from __future__ import annotations

import ipaddress
from pathlib import Path
import struct

import pyarrow.parquet as pq

from proxy_analysis.pipeline.extract_packets import CaptureSource, write_packet_events


def _block(block_type: int, body: bytes) -> bytes:
    length = 12 + len(body)
    return struct.pack("<II", block_type, length) + body + struct.pack("<I", length)


def _pcapng(path: Path) -> None:
    shb = _block(0x0A0D0D0A, struct.pack("<IHHq", 0x1A2B3C4D, 1, 0, -1))
    end = struct.pack("<HH", 0, 0)
    idb = _block(1, struct.pack("<HHI", 101, 0, 262144) + end)
    tcp = struct.pack("!HHIIHHHH", 1000, 443, 1, 0, (5 << 12) | 2, 1024, 0, 0)
    total_len = 20 + len(tcp)
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
    ) + tcp
    epb_body = struct.pack("<IIIII", 0, 0, 10, len(ip), len(ip)) + ip
    epb_body += b"\x00" * ((-len(ip)) % 4)
    path.write_bytes(shb + idb + _block(6, epb_body))


def test_write_packet_events_produces_schema_conformant_parquet(tmp_path: Path) -> None:
    capture = tmp_path / "capture.pcap"
    output = tmp_path / "events.parquet"
    _pcapng(capture)
    source = CaptureSource("VLESS", "session-1", "artifact-1", capture, "pre")
    summary = write_packet_events(source, output)
    table = pq.read_table(output)
    assert summary == {"packet_count": 1, "decode_failed_count": 0}
    assert table.num_rows == 1
    assert table.column("timestamp_ns").to_pylist() == [10_000]
    assert table.column("transport_protocol").to_pylist() == ["tcp"]
    assert table.column("tcp_flags_raw").to_pylist() == [2]
    assert "payload" not in table.schema.names

