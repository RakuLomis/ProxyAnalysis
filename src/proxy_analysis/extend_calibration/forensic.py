"""Narrow socket-lineage evidence. No hostname/time-nearest rematching."""
from collections import defaultdict
from decimal import Decimal
from urllib.parse import urlsplit


def endpoint(value):
    host, port = value.rsplit(":", 1)
    return host.strip("[]"), int(port)


def flow_tuple(flow):
    return (flow.get("network"), flow.get("src_ip"), flow.get("src_port"),
            flow.get("dst_ip"), flow.get("dst_port"))


def utc_ns(tick_ms, offset_ms):
    return int((Decimal(str(tick_ms)) + Decimal(str(offset_ms))) * 1_000_000)


def successful_socket(netlog, h2_source, target_url):
    types = {v: k for k, v in netlog["constants"]["logEventTypes"].items()}
    by_source = defaultdict(list)
    for e in netlog["events"]:
        by_source[e["source"]["id"]].append(e)
    events = by_source[h2_source]
    initializes = [e for e in events if types[e["type"]] == "HTTP2_SESSION_INITIALIZED"]
    if len(initializes) != 1:
        raise ValueError("HTTP2 initialized dependency is not unique")
    socket_id = initializes[0]["params"]["source_dependency"]["id"]
    ends = [e for e in by_source[socket_id] if types[e["type"]] == "TCP_CONNECT" and e["phase"] == 2
            and e.get("params", {}).get("local_address") and e.get("params", {}).get("remote_address")
            and not e.get("params", {}).get("net_error")]
    if len(ends) != 1:
        raise ValueError("successful TCP_CONNECT is not unique")
    parsed = urlsplit(target_url)
    expected_path = parsed.path + ("?" + parsed.query if parsed.query else "")
    streams = set()
    for e in events:
        params = e.get("params") or {}
        if types[e["type"]] == "HTTP2_SESSION_SEND_HEADERS":
            headers = params.get("headers", [])
            if ":path: " + expected_path in headers and ":authority: " + parsed.netloc in headers:
                streams.add(params["stream_id"])
    received = [e for e in events if types[e["type"]] == "HTTP2_SESSION_RECV_HEADERS"
                and (e.get("params") or {}).get("stream_id") in streams
                and ":status: 200" in (e.get("params") or {}).get("headers", [])]
    if not received:
        raise ValueError("no same-stream successful target response")
    local = endpoint(ends[0]["params"]["local_address"])
    remote = endpoint(ends[0]["params"]["remote_address"])
    return {"h2_source": h2_source, "socket_source": socket_id,
        "stream_ids": sorted(streams), "successful_stream_ids": sorted({e["params"]["stream_id"] for e in received}),
        "tcp_connect_end_ns": utc_ns(ends[0]["time"], netlog["constants"]["timeTickOffset"]),
        "h2_initialized_ns": utc_ns(initializes[0]["time"], netlog["constants"]["timeTickOffset"]),
        "response_first_ns": min(utc_ns(e["time"], netlog["constants"]["timeTickOffset"]) for e in received),
        "pre_flow": dict(network="tcp", src_ip=local[0], src_port=local[1], dst_ip=remote[0], dst_port=remote[1])}
