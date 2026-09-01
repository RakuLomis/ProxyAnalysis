"""Decode raw L2/L3/L4 header values without higher-level feature inference."""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import struct


DLT_EN10MB = 1
DLT_RAW = 101
ETH_IPV4 = 0x0800
ETH_IPV6 = 0x86DD
VLAN_TYPES = {0x8100, 0x88A8, 0x9100}
IP_TCP = 6
IP_UDP = 17
IPV6_EXTENSIONS = {0, 43, 44, 51, 60}


@dataclass(frozen=True, slots=True)
class ParsedPacket:
    decode_status: str
    decode_reason: str | None = None
    ip_version: int | None = None
    ip_src: str | None = None
    ip_dst: str | None = None
    ip_total_len: int | None = None
    ip_header_len: int | None = None
    ip_protocol: int | None = None
    ip_fragment_offset: int | None = None
    ip_more_fragments: bool | None = None
    transport_protocol: str | None = None
    src_port: int | None = None
    dst_port: int | None = None
    transport_header_len: int | None = None
    transport_payload_len: int | None = None
    tcp_seq: int | None = None
    tcp_ack: int | None = None
    tcp_flags_raw: int | None = None
    tcp_window_raw: int | None = None
    tcp_urgent_pointer: int | None = None
    tcp_options_raw: bytes | None = None
    udp_length: int | None = None


def decode_packet(link_type: int, data: bytes) -> ParsedPacket:
    try:
        ip_data = _strip_link_header(link_type, data)
        version = ip_data[0] >> 4 if ip_data else 0
        if version == 4:
            return _decode_ipv4(ip_data)
        if version == 6:
            return _decode_ipv6(ip_data)
        return ParsedPacket("skipped", "unsupported_network_protocol")
    except (IndexError, struct.error, ValueError) as exc:
        return ParsedPacket("failed", f"malformed_packet:{type(exc).__name__}")


def _strip_link_header(link_type: int, data: bytes) -> bytes:
    if link_type == DLT_RAW:
        return data
    if link_type != DLT_EN10MB:
        raise ValueError("unsupported_link_type")
    if len(data) < 14:
        raise ValueError("truncated_ethernet")
    ether_type = struct.unpack("!H", data[12:14])[0]
    offset = 14
    while ether_type in VLAN_TYPES:
        if len(data) < offset + 4:
            raise ValueError("truncated_vlan")
        ether_type = struct.unpack("!H", data[offset + 2 : offset + 4])[0]
        offset += 4
    if ether_type not in (ETH_IPV4, ETH_IPV6):
        raise ValueError("unsupported_ether_type")
    return data[offset:]


def _decode_ipv4(data: bytes) -> ParsedPacket:
    if len(data) < 20:
        raise ValueError("truncated_ipv4")
    version_ihl, _tos, total_len, _ident, flags_fragment, _ttl, protocol = struct.unpack(
        "!BBHHHBB", data[:10]
    )
    ihl = (version_ihl & 0x0F) * 4
    if ihl < 20 or len(data) < ihl:
        raise ValueError("invalid_ipv4_header_length")
    if total_len < ihl:
        raise ValueError("invalid_ipv4_total_length")
    src = str(ipaddress.IPv4Address(data[12:16]))
    dst = str(ipaddress.IPv4Address(data[16:20]))
    fragment_offset = (flags_fragment & 0x1FFF) * 8
    more_fragments = bool(flags_fragment & 0x2000)
    payload_end = min(total_len, len(data))
    transport = data[ihl:payload_end]
    if fragment_offset:
        return _base_ip_result(
            4, src, dst, total_len, ihl, protocol, fragment_offset, more_fragments
        )
    return _decode_transport(
        transport,
        4,
        src,
        dst,
        total_len,
        ihl,
        protocol,
        fragment_offset,
        more_fragments,
    )


def _decode_ipv6(data: bytes) -> ParsedPacket:
    if len(data) < 40:
        raise ValueError("truncated_ipv6")
    payload_len, next_header = struct.unpack("!HB", data[4:7])
    total_len = 40 + payload_len
    src = str(ipaddress.IPv6Address(data[8:24]))
    dst = str(ipaddress.IPv6Address(data[24:40]))
    offset = 40
    fragment_offset = 0
    more_fragments = False
    protocol = next_header
    while protocol in IPV6_EXTENSIONS:
        if protocol == 44:
            if len(data) < offset + 8:
                raise ValueError("truncated_ipv6_fragment")
            next_protocol = data[offset]
            raw_fragment = struct.unpack("!H", data[offset + 2 : offset + 4])[0]
            fragment_offset = ((raw_fragment >> 3) & 0x1FFF) * 8
            more_fragments = bool(raw_fragment & 1)
            header_len = 8
        elif protocol == 51:
            if len(data) < offset + 2:
                raise ValueError("truncated_ipv6_ah")
            next_protocol = data[offset]
            header_len = (data[offset + 1] + 2) * 4
        else:
            if len(data) < offset + 2:
                raise ValueError("truncated_ipv6_extension")
            next_protocol = data[offset]
            header_len = (data[offset + 1] + 1) * 8
        if header_len <= 0 or len(data) < offset + header_len:
            raise ValueError("invalid_ipv6_extension_length")
        offset += header_len
        protocol = next_protocol
    if fragment_offset:
        return _base_ip_result(
            6, src, dst, total_len, offset, protocol, fragment_offset, more_fragments
        )
    payload_end = min(total_len, len(data))
    return _decode_transport(
        data[offset:payload_end],
        6,
        src,
        dst,
        total_len,
        offset,
        protocol,
        fragment_offset,
        more_fragments,
    )


def _base_ip_result(
    version: int,
    src: str,
    dst: str,
    total_len: int,
    header_len: int,
    protocol: int,
    fragment_offset: int,
    more_fragments: bool,
) -> ParsedPacket:
    return ParsedPacket(
        decode_status="ip_only",
        decode_reason="non_initial_fragment" if fragment_offset else "unsupported_ip_protocol",
        ip_version=version,
        ip_src=src,
        ip_dst=dst,
        ip_total_len=total_len,
        ip_header_len=header_len,
        ip_protocol=protocol,
        ip_fragment_offset=fragment_offset,
        ip_more_fragments=more_fragments,
    )


def _decode_transport(
    data: bytes,
    version: int,
    src: str,
    dst: str,
    total_len: int,
    ip_header_len: int,
    protocol: int,
    fragment_offset: int,
    more_fragments: bool,
) -> ParsedPacket:
    base = dict(
        ip_version=version,
        ip_src=src,
        ip_dst=dst,
        ip_total_len=total_len,
        ip_header_len=ip_header_len,
        ip_protocol=protocol,
        ip_fragment_offset=fragment_offset,
        ip_more_fragments=more_fragments,
    )
    if protocol == IP_TCP:
        if len(data) < 20:
            raise ValueError("truncated_tcp")
        src_port, dst_port, seq, ack, offset_flags, window = struct.unpack(
            "!HHIIHH", data[:16]
        )
        header_len = ((offset_flags >> 12) & 0xF) * 4
        if header_len < 20 or len(data) < header_len:
            raise ValueError("invalid_tcp_header_length")
        urgent = struct.unpack("!H", data[18:20])[0]
        declared_transport_len = max(total_len - ip_header_len, 0)
        payload_len = max(declared_transport_len - header_len, 0)
        return ParsedPacket(
            decode_status="ok",
            transport_protocol="tcp",
            src_port=src_port,
            dst_port=dst_port,
            transport_header_len=header_len,
            transport_payload_len=payload_len,
            tcp_seq=seq,
            tcp_ack=ack,
            tcp_flags_raw=offset_flags & 0x01FF,
            tcp_window_raw=window,
            tcp_urgent_pointer=urgent,
            tcp_options_raw=data[20:header_len],
            **base,
        )
    if protocol == IP_UDP:
        if len(data) < 8:
            raise ValueError("truncated_udp")
        src_port, dst_port, udp_length = struct.unpack("!HHH", data[:6])
        if udp_length < 8:
            raise ValueError("invalid_udp_length")
        return ParsedPacket(
            decode_status="ok",
            transport_protocol="udp",
            src_port=src_port,
            dst_port=dst_port,
            transport_header_len=8,
            transport_payload_len=udp_length - 8,
            udp_length=udp_length,
            **base,
        )
    return _base_ip_result(
        version,
        src,
        dst,
        total_len,
        ip_header_len,
        protocol,
        fragment_offset,
        more_fragments,
    )

