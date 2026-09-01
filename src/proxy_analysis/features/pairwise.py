"""Pre/post transformation features for eligible exclusive pairs."""

from __future__ import annotations

import math
from typing import Any, Iterable, TYPE_CHECKING

import numpy as np
from scipy.stats import ks_2samp, wasserstein_distance

from ..config import FeatureConfig
if TYPE_CHECKING:
    from ..pipeline.analyze_entity import EntityAnalysis
from .burst import direction_run_bursts
from .cumulative import cumulative_shape
from .distribution import fixed_histogram
from .models import PacketMeasure, ordered_packets
from .reversal import reversal_features
from .transition import transition_features


def log_ratio(post: float, pre: float, epsilon: float) -> float:
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    return math.log((post + epsilon) / (pre + epsilon))


def normalized_difference(post: float, pre: float) -> float | None:
    return (post - pre) / (post + pre) if post + pre else None


def js_divergence(counts_a: Iterable[int], counts_b: Iterable[int]) -> float | None:
    a = np.asarray(list(counts_a), dtype=np.float64)
    b = np.asarray(list(counts_b), dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError("JS inputs must have the same shape")
    if a.sum() == 0 or b.sum() == 0:
        return None
    p = a / a.sum()
    q = b / b.sum()
    midpoint = (p + q) / 2

    def kl(left: np.ndarray, right: np.ndarray) -> float:
        mask = left > 0
        return float(np.sum(left[mask] * np.log2(left[mask] / right[mask])))

    return 0.5 * kl(p, midpoint) + 0.5 * kl(q, midpoint)


def _iats_us(packets: list[PacketMeasure]) -> list[float]:
    return [
        (current.timestamp_ns - previous.timestamp_ns) / 1000
        for previous, current in zip(packets, packets[1:])
    ]


def _sample_distances(
    pre: list[float], post: list[float], low_power_min_samples: int
) -> dict[str, float | int | bool | None]:
    if not pre or not post:
        return {
            "pre_count": len(pre),
            "post_count": len(post),
            "wasserstein": None,
            "ks_statistic": None,
            "ks_pvalue": None,
            "low_power": True,
        }
    ks = ks_2samp(pre, post, method="auto")
    return {
        "pre_count": len(pre),
        "post_count": len(post),
        "wasserstein": float(wasserstein_distance(pre, post)),
        "ks_statistic": float(ks.statistic),
        "ks_pvalue": float(ks.pvalue),
        "low_power": min(len(pre), len(post)) < low_power_min_samples,
    }


def _curve_distances(pre: Iterable[float], post: Iterable[float]) -> dict[str, float]:
    a = np.asarray(list(pre), dtype=np.float64)
    b = np.asarray(list(post), dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError("cumulative curves must have the same shape")
    difference = np.abs(b - a)
    return {
        "l1_mean": float(difference.mean()),
        "l2_rms": float(np.sqrt(np.mean((b - a) ** 2))),
        "max_abs": float(difference.max()),
    }


def _normalize_curve(values: Iterable[float]) -> list[float]:
    array = np.asarray(list(values), dtype=np.float64)
    denominator = array[-1] if array.size else 0
    return (array / denominator).tolist() if denominator > 0 else array.tolist()


def _transition_vector(packets: list[PacketMeasure]) -> list[float] | None:
    nonempty = [item.direction for item in packets if item.transport_payload_len > 0]
    transition = transition_features(nonempty)
    counts = np.asarray(
        [transition.n_pp, transition.n_pm, transition.n_mp, transition.n_mm],
        dtype=np.float64,
    )
    return (counts / counts.sum()).tolist() if counts.sum() else None


def extract_pairwise_features(
    pre_analysis: EntityAnalysis,
    post_analysis: EntityAnalysis,
    config: FeatureConfig,
) -> dict[str, Any]:
    if pre_analysis.descriptor.session_id != post_analysis.descriptor.session_id:
        raise ValueError("pre/post session mismatch")
    if post_analysis.descriptor.shared or post_analysis.descriptor.entity_level == "carrier":
        raise ValueError("shared carrier cannot be used as an exclusive pair")

    pre = ordered_packets(pre_analysis.packet_measures)
    post = ordered_packets(post_analysis.packet_measures)
    epsilon = float(config.values["ratios"]["epsilon"])
    low_power = int(config.values["pairing"]["low_power_min_samples"])
    hist_edges = config.values["histograms"]["transport_payload_len_edges_bytes"]
    grid_points = int(config.values["cumulative_shape"]["grid_points"])

    pre_duration = pre[-1].timestamp_ns - pre[0].timestamp_ns if pre else 0
    post_duration = post[-1].timestamp_ns - post[0].timestamp_ns if post else 0
    scalar_values = {
        "packet_count": (len(pre), len(post)),
        "transport_payload_bytes": (
            sum(item.transport_payload_len for item in pre),
            sum(item.transport_payload_len for item in post),
        ),
        "ip_bytes": (
            sum(item.ip_total_len for item in pre),
            sum(item.ip_total_len for item in post),
        ),
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
        for name, (before, after) in scalar_values.items()
    }

    pre_nonempty_lengths = [
        float(item.transport_payload_len) for item in pre if item.transport_payload_len > 0
    ]
    post_nonempty_lengths = [
        float(item.transport_payload_len) for item in post if item.transport_payload_len > 0
    ]
    pre_hist = fixed_histogram(pre_nonempty_lengths, hist_edges)
    post_hist = fixed_histogram(post_nonempty_lengths, hist_edges)
    length_distance = _sample_distances(pre_nonempty_lengths, post_nonempty_lengths, low_power)
    length_distance["js_divergence_fixed_bins"] = js_divergence(
        pre_hist["counts"], post_hist["counts"]
    )

    pre_iat = [math.log1p(value) for value in _iats_us(pre)]
    post_iat = [math.log1p(value) for value in _iats_us(post)]
    iat_distance = _sample_distances(pre_iat, post_iat, low_power)
    iat_distance["domain"] = "log1p_us"

    pre_curve = cumulative_shape(
        pre, axis="normalized_time", grid_points=grid_points
    ).absolute_transport_bytes
    post_curve = cumulative_shape(
        post, axis="normalized_time", grid_points=grid_points
    ).absolute_transport_bytes
    cumulative_distance = {
        "absolute_bytes": _curve_distances(pre_curve, post_curve),
        "normalized_absolute_bytes": _curve_distances(
            _normalize_curve(pre_curve), _normalize_curve(post_curve)
        ),
    }

    pre_transition = _transition_vector(pre)
    post_transition = _transition_vector(post)
    if pre_transition is None or post_transition is None:
        transition_distance = {"l1": None, "frobenius": None}
    else:
        difference = np.asarray(post_transition) - np.asarray(pre_transition)
        transition_distance = {
            "l1": float(np.abs(difference).sum()),
            "frobenius": float(np.sqrt(np.square(difference).sum())),
        }

    both_tcp = (
        pre_analysis.descriptor.transport_protocol == "tcp"
        and post_analysis.descriptor.transport_protocol == "tcp"
    )
    if both_tcp:
        pre_fr = reversal_features(pre)
        post_fr = reversal_features(post)
        reversal_preservation: dict[str, Any] = {
            "applicable": True,
            "pre_reversals": pre_fr.fr_reversals,
            "post_reversals": post_fr.fr_reversals,
            "log_ratio": log_ratio(post_fr.fr_reversals, pre_fr.fr_reversals, epsilon),
            "normalized_difference": normalized_difference(
                post_fr.fr_reversals, pre_fr.fr_reversals
            ),
        }
    else:
        reversal_preservation = {
            "applicable": False,
            "reason": "not_applicable_transport",
        }

    return {
        "feature_schema_version": config.schema_version,
        "feature_config_sha256": config.sha256,
        "session_id": pre_analysis.descriptor.session_id,
        "connection_id": pre_analysis.descriptor.entity_id,
        "protocol_dataset": pre_analysis.descriptor.protocol_dataset,
        "pre_entity_id": pre_analysis.descriptor.entity_id,
        "post_entity_id": post_analysis.descriptor.entity_id,
        "pre_transport": pre_analysis.descriptor.transport_protocol,
        "post_transport": post_analysis.descriptor.transport_protocol,
        "scalar": scalar,
        "length_distribution_distance": length_distance,
        "iat_distribution_distance": iat_distance,
        "cumulative_distance": cumulative_distance,
        "transition_distance": transition_distance,
        "flow_reversal_preservation": reversal_preservation,
    }
