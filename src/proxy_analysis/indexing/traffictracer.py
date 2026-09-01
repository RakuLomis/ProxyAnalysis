"""Normalize TrafficTracer indexes without deriving packet features."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Mapping


class IndexContractError(RuntimeError):
    """Raised when an index cannot satisfy its basic structural contract."""


@dataclass(frozen=True, slots=True)
class PairEligibility:
    session_id: str
    protocol_dataset: str
    connection_id: str
    eligible: bool
    pair_level: str | None
    reason: str | None
    outer_connection_id: str | None
    carrier_id: str | None
    post_transport: str | None


@dataclass(frozen=True, slots=True)
class IndexAudit:
    session_id: str
    protocol_dataset: str
    request_count: int
    connection_count: int
    logical_flow_count: int
    pcap_connection_count: int
    proxy_connection_count: int
    direct_connection_count: int
    rejected_connection_count: int
    shared_proxy_connection_count: int
    unique_carrier_count: int
    eligible_exclusive_pair_count: int
    request_connection_orphans: int
    pcap_connection_orphans: int
    connection_request_orphans: int
    duplicate_connection_ids: int
    duplicate_request_occurrence_ids: int
    eligibility: tuple[PairEligibility, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_items(path: Path, key: str = "items") -> list[dict[str, Any]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IndexContractError(f"cannot read {path}: {exc}") from exc
    items = raw.get(key)
    if not isinstance(items, list):
        raise IndexContractError(f"{path}: {key} must be a list")
    if any(not isinstance(item, dict) for item in items):
        raise IndexContractError(f"{path}: every {key} entry must be an object")
    return items


def _duplicates(values: list[str]) -> int:
    return len(values) - len(set(values))


def _string(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _nested(mapping: Mapping[str, Any], *keys: str) -> Any:
    current: Any = mapping
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _pcap_success(pcap_item: Mapping[str, Any] | None, side: str) -> bool:
    if not pcap_item:
        return False
    value = pcap_item.get(side)
    return isinstance(value, Mapping) and value.get("status") == "success"


def _pair_eligibility(
    protocol_dataset: str,
    session_id: str,
    connection: Mapping[str, Any],
    pcap_item: Mapping[str, Any] | None,
) -> PairEligibility:
    connection_id = str(connection.get("connection_id", ""))
    outcome = _nested(connection, "egress", "outcome")
    outer_id = _string(connection.get("outer_connection_id"))
    carrier_id = _string(_nested(connection, "carrier_binding", "carrier_id"))
    post_transport = _string(_nested(connection, "post_flow", "network"))
    shared = bool(_nested(connection, "post_flow", "shared")) or (
        _nested(connection, "carrier_binding", "mode") == "shared"
    )

    reason: str | None = None
    if outcome != "proxy":
        reason = "not_proxy_egress"
    elif not _pcap_success(pcap_item, "pre_proxy"):
        reason = "missing_pre"
    elif not _pcap_success(pcap_item, "post_proxy"):
        reason = "missing_post"
    elif protocol_dataset == "HYSTERIA2" or shared:
        reason = "shared_carrier"
    elif outer_id is None:
        reason = "missing_outer_connection_id"

    return PairEligibility(
        session_id=session_id,
        protocol_dataset=protocol_dataset,
        connection_id=connection_id,
        eligible=reason is None,
        pair_level="logical_connection" if reason is None else None,
        reason=reason,
        outer_connection_id=outer_id,
        carrier_id=carrier_id,
        post_transport=post_transport,
    )


def audit_session_indexes(session_path: Path | str, protocol_dataset: str) -> IndexAudit:
    session_dir = Path(session_path)
    analysis = session_dir / "analysis"
    connections = _load_items(analysis / "connection-index-v2.json")
    requests = _load_items(analysis / "request-index-v2.json")
    flows = _load_items(analysis / "flow-index.json")
    pcap_connections = _load_items(analysis / "pcap-index-v1.json", "connections")

    manifest = json.loads((session_dir / "manifest.json").read_text(encoding="utf-8"))
    session_id = str(manifest.get("session_id", ""))

    connection_ids_list = [str(item.get("connection_id", "")) for item in connections]
    connection_ids = set(connection_ids_list)
    request_occurrence_ids = [
        str(item.get("request_occurrence_id", "")) for item in requests
    ]
    request_ids = {
        str(item["request_id"])
        for item in requests
        if item.get("request_id") is not None
    }
    pcap_by_connection = {
        str(item.get("connection_id", "")): item for item in pcap_connections
    }

    request_connection_orphans = sum(
        1
        for item in requests
        if _string(item.get("connection_id")) is not None
        and str(item["connection_id"]) not in connection_ids
    )
    pcap_connection_orphans = sum(
        1
        for item in pcap_connections
        if str(item.get("connection_id", "")) not in connection_ids
    )
    connection_request_orphans = sum(
        1
        for item in connections
        for request_id in item.get("request_ids", [])
        if str(request_id) not in request_ids
    )

    outcomes = [_nested(item, "egress", "outcome") for item in connections]
    eligibility = tuple(
        _pair_eligibility(
            protocol_dataset,
            session_id,
            item,
            pcap_by_connection.get(str(item.get("connection_id", ""))),
        )
        for item in connections
    )
    proxy_connections = [
        item for item in connections if _nested(item, "egress", "outcome") == "proxy"
    ]
    carriers = {
        value
        for item in proxy_connections
        if (value := _string(_nested(item, "carrier_binding", "carrier_id"))) is not None
    }
    shared_count = sum(
        bool(_nested(item, "post_flow", "shared"))
        or _nested(item, "carrier_binding", "mode") == "shared"
        for item in proxy_connections
    )
    return IndexAudit(
        session_id=session_id,
        protocol_dataset=protocol_dataset,
        request_count=len(requests),
        connection_count=len(connections),
        logical_flow_count=len(flows),
        pcap_connection_count=len(pcap_connections),
        proxy_connection_count=outcomes.count("proxy"),
        direct_connection_count=outcomes.count("direct"),
        rejected_connection_count=outcomes.count("rejected"),
        shared_proxy_connection_count=shared_count,
        unique_carrier_count=len(carriers),
        eligible_exclusive_pair_count=sum(item.eligible for item in eligibility),
        request_connection_orphans=request_connection_orphans,
        pcap_connection_orphans=pcap_connection_orphans,
        connection_request_orphans=connection_request_orphans,
        duplicate_connection_ids=_duplicates(connection_ids_list),
        duplicate_request_occurrence_ids=_duplicates(request_occurrence_ids),
        eligibility=eligibility,
    )


def aggregate_index_audits(audits: list[IndexAudit]) -> dict[str, Any]:
    numeric_fields = (
        "request_count",
        "connection_count",
        "logical_flow_count",
        "pcap_connection_count",
        "proxy_connection_count",
        "direct_connection_count",
        "rejected_connection_count",
        "shared_proxy_connection_count",
        "unique_carrier_count",
        "eligible_exclusive_pair_count",
        "request_connection_orphans",
        "pcap_connection_orphans",
        "connection_request_orphans",
        "duplicate_connection_ids",
        "duplicate_request_occurrence_ids",
    )
    totals = {field: sum(getattr(audit, field) for audit in audits) for field in numeric_fields}
    by_protocol: dict[str, dict[str, int]] = {}
    for protocol in sorted({audit.protocol_dataset for audit in audits}):
        selected = [audit for audit in audits if audit.protocol_dataset == protocol]
        by_protocol[protocol] = {
            field: sum(getattr(audit, field) for audit in selected) for field in numeric_fields
        }
        by_protocol[protocol]["session_count"] = len(selected)
    return {"session_count": len(audits), "totals": totals, "by_protocol": by_protocol}

