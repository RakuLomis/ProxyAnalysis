"""Quality gates over checkpointed feature records."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable

import pyarrow.parquet as pq


def _rows(feature_root: Path, filename: str) -> Iterable[dict[str, Any]]:
    for path in sorted(feature_root.glob(f"*/*/{filename}")):
        yield from pq.read_table(path).to_pylist()


def _close(a: Any, b: Any, tolerance: float = 1e-9) -> bool:
    return isinstance(a, (int, float)) and isinstance(b, (int, float)) and math.isclose(
        float(a), float(b), rel_tol=tolerance, abs_tol=tolerance
    )


def build_quality_report(feature_root: Path | str, *, expected_session_ids: Iterable[str] | None = None) -> dict[str, Any]:
    root = Path(feature_root)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    statuses = []
    for path in sorted(root.glob("*/*/status.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        statuses.append(value)
        if value.get("state") != "complete":
            errors.append({"code": "session_not_complete", "path": str(path)})

    entity_rows = list(_rows(root, "entity-features.parquet"))
    pair_rows = list(_rows(root, "exclusive-pair-features.parquet"))
    hy2_rows = list(_rows(root, "hysteria2-window-features.parquet"))
    web_rows = list(_rows(root, "web-features.parquet"))

    for row in entity_rows:
        feature = json.loads(row["features_json"])
        record = row["record_id"]
        if feature.get("unknown_direction_count") != 0:
            errors.append(
                {
                    "code": "unknown_direction",
                    "record_id": record,
                    "count": feature.get("unknown_direction_count"),
                }
            )
        volume = feature["volume"]
        for metric in ("packets", "transport_bytes", "ip_bytes", "captured_bytes"):
            if volume[f"up_{metric}"] + volume[f"down_{metric}"] != volume[f"total_{metric}"]:
                errors.append(
                    {"code": "directional_volume_mismatch", "record_id": record, "metric": metric}
                )
        endpoint = feature["cumulative_shape"]["normalized_time"][
            "absolute_transport_bytes"
        ][-1]
        if not _close(endpoint, volume["total_transport_bytes"]):
            errors.append({"code": "cumulative_endpoint_mismatch", "record_id": record})

        transition = feature["transition_nonempty"]
        transition_count = sum(
            transition[key] for key in ("n_pp", "n_pm", "n_mp", "n_mm")
        )
        expected_transition = max(transition["packet_count"] - 1, 0)
        if transition_count != expected_transition:
            errors.append({"code": "transition_count_mismatch", "record_id": record})

        reversal_key = (
            "carrier_datagram_reversal"
            if feature["transport_protocol"] == "udp"
            else "flow_reversal"
        )
        reversal = feature[reversal_key]["observed"]
        count = reversal["nonempty_packet_count"]
        runs = reversal["fr_runs"]
        if (count == 0 and runs != 0) or (count > 0 and not 1 <= runs <= count):
            errors.append({"code": "fr_bounds", "record_id": record})

    for row in pair_rows:
        feature = json.loads(row["features_json"])
        if feature["protocol_dataset"] == "HYSTERIA2":
            errors.append({"code": "hy2_exclusive_pair", "record_id": row["record_id"]})
        if row.get("group_carrier_id") is not None:
            errors.append({"code": "exclusive_pair_has_carrier_group", "record_id": row["record_id"]})

    for row in hy2_rows:
        feature = json.loads(row["features_json"])
        expected_carrier_group = f"{row['session_id']}::{feature.get('carrier_id')}"
        if row.get("group_carrier_id") != expected_carrier_group:
            errors.append({"code": "hy2_carrier_group_mismatch", "record_id": row["record_id"]})
        for window_name in ("inner_union_envelope", "carrier_full_lifetime"):
            preservation = feature[window_name]["comparison"]["flow_reversal_preservation"]
            if preservation.get("applicable") is not False:
                errors.append(
                    {"code": "hy2_fr_preservation_enabled", "record_id": row["record_id"]}
                )

    for row in web_rows:
        feature = json.loads(row["features_json"])
        if feature.get("privacy", {}).get("full_url_stored") is not False:
            errors.append({"code": "web_full_url_present", "record_id": row["record_id"]})

    config_hashes = {
        row["feature_config_sha256"]
        for rows in (entity_rows, pair_rows, hy2_rows, web_rows)
        for row in rows
    }
    if len(config_hashes) > 1:
        errors.append({"code": "mixed_feature_config_hashes", "count": len(config_hashes)})

    session_count = len(statuses)
    status_ids = [s.get("session_id") for s in statuses]
    if not statuses:
        errors.append({"code": "empty_feature_dataset"})
    if len(set(status_ids)) != session_count:
        errors.append({"code": "duplicate_session_status"})
    if expected_session_ids is not None:
        expected_ids = set(expected_session_ids)
        if set(status_ids) != expected_ids:
            errors.append({"code": "session_selection_mismatch",
                           "missing": sorted(expected_ids - set(status_ids)),
                           "unexpected": sorted(set(status_ids) - expected_ids)})
    else:
        warnings.append({"code": "expected_session_ids_not_supplied"})
    for rows, key in [(entity_rows, "entity_record_count"), (pair_rows, "exclusive_pair_record_count"),
                      (hy2_rows, "hysteria2_window_record_count"), (web_rows, "web_record_count")]:
        for status in statuses:
            actual = sum(r['session_id'] == status['session_id'] for r in rows)
            if actual != status.get(key):
                errors.append({"code": "checkpoint_record_count_mismatch", "table": key,
                               "session_id": status['session_id'], "expected": status.get(key), "actual": actual})
        if any(r['session_id'] not in set(status_ids) for r in rows):
            errors.append({"code": "orphan_feature_session", "table": key})
    if len(web_rows) != session_count or len({r['session_id'] for r in web_rows}) != session_count:
        errors.append({"code": "web_session_cardinality"})

    return {
        "state": "passed" if not errors else "failed",
        "session_count": session_count,
        "record_counts": {
            "entity": len(entity_rows),
            "exclusive_pair": len(pair_rows),
            "hysteria2_window": len(hy2_rows),
            "web_session": len(web_rows),
        },
        "feature_config_hashes": sorted(config_hashes),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }
