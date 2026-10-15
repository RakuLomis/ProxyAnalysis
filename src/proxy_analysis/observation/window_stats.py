"""Cold-window TCP payload interval accounting and the frozen ten statistics."""
from __future__ import annotations

from ..sequences.tcp_state import SequenceUnwrapper

FEATURES = ["W_up", "W_down", "U_up", "U_down", "P_up", "P_down", "E_up", "E_down",
            "FR_packet_runs", "R_unique_zero_runs"]


def sweep(intervals):
    result = []
    for a, b in sorted(intervals):
        if b <= a:
            continue
        if result and a <= result[-1][1]:
            result[-1] = (result[-1][0], max(result[-1][1], b))
        else:
            result.append((a, b))
    return result


def overlap_conflict(pieces):
    """Sorted interval witness; O(n log n), without persisting any payload."""
    far_start, far_end, far_body = 0, 0, b""
    for start, body in sorted(pieces, key=lambda item: item[0]):
        end = start + len(body)
        if far_body and start < far_end:
            stop = min(end, far_end)
            if body[:stop-start] != far_body[start-far_start:stop-far_start]:
                return True
        if not far_body or end > far_end:
            far_start, far_end, far_body = start, end, body
    return False


def summarize(epoch, start_ns, end_ns):
    # No header/payload from outside the window seeds the unwrap or byte union.
    ps = [p for p in epoch.packets if start_ns <= p.timestamp_ns < end_ns]
    values = dict.fromkeys(FEATURES, 0)
    reasons = set(epoch.reasons)
    events, total_reference, side_references = [], 0, {}
    positive = [p for p in ps if p.payload_length > 0]
    for direction, suffix in [(1, "up"), (-1, "down")]:
        ds = [p for p in ps if p.direction == direction]
        unwrapper = SequenceUnwrapper()
        intervals, union, pieces, unwrapped, syns = [], [], [], [], set()
        previous = None
        for p in ds:
            if previous is not None and (p.seq - previous) % (1 << 32) == (1 << 31):
                reasons.add("half_sequence_space_ambiguity")
            previous = p.seq
            seq = unwrapper.unwrap(p.seq)
            unwrapped.append(seq)
            if p.flags & 2:
                syns.add(seq)
            if not p.payload_length:
                continue
            values["W_" + suffix] += p.payload_length
            values["P_" + suffix] += 1
            a, b = seq + bool(p.flags & 2), seq + bool(p.flags & 2) + p.payload_length
            if p.payload is None or len(p.payload) != p.payload_length:
                reasons.add("payload_integrity_unverified")
            else:
                pieces.append((a, p.payload))
            covered = sum(max(0, min(b, y)-max(a, x)) for x, y in union)
            new = b-a-covered
            intervals.append((a, b))
            union = sweep([*union, (a, b)])
            if new > 0:
                values["E_" + suffix] += 1
            events.append({"timestamp_ns": p.timestamp_ns, "ordinal": p.ordinal,
                           "direction": direction, "new_bytes": new,
                           "observed_bytes": p.payload_length})
        if len(syns) > 1 or (unwrapped and max(unwrapped)-min(unwrapped) >= 1 << 31):
            reasons.add("sequence_epoch_or_span_ambiguous")
        # Reference is an independent endpoint sweep, not the incremental union.
        boundaries = sorted([(a, 1) for a, b in intervals] + [(b, -1) for a, b in intervals])
        reference, depth, previous_boundary = 0, 0, None
        for position, change in boundaries:
            if previous_boundary is not None and depth:
                reference += position - previous_boundary
            depth += change
            previous_boundary = position
        if overlap_conflict(pieces):
            reasons.add("overlap_content_conflict")
        unique = sum(b-a for a, b in union)
        if unique != reference:
            raise AssertionError("independent_unique_byte_replay")
        values["U_" + suffix] = unique
        side_references[suffix] = reference
        total_reference += reference
    last_packet = last_unique = None
    for p in positive:
        if p.direction != last_packet:
            values["FR_packet_runs"] += 1
        last_packet = p.direction
    for e in sorted(events, key=lambda e: (e["timestamp_ns"], e["ordinal"])):
        if e["new_bytes"] > 0:
            if e["direction"] != last_unique:
                values["R_unique_zero_runs"] += 1
            last_unique = e["direction"]
    for s in ("up", "down"):
        if not (0 <= values["U_"+s] <= values["W_"+s]
                and 0 <= values["E_"+s] <= values["P_"+s]
                and values["E_"+s] <= values["U_"+s]):
            raise AssertionError("direction_counter_invariant")
    if values["R_unique_zero_runs"] > values["E_up"]+values["E_down"]:
        raise AssertionError("unique_run_invariant")
    return {"epoch_token": epoch.token, "nonempty": bool(positive),
            "valid": not reasons, "reasons": sorted(reasons),
            "statistics": values, "new_byte_events": sorted(events, key=lambda e: (e["timestamp_ns"], e["ordinal"])),
            "unique_reference_bytes": total_reference, "side_reference_bytes": side_references,
            "packet_fingerprints": [p.fingerprint for p in ps],
            "cold_window_state": True, "application_delivery_proven": False}
