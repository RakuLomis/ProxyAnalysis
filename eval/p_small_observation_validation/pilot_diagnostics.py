"""Post-extraction interpretation only; never raw input, filtering or scoring.

All diagnostic flow-index reads are self-owned fold0 training contents with
explicit C permission under one of the preregistered masks. Only post socket
metadata is projected; no pre numeric feature or model is loaded. These data
must never feed back into the sealed worker outputs.
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import pandas as pd
from .common import ROOT, EXTRACT, Q, io_path, write, save

OUT = ROOT / "outputs/p-small-observation-validation-20261010/pilot-02-diagnostics"
PILOT = ROOT / "outputs/p-small-observation-validation-20261010/pilot-02"


def hash_value(v):
    return hashlib.sha256(repr(v).encode()).hexdigest()


def sha(p):
    if Path(p).suffix.lower() in {".pcap", ".cap", ".pcapng"}:
        raise PermissionError("diagnostics_do_not_open_raw")
    return hashlib.sha256(io_path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(io_path(p).read_text(encoding="utf-8-sig"))


def run():
    if OUT.exists():
        raise FileExistsError("preserve independent diagnostics")
    js = read(PILOT / "audit/visit-join.json")
    roles = read(ROOT / "outputs/p-small-observation-validation-20261010/run-04/manifests/cohort-and-roles.json")["roles"]
    feature_path = Q / "features/paired-flow-features.parquet"
    old_pairs = pd.read_parquet(feature_path, columns=["session_id", "carrier_id"],
                               filters=[("session_id", "in", [j["session_id"] for j in js])])
    visits, bad, access = [], [], []
    for j in js:
        assert j["fold"] != 0
        role = next(r for r in roles if r["target"] == j["protocol"] and r["outer"] == 0
                    and j["content_id"] in r["C_contents"])
        assert j["content_id"] not in role["validation_contents"] and j["content_id"] not in role["U_contents"]
        file = (ROOT / "Datasets/extend" / j["manifest_relative"]).parent / "analysis/flow-index.json"
        flow = read(file)
        access.append({"path": str(file.relative_to(ROOT)), "sha256": sha(file), "role_id": role["id"],
                       "purpose": "offline_self_owned_C_post_socket_scope_interpretation", "worker_input": False})
        carrier_networks, socket_evidence = defaultdict(set), defaultdict(list)
        for f in flow["items"]:
            binding = f.get("carrier_binding") or {}
            post = f.get("post_flow") or {}
            cid = binding.get("carrier_id")
            paths = [post, *(binding.get("physical_paths") or [])]
            for p in paths:
                if cid and p.get("network"):
                    carrier_networks[cid].add(p["network"])
                if p.get("network") == "tcp" and all(p.get(k) for k in ["src_ip", "src_port", "dst_ip", "dst_port"]):
                    key = (p["src_ip"], int(p["src_port"]), p["dst_ip"], int(p["dst_port"]))
                    socket_evidence[hash_value(key)].append({"egress": f.get("egress_outcome"),
                        "disposition": f.get("post_flow_disposition"), "carrier_present": bool(cid)})
        result = read(PILOT / "pilot/by-visit" / (j["visit_token"]+".json"))
        event_keys = {(e["timestamp_ns"], e["ordinal"]) for e in result["events"]}
        event_path = EXTRACT / "sessions" / j["session_id"] / "post-W-events.parquet"
        old = pd.read_parquet(event_path)
        access.append({"path": str(event_path.relative_to(ROOT)), "sha256": sha(event_path),
                       "purpose": "old_post_events_scope_replay", "worker_input": False})
        pair_ids = set(old_pairs[old_pairs.session_id.eq(j["session_id"])].carrier_id)
        misses = Counter()
        missing_pairs = 0
        for e in old.to_dict("records"):
            if (int(e["timestamp_ns"]), int(e["raw_packet_ordinal"])) not in event_keys:
                networks = carrier_networks.get(e["entity_id"], set())
                misses["+".join(sorted(networks)) or "unresolved"] += 1
                missing_pairs += e["entity_id"] in pair_ids
        a = read(PILOT / "audit/replay" / (j["visit_token"]+".json"))
        audit = result["audit"]
        row = {"protocol": j["protocol"], "label_id": j["label_id"], "session_id": j["session_id"],
               "visit_token": j["visit_token"], "content_id": j["content_id"], "fold": j["fold"],
               "status": result["visit"]["status"], "epochs": len(result["connections"]),
               "nonempty": result["visit"]["nonempty_connections"],
               "valid_nonempty": result["visit"]["technically_valid_nonempty_connections"],
               "old_TCP_pairs": a["paired_post_connections"], "exact_TCP_replays": a["exact_ten_stat_replays"],
               "old_W_packets": len(old), "physical_TCP_payload_packets": len(result["events"]),
               "old_W_unmatched": a["missing_old_packets"], "unmatched_UDP": misses["udp"],
               "unmatched_TCP": misses["tcp"], "unmatched_unresolved_or_mixed": sum(v for k,v in misses.items() if k not in {"udp", "tcp"}),
               "unmatched_paired_TCP": int(missing_pairs), "extra_TCP_payload_packets": a["physical_extra_positive_packets"],
               "parse_seconds": audit["elapsed_seconds"], "raw_bytes": audit["bytes_read"],
               "packet_span_enclosed": audit["window_packet_span_enclosed"],
               "first_packet_minus_start_ms": (audit["first_packet_ns"]-j["window_start_ns"])/1e6,
               "last_packet_minus_end_ms": (audit["last_packet_ns"]-j["window_end_ns"])/1e6}
        visits.append(row)
        for c in result["connections"]:
            if c["nonempty"] and not c["valid"]:
                evidence = socket_evidence.get(c["socket_token"], [])
                bad.append({"protocol": j["protocol"], "label_id": j["label_id"], "session_id": j["session_id"],
                            "instance_token": c["instance_token"], "reasons": c["reasons"],
                            "metadata_post_socket_matches": len(evidence), "metadata_evidence": evidence,
                            "old_W_payload_matches": sum(e["instance_token"] == c["instance_token"]
                                                        and (e["timestamp_ns"], e["ordinal"]) in {
                                                            (int(p.timestamp_ns), int(p.raw_packet_ordinal)) for p in old.itertuples()}
                                                        for e in result["events"]),
                            "bare_syn_observed": c["bare_syn_observed"], "rst": c["rst"], "fin_directions": c["fin_directions"],
                            "window_packet_count": c["window_packet_count"], "statistics": c["statistics"],
                            "first_minus_window_start_s": (c["first_ns"]-j["window_start_ns"])/1e9,
                            "last_minus_window_end_s": (c["last_ns"]-j["window_end_ns"])/1e9})
    frame = pd.DataFrame(visits)
    save(OUT, "visits.parquet", frame)
    write(OUT, "invalid-connections.json", bad)
    write(OUT, "metadata-access.json", access)
    totals = {c: int(frame[c].sum()) for c in ["old_W_unmatched", "unmatched_UDP", "unmatched_TCP",
              "unmatched_unresolved_or_mixed", "unmatched_paired_TCP", "extra_TCP_payload_packets", "exact_TCP_replays"]}
    assert totals["old_W_unmatched"] == totals["unmatched_UDP"] + totals["unmatched_TCP"] + totals["unmatched_unresolved_or_mixed"]
    summary = {"totals": totals, "invalid_connections": len(bad),
               "invalid_connections_without_post_socket_metadata": sum(not c["metadata_post_socket_matches"] for c in bad),
               "same_TCP_scope_replay_passed": totals["unmatched_paired_TCP"] == 0 and totals["exact_TCP_replays"] == 1235,
               "old_W_all_transport_equal_to_O1_TCP_scope": False,
               "old_W_nonTCP_difference_not_packet_loss": totals["old_W_unmatched"] == totals["unmatched_UDP"],
               "raw_PCAP_reopens": 0, "numeric_pre_reads": 0, "classifier_fits": 0,
               "old_worker_outputs_unchanged": True, "O1_engineering_gate_revised_or_passed": False,
               "permission": "self-owned C post metadata offline only, never worker or selection",
               "source_sha256": sha(Path(__file__)),
               "per_protocol": frame.groupby("protocol").agg(visits=("status", "size"),
                    valid=("status", lambda s: int(s.eq("valid").sum())), nonempty=("nonempty", "sum"),
                    old_pairs=("old_TCP_pairs", "sum"), missing_udp=("unmatched_UDP", "sum"),
                    extra_tcp_packets=("extra_TCP_payload_packets", "sum")).to_dict("index")}
    write(OUT, "summary.json", summary)
    files = {str(p.relative_to(OUT)): sha(p) for p in OUT.rglob("*") if p.is_file()}
    write(OUT, "seal.json", {"files": files, "pilot_seal_sha256": sha(PILOT / "seal.json")})
    assert all(sha(OUT/k) == v for k,v in files.items())
    assert all(sha(ROOT/e["path"]) == e["sha256"] for e in access)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    run()
