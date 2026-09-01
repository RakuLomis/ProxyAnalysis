"""Paired, clustered non-parametric statistics used by the frozen analysis."""

from __future__ import annotations

import math
from typing import Any, Iterable

import numpy as np
from scipy.stats import friedmanchisquare, rankdata, wilcoxon


def benjamini_hochberg(pvalues: Iterable[float]) -> list[float]:
    values = np.asarray(list(pvalues), dtype=np.float64)
    if not values.size:
        return []
    order = np.argsort(values)
    adjusted = np.empty_like(values)
    running = 1.0
    for reverse_rank in range(values.size - 1, -1, -1):
        index = order[reverse_rank]
        rank = reverse_rank + 1
        running = min(running, float(values[index]) * values.size / rank)
        adjusted[index] = min(running, 1.0)
    return adjusted.tolist()


def finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def descriptive(values: Iterable[float]) -> dict[str, float | int | None]:
    array = np.asarray(list(values), dtype=np.float64)
    if not array.size:
        return {
            "n": 0,
            "mean": None,
            "sd": None,
            "median": None,
            "q25": None,
            "q75": None,
            "mad": None,
            "min": None,
            "max": None,
            "zero_proportion": None,
        }
    median = float(np.median(array))
    return {
        "n": int(array.size),
        "mean": float(array.mean()),
        "sd": float(array.std(ddof=1)) if array.size > 1 else 0.0,
        "median": median,
        "q25": float(np.quantile(array, 0.25)),
        "q75": float(np.quantile(array, 0.75)),
        "mad": float(np.median(np.abs(array - median))),
        "min": float(array.min()),
        "max": float(array.max()),
        "zero_proportion": float(np.mean(array == 0)),
    }


def hodges_lehmann_one_sample(values: np.ndarray) -> float | None:
    if not values.size:
        return None
    walsh = (values[:, None] + values[None, :]) / 2
    return float(np.median(walsh[np.triu_indices(values.size)]))


def paired_rank_biserial(differences: np.ndarray) -> float | None:
    nonzero = differences[differences != 0]
    if not nonzero.size:
        return 0.0 if differences.size else None
    ranks = rankdata(np.abs(nonzero), method="average")
    denominator = float(ranks.sum())
    return float((ranks[nonzero > 0].sum() - ranks[nonzero < 0].sum()) / denominator)


def cluster_bootstrap_median_ci(
    values: np.ndarray,
    clusters: list[str],
    *,
    seed: int,
    repetitions: int,
    confidence_level: float,
) -> tuple[float | None, float | None]:
    if not values.size:
        return None, None
    unique = sorted(set(clusters))
    by_cluster = {
        cluster: values[np.asarray([item == cluster for item in clusters])]
        for cluster in unique
    }
    rng = np.random.default_rng(seed)
    estimates = np.empty(repetitions, dtype=np.float64)
    for index in range(repetitions):
        sampled = rng.choice(unique, size=len(unique), replace=True)
        estimates[index] = np.median(
            np.concatenate([by_cluster[str(cluster)] for cluster in sampled])
        )
    alpha = 1 - confidence_level
    return (
        float(np.quantile(estimates, alpha / 2)),
        float(np.quantile(estimates, 1 - alpha / 2)),
    )


def blocked_sign_flip_pvalue(
    differences: np.ndarray,
    clusters: list[str],
    *,
    seed: int,
    repetitions: int,
) -> float | None:
    if not differences.size:
        return None
    unique = sorted(set(clusters))
    cluster_index = {cluster: index for index, cluster in enumerate(unique)}
    indexes = np.asarray([cluster_index[item] for item in clusters], dtype=np.int64)
    observed = abs(float(differences.mean()))
    rng = np.random.default_rng(seed)
    extreme = 0
    for _ in range(repetitions):
        signs = rng.choice((-1.0, 1.0), size=len(unique))
        statistic = abs(float(np.mean(differences * signs[indexes])))
        extreme += statistic >= observed - 1e-15
    return float((extreme + 1) / (repetitions + 1))


def one_sample_result(
    values: Iterable[float],
    clusters: Iterable[str],
    *,
    seed: int,
    bootstrap_repetitions: int,
    permutation_repetitions: int,
    confidence_level: float,
) -> dict[str, Any]:
    pairs = [
        (float(value), str(cluster))
        for value, cluster in zip(values, clusters)
        if finite(value)
    ]
    array = np.asarray([value for value, _ in pairs], dtype=np.float64)
    cluster_values = [cluster for _, cluster in pairs]
    base = descriptive(array)
    if not array.size:
        return {
            **base,
            "nonzero_n": 0,
            "test": None,
            "pvalue_raw": None,
            "blocked_permutation_pvalue": None,
            "hodges_lehmann_shift": None,
            "paired_rank_biserial": None,
            "cluster_bootstrap_median_ci95": [None, None],
        }
    nonzero_n = int(np.count_nonzero(array))
    if nonzero_n:
        test = wilcoxon(array, alternative="two-sided", zero_method="wilcox", method="auto")
        test_name = "wilcoxon_signed_rank"
        statistic = float(test.statistic)
        pvalue = float(test.pvalue)
    else:
        test_name = "all_zero_no_test"
        statistic = 0.0
        pvalue = 1.0
    low, high = cluster_bootstrap_median_ci(
        array,
        cluster_values,
        seed=seed,
        repetitions=bootstrap_repetitions,
        confidence_level=confidence_level,
    )
    return {
        **base,
        "nonzero_n": nonzero_n,
        "test": test_name,
        "statistic": statistic,
        "pvalue_raw": pvalue,
        "blocked_permutation_pvalue": blocked_sign_flip_pvalue(
            array,
            cluster_values,
            seed=seed + 1,
            repetitions=permutation_repetitions,
        ),
        "hodges_lehmann_shift": hodges_lehmann_one_sample(array),
        "paired_rank_biserial": paired_rank_biserial(array),
        "cluster_bootstrap_median_ci95": [low, high],
    }


def friedman_result(groups: list[np.ndarray]) -> dict[str, float | int | None]:
    if len(groups) < 3 or not groups[0].size:
        return {"n": 0, "statistic": None, "pvalue_raw": None, "kendalls_w": None}
    test = friedmanchisquare(*groups)
    n = int(groups[0].size)
    k = len(groups)
    return {
        "n": n,
        "statistic": float(test.statistic),
        "pvalue_raw": float(test.pvalue),
        "kendalls_w": float(test.statistic / (n * (k - 1))),
    }
