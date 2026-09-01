"""Convert one capture artifact into immutable packet-event Parquet."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any, Iterator

import pyarrow as pa
import pyarrow.parquet as pq

from ..parsing import PcapNgReader, decode_packet
from ..schemas.fields import packet_event_schema


@dataclass(frozen=True, slots=True)
class CaptureSource:
    dataset_protocol: str
    session_id: str
    source_artifact_id: str
    source_path: Path
    capture_side: str

    def __post_init__(self) -> None:
        if self.capture_side not in {"pre", "post"}:
            raise ValueError("capture_side must be pre or post")


def _event_id(source: CaptureSource, interface_id: int, ordinal: int, timestamp_ns: int) -> str:
    material = (
        f"{source.source_artifact_id}\0{interface_id}\0{ordinal}\0{timestamp_ns}".encode("utf-8")
    )
    return hashlib.sha256(material).hexdigest()


def iter_packet_events(
    source: CaptureSource, *, offload_ip_len_threshold: int = 1500
) -> Iterator[dict[str, Any]]:
    if offload_ip_len_threshold <= 0:
        raise ValueError("offload_ip_len_threshold must be positive")
    reader = PcapNgReader(source.source_path)
    for record in reader:
        parsed = decode_packet(record.link_type, record.packet_data)
        ip_total_len = parsed.ip_total_len
        payload_len = parsed.transport_payload_len
        yield {
            "packet_event_id": _event_id(
                source, record.interface_id, record.packet_ordinal, record.timestamp_ns
            ),
            "dataset_protocol": source.dataset_protocol,
            "session_id": source.session_id,
            "source_artifact_id": source.source_artifact_id,
            "source_path": str(source.source_path),
            "capture_side": source.capture_side,
            "interface_id": record.interface_id,
            "link_type": record.link_type,
            "packet_ordinal": record.packet_ordinal,
            "timestamp_ns": record.timestamp_ns,
            "captured_len": record.captured_len,
            "original_len": record.original_len,
            "ip_version": parsed.ip_version,
            "ip_src": parsed.ip_src,
            "ip_dst": parsed.ip_dst,
            "ip_total_len": ip_total_len,
            "ip_header_len": parsed.ip_header_len,
            "ip_protocol": parsed.ip_protocol,
            "ip_fragment_offset": parsed.ip_fragment_offset,
            "ip_more_fragments": parsed.ip_more_fragments,
            "transport_protocol": parsed.transport_protocol,
            "src_port": parsed.src_port,
            "dst_port": parsed.dst_port,
            "transport_header_len": parsed.transport_header_len,
            "transport_payload_len": payload_len,
            "tcp_seq": parsed.tcp_seq,
            "tcp_ack": parsed.tcp_ack,
            "tcp_flags_raw": parsed.tcp_flags_raw,
            "tcp_window_raw": parsed.tcp_window_raw,
            "tcp_urgent_pointer": parsed.tcp_urgent_pointer,
            "tcp_options_raw": parsed.tcp_options_raw,
            "udp_length": parsed.udp_length,
            "decode_status": parsed.decode_status,
            "decode_reason": parsed.decode_reason,
            "entity_id": None,
            "entity_level": None,
            "direction": None,
            "relative_time_ns": None,
            "packet_iat_ns": None,
            "is_transport_payload_nonempty": (
                payload_len > 0 if payload_len is not None else None
            ),
            "is_ip_fragment": (
                bool(parsed.ip_fragment_offset or parsed.ip_more_fragments)
                if parsed.ip_fragment_offset is not None
                else None
            ),
            "offload_suspected": (
                ip_total_len > offload_ip_len_threshold if ip_total_len is not None else None
            ),
        }


def write_packet_events(
    source: CaptureSource,
    output_path: Path | str,
    *,
    offload_ip_len_threshold: int = 1500,
    batch_size: int = 8192,
) -> dict[str, int]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    schema = packet_event_schema()
    writer: pq.ParquetWriter | None = None
    rows: list[dict[str, Any]] = []
    packet_count = 0
    decode_failed_count = 0
    try:
        for event in iter_packet_events(
            source, offload_ip_len_threshold=offload_ip_len_threshold
        ):
            rows.append(event)
            packet_count += 1
            decode_failed_count += event["decode_status"] == "failed"
            if len(rows) >= batch_size:
                writer = _flush(rows, output, schema, writer)
        if rows:
            writer = _flush(rows, output, schema, writer)
        elif writer is None:
            pq.write_table(pa.Table.from_pylist([], schema=schema), output)
    finally:
        if writer is not None:
            writer.close()
    return {"packet_count": packet_count, "decode_failed_count": decode_failed_count}


def _flush(
    rows: list[dict[str, Any]],
    output: Path,
    schema: pa.Schema,
    writer: pq.ParquetWriter | None,
) -> pq.ParquetWriter:
    table = pa.Table.from_pylist(rows, schema=schema)
    if writer is None:
        writer = pq.ParquetWriter(output, schema, compression="zstd")
    writer.write_table(table)
    rows.clear()
    return writer

