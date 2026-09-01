from __future__ import annotations

import math

from proxy_analysis.features import (
    PacketMeasure,
    cumulative_shape,
    direction_run_bursts,
    directional_volume,
    distribution_summary,
    fixed_histogram,
    reversal_features,
    time_gap_bursts,
    transition_features,
    active_idle_periods,
)


def p(event: str, ts: int, ordinal: int, direction: int, payload: int, *, classification=None):
    return PacketMeasure(event, ts, ordinal, direction, payload, payload + 40, payload + 54, classification)


def test_fr_empty_single_direction_and_alternating() -> None:
    assert reversal_features([]).fr_runs == 0
    single = reversal_features([p("a", 1, 1, 1, 10)])
    assert (single.fr_runs, single.fr_reversals, single.fr_norm_packets) == (1, 0, None)
    alternating = reversal_features(
        [p("a", 1, 1, 1, 10), p("b", 2, 2, -1, 20), p("c", 3, 3, 1, 30)]
    )
    assert alternating.fr_runs == 3
    assert alternating.fr_reversals == 2
    assert alternating.fr_norm_packets == 1.0


def test_unique_seq_fr_drops_full_retransmission() -> None:
    packets = [
        p("a", 1, 1, 1, 10),
        p("retry", 2, 2, -1, 10, classification="full_retransmission"),
        p("b", 3, 3, 1, 10),
    ]
    assert reversal_features(packets).fr_reversals == 2
    assert reversal_features(packets, unique_seq=True).fr_reversals == 0


def test_transition_counts_probabilities_and_entropy() -> None:
    same = transition_features([1, 1, 1])
    assert same.n_pp == 2
    assert same.p_pp == 1.0
    assert same.direction_entropy_bits == 0.0
    assert same.transition_entropy_bits == 0.0
    alternating = transition_features([1, -1, 1, -1])
    assert alternating.n_pm == 2
    assert alternating.n_mp == 1
    assert alternating.transition_entropy_bits == 0.0


def test_bursts_reconstruct_direction_and_apply_inclusive_gap_threshold() -> None:
    packets = [p("a", 0, 1, 1, 10), p("b", 10, 2, 1, 20), p("c", 11, 3, -1, 5)]
    runs = direction_run_bursts(packets)
    assert [(item.direction, item.packet_count, item.transport_payload_bytes) for item in runs] == [
        (1, 2, 30),
        (-1, 1, 5),
    ]
    assert len(time_gap_bursts(packets, threshold_ns=10)) == 2
    assert len(time_gap_bursts(packets, threshold_ns=9)) == 3


def test_distribution_and_fixed_histogram() -> None:
    summary = distribution_summary([0, 10, 20])
    assert summary["count"] == 3
    assert summary["mean"] == 10.0
    assert summary["std_population"] == math.sqrt(200 / 3)
    empty = distribution_summary([])
    assert empty["count"] is None
    histogram = fixed_histogram([-1, 0, 5, 10, 11], [0, 5, 10])
    assert histogram["counts"] == [1, 2]
    assert histogram["underflow"] == 1
    assert histogram["overflow"] == 1


def test_directional_volume_invariants() -> None:
    packets = [p("a", 1, 1, 1, 10), p("b", 2, 2, -1, 20)]
    volume = directional_volume(packets)
    assert volume["up_packets"] + volume["down_packets"] == volume["total_packets"]
    assert volume["total_transport_bytes"] == 30
    assert volume["transport_bytes_normalized_difference"] == -1 / 3


def test_cumulative_shape_endpoint_and_monotonic_absolute_curve() -> None:
    packets = [p("a", 0, 1, 1, 10), p("b", 10, 2, -1, 20)]
    shape = cumulative_shape(packets, axis="normalized_packet_index", grid_points=3)
    assert shape.absolute_transport_bytes == (0.0, 10.0, 30.0)
    assert shape.signed_transport_bytes[-1] == -10.0
    assert all(a <= b for a, b in zip(shape.absolute_transport_bytes, shape.absolute_transport_bytes[1:]))


def test_active_idle_uses_strictly_greater_gap_as_boundary() -> None:
    packets = [p("a", 0, 1, 1, 1), p("b", 10, 2, 1, 1), p("c", 21, 3, 1, 1)]
    periods = active_idle_periods(packets, threshold_ns=10)
    assert periods.active_durations_ns == (10, 0)
    assert periods.idle_durations_ns == (11,)
