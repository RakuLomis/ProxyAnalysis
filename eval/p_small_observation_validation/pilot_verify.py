"""Artifact-only verification; never opens raw captures or old models."""
import argparse
import hashlib
import json
from pathlib import Path
from .common import ROOT, write, io_path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    if Path(path).suffix.lower() in {".pcap", ".pcapng", ".cap"}:
        raise PermissionError("verifier_no_raw_open")
    return hashlib.sha256(io_path(path).read_bytes()).hexdigest()


def verify(out):
    out = Path(out).resolve()
    seal = load(out / "seal.json")
    for rel, expected in seal["files"].items():
        assert sha(out / rel) == expected, "artifact_changed:"+rel
    for rel, expected in load(out / "manifests/source-lock.json").items():
        assert sha(ROOT / rel) == expected, "source_changed:"+rel
    contract = load(out / "manifests/observation-contract.json")
    ledger = load(out / "audit/raw-read-ledger.json")
    assert len(ledger) == 24 and len({r["visit_token"] for r in ledger}) == 24
    assert sum(r["bytes_read"] for r in ledger) == contract["raw_byte_limit"] == 768325364
    assert all(r["raw_open_count"] == 1 and r["bytes_read"] == r["file_bytes"] for r in ledger)
    assert all(r["partition_verified"] and r["independent_counters_verified"] for r in ledger)
    assert not contract["O2_authorized"] and not contract["full480_authorized"]
    assert not contract["classifier_fits"] and not contract["model_inference"]
    packages = load(out / "private/worker-packages.json")
    from .packages import validate_worker_package
    for p in packages:
        validate_worker_package(p)
        assert len(p["windows"]) == 1 and p["windows"][0]["version"] == "O1"
    accesses = load(out / "audit/metadata-access.json")
    index = [r for r in accesses if Path(r["path"]).name == "flow-index.json"]
    assert len(index) == 8 and all(r["purpose"] == "self_owned_C_endpoint_registration_only" for r in index)
    assert not any(Path(r["path"]).name in {"netlog.json", "cdp.json", "tun.pcap", "mihomo-trace.jsonl"} for r in accesses)
    # Rehash allowed metadata only; the streaming raw hashes are not reread.
    for r in accesses:
        if "sha256" in r:
            assert sha(ROOT / r["path"]) == r["sha256"], "metadata_changed"
    result = {"passed": True, "scope": "artifact_integrity_permission_and_counter_audit_not_classification",
              "files_verified": len(seal["files"]), "raw_files_reopened": 0,
              "engineering_gate": load(out / "pilot/gate.json"), "O2_qualified": False,
              "stageA_complete": False, "full480_leakage_verified": False}
    write(out, "verification.json", result)
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=ROOT/"outputs/p-small-observation-validation-20261010/pilot-01")
    print(json.dumps(verify(p.parse_args().out), ensure_ascii=False))
