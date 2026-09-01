"""Integer-timestamp PCAPNG reader.

This intentionally does not use dpkt's Reader iterator because dpkt exposes a
floating-point timestamp and drops the Enhanced Packet Block interface id and
original length. No traffic feature is computed in this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct
from typing import BinaryIO, Iterator

from ..pathutils import filesystem_path


SECTION_HEADER = 0x0A0D0D0A
INTERFACE_DESCRIPTION = 0x00000001
PACKET_BLOCK = 0x00000002
SIMPLE_PACKET = 0x00000003
ENHANCED_PACKET = 0x00000006
BYTE_ORDER_MAGIC = 0x1A2B3C4D
OPTION_END = 0
OPTION_IF_NAME = 2
OPTION_IF_TSRESOL = 9
OPTION_IF_TSOFFSET = 14


class PcapNgError(RuntimeError):
    """Raised for malformed or unsupported PCAPNG content."""


@dataclass(frozen=True, slots=True)
class InterfaceDescription:
    section_index: int
    interface_id: int
    link_type: int
    snap_len: int
    name: str | None
    timestamp_units_per_second: int
    timestamp_offset_seconds: int


@dataclass(frozen=True, slots=True)
class CaptureRecord:
    section_index: int
    interface_id: int
    link_type: int
    packet_ordinal: int
    timestamp_ns: int
    captured_len: int
    original_len: int
    packet_data: bytes


class PcapNgReader:
    """Stream Enhanced Packet Blocks while preserving integer nanoseconds."""

    def __init__(self, source: Path | str | BinaryIO) -> None:
        self._source = source
        self.interfaces: list[InterfaceDescription] = []

    def __iter__(self) -> Iterator[CaptureRecord]:
        close_after = not hasattr(self._source, "read")
        stream = open(filesystem_path(Path(self._source)), "rb") if close_after else self._source
        try:
            yield from self._iter_stream(stream)  # type: ignore[arg-type]
        finally:
            if close_after:
                stream.close()  # type: ignore[union-attr]

    def _iter_stream(self, stream: BinaryIO) -> Iterator[CaptureRecord]:
        endian: str | None = None
        section_index = -1
        section_interfaces: list[InterfaceDescription] = []
        ordinal = 0
        while True:
            header = stream.read(8)
            if not header:
                return
            if len(header) != 8:
                raise PcapNgError("truncated block header")

            raw_type = header[:4]
            if raw_type == struct.pack("<I", SECTION_HEADER):
                prefix = stream.read(4)
                if len(prefix) != 4:
                    raise PcapNgError("truncated section byte-order magic")
                if prefix == struct.pack("<I", BYTE_ORDER_MAGIC):
                    endian = "<"
                elif prefix == struct.pack(">I", BYTE_ORDER_MAGIC):
                    endian = ">"
                else:
                    raise PcapNgError("invalid section byte-order magic")
                block_len = struct.unpack(endian + "I", header[4:8])[0]
                body_tail = stream.read(block_len - 12)
                _validate_block_length(block_len, prefix + body_tail, endian)
                section_index += 1
                section_interfaces = []
                continue

            if endian is None:
                raise PcapNgError("capture does not start with a section header")
            block_type, block_len = struct.unpack(endian + "II", header)
            if block_len < 12 or block_len % 4:
                raise PcapNgError(f"invalid block length: {block_len}")
            remainder = stream.read(block_len - 8)
            _validate_block_length(block_len, remainder, endian)
            body = remainder[:-4]

            if block_type == INTERFACE_DESCRIPTION:
                interface = _parse_interface(body, endian, section_index, len(section_interfaces))
                section_interfaces.append(interface)
                self.interfaces.append(interface)
            elif block_type == ENHANCED_PACKET:
                if len(body) < 20:
                    raise PcapNgError("truncated enhanced packet block")
                interface_id, ts_high, ts_low, cap_len, orig_len = struct.unpack(
                    endian + "IIIII", body[:20]
                )
                if interface_id >= len(section_interfaces):
                    raise PcapNgError(f"unknown interface id: {interface_id}")
                padded_cap_len = (cap_len + 3) & ~3
                if len(body) < 20 + padded_cap_len:
                    raise PcapNgError("truncated enhanced packet data")
                interface = section_interfaces[interface_id]
                ticks = (ts_high << 32) | ts_low
                timestamp_ns = (
                    interface.timestamp_offset_seconds * 1_000_000_000
                    + ticks * 1_000_000_000 // interface.timestamp_units_per_second
                )
                ordinal += 1
                yield CaptureRecord(
                    section_index=section_index,
                    interface_id=interface_id,
                    link_type=interface.link_type,
                    packet_ordinal=ordinal,
                    timestamp_ns=timestamp_ns,
                    captured_len=cap_len,
                    original_len=orig_len,
                    packet_data=body[20 : 20 + cap_len],
                )
            elif block_type in (PACKET_BLOCK, SIMPLE_PACKET):
                raise PcapNgError(
                    "legacy Packet Block/Simple Packet Block lacks the required event contract"
                )


def _validate_block_length(block_len: int, remainder: bytes, endian: str) -> None:
    if block_len < 12 or block_len % 4:
        raise PcapNgError(f"invalid block length: {block_len}")
    if len(remainder) != block_len - 8:
        raise PcapNgError("truncated block")
    trailer = struct.unpack(endian + "I", remainder[-4:])[0]
    if trailer != block_len:
        raise PcapNgError(f"block length trailer mismatch: {block_len} != {trailer}")


def _parse_options(data: bytes, endian: str) -> dict[int, list[bytes]]:
    options: dict[int, list[bytes]] = {}
    offset = 0
    while offset + 4 <= len(data):
        code, length = struct.unpack(endian + "HH", data[offset : offset + 4])
        offset += 4
        if code == OPTION_END:
            return options
        padded = (length + 3) & ~3
        if offset + padded > len(data):
            raise PcapNgError("truncated option")
        options.setdefault(code, []).append(data[offset : offset + length])
        offset += padded
    if any(data[offset:]):
        raise PcapNgError("non-zero trailing option bytes")
    return options


def _parse_interface(
    body: bytes, endian: str, section_index: int, interface_id: int
) -> InterfaceDescription:
    if len(body) < 8:
        raise PcapNgError("truncated interface description")
    link_type, _reserved, snap_len = struct.unpack(endian + "HHI", body[:8])
    options = _parse_options(body[8:], endian)

    name: str | None = None
    if OPTION_IF_NAME in options:
        name = options[OPTION_IF_NAME][0].decode("utf-8", errors="replace")

    units_per_second = 1_000_000
    if OPTION_IF_TSRESOL in options:
        value = options[OPTION_IF_TSRESOL][0]
        if len(value) != 1:
            raise PcapNgError("if_tsresol must contain exactly one byte")
        raw = value[0]
        units_per_second = 2 ** (raw & 0x7F) if raw & 0x80 else 10**raw

    offset_seconds = 0
    if OPTION_IF_TSOFFSET in options:
        value = options[OPTION_IF_TSOFFSET][0]
        if len(value) != 8:
            raise PcapNgError("if_tsoffset must contain exactly eight bytes")
        offset_seconds = struct.unpack(endian + "q", value)[0]

    return InterfaceDescription(
        section_index=section_index,
        interface_id=interface_id,
        link_type=link_type,
        snap_len=snap_len,
        name=name,
        timestamp_units_per_second=units_per_second,
        timestamp_offset_seconds=offset_seconds,
    )
