"""Conservative IPv4 fragment reassembly with original-packet provenance.

No time-selected cuts, padding, cross-session state, or best-effort output.
IPv6 fragments are retained as unsupported holds, never silently accepted.
"""
from dataclasses import dataclass, replace
from collections import Counter
import struct

from ..parsing import PcapNgReader, decode_packet
from ..parsing.packet_decoder import _strip_link_header


@dataclass
class Datagram:
    header: bytes
    pieces: dict
    sources: list
    first_ns: int
    last_ns: int
    final_length: int | None = None


class StrictIPv4:
    def __init__(self):
        self.pending = {}
        self.poisoned = set()
        self.stats = Counter()
        self.provenance = []

    def fail(self, key, reason):
        self.stats[reason] += 1
        self.pending.pop(key, None)
        self.poisoned.add(key)

    def feed(self, rec, ip):
        ihl = (ip[0] & 15)*4
        length, ident, flags = struct.unpack('!HHH', ip[2:8])
        offset, more = (flags & 8191)*8, bool(flags & 8192)
        key = (rec.section_index, rec.interface_id, ip[12:20], ip[9], ident)
        self.stats['fragment_packets'] += 1
        if key in self.poisoned:
            self.stats['poisoned_key_packets'] += 1
            return None
        if ihl < 20 or len(ip) < length or rec.captured_len < rec.original_len or length <= ihl:
            self.fail(key, 'truncated_or_empty_fragment')
            return None
        data = ip[ihl:length]
        if (more and len(data) % 8) or offset + len(data) > 65535-ihl:
            self.fail(key, 'invalid_fragment_extent')
            return None
        if key not in self.pending:
            # First-observed nonzero fragment is not guessed into a later ID epoch.
            if offset:
                self.fail(key, 'orphan_nonzero_fragment')
                return None
            self.pending[key] = Datagram(ip[:ihl], {}, [], rec.timestamp_ns, rec.timestamp_ns)
        d = self.pending[key]
        if offset == 0 and d.pieces and d.pieces.get(0) != data:
            self.fail(key, 'id_reuse_before_completion')
            return None
        if ihl != len(d.header) or ip[20:ihl] != d.header[20:]:
            self.fail(key, 'incompatible_fragment_headers')
            return None
        end = offset + len(data)
        if d.final_length is not None and (end > d.final_length or (more and end >= d.final_length)):
            self.fail(key, 'fragment_past_final_extent')
            return None
        if not more:
            if d.final_length is not None and d.final_length != end:
                self.fail(key, 'conflicting_final_lengths')
                return None
            if any(a+len(b) > end for a,b in d.pieces.items()):
                self.fail(key, 'prior_fragment_past_final_extent')
                return None
            d.final_length = end
        for a,b in d.pieces.items():
            lo,hi=max(a,offset),min(a+len(b),end)
            if lo < hi and b[lo-a:hi-a] != data[lo-offset:hi-offset]:
                self.fail(key, 'overlap_content_conflict')
                return None
        # Keep all covered bytes: an equal-start shorter retransmission must not
        # replace a previously longer piece.
        if len(data) > len(d.pieces.get(offset, b'')):
            d.pieces[offset] = data
        d.sources.append(rec.packet_ordinal)
        d.last_ns=max(d.last_ns,rec.timestamp_ns)
        extent=0
        for a,b in sorted(d.pieces.items()):
            if a > extent:
                return None
            extent=max(extent,a+len(b))
        if d.final_length is None or extent != d.final_length:
            return None
        payload=bytearray(extent)
        for a,b in d.pieces.items():
            payload[a:a+len(b)]=b
        header=bytearray(d.header)
        header[2:4]=struct.pack('!H',len(header)+extent)
        header[6:8]=b'\x00\x00'
        header[10:12]=b'\x00\x00'
        words=struct.unpack('!%dH'%(len(header)//2),header)
        total=sum(words)
        while total >> 16:
            total=(total & 65535)+(total >> 16)
        header[10:12]=struct.pack('!H',(~total)&65535)
        packet=bytes(header)+bytes(payload)
        decoded=decode_packet(101,packet)
        if decoded.decode_status != 'ok' or (decoded.transport_protocol == 'udp' and decoded.udp_length != extent):
            self.fail(key,'invalid_reassembled_transport')
            return None
        self.provenance.append({'completion_ordinal':rec.packet_ordinal,'source_ordinals':d.sources,
            'first_ns':d.first_ns,'complete_ns':d.last_ns,'datagram_bytes':len(packet),
            'transport_payload_bytes':decoded.transport_payload_len})
        del self.pending[key]
        self.stats['complete_datagrams'] += 1
        return replace(rec,link_type=101,timestamp_ns=d.last_ns,packet_data=packet,
                       captured_len=len(packet),original_len=len(packet))

    def finish(self):
        self.stats['incomplete_datagrams'] = len(self.pending)
        good={'fragment_packets','complete_datagrams'}
        return [k for k,v in self.stats.items() if v and k not in good]


class NormalizedReader:
    def __init__(self,path,start,end,selected_addresses):
        self.path,self.start,self.end,self.addresses=path,start,end,selected_addresses
        self.reassembly=StrictIPv4()
        self.raw_count=0
        self.first=self.last=None

    def __iter__(self):
        for rec in PcapNgReader(self.path):
            self.raw_count += 1
            self.first=rec.timestamp_ns if self.first is None else min(self.first,rec.timestamp_ns)
            self.last=rec.timestamp_ns if self.last is None else max(self.last,rec.timestamp_ns)
            p=decode_packet(rec.link_type,rec.packet_data)
            relevant=(p.ip_src,p.ip_dst) in self.addresses
            if self.start <= rec.timestamp_ns < self.end and relevant and (p.ip_fragment_offset or p.ip_more_fragments):
                if p.ip_version != 4:
                    self.reassembly.stats['unsupported_ipv6_fragments'] += 1
                    continue
                result=self.reassembly.feed(rec,_strip_link_header(rec.link_type,rec.packet_data))
                if result is not None:
                    yield result
            else:
                yield rec
