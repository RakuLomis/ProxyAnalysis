"""Assemble versioned single-entity core features from atomic implementations."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, TYPE_CHECKING

from ..config import FeatureConfig
if TYPE_CHECKING:
    from ..pipeline.analyze_entity import EntityAnalysis
from .active_idle import active_idle_periods
from .burst import direction_run_bursts, time_gap_bursts
from .cumulative import cumulative_shape
from .distribution import distribution_summary, fixed_histogram
from .models import PacketMeasure, ordered_packets
from .reversal import reversal_features
from .transition import transition_features
from .volume import directional_volume
from .tcp_transport import tcp_transport_features


def _iats(packets: list[PacketMeasure]) -> list[int]:
    return [
        current.timestamp_ns - previous.timestamp_ns
        for previous, current in zip(packets, packets[1:])
    ]


def _distribution_by_direction(
    packets: list[PacketMeasure], attribute: str
) -> dict[str, dict[str, float | int | None]]:
    result = {}
    for name, direction in (("all", None), ("up", 1), ("down", -1)):
        selected = [
            getattr(item, attribute)
            for item in packets
            if direction is None or item.direction == direction
        ]
        result[name] = distribution_summary(selected)
    return result


def extract_core_entity_features(
    analysis: EntityAnalysis, config: FeatureConfig
) -> dict[str, Any]:
    packets = ordered_packets(analysis.packet_measures)
    nonempty = [item for item in packets if item.transport_payload_len > 0]
    sequence_prefix = max(int(value) for value in config.values["sequence"]["prefix_lengths"])
    epsilon = float(config.values["ratios"]["epsilon"])
    hist = config.values["histograms"]
    grid_points = int(config.values["cumulative_shape"]["grid_points"])
    is_datagram_reversal = analysis.descriptor.transport_protocol == "udp"

    result: dict[str, Any] = {
        "feature_schema_version": config.schema_version,
        "feature_config_sha256": config.sha256,
        "session_id": analysis.descriptor.session_id,
        "protocol_dataset": analysis.descriptor.protocol_dataset,
        "entity_id": analysis.descriptor.entity_id,
        "entity_level": analysis.descriptor.entity_level,
        "capture_side": analysis.descriptor.capture_side,
        "transport_protocol": analysis.descriptor.transport_protocol,
        "shared": analysis.descriptor.shared,
        "packet_count": len(packets),
        "unknown_direction_count": analysis.unknown_direction_count,
        "duration_ns": (
            packets[-1].timestamp_ns - packets[0].timestamp_ns if packets else None
        ),
        "sequences": {
            "prefix_length": sequence_prefix,
            "direction": [item.direction for item in packets[:sequence_prefix]],
            "signed_transport_payload_len": [
                item.direction * item.transport_payload_len
                for item in packets[:sequence_prefix]
            ],
            "signed_ip_total_len": [
                item.direction * item.ip_total_len for item in packets[:sequence_prefix]
            ],
            "iat_ns": [None, *_iats(packets)][:sequence_prefix] if packets else [],
        },
        "volume": directional_volume(packets, epsilon=epsilon),
        "distributions": {
            "transport_payload_len": _distribution_by_direction(
                packets, "transport_payload_len"
            ),
            "ip_total_len": _distribution_by_direction(packets, "ip_total_len"),
            "iat_ns": distribution_summary(_iats(packets)),
            "nonempty_iat_ns": distribution_summary(_iats(nonempty)),
        },
        "histograms": {
            "transport_payload_len": fixed_histogram(
                (item.transport_payload_len for item in packets),
                hist["transport_payload_len_edges_bytes"],
            ),
            "ip_total_len": fixed_histogram(
                (item.ip_total_len for item in packets), hist["ip_total_len_edges_bytes"]
            ),
            "iat_us": fixed_histogram(
                (value / 1000 for value in _iats(packets)), hist["iat_edges_us"]
            ),
        },
        "transition_nonempty": asdict(
            transition_features(item.direction for item in nonempty)
        ),
        "cumulative_shape": {
            "normalized_time": asdict(
                cumulative_shape(
                    packets, axis="normalized_time", grid_points=grid_points
                )
            ),
            "normalized_packet_index": asdict(
                cumulative_shape(
                    packets, axis="normalized_packet_index", grid_points=grid_points
                )
            ),
        },
    }

    reversal_key = "carrier_datagram_reversal" if is_datagram_reversal else "flow_reversal"
    result[reversal_key] = {
        "observed": asdict(reversal_features(packets)),
        "unique_seq": (
            None if is_datagram_reversal else asdict(reversal_features(packets, unique_seq=True))
        ),
        "reason": "not_applicable_transport" if is_datagram_reversal else None,
    }

    direction_bursts = direction_run_bursts(packets)
    result["direction_run_burst"] = {
        "count": len(direction_bursts),
        "packet_count": distribution_summary(item.packet_count for item in direction_bursts),
        "transport_payload_bytes": distribution_summary(
            item.transport_payload_bytes for item in direction_bursts
        ),
        "duration_ns": distribution_summary(item.duration_ns for item in direction_bursts),
    }
    result["time_gap_burst"] = {}
    for threshold_ms in config.values["burst"]["time_gap_thresholds_ms"]:
        threshold_ns = int(threshold_ms * 1_000_000)
        bursts = time_gap_bursts(packets, threshold_ns)
        result["time_gap_burst"][f"{threshold_ms}ms"] = {
            "count": len(bursts),
            "packet_count": distribution_summary(item.packet_count for item in bursts),
            "transport_payload_bytes": distribution_summary(
                item.transport_payload_bytes for item in bursts
            ),
            "duration_ns": distribution_summary(item.duration_ns for item in bursts),
        }

    result["active_idle"] = {}
    for threshold_ms in config.values["active_idle"]["thresholds_ms"]:
        periods = active_idle_periods(packets, int(threshold_ms * 1_000_000))
        result["active_idle"][f"{threshold_ms}ms"] = {
            "active_duration_ns": distribution_summary(periods.active_durations_ns),
            "idle_duration_ns": distribution_summary(periods.idle_durations_ns),
        }

    if analysis.tcp is None:
        result["tcp_state"] = {"applicable": False, "reason": "not_applicable_transport"}
        result["tcp_transport"] = {
            "applicable": False,
            "reason": "not_applicable_transport",
        }
    else:
        result["tcp_state"] = {
            "applicable": True,
            "full_retransmission_count": analysis.tcp.full_retransmission_count,
            "partial_retransmission_count": analysis.tcp.partial_retransmission_count,
            "out_of_order_count": analysis.tcp.out_of_order_count,
            "retransmitted_payload_bytes": sum(
                item.retransmitted_payload_bytes for item in analysis.tcp.segments
            ),
            "unique_payload_bytes": sum(item.new_payload_bytes for item in analysis.tcp.segments),
            "rtt_ns": distribution_summary(item.rtt_ns for item in analysis.tcp.rtt_samples),
            "rtt_sample_count": len(analysis.tcp.rtt_samples),
        }
        result["tcp_transport"] = tcp_transport_features(analysis.tcp_packets)
    return result
