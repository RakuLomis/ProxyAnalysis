"""Metadata-only coverage evidence. Never use NetLog to create O2 UTC times."""
from collections import Counter
from decimal import Decimal
import hashlib
from .common import *


def run(out, parents, pilot):
    import pandas as pd
    old = {w["session_id"]: w for w in read(EXTRACT / "prepared-windows.json")}
    rows, inputs, file_rows, endpoints = [], {}, [], []
    pilot_ids = set(pilot.session_id)
    for row in parents.to_dict("records"):
        base = (ROOT / "Datasets/extend" / row["manifest_relative"]).parent
        manifest_path = base / "manifest.json"
        context_path = base / "raw/capture-context.json"
        proxy_path = base / "raw/proxy-info.json"
        manifest = read(manifest_path)
        context = read(context_path)
        info = read(proxy_path)
        for p in [manifest_path, context_path, proxy_path]:
            inputs[str(p.relative_to(ROOT))] = sha(p)
        c = context["packet_coverage"]
        ready = Decimal(str(c["ready"]["physical"]))
        nav = Decimal(str(c["navigation_requested"]))
        quiet = Decimal(str(c["browser_quiescent"]))
        stop = Decimal(str(c["stopped"]["physical"]))
        assert c["clock"] == "monotonic_seconds" and ready <= nav < quiet <= stop
        assert manifest["session_id"] == row["session_id"]
        w = old[row["session_id"]]
        assert w["start_ns"] == row["window_start_ns"] and w["end_ns"] == row["window_end_ns"]
        # Node-independent info contains server/port slots but may redact them.
        # Store only presence/evidence, not credentials or selection chains.
        entries = info if isinstance(info, list) else [info]
        selected = [v for v in entries if v.get("group") == context.get("orchestration", {}).get("selection_group")]
        endpoint_present = any(v.get("server") and v.get("port") for v in selected)
        endpoints.append({"session_id": row["session_id"], "protocol": row["protocol"],
                          "source": str(proxy_path.relative_to(ROOT)),
                          "known_endpoint_values_available": endpoint_present,
                          "selected_group_entry_found": bool(selected), "worker_endpoint_registered": False})
        raw = base / "raw/phys.pcap"
        try:
            st = io_path(raw).stat()  # No open/read/hash of capture contents.
            size, exists = st.st_size, True
        except FileNotFoundError:
            size, exists = None, False
        token = hashlib.sha256(("physical-observation-v1:"+row["session_id"]).encode()).hexdigest()
        file_rows.append({"visit_token": token, "session_id": row["session_id"],
             "path": str(raw.relative_to(ROOT)), "exists": exists, "bytes": size,
             "pilot": row["session_id"] in pilot_ids, "content_read": False})
        rows.append({"session_id": row["session_id"], "protocol": row["protocol"],
             "label_id": row["label_id"], "fold": row["fold"], "repetition": row["repetition"],
             "clock": c["clock"], "t0_source": "packet_coverage.navigation_requested",
             "t0_monotonic_seconds": str(nav), "t0_permission": "given_activity_start_not_external_trigger",
             "t0_UTC_ns": None, "independent_monotonic_to_PCAP_clock_anchor": False,
             "metadata_nominal_nav_to_quiescent_seconds": float(quiet-nav),
             "metadata_nav_to_stop_completion_seconds": float(stop-nav),
             "metadata_physical_ready_to_nav_seconds": float(nav-ready),
             "physical_exit_code": c["exit"]["physical"]["code"],
             "physical_killed": c["exit"]["physical"]["killed"],
             "capture_status": c["status"], "drops": str(c.get("drops", "unknown")),
             "last_live_capture_boundary_verified": False, "coverage_proven": False,
             "nominal_30s_before_browser_quiescent": quiet-nav >= 30,
             "O1_start_ns": w["start_ns"], "O1_end_ns": w["end_ns"],
             "O1_clock_source": "frozen_old_NetLog_conversion_diagnostic_only",
             "manifest_started_at": manifest["started_at"],
             "manifest_completed_at": manifest["completed_at"]})
    frame = pd.DataFrame(rows)
    files = pd.DataFrame(file_rows)
    endpoint_frame = pd.DataFrame(endpoints)
    assert len(frame) == 480 and frame.session_id.is_unique
    save(out, "windows/coverage-inventory.parquet", frame)
    save(out, "windows/start-evidence.parquet", frame[["session_id", "clock", "t0_source",
         "t0_monotonic_seconds", "t0_permission", "t0_UTC_ns", "independent_monotonic_to_PCAP_clock_anchor"]])
    save(out, "manifests/physical-files.parquet", files)
    save(out, "manifests/endpoint-evidence.parquet", endpoint_frame)
    write(out, "manifests/metadata-input-hashes.json", inputs)
    nominal = frame.metadata_nominal_nav_to_quiescent_seconds
    summary = {"visits": len(frame), "existing_physical_files": int(files.exists.sum()),
        "physical_file_bytes_stat_only": int(files.bytes.sum()),
        "pilot_files": int(files.pilot.sum()), "pilot_bytes_stat_only": int(files[files.pilot].bytes.sum()),
        "nominal_nav_to_quiescent_seconds": {"min": float(nominal.min()), "median": float(nominal.median()), "max": float(nominal.max())},
        "nominal_30s_compatible_count": int(frame.nominal_30s_before_browser_quiescent.sum()),
        "independent_UTC_clock_anchor_count": 0, "proven_fixed_window_coverage_count": 0,
        "proxy_info_endpoint_values_available_count": int(endpoint_frame.known_endpoint_values_available.sum()),
        "drops": dict(Counter(frame.drops)), "stop_is_shutdown_completion_not_capture_live_boundary": True,
        "PCAP_reads": 0, "pre_capture_reads": 0, "NetLog_reads": 0, "CDP_reads": 0}
    write(out, "windows/coverage-summary.json", summary)
    write(out, "windows/window-proposal.json", {
        "T_seconds": None, "T_frozen": False, "O2_qualified": False,
        "nominal_candidate_seconds": 30 if summary["nominal_30s_compatible_count"] == 480 else None,
        "candidate_is_metadata_feasibility_only": True,
        "blocking_conditions": ["independent_monotonic_to_capture_clock_anchor_missing",
                                "live_fixed_window_coverage_not_independently_verified",
                                "known_proxy_endpoint_registry_not_supplied"],
        "no_F1_used": True, "no_NetLog_offset_imported_for_O2": True,
        "required_user_decision": "provide timing/endpoint evidence or authorize explicitly restricted O1-only pilot"})
    write(out, "manifests/endpoint-contract.json", {
        "status": "not_registered", "endpoint_filter_is_allowed_metadata": True,
        "endpoint_model_feature": False, "raw_endpoint_values_published": False,
        "missing_selected_info_count": int((~endpoint_frame.selected_group_entry_found).sum()),
        "endpoint_values_present_count": int(endpoint_frame.known_endpoint_values_available.sum()),
        "pair_tuple_inference_forbidden": True})
    return summary
