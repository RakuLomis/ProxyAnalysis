"""Build eligible exclusive pre/post pairs without copying packet sequences."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .identities import EntityDescriptor, build_entity_descriptors


@dataclass(frozen=True, slots=True)
class ExclusivePair:
    session_id: str
    protocol_dataset: str
    connection_id: str
    pre: EntityDescriptor
    post: EntityDescriptor


def build_exclusive_pairs(
    session_path: Path | str, protocol_dataset: str
) -> list[ExclusivePair]:
    if protocol_dataset == "HYSTERIA2":
        return []
    descriptors = build_entity_descriptors(session_path, protocol_dataset)
    pre_by_connection = {
        item.entity_id: item
        for item in descriptors
        if item.capture_side == "pre"
        and item.entity_level == "logical_connection"
        and item.egress_outcome == "proxy"
    }
    post_by_connection: dict[str, EntityDescriptor] = {}
    for item in descriptors:
        if (
            item.capture_side != "post"
            or item.entity_level != "outer_connection"
            or item.egress_outcome != "proxy"
            or item.shared
        ):
            continue
        for connection_id in item.logical_connection_ids:
            if connection_id in post_by_connection:
                raise ValueError(f"duplicate exclusive post mapping: {connection_id}")
            post_by_connection[connection_id] = item

    pairs = []
    for connection_id in sorted(pre_by_connection.keys() & post_by_connection.keys()):
        pre = pre_by_connection[connection_id]
        post = post_by_connection[connection_id]
        pairs.append(
            ExclusivePair(
                session_id=pre.session_id,
                protocol_dataset=protocol_dataset,
                connection_id=connection_id,
                pre=pre,
                post=post,
            )
        )
    return pairs

