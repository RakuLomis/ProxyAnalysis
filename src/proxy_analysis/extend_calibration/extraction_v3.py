"""Observed-window W and observed-unique exclusive TCP T; no model fitting."""
from collections import Counter, defaultdict
from pathlib import Path
import json
import time

import pandas as pd

from .audit import read, write, file_hash, fs_path, path_identity, digest
from .forensic import flow_tuple
from .reassembly import NormalizedReader
from ..parsing import PcapNgReader, decode_packet
from ..parsing.packet_decoder import _strip_link_header
from ..sequences.tcp_state import TcpPacket, analyze_tcp_flow
from ..protocol_normalization.tcp_ledger import ledger


def reverse(k):
    return k[0], k[3], k[4], k[1], k[2]


def summarize(events, byte_field="payload_bytes"):
    counts = {f"{q}_{d}": 0 for q in ["W", "P", "R"] for d in ["up", "down"]}
    last = None
    for row in sorted(events, key=lambda r: (r["timestamp_ns"], r["raw_packet_ordinal"])):
        length = int(row[byte_field])
        if length <= 0:
            continue
        suffix = "up" if row["direction"] == 1 else "down"
        counts["W_" + suffix] += length
        counts["P_" + suffix] += 1
        if row["direction"] != last:
            counts["R_" + suffix] += 1
        last = row["direction"]
    return counts


def valid_window(s):
    for d in ["up", "down"]:
        w, p, r = [s[f"{q}_{d}"] for q in ["W", "P", "R"]]
        if not (0 <= r <= p <= w <= 65527 * p and (r == 0) == (p == 0) == (w == 0)):
            return False
    return s["R_up"] + s["R_down"] >= 1 and abs(s["R_up"] - s["R_down"]) <= 1


def mapping_add(mapping, flow, identifier):
    k = flow_tuple(flow)
    if any(v is None or v == "" for v in k):
        return False
    mapping[k].add((identifier, 1))
    mapping[reverse(k)].add((identifier, -1))
    return True


def extract_one(task):
    row, source_dir, output_dir = task
    sid = row["session_id"]
    base = (fs_path(Path(source_dir)) / row["manifest_relative"]).parent
    dest = Path(output_dir) / "sessions" / sid
    dest.mkdir(parents=True, exist_ok=True)
    checkpoint = dest / "complete.json"
    if checkpoint.exists():
        saved = read(checkpoint)
        for rel, h in saved["input_hashes"].items():
            if file_hash(base / rel) != h:
                raise ValueError("resumed source changed: " + sid)
        return saved
    start_clock = time.monotonic()
    manifest = read(base / "manifest.json")
    window = row["common_window"]
    for rel, expected in window["evidence_hashes"].items():
        assert file_hash(base / rel) == expected, "prepared window evidence changed"
    start, end = window["start_ns"], window["end_ns"]
    write(dest / "common-window.json", window)
    assert end > start
    flowdoc = read(base / "analysis/flow-index.json")
    flows = flowdoc["items"]
    all_selected, excluded = [], []
    lifecycle_excluded = []
    for f in flows:
        sem = f.get("proxy_semantics") or {}
        protocol = sem.get("protocol")
        if protocol == "ss":
            protocol = "shadowsocks"
        b = f.get("carrier_binding") or {}
        if f.get("egress_outcome") == "proxy" and protocol == row["protocol"] and b.get("carrier_id") and f.get("post_flow_disposition") == "with_post_flow":
            if f["conn_id"] in window["excluded_selected"]:
                lifecycle_excluded.append(f)
                excluded.append({"logical_id": f["conn_id"], **window["excluded_selected"][f["conn_id"]]})
            else:
                all_selected.append(f)
        else:
            excluded.append({"logical_id": f.get("conn_id"), "egress": f.get("egress_outcome"),
                "disposition": f.get("post_flow_disposition"), "semantic_protocol": protocol})
    pre, post = defaultdict(set), defaultdict(set)
    excluded_maps = {"pre": defaultdict(set), "post": defaultdict(set)}
    for f in lifecycle_excluded:
        mapping_add(excluded_maps["pre"], f["pre_flow"], f["conn_id"])
        for path in f["carrier_binding"].get("physical_paths") or [f.get("post_flow") or {}]:
            mapping_add(excluded_maps["post"], path, f["carrier_binding"]["carrier_id"])
    reasons = []
    carrier_members = defaultdict(set)
    for f in all_selected:
        cid = f["carrier_binding"]["carrier_id"]
        carrier_members[cid].add(f["conn_id"])
        if not mapping_add(pre, f.get("pre_flow") or {}, f["conn_id"]):
            reasons.append("incomplete_pre_tuple")
        paths = f["carrier_binding"].get("physical_paths") or [f.get("post_flow") or {}]
        for flow in paths:
            if not mapping_add(post, flow, cid):
                reasons.append("incomplete_post_tuple")
    # Include lifecycle path changes only within the verified trace snapshot.
    summary = read(base / "analysis/summary.json")
    snapshots = summary.get("trace_snapshot", {}).get("traces", [])
    if len(snapshots) != 1 or not snapshots[0].get("barrier_verified"):
        reasons.append("unverified_trace_boundary")
    else:
        snap = snapshots[0]
        causal = set(snap.get("causal_tail_event_seqs", []))
        for line in (base / "raw/mihomo-trace.jsonl").open(encoding="utf-8"):
            if '"carrier_id"' not in line:
                continue
            e = json.loads(line)
            seq = e.get("event_seq")
            if not isinstance(seq, int) or not (seq <= snap["cutoff_event_seq"] or seq in causal):
                continue
            if e.get("carrier_id") not in carrier_members:
                continue
            for flow in e.get("carrier_paths", []):
                mapping_add(post, flow, e["carrier_id"])
            if e.get("post_flow"):
                mapping_add(post, e["post_flow"], e["carrier_id"])
    if not all_selected:
        reasons.append("no_selected_proxy_members")
    t_pairs = []
    if row["protocol"] != "anytls":
        for f in all_selected:
            b = f["carrier_binding"]
            if b.get("mode") == "exclusive" and len(carrier_members[b["carrier_id"]]) == 1 and f["pre_flow"].get("network") == "tcp" and f["post_flow"].get("network") == "tcp":
                t_pairs.append((f["conn_id"], b["carrier_id"]))
    t_ids = {"pre": {p for p, _ in t_pairs}, "post": {q for _, q in t_pairs}}
    tcp_packets = {"pre": defaultdict(list), "post": defaultdict(list)}
    tcp_payloads = {"pre": defaultdict(dict), "post": defaultdict(dict)}
    invalid_tcp = {"pre": set(), "post": set()}
    member_counts = Counter()
    captures, side_summaries = [], []
    for side, filename, mapping in [("pre", "tun.pcap", pre), ("post", "phys.pcap", post)]:
        stats = Counter()
        events = []
        first, last = None, None
        selected_addresses = {(k[1], k[3]) for k in mapping}
        reader = NormalizedReader(base / "raw" / filename, start, end, selected_addresses)
        for rec in reader:
            stats["raw_packets"] += 1
            first = rec.timestamp_ns if first is None else min(first, rec.timestamp_ns)
            last = rec.timestamp_ns if last is None else max(last, rec.timestamp_ns)
            if not start <= rec.timestamp_ns < end:
                stats["outside_manifest_window"] += 1
                continue
            pkt = decode_packet(rec.link_type, rec.packet_data)
            key = (pkt.transport_protocol, pkt.ip_src, pkt.src_port, pkt.ip_dst, pkt.dst_port)
            matches = mapping.get(key, set())
            fragment = bool(pkt.ip_fragment_offset or pkt.ip_more_fragments)
            if not matches:
                stats["unselected_packets"] += 1
                if key in excluded_maps[side] and (pkt.transport_payload_len or 0) > 0:
                    stats["excluded_lifecycle_payload_observed"] += 1
                if fragment and (pkt.ip_src, pkt.ip_dst) in selected_addresses:
                    stats["unmatched_scope_fragment"] += 1
                continue
            stats["selected_packets"] += 1
            ids = {v[0] for v in matches}
            dirs = {v[1] for v in matches}
            for ident in ids:
                member_counts[(side, ident)] += 1
            if len(dirs) != 1:
                stats["ambiguous_direction"] += 1
                invalid_tcp[side].update(ids)
                continue
            if len(ids) != 1:
                # W union ownership is sufficient only within the same selected
                # scope and direction. T attribution remains explicitly invalid.
                stats["union_multi_owner_packets"] += 1
                invalid_tcp[side].update(ids)
                ident = "union:" + digest(sorted(ids))
            else:
                ident = next(iter(ids))
            direction = next(iter(dirs))
            try:
                ipdata = _strip_link_header(rec.link_type, rec.packet_data)
            except ValueError:
                ipdata = b""
            error = None
            if fragment:
                error = "selected_fragment"
            elif rec.captured_len < rec.original_len or pkt.ip_total_len is None or len(ipdata) < pkt.ip_total_len:
                error = "selected_truncation"
            elif pkt.decode_status != "ok":
                error = "selected_decode_failure"
            elif pkt.transport_payload_len is None:
                error = "selected_unknown_payload"
            elif pkt.transport_payload_len > 65527:
                error = "selected_payload_oversize"
            if error:
                stats[error] += 1
                invalid_tcp[side].add(ident)
                continue
            length = pkt.transport_payload_len
            if length > 0:
                events.append({"timestamp_ns": rec.timestamp_ns, "raw_packet_ordinal": rec.packet_ordinal,
                    "direction": direction, "payload_bytes": length, "entity_id": ident})
            else:
                stats["zero_payload_packets"] += 1
            if ident in t_ids[side] and pkt.transport_protocol == "tcp":
                event_id = f"{sid}:{side}:{rec.packet_ordinal}"
                tcp_packets[side][ident].append(TcpPacket(event_id, rec.timestamp_ns, rec.packet_ordinal,
                    direction, pkt.tcp_seq, pkt.tcp_ack, pkt.tcp_flags_raw, length,
                    pkt.tcp_window_raw or 0, pkt.tcp_options_raw or b""))
                offset = pkt.ip_header_len + pkt.transport_header_len
                tcp_payloads[side][ident][event_id] = ipdata[offset:pkt.ip_total_len]
        hard = ["excluded_lifecycle_payload_observed", "unmatched_scope_fragment", "ambiguous_direction", "selected_fragment", "selected_truncation",
            "selected_decode_failure", "selected_unknown_payload", "selected_payload_oversize"]
        reasons.extend(side + ":" + key for key in hard if stats[key])
        reasons.extend(side + ":reassembly:" + key for key in reader.reassembly.finish())
        stats["normalized_records"] = stats["raw_packets"]
        stats["raw_packets"] = reader.raw_count
        first, last = reader.first, reader.last
        write(dest / (side + "-reassembly.json"), {
            "stats": dict(reader.reassembly.stats), "provenance": reader.reassembly.provenance,
            "unit": "transport_datagram_at_complete_time",
            "raw_packet_count": reader.raw_count})
        values = summarize(events)
        if not valid_window(values):
            reasons.append(side + ":invalid_or_empty_W")
        frame = pd.DataFrame(events, columns=["timestamp_ns", "raw_packet_ordinal", "direction", "payload_bytes", "entity_id"])
        frame.sort_values(["timestamp_ns", "raw_packet_ordinal"]).to_parquet(dest / (side + "-W-events.parquet"), index=False, compression="zstd")
        side_summaries.append({"session_id": sid, "side": side, **values})
        captures.append({"side": side, "first_packet_ns": first, "last_packet_ns": last,
            "file_bytes": (base / "raw" / filename).stat().st_size, **stats})
    missing_pre = [f["conn_id"] for f in all_selected if member_counts[("pre", f["conn_id"])] == 0]
    missing_post = [cid for cid in carrier_members if member_counts[("post", cid)] == 0]
    if missing_pre:
        reasons.append("members_without_window_packets")
    if missing_post:
        reasons.append("carriers_without_window_packets")
    t_rows, t_events, t_pair_rows = [], [], []
    for logical, carrier in t_pairs:
        good = True
        pair_values = {}
        for side, ident in [("pre", logical), ("post", carrier)]:
            packets = tcp_packets[side][ident]
            if not packets:
                good = False
                pair_values[side] = None
                continue
            analysis = analyze_tcp_flow(packets)
            rows, ev, runs = ledger(packets, analysis.segments, tcp_payloads[side][ident], ident not in invalid_tcp[side])
            valid = all(r["observed_unique_valid"] for r in rows) and bool(ev)
            good &= valid
            ordered = sorted(packets, key=lambda p: (p.timestamp_ns, p.packet_ordinal))
            ev_rows = [{"session_id": sid, "logical_id": logical, "side": side,
                "timestamp_ns": ordered[0].timestamp_ns + e["relative_time_ns"],
                "raw_packet_ordinal": e["packet_ordinal"], "direction": e["direction"],
                "new_bytes": e["new_payload_bytes"]} for e in ev]
            val = summarize(ev_rows, "new_bytes")
            pair_values[side] = {"U_up": val["W_up"], "U_down": val["W_down"],
                "E_up": val["P_up"], "E_down": val["P_down"], "R_up": val["R_up"], "R_down": val["R_down"]}
            for r in rows:
                t_rows.append({"session_id": sid, "logical_id": logical, "side": side,
                    "direction": r["direction"], "valid": r["observed_unique_valid"],
                    "unique_bytes": r["unique_payload_bytes"], "reasons": json.dumps(r["qualification_reasons"]),
                    "closed_contiguous": r["closed_contiguous_capture_candidate"]})
            t_events.extend(ev_rows)
        t_pair_rows.append({"logical_id": logical, "carrier_id": carrier, "common_valid_nonempty": good,
            "summaries": pair_values})
    common = [r for r in t_pair_rows if r["common_valid_nonempty"]]
    t_summaries = []
    for side in ["pre", "post"]:
        keys = ["U_up", "U_down", "E_up", "E_down", "R_up", "R_down"]
        t_summaries.append({"session_id": sid, "side": side, "F": len(common),
            **{k: sum(r["summaries"][side][k] for r in common) for k in keys}})
    pd.DataFrame(t_rows).to_parquet(dest / "T-direction-ledger.parquet", index=False)
    pd.DataFrame(t_events).to_parquet(dest / "T-newbyte-events.parquet", index=False, compression="zstd")
    write(dest / "T-pairs.json", t_pair_rows)
    write(dest / "scope.json", {"selected_logical_ids": [f["conn_id"] for f in all_selected],
        "carriers": {c:sorted(v) for c,v in carrier_members.items()}, "excluded": excluded,
        "pre_path_hashes": sorted({path_identity(f["pre_flow"]) for f in all_selected}),
        "post_path_hashes": sorted({path_identity(dict(zip(["network","src_ip","src_port","dst_ip","dst_port"],k))) for k,v in post.items() if any(d==1 for _,d in v)}),
        "missing_pre": missing_pre, "missing_post": missing_post})
    inputs = ["manifest.json", "analysis/flow-index.json", "analysis/summary.json", "raw/tun.pcap", "raw/phys.pcap", "raw/mihomo-trace.jsonl", "raw/capture-context.json", "raw/netlog.json"]
    result = {"session_id": sid, "protocol": row["protocol"], "content_id": row["content_id"],
        "label": row["label"], "repetition": row["repetition"], "start_ns": start, "end_ns": end,
        "members": len(all_selected), "carriers": len(carrier_members), "missing_pre": len(missing_pre),
        "missing_post": len(missing_post), "review_reasons": sorted(set(reasons)), "W_gate_passed": not reasons,
        "W": side_summaries, "T": t_summaries, "T_candidate_pairs": len(t_pairs), "T_common_pairs": len(common),
        "T_pair_validation_only": True, "capture_audit": captures,
        "input_hashes": {rel: file_hash(base / rel) for rel in inputs}, "seconds": time.monotonic() - start_clock,
        "training_performed": False, "extraction_version": "extend-WT-3",
        "W_unit": "positive_transport_datagram_after_strict_IP_reassembly",
        "multi_owner_W_is_union_only": True, "epoch_attribution_completed": False,
        "common_window": window, "lifecycle_excluded_members": len(lifecycle_excluded)}
    write(checkpoint, result)
    return result


