"""Approved 24-file O1 pilot, with separated preparation/extraction/audit."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import time

# Arrow first; this entry intentionally never imports torch or fits a model.
import pandas as pd
from .common import ROOT, EXTRACT, Q, PROTOCOLS, io_path, write, save, source_lock
from .pilot_worker import ReadBudget, extract
from proxy_analysis.observation.window_stats import FEATURES
from .packages import validate_worker_package

PRIOR = ROOT / "outputs/p-small-observation-validation-20261010/run-04"
AMENDMENT = ROOT / "plan/o1-pilot-scope-amendment-20261010.md"
BUDGET = 768325364
CALIBRATION_LABELS = {"bing.com::search_results_view", "developer.mozilla.org::document_view"}


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def read_json(path, ledger, purpose):
    path = Path(path).resolve()
    if path.suffix.lower() in {".pcap", ".pcapng", ".cap"} or path.name in {
        "netlog.json", "cdp.json", "mihomo-trace.jsonl"}:
        raise PermissionError("pilot_metadata_forbidden_input")
    raw = io_path(path).read_bytes()
    ledger.append({"path": str(path.relative_to(ROOT)), "purpose": purpose, "bytes": len(raw),
                   "sha256": digest_bytes(raw)})
    return json.loads(raw.decode("utf-8-sig"))


def prepare(out, ledger):
    original = read_json(PRIOR / "verification.json", ledger, "prior_stage_verification")
    assert original["passed"], "prior_metadata_stage_unaccepted"
    locked = read_json(PRIOR / "manifests/source-lock.json", ledger, "prior_source_lineage")
    # Added modules do not alter any previously sealed implementation.
    for name, expected in locked.items():
        assert digest_bytes(io_path(ROOT / name).read_bytes()) == expected, "sealed_source_changed:"+name
    pilot = read_json(PRIOR / "manifests/pilot-visits.json", ledger, "preregistered_members")["visits"]
    assert len(pilot) == 24 and len({r["session_id"] for r in pilot}) == 24
    assert all(r["fold"] != 0 for r in pilot)
    assert Counter(r["protocol"] for r in pilot) == Counter(dict.fromkeys(PROTOCOLS, 6))
    physical_path = PRIOR / "manifests/physical-files.parquet"
    ledger.append({"path": str(physical_path.relative_to(ROOT)), "purpose": "frozen_file_stat_manifest",
                   "sha256": digest_bytes(physical_path.read_bytes())})
    physical = pd.read_parquet(physical_path)
    selected = physical[physical.session_id.isin([r["session_id"] for r in pilot])].copy()
    assert len(selected) == 24 and selected.pilot.all() and selected.exists.all()
    assert int(selected.bytes.sum()) == BUDGET
    file_rows = selected.set_index("session_id").to_dict("index")
    roles = read_json(PRIOR / "manifests/cohort-and-roles.json", ledger, "calibration_permission_check")["roles"]
    windows = read_json(EXTRACT / "prepared-windows.json", ledger, "old_window_numeric_projection")
    windows = {r["session_id"]: r for r in windows}
    endpoint_registry = {}
    endpoint_evidence = []
    for protocol in PROTOCOLS:
        role = next(r for r in roles if r["target"] == protocol and r["outer"] == 0 and r["group"] == "G0")
        candidates = [r for r in pilot if r["protocol"] == protocol and r["label_id"] in CALIBRATION_LABELS]
        assert len(candidates) == 2
        confirmations = []
        for r in candidates:
            assert r["content_id"] in role["C_contents"] and r["content_id"] not in role["U_contents"]
            assert r["content_id"] not in role["validation_contents"]
            base = (ROOT / "Datasets/extend" / r["manifest_relative"]).parent
            doc = read_json(base / "analysis/flow-index.json", ledger, "self_owned_C_endpoint_registration_only")
            endpoints = set()
            count = 0
            for f in doc["items"]:
                sem = (f.get("proxy_semantics") or {}).get("protocol")
                sem = "shadowsocks" if sem == "ss" else sem
                if f.get("egress_outcome") != "proxy" or sem != protocol:
                    continue
                # No common-valid-pair or client socket selection is made here.
                for p in [f.get("post_flow") or {}, *((f.get("carrier_binding") or {}).get("physical_paths") or [])]:
                    if p.get("network") == "tcp" and p.get("dst_ip") and p.get("dst_port"):
                        endpoints.add((p["dst_ip"], int(p["dst_port"])))
                        count += 1
            assert len(endpoints) == 1, "ambiguous_calibration_endpoint_registry"
            confirmations.append(endpoints)
            endpoint_evidence.append({"protocol": protocol, "session_id": r["session_id"],
                                      "role_id": role["id"], "permission": "C",
                                      "eligible_tcp_path_evidence_count": count, "endpoint_count": len(endpoints)})
        assert confirmations[0] == confirmations[1], "cross_calibration_endpoint_disagreement"
        endpoint_registry[protocol] = [{"address": address, "port": port}
                                      for address, port in sorted(confirmations[0])]
    write(out, "private/endpoint-registry.json", {"endpoints": endpoint_registry,
          "source": "self_owned_fold0_G0_C_only", "frozen_before_raw_open": True,
          "endpoint_known_from_calibration": True, "public_report_addresses": False,
          "evidence": endpoint_evidence})
    endpoint_sha = digest_bytes((out / "private/endpoint-registry.json").read_bytes())
    packages, joins = [], []
    for r in pilot:
        f = file_rows[r["session_id"]]
        w = windows[r["session_id"]]
        assert w["start_ns"] == r["window_start_ns"] and w["end_ns"] == r["window_end_ns"]
        package = {"visit_token": f["visit_token"], "physical_path": str(ROOT / f["path"]),
                   "endpoints": endpoint_registry[r["protocol"]], "windows": [{"version": "O1",
                   "start_ns": int(w["start_ns"]), "end_ns": int(w["end_ns"]), "coverage_verified": False}]}
        validate_worker_package(package)
        packages.append(package)
        joins.append({**r, "visit_token": f["visit_token"], "file_bytes": int(f["bytes"])})
    write(out, "private/worker-packages.json", packages)
    write(out, "audit/visit-join.json", joins)
    source = source_lock()
    write(out, "manifests/source-lock.json", source)
    contract = {"version": "O1-pilot-1", "scope": "conditional_old_window_physical_only_engineering",
                "user_authorization": "同意先按上述范围执行O1先导", "visits": 24,
                "raw_byte_limit": BUDGET, "raw_unique_open_limit": 24, "raw_passes_per_file": 1,
                "membership_manifest_sha256": digest_bytes((PRIOR / "manifests/pilot-visits.json").read_bytes()),
                "old_plan_sha256": digest_bytes((ROOT / "plan/p-small-observation-validation-retraining-cross-batch-plan-20261010.md").read_bytes()),
                "scope_amendment_sha256": digest_bytes(AMENDMENT.read_bytes()),
                "endpoint_registry_sha256": endpoint_sha,
                "worker_packages_sha256": digest_bytes((out / "private/worker-packages.json").read_bytes()),
                "prior_sources_unchanged": True, "old_windows_browser_conditioned": True,
                "independent_fixed_window_qualified": False, "O2_authorized": False,
                "full480_authorized": False, "classifier_fits": 0, "model_inference": 0,
                "test_pre_reads": 0, "tun_reads": 0, "netlog_reads": 0, "cdp_reads": 0,
                "same_isn_after_terminal_policy": "conservative ambiguity extension; no guessed split"}
    write(out, "manifests/observation-contract.json", contract)
    return packages, joins


def cache_audit(result, join, old_features, out, ledger):
    """After extraction only: paired cache does not select physical members."""
    path = EXTRACT / "sessions" / join["session_id"] / "post-W-events.parquet"
    ledger.append({"path": str(path.relative_to(ROOT)), "purpose": "post_only_offline_same_window_replay",
                   "sha256": digest_bytes(path.read_bytes())})
    old = pd.read_parquet(path)
    event_map = {(e["timestamp_ns"], e["ordinal"]): e for e in result["events"]}
    assert len(event_map) == len(result["events"]), "physical_event_identity_not_unique"
    missing, difference = [], []
    carrier_instances = defaultdict(set)
    for r in old.to_dict("records"):
        key = (int(r["timestamp_ns"]), int(r["raw_packet_ordinal"]))
        found = event_map.get(key)
        if found is None:
            missing.append({"timestamp_ns": key[0], "ordinal": key[1]})
        elif found["direction"] != r["direction"] or found["observed_bytes"] != r["payload_bytes"]:
            difference.append({"timestamp_ns": key[0], "ordinal": key[1]})
        else:
            carrier_instances[r["entity_id"]].add(found["instance_token"])
    conns = {c["instance_token"]: c for c in result["connections"]}
    comparisons = []
    for r in old_features[old_features.session_id.eq(join["session_id"])].to_dict("records"):
        instances = carrier_instances.get(r["carrier_id"], set())
        mismatches = []
        if len(instances) == 1:
            physical = conns[next(iter(instances))]["statistics"]
            mismatches = [k for k in FEATURES if int(r["post_"+k]) != physical[k]]
        comparisons.append({"carrier_token": digest_bytes(r["carrier_id"].encode()),
                            "physical_epoch_count": len(instances), "mismatch_features": mismatches,
                            "exact": len(instances) == 1 and not mismatches})
    audit = {"visit_token": join["visit_token"], "old_positive_packets": len(old),
             "physical_positive_packets": len(result["events"]), "missing_old_packets": len(missing),
             "packet_value_mismatches": len(difference), "paired_post_connections": len(comparisons),
             "exact_ten_stat_replays": sum(c["exact"] for c in comparisons),
             "paired_post_mismatches": [c for c in comparisons if not c["exact"]],
             "physical_extra_positive_packets": len(result["events"])-len(old)+len(missing),
             "old_membership_not_worker_input": True, "old_time_boundary_unchanged": True,
             "pre_columns_read": 0, "missing_examples": missing[:10], "value_examples": difference[:10]}
    write(out, "audit/replay/"+join["visit_token"]+".json", audit)
    return audit


def run(out):
    out = Path(out).resolve()
    if out.exists():
        raise FileExistsError("new pilot output required; do not overwrite or silently resume")
    if not out.is_relative_to(ROOT / "outputs/p-small-observation-validation-20261010"):
        raise PermissionError("output_root")
    ledger = []
    started = time.monotonic()
    from .tests import run as old_tests
    from .pilot_tests import run as extra_tests
    tests = {"original": old_tests(), "pilot": extra_tests()}
    assert all(t["passed"] for t in tests.values())
    write(out, "manifests/engineering-tests.json", tests)
    packages, joins = prepare(out, ledger)
    budget = ReadBudget([(p["physical_path"], j["file_bytes"]) for p, j in zip(packages, joins)], BUDGET)
    results = []
    for index, (package, join) in enumerate(zip(packages, joins), 1):
        print("O1 physical pilot", index, "/ 24", join["protocol"], flush=True)
        result = extract(package, budget)
        write(out, "pilot/by-visit/"+join["visit_token"]+".json", result)
        results.append(result)
        write(out, "progress.json", {"stage": "O1_extraction", "done": index, "total": 24,
                                    "actual_raw_bytes": budget.bytes, "elapsed_seconds": time.monotonic()-started})
    assert len(budget.opened) == 24 and budget.bytes == BUDGET
    # post-only projection, restricted to the 24 training parents; no pre values.
    feature_path = Q / "features/paired-flow-features.parquet"
    ledger.append({"path": str(feature_path.relative_to(ROOT)), "purpose": "post_columns_only_pilot_parents_offline_replay",
                   "columns": ["session_id", "carrier_id"]+["post_"+k for k in FEATURES],
                   "session_ids": [j["session_id"] for j in joins]})
    cached = pd.read_parquet(feature_path, columns=["session_id", "carrier_id"]+["post_"+k for k in FEATURES],
                             filters=[("session_id", "in", [j["session_id"] for j in joins])])
    replay = [cache_audit(r, j, cached, out, ledger) for r, j in zip(results, joins)]
    connections = [c for r in results for c in r["connections"]]
    visits = []
    for r, j in zip(results, joins):
        v = r["visit"]
        visits.append({"visit_token": j["visit_token"], "session_id": j["session_id"],
                       "protocol": j["protocol"], "label_id": j["label_id"], "fold": j["fold"],
                       **{k: value for k, value in v.items() if k != "x"}, **(v["x"] or {})})
    save(out, "pilot/visits.parquet", pd.DataFrame(visits))
    save(out, "pilot/connections.parquet", pd.DataFrame([{**{k:v for k,v in c.items() if k != "statistics"},
                                                         **c["statistics"]} for c in connections]))
    witnesses = defaultdict(set)
    instances = defaultdict(set)
    for result in results:
        for w in result["duplicate_evidence"]:
            witnesses[w["witness"]].add((w["visit_token"], w["instance_token"]))
        for c in result["connections"]:
            instances[c["instance_token"]].add(c["visit_token"])
    shared = [{"witness": w, "visits": sorted({v for v, _ in owners})}
              for w, owners in witnesses.items() if len({v for v, _ in owners}) > 1]
    duplicate_instances = [{"instance_token": k, "visits": sorted(v)} for k, v in instances.items() if len(v) > 1]
    write(out, "audit/epoch-leakage.json", {"scope": "24 pilot files only, not full480",
          "exact_packet_time_socket_witnesses_shared": shared, "instance_tokens_shared": duplicate_instances,
          "raw_fingerprint_alone_used_as_identity": False, "full_cohort_leakage_verified": False})
    raw_audits = [r["audit"] for r in results]
    write(out, "audit/raw-read-ledger.json", raw_audits)
    write(out, "audit/metadata-access.json", ledger)
    reasons = Counter(reason for c in connections if c["nonempty"] for reason in c["reasons"])
    summary = {"files": 24, "raw_bytes": budget.bytes, "single_pass": True,
               "raw_records": sum(a["raw_records"] for a in raw_audits),
               "epochs": len(connections), "nonempty_epochs": sum(c["nonempty"] for c in connections),
               "invalid_nonempty_epochs": sum(c["nonempty"] and not c["valid"] for c in connections),
               "valid_visits": sum(r["visit"]["status"] == "valid" for r in results),
               "invalid_visits": sum(r["visit"]["status"] != "valid" for r in results),
               "nonempty_epoch_reasons": dict(reasons),
               "capture_failure_visits": sum(bool(a["failures"]) for a in raw_audits),
               "old_positive_packets": sum(a["old_positive_packets"] for a in replay),
               "physical_positive_packets": sum(a["physical_positive_packets"] for a in replay),
               "missing_old_packets": sum(a["missing_old_packets"] for a in replay),
               "packet_value_mismatches": sum(a["packet_value_mismatches"] for a in replay),
               "paired_post_connections": sum(a["paired_post_connections"] for a in replay),
               "exact_ten_stat_replays": sum(a["exact_ten_stat_replays"] for a in replay),
               "duplicate_packet_witness_groups": len(shared), "duplicate_instance_groups": len(duplicate_instances),
               "classifier_fits": 0, "model_inference": 0, "pre_capture_reads": 0,
               "netlog_reads": 0, "cdp_reads": 0, "elapsed_seconds": time.monotonic()-started,
               "independent_fixed_window_qualified": False, "full480_started": False}
    write(out, "pilot/summary.json", summary)
    passed = (summary["valid_visits"] == 24 and not summary["capture_failure_visits"]
              and not summary["missing_old_packets"] and not summary["packet_value_mismatches"]
              and summary["paired_post_connections"] == summary["exact_ten_stat_replays"]
              and not shared and not duplicate_instances)
    write(out, "pilot/gate.json", {"O1_engineering_pilot_passed": passed,
          "full480_authorized": False, "O2_qualified": False, "stageA_complete": False,
          "next": "A17_user_budget_decision" if passed else "inspect_engineering_or_observation_failures",
          "no_automatic_full_scan_training_or_scoring": True})
    write(out, "progress.json", {"stage": "O1_pilot_extraction_complete", "files": 24,
          "raw_bytes": budget.bytes, "engineering_gate_passed": passed})
    # Seal generated artifacts, never reread raw input for hashing.
    files = {str(p.relative_to(out)): digest_bytes(p.read_bytes()) for p in out.rglob("*") if p.is_file()}
    write(out, "seal.json", {"files": files, "source_lock_sha256": digest_bytes((out/"manifests/source-lock.json").read_bytes()),
                             "no_raw_rehash": True})
    from .pilot_verify import verify
    verify(out)
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT/"outputs/p-small-observation-validation-20261010/pilot-01")
    args = parser.parse_args()
    run(args.out)
