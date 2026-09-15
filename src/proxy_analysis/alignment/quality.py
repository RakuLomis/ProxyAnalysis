"""Cross-table quality gates and lineage for URL-aligned datasets."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable, Mapping

import pyarrow.parquet as pq

from .build import ALIGNMENT_IMPLEMENTATION_VERSION
from .urls import URL_ALIGNMENT_SCHEMA_VERSION


TABLES = {
    "url_connection_index": "url-connection-index.parquet",
    "url_aligned_pair_features": "url-aligned-pair-features.parquet",
    "page_aligned_protocol_features": "page-aligned-protocol-features.parquet",
}

EXPECTED_PROTOCOLS = {"HYSTERIA2", "SHADOWSOCKS", "VLESS"}

# These columns are available for stratification, grouping, auditing, or lineage only.
# They are deliberately not an ML feature allowlist.
METADATA_ONLY_COLUMNS = {
    "protocol_dataset",
    "session_id",
    "target_url_hash",
    "target_normalized_url_hash",
    "target_domain",
    "page_label",
    "resource_url_hash",
    "normalized_url_hash",
    "representative_resource_url_hash",
    "host",
    "scheme",
    "connection_id",
    "comparison_entity_id",
    "pre_record_id",
    "post_record_id",
    "carrier_id",
    "outer_connection_id",
    "pre_src_ip",
    "pre_dst_ip",
    "post_src_ip",
    "post_dst_ip",
    "pre_src_port",
    "pre_dst_port",
    "post_src_port",
    "post_dst_port",
    "pre_tls_sni",
    "post_outer_tls_sni",
    "tls_sni_role",
    "group_site",
    "repetition", "activity_id", "target_key", "target_index", "page_protocol_id",
    "split_by_site",
    "split_by_session",
    "pre_entity_set_hash",
    "post_entity_set_hash",
}


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sum_to_one_error_count(
    rows: Iterable[Mapping[str, Any]], key_names: tuple[str, ...], weight_name: str
) -> int:
    sums: dict[tuple[str, ...], float] = {}
    for row in rows:
        key = tuple(str(row.get(name)) for name in key_names)
        value = row.get(weight_name)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return 1
        sums[key] = sums.get(key, 0.0) + float(value)
    return sum(not math.isclose(value, 1.0, rel_tol=1e-9, abs_tol=1e-9) for value in sums.values())


def _target_protocol_errors(
    rows: Iterable[Mapping[str, Any]], *, require_exactly_one_row_per_protocol: bool
) -> int:
    grouped: dict[str, list[str]] = {}
    for row in rows:
        grouped.setdefault((str(row.get("target_url_hash")), row.get('repetition')), []).append(
            str(row.get("protocol_dataset"))
        )
    return sum(
        set(protocols) != EXPECTED_PROTOCOLS
        or (require_exactly_one_row_per_protocol and len(protocols) != 3)
        for protocols in grouped.values()
    )


def _table_manifest(path: Path) -> dict[str, Any]:
    schema = pq.read_schema(path)
    metadata = pq.read_metadata(path)
    return {
        "path": str(path),
        "sha256": _sha256(path),
        "byte_size": path.stat().st_size,
        "row_count": metadata.num_rows,
        "column_count": len(schema.names),
        "schema_sha256": hashlib.sha256(str(schema).encode("utf-8")).hexdigest(),
    }


def validate_aligned_datasets(root: Path | str, *, registry: Path | str | None = None) -> dict[str, Any]:
    """Validate the three frozen aligned tables and write report plus manifest."""
    output_root = Path(root)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    paths = {name: output_root / filename for name, filename in TABLES.items()}
    for name, path in paths.items():
        if not path.is_file():
            errors.append({"code": "missing_table", "table": name, "path": str(path)})
    if errors:
        report = {
            "state": "failed",
            "error_count": len(errors),
            "warning_count": 0,
            "errors": errors,
            "warnings": warnings,
            "tables": {},
        }
        _atomic_json(output_root / "aligned-quality-report.json", report)
        return report

    index_rows = pq.read_table(paths["url_connection_index"]).to_pylist()
    pair_rows = pq.read_table(paths["url_aligned_pair_features"]).to_pylist()
    page_rows = pq.read_table(paths["page_aligned_protocol_features"]).to_pylist()

    def require(condition: bool, code: str, **details: Any) -> None:
        if not condition:
            errors.append({"code": code, **details})

    require(bool(index_rows), "empty_url_index")
    page_ids = {r['session_id'] for r in page_rows}
    require({r['session_id'] for r in index_rows} == page_ids, 'index_page_session_coverage')
    if registry is not None:
        selected = {r['session_id']:r for r in pq.read_table(registry).to_pylist() if r['is_final']}
        require(page_ids == set(selected), 'selected_page_session_coverage')
        for rows in [index_rows, pair_rows, page_rows]:
            require(all(r['session_id'] in selected and all(
                r.get(k) == selected[r['session_id']].get(k) for k in ['repetition','activity_id','target_key','target_index'])
                and r['protocol_dataset'] == selected[r['session_id']]['protocol'] for r in rows),
                'aligned_registry_identity')
    request_ids = [row.get("request_occurrence_id") for row in index_rows]
    require(len(set(request_ids)) == len(request_ids), "duplicate_request_occurrence_id")
    require(
        _target_protocol_errors(
            index_rows, require_exactly_one_row_per_protocol=False
        )
        == 0,
        "url_index_target_protocol_matrix",
    )
    require(
        {row.get("target_url_hash") for row in index_rows} == {row.get("target_url_hash") for row in page_rows},
        "url_index_target_url_count",
    )
    require(
        sum(row.get("url_parse_status") != "parsed" for row in index_rows) == 0,
        "url_parse_failure",
    )
    require(
        sum(bool(row.get("cdn_endpoint_observed")) for row in index_rows) == 0,
        "unsupported_cdn_endpoint_claim",
    )
    require(
        all(
            row.get("pre_destination_role") in {"fake_ip", "direct_origin_candidate", "unknown"}
            and row.get("post_destination_role")
            in {"proxy_endpoint", "direct_origin_candidate", "unknown"}
            for row in index_rows
        ),
        "invalid_endpoint_role",
    )
    missing_connections = sum(row.get("connection_id") is None for row in index_rows)
    if missing_connections:
        warnings.append(
            {
                "code": "request_connection_unavailable",
                "count": missing_connections,
                "explanation": "Rows are retained with explicit unavailable attribution; no feature values are imputed.",
            }
        )

    pair_ids = [row.get("url_connection_incidence_id") for row in pair_rows]
    require(len(set(pair_ids)) == len(pair_ids), "duplicate_url_connection_incidence_id")
    require(all(bool(row.get("feature_join_complete")) for row in pair_rows), "pair_feature_join_incomplete")
    for keys, weight, code in (
        (("session_id", "connection_id"), "connection_incidence_weight", "connection_weight_sum"),
        (("session_id", "post_record_id"), "post_entity_incidence_weight", "post_entity_weight_sum"),
        (("session_id", "comparison_entity_id"), "comparison_entity_incidence_weight", "comparison_entity_weight_sum"),
    ):
        count = _sum_to_one_error_count(pair_rows, keys, weight)
        require(count == 0, code, group_error_count=count)
    require(
        all(
            (row.get("protocol_dataset") == "HYSTERIA2")
            == (row.get("pairing_semantics") == "shared_carrier")
            for row in pair_rows
        ),
        "pair_protocol_semantics_mismatch",
    )
    require(
        all(
            not bool(row.get("flow_reversal_preservation_applicable"))
            for row in pair_rows
            if row.get("protocol_dataset") == "HYSTERIA2"
        ),
        "pair_hysteria2_flow_reversal_preservation_enabled",
    )
    require(
        {(r['session_id'],r['comparison_entity_id']) for r in pair_rows if r['protocol_dataset']=='HYSTERIA2'}
        <= {(r['session_id'],r['carrier_id']) for r in index_rows if r['protocol_dataset']=='HYSTERIA2'},
        "hysteria2_carrier_reference",
    )
    index_incidence_keys = {
        (row.get("session_id"), row.get("normalized_url_hash"), row.get("connection_id"))
        for row in index_rows
        if row.get("pairing_semantics") in {"exclusive_pair", "shared_carrier"}
        and row.get("connection_id")
        and row.get("normalized_url_hash")
    }
    require(
        all(
            (row.get("session_id"), row.get("normalized_url_hash"), row.get("connection_id"))
            in index_incidence_keys
            for row in pair_rows
        ),
        "pair_to_url_index_foreign_key",
    )

    require(bool(page_rows), "empty_page_table")
    require(len(page_ids) == len(page_rows), "page_session_uniqueness")
    require(len({r['page_protocol_id'] for r in page_rows}) == len(page_rows), "page_record_identity")
    require(
        _target_protocol_errors(
            page_rows, require_exactly_one_row_per_protocol=True
        )
        == 0,
        "page_target_protocol_matrix",
    )
    require(
        all(
            bool(row.get("proxy_coverage"))
            == (int(row.get("pre_entity_count") or 0) > 0 and int(row.get("post_entity_count") or 0) > 0)
            for row in page_rows
        ),
        "page_proxy_coverage_flag_mismatch",
    )
    require(
        all(
            not bool(row.get("flow_reversal_preservation_applicable"))
            for row in page_rows
            if row.get("protocol_dataset") == "HYSTERIA2"
        ),
        "hysteria2_flow_reversal_preservation_enabled",
    )
    require(
        sum(bool(row.get("cdn_endpoint_observed")) for row in page_rows) == 0,
        "page_unsupported_cdn_endpoint_claim",
    )
    coverage_by_protocol = {
        protocol: sum(
            row.get("protocol_dataset") == protocol and bool(row.get("proxy_coverage"))
            for row in page_rows
        )
        for protocol in sorted(EXPECTED_PROTOCOLS)
    }
    uncovered = sum(not bool(row.get("proxy_coverage")) for row in page_rows)
    full_coverage_targets = len(
        {
            row.get("target_url_hash")
            for row in page_rows
            if bool(row.get("all_three_proxy_coverage"))
        }
    )
    if uncovered:
        warnings.append(
            {
                "code": "page_proxy_coverage_incomplete",
                "row_count": uncovered,
                "coverage_by_protocol": coverage_by_protocol,
                "target_urls_with_all_three_proxy_coverage": full_coverage_targets,
                "explanation": "Raw request attribution contains no eligible proxy pre/post entity pair for these sessions; rows remain null and must be excluded from transformation tests.",
            }
        )

    source_config_hashes = sorted(
        {
            str(row["source_feature_config_sha256"])
            for rows in (pair_rows, page_rows)
            for row in rows
            if row.get("source_feature_config_sha256")
        }
    )
    require(len(source_config_hashes) == 1, "mixed_or_missing_source_feature_config", hashes=source_config_hashes)

    table_reports = {
        "url_connection_index": {
            "row_count": len(index_rows),
            "column_count": len(pq.read_schema(paths["url_connection_index"]).names),
            "missing_connection_count": missing_connections,
        },
        "url_aligned_pair_features": {
            "row_count": len(pair_rows),
            "column_count": len(pq.read_schema(paths["url_aligned_pair_features"]).names),
            "unique_normalized_url_count": len({row.get("normalized_url_hash") for row in pair_rows}),
        },
        "page_aligned_protocol_features": {
            "row_count": len(page_rows),
            "column_count": len(pq.read_schema(paths["page_aligned_protocol_features"]).names),
            "proxy_coverage_by_protocol": coverage_by_protocol,
            "target_urls_with_all_three_proxy_coverage": full_coverage_targets,
        },
    }
    report = {
        "state": "passed" if not errors else "failed",
        "url_alignment_schema_version": URL_ALIGNMENT_SCHEMA_VERSION,
        "alignment_implementation_version": ALIGNMENT_IMPLEMENTATION_VERSION,
        "source_feature_config_sha256": source_config_hashes[0] if len(source_config_hashes) == 1 else None,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "tables": table_reports,
    }
    _atomic_json(output_root / "aligned-quality-report.json", report)

    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "url_alignment_schema_version": URL_ALIGNMENT_SCHEMA_VERSION,
        "alignment_implementation_version": ALIGNMENT_IMPLEMENTATION_VERSION,
        "source_feature_config_sha256": report["source_feature_config_sha256"],
        "tables": {name: _table_manifest(path) for name, path in paths.items()},
        "quality_report": {
            "state": report["state"],
            "error_count": report["error_count"],
            "warning_count": report["warning_count"],
            "path": str(output_root / "aligned-quality-report.json"),
        },
        "lineage": {
            "url_connection_index": ["raw manifest", "request-index-v2", "connection-index-v2"],
            "url_aligned_pair_features": [
                "url-connection-index.parquet",
                "entity-wide.parquet",
                "exclusive_pair-wide.parquet",
                "hysteria2_window-wide.parquet",
                "transformation-common.parquet",
            ],
            "page_aligned_protocol_features": [
                "url-connection-index.parquet",
                "entity-wide.parquet",
            ],
        },
        "metadata_only_columns": sorted(METADATA_ONLY_COLUMNS),
        "cdn_inference_policy": "SNI and captured proxy endpoints are metadata only; no CDN IP/provider is inferred.",
    }
    _atomic_json(output_root / "aligned-manifest.json", manifest)
    return report
