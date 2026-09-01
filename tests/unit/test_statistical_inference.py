import numpy as np
import pytest

from proxy_analysis.statistical.inference import (
    benjamini_hochberg,
    blocked_sign_flip_pvalue,
    friedman_result,
    one_sample_result,
    paired_rank_biserial,
)


def test_paired_rank_biserial_has_expected_extremes() -> None:
    assert paired_rank_biserial(np.asarray([1.0, 2.0, 3.0])) == pytest.approx(1.0)
    assert paired_rank_biserial(np.asarray([-1.0, -2.0])) == pytest.approx(-1.0)
    assert paired_rank_biserial(np.asarray([0.0, 0.0])) == pytest.approx(0.0)


def test_clustered_one_sample_result_is_deterministic() -> None:
    kwargs = {
        "seed": 7,
        "bootstrap_repetitions": 100,
        "permutation_repetitions": 100,
        "confidence_level": 0.95,
    }
    left = one_sample_result([1, 2, 3, 4], ["a", "a", "b", "b"], **kwargs)
    right = one_sample_result([1, 2, 3, 4], ["a", "a", "b", "b"], **kwargs)
    assert left == right
    assert left["paired_rank_biserial"] == pytest.approx(1.0)


def test_blocked_sign_flip_and_friedman() -> None:
    value = blocked_sign_flip_pvalue(
        np.asarray([1.0, 1.0, 2.0]),
        ["a", "a", "b"],
        seed=1,
        repetitions=100,
    )
    assert value is not None and 0 < value <= 1
    result = friedman_result(
        [np.asarray([1.0, 2.0]), np.asarray([2.0, 3.0]), np.asarray([3.0, 4.0])]
    )
    assert result["n"] == 2
    assert result["kendalls_w"] == pytest.approx(1.0)


def test_bh_is_monotone_in_rank_order() -> None:
    adjusted = benjamini_hochberg([0.01, 0.04, 0.03])
    assert adjusted == pytest.approx([0.03, 0.04, 0.04])
