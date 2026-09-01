"""Hysteria2 page-level inner-flow to shared-carrier relationships."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .identities import EntityDescriptor, build_entity_descriptors


@dataclass(frozen=True, slots=True)
class Hysteria2CarrierWindow:
    session_id: str
    carrier_id: str
    pre_connections: tuple[EntityDescriptor, ...]
    post_carrier: EntityDescriptor


def build_hysteria2_carrier_windows(
    session_path: Path | str,
) -> list[Hysteria2CarrierWindow]:
    descriptors = build_entity_descriptors(session_path, "HYSTERIA2")
    pre_by_connection = {
        item.entity_id: item
        for item in descriptors
        if item.capture_side == "pre" and item.egress_outcome == "proxy"
    }
    windows: list[Hysteria2CarrierWindow] = []
    for carrier in descriptors:
        if carrier.entity_level != "carrier" or carrier.capture_side != "post":
            continue
        pre = tuple(
            pre_by_connection[connection_id]
            for connection_id in carrier.logical_connection_ids
            if connection_id in pre_by_connection
        )
        if not pre:
            continue
        windows.append(
            Hysteria2CarrierWindow(
                session_id=carrier.session_id,
                carrier_id=carrier.entity_id,
                pre_connections=pre,
                post_carrier=carrier,
            )
        )
    return sorted(windows, key=lambda item: item.carrier_id)

