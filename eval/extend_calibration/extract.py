"""Apply the approved lineage sidecar, then extract and gate W/T observations."""
from pathlib import Path
import sys
import argparse
import json
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from proxy_analysis.extend_calibration.audit import read, write, file_hash
from proxy_analysis.extend_calibration.extraction import extract_one


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    prior = ROOT / "outputs/extend-calibration-20260930/run-01"
    out = prior / "extraction-01"
    out.mkdir(exist_ok=True)
    overlay = pd.read_parquet(prior / "forensic-01/proposed-lineage-overlay.parquet")
    findings = pd.read_parquet(prior / "forensic-01/findings.parquet")
    audit = pd.read_parquet(prior / "primary-lineage-01/primary-document-lineage.parquet")
    assert len(overlay) == 7 and overlay.evidence_supported.all()
    assert set(overlay.session_id) == set(audit[audit.status == "different_successful_socket"].session_id)
    assert findings.resolution.eq("independent_chain_supported").all()
    pool = pd.read_parquet(prior / "forensic-01/cohort-after-label-acceptance.parquet")
    pool = pool[(pool.domain != "bilibili.com") & pool.repetition.isin([1,2,3,4]) & (pool.protocol != "hysteria2")].copy()
    assert len(pool) == 600 and pool.groupby("protocol").size().eq(120).all()
    # Only resolve the exact seven independently supported principal-route holds.
    pool["reasons"] = pool.apply(lambda r: json.dumps([v for v in json.loads(r.reasons)
        if not (r.session_id in set(overlay.session_id) and v == "primary_route_unresolved_or_direct")]), axis=1)
    assert pool.reasons.eq("[]").all()
    pool["metadata_candidate"] = True
    pool["training_eligible"] = False
    pool["W_status"] = "pending_raw_validation"
    pool["T_status"] = pool.protocol.map(lambda p: "not_applicable" if p == "anytls" else "pending_exclusive_tcp_validation")
    files = [Path(__file__), ROOT / "src/proxy_analysis/extend_calibration/extraction.py",
        ROOT / "src/proxy_analysis/protocol_normalization/tcp_ledger.py",
        ROOT / "src/proxy_analysis/sequences/tcp_state.py",
        ROOT / "src/proxy_analysis/parsing/packet_decoder.py", ROOT / "src/proxy_analysis/parsing/pcapng.py",
        prior / "forensic-01/proposed-lineage-overlay.parquet", prior / "primary-lineage-01/primary-document-lineage.parquet"]
    contract = {"version": "extend-WT-1", "input_and_code_hashes": {str(p.relative_to(ROOT)):file_hash(p) for p in files},
        "sessions": sorted(pool.session_id), "window": "manifest_utc_half_open",
        "scope": "all selected-protocol proxy members with physical binding; carrier union; excludes explicit failed-before-socket and DIRECT",
        "T_definition": "observed-unique raw-window exclusive TCP pairs, common Q1 nonempty on both sides",
        "raw_data_modified": False, "hy2": "measurement_only_not_in_this_classifier_pool",
        "overlay_approved_by_user": True, "training_allowed": False}
    if (out / "contract.json").exists():
        assert read(out / "contract.json") == contract, "frozen extraction code/input changed"
    else:
        write(out / "contract.json", contract)
        overlay["applied"] = True
        overlay["application_scope"] = "local principal-route qualification sidecar; original indexes unchanged"
        overlay.to_parquet(out / "accepted-lineage-overlay.parquet", index=False)
        pool.to_parquet(out / "metadata-qualified-pool.parquet", index=False)
    selected = pool.groupby("protocol", sort=True).head(1) if args.pilot else pool
    tasks = [(r, str(ROOT / "Datasets/extend"), str(out)) for r in selected.to_dict("records")]
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for i, result in enumerate(executor.map(extract_one, tasks), 1):
            results.append(result)
            print(f"Extract {i}/{len(tasks)} {result['protocol']} W={result['W_gate_passed']} T={result['T_common_pairs']}/{result['T_candidate_pairs']} {result['review_reasons']}", flush=True)
            write(out / "progress.json", {"completed_in_invocation":i, "total_in_invocation":len(tasks), "pilot":args.pilot, "training_performed":False})
    tag = "pilot" if args.pilot else "full"
    pd.DataFrame([v for r in results for v in r["W"]]).to_parquet(out / f"{tag}-W-features.parquet", index=False)
    pd.DataFrame([v for r in results for v in r["T"]]).to_parquet(out / f"{tag}-T-features.parquet", index=False)
    pd.DataFrame([{k:r[k] for k in ["session_id","protocol","members","carriers","missing_pre","missing_post","W_gate_passed","T_candidate_pairs","T_common_pairs"]} |
        {"review_reasons":json.dumps(r["review_reasons"])} for r in results]).to_parquet(out / f"{tag}-coverage.parquet", index=False)
    pd.DataFrame([{"session_id":r["session_id"], **c} for r in results for c in r["capture_audit"]]).to_parquet(out / f"{tag}-capture-audit.parquet", index=False)
    reasons = dict(Counter(x for r in results for x in r["review_reasons"]))
    gate = {"visits":len(results), "W_passed":sum(r["W_gate_passed"] for r in results), "reasons":reasons,
        "raw_bytes_scanned":sum(v["file_bytes"] for r in results for v in r["capture_audit"]),
        "training_performed":False, "passed":not reasons,
        "T_scope_validation_complete":False, "split_isolation_complete":False,
        "permission_packages_exported":False}
    write(out / f"{tag}-gate.json", gate)
    print(json.dumps(gate), flush=True)


if __name__ == "__main__":
    main()
