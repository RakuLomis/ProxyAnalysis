"""Pre-registered robustness checks and direction-stability matrix."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from .config import StatisticalConfig
from .inference import finite
from .page import _value
from .resource import URL_METRICS, _aggregate_long


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def _atomic_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = sorted(set().union(*(row.keys() for row in rows))) if rows else []
    table = pa.table({name: [row.get(name) for row in rows] for name in columns})
    temporary = path.with_name(path.name + ".tmp")
    pq.write_table(table, temporary, compression="zstd")
    os.replace(temporary, path)


def _median(values: list[float]) -> float | None:
    return float(np.median(values)) if values else None


def _sign(value: float | None, tolerance: float = 1e-12) -> int | None:
    if value is None:
        return None
    if value > tolerance:
        return 1
    if value < -tolerance:
        return -1
    return 0


def _comparison_row(
    *,
    check: str,
    protocol: str,
    metric_id: str,
    primary_values: list[float],
    sensitivity_values: list[float],
) -> dict[str, Any]:
    primary = _median(primary_values)
    sensitivity = _median(sensitivity_values)
    return {
        "check": check,
        "protocol_dataset": protocol,
        "metric_id": metric_id,
        "primary_n": len(primary_values),
        "sensitivity_n": len(sensitivity_values),
        "primary_median": primary,
        "sensitivity_median": sensitivity,
        "primary_sign": _sign(primary),
        "sensitivity_sign": _sign(sensitivity),
        "direction_stable": (
            _sign(primary) == _sign(sensitivity)
            if _sign(primary) is not None and _sign(sensitivity) is not None
            else None
        ),
    }


def run_sensitivity_analysis(
    marts_root: Path | str,
    output_root: Path | str,
    config_path: Path | str,
) -> dict[str, Any]:
    marts = Path(marts_root)
    output = Path(output_root)
    config = StatisticalConfig.load(config_path)
    available = pq.read_table(marts / "page-available-pairs.parquet").to_pylist()
    complete = pq.read_table(marts / "page-complete-triplets.parquet").to_pylist()
    strict_long = pq.read_table(marts / "url-metrics-strict.parquet").to_pylist()
    weighted_long = pq.read_table(marts / "url-metrics-weighted.parquet").to_pylist()
    weighted_raw = pq.read_table(marts / "url-weighted.parquet").to_pylist()

    matrix: list[dict[str, Any]] = []
    complete_sessions = {row["session_id"] for row in complete}
    for metric in config.metrics:
        for protocol in metric.protocols:
            protocol_rows = [row for row in available if row["protocol_dataset"] == protocol]
            primary = [
                value
                for row in protocol_rows
                if (value := _value(row, metric, "delta")) is not None
            ]
            complete_values = [
                value
                for row in protocol_rows
                if row["session_id"] in complete_sessions
                and (value := _value(row, metric, "delta")) is not None
            ]
            matrix.append(
                _comparison_row(
                    check="page_available_vs_complete_triplets",
                    protocol=protocol,
                    metric_id=metric.metric_id,
                    primary_values=primary,
                    sensitivity_values=complete_values,
                )
            )

            fractions = [
                (
                    float(row.get("direct_request_occurrence_count", 0))
                    + float(row.get("rejected_request_occurrence_count", 0))
                )
                / max(float(row.get("request_occurrence_count", 0)), 1.0)
                for row in protocol_rows
            ]
            cutoff = float(np.quantile(fractions, 0.9)) if fractions else 0.0
            low_nonproxy = [
                value
                for row, fraction in zip(protocol_rows, fractions)
                if fraction <= cutoff
                and (value := _value(row, metric, "delta")) is not None
            ]
            matrix.append(
                _comparison_row(
                    check="exclude_top_10pct_direct_rejected_fraction",
                    protocol=protocol,
                    metric_id=metric.metric_id,
                    primary_values=primary,
                    sensitivity_values=low_nonproxy,
                )
                | {"exclusion_cutoff": cutoff}
            )

            sites = sorted({str(row["group_site"]) for row in protocol_rows})
            leave_one_out = []
            for site in sites:
                values = [
                    value
                    for row in protocol_rows
                    if str(row["group_site"]) != site
                    and (value := _value(row, metric, "delta")) is not None
                ]
                if values:
                    leave_one_out.append(float(np.median(values)))
            primary_sign = _sign(_median(primary))
            stable_fraction = (
                float(np.mean([_sign(value) == primary_sign for value in leave_one_out]))
                if leave_one_out
                else None
            )
            matrix.append(
                {
                    "check": "leave_one_site_out",
                    "protocol_dataset": protocol,
                    "metric_id": metric.metric_id,
                    "primary_n": len(primary),
                    "sensitivity_n": len(leave_one_out),
                    "primary_median": _median(primary),
                    "sensitivity_median": _median(leave_one_out),
                    "primary_sign": primary_sign,
                    "sensitivity_sign": _sign(_median(leave_one_out)),
                    "direction_stable": stable_fraction == 1.0,
                    "leave_one_site_out_direction_stable_fraction": stable_fraction,
                }
            )

    for protocol in ("SHADOWSOCKS", "VLESS"):
        for metric_id, _, _ in URL_METRICS:
            strict_values = [
                float(row["value"])
                for row in strict_long
                if row["protocol_dataset"] == protocol and row["metric_id"] == metric_id
            ]
            weighted_values = [
                float(row["value"])
                for row in weighted_long
                if row["protocol_dataset"] == protocol and row["metric_id"] == metric_id
            ]
            matrix.append(
                _comparison_row(
                    check="url_strict_vs_weighted",
                    protocol=protocol,
                    metric_id=metric_id,
                    primary_values=strict_values,
                    sensitivity_values=weighted_values,
                )
            )

    exact_raw = [row for row in weighted_raw if int(row.get("exact_url_count") or 0) == 1]
    exact_long = _aggregate_long(
        exact_raw, level="url", weighted=True, cohort="url_exact_single_weighted"
    )
    for protocol in sorted({str(row["protocol_dataset"]) for row in weighted_long}):
        for metric_id, _, _ in URL_METRICS:
            if protocol == "HYSTERIA2" and metric_id == "flow_reversals":
                continue
            normalized_values = [
                float(row["value"])
                for row in weighted_long
                if row["protocol_dataset"] == protocol and row["metric_id"] == metric_id
            ]
            exact_values = [
                float(row["value"])
                for row in exact_long
                if row["protocol_dataset"] == protocol and row["metric_id"] == metric_id
            ]
            matrix.append(
                _comparison_row(
                    check="query_stripped_vs_single_exact_url",
                    protocol=protocol,
                    metric_id=metric_id,
                    primary_values=normalized_values,
                    sensitivity_values=exact_values,
                )
            )

    hysteria_rows: dict[tuple[str, str], dict[str, Any]] = {}
    for row in weighted_raw:
        if row["protocol_dataset"] == "HYSTERIA2":
            hysteria_rows[(str(row["session_id"]), str(row["comparison_entity_id"]))] = row
    inner_column = (
        "comparison__inner_union_envelope__comparison__scalar__packet_count__log_ratio"
    )
    full_column = (
        "comparison__carrier_full_lifetime__comparison__scalar__packet_count__log_ratio"
    )
    inner = [float(row[inner_column]) for row in hysteria_rows.values() if finite(row.get(inner_column))]
    full = [float(row[full_column]) for row in hysteria_rows.values() if finite(row.get(full_column))]
    matrix.append(
        _comparison_row(
            check="hysteria2_inner_union_vs_carrier_full_lifetime",
            protocol="HYSTERIA2",
            metric_id="packet_count",
            primary_values=inner,
            sensitivity_values=full,
        )
    )

    _atomic_rows(output / "sensitivity-matrix.parquet", matrix)
    evaluated = [row for row in matrix if row.get("direction_stable") is not None]
    conflicts = [row for row in evaluated if not bool(row["direction_stable"])]
    summary = {
        "statistical_config_sha256": config.sha256,
        "check_row_count": len(matrix),
        "evaluated_direction_row_count": len(evaluated),
        "direction_conflict_count": len(conflicts),
        "direction_conflicts": [
            {
                "check": row["check"],
                "protocol_dataset": row["protocol_dataset"],
                "metric_id": row["metric_id"],
                "primary_median": row["primary_median"],
                "sensitivity_median": row["sensitivity_median"],
            }
            for row in conflicts
        ],
    }
    _atomic_json(output / "sensitivity-summary.json", summary)
    return summary
