"""URL- and host-level strict/weighted sensitivity analysis."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from .config import PROTOCOLS, StatisticalConfig
from .inference import benjamini_hochberg, descriptive, finite, friedman_result, one_sample_result


URL_METRICS = (
    ("packet_count", "workload", "transform__scalar__packet_count__log_ratio"),
    (
        "transport_payload_bytes",
        "workload",
        "transform__scalar__transport_payload_bytes__log_ratio",
    ),
    (
        "burst_count",
        "interaction",
        "transform__scalar__direction_run_burst_count__log_ratio",
    ),
    (
        "packet_length_js",
        "distribution",
        "transform__length_distribution_distance__js_divergence_fixed_bins",
    ),
    (
        "iat_wasserstein",
        "distribution",
        "transform__iat_distribution_distance__wasserstein",
    ),
    (
        "cumulative_l1",
        "cumulative_shape",
        "transform__cumulative_distance__normalized_absolute_bytes__l1_mean",
    ),
    ("flow_reversals", "flow_reversal", "transform__flow_reversal__log_ratio"),
)


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


def _seed(base: int, *parts: str) -> int:
    digest = hashlib.sha256("\0".join(parts).encode("utf-8")).digest()
    return (base + int.from_bytes(digest[:4], "big")) % (2**32)


def _aggregate_long(
    rows: list[dict[str, Any]], *, level: str, weighted: bool, cohort: str
) -> list[dict[str, Any]]:
    key_fields = (
        ("session_id", "target_url_hash", "normalized_url_hash", "protocol_dataset")
        if level == "url"
        else ("session_id", "target_url_hash", "host", "protocol_dataset")
    )
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in rows:
        if level == "host" and not row.get("host"):
            continue
        key = tuple(str(row.get(name)) for name in key_fields)
        groups.setdefault(key, []).append(row)

    output: list[dict[str, Any]] = []
    for key, group in sorted(groups.items()):
        first = group[0]
        for metric_id, family, column in URL_METRICS:
            if metric_id == "flow_reversals" and first["protocol_dataset"] == "HYSTERIA2":
                continue
            values = []
            weights = []
            for row in group:
                value = row.get(column)
                if not finite(value):
                    continue
                weight = (
                    row.get("comparison_entity_incidence_weight", 0.0)
                    if weighted
                    else 1.0
                )
                if not finite(weight) or float(weight) <= 0:
                    continue
                values.append(float(value))
                weights.append(float(weight))
            if not values:
                continue
            output.append(
                {
                    "cohort": cohort,
                    "aggregation_level": level,
                    **dict(zip(key_fields, key)),
                    "target_domain": first.get("target_domain"),
                    "metric_id": metric_id,
                    "feature_family": family,
                    "source_column": column,
                    "value": float(np.average(values, weights=weights)),
                    "incidence_count": len(group),
                    "effective_weight_sum": float(sum(weights)),
                    "shared_incidence_count": sum(
                        bool(row.get("shared_connection")) for row in group
                    ),
                }
            )
    return output


def _bh_on_primary(rows: list[dict[str, Any]], groups: tuple[str, ...]) -> None:
    nested: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in rows:
        if finite(row.get("primary_pvalue")):
            key = tuple(str(row.get(name)) for name in groups)
            nested.setdefault(key, []).append(row)
    for values in nested.values():
        adjusted = benjamini_hochberg(float(row["primary_pvalue"]) for row in values)
        for row, qvalue in zip(values, adjusted):
            row["qvalue_bh"] = qvalue


def _within_protocol(
    strict: list[dict[str, Any]],
    weighted: list[dict[str, Any]],
    config: StatisticalConfig,
) -> list[dict[str, Any]]:
    output = []
    for protocol in sorted(PROTOCOLS):
        policy = config.url_protocol_policy[protocol]
        primary_rows = strict if policy["cohort"] == "url_strict" else weighted
        for metric_id, family, _ in URL_METRICS:
            if protocol == "HYSTERIA2" and metric_id == "flow_reversals":
                continue
            selected = [
                row
                for row in primary_rows
                if row["protocol_dataset"] == protocol and row["metric_id"] == metric_id
            ]
            values = [float(row["value"]) for row in selected]
            clusters = [str(row["target_domain"]) for row in selected]
            result = one_sample_result(
                values,
                clusters,
                seed=_seed(config.seed, "q3-within", protocol, metric_id),
                bootstrap_repetitions=config.bootstrap_repetitions,
                permutation_repetitions=config.permutation_repetitions,
                confidence_level=config.confidence_level,
            )
            ci = result.pop("cluster_bootstrap_median_ci95")
            confirmatory = policy["inference"] == "confirmatory"
            output.append(
                {
                    "question": "Q3_url_within_protocol",
                    "cohort": policy["cohort"],
                    "inference_scope": policy["inference"],
                    "protocol_dataset": protocol,
                    "metric_id": metric_id,
                    "feature_family": family,
                    "target_cluster_count": len(
                        {row["target_url_hash"] for row in selected}
                    ),
                    "site_cluster_count": len(set(clusters)),
                    **result,
                    "cluster_bootstrap_median_ci95_low": ci[0],
                    "cluster_bootstrap_median_ci95_high": ci[1],
                    "primary_pvalue": (
                        result["blocked_permutation_pvalue"] if confirmatory else None
                    ),
                }
            )
    _bh_on_primary(output, ("question", "inference_scope"))
    return output


def _cross_protocol(
    rows: list[dict[str, Any]], *, level: str, config: StatisticalConfig
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    identity = "normalized_url_hash" if level == "url" else "host"
    omnibus = []
    pairwise = []
    for metric_id, family, _ in URL_METRICS:
        if metric_id == "flow_reversals":
            continue
        grouped: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
        for row in rows:
            if row["metric_id"] != metric_id:
                continue
            key = (str(row["target_url_hash"]), str(row[identity]))
            grouped.setdefault(key, {})[str(row["protocol_dataset"])] = row
        complete = [
            values for values in grouped.values() if set(values) == PROTOCOLS
        ]
        arrays = {
            protocol: np.asarray(
                [float(values[protocol]["value"]) for values in complete],
                dtype=np.float64,
            )
            for protocol in sorted(PROTOCOLS)
        }
        sites = [str(values["HYSTERIA2"]["target_domain"]) for values in complete]
        friedman = friedman_result([arrays[p] for p in sorted(PROTOCOLS)])
        omnibus.append(
            {
                "question": f"Q3_{level}_cross_protocol",
                "inference_scope": "exploratory_weighted_carrier_context",
                "metric_id": metric_id,
                "feature_family": family,
                "matched_key_count": len(complete),
                "site_cluster_count": len(set(sites)),
                **friedman,
            }
        )
        protocols = sorted(PROTOCOLS)
        for left_index, left in enumerate(protocols):
            for right in protocols[left_index + 1 :]:
                differences = arrays[left] - arrays[right]
                result = one_sample_result(
                    differences,
                    sites,
                    seed=_seed(config.seed, "q3-cross", level, metric_id, left, right),
                    bootstrap_repetitions=config.bootstrap_repetitions,
                    permutation_repetitions=config.permutation_repetitions,
                    confidence_level=config.confidence_level,
                )
                ci = result.pop("cluster_bootstrap_median_ci95")
                pairwise.append(
                    {
                        "question": f"Q3_{level}_cross_protocol_pairwise",
                        "inference_scope": "exploratory_weighted_carrier_context",
                        "metric_id": metric_id,
                        "feature_family": family,
                        "left_protocol": left,
                        "right_protocol": right,
                        "difference_direction": "left_minus_right",
                        "matched_key_count": len(complete),
                        "site_cluster_count": len(set(sites)),
                        **result,
                        "cluster_bootstrap_median_ci95_low": ci[0],
                        "cluster_bootstrap_median_ci95_high": ci[1],
                        "primary_pvalue": result["blocked_permutation_pvalue"],
                    }
                )
    _bh_on_primary(pairwise, ("question", "feature_family"))
    return omnibus, pairwise


def run_resource_statistics(
    marts_root: Path | str,
    output_root: Path | str,
    config_path: Path | str,
) -> dict[str, Any]:
    marts = Path(marts_root)
    output = Path(output_root)
    config = StatisticalConfig.load(config_path)
    strict_raw = pq.read_table(marts / "url-strict.parquet").to_pylist()
    weighted_raw = pq.read_table(marts / "url-weighted.parquet").to_pylist()
    strict_url = _aggregate_long(
        strict_raw, level="url", weighted=False, cohort="url_strict"
    )
    weighted_url = _aggregate_long(
        weighted_raw, level="url", weighted=True, cohort="url_weighted"
    )
    strict_host = _aggregate_long(
        strict_raw, level="host", weighted=False, cohort="host_strict"
    )
    weighted_host = _aggregate_long(
        weighted_raw, level="host", weighted=True, cohort="host_weighted"
    )
    _atomic_rows(marts / "url-metrics-strict.parquet", strict_url)
    _atomic_rows(marts / "url-metrics-weighted.parquet", weighted_url)
    _atomic_rows(marts / "host-metrics-strict.parquet", strict_host)
    _atomic_rows(marts / "host-metrics-weighted.parquet", weighted_host)

    within = _within_protocol(strict_url, weighted_url, config)
    url_omnibus, url_pairwise = _cross_protocol(
        weighted_url, level="url", config=config
    )
    host_omnibus, host_pairwise = _cross_protocol(
        weighted_host, level="host", config=config
    )
    _atomic_rows(output / "q3-within-protocol-results.parquet", within)
    _atomic_rows(output / "q3-url-cross-protocol-omnibus.parquet", url_omnibus)
    _atomic_rows(output / "q3-url-cross-protocol-pairwise.parquet", url_pairwise)
    _atomic_rows(output / "q3-host-cross-protocol-omnibus.parquet", host_omnibus)
    _atomic_rows(output / "q3-host-cross-protocol-pairwise.parquet", host_pairwise)
    report = {
        "statistical_config_sha256": config.sha256,
        "url_protocol_policy": config.url_protocol_policy,
        "strict_url_metric_row_count": len(strict_url),
        "weighted_url_metric_row_count": len(weighted_url),
        "strict_host_metric_row_count": len(strict_host),
        "weighted_host_metric_row_count": len(weighted_host),
        "within_protocol_result_count": len(within),
        "confirmatory_within_protocol_bh_significant_count": sum(
            finite(row.get("qvalue_bh")) and float(row["qvalue_bh"]) < config.fdr_alpha
            for row in within
        ),
        "weighted_url_cross_protocol_matched_key_count": (
            url_omnibus[0]["matched_key_count"] if url_omnibus else 0
        ),
        "weighted_host_cross_protocol_matched_key_count": (
            host_omnibus[0]["matched_key_count"] if host_omnibus else 0
        ),
        "cross_protocol_inference_scope": "exploratory_weighted_carrier_context",
        "hysteria2_url_scope": "descriptive_carrier_context",
        "cdn_endpoint_analysis_supported": False,
    }
    _atomic_json(
        output / "q3-resource-host-results.json",
        {
            "summary": report,
            "within_protocol": within,
            "url_omnibus": url_omnibus,
            "url_pairwise": url_pairwise,
            "host_omnibus": host_omnibus,
            "host_pairwise": host_pairwise,
        },
    )
    return report
