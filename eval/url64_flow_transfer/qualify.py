"""Read-only Broad qualification. Never extracts packets or fits models.

Run from repository root with Pytorch312. Outputs are metadata candidates,
not a certification of packet-level identity, post-only selection or T/W validity.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
from proxy_analysis.extend_calibration.audit import (
    content_key, digest, file_hash, fs_path, read, route_evidence, write,
)


def window_candidate(context):
    p = context.get("packet_coverage") or {}
    # Coverage here is the collector's metadata assertion, not packet replay.
    return p.get("status") == "passed" and not p.get("errors")


def flow_candidate(f):
    b = f.get("carrier_binding") or {}
    post = f.get("post_flow") or {}
    return (f.get("egress_outcome") == "proxy"
            and b.get("mode") == "exclusive"
            and post.get("network") == "tcp"
            and post.get("complete") is True
            and not post.get("shared", False)
            and f.get("post_flow_disposition") == "with_post_flow")


def run(args):
    source = Path(args.inventory)
    out = Path(args.output)
    if (out / "status.json").exists():
        raise RuntimeError("Completed output exists; use a fresh output directory")
    sessions = pd.read_parquet(source / "sessions.parquet")
    broad = sessions[sessions.dataset_role.eq("broad")].copy()
    assert len(broad) == 384 and broad.session_id.nunique() == 384
    labels = sorted(broad.url.map(content_key).unique())
    assert len(labels) == 64
    registry = [{"url_id": i, "url_key": u} for i, u in enumerate(labels)]
    hashes, visits, evidence, flows, aliases = [], [], [], [], defaultdict(set)
    carrier_members = defaultdict(set)
    sid_role = dict(zip(sessions.session_id, sessions.dataset_role))
    sid_protocol = dict(zip(sessions.session_id, sessions.protocol))

    def load(base, name):
        path = base / name
        hashes.append({"relative": str(path.relative_to(fs_path(Path(args.raw)))),
                       "sha256": file_hash(path)})
        return read(path)

    for n, r in enumerate(broad.itertuples(), 1):
        base = fs_path(Path(args.raw) / r.manifest_relative).parent
        summary = load(base, "analysis/summary.json")
        request = load(base, "analysis/request-index-v2.json")
        connection = load(base, "analysis/connection-index-v2.json")
        flow = load(base, "analysis/flow-index.json")
        context = load(base, "raw/capture-context.json")
        docs = [summary, request, connection, flow]
        generation_ok = all(d.get("analysis_generation_id") == r.analysis_generation_id for d in docs)
        decision, rows = route_evidence(request["items"], connection["items"], {"url": r.url}, summary)
        evidence.extend(dict(x, session_id=r.session_id) for x in rows)
        key = content_key(r.url)
        aliases[key].add(key)
        nav = summary.get("navigation_outcome") or {}
        if nav.get("final_url"):
            aliases[key].add(content_key(nav["final_url"]))
        # Intermediate document redirects are recorded but not treated as aliases
        # of the main frame without independent navigation lineage.
        linked = {c.get("mihomo_connection_id"): c for c in connection["items"]
                  if c.get("mihomo_connection_id")}
        candidates = 0
        for f in flow["items"]:
            b = f.get("carrier_binding") or {}
            sem = f.get("proxy_semantics") or {}
            cid = b.get("carrier_id")
            entity = digest([r.protocol, sem.get("adapter_instance_id"), cid]) if cid else None
            if entity:
                carrier_members[entity].add(r.session_id)
            c = linked.get(f.get("conn_id"), {})
            candidate = flow_candidate(f)
            candidates += int(candidate)
            flows.append({"session_id": r.session_id, "protocol": r.protocol,
                          "flow_id": f.get("flow_id"), "carrier_entity": entity,
                          "binding_mode": b.get("mode"), "relation": b.get("relation"),
                          "egress": f.get("egress_outcome"),
                          "post_tcp_exclusive_metadata_candidate": candidate,
                          "page_connection_linked": bool(c),
                          "request_count": len(c.get("request_occurrence_ids", [])),
                          "attribution_scope": c.get("attribution_scope", f.get("attribution_scope")),
                          "sni_status": "not_extracted_not_a_filter"})
        visits.append({"session_id": r.session_id, "protocol": r.protocol,
                       "url": r.url, "url_key": key, "final_url": nav.get("final_url"),
                       "route": decision, "generation_ok": generation_ok,
                       "selection_ok": bool(r.selection_ok),
                       "window_metadata_candidate": bool(window_candidate(context)),
                       "flow_count": len(flow["items"]), "exclusive_tcp_candidates": candidates})
        if n % 64 == 0:
            print(f"Broad metadata inspected {n}/384", flush=True)

    all_aliases = set().union(*aliases.values())
    alias_owners = defaultdict(set)
    for key, values in aliases.items():
        for a in values:
            alias_owners[a].add(key)
    collisions = [{"alias": a, "labels": sorted(ks)} for a, ks in alias_owners.items() if len(ks) > 1]
    calibration = []
    for r in sessions[sessions.dataset_role.eq("content")].itertuples():
        base = fs_path(Path(args.raw) / r.manifest_relative).parent
        summary = load(base, "analysis/summary.json") if (base / "analysis/summary.json").exists() else {}
        values = {content_key(r.url)}
        final = (summary.get("navigation_outcome") or {}).get("final_url")
        if final:
            values.add(content_key(final))
        calibration.append({"session_id": r.session_id, "protocol": r.protocol,
                            "content_id": r.content_id, "repetition": r.repetition,
                            "overlaps_broad_observed_alias": bool(values & all_aliases),
                            "prior_route": r.route_decision,
                            "prior_generation_ok": r.generation_ok is True or r.generation_ok == True,
                            "summary_present": bool(summary),
                            "summary_generation_ok": summary.get("analysis_generation_id") == r.analysis_generation_id})
    # Existing entity ledger supplies Content and Detailed relationships only.
    # Broad is freshly rebuilt above. Fingerprint the imported inventory explicitly.
    entities = pd.read_parquet(source / "entity-graph.parquet")
    for r in entities[~entities.dataset_role.eq("broad")].itertuples():
        if r.entity_key:
            carrier_members[r.entity_key].add(r.session_id)
    shared = [{"entity": k, "session_ids": sorted(v),
               "roles": sorted({sid_role[s] for s in v}),
               "protocols": sorted({sid_protocol[s] for s in v})}
              for k, v in carrier_members.items() if len(v) > 1]
    v = pd.DataFrame(visits)
    cal = pd.DataFrame(calibration)
    summaries = []
    for protocol, group in v.groupby("protocol"):
        eligible = group.route.eq("proxy_success") & group.generation_ok & group.selection_ok & group.window_metadata_candidate
        c = cal[cal.protocol.eq(protocol) & ~cal.overlaps_broad_observed_alias
                & cal.prior_route.eq("proxy_success") & cal.prior_generation_ok & cal.summary_generation_ok
                & cal.repetition.isin([1, 2, 4, 5])]
        complete_c = int(c.groupby("content_id").repetition.nunique().eq(4).sum())
        summaries.append({"protocol": protocol, "visits": len(group),
                          "routes": dict(Counter(group.route)),
                          "metadata_proxy_visits": int(eligible.sum()),
                          "proxy_visits_with_tcp_candidate": int((eligible & group.exclusive_tcp_candidates.gt(0)).sum()),
                          "nonoverlap_four_repeat_content_candidates": complete_c,
                          "full64_metadata_route_gate": bool(eligible.all())})
    status = {"stage": "G1_requires_user_decision", "training_started": False,
              "plan_scope": "P00-P05 metadata qualification; raw identity and post-only eligibility remain pending",
              "protocols": summaries, "alias_collision_count": len(collisions),
              "shared_entity_components": len(shared),
              "broad_shared_components": sum(any(sid_role[s] == "broad" for s in x["session_ids"]) for x in shared),
              "unverified": ["PCAP content hashes and TCP instance replay", "W clock anchors and byte coverage",
                             "post-only eligible-flow selector", "semantic URL aliases beyond observed redirects",
                             "carrier graph across raw file identities", "final C/U/H split and calibration selection"],
              "source_sha256": {n: file_hash(source / n) for n in ["sessions.parquet", "entity-graph.parquet"]},
              "script_sha256": file_hash(Path(__file__))}
    out.mkdir(parents=True, exist_ok=True)
    for name, data in [("label-registry", registry), ("observed-aliases", {k: sorted(x) for k, x in aliases.items()}),
                       ("alias-collisions", collisions), ("carrier-components", shared), ("metadata-hashes", hashes)]:
        write(out / f"{name}.json", data)
    for name, data in [("broad-visits", visits), ("request-route-evidence", evidence),
                       ("flow-candidates", flows), ("calibration-candidates", calibration)]:
        pd.DataFrame(data).to_parquet(out / f"{name}.parquet", index=False)
    write(out / "status.json", status)
    print(json.dumps(status, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default="outputs/extend-calibration-20260930/run-01")
    parser.add_argument("--raw", default="Datasets/extend")
    parser.add_argument("--output", default="outputs/url64-flow-transfer-extend/run-01")
    run(parser.parse_args())
