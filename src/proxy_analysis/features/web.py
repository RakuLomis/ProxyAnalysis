"""URL/host flow counts, request concurrency, and proxy carrier multiplexing."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit

from .concurrency import Interval, concurrency_features


def _load_items(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    items = value.get("items")
    if not isinstance(items, list):
        raise ValueError(f"index items must be a list: {path}")
    return [item for item in items if isinstance(item, dict)]


def _seconds_to_ns(value: Any) -> int | None:
    return round(float(value) * 1_000_000_000) if isinstance(value, (int, float)) else None


def _connection_interval(connection: Mapping[str, Any]) -> tuple[Interval | None, str | None]:
    timing = connection.get("timing")
    if not isinstance(timing, Mapping):
        return None, None
    start = _seconds_to_ns(timing.get("first_observed"))
    last = _seconds_to_ns(timing.get("last_observed"))
    if start is None:
        return None, None
    end_candidates: list[tuple[int, str]] = []
    if last is not None and last >= start:
        end_candidates.append((last, "last_observed"))
    terminal = connection.get("terminal")
    if isinstance(terminal, Mapping) and isinstance(terminal.get("duration_ms"), (int, float)):
        terminal_end = start + round(float(terminal["duration_ms"]) * 1_000_000)
        if terminal_end >= start:
            end_candidates.append((terminal_end, "terminal_duration"))
    if not end_candidates:
        return Interval(str(connection.get("connection_id", "")), start, start), "start_only"
    end, source = max(end_candidates, key=lambda item: item[0])
    return Interval(str(connection.get("connection_id", "")), start, end), source


def _request_interval(
    request: Mapping[str, Any], connection_intervals: Mapping[str, Interval]
) -> tuple[Interval | None, str | None]:
    timing = request.get("timing")
    if not isinstance(timing, Mapping):
        return None, None
    start = _seconds_to_ns(timing.get("request"))
    if start is None:
        return None, None
    candidates = [
        (end, name)
        for name in ("completion", "response")
        if (end := _seconds_to_ns(timing.get(name))) is not None and end >= start
    ]
    if candidates:
        end, source = max(candidates, key=lambda item: item[0])
    else:
        connection_id = request.get("connection_id")
        connection = connection_intervals.get(str(connection_id))
        if connection is not None and connection.end_ns >= start:
            end, source = connection.end_ns, "connection_end_fallback"
        else:
            end, source = start, "start_only"
    return Interval(str(request.get("request_occurrence_id", "")), start, end), source


def _url_parts(url: str) -> tuple[str, str, str]:
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    origin = f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return url_hash, origin, host


def extract_web_features(session_path: Path | str, protocol_dataset: str) -> dict[str, Any]:
    session = Path(session_path)
    manifest = json.loads((session / "manifest.json").read_text(encoding="utf-8"))
    session_id = str(manifest.get("session_id", ""))
    requests = _load_items(session / "analysis/request-index-v2.json")
    connections = _load_items(session / "analysis/connection-index-v2.json")
    connection_by_id = {str(item.get("connection_id", "")): item for item in connections}

    connection_intervals: dict[str, Interval] = {}
    connection_end_sources: dict[str, int] = {}
    for connection in connections:
        interval, source = _connection_interval(connection)
        if interval is not None:
            connection_intervals[interval.entity_id] = interval
        if source is not None:
            connection_end_sources[source] = connection_end_sources.get(source, 0) + 1

    request_intervals: list[Interval] = []
    request_end_sources: dict[str, int] = {}
    request_rows = []
    for request in requests:
        interval, source = _request_interval(request, connection_intervals)
        if interval is not None:
            request_intervals.append(interval)
        if source is not None:
            request_end_sources[source] = request_end_sources.get(source, 0) + 1
        url = str(request.get("url", ""))
        url_hash, origin, host = _url_parts(url)
        request_rows.append(
            {
                "request_occurrence_id": str(request.get("request_occurrence_id", "")),
                "connection_id": str(request.get("connection_id", "")) if request.get("connection_id") else None,
                "url_hash": url_hash,
                "origin": origin,
                "host": host,
            }
        )

    url_groups: dict[str, list[dict[str, Any]]] = {}
    host_groups: dict[str, list[dict[str, Any]]] = {}
    for row in request_rows:
        url_groups.setdefault(row["url_hash"], []).append(row)
        host_groups.setdefault(row["host"], []).append(row)

    def grouped_features(groups: Mapping[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
        output = []
        for key, rows in sorted(groups.items()):
            connection_ids = {
                row["connection_id"] for row in rows if row["connection_id"] is not None
            }
            outcomes = [
                _outcome(connection_by_id.get(connection_id)) for connection_id in connection_ids
            ]
            output.append(
                {
                    "key": key,
                    "request_occurrence_count": len(rows),
                    "unique_connection_count": len(connection_ids),
                    "proxy_connection_count": outcomes.count("proxy"),
                    "direct_connection_count": outcomes.count("direct"),
                    "rejected_connection_count": outcomes.count("rejected"),
                    "connection_reuse_factor": (
                        len(rows) / len(connection_ids) if connection_ids else None
                    ),
                }
            )
        return output

    carrier_groups: dict[str, list[dict[str, Any]]] = {}
    for connection in connections:
        carrier_id = _nested_string(connection, "carrier_binding", "carrier_id")
        if carrier_id and _outcome(connection) == "proxy":
            carrier_groups.setdefault(carrier_id, []).append(connection)
    carrier_rows = []
    for carrier_id, bound in sorted(carrier_groups.items()):
        connection_ids = {str(item.get("connection_id", "")) for item in bound}
        urls = {url for item in bound for url in item.get("urls", []) if isinstance(url, str)}
        hosts = {_url_parts(url)[2] for url in urls}
        intervals = [
            connection_intervals[connection_id]
            for connection_id in connection_ids
            if connection_id in connection_intervals
        ]
        carrier_rows.append(
            {
                "carrier_id": carrier_id,
                "logical_connection_count": len(connection_ids),
                "unique_url_count": len(urls),
                "unique_host_count": len(hosts),
                "connection_concurrency": asdict(concurrency_features(intervals)),
            }
        )

    return {
        "session_id": session_id,
        "protocol_dataset": protocol_dataset,
        "request_count": len(requests),
        "connection_count": len(connections),
        "request_concurrency": asdict(concurrency_features(request_intervals)),
        "connection_concurrency": asdict(
            concurrency_features(connection_intervals.values())
        ),
        "request_end_time_sources": dict(sorted(request_end_sources.items())),
        "connection_end_time_sources": dict(sorted(connection_end_sources.items())),
        "url_features": grouped_features(url_groups),
        "host_features": grouped_features(host_groups),
        "carrier_features": carrier_rows,
        "privacy": {"full_url_stored": False, "url_identity": "sha256"},
    }


def _outcome(connection: Mapping[str, Any] | None) -> str | None:
    return _nested_string(connection, "egress", "outcome") if connection else None


def _nested_string(value: Mapping[str, Any], *keys: str) -> str | None:
    current: Any = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current if isinstance(current, str) and current else None

