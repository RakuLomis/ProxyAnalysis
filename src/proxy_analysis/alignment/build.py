"""Build request-level URL/connection/entity alignment records."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from ..indexing.identities import build_entity_descriptors
from ..indexing.pairs import build_exclusive_pairs
from ..inventory import InventoryScanner, SessionInventory
from ..features.pairwise import js_divergence, log_ratio, normalized_difference
from ..pipeline.export_ml import deterministic_split
from .urls import (
    URL_ALIGNMENT_SCHEMA_VERSION,
    endpoint_role,
    host_matches_domain,
    stable_hash,
    url_identity,
)


ALIGNMENT_IMPLEMENTATION_VERSION = 2


def _load_items(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    items = value.get("items")
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError(f"invalid items list: {path}")
    return items


def _nested(value: Mapping[str, Any] | None, *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _seconds_to_ns(value: Any) -> int | None:
    return round(float(value) * 1_000_000_000) if isinstance(value, (int, float)) else None


def _connection_interval(connection: Mapping[str, Any] | None) -> tuple[int | None, int | None]:
    timing = connection.get("timing") if isinstance(connection, Mapping) else None
    if not isinstance(timing, Mapping):
        return None, None
    start = _seconds_to_ns(timing.get("first_observed"))
    end = _seconds_to_ns(timing.get("last_observed"))
    terminal_ms = _nested(connection, "terminal", "duration_ms")
    if start is not None and isinstance(terminal_ms, (int, float)):
        terminal_end = start + round(float(terminal_ms) * 1_000_000)
        end = max(end or terminal_end, terminal_end)
    return start, end


def _request_interval(
    request: Mapping[str, Any], connection_end_ns: int | None
) -> tuple[int | None, int | None, str | None]:
    timing = request.get("timing")
    if not isinstance(timing, Mapping):
        return None, None, None
    start = _seconds_to_ns(timing.get("request"))
    candidates = [
        (value, name)
        for name in ("completion", "response")
        if (value := _seconds_to_ns(timing.get(name))) is not None
        and start is not None
        and value >= start
    ]
    if candidates:
        end, source = max(candidates, key=lambda item: item[0])
    elif start is not None and connection_end_ns is not None and connection_end_ns >= start:
        end, source = connection_end_ns, "connection_end_fallback"
    else:
        end, source = start, "start_only" if start is not None else None
    return start, end, source


def _atomic_wide_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    columns = sorted(set().union(*(row.keys() for row in rows))) if rows else []
    table = pa.table({name: [row.get(name) for row in rows] for name in columns})
    pq.write_table(table, temporary, compression="zstd")
    os.replace(temporary, path)


def _origin_observability(
    pre_role: str, post_role: str, outcome: str | None
) -> tuple[bool, str]:
    if outcome == "direct" and (
        pre_role == "direct_origin_candidate" or post_role == "direct_origin_candidate"
    ):
        return True, "direct_endpoint_candidate"
    if pre_role == "fake_ip" and post_role == "proxy_endpoint":
        return False, "fake_ip_and_proxy_endpoint_only"
    if post_role == "proxy_endpoint":
        return False, "proxy_endpoint_only"
    return False, "no_authoritative_origin_endpoint"


def build_session_url_index(
    session: SessionInventory,
) -> list[dict[str, Any]]:
    session_path = Path(session.session_path)
    requests = _load_items(session_path / "analysis/request-index-v2.json")
    connections = _load_items(session_path / "analysis/connection-index-v2.json")
    connection_by_id = {str(item.get("connection_id", "")): item for item in connections}
    descriptors = build_entity_descriptors(session_path, session.protocol_dataset)
    pre_by_connection = {
        item.entity_id: item.entity_id
        for item in descriptors
        if item.capture_side == "pre" and item.entity_level == "logical_connection"
    }
    post_by_connection: dict[str, tuple[str, str]] = {}
    for descriptor in descriptors:
        if descriptor.capture_side != "post":
            continue
        for connection_id in descriptor.logical_connection_ids:
            post_by_connection[connection_id] = (
                descriptor.entity_id,
                descriptor.entity_level,
            )
    eligible_pairs = {
        pair.connection_id
        for pair in build_exclusive_pairs(session_path, session.protocol_dataset)
    }
    target = url_identity(session.target_url)
    page_label = session_path.name.split("__", 1)[0]
    rows = []
    for request in requests:
        connection_id = (
            str(request["connection_id"]) if request.get("connection_id") else None
        )
        connection = connection_by_id.get(connection_id or "")
        outcome = _nested(connection, "egress", "outcome")
        pre_flow = connection.get("pre_flow") if isinstance(connection, Mapping) else None
        post_flow = connection.get("post_flow") if isinstance(connection, Mapping) else None
        pre_dst_ip = _nested(pre_flow, "dst_ip")
        post_dst_ip = _nested(post_flow, "dst_ip")
        pre_role = endpoint_role(pre_dst_ip, side="pre", outcome=outcome)
        post_role = endpoint_role(post_dst_ip, side="post", outcome=outcome)
        origin_observed, origin_reason = _origin_observability(
            pre_role, post_role, outcome
        )
        carrier_id = _nested(connection, "carrier_binding", "carrier_id")
        shared = bool(_nested(connection, "post_flow", "shared")) or (
            _nested(connection, "carrier_binding", "mode") == "shared"
        )
        if outcome == "proxy" and connection_id in eligible_pairs:
            pairing = "exclusive_pair"
        elif outcome == "proxy" and shared and carrier_id:
            pairing = "shared_carrier"
        elif outcome == "direct":
            pairing = "direct"
        elif outcome == "rejected":
            pairing = "rejected"
        else:
            pairing = "unavailable"
        post_entity = post_by_connection.get(connection_id or "")
        identity = url_identity(str(request.get("url", "")))
        connection_start, connection_end = _connection_interval(connection)
        request_start, request_end, request_end_source = _request_interval(
            request, connection_end
        )
        attribution = request.get("attribution")
        candidate_ids = request.get("candidate_connection_ids")
        row = {
            "url_alignment_schema_version": URL_ALIGNMENT_SCHEMA_VERSION,
            "alignment_implementation_version": ALIGNMENT_IMPLEMENTATION_VERSION,
            "protocol_dataset": session.protocol_dataset,
            "session_id": session.session_id,
            "page_label": page_label,
            "target_domain": session.target_domain,
            "target_url_hash": target.resource_url_hash,
            "target_normalized_url_hash": target.normalized_url_hash,
            "request_occurrence_id": str(request.get("request_occurrence_id", "")),
            "request_id": str(request["request_id"]) if request.get("request_id") else None,
            "resource_type": request.get("resource_type"),
            **identity.to_dict(),
            "host_matches_target_domain": host_matches_domain(
                identity.host, session.target_domain
            ),
            "connection_id": connection_id,
            "candidate_connection_count": (
                len(candidate_ids) if isinstance(candidate_ids, list) else 0
            ),
            "attribution_status": _nested(attribution, "status"),
            "attribution_method": _nested(attribution, "method"),
            "attribution_confidence": _nested(attribution, "confidence"),
            "egress_outcome": outcome,
            "application_protocol": (
                connection.get("application_protocol")
                if isinstance(connection, Mapping)
                else None
            ),
            "request_multiplexed": bool(_nested(connection, "sharing", "request_multiplexed")),
            "outer_connection_reused": bool(_nested(connection, "sharing", "outer_connection_reused")),
            "post_flow_shared": shared,
            "outer_connection_id": (
                connection.get("outer_connection_id")
                if isinstance(connection, Mapping)
                else None
            ),
            "carrier_id": carrier_id,
            "pre_entity_id": pre_by_connection.get(connection_id or ""),
            "post_entity_id": post_entity[0] if post_entity else None,
            "post_entity_level": post_entity[1] if post_entity else None,
            "pairing_semantics": pairing,
            "request_start_ns": request_start,
            "request_end_ns": request_end,
            "request_duration_ns": (
                request_end - request_start
                if request_start is not None and request_end is not None
                else None
            ),
            "request_end_source": request_end_source,
            "connection_start_ns": connection_start,
            "connection_end_ns": connection_end,
            "pre_src_ip": _nested(pre_flow, "src_ip"),
            "pre_src_port": _nested(pre_flow, "src_port"),
            "pre_dst_ip": pre_dst_ip,
            "pre_dst_port": _nested(pre_flow, "dst_port"),
            "post_src_ip": _nested(post_flow, "src_ip"),
            "post_src_port": _nested(post_flow, "src_port"),
            "post_dst_ip": post_dst_ip,
            "post_dst_port": _nested(post_flow, "dst_port"),
            "pre_destination_role": pre_role,
            "post_destination_role": post_role,
            "origin_endpoint_observed": origin_observed,
            "origin_endpoint_reason": origin_reason,
            "cdn_endpoint_observed": False,
            "pre_tls_sni": None,
            "post_outer_tls_sni": None,
            "tls_sni_role": "not_parsed",
            "sni_url_host_consistent": None,
            "sni_parse_reason": "optional_stage_not_run",
        }
        rows.append(row)
    return rows


def build_url_connection_index(
    dataset_root: Path | str, output: Path | str, *, registry: Path | str | None = None
) -> dict[str, Any]:
    sessions = InventoryScanner(dataset_root).scan()
    if registry is not None:
        registered = pq.read_table(registry).to_pylist()
        ids = [r['session_id'] for r in registered if r.get('is_selected', r.get('is_final', False))]
        if len(ids) != len(set(ids)):
            raise ValueError('duplicate selected registry session')
        if set(ids) - {s.session_id for s in sessions}:
            raise ValueError('selected registry session missing from inventory')
        sessions = [s for s in sessions if s.session_id in set(ids)]
    rows = [row for session in sessions for row in build_session_url_index(session)]
    if registry is not None:
        by_id = {r['session_id']: r for r in registered}
        for row in rows:
            identity = by_id[row['session_id']]
            row.update({k: identity[k] for k in ['repetition','activity_id','target_key','target_index']})
    destination = Path(output)
    _atomic_wide_parquet(destination, rows)
    return summarize_url_index(rows)


def summarize_url_index(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    values = list(rows)
    target_protocols: dict[str, set[str]] = {}
    for row in values:
        target_protocols.setdefault(str(row["target_url_hash"]), set()).add(
            str(row["protocol_dataset"])
        )
    return {
        "row_count": len(values),
        "unique_request_occurrence_count": len(
            {row["request_occurrence_id"] for row in values}
        ),
        "session_count": len({row["session_id"] for row in values}),
        "target_url_count": len(target_protocols),
        "target_urls_with_all_protocols": sum(
            protocols == {"HYSTERIA2", "SHADOWSOCKS", "VLESS"}
            for protocols in target_protocols.values()
        ),
        "url_parse_failure_count": sum(
            row["url_parse_status"] != "parsed" for row in values
        ),
        "missing_connection_count": sum(row["connection_id"] is None for row in values),
        "pairing_semantics": {
            name: sum(row["pairing_semantics"] == name for row in values)
            for name in sorted({str(row["pairing_semantics"]) for row in values})
        },
        "cdn_endpoint_observed_count": sum(
            bool(row["cdn_endpoint_observed"]) for row in values
        ),
    }


def read_url_index(path: Path | str) -> list[dict[str, Any]]:
    return pq.read_table(path).to_pylist()


def _entity_feature_columns(schema: pa.Schema) -> list[str]:
    identity = {
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
    selected = []
    for name in schema.names:
        if name in identity:
            continue
        if name in {"packet_count", "duration_ns"}:
            selected.append(name)
        elif name.startswith(
            (
                "volume__",
                "histograms__",
                "transition_nonempty__",
                "direction_run_burst__",
                "flow_reversal__",
                "carrier_datagram_reversal__",
                "tcp_state__",
                "tcp_transport__flag_counts__",
                "tcp_transport__handshake__",
            )
        ):
            selected.append(name)
        elif name in {
            "tcp_transport__effective_window__down__mean",
            "tcp_transport__effective_window__up__mean",
            "tcp_transport__raw_window__all__mean",
            "tcp_transport__raw_window__zero_window_count",
        }:
            selected.append(name)
        elif (
            name.startswith("cumulative_shape__normalized_time__")
            and "__grid__" not in name
            and any(
                token in name
                for token in (
                    "__absolute_transport_bytes__",
                    "__up_transport_bytes__",
                    "__down_transport_bytes__",
                )
            )
            and name.rsplit("__", 1)[-1]
            in {f"{index:03d}" for index in range(0, 101, 10)}
        ):
            selected.append(name)
    return selected


def _numeric_feature_columns(schema: pa.Schema) -> list[str]:
    metadata = {
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
        "unit_id",
        "comparison_scope",
    }
    return [
        field.name
        for field in schema
        if field.name not in metadata
        and (
            pa.types.is_boolean(field.type)
            or pa.types.is_integer(field.type)
            or pa.types.is_floating(field.type)
            or pa.types.is_null(field.type)
        )
    ]


def _read_selected(path: Path, columns: list[str]) -> list[dict[str, Any]]:
    available = set(pq.read_schema(path).names)
    return pq.read_table(path, columns=[name for name in columns if name in available]).to_pylist()


def build_url_aligned_pair_features(
    url_index_path: Path | str,
    ml_root: Path | str,
    experiment_root: Path | str,
    output: Path | str,
) -> dict[str, Any]:
    index_rows = read_url_index(url_index_path)
    eligible = [
        row
        for row in index_rows
        if row.get("pairing_semantics") in {"exclusive_pair", "shared_carrier"}
        and row.get("connection_id")
        and row.get("normalized_url_hash")
    ]
    incidences: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in eligible:
        key = (
            str(row["session_id"]),
            str(row["normalized_url_hash"]),
            str(row["connection_id"]),
        )
        incidences.setdefault(key, []).append(row)

    ml = Path(ml_root)
    entity_path = ml / "entity-wide.parquet"
    entity_schema = pq.read_schema(entity_path)
    entity_features = _entity_feature_columns(entity_schema)
    entity_identity = [
        "session_id",
        "record_id",
        "capture_side",
        "record_level",
        "transport_protocol",
        "feature_schema_version",
        "feature_config_sha256",
    ]
    entity_rows = _read_selected(entity_path, [*entity_identity, *entity_features])
    entity_by_key = {
        (row["session_id"], row["record_id"], row["capture_side"]): row
        for row in entity_rows
    }

    pair_path = ml / "exclusive_pair-wide.parquet"
    pair_schema = pq.read_schema(pair_path)
    pair_features = _numeric_feature_columns(pair_schema)
    pair_rows = _read_selected(
        pair_path, ["session_id", "record_id", *pair_features]
    )
    pair_by_key = {(row["session_id"], row["record_id"]): row for row in pair_rows}

    hy2_path = ml / "hysteria2_window-wide.parquet"
    hy2_schema = pq.read_schema(hy2_path)
    hy2_features = _numeric_feature_columns(hy2_schema)
    hy2_rows = _read_selected(
        hy2_path, ["session_id", "record_id", *hy2_features]
    )
    hy2_by_key = {(row["session_id"], row["record_id"]): row for row in hy2_rows}

    transform_path = Path(experiment_root) / "transformation-common.parquet"
    transform_schema = pq.read_schema(transform_path)
    transform_features = _numeric_feature_columns(transform_schema)
    transform_rows = _read_selected(
        transform_path,
        ["session_id", "unit_id", "comparison_scope", *transform_features],
    )
    transform_by_key = {
        (row["session_id"], row["unit_id"]): row for row in transform_rows
    }

    urls_by_connection: dict[tuple[str, str], set[str]] = {}
    for session_id, normalized_hash, connection_id in incidences:
        urls_by_connection.setdefault((session_id, connection_id), set()).add(
            normalized_hash
        )

    output_rows: list[dict[str, Any]] = []
    missing_features = 0
    for (session_id, normalized_hash, connection_id), requests in sorted(incidences.items()):
        first = requests[0]
        semantics = str(first["pairing_semantics"])
        comparison_id = (
            str(first["carrier_id"])
            if semantics == "shared_carrier"
            else connection_id
        )
        pre_id = first.get("pre_entity_id")
        post_id = first.get("post_entity_id")
        pre = entity_by_key.get((session_id, pre_id, "pre"))
        post = entity_by_key.get((session_id, post_id, "post"))
        comparison = (
            hy2_by_key.get((session_id, comparison_id))
            if semantics == "shared_carrier"
            else pair_by_key.get((session_id, comparison_id))
        )
        transform = transform_by_key.get((session_id, comparison_id))
        if pre is None or post is None or comparison is None or transform is None:
            missing_features += 1
        exact_hashes = sorted({str(row["resource_url_hash"]) for row in requests})
        hosts = sorted({str(row["host"]) for row in requests if row.get("host")})
        url_count = len(urls_by_connection[(session_id, connection_id)])
        row: dict[str, Any] = {
            "url_alignment_schema_version": URL_ALIGNMENT_SCHEMA_VERSION,
            "alignment_implementation_version": ALIGNMENT_IMPLEMENTATION_VERSION,
            "source_feature_schema_version": pre.get("feature_schema_version") if pre else None,
            "source_feature_config_sha256": pre.get("feature_config_sha256") if pre else None,
            "url_connection_incidence_id": stable_hash(
                "\0".join((session_id, normalized_hash, connection_id))
            ),
            **{k: first.get(k) for k in ['repetition','activity_id','target_key','target_index']},
            "protocol_dataset": first["protocol_dataset"],
            "session_id": session_id,
            "target_url_hash": first["target_url_hash"],
            "target_normalized_url_hash": first["target_normalized_url_hash"],
            "target_domain": first["target_domain"],
            "page_label": first["page_label"],
            "normalized_url_hash": normalized_hash,
            "representative_resource_url_hash": exact_hashes[0],
            "exact_url_count": len(exact_hashes),
            "host": hosts[0] if len(hosts) == 1 else None,
            "host_count": len(hosts),
            "connection_id": connection_id,
            "comparison_entity_id": comparison_id,
            "comparison_scope": (
                "carrier_inner_union_envelope"
                if semantics == "shared_carrier"
                else "exclusive_connection_pair"
            ),
            "pairing_semantics": semantics,
            "pre_record_id": pre_id,
            "post_record_id": post_id,
            "post_record_level": first["post_entity_level"],
            "request_occurrence_count": len(requests),
            "unique_url_count_on_connection": url_count,
            "connection_incidence_weight": 1.0 / url_count,
            "shared_connection": bool(first["request_multiplexed"]),
            "shared_carrier": semantics == "shared_carrier",
            "independence_unit": session_id,
            "feature_join_complete": all(
                item is not None for item in (pre, post, comparison, transform)
            ),
            "flow_reversal_preservation_applicable": (
                semantics != "shared_carrier"
                and pre is not None
                and post is not None
                and pre.get("transport_protocol") == "tcp"
                and post.get("transport_protocol") == "tcp"
            ),
        }
        for side, source in (("pre", pre), ("post", post)):
            if source:
                for name in entity_features:
                    row[f"{side}__{name}"] = source.get(name)
        if comparison:
            for name in (hy2_features if semantics == "shared_carrier" else pair_features):
                row[f"comparison__{name}"] = comparison.get(name)
        if transform:
            for name in transform_features:
                row[f"transform__{name}"] = transform.get(name)
        output_rows.append(row)

    post_counts: dict[tuple[str, str], int] = {}
    comparison_counts: dict[tuple[str, str], int] = {}
    for row in output_rows:
        post_counts[(row["session_id"], row["post_record_id"])] = (
            post_counts.get((row["session_id"], row["post_record_id"]), 0) + 1
        )
        comparison_counts[(row["session_id"], row["comparison_entity_id"])] = (
            comparison_counts.get(
                (row["session_id"], row["comparison_entity_id"]), 0
            )
            + 1
        )
    for row in output_rows:
        post_count = post_counts[(row["session_id"], row["post_record_id"])]
        comparison_count = comparison_counts[
            (row["session_id"], row["comparison_entity_id"])
        ]
        row["post_entity_incidence_weight"] = 1.0 / post_count
        row["comparison_entity_incidence_weight"] = 1.0 / comparison_count
        row["comparison_entity_reused"] = comparison_count > 1

    _atomic_wide_parquet(Path(output), output_rows)
    connection_weight_sums: dict[tuple[str, str], float] = {}
    post_weight_sums: dict[tuple[str, str], float] = {}
    for row in output_rows:
        connection_key = (row["session_id"], row["connection_id"])
        connection_weight_sums[connection_key] = (
            connection_weight_sums.get(connection_key, 0.0)
            + row["connection_incidence_weight"]
        )
        post_key = (row["session_id"], row["post_record_id"])
        post_weight_sums[post_key] = (
            post_weight_sums.get(post_key, 0.0) + row["post_entity_incidence_weight"]
        )
    return {
        "row_count": len(output_rows),
        "by_protocol": {
            protocol: sum(row["protocol_dataset"] == protocol for row in output_rows)
            for protocol in sorted({row["protocol_dataset"] for row in output_rows})
        },
        "unique_normalized_url_count": len(
            {row["normalized_url_hash"] for row in output_rows}
        ),
        "feature_join_incomplete_count": missing_features,
        "connection_weight_error_count": sum(
            abs(value - 1.0) > 1e-9 for value in connection_weight_sums.values()
        ),
        "post_entity_weight_error_count": sum(
            abs(value - 1.0) > 1e-9 for value in post_weight_sums.values()
        ),
        "unique_hysteria2_carrier_count": len(
            {
                (row["session_id"], row["comparison_entity_id"])
                for row in output_rows
                if row["protocol_dataset"] == "HYSTERIA2"
            }
        ),
    }


def _is_finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _is_additive_entity_feature(name: str) -> bool:
    if name == "packet_count":
        return True
    if name.startswith("histograms__"):
        return True
    if name.startswith("volume__") and not name.endswith(
        ("_log_ratio", "_normalized_difference")
    ):
        return True
    if name.startswith("transition_nonempty__n_") or name == "transition_nonempty__packet_count":
        return True
    if name == "direction_run_burst__count":
        return True
    if name.startswith(("flow_reversal__observed__", "carrier_datagram_reversal__observed__")):
        return name.rsplit("__", 1)[-1] in {
            "duration_ns",
            "fr_reversals",
            "fr_runs",
            "nonempty_packet_count",
            "payload_bytes",
        }
    if name.startswith("tcp_state__"):
        return name.endswith("_count") or name.endswith("_bytes")
    if name.startswith("tcp_transport__flag_counts__") or name in {
        "tcp_transport__raw_window__zero_window_count",
    }:
        return True
    return False


def _canonical_reversal_values(row: Mapping[str, Any]) -> dict[str, float]:
    prefix = (
        "carrier_datagram_reversal__observed__"
        if row.get("transport_protocol") == "udp"
        else "flow_reversal__observed__"
    )
    values = {}
    for name in (
        "duration_ns",
        "fr_reversals",
        "fr_runs",
        "nonempty_packet_count",
        "payload_bytes",
    ):
        value = row.get(prefix + name)
        if _is_finite_number(value):
            values[name] = float(value)
    return values


def _aggregate_page_entities(
    rows: list[dict[str, Any]], feature_names: list[str]
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "entity_count": len(rows),
        "tcp_entity_count": sum(row.get("transport_protocol") == "tcp" for row in rows),
        "udp_entity_count": sum(row.get("transport_protocol") == "udp" for row in rows),
    }
    packet_weights = np.asarray(
        [float(row.get("packet_count") or 0) for row in rows], dtype=np.float64
    )
    for name in feature_names:
        values = [
            (index, float(row[name]))
            for index, row in enumerate(rows)
            if _is_finite_number(row.get(name))
        ]
        if not values:
            continue
        array = np.asarray([value for _, value in values], dtype=np.float64)
        if _is_additive_entity_feature(name):
            result[f"aggregate__{name}"] = float(array.sum())
        else:
            result[f"mean__{name}"] = float(array.mean())
            selected_weights = np.asarray(
                [packet_weights[index] for index, _ in values], dtype=np.float64
            )
            result[f"packet_weighted_mean__{name}"] = (
                float(np.average(array, weights=selected_weights))
                if selected_weights.sum() > 0
                else float(array.mean())
            )

    for metric in ("packets", "transport_bytes", "ip_bytes", "captured_bytes"):
        up = result.get(f"aggregate__volume__up_{metric}")
        down = result.get(f"aggregate__volume__down_{metric}")
        if _is_finite_number(up) and _is_finite_number(down):
            result[f"derived__volume__{metric}_log_ratio"] = log_ratio(
                float(up), float(down), 1.0
            )
            result[f"derived__volume__{metric}_normalized_difference"] = (
                normalized_difference(float(up), float(down))
            )

    n_pp = result.get("aggregate__transition_nonempty__n_pp", 0.0)
    n_pm = result.get("aggregate__transition_nonempty__n_pm", 0.0)
    n_mp = result.get("aggregate__transition_nonempty__n_mp", 0.0)
    n_mm = result.get("aggregate__transition_nonempty__n_mm", 0.0)
    plus = n_pp + n_pm
    minus = n_mp + n_mm
    result["derived__transition_nonempty__p_pp"] = n_pp / plus if plus else None
    result["derived__transition_nonempty__p_pm"] = n_pm / plus if plus else None
    result["derived__transition_nonempty__p_mp"] = n_mp / minus if minus else None
    result["derived__transition_nonempty__p_mm"] = n_mm / minus if minus else None

    reversal_totals: dict[str, float] = {}
    for row in rows:
        for name, value in _canonical_reversal_values(row).items():
            reversal_totals[name] = reversal_totals.get(name, 0.0) + value
    for name, value in reversal_totals.items():
        result[f"aggregate__proxy_reversal__{name}"] = value
    reversals = reversal_totals.get("fr_reversals")
    packets = reversal_totals.get("nonempty_packet_count")
    payload = reversal_totals.get("payload_bytes")
    duration = reversal_totals.get("duration_ns")
    result["derived__proxy_reversal__fr_norm_packets"] = (
        reversals / packets if reversals is not None and packets else None
    )
    result["derived__proxy_reversal__fr_per_kib"] = (
        reversals / (payload / 1024)
        if reversals is not None and payload
        else None
    )
    result["derived__proxy_reversal__fr_per_second"] = (
        reversals / (duration / 1_000_000_000)
        if reversals is not None and duration
        else None
    )

    curve_bases = (
        "absolute_transport_bytes",
        "up_transport_bytes",
        "down_transport_bytes",
    )
    for base in curve_bases:
        prefix = f"cumulative_shape__normalized_time__{base}__"
        normalized_rows = []
        normalized_weights = []
        for row, weight in zip(rows, packet_weights):
            endpoint = row.get(prefix + "100")
            if not _is_finite_number(endpoint) or float(endpoint) <= 0:
                continue
            values = [row.get(prefix + f"{index:03d}") for index in range(0, 101, 10)]
            if not all(_is_finite_number(value) for value in values):
                continue
            normalized_rows.append([float(value) / float(endpoint) for value in values])
            normalized_weights.append(weight)
        if normalized_rows:
            matrix = np.asarray(normalized_rows, dtype=np.float64)
            weights = np.asarray(normalized_weights, dtype=np.float64)
            for position, index in enumerate(range(0, 101, 10)):
                result[f"mean__normalized_cumulative_shape__{base}__{index:03d}"] = float(
                    matrix[:, position].mean()
                )
                result[
                    f"packet_weighted_mean__normalized_cumulative_shape__{base}__{index:03d}"
                ] = (
                    float(np.average(matrix[:, position], weights=weights))
                    if weights.sum() > 0
                    else float(matrix[:, position].mean())
                )
    return result


def _histogram_js(
    pre: Mapping[str, Any], post: Mapping[str, Any], histogram: str
) -> float | None:
    prefix = f"aggregate__histograms__{histogram}__counts__"
    names = sorted(name for name in pre if name.startswith(prefix) and name in post)
    return js_divergence([int(pre[name]) for name in names], [int(post[name]) for name in names]) if names else None


def _workload_from_entities(rows: list[dict[str, Any]]) -> dict[str, float | int]:
    result: dict[str, float | int] = {"entity_count": len(rows)}
    for name in (
        "packet_count",
        "volume__total_packets",
        "volume__total_transport_bytes",
        "volume__total_ip_bytes",
        "volume__up_packets",
        "volume__down_packets",
        "volume__up_transport_bytes",
        "volume__down_transport_bytes",
    ):
        result[name] = sum(
            float(row[name]) for row in rows if _is_finite_number(row.get(name))
        )
    return result


def build_page_aligned_protocol_features(
    url_index_path: Path | str,
    ml_root: Path | str,
    output: Path | str,
) -> dict[str, Any]:
    index_rows = read_url_index(url_index_path)
    by_session: dict[str, list[dict[str, Any]]] = {}
    for row in index_rows:
        by_session.setdefault(str(row["session_id"]), []).append(row)

    entity_path = Path(ml_root) / "entity-wide.parquet"
    entity_schema = pq.read_schema(entity_path)
    feature_names = _entity_feature_columns(entity_schema)
    identity_columns = [
        "session_id",
        "record_id",
        "capture_side",
        "record_level",
        "transport_protocol",
        "feature_schema_version",
        "feature_config_sha256",
    ]
    entity_rows = _read_selected(entity_path, [*identity_columns, *feature_names])
    entity_by_key = {
        (row["session_id"], row["record_id"], row["capture_side"]): row
        for row in entity_rows
    }

    output_rows: list[dict[str, Any]] = []
    for session_id, requests in sorted(by_session.items()):
        first = requests[0]
        proxy_rows = [
            row
            for row in requests
            if row["pairing_semantics"] in {"exclusive_pair", "shared_carrier"}
        ]
        direct_rows = [row for row in requests if row["pairing_semantics"] == "direct"]
        rejected_rows = [row for row in requests if row["pairing_semantics"] == "rejected"]
        pre_ids = sorted(
            {str(row["pre_entity_id"]) for row in proxy_rows if row.get("pre_entity_id")}
        )
        post_ids = sorted(
            {str(row["post_entity_id"]) for row in proxy_rows if row.get("post_entity_id")}
        )
        pre_entities = [
            entity_by_key[(session_id, record_id, "pre")]
            for record_id in pre_ids
            if (session_id, record_id, "pre") in entity_by_key
        ]
        post_entities = [
            entity_by_key[(session_id, record_id, "post")]
            for record_id in post_ids
            if (session_id, record_id, "post") in entity_by_key
        ]
        direct_pre_ids = sorted(
            {str(row["pre_entity_id"]) for row in direct_rows if row.get("pre_entity_id")}
        )
        direct_post_ids = sorted(
            {str(row["post_entity_id"]) for row in direct_rows if row.get("post_entity_id")}
        )
        rejected_pre_ids = sorted(
            {str(row["pre_entity_id"]) for row in rejected_rows if row.get("pre_entity_id")}
        )
        direct_pre_entities = [
            entity_by_key[(session_id, record_id, "pre")]
            for record_id in direct_pre_ids
            if (session_id, record_id, "pre") in entity_by_key
        ]
        direct_post_entities = [
            entity_by_key[(session_id, record_id, "post")]
            for record_id in direct_post_ids
            if (session_id, record_id, "post") in entity_by_key
        ]
        rejected_pre_entities = [
            entity_by_key[(session_id, record_id, "pre")]
            for record_id in rejected_pre_ids
            if (session_id, record_id, "pre") in entity_by_key
        ]
        pre_features = _aggregate_page_entities(pre_entities, feature_names)
        post_features = _aggregate_page_entities(post_entities, feature_names)
        protocol = str(first["protocol_dataset"])
        row: dict[str, Any] = {
            "url_alignment_schema_version": URL_ALIGNMENT_SCHEMA_VERSION,
            "alignment_implementation_version": ALIGNMENT_IMPLEMENTATION_VERSION,
            "source_feature_schema_version": (
                pre_entities[0].get("feature_schema_version") if pre_entities else None
            ),
            "source_feature_config_sha256": (
                pre_entities[0].get("feature_config_sha256") if pre_entities else None
            ),
            "page_protocol_id": stable_hash(
                "\0".join((protocol, str(first["target_url_hash"]), session_id))
            ),
            **{k: first.get(k) for k in ['repetition','activity_id','target_key','target_index']},
            "protocol_dataset": protocol,
            "session_id": session_id,
            "target_url_hash": first["target_url_hash"],
            "target_normalized_url_hash": first["target_normalized_url_hash"],
            "target_domain": first["target_domain"],
            "page_label": first["page_label"],
            "group_site": first["target_domain"],
            "split_by_site": deterministic_split(
                str(first["target_domain"]), seed="proxy-analysis-v1:site"
            ),
            "split_by_session": deterministic_split(
                session_id, seed="proxy-analysis-v1:session"
            ),
            "proxy_coverage": bool(pre_entities and post_entities),
            "proxy_request_occurrence_count": len(proxy_rows),
            "proxy_unique_connection_count": len(
                {item["connection_id"] for item in proxy_rows if item.get("connection_id")}
            ),
            "direct_request_occurrence_count": sum(
                item["pairing_semantics"] == "direct" for item in requests
            ),
            "direct_unique_connection_count": len(
                {item["connection_id"] for item in direct_rows if item.get("connection_id")}
            ),
            "rejected_request_occurrence_count": sum(
                item["pairing_semantics"] == "rejected" for item in requests
            ),
            "rejected_unique_connection_count": len(
                {item["connection_id"] for item in rejected_rows if item.get("connection_id")}
            ),
            "unavailable_request_occurrence_count": sum(
                item["pairing_semantics"] == "unavailable" for item in requests
            ),
            "request_occurrence_count": len(requests),
            "unique_exact_resource_url_count": len(
                {item["resource_url_hash"] for item in requests}
            ),
            "unique_normalized_url_count": len(
                {item["normalized_url_hash"] for item in requests if item["normalized_url_hash"]}
            ),
            "unique_host_count": len({item["host"] for item in requests if item["host"]}),
            "pre_entity_count": len(pre_entities),
            "post_entity_count": len(post_entities),
            "pre_entity_set_hash": stable_hash("\0".join(pre_ids)),
            "post_entity_set_hash": stable_hash("\0".join(post_ids)),
            "post_carrier_count": len(
                {
                    item["carrier_id"]
                    for item in proxy_rows
                    if item.get("carrier_id")
                }
            ),
            "origin_endpoint_observed_for_proxy": False,
            "cdn_endpoint_observed": False,
            "aggregation_semantics": "unique_page_attributed_proxy_entities",
        }
        for name, value in pre_features.items():
            row[f"pre__{name}"] = value
        for name, value in post_features.items():
            row[f"post__{name}"] = value
        for workload_name, workload_entities in (
            ("direct_pre", direct_pre_entities),
            ("direct_post", direct_post_entities),
            ("rejected_pre", rejected_pre_entities),
        ):
            for name, value in _workload_from_entities(workload_entities).items():
                row[f"workload__{workload_name}__{name}"] = value

        comparison_scalars = (
            "entity_count",
            "aggregate__packet_count",
            "aggregate__volume__total_packets",
            "aggregate__volume__total_transport_bytes",
            "aggregate__volume__total_ip_bytes",
            "aggregate__direction_run_burst__count",
            "aggregate__proxy_reversal__fr_reversals",
        )
        for name in comparison_scalars:
            pre_value = pre_features.get(name)
            post_value = post_features.get(name)
            if _is_finite_number(pre_value) and _is_finite_number(post_value):
                row[f"delta__{name}__log_ratio"] = log_ratio(
                    float(post_value), float(pre_value), 1.0
                )
                row[f"delta__{name}__normalized_difference"] = normalized_difference(
                    float(post_value), float(pre_value)
                )
            else:
                row[f"delta__{name}__log_ratio"] = None
                row[f"delta__{name}__normalized_difference"] = None
        for histogram in ("transport_payload_len", "ip_total_len", "iat_us"):
            row[f"distance__{histogram}__js_divergence"] = _histogram_js(
                pre_features, post_features, histogram
            )
        pre_curve = [
            pre_features.get(
                f"mean__normalized_cumulative_shape__absolute_transport_bytes__{index:03d}"
            )
            for index in range(0, 101, 10)
        ]
        post_curve = [
            post_features.get(
                f"mean__normalized_cumulative_shape__absolute_transport_bytes__{index:03d}"
            )
            for index in range(0, 101, 10)
        ]
        if all(_is_finite_number(value) for value in [*pre_curve, *post_curve]):
            differences = np.abs(
                np.asarray(post_curve, dtype=np.float64)
                - np.asarray(pre_curve, dtype=np.float64)
            )
            row["distance__normalized_cumulative_shape__l1_mean"] = float(
                differences.mean()
            )
            row["distance__normalized_cumulative_shape__max_abs"] = float(
                differences.max()
            )
        else:
            row["distance__normalized_cumulative_shape__l1_mean"] = None
            row["distance__normalized_cumulative_shape__max_abs"] = None
        row["flow_reversal_preservation_applicable"] = (
            protocol != "HYSTERIA2"
            and bool(pre_entities)
            and bool(post_entities)
            and all(item.get("transport_protocol") == "tcp" for item in [*pre_entities, *post_entities])
        )
        output_rows.append(row)

    target_groups: dict[str, list[dict[str, Any]]] = {}
    for row in output_rows:
        target_groups.setdefault((str(row["target_url_hash"]), row.get('repetition')), []).append(row)
    for rows in target_groups.values():
        protocols = {row["protocol_dataset"] for row in rows}
        all_present = protocols == {"HYSTERIA2", "SHADOWSOCKS", "VLESS"}
        all_proxy = all_present and all(bool(row["proxy_coverage"]) for row in rows)
        for row in rows:
            row["all_three_protocol_rows_present"] = all_present
            row["all_three_proxy_coverage"] = all_proxy

    _atomic_wide_parquet(Path(output), output_rows)
    return {
        "row_count": len(output_rows),
        "session_count": len({row["session_id"] for row in output_rows}),
        "target_url_count": len(target_groups),
        "target_urls_with_all_protocol_rows": sum(
            len(rows) == 3
            and {row["protocol_dataset"] for row in rows}
            == {"HYSTERIA2", "SHADOWSOCKS", "VLESS"}
            for rows in target_groups.values()
        ),
        "target_urls_with_all_protocol_proxy_coverage": sum(
            all(bool(row["proxy_coverage"]) for row in rows)
            for rows in target_groups.values()
        ),
        "proxy_coverage_by_protocol": {
            protocol: sum(
                row["protocol_dataset"] == protocol and row["proxy_coverage"]
                for row in output_rows
            )
            for protocol in ("HYSTERIA2", "SHADOWSOCKS", "VLESS")
        },
        "missing_pre_feature_entity_count": sum(
            row["proxy_request_occurrence_count"] > 0 and row["pre_entity_count"] == 0
            for row in output_rows
        ),
        "missing_post_feature_entity_count": sum(
            row["proxy_request_occurrence_count"] > 0 and row["post_entity_count"] == 0
            for row in output_rows
        ),
        "cdn_endpoint_observed_count": sum(
            bool(row["cdn_endpoint_observed"]) for row in output_rows
        ),
    }
