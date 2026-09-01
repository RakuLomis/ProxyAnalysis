import math

import pytest

from proxy_analysis.features.pairwise import (
    _curve_distances,
    js_divergence,
    log_ratio,
    normalized_difference,
)


def test_js_divergence_identity_symmetry_and_disjoint_maximum() -> None:
    assert js_divergence([1, 2], [1, 2]) == pytest.approx(0.0)
    assert js_divergence([1, 0], [0, 1]) == pytest.approx(1.0)
    assert js_divergence([2, 1], [1, 3]) == pytest.approx(
        js_divergence([1, 3], [2, 1])
    )


def test_ratio_contract() -> None:
    assert log_ratio(10, 10, 1) == 0.0
    assert log_ratio(20, 10, 1) == math.log(21 / 11)
    assert normalized_difference(20, 10) == pytest.approx(1 / 3)
    assert normalized_difference(0, 0) is None


def test_curve_distances() -> None:
    result = _curve_distances([0, 1, 2], [0, 2, 4])
    assert result["l1_mean"] == 1.0
    assert result["max_abs"] == 2.0

