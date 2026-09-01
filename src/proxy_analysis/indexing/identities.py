"""Build capture entities from TrafficTracer's authoritative tuple mappings."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from ..sequences.direction import Endpoint


@dataclass(frozen=True, slots=True)
class EntityDescriptor:
    session_id: str
    protocol_dataset: str
    entity_id: str
    entity_level: str
    capture_side: str
    capture_path: Path
    artifact_id: str
    transport_protocol: str
    initiator: Endpoint
    responder: Endpoint
    shared: bool
    egress_outcome: str | None
    logical_connection_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _Candidate:
    session_id: str
    protocol_dataset: str
    entity_id: str
    entity_level: str
    capture_side: str
    capture_path: Path
    artifact_id: str
    transport_protocol: str
    initiator: Endpoint
    responder: Endpoint
    shared: bool
    egress_outcome: str | None
    logical_connection_id: str


def _load(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _endpoint(flow: Mapping[str, Any], source: bool) -> Endpoint:
    prefix = "src" if source else "dst"
    ip = flow.get(f"{prefix}_ip")
    port = flow.get(f"{prefix}_port")
    if not isinstance(ip, str) or not ip:
        raise ValueError(f"incomplete endpoint: {flow}")
    return Endpoint(ip, int(port) if isinstance(port, int) else None)


def _is_success(side: Any) -> bool:
    return isinstance(side, Mapping) and side.get("status") == "success"


def build_entity_descriptors(
    session_path: Path | str, protocol_dataset: str
) -> list[EntityDescriptor]:
    """Create one descriptor per physical packet sequence, deduplicating carriers."""
    session_dir = Path(session_path)
    manifest = _load(session_dir / "manifest.json")
    session_id = str(manifest.get("session_id", ""))
    connection_index = _load(session_dir / "analysis/connection-index-v2.json")
    pcap_index = _load(session_dir / "analysis/pcap-index-v1.json")
    connections = {
        str(item.get("connection_id")): item
        for item in connection_index.get("items", [])
        if isinstance(item, dict)
    }
    candidates: list[_Candidate] = []

    for pcap in pcap_index.get("connections", []):
        if not isinstance(pcap, dict):
            continue
        connection_id = str(pcap.get("connection_id", ""))
        connection = connections.get(connection_id)
        if connection is None:
            continue
        outcome = _nested_string(connection, "egress", "outcome")

        pre = pcap.get("pre_proxy")
        pre_flow = connection.get("pre_flow")
        if _is_success(pre) and isinstance(pre, Mapping) and isinstance(pre_flow, Mapping):
            candidates.append(
                _Candidate(
                    session_id,
                    protocol_dataset,
                    connection_id,
                    "logical_connection",
                    "pre",
                    session_dir / str(pre["path"]),
                    str(pre.get("artifact_id", f"{connection_id}-pre")),
                    str(pre_flow.get("network", pcap.get("protocol", "unknown"))),
                    _endpoint(pre_flow, True),
                    _endpoint(pre_flow, False),
                    False,
                    outcome,
                    connection_id,
                )
            )

        post = pcap.get("post_proxy")
        post_flow = connection.get("post_flow")
        if not (_is_success(post) and isinstance(post, Mapping) and isinstance(post_flow, Mapping)):
            continue
        shared = bool(post_flow.get("shared")) or _nested_string(
            connection, "carrier_binding", "mode"
        ) == "shared"
        carrier_id = _nested_string(connection, "carrier_binding", "carrier_id")
        if shared:
            if not carrier_id:
                raise ValueError(f"shared post flow lacks carrier_id: {connection_id}")
            entity_id = carrier_id
            level = "carrier"
        else:
            entity_id = str(connection.get("outer_connection_id") or connection_id)
            level = "outer_connection"
        candidates.append(
            _Candidate(
                session_id,
                protocol_dataset,
                entity_id,
                level,
                "post",
                session_dir / str(post["path"]),
                str(post.get("artifact_id", f"{entity_id}-post")),
                str(post_flow.get("network", "unknown")),
                _endpoint(post_flow, True),
                _endpoint(post_flow, False),
                shared,
                outcome,
                connection_id,
            )
        )
    return _merge_candidates(candidates)


def _nested_string(value: Mapping[str, Any], *keys: str) -> str | None:
    current: Any = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current if isinstance(current, str) and current else None


def _merge_candidates(candidates: list[_Candidate]) -> list[EntityDescriptor]:
    groups: dict[tuple[str, str, str, str], list[_Candidate]] = {}
    for item in candidates:
        key = (item.capture_side, item.entity_level, item.entity_id, str(item.capture_path))
        groups.setdefault(key, []).append(item)

    descriptors: list[EntityDescriptor] = []
    for key in sorted(groups):
        items = groups[key]
        first = items[0]
        initiator = _merge_endpoint([item.initiator for item in items])
        responder = _merge_endpoint([item.responder for item in items])
        protocols = {item.transport_protocol for item in items}
        if len(protocols) != 1:
            raise ValueError(f"entity has inconsistent transports: {key}: {protocols}")
        outcomes = {item.egress_outcome for item in items}
        descriptors.append(
            EntityDescriptor(
                session_id=first.session_id,
                protocol_dataset=first.protocol_dataset,
                entity_id=first.entity_id,
                entity_level=first.entity_level,
                capture_side=first.capture_side,
                capture_path=first.capture_path,
                artifact_id=first.artifact_id,
                transport_protocol=first.transport_protocol,
                initiator=initiator,
                responder=responder,
                shared=first.shared,
                egress_outcome=next(iter(outcomes)) if len(outcomes) == 1 else None,
                logical_connection_ids=tuple(
                    sorted({item.logical_connection_id for item in items})
                ),
            )
        )
    return descriptors


def _merge_endpoint(endpoints: list[Endpoint]) -> Endpoint:
    ips = {item.ip for item in endpoints}
    if len(ips) != 1:
        raise ValueError(f"entity endpoint has multiple IPs: {sorted(ips)}")
    ports = {item.port for item in endpoints}
    return Endpoint(next(iter(ips)), next(iter(ports)) if len(ports) == 1 else None)

