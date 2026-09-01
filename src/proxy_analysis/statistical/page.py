"""Page-level within-protocol and matched cross-protocol inference."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from .config import MetricSpec, StatisticalConfig
from .inference import (
    benjamini_hochberg,
    descriptive,
    finite,
    friedman_result,
    one_sample_result,
)


PROTOCOL_ORDER = ("HYSTERIA2", "SHADOWSOCKS", "VLESS")


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def _atomic_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = sorted(set().union(*(row.keys() for row in rows))) if rows else []
    table = pa.table({name: [row.get(name) for row in rows] for name in columns})
    temporary = path.with_name(path.name + ".tmp")
    pq.write_table(table, temporary, compression="zstd")
    os.replace(temporary, path)


def _metric_seed(base: int, *parts: str) -> int:
    digest = hashlib.sha256("\0".join(parts).encode("utf-8")).digest()
    return (base + int.from_bytes(digest[:4], "big")) % (2**32)


def _value(row: Mapping[str, Any], metric: MetricSpec, stage: str) -> float | None:
    if metric.distance_column:
        candidate = row.get(metric.distance_column) if stage == "delta" else None
    elif stage == "pre":
        candidate = row.get(metric.pre_column) if metric.pre_column else None
    elif stage == "post":
        candidate = row.get(metric.post_column) if metric.post_column else None
    elif metric.delta_column:
        candidate = row.get(metric.delta_column)
    else:
        pre = row.get(metric.pre_column) if metric.pre_column else None
        post = row.get(metric.post_column) if metric.post_column else None
        candidate = float(post) - float(pre) if finite(pre) and finite(post) else None
    return float(candidate) if finite(candidate) else None


def _threshold(config: StatisticalConfig, metric: MetricSpec) -> float:
    value = float(config.practical_thresholds[metric.practical_threshold])
    return math.log1p(value) if metric.transform == "log_ratio" else value


def _flatten_ci(result: dict[str, Any]) -> dict[str, Any]:
    output = dict(result)
    ci = output.pop("cluster_bootstrap_median_ci95", [None, None])
    output["cluster_bootstrap_median_ci95_low"] = ci[0]
    output["cluster_bootstrap_median_ci95_high"] = ci[1]
    return output


def _apply_bh(rows: list[dict[str, Any]], group_names: tuple[str, ...]) -> None:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in rows:
        if finite(row.get("pvalue_raw")):
            key = tuple(str(row.get(name)) for name in group_names)
            groups.setdefault(key, []).append(row)
    for group in groups.values():
        adjusted = benjamini_hochberg(float(row["pvalue_raw"]) for row in group)
        for row, qvalue in zip(group, adjusted):
            row["qvalue_bh"] = qvalue


def _descriptive_rows(
    rows: list[dict[str, Any]], config: StatisticalConfig
) -> list[dict[str, Any]]:
    output = []
    for metric in config.metrics:
        stages = ("delta",) if metric.distance_column else ("pre", "post", "delta")
        for protocol in metric.protocols:
            protocol_rows = [row for row in rows if row["protocol_dataset"] == protocol]
            for stage in stages:
                values = [
                    value
                    for row in protocol_rows
                    if (value := _value(row, metric, stage)) is not None
                ]
                output.append(
                    {
                        "cohort": "page_available",
                        "metric_id": metric.metric_id,
                        "feature_family": metric.family,
                        "protocol_dataset": protocol,
                        "stage": stage,
                        "eligible_row_count": len(protocol_rows),
                        "missing_count": len(protocol_rows) - len(values),
                        **descriptive(values),
                    }
                )
    return output


def _q1_results(
    rows: list[dict[str, Any]], config: StatisticalConfig
) -> list[dict[str, Any]]:
    output = []
    for metric in config.metrics:
        for protocol in metric.protocols:
            values = []
            clusters = []
            sessions = set()
            for row in rows:
                if row["protocol_dataset"] != protocol:
                    continue
                value = _value(row, metric, "delta")
                if value is None:
                    continue
                values.append(value)
                clusters.append(str(row["group_site"]))
                sessions.add(str(row["session_id"]))
            result = one_sample_result(
                values,
                clusters,
                seed=_metric_seed(config.seed, "q1", protocol, metric.metric_id),
                bootstrap_repetitions=config.bootstrap_repetitions,
                permutation_repetitions=config.permutation_repetitions,
                confidence_level=config.confidence_level,
            )
            threshold = _threshold(config, metric)
            output.append(
                {
                    "question": "Q1_within_protocol_pre_post",
                    "inference_scope": "confirmatory_page_level",
                    "protocol_dataset": protocol,
                    "metric_id": metric.metric_id,
                    "feature_family": metric.family,
                    "delta_source": metric.delta_column or metric.distance_column or "post_minus_pre",
                    "session_count": len(sessions),
                    "site_cluster_count": len(set(clusters)),
                    "minimum_cluster_gate_passed": len(set(clusters))
                    >= config.minimum_paired_clusters,
                    "practical_threshold": threshold,
                    **_flatten_ci(result),
                    "practical_threshold_exceeded_by_median": (
                        abs(float(result["median"])) >= threshold
                        if finite(result.get("median"))
                        else None
                    ),
                    "interpretation_flag": (
                        config.interpretation_policy["transition_p_pm"]["within_vless"]
                        if metric.metric_id == "transition_p_pm" and protocol == "VLESS"
                        else None
                    ),
                }
            )
    _apply_bh(output, ("question",))
    return output


def _matched_values(
    rows: list[dict[str, Any]], metric: MetricSpec, stage: str
) -> tuple[list[str], dict[str, np.ndarray], list[str]]:
    protocols = tuple(item for item in PROTOCOL_ORDER if item in metric.protocols)
    grouped: dict[str, dict[str, tuple[float, str]]] = {}
    for row in rows:
        protocol = str(row["protocol_dataset"])
        if protocol not in protocols:
            continue
        value = _value(row, metric, stage)
        if value is not None:
            grouped.setdefault(str(row["target_url_hash"]), {})[protocol] = (
                value,
                str(row["group_site"]),
            )
    complete = [
        (target, values)
        for target, values in sorted(grouped.items())
        if all(protocol in values for protocol in protocols)
    ]
    arrays = {
        protocol: np.asarray([values[protocol][0] for _, values in complete], dtype=np.float64)
        for protocol in protocols
    }
    sites = [values[protocols[0]][1] for _, values in complete]
    return list(protocols), arrays, sites


def _q2_results(
    rows: list[dict[str, Any]], config: StatisticalConfig
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    omnibus_rows: list[dict[str, Any]] = []
    pairwise_rows: list[dict[str, Any]] = []
    for metric in config.metrics:
        stages = ("delta",) if metric.distance_column else ("pre", "post", "delta")
        for stage in stages:
            protocols, arrays, sites = _matched_values(rows, metric, stage)
            if len(protocols) == 3:
                result = friedman_result([arrays[protocol] for protocol in protocols])
                omnibus_rows.append(
                    {
                        "question": "Q2_cross_protocol",
                        "inference_scope": "confirmatory_page_complete_triplets",
                        "metric_id": metric.metric_id,
                        "feature_family": metric.family,
                        "stage": stage,
                        "protocols": ",".join(protocols),
                        "site_cluster_count": len(set(sites)),
                        "interpretation_flag": (
                            config.interpretation_policy["transition_p_pm"][
                                "cross_protocol"
                            ]
                            if metric.metric_id == "transition_p_pm"
                            else None
                        ),
                        **result,
                    }
                )
            for left_index, left in enumerate(protocols):
                for right in protocols[left_index + 1 :]:
                    differences = arrays[left] - arrays[right]
                    result = one_sample_result(
                        differences,
                        sites,
                        seed=_metric_seed(
                            config.seed, "q2", metric.metric_id, stage, left, right
                        ),
                        bootstrap_repetitions=config.bootstrap_repetitions,
                        permutation_repetitions=config.permutation_repetitions,
                        confidence_level=config.confidence_level,
                    )
                    pairwise_rows.append(
                        {
                            "question": "Q2_cross_protocol_pairwise",
                            "inference_scope": "confirmatory_page_complete_triplets",
                            "metric_id": metric.metric_id,
                            "feature_family": metric.family,
                            "stage": stage,
                            "left_protocol": left,
                            "right_protocol": right,
                            "difference_direction": "left_minus_right",
                            "site_cluster_count": len(set(sites)),
                            **_flatten_ci(result),
                        }
                    )
    _apply_bh(omnibus_rows, ("question", "stage"))
    _apply_bh(pairwise_rows, ("question", "stage", "feature_family"))
    omnibus_significant = {
        (row["metric_id"], row["stage"])
        for row in omnibus_rows
        if finite(row.get("qvalue_bh")) and float(row["qvalue_bh"]) < config.fdr_alpha
    }
    for row in pairwise_rows:
        # Two-protocol FR has no three-way omnibus and remains its own registered family.
        row["omnibus_gate_passed"] = (
            (row["metric_id"], row["stage"]) in omnibus_significant
            or row["feature_family"] == "flow_reversal"
        )
    return omnibus_rows, pairwise_rows


def run_page_statistics(
    marts_root: Path | str,
    output_root: Path | str,
    config_path: Path | str,
) -> dict[str, Any]:
    marts = Path(marts_root)
    output = Path(output_root)
    config = StatisticalConfig.load(config_path)
    available = pq.read_table(marts / "page-available-pairs.parquet").to_pylist()
    complete = pq.read_table(marts / "page-complete-triplets.parquet").to_pylist()
    descriptive_rows = _descriptive_rows(available, config)
    q1_rows = _q1_results(available, config)
    q2_omnibus, q2_pairwise = _q2_results(complete, config)

    _atomic_rows(output / "descriptive-statistics.parquet", descriptive_rows)
    _atomic_rows(output / "q1-within-protocol-results.parquet", q1_rows)
    _atomic_rows(output / "q2-cross-protocol-omnibus.parquet", q2_omnibus)
    _atomic_rows(output / "q2-cross-protocol-pairwise.parquet", q2_pairwise)
    report = {
        "statistical_config_sha256": config.sha256,
        "unit_of_inference": "page session; site-clustered uncertainty",
        "page_available_row_count": len(available),
        "page_complete_triplet_row_count": len(complete),
        "page_complete_target_count": len({row["target_url_hash"] for row in complete}),
        "descriptive_result_count": len(descriptive_rows),
        "q1_result_count": len(q1_rows),
        "q1_bh_significant_count": sum(
            finite(row.get("qvalue_bh")) and float(row["qvalue_bh"]) < config.fdr_alpha
            for row in q1_rows
        ),
        "q2_omnibus_result_count": len(q2_omnibus),
        "q2_omnibus_bh_significant_count": sum(
            finite(row.get("qvalue_bh")) and float(row["qvalue_bh"]) < config.fdr_alpha
            for row in q2_omnibus
        ),
        "q2_pairwise_result_count": len(q2_pairwise),
        "q2_pairwise_bh_significant_and_gated_count": sum(
            bool(row["omnibus_gate_passed"])
            and finite(row.get("qvalue_bh"))
            and float(row["qvalue_bh"]) < config.fdr_alpha
            for row in q2_pairwise
        ),
        "hysteria2_tcp_flow_reversal_excluded": True,
    }
    _atomic_json(output / "page-statistics-summary.json", report)
    _atomic_json(
        output / "q1-within-protocol-results.json",
        {"summary": report, "results": q1_rows},
    )
    _atomic_json(
        output / "q2-cross-protocol-results.json",
        {"summary": report, "omnibus": q2_omnibus, "pairwise": q2_pairwise},
    )
    return report
