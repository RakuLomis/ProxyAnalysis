"""Scope-explicit repeated feature extraction with original-stream boundaries."""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
import pyarrow.parquet as pq
import yaml

from ..config import FeatureConfig
from ..features.burst import direction_run_bursts
from ..features.cumulative import cumulative_shape
from ..features.distribution import fixed_histogram
from ..features.models import ordered_packets
from ..features.pairwise import js_divergence
from ..features.reversal import reversal_features
from ..features.transition import transition_features
from ..indexing.identities import build_entity_descriptors, EntityDescriptor
from ..sequences.direction import Endpoint
from ..indexing.pairs import build_exclusive_pairs
from ..pipeline.analyze_entity import analyze_entity_capture
from ..pipeline.analyze_entity import EntityAnalysis
from ..features.models import PacketMeasure
from ..parsing import PcapNgReader, decode_packet
from .scope_gate import bounded_events
from .preflight import write_json, write_table
from .registry import read_json


def describe(groups: list[list], config: FeatureConfig) -> dict:
    groups = [ordered_packets(group) for group in groups if group]
    packets = ordered_packets([p for group in groups for p in group])
    if not packets:
        return {}
    nonempty = [p for p in packets if p.transport_payload_len]
    payload = sum(p.transport_payload_len for p in packets)
    up = sum(p.transport_payload_len for p in packets if p.direction == 1)
    # IAT and transition counts must not cross unrelated stream boundaries.
    iat = [(b.timestamp_ns - a.timestamp_ns) / 1000 for group in groups
           for a, b in zip(group, group[1:])]
    transitions = [transition_features(p.direction for p in g if p.transport_payload_len)
                   for g in groups]
    plus_row = sum(t.n_pp + t.n_pm for t in transitions)
    plus_fraction = sum(p.direction == 1 for p in nonempty) / len(nonempty) if nonempty else None
    entropy = (-sum(p * math.log2(p) for p in (plus_fraction, 1 - plus_fraction) if p)
               if plus_fraction is not None else None)
    reversals = [reversal_features(g) for g in groups]
    lengths = [p.transport_payload_len for p in nonempty]
    hist = config.values["histograms"]

    def counts(values, edges):
        h = fixed_histogram(values, edges)
        # Explicit tails preserve probability mass outside frozen boundaries.
        return [h["underflow"], *h["counts"], h["overflow"]]

    curve = cumulative_shape(packets, axis="normalized_time", grid_points=101).absolute_transport_bytes
    return {"packet_count": len(packets), "transport_bytes": payload,
            "ip_bytes": sum(p.ip_total_len for p in packets), "up_transport_bytes": up,
            "down_transport_bytes": payload - up,
            "burst_count": sum(len(direction_run_bursts(g)) for g in groups),
            "fr_runs": sum(r.fr_runs for r in reversals),
            "fr_switches": sum(r.fr_reversals for r in reversals),
            "fr_runs_per_packet": sum(r.fr_runs for r in reversals) / len(nonempty) if nonempty else None,
            "up_byte_fraction": up / payload if payload else None,
            "transition_p_pm": sum(t.n_pm for t in transitions) / plus_row if plus_row else None,
            "direction_entropy": entropy,
            "length_median": float(np.median(lengths)) if lengths else None,
            "iat_median_us": float(np.median(iat)) if iat else None,
            "entity_count": len(groups),
            "length_hist": counts(lengths, hist["transport_payload_len_edges_bytes"]),
            "iat_hist": counts(iat, hist["iat_edges_us"]),
            "curve": [v / payload for v in curve] if payload else None,
            "first_ns": packets[0].timestamp_ns, "last_ns": packets[-1].timestamp_ns,
            "nonempty_packets": len(nonempty), "iat_count": len(iat),
            "zero_iat_count": sum(v == 0 for v in iat)}


def compare(before: dict, after: dict, metrics: list[dict], tcp: bool) -> list[dict]:
    result = []
    for metric in metrics:
        name, transform = metric["id"], metric["transform"]
        pre, post, delta, smoothed, reason = before.get(name), after.get(name), None, None, None
        if not before or not after:
            reason = "missing_nonempty_entity_side"
        elif metric.get("tcp_only") and not tcp:
            reason = "tcp_fr_not_comparable_to_shared_udp"
        elif transform == "distance":
            if name in {"length_js", "iat_js"}:
                key = "length_hist" if name == "length_js" else "iat_hist"
                delta = js_divergence(before[key], after[key])
            elif before["curve"] is not None and after["curve"] is not None:
                delta = float(np.mean(np.abs(np.asarray(before["curve"]) - after["curve"])))
            if delta is None:
                reason = "empty_distribution"
        elif pre is None or post is None:
            reason = "undefined_scalar"
        elif transform == "log_ratio":
            smoothed = math.log((post + 1) / (pre + 1))
            if pre > 0 and post > 0:
                delta = math.log(post / pre)
            else:
                reason = "zero_ratio_operand"
        else:
            delta = post - pre
        result.append({"metric": name, "family": metric["family"], "transform": transform,
                       "unit": metric["unit"], "pre": float(pre) if pre is not None else None,
                       "post": float(post) if post is not None else None,
                       "delta": delta, "delta_smoothed": smoothed, "reason": reason})
    return result


def analyze_carrier(descriptor, path):
    """Resolve all trace-declared paths, including Hy2 UDP port hopping."""
    paths=[]
    for flow in read_json(path / "analysis/flow-index.json")["items"]:
        binding=flow.get("carrier_binding") or {}
        if binding.get("carrier_id")==descriptor.entity_id:
            paths.extend(binding.get("physical_paths", []))
    events=[json.loads(line) for line in (path / "raw/mihomo-trace.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    for event in bounded_events(events, read_json(path / "analysis/summary.json")):
        if event.get("carrier_id")==descriptor.entity_id:
            paths.extend(event.get("carrier_paths", []))
            if event.get("post_flow"): paths.append(event["post_flow"])
    orientations={}
    for flow in paths:
        if all(flow.get(k) is not None for k in ("src_ip","src_port","dst_ip","dst_port")):
            forward=(flow["src_ip"],flow["src_port"],flow["dst_ip"],flow["dst_port"])
            reverse=(flow["dst_ip"],flow["dst_port"],flow["src_ip"],flow["src_port"])
            for key,direction in ((forward,1),(reverse,-1)):
                if key in orientations and orientations[key]!=direction:
                    raise ValueError("ambiguous carrier path orientation")
                orientations[key]=direction
    measures=[]
    for record in PcapNgReader(descriptor.capture_path):
        p=decode_packet(record.link_type,record.packet_data)
        direction=orientations.get((p.ip_src,p.src_port,p.ip_dst,p.dst_port))
        if direction is None or p.transport_protocol!="udp" or p.transport_payload_len is None:
            raise ValueError(f"unresolved carrier path: {descriptor.entity_id}")
        measures.append(PacketMeasure(f"{descriptor.artifact_id}:{record.packet_ordinal}",
            record.timestamp_ns,record.packet_ordinal,direction,p.transport_payload_len,
            p.ip_total_len,record.captured_len))
    return EntityAnalysis(descriptor,len(measures),len(measures),0,(),tuple(measures),(),None)


def context_descriptors(path):
    """Preserve carrier identity when its physical endpoint changes IP or port."""
    manifest=read_json(path/'manifest.json')
    connections={c['connection_id']:c for c in read_json(path/'analysis/connection-index-v2.json')['items']}
    descriptors=[]
    carriers={}
    for record in read_json(path/'analysis/pcap-index-v1.json')['connections']:
        c=connections[record['connection_id']]
        if c.get('egress',{}).get('outcome')!='proxy': continue
        pre,post=record.get('pre_proxy',{}),record.get('post_proxy',{})
        binding=c.get('carrier_binding',{})
        if pre.get('status')!='success' or post.get('status')!='success' or not binding.get('carrier_id'):
            continue
        flow=c['pre_flow']
        descriptors.append(EntityDescriptor(manifest['session_id'],'HYSTERIA2',c['connection_id'],
            'logical_connection','pre',path/pre['path'],pre['artifact_id'],flow['network'],
            Endpoint(flow['src_ip'],flow['src_port']),Endpoint(flow['dst_ip'],flow['dst_port']),
            False,'proxy',(c['connection_id'],)))
        key=(binding['carrier_id'],post['path'])
        carriers.setdefault(key,[]).append((c,post))
    for (cid,_),members in carriers.items():
        c,post=members[0]
        flow=c['post_flow']
        # Endpoints here identify an initial path only. analyze_carrier uses all declared paths.
        descriptors.append(EntityDescriptor(manifest['session_id'],'HYSTERIA2',cid,'carrier','post',
            path/post['path'],post['artifact_id'],'udp',Endpoint(flow['src_ip'],flow['src_port']),
            Endpoint(flow['dst_ip'],flow['dst_port']),True,'proxy',
            tuple(sorted({m[0]['connection_id'] for m in members}))))
    return descriptors


def extract_one(row: dict, config: FeatureConfig, metrics: list[dict]) -> dict:
    path = Path(row["session_path"])
    descriptors = context_descriptors(path) if row['protocol']=='HYSTERIA2' else build_entity_descriptors(path, row["protocol"])
    cache = {}

    def load(d):
        key = (d.capture_side, d.entity_id, str(d.capture_path))
        if key not in cache:
            analysis = analyze_carrier(d,path) if d.entity_level=="carrier" else analyze_entity_capture(d)
            if analysis.unknown_direction_count:
                raise ValueError(f"unknown direction: {d.entity_id}")
            cache[key] = analysis
        return cache[key]

    pair_records = []
    excluded = []
    hy2 = row["protocol"] == "HYSTERIA2"
    if not hy2:
        pairs = build_exclusive_pairs(path, row["protocol"])
        counts = Counter((p.post.entity_id, str(p.post.capture_path)) for p in pairs)
        accepted = []
        for pair in pairs:
            if counts[(pair.post.entity_id, str(pair.post.capture_path))] != 1:
                excluded.append({"connection_id": pair.connection_id, "reason": "outer_reused"})
            elif pair.pre.transport_protocol != "tcp" or pair.post.transport_protocol != "tcp":
                excluded.append({"connection_id": pair.connection_id, "reason": "non_tcp_pair"})
            else:
                accepted.append(pair)
        pre_desc, post_desc = [p.pre for p in accepted], [p.post for p in accepted]
        for pair in accepted:
            a, b = describe([list(load(pair.pre).packet_measures)], config), describe(
                [list(load(pair.post).packet_measures)], config)
            pair_records.extend({"connection_id": pair.connection_id, **item}
                                for item in compare(a, b, metrics, True))
    else:
        post_desc = [d for d in descriptors if d.capture_side == "post"
                     and d.entity_level == "carrier" and d.egress_outcome == "proxy"]
        related = {cid for d in post_desc for cid in d.logical_connection_ids}
        pre_desc = [d for d in descriptors if d.capture_side == "pre" and d.entity_id in related
                    and d.egress_outcome == "proxy"]
    pre_groups = [list(load(d).packet_measures) for d in pre_desc]
    post_groups = [list(load(d).packet_measures) for d in post_desc]
    comparisons = []
    for selection in ("observed", "nonempty", "exclude_full_retransmission"):
        def select(groups):
            return [[p for p in g if (selection != "nonempty" or p.transport_payload_len > 0)
                     and (selection != "exclude_full_retransmission" or
                          p.tcp_classification != "full_retransmission")] for g in groups]
        before_groups, after_groups = select(pre_groups), select(post_groups)
        before = describe(before_groups, config)
        scopes = ["carrier_context_envelope", "carrier_context_full"] if hy2 else ["exclusive_page"]
        for scope in scopes:
            windowed = after_groups
            if scope == "carrier_context_envelope":
                windowed = [[p for p in g if before and before["first_ns"] <= p.timestamp_ns <= before["last_ns"]]
                            for g in after_groups]
            after = describe(windowed, config)
            comparisons.extend({"scope": scope, "selection": selection, **item}
                               for item in compare(before, after, metrics, not hy2))
    sequences = []
    for analysis in cache.values():
        p = ordered_packets(analysis.packet_measures)[:32]
        sequences.append({"side": analysis.descriptor.capture_side,
                          "entity_id": analysis.descriptor.entity_id,
                          "transport": analysis.descriptor.transport_protocol,
                          "prefix_direction": [x.direction for x in p],
                          "prefix_signed_payload_length": [x.direction*x.transport_payload_len for x in p],
                          "prefix_iat_ns": [None, *[b.timestamp_ns-a.timestamp_ns for a,b in zip(p,p[1:])]][:len(p)]})
    return {"session_id": row["session_id"], "comparisons": comparisons,
            "exclusive_pairs": pair_records, "excluded_pairs": excluded,
            "sequences": sequences, "pre_entities": len(pre_desc), "post_entities": len(post_desc)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument('--feature-config', type=Path, default=Path('configs/feature-defaults.yaml'))
    parser.add_argument('--spec', type=Path, default=Path('configs/reproducibility.yaml'))
    parser.add_argument('--selected-only', action='store_true')
    args = parser.parse_args()
    root = args.output_root
    feature_config = FeatureConfig.load(args.feature_config)
    specification = yaml.safe_load(args.spec.read_text(encoding='utf-8'))
    digest = hashlib.sha256(args.spec.read_bytes()
                            + Path(__file__).read_bytes() + feature_config.sha256.encode()).hexdigest()
    write_json(root / "feature-contract.json", {"sha256": digest, "specification": specification,
               "feature_config_sha256": feature_config.sha256,
               "boundary_policy": "IAT/bursts/FR within entities; counts summed; cumulative time-union",
               "smoothing": "secondary only; c=1 in each metric's native unit"})
    rows = pq.read_table(root / "run_registry.parquet").to_pylist()
    if args.selected_only:
        rows = [r for r in rows if r['is_final']]
    if args.limit:
        rows = rows[:args.limit]
    features, pairs, sequences, statuses = [], [], [], []
    for index, row in enumerate(rows, 1):
        start = time.perf_counter()
        destination = root / "repeat-feature-sessions" / (row["session_id"] + ".json")
        source = Path(row["session_path"])
        files = [source / "analysis/connection-index-v2.json", source / "analysis/pcap-index-v1.json"]
        # Include indexed split file metadata; these are the extraction sources.
        for c in read_json(files[1])["connections"]:
            for side in ("pre_proxy", "post_proxy"):
                if c.get(side, {}).get("status") == "success":
                    files.append(source / c[side]["path"])
        fingerprint = hashlib.sha256(json.dumps([digest, [(str(p),p.stat().st_size,p.stat().st_mtime_ns)
            for p in sorted(set(files))]], sort_keys=True).encode()).hexdigest()
        saved = read_json(destination) if destination.is_file() else {}
        try:
            if saved.get("fingerprint") != fingerprint:
                saved = {**extract_one(row, feature_config, specification["metrics"]), "fingerprint": fingerprint}
                write_json(destination, saved)
            base = {k: row[k] for k in ("session_id", "activity_id", "target_domain", "protocol",
                                        "repetition", "attempt", "is_final", "is_first_attempt", "traffictracer_commit")}
            features.extend({**base, **r, "contract_sha256": digest} for r in saved["comparisons"])
            pairs.extend({**base, **r} for r in saved["exclusive_pairs"])
            sequences.extend({**base, **r} for r in saved["sequences"])
            status = {**base, "state": "complete", "pre_entities": saved["pre_entities"],
                      "post_entities": saved["post_entities"], "excluded_pairs": len(saved["excluded_pairs"])}
        except Exception as exc:
            status = {"session_id": row["session_id"], "state": "error", "error": str(exc)}
        statuses.append(status)
        print(f"[{index}/{len(rows)}] {row['protocol']} {row['target_domain']} r{row['repetition']} "
              f"{status['state']} {time.perf_counter()-start:.2f}s", flush=True)
    write_table(root / "repeat_feature_long.parquet", features)
    write_table(root / "exclusive_pair_feature_long.parquet", pairs)
    write_table(root / "sequence_prefixes.parquet", sequences)
    write_json(root / "repeat-extraction-status.json", statuses)
    if any(s["state"] == "error" for s in statuses):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
