"""Build the two frozen research tracks from validated ML-wide feature tables."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq


IDENTITY_COLUMNS = {
    "session_id",
    "protocol_dataset",
    "record_id",
    "record_level",
    "capture_side",
    "transport_protocol",
    "group_site",
    "group_session_id",
    "group_carrier_id",
    "feature_schema_version",
    "feature_config_sha256",
    "split_by_site",
    "split_by_session",
    "split_by_carrier",
}

TRANSFORMATION_METRICS = (
    "scalar__packet_count__log_ratio",
    "scalar__packet_count__normalized_difference",
    "scalar__transport_payload_bytes__log_ratio",
    "scalar__transport_payload_bytes__normalized_difference",
    "scalar__duration_ns__log_ratio",
    "scalar__duration_ns__normalized_difference",
    "scalar__direction_run_burst_count__log_ratio",
    "scalar__direction_run_burst_count__normalized_difference",
    "length_distribution_distance__js_divergence_fixed_bins",
    "length_distribution_distance__wasserstein",
    "length_distribution_distance__ks_statistic",
    "iat_distribution_distance__wasserstein",
    "iat_distribution_distance__ks_statistic",
    "cumulative_distance__normalized_absolute_bytes__l1_mean",
    "cumulative_distance__normalized_absolute_bytes__l2_rms",
    "cumulative_distance__normalized_absolute_bytes__max_abs",
)

A_CORE_PREFIXES = (
    "volume__",
    "histograms__transport_payload_len__",
    "histograms__ip_total_len__",
    "histograms__iat_us__",
    "transition_nonempty__",
    "direction_run_burst__",
)

B_PREFIXES = ("tcp_state__", "tcp_transport__", "active_idle__")


def _atomic_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    columns = sorted(set().union(*(row.keys() for row in rows))) if rows else []
    table = pa.table({name: [row.get(name) for row in rows] for name in columns})
    pq.write_table(table, temporary, compression="zstd")
    os.replace(temporary, path)


def _finite(value: Any) -> float | None:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def _transform_row(
    row: dict[str, Any], *, prefix: str, scope: str, fr_comparable: bool
) -> dict[str, Any]:
    result = {
        "unit_id": row["record_id"],
        "session_id": row["session_id"],
        "protocol_dataset": row["protocol_dataset"],
        "comparison_scope": scope,
        "group_site": row["group_site"],
        "group_session_id": row["group_session_id"],
        "group_carrier_id": row.get("group_carrier_id"),
        "split_by_site": row["split_by_site"],
        "split_by_session": row["split_by_session"],
        "split_by_carrier": row["split_by_carrier"],
        "flow_reversal_comparable": fr_comparable,
    }
    for metric in TRANSFORMATION_METRICS:
        result[metric] = row.get(prefix + metric)
    if fr_comparable:
        result["flow_reversal__log_ratio"] = row.get(
            prefix + "flow_reversal_preservation__log_ratio"
        )
        result["flow_reversal__normalized_difference"] = row.get(
            prefix + "flow_reversal_preservation__normalized_difference"
        )
    else:
        result["flow_reversal__log_ratio"] = None
        result["flow_reversal__normalized_difference"] = None
    return result


def build_transformation_track(ml_root: Path | str, output: Path | str) -> dict[str, Any]:
    root = Path(ml_root)
    rows = []
    for row in pq.read_table(root / "exclusive_pair-wide.parquet").to_pylist():
        rows.append(
            _transform_row(row, prefix="", scope="exclusive_connection_pair", fr_comparable=True)
        )
    for row in pq.read_table(root / "hysteria2_window-wide.parquet").to_pylist():
        rows.append(
            _transform_row(
                row,
                prefix="inner_union_envelope__comparison__",
                scope="carrier_inner_union_envelope",
                fr_comparable=False,
            )
        )
    destination = Path(output)
    _atomic_parquet(destination, rows)
    return {
        "row_count": len(rows),
        "by_protocol": {
            protocol: sum(row["protocol_dataset"] == protocol for row in rows)
            for protocol in sorted({row["protocol_dataset"] for row in rows})
        },
        "fr_comparable_rows": sum(bool(row["flow_reversal_comparable"]) for row in rows),
    }


def summarize_transformation_track(path: Path | str) -> dict[str, Any]:
    rows = pq.read_table(path).to_pylist()
    metric_names = [*TRANSFORMATION_METRICS, "flow_reversal__log_ratio", "flow_reversal__normalized_difference"]
    summaries: dict[str, Any] = {}
    for protocol in sorted({row["protocol_dataset"] for row in rows}):
        protocol_rows = [row for row in rows if row["protocol_dataset"] == protocol]
        metrics: dict[str, Any] = {}
        for metric in metric_names:
            by_session: dict[str, list[float]] = {}
            for row in protocol_rows:
                value = _finite(row.get(metric))
                if value is not None:
                    by_session.setdefault(row["session_id"], []).append(value)
            session_values = np.asarray(
                [np.mean(values) for values in by_session.values()], dtype=np.float64
            )
            if session_values.size:
                metrics[metric] = {
                    "unit_nonnull_count": sum(len(values) for values in by_session.values()),
                    "session_count": int(session_values.size),
                    "session_mean_mean": float(session_values.mean()),
                    "session_mean_median": float(np.median(session_values)),
                    "session_mean_q25": float(np.quantile(session_values, 0.25)),
                    "session_mean_q75": float(np.quantile(session_values, 0.75)),
                }
            else:
                metrics[metric] = {"unit_nonnull_count": 0, "session_count": 0}
        summaries[protocol] = {
            "unit_count": len(protocol_rows),
            "session_count": len({row["session_id"] for row in protocol_rows}),
            "site_count": len({row["group_site"] for row in protocol_rows}),
            "metrics": metrics,
        }
    return {
        "aggregation_policy": "mean_within_session_then_summarize_sessions",
        "protocols": summaries,
    }


def _canonical_reversal(row: dict[str, Any]) -> dict[str, float | None]:
    prefix = (
        "carrier_datagram_reversal__observed__"
        if row.get("transport_protocol") == "udp"
        else "flow_reversal__observed__"
    )
    return {
        name: _finite(row.get(prefix + name))
        for name in (
            "duration_ns",
            "fr_norm_packets",
            "fr_per_kib",
            "fr_per_second",
            "fr_reversals",
            "fr_runs",
            "nonempty_packet_count",
            "payload_bytes",
        )
    }


def _selected_entity_columns(columns: Iterable[str], include_b: bool) -> list[str]:
    prefixes = A_CORE_PREFIXES + (B_PREFIXES if include_b else ())
    selected = []
    for name in columns:
        if name in IDENTITY_COLUMNS or not name.startswith(prefixes):
            continue
        # Grid values and validity/applicability flags are constants or metadata.
        if "__grid__" in name or name.endswith("__applicable"):
            continue
        selected.append(name)
    return selected


def _aggregate_session(
    rows: list[dict[str, Any]], selected: list[str], *, include_b: bool
) -> dict[str, Any]:
    first = rows[0]
    result: dict[str, Any] = {
        "session_id": first["session_id"],
        "protocol_dataset": first["protocol_dataset"],
        "group_site": first["group_site"],
        "split_by_site": first["split_by_site"],
        "split_by_session": first["split_by_session"],
        "post_entity_count": len(rows),
        "post_outer_connection_count": sum(row["record_level"] == "outer_connection" for row in rows),
        "post_carrier_count": sum(row["record_level"] == "carrier" for row in rows),
        "feature_set": "a_plus_b" if include_b else "a_core",
    }
    additive_markers = (
        "histograms__",
        "volume__up_",
        "volume__down_",
        "volume__total_",
        "transition_nonempty__n_",
        "transition_nonempty__packet_count",
        "direction_run_burst__count",
    )
    for name in selected:
        values = [_finite(row.get(name)) for row in rows]
        finite = np.asarray([value for value in values if value is not None], dtype=np.float64)
        if not finite.size:
            result[f"aggregate__{name}"] = None
        elif name.startswith(additive_markers):
            result[f"aggregate__{name}"] = float(finite.sum())
        else:
            result[f"mean__{name}"] = float(finite.mean())
            result[f"std__{name}"] = float(finite.std())

    reversal_fields: dict[str, list[float]] = {}
    for row in rows:
        for name, value in _canonical_reversal(row).items():
            if value is not None:
                reversal_fields.setdefault(name, []).append(value)
    for name, values in reversal_fields.items():
        array = np.asarray(values, dtype=np.float64)
        if name in {"duration_ns", "fr_reversals", "fr_runs", "nonempty_packet_count", "payload_bytes"}:
            result[f"aggregate__proxy_reversal__{name}"] = float(array.sum())
        else:
            result[f"mean__proxy_reversal__{name}"] = float(array.mean())
            result[f"std__proxy_reversal__{name}"] = float(array.std())

    # Use eleven normalized cumulative-shape landmarks without treating the frozen
    # grid itself as a sample feature.
    curve_prefix = "cumulative_shape__normalized_time__absolute_transport_bytes__"
    for index in range(0, 101, 10):
        name = curve_prefix + f"{index:03d}"
        normalized = []
        for row in rows:
            endpoint = _finite(row.get(curve_prefix + "100"))
            value = _finite(row.get(name))
            if endpoint and value is not None:
                normalized.append(value / endpoint)
        result[f"mean__normalized_cumulative_shape__{index:03d}"] = (
            float(np.mean(normalized)) if normalized else None
        )
    return result


def build_protocol_classification_track(
    ml_root: Path | str, output_root: Path | str
) -> dict[str, Any]:
    table = pq.read_table(Path(ml_root) / "entity-wide.parquet")
    post_rows = [
        row
        for row in table.to_pylist()
        if row["capture_side"] == "post" and row["record_level"] in {"outer_connection", "carrier"}
    ]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in post_rows:
        grouped.setdefault(row["session_id"], []).append(row)
    carrier_splits: dict[str, set[str]] = {}
    for row in post_rows:
        carrier = row.get("group_carrier_id")
        if carrier:
            carrier_splits.setdefault(str(carrier), set()).add(str(row["split_by_site"]))
    crossing_carriers = sum(len(splits) > 1 for splits in carrier_splits.values())
    if crossing_carriers:
        raise ValueError(f"{crossing_carriers} Hysteria2 carrier groups cross site splits")
    destination = Path(output_root)
    counts: dict[str, Any] = {}
    for include_b, name in ((False, "a_core"), (True, "a_plus_b")):
        selected = _selected_entity_columns(table.column_names, include_b)
        rows = [_aggregate_session(values, selected, include_b=include_b) for values in grouped.values()]
        _atomic_parquet(destination / f"protocol-classification-{name}.parquet", rows)
        counts[name] = {
            "row_count": len(rows),
            "feature_column_count": len(set().union(*(row.keys() for row in rows))) - 6,
            "by_protocol": {
                protocol: sum(row["protocol_dataset"] == protocol for row in rows)
                for protocol in sorted({row["protocol_dataset"] for row in rows})
            },
            "split_counts": {
                split: sum(row["split_by_site"] == split for row in rows)
                for split in ("train", "validation", "test")
            },
            "carrier_isolation": {
                "carrier_group_count": len(carrier_splits),
                "cross_split_carrier_count": crossing_carriers,
            },
        }
    return counts


def build_dual_track_datasets(ml_root: Path | str, output_root: Path | str) -> dict[str, Any]:
    destination = Path(output_root)
    transformation_path = destination / "transformation-common.parquet"
    track_a = build_transformation_track(ml_root, transformation_path)
    summary = summarize_transformation_track(transformation_path)
    summary_path = destination / "transformation-summary.json"
    temporary = summary_path.with_name(summary_path.name + ".tmp")
    temporary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, summary_path)
    track_b = build_protocol_classification_track(ml_root, destination)
    manifest = {"track_a": track_a, "track_b": track_b}
    manifest_path = destination / "dual-track-manifest.json"
    temporary = manifest_path.with_name(manifest_path.name + ".tmp")
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, manifest_path)
    return manifest
