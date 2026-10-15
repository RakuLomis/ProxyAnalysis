"""No model training, inference or raw capture opening in this stage."""
import platform
from .common import *


def run(out):
    # On this Windows environment torch-before-pyarrow can abort the process
    # in native DLL initialization. Keep the established pandas/Arrow-first
    # import order; no package upgrade or DLL/environment alteration.
    import pandas as pd
    import torch
    print("inventory: verifying frozen baseline", flush=True)
    contract_path = BASE / "manifests/experiment-contract.json"
    contract = read(contract_path)
    assert sha(contract_path) == read(BASE / "manifests/seal.json")["contract_sha256"]
    completion = read(BASE / "completion.json")
    verification = read(BASE / "verification.json")
    assert completion["passed"] and verification["passed"]
    assert sha(BASE / "verification.json") == completion["verification_sha256"]
    for path, expected in verification["files"].items():
        assert sha(ROOT / path) == expected, "old_verified_artifact_changed"
    print("inventory: verified baseline outputs", flush=True)
    # Check old code lineage without importing old common.py / OUT globals.
    for path, expected in {**contract["historical_source_sha256"], **contract["source_sha256"]}.items():
        assert sha(ROOT / path) == expected, "old_code_changed:" + path
    print("inventory: verified source lineage", flush=True)
    refs = list(contract["references"])
    new = parquet(BASE / "manifests/new-endpoints.parquet")
    print("inventory: opened model registry", flush=True)
    refs += new[["role_id", "arm", "model_path", "model_sha256"]].to_dict("records")
    assert len(refs) == 360 and len({(r["role_id"], r["arm"]) for r in refs}) == 360
    for ref in refs:
        path = ROOT / ref["model_path"]
        assert sha(path) == ref["model_sha256"], "old_model_changed"
        sidecar = read(path.with_suffix(".json"))
        assert sidecar["sha256"] == ref["model_sha256"]
        if "optimizer" in sidecar:
            assert sidecar["optimizer"]["accepted"], "unaccepted_old_model"
    print("inventory: verified 360 frozen models", flush=True)
    roles = contract["roles"]
    assert len(roles) == 60 and all(r["inner"] is None for r in roles)
    parents = parquet(Q / "cohorts/parents.parquet")
    parents = parents[parents.protocol.isin(PROTOCOLS)].copy()
    folds = parquet(Q / "cohorts/folds.parquet")
    assert len(parents) == 480 and parents.session_id.is_unique
    assert parents.groupby("protocol").size().eq(120).all()
    assert set(parents.repetition) == {1, 2, 3, 4}
    assert len(folds) == 30 and folds.groupby(["fold", "label_id"]).size().eq(1).all()
    assert parents.content_id.map(folds.set_index("content_id").fold).eq(parents.fold).all()
    for r in roles:
        assert not set(r["train_contents"]) & set(r["validation_contents"])
        assert set(r["C_contents"]) | set(r["U_contents"]) == set(r["train_contents"])
        assert not set(r["C_contents"]) & set(r["U_contents"])
        assert len(r["sources"]) == 3 and r["target"] not in r["sources"]
    sessions = parquet(ROOT / "outputs/extend-calibration-20260930/run-01/sessions.parquet")
    sessions = sessions[sessions.session_id.isin(parents.session_id)][["session_id", "manifest_relative"]]
    assert sessions.session_id.is_unique and len(sessions) == 480
    joined = parents.merge(sessions, on="session_id", validate="one_to_one")
    # Development selection is independent of outcomes and model predictions.
    dev = joined[joined.fold.ne(0)]
    selected_contents = dev.groupby("label_id").content_id.min().tolist()
    pilot = dev[dev.content_id.isin(selected_contents) & dev.repetition.eq(dev.repetition.min())]
    pilot = pilot.sort_values(["protocol", "label_id"])
    assert len(pilot) == 24 and pilot.groupby(["protocol", "label_id"]).size().eq(1).all()
    env = {"python": __import__("sys").executable, "python_version": platform.python_version(),
           "torch": torch.__version__, "cuda": torch.version.cuda,
           "cuda_available": torch.cuda.is_available(), "dependencies_installed": False}
    assert env["cuda_available"], "CUDA required, no CPU fallback"
    env["gpu"] = torch.cuda.get_device_name(0)
    # Availability/float64 execution smoke test, not model inference.
    x = torch.arange(8, dtype=torch.float64, device="cuda")
    env["float64_smoke_sum"] = float(x.sum())
    assert env["float64_smoke_sum"] == 28
    env["real_model_inference_count"] = 0
    write(out, "manifests/environment.json", env)
    write(out, "manifests/baseline-inventory.json", {
        "contract_sha256": sha(contract_path), "completion": completion,
        "models": refs, "model_count": len(refs), "new_classifier_fits": 0,
        "old_prediction_sha256": sha(BASE / "predictions/visits.parquet")})
    write(out, "manifests/cohort-and-roles.json", {"roles": roles, "visits": 480,
          "contents": 30, "global_folds": 5, "protocols": PROTOCOLS,
          "target_U_training_numeric_packages_read": 0, "test_pre_reads": 0})
    save(out, "manifests/parents.parquet", joined)
    save(out, "manifests/folds.parquet", folds)
    write(out, "manifests/pilot-visits.json", {"selection": "fold0_training_lexical_first_content_per_label_min_repeat",
          "prediction_used_for_selection": False, "visits": pilot.to_dict("records"), "count": 24})
    write(out, "audit/o0-scope.json", {"scope": "common-window packet events, not complete lifetime TCP bytes",
          "evidence": {
              "extraction_implementation_sha256": sha(ROOT / "src/proxy_analysis/extend_calibration/extraction_v3.py"),
              "feature_implementation_sha256": sha(ROOT / "eval/protocol_probability_drift/features.py"),
              "prepared_windows_sha256": sha(EXTRACT / "prepared-windows.json")},
          "original_selection": "offline mapped members and common_valid_nonempty pre/post pairs",
          "O1_same_time_boundary_possible": True, "matched_count_replay_completed": False,
          "actual_cached_events_reopened": False,
          "scope_confidence": "implementation_and_frozen_metadata; packet replay awaits PCAP gate"})
    write(out, "manifests/cache-usability.json", {
          "existing_pair_features_recover_all_endpoint_connections": False,
          "full_W_full_T_visit_totals_recover_96D": False,
          "raw_capture_required_if_pilot_approved": True,
          "PCAP_reads": 0, "new_classifier_fits": 0})
    return joined, pilot
