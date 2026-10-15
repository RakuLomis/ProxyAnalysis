"""Endpoint-scoped TCP epochs from packet evidence, never paired descriptors.

Conservative ambiguity flags are retained. A passed synthetic test is not an
assertion that epoch reconstruction has been verified on the real captures.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import hashlib
import ipaddress

from ..extend_calibration.reassembly import StrictIPv4
from ..parsing import decode_packet
from ..parsing.packet_decoder import _strip_link_header


@dataclass(frozen=True)
class Endpoint:
    address: str
    port: int

    def __post_init__(self):
        object.__setattr__(self, "address", str(ipaddress.ip_address(self.address)))
        if not 1 <= self.port <= 65535:
            raise ValueError("invalid_endpoint_port")


@dataclass(frozen=True)
class Packet:
    timestamp_ns: int
    ordinal: int
    direction: int
    local_address: str
    local_port: int
    remote_address: str
    remote_port: int
    seq: int
    ack: int
    flags: int
    payload_length: int
    payload: bytes | None
    fingerprint: str

    @property
    def key(self):
        return self.local_address, self.local_port, self.remote_address, self.remote_port


@dataclass
class Epoch:
    key: tuple
    ordinal: int
    packets: list[Packet] = field(default_factory=list)
    syn: dict[int, int] = field(default_factory=dict)
    bare_syn_observed: bool = False
    fins: set[int] = field(default_factory=set)
    rst: bool = False
    reasons: set[str] = field(default_factory=set)

    @property
    def terminated(self):
        return self.rst or self.fins == {1, -1}

    @property
    def token(self):
        # Audit identity only. Local ports and endpoint identity never reach x.
        material = repr((self.key, self.ordinal, self.syn)).encode()
        return hashlib.sha256(material).hexdigest()


def epochs(packets: list[Packet]) -> list[Epoch]:
    """No idle threshold, no label-dependent splits, no first-packet direction."""
    history: dict[tuple, list[Epoch]] = {}
    for p in sorted(packets, key=lambda q: (q.timestamp_ns, q.ordinal)):
        hs = history.setdefault(p.key, [])
        initial_syn = bool(p.flags & 2) and not bool(p.flags & 16)
        if not hs:
            hs.append(Epoch(p.key, 0))
        current = hs[-1]
        if initial_syn and p.direction in current.syn and current.syn[p.direction] != p.seq:
            previous = current
            current = Epoch(p.key, len(hs))
            hs.append(current)
            if not previous.terminated:
                previous.reasons.add("syn_restart_without_terminal_evidence")
                current.reasons.add("syn_restart_without_terminal_evidence")
        elif initial_syn and current.packets and p.direction not in current.syn:
            # A new SYN after a midstream epoch is not silently assigned to it.
            if current.terminated:
                current = Epoch(p.key, len(hs))
                hs.append(current)
            elif not current.syn:
                current.reasons.add("initial_syn_after_midstream_packets")
        if p.flags & 2:
            if p.direction in current.syn and current.syn[p.direction] != p.seq:
                current.reasons.add("conflicting_syn_sequence")
            current.syn.setdefault(p.direction, p.seq)
            current.bare_syn_observed |= initial_syn
        if p.payload_length and len(hs) > 1:
            # Do not silently put late data from an earlier socket incarnation
            # into the new epoch. Only detect ambiguity, never guess ownership.
            start = (p.seq + bool(p.flags & 2)) % (1 << 32)
            for old in hs[:-1]:
                if any(q.direction == p.direction and q.payload_length
                       and (start - (q.seq + bool(q.flags & 2))) % (1 << 32)
                       < q.payload_length for q in old.packets):
                    current.reasons.add("payload_may_belong_to_previous_epoch")
                    old.reasons.add("payload_may_belong_to_previous_epoch")
        current.packets.append(p)
        if p.flags & 1:
            current.fins.add(p.direction)
        current.rst |= bool(p.flags & 4)
    result = [e for hs in history.values() for e in hs]
    for e in result:
        if not e.bare_syn_observed:
            e.reasons.add("midstream_epoch_identity_unproven")
    return sorted(result, key=lambda e: (e.packets[0].timestamp_ns, e.packets[0].ordinal))


def ipv6_fragment_header(data: bytes) -> bool:
    if not data or data[0] >> 4 != 6:
        return False
    proto, offset = data[6], 40
    while proto in {0, 43, 44, 51, 60}:
        if proto == 44:
            return True
        if offset + 2 > len(data):
            return False  # Decoder will report malformed data independently.
        length = (data[offset + 1] + (2 if proto == 51 else 1)) * (4 if proto == 51 else 8)
        proto, offset = data[offset], offset + length
    return False


class EndpointDecoder:
    """One independent decoder per observation window.

    Header-only outside-window history can identify lifecycles. Payload bytes
    and interval accounting are retained only inside the specified window.
    IPv4 fragments are normalized only when every required piece is observed
    in-window, matching the old completion-time normalization, not guessed.
    """
    def __init__(self, endpoints: list[Endpoint], start_ns: int, end_ns: int):
        if end_ns <= start_ns or not endpoints:
            raise ValueError("invalid_window_or_empty_endpoints")
        self.endpoints = {(e.address, e.port) for e in endpoints}
        self.addresses = {e.address for e in endpoints}
        self.start, self.end = start_ns, end_ns
        self.fragments = StrictIPv4()
        self.counts = Counter()
        self.failures: set[str] = set()
        self.packets: list[Packet] = []

    def feed(self, rec):
        self.counts["raw_records"] += 1
        inside = self.start <= rec.timestamp_ns < self.end
        p = decode_packet(rec.link_type, rec.packet_data)
        relevant_address = p.ip_src in self.addresses or p.ip_dst in self.addresses
        if p.decode_status == "failed":
            # Non-IP Ethernet frames have no TCP relevance. Malformed unknown
            # scope cannot be silently certified as unrelated endpoint traffic.
            if inside and p.decode_reason not in {
                "malformed_packet:ValueError"  # handled below via link header
            }:
                self.failures.add("unclassifiable_packet")
            elif inside:
                try:
                    _strip_link_header(rec.link_type, rec.packet_data)
                except ValueError as exc:
                    if str(exc) != "unsupported_ether_type":
                        self.failures.add("unclassifiable_packet")
                else:
                    self.failures.add("unclassifiable_packet")
            return
        if not relevant_address:
            self.counts["outside_endpoint_addresses"] += 1
            return
        data = _strip_link_header(rec.link_type, rec.packet_data)
        if inside and (p.ip_fragment_offset or p.ip_more_fragments or ipv6_fragment_header(data)):
            if p.ip_version != 4:
                self.failures.add("unsupported_ipv6_fragments")
                return
            normalized = self.fragments.feed(rec, data)
            if normalized is None:
                return
            rec = normalized
            p = decode_packet(rec.link_type, rec.packet_data)
            data = _strip_link_header(rec.link_type, rec.packet_data)
        elif p.ip_fragment_offset or p.ip_more_fragments:
            return  # No reconstruction/state carried in from outside window.
        if p.transport_protocol != "tcp":
            self.counts["non_tcp_endpoint_address_packets"] += 1
            return
        source = (p.ip_src, p.src_port) in self.endpoints
        dest = (p.ip_dst, p.dst_port) in self.endpoints
        if not source and not dest:
            self.counts["outside_endpoint_ports"] += 1
            return
        if source and dest:
            if inside:
                self.failures.add("direction_ambiguous")
            return
        direction = 1 if dest else -1
        offset = p.ip_header_len + p.transport_header_len
        body = data[offset:p.ip_total_len]
        length = p.transport_payload_len
        if inside and (rec.captured_len < rec.original_len
                       or len(data) < p.ip_total_len or len(body) != length):
            self.failures.add("endpoint_packet_truncated")
            return
        local = (p.ip_src, p.src_port) if dest else (p.ip_dst, p.dst_port)
        remote = (p.ip_dst, p.dst_port) if dest else (p.ip_src, p.src_port)
        self.packets.append(Packet(rec.timestamp_ns, rec.packet_ordinal, direction,
                                   *local, *remote, p.tcp_seq, p.tcp_ack, p.tcp_flags_raw,
                                   length, body if inside else None,
                                   hashlib.sha256(rec.packet_data).hexdigest()))
        self.counts["endpoint_tcp_records"] += 1

    def finish(self):
        self.failures.update(self.fragments.finish())
        return epochs(self.packets), sorted(self.failures)
