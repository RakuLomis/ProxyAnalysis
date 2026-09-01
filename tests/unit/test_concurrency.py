import pytest

from proxy_analysis.features.concurrency import Interval, concurrency_features


def test_half_open_intervals_do_not_overlap_at_touching_boundary() -> None:
    result = concurrency_features([Interval("a", 0, 10), Interval("b", 10, 20)])
    assert result.max_active == 1
    assert result.time_weighted_mean_active == 1.0


def test_concurrency_peak_and_time_weighted_mean() -> None:
    result = concurrency_features([Interval("a", 0, 10), Interval("b", 5, 15)])
    assert result.max_active == 2
    assert result.time_weighted_mean_active == pytest.approx(20 / 15)


def test_zero_duration_interval_does_not_inflate_peak() -> None:
    result = concurrency_features([Interval("point", 5, 5)])
    assert result.zero_duration_count == 1
    assert result.max_active == 0
    assert result.time_weighted_mean_active is None

