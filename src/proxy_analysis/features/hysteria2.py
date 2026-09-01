"""Hysteria2 aggregate-inner versus shared-carrier window features."""

from __future__ import annotations

from dataclasses import asdict
import math
from typing import Any, Iterable, Callable, TYPE_CHECKING

from ..config import FeatureConfig
from ..indexing.hysteria2 import Hysteria2CarrierWindow
from .burst import direction_run_bursts
from .cumulative import cumulative_shape
from .distribution import fixed_histogram
from .models import PacketMeasure, ordered_packets
from .pairwise import (
    _curve_distances,
    _normalize_curve,
    _sample_distances,
    js_divergence,
    log_ratio,
    normalized_difference,
)
from .reversal import reversal_features

if TYPE_CHECKING:
    from ..indexing.identities import EntityDescriptor
    from ..pipeline.analyze_entity import EntityAnalysis


def select_time_envelope(
    packets: Iterable[PacketMeasure], start_ns: int, end_ns: int
) -> list[PacketMeasure]:
    if end_ns < start_ns:
        raise ValueError("window end must be >= start")
    return [
        item
        for item in ordered_packets(tuple(packets))
        if start_ns <= item.timestamp_ns <= end_ns
    ]


def _iats_log1p_us(packets: list[PacketMeasure]) -> list[float]:
    return [
        math.log1p((current.timestamp_ns - previous.timestamp_ns) / 1000)
        for previous, current in zip(packets, packets[1:])
    ]


def _window_comparison(
    pre: list[PacketMeasure],
    post: list[PacketMeasure],
    config: FeatureConfig,
) -> dict[str, Any]:
    epsilon = float(config.values["ratios"]["epsilon"])
    low_power = int(config.values["pairing"]["low_power_min_samples"])
    grid_points = int(config.values["cumulative_shape"]["grid_points"])
    edges = config.values["histograms"]["transport_payload_len_edges_bytes"]
    pre_payload = sum(item.transport_payload_len for item in pre)
    post_payload = sum(item.transport_payload_len for item in post)
    pre_duration = pre[-1].timestamp_ns - pre[0].timestamp_ns if pre else 0
    post_duration = post[-1].timestamp_ns - post[0].timestamp_ns if post else 0

    scalar_raw = {
        "packet_count": (len(pre), len(post)),
        "transport_payload_bytes": (pre_payload, post_payload),
        "duration_ns": (pre_duration, post_duration),
        "direction_run_burst_count": (
            len(direction_run_bursts(pre)),
            len(direction_run_bursts(post)),
        ),
    }
    scalar = {
        name: {
            "pre": before,
            "post": after,
            "log_ratio": log_ratio(after, before, epsilon),
            "normalized_difference": normalized_difference(after, before),
        }
        for name, (before, after) in scalar_raw.items()
    }

    pre_lengths = [float(item.transport_payload_len) for item in pre if item.transport_payload_len]
    post_lengths = [float(item.transport_payload_len) for item in post if item.transport_payload_len]
    pre_hist = fixed_histogram(pre_lengths, edges)
    post_hist = fixed_histogram(post_lengths, edges)
    length = _sample_distances(pre_lengths, post_lengths, low_power)
    length["js_divergence_fixed_bins"] = js_divergence(
        pre_hist["counts"], post_hist["counts"]
    )
    iat = _sample_distances(_iats_log1p_us(pre), _iats_log1p_us(post), low_power)
    iat["domain"] = "log1p_us"

    pre_curve = cumulative_shape(
        pre, axis="normalized_time", grid_points=grid_points
    ).absolute_transport_bytes
    post_curve = cumulative_shape(
        post, axis="normalized_time", grid_points=grid_points
    ).absolute_transport_bytes
    return {
        "scalar": scalar,
        "length_distribution_distance": length,
        "iat_distribution_distance": iat,
        "cumulative_distance": {
            "absolute_bytes": _curve_distances(pre_curve, post_curve),
            "normalized_absolute_bytes": _curve_distances(
                _normalize_curve(pre_curve), _normalize_curve(post_curve)
            ),
        },
        "inner_aggregate_flow_reversal": asdict(reversal_features(pre)),
        "carrier_datagram_reversal": asdict(reversal_features(post)),
        "flow_reversal_preservation": {
            "applicable": False,
            "reason": "shared_carrier_different_semantics",
        },
    }


def extract_hysteria2_window_features(
    window: Hysteria2CarrierWindow,
    config: FeatureConfig,
    analysis_loader: Callable[["EntityDescriptor"], "EntityAnalysis"] | None = None,
) -> dict[str, Any]:
    # Local import prevents the packet-analysis layer and feature package from
    # forming an import cycle while keeping this orchestration function public.
    from ..pipeline.analyze_entity import analyze_entity_capture

    loader = analysis_loader or analyze_entity_capture
    pre_analyses = [loader(item) for item in window.pre_connections]
    post_analysis = loader(window.post_carrier)
    pre = ordered_packets(
        tuple(measure for analysis in pre_analyses for measure in analysis.packet_measures)
    )
    post_full = ordered_packets(post_analysis.packet_measures)
    if pre:
        envelope_start = pre[0].timestamp_ns
        envelope_end = pre[-1].timestamp_ns
        post_envelope = select_time_envelope(post_full, envelope_start, envelope_end)
    else:
        envelope_start = envelope_end = None
        post_envelope = []
    full_payload = sum(item.transport_payload_len for item in post_full)
    envelope_payload = sum(item.transport_payload_len for item in post_envelope)
    return {
        "feature_schema_version": config.schema_version,
        "feature_config_sha256": config.sha256,
        "session_id": window.session_id,
        "protocol_dataset": "HYSTERIA2",
        "carrier_id": window.carrier_id,
        "logical_connection_count": len(window.pre_connections),
        "logical_connection_ids": [item.entity_id for item in window.pre_connections],
        "inner_packet_count": len(pre),
        "carrier_full_packet_count": len(post_full),
        "inner_union_envelope": {
            "start_ns": envelope_start,
            "end_ns": envelope_end,
            "carrier_packet_count": len(post_envelope),
            "carrier_packet_fraction": len(post_envelope) / len(post_full) if post_full else None,
            "carrier_payload_fraction": envelope_payload / full_payload if full_payload else None,
            "comparison": _window_comparison(pre, post_envelope, config),
        },
        "carrier_full_lifetime": {
            "start_ns": post_full[0].timestamp_ns if post_full else None,
            "end_ns": post_full[-1].timestamp_ns if post_full else None,
            "comparison": _window_comparison(pre, post_full, config),
        },
    }
