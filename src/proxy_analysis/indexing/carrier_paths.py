"""Direction evidence for a session-local carrier, including UDP path changes."""
from __future__ import annotations

import json
from pathlib import Path

from ..pathutils import filesystem_path
from ..sequences.direction import Endpoint


def bounded_events(events: list[dict], summary: dict) -> list[dict]:
    snapshots = summary.get("trace_snapshot", {}).get("traces", [])
    if len(snapshots) != 1 or not snapshots[0].get("barrier_verified"):
        raise ValueError("single verified trace barrier required")
    snapshot = snapshots[0]
    cutoff = snapshot["cutoff_event_seq"]
    causal = set(snapshot.get("causal_tail_event_seqs", []))
    return [e for e in events if e.get("event_seq", cutoff + 1) <= cutoff
            or e.get("event_seq") in causal]


def carrier_paths(session: Path) -> dict[str, tuple[tuple[Endpoint, Endpoint], ...]]:
    def read(relative):
        return json.loads(Path(filesystem_path(session / relative)).read_text(encoding="utf-8"))

    paths: dict[str, set[tuple[Endpoint, Endpoint]]] = {}

    def add(cid, flow):
        if not cid or any(flow.get(k) is None for k in ("src_ip", "src_port", "dst_ip", "dst_port")):
            return
        pair = (Endpoint(flow["src_ip"], int(flow["src_port"])),
                Endpoint(flow["dst_ip"], int(flow["dst_port"])))
        bucket = paths.setdefault(cid, set())
        if pair[::-1] in bucket or pair[0] == pair[1]:
            raise ValueError(f"ambiguous carrier path orientation: {cid}")
        bucket.add(pair)

    index = Path(filesystem_path(session / "analysis/flow-index.json"))
    if index.is_file():
        for flow in read("analysis/flow-index.json").get("items", []):
            binding = flow.get("carrier_binding") or {}
            for physical in binding.get("physical_paths", []):
                add(binding.get("carrier_id"), physical)
    trace = Path(filesystem_path(session / "raw/mihomo-trace.jsonl"))
    summary = Path(filesystem_path(session / "analysis/summary.json"))
    if trace.is_file() and summary.is_file():
        evidence = read("analysis/summary.json")
        # Older datasets without a verified snapshot use indexed paths only.
        if evidence.get("trace_snapshot", {}).get("traces"):
            events = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line.strip()]
            for event in bounded_events(events, evidence):
                for physical in event.get("carrier_paths", []):
                    add(event.get("carrier_id"), physical)
                if event.get("post_flow"):
                    add(event.get("carrier_id"), event["post_flow"])
    return {cid: tuple(sorted(values, key=lambda p: (p[0].ip, p[0].port, p[1].ip, p[1].port)))
            for cid, values in paths.items()}
