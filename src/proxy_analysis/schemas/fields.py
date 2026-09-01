"""Arrow schemas for immutable intermediate records."""

from __future__ import annotations

import pyarrow as pa


PACKET_SCHEMA_VERSION = 1


def packet_event_schema() -> pa.Schema:
    metadata = {
        b"schema_name": b"packet_event",
        b"schema_version": str(PACKET_SCHEMA_VERSION).encode("ascii"),
        b"timestamp_unit": b"ns",
        b"length_semantics": b"captured_len,is_not_wire_length",
    }
    return pa.schema(
        [
            pa.field("packet_event_id", pa.string(), nullable=False),
            pa.field("dataset_protocol", pa.string(), nullable=False),
            pa.field("session_id", pa.string(), nullable=False),
            pa.field("source_artifact_id", pa.string(), nullable=False),
            pa.field("source_path", pa.string(), nullable=False),
            pa.field("capture_side", pa.string(), nullable=False),
            pa.field("interface_id", pa.int32(), nullable=False),
            pa.field("link_type", pa.int32(), nullable=False),
            pa.field("packet_ordinal", pa.int64(), nullable=False),
            pa.field("timestamp_ns", pa.int64(), nullable=False),
            pa.field("captured_len", pa.int32(), nullable=False),
            pa.field("original_len", pa.int32(), nullable=False),
            pa.field("ip_version", pa.int8()),
            pa.field("ip_src", pa.string()),
            pa.field("ip_dst", pa.string()),
            pa.field("ip_total_len", pa.int32()),
            pa.field("ip_header_len", pa.int16()),
            pa.field("ip_protocol", pa.int16()),
            pa.field("ip_fragment_offset", pa.int32()),
            pa.field("ip_more_fragments", pa.bool_()),
            pa.field("transport_protocol", pa.string()),
            pa.field("src_port", pa.int32()),
            pa.field("dst_port", pa.int32()),
            pa.field("transport_header_len", pa.int16()),
            pa.field("transport_payload_len", pa.int32()),
            pa.field("tcp_seq", pa.uint32()),
            pa.field("tcp_ack", pa.uint32()),
            pa.field("tcp_flags_raw", pa.uint16()),
            pa.field("tcp_window_raw", pa.uint16()),
            pa.field("tcp_urgent_pointer", pa.uint16()),
            pa.field("tcp_options_raw", pa.binary()),
            pa.field("udp_length", pa.uint16()),
            pa.field("decode_status", pa.string(), nullable=False),
            pa.field("decode_reason", pa.string()),
            pa.field("entity_id", pa.string()),
            pa.field("entity_level", pa.string()),
            pa.field("direction", pa.int8()),
            pa.field("relative_time_ns", pa.int64()),
            pa.field("packet_iat_ns", pa.int64()),
            pa.field("is_transport_payload_nonempty", pa.bool_()),
            pa.field("is_ip_fragment", pa.bool_()),
            pa.field("offload_suspected", pa.bool_()),
        ],
        metadata=metadata,
    )

