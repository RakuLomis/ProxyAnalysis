"""Strict worker schema; labels and offline membership cannot enter extraction."""
from pathlib import Path

FIELDS = {"visit_token", "physical_path", "endpoints", "windows"}
WINDOW_FIELDS = {"version", "start_ns", "end_ns", "coverage_verified"}


def validate_worker_package(package):
    if set(package) != FIELDS:
        raise PermissionError("worker_schema_has_forbidden_or_missing_fields")
    token = package["visit_token"]
    if not isinstance(token, str) or len(token) != 64 or any(c not in "0123456789abcdef" for c in token):
        raise ValueError("invalid_opaque_token")
    if Path(package["physical_path"]).name != "phys.pcap":
        raise PermissionError("worker_only_all_physical_capture")
    if not package["endpoints"]:
        raise ValueError("endpoint_registry_missing")
    for e in package["endpoints"]:
        if set(e) != {"address", "port"}:
            raise PermissionError("endpoint_schema")
    for w in package["windows"]:
        if set(w) != WINDOW_FIELDS or w["version"] not in {"O1", "O2"}:
            raise PermissionError("window_schema")
        if not isinstance(w["start_ns"], int) or not isinstance(w["end_ns"], int) or w["end_ns"] <= w["start_ns"]:
            raise ValueError("invalid_window")
    return True
