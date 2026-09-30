"""Observed unique sequence positions, not proof of application delivery."""
from pathlib import Path
import numpy as np

from ..parsing import PcapNgReader, decode_packet
from ..parsing.packet_decoder import _strip_link_header
from ..pipeline.analyze_entity import analyze_entity_capture
from .byte_runs import multiscale


def interval_union(intervals):
    """Independent sorted sweep reference, separate from legacy IntervalSet."""
    merged = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def conflicts(fragments):
    """Compare overlaps in memory; return a flag, never persist content."""
    far_start, far_end, far_data = 0, 0, b''
    count = 0
    for start, data in sorted(fragments, key=lambda x: x[0]):
        end = start+len(data)
        if far_data and start < far_end:
            overlap_end = min(end, far_end)
            if data[:overlap_end-start] != far_data[start-far_start:overlap_end-far_start]:
                count += 1
        if end > far_end or not far_data:
            far_start, far_end, far_data = start, end, data
    return count


def ledger(packets, segments, payloads=None, capture_ok=True):
    ordered = sorted(packets, key=lambda p: (p.timestamp_ns, p.packet_ordinal))
    by_id = {s.packet_event_id: s for s in segments}
    entries, events = [], []
    sides = {}
    for direction in (1, -1):
        ps = [p for p in ordered if p.direction == direction]
        intervals, pieces, payload_segments = [], [], []
        syn_positions, fin_positions = set(), []
        for p in ps:
            s = by_id[p.packet_event_id]
            start = s.seq_start_unwrapped+int(bool(p.flags & 2))
            if p.flags & 2:
                syn_positions.add(s.seq_start_unwrapped)
            if p.flags & 1:
                fin_positions.append(start+p.payload_len)
            if p.payload_len:
                intervals.append((start, start+p.payload_len))
                payload_segments.append(s)
                if payloads is not None and p.packet_event_id in payloads:
                    pieces.append((start, payloads[p.packet_event_id]))
        union = interval_union(intervals)
        observed = sum(p.payload_len for p in ps)
        unique = sum(b-a for a, b in union)
        legacy_unique = sum(s.new_payload_bytes for s in payload_segments)
        if unique != legacy_unique:
            raise AssertionError('Legacy incremental byte count differs from independent union')
        starts = [by_id[p.packet_event_id].seq_start_unwrapped for p in ps]
        span = max(starts)-min(starts) if starts else 0
        ambiguous = len(syn_positions) > 1 or span >= 2**31
        # Adjacent wire sequence numbers exactly half a sequence space apart are ambiguous.
        ambiguous |= any(((b.seq-a.seq) % 2**32) == 2**31 for a, b in zip(ps, ps[1:]))
        gaps = [b[0]-a[1] for a, b in zip(union, union[1:])]
        conflict = conflicts(pieces) if payloads is not None else None
        payload_verified = payloads is not None and all(p.packet_event_id in payloads and len(payloads[p.packet_event_id]) == p.payload_len for p in ps if p.payload_len)
        prefix = len(syn_positions) == 1 and (not union or union[0][0] == next(iter(syn_positions))+1)
        suffix = bool(fin_positions) and (not union or max(fin_positions) == union[-1][1])
        valid = capture_ok and not ambiguous and conflict == 0 and payload_verified
        reason = []
        if not capture_ok: reason.append('capture_or_direction_incomplete')
        if ambiguous: reason.append('epoch_or_sequence_span_ambiguous')
        if conflict: reason.append('overlap_content_conflict')
        if not payload_verified: reason.append('payload_integrity_unverified')
        if not prefix: reason.append('prefix_unobserved_or_incomplete')
        if not suffix: reason.append('fin_suffix_unobserved_or_incomplete')
        if gaps: reason.append('final_internal_gaps')
        if any(p.flags & 4 for p in ps): reason.append('rst_observed')
        reason.append('application_delivery_not_proven')
        # No Q2 assertion from packet flags alone: an independent successful relay gate is required.
        row = {'direction': direction, 'observed_payload_bytes': observed,
               'unique_payload_bytes': unique if valid else None,
               'duplicate_payload_bytes': observed-unique if valid else None,
               'duplicate_fraction': (observed-unique)/observed if observed and valid else None,
               'exclude_full_retransmission_bytes': sum(p.payload_len for p in ps if by_id[p.packet_event_id].classification != 'full_retransmission'),
               'new_data_event_count': sum(s.new_payload_bytes > 0 for s in payload_segments) if valid else None,
               'zero_payload_packet_count': sum(p.payload_len == 0 for p in ps),
               'full_retransmission_packets': sum(by_id[p.packet_event_id].classification == 'full_retransmission' for p in ps),
               'partial_retransmission_packets': sum(by_id[p.packet_event_id].classification == 'partial_retransmission' for p in ps),
               'final_internal_gap_count': len(gaps), 'final_internal_gap_bytes': sum(gaps),
               'prefix_observed': prefix, 'suffix_observed': suffix,
               'syn_count': sum(bool(p.flags & 2) for p in ps), 'fin_count': sum(bool(p.flags & 1) for p in ps),
               'rst_count': sum(bool(p.flags & 4) for p in ps), 'sequence_epoch_ambiguous': ambiguous,
               'overlap_content_conflicts': conflict, 'observed_unique_valid': valid,
               'quality': 'Q1' if valid else 'Q0', 'qualification_reasons': reason,
               'closed_contiguous_capture_candidate': valid and prefix and suffix and not gaps and not any(p.flags & 4 for p in ps)}
        sides[direction] = row
        entries.append(row)
    first = ordered[0].timestamp_ns if ordered else 0
    for p in ordered:
        s = by_id[p.packet_event_id]
        if s.new_payload_bytes and sides[p.direction]['observed_unique_valid']:
            events.append({'packet_ordinal': p.packet_ordinal, 'direction': p.direction,
                           'relative_time_ns': p.timestamp_ns-first, 'new_payload_bytes': s.new_payload_bytes,
                           'observed_payload_bytes': p.payload_len, 'partial_retransmission': s.classification == 'partial_retransmission'})
    end = ordered[-1].timestamp_ns-first if ordered else 0
    grid = np.linspace(0, end, 101)
    for row in entries:
        e = [x for x in events if x['direction'] == row['direction']]
        ts = np.array([x['relative_time_ns'] for x in e])
        sums = np.r_[0, np.cumsum([x['new_payload_bytes'] for x in e])]
        curve = sums[np.searchsorted(ts, grid, side='right')].tolist()
        row['new_byte_curve_absolute'] = curve if row['observed_unique_valid'] else None
        row['new_byte_curve_normalized'] = [x/row['unique_payload_bytes'] for x in curve] if row['unique_payload_bytes'] else None
        row['curve_duration_ns'] = end
    runs = multiscale((e['direction'], e['new_payload_bytes']) for e in events) if all(r['observed_unique_valid'] for r in entries) else []
    return entries, events, runs


def analyze_descriptor(desc):
    analysis = analyze_entity_capture(desc)
    payloads = {}
    audit = {'snaplen_truncated': 0, 'parse_incomplete': 0, 'timestamp_regressions': 0,
             'unknown_direction': analysis.unknown_direction_count, 'packet_count': analysis.packet_count}
    previous = None
    for record in PcapNgReader(desc.capture_path):
        if record.captured_len < record.original_len:
            audit['snaplen_truncated'] += 1
        if previous is not None and record.timestamp_ns < previous:
            audit['timestamp_regressions'] += 1
        previous = record.timestamp_ns
        p = decode_packet(record.link_type, record.packet_data)
        if p.transport_protocol != 'tcp' or p.decode_status != 'ok' or p.ip_more_fragments or p.ip_fragment_offset:
            audit['parse_incomplete'] += 1
            continue
        data = _strip_link_header(record.link_type, record.packet_data)
        offset = p.ip_header_len+p.transport_header_len
        body = data[offset:p.ip_total_len]
        if len(body) != p.transport_payload_len or len(data) < p.ip_total_len:
            audit['parse_incomplete'] += 1
            continue
        key = f'{desc.artifact_id}:{record.interface_id}:{record.packet_ordinal}'
        payloads[key] = body
    good = not (audit['snaplen_truncated'] or audit['parse_incomplete'] or audit['unknown_direction'])
    good &= len(analysis.tcp_packets) == analysis.packet_count
    rows, events, runs = ledger(analysis.tcp_packets, analysis.tcp.segments if analysis.tcp else (), payloads, good)
    return rows, events, runs, audit
