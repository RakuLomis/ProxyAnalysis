"""Build frozen statistical cohorts without treating URL incidences as independent."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from .config import PROTOCOLS, StatisticalConfig


STATISTICAL_MART_SCHEMA_VERSION = 1


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def _atomic_parquet(path: Path, table: pa.Table) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    pq.write_table(table, temporary, compression="zstd")
    os.replace(temporary, path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _protocol_counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    return {
        protocol: len({row[key] for row in rows if row["protocol_dataset"] == protocol})
        for protocol in sorted(PROTOCOLS)
    }


def _matched_key_count(
    rows: list[dict[str, Any]], key_names: tuple[str, ...]
) -> int:
    groups: dict[tuple[str, ...], set[str]] = {}
    for row in rows:
        key = tuple(str(row.get(name)) for name in key_names)
        groups.setdefault(key, set()).add(str(row["protocol_dataset"]))
    return sum(protocols == PROTOCOLS for protocols in groups.values())


def _host_coverage(index_rows: list[dict[str, Any]]) -> pa.Table:
    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in index_rows:
        host = row.get("host")
        if not host:
            continue
        key = (str(row["target_url_hash"]), str(host), str(row["protocol_dataset"]))
        result = groups.setdefault(
            key,
            {
                "statistical_mart_schema_version": STATISTICAL_MART_SCHEMA_VERSION,
                "target_url_hash": key[0],
                "host": key[1],
                "protocol_dataset": key[2],
                "target_domain": row.get("target_domain"),
                "request_occurrence_count": 0,
                "proxy_request_occurrence_count": 0,
                "direct_request_occurrence_count": 0,
                "rejected_request_occurrence_count": 0,
                "unavailable_request_occurrence_count": 0,
                "connection_ids": set(),
                "normalized_url_hashes": set(),
            },
        )
        result["request_occurrence_count"] += 1
        semantics = str(row.get("pairing_semantics"))
        if semantics in {"exclusive_pair", "shared_carrier"}:
            result["proxy_request_occurrence_count"] += 1
        elif semantics in {"direct", "rejected", "unavailable"}:
            result[f"{semantics}_request_occurrence_count"] += 1
        if row.get("connection_id"):
            result["connection_ids"].add(str(row["connection_id"]))
        if row.get("normalized_url_hash"):
            result["normalized_url_hashes"].add(str(row["normalized_url_hash"]))

    matched: dict[tuple[str, str], set[str]] = {}
    for target, host, protocol in groups:
        matched.setdefault((target, host), set()).add(protocol)
    rows = []
    for (target, host, protocol), value in sorted(groups.items()):
        rows.append(
            {
                key: item
                for key, item in value.items()
                if key not in {"connection_ids", "normalized_url_hashes"}
            }
            | {
                "unique_connection_count": len(value["connection_ids"]),
                "unique_normalized_url_count": len(value["normalized_url_hashes"]),
                "all_three_protocols_present": matched[(target, host)] == PROTOCOLS,
            }
        )
    columns = sorted(set().union(*(row.keys() for row in rows))) if rows else []
    return pa.table({name: [row.get(name) for row in rows] for name in columns})


def build_statistical_marts(
    aligned_root: Path | str,
    output_root: Path | str,
    config_path: Path | str,
) -> dict[str, Any]:
    aligned = Path(aligned_root)
    output = Path(output_root)
    config = StatisticalConfig.load(config_path)
    quality_path = aligned / "aligned-quality-report.json"
    manifest_path = aligned / "aligned-manifest.json"
    if not quality_path.is_file() or not manifest_path.is_file():
        raise ValueError("aligned quality report and manifest are required")
    quality = json.loads(quality_path.read_text(encoding="utf-8"))
    if quality.get("state") != "passed":
        raise ValueError("aligned quality report must be passed")

    page_path = aligned / "page-aligned-protocol-features.parquet"
    pair_path = aligned / "url-aligned-pair-features.parquet"
    index_path = aligned / "url-connection-index.parquet"
    page = pq.read_table(page_path)
    pair = pq.read_table(pair_path)
    index = pq.read_table(index_path)
    config.validate_page_columns(set(page.schema.names))

    page_complete = page.filter(pc.equal(page["all_three_proxy_coverage"], True))
    page_available = page.filter(pc.equal(page["proxy_coverage"], True))
    strict_mask = pc.and_kleene(
        pc.and_kleene(
            pc.equal(pair["feature_join_complete"], True),
            pc.equal(pair["unique_url_count_on_connection"], 1),
        ),
        pc.and_kleene(
            pc.equal(pair["shared_connection"], False),
            pc.equal(pair["comparison_entity_reused"], False),
        ),
    )
    url_strict = pair.filter(strict_mask)
    url_weighted = pair.filter(pc.equal(pair["feature_join_complete"], True))
    host_coverage = _host_coverage(index.to_pylist())

    marts_root = output / "marts"
    outputs = {
        "page_complete_triplets": marts_root / "page-complete-triplets.parquet",
        "page_available_pairs": marts_root / "page-available-pairs.parquet",
        "url_strict": marts_root / "url-strict.parquet",
        "url_weighted": marts_root / "url-weighted.parquet",
        "host_coverage": marts_root / "host-coverage.parquet",
    }
    for name, table in (
        ("page_complete_triplets", page_complete),
        ("page_available_pairs", page_available),
        ("url_strict", url_strict),
        ("url_weighted", url_weighted),
        ("host_coverage", host_coverage),
    ):
        _atomic_parquet(outputs[name], table)

    page_complete_rows = page_complete.to_pylist()
    page_available_rows = page_available.to_pylist()
    strict_rows = url_strict.to_pylist()
    weighted_rows = url_weighted.to_pylist()
    host_rows = host_coverage.to_pylist()
    strict_targets = _protocol_counts(strict_rows, "target_url_hash")
    critical_nodes = []
    below_minimum = {
        protocol: count
        for protocol, count in strict_targets.items()
        if count < config.minimum_paired_clusters
    }
    if below_minimum:
        critical_nodes.append(
            {
                "code": "url_strict_cluster_coverage_below_minimum",
                "minimum_paired_clusters": config.minimum_paired_clusters,
                "target_cluster_count_by_protocol": strict_targets,
                "below_minimum": below_minimum,
                "recommended_resolution": (
                    "Keep URL-strict confirmatory inference for VLESS/SHADOWSOCKS; "
                    "treat HYSTERIA2 URL results as weighted/descriptive because shared "
                    "carrier reuse is intrinsic to the protocol."
                ),
            }
        )

    audit = {
        "state": "needs_confirmation" if critical_nodes else "ready",
        "statistical_mart_schema_version": STATISTICAL_MART_SCHEMA_VERSION,
        "statistical_config_sha256": config.sha256,
        "minimum_paired_clusters": config.minimum_paired_clusters,
        "page": {
            "complete_triplet_row_count": len(page_complete_rows),
            "complete_triplet_target_count": len(
                {row["target_url_hash"] for row in page_complete_rows}
            ),
            "available_row_count": len(page_available_rows),
            "available_target_count_by_protocol": _protocol_counts(
                page_available_rows, "target_url_hash"
            ),
        },
        "url_strict": {
            "row_count": len(strict_rows),
            "row_count_by_protocol": {
                protocol: sum(row["protocol_dataset"] == protocol for row in strict_rows)
                for protocol in sorted(PROTOCOLS)
            },
            "target_cluster_count_by_protocol": strict_targets,
            "matched_target_normalized_url_triplet_count": _matched_key_count(
                strict_rows, ("target_url_hash", "normalized_url_hash")
            ),
        },
        "url_weighted": {
            "row_count": len(weighted_rows),
            "target_cluster_count_by_protocol": _protocol_counts(
                weighted_rows, "target_url_hash"
            ),
            "matched_target_normalized_url_triplet_count": _matched_key_count(
                weighted_rows, ("target_url_hash", "normalized_url_hash")
            ),
        },
        "host": {
            "row_count": len(host_rows),
            "matched_target_host_triplet_count": _matched_key_count(
                host_rows, ("target_url_hash", "host")
            ),
            "unique_host_count": len({row["host"] for row in host_rows}),
        },
        "critical_nodes": critical_nodes,
        "cdn_endpoint_analysis_supported": False,
        "cdn_reason": "No proxy-exit-to-origin endpoint is observed; SNI/host remain metadata only.",
    }
    _atomic_json(output / "coverage-audit.json", audit)

    frozen_spec = {
        "statistical_mart_schema_version": STATISTICAL_MART_SCHEMA_VERSION,
        "statistical_config_sha256": config.sha256,
        "config": {
            **{
                key: value
                for key, value in asdict(config).items()
                if key not in {"metrics", "sha256"}
            },
            "metrics": [asdict(metric) for metric in config.metrics],
        },
        "inputs": {
            path.name: {"sha256": _sha256(path), "row_count": pq.read_metadata(path).num_rows}
            for path in (index_path, pair_path, page_path)
        },
        "aligned_manifest_sha256": _sha256(manifest_path),
        "metadata_excluded_from_metric_allowlist": True,
        "hysteria2_tcp_flow_reversal_excluded": True,
        "cdn_endpoint_analysis_supported": False,
    }
    _atomic_json(output / "frozen-analysis-spec.json", frozen_spec)
    return audit
