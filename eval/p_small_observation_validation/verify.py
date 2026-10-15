"""Independent metadata/permission verification, not a fake physical-data gate."""
from .common import *


def run(out):
    state = read(Path(out) / "progress.json")
    c = read(Path(out) / "manifests/baseline-inventory.json")
    assert len(c["models"]) == 360
    assert state["PCAP_reads"] == state["new_classifier_fits"] == state["real_model_inferences"] == 0
    assert not state["stage_A_complete"] and not state["O2_qualified"]
    for path, expected in state["source_sha256"].items():
        assert sha(ROOT / path) == expected
    for path, expected in read(Path(out) / "manifests/metadata-input-hashes.json").items():
        assert sha(ROOT / path) == expected
    for r in c["models"]:
        assert sha(ROOT / r["model_path"]) == r["model_sha256"]
    ledger = read(Path(out) / "manifests/access-log.json")
    for entry in ledger:
        safe_read_path(ROOT / entry["path"])
    parents = parquet(Path(out) / "manifests/parents.parquet")
    pilot = read(Path(out) / "manifests/pilot-visits.json")["visits"]
    assert len(parents) == 480 and len(pilot) == 24
    assert all(v["fold"] != 0 and v["repetition"] == 1 for v in pilot)
    assert len({(v["protocol"], v["label_id"]) for v in pilot}) == 24
    files = {}
    for p in sorted(Path(out).rglob("*")):
        if p.is_file() and p.name not in {"verification.json", "failure.json"}:
            files[str(p.relative_to(ROOT))] = sha(p)
    return {"passed": True, "scope": "metadata_preflight_and_synthetic_tests_only",
          "PCAP_reads": 0, "new_classifier_fits": 0, "raw_extraction_validated": False,
          "O2_qualified": False, "files": files, **timestamp()}
