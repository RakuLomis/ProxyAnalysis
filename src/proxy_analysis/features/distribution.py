"""Frozen descriptive summaries and fixed-bin histograms."""

from __future__ import annotations

from typing import Iterable

import numpy as np


QUANTILES = (0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99)


def distribution_summary(values: Iterable[int | float]) -> dict[str, float | int | None]:
    array = np.asarray(list(values), dtype=np.float64)
    names = ("p01", "p05", "p10", "p25", "p50", "p75", "p90", "p95", "p99")
    if array.size == 0:
        return {
            key: None
            for key in (
                "count",
                "min",
                "max",
                "sum",
                "mean",
                "std_population",
                *names,
                "zero_fraction",
                "cv",
            )
        }
    mean = float(array.mean())
    quantiles = np.quantile(array, QUANTILES, method="linear")
    result: dict[str, float | int | None] = {
        "count": int(array.size),
        "min": float(array.min()),
        "max": float(array.max()),
        "sum": float(array.sum()),
        "mean": mean,
        "std_population": float(array.std(ddof=0)),
        "zero_fraction": float(np.count_nonzero(array == 0) / array.size),
        "cv": float(array.std(ddof=0) / mean) if mean != 0 else None,
    }
    result.update({name: float(value) for name, value in zip(names, quantiles)})
    return result


def fixed_histogram(values: Iterable[int | float], edges: Iterable[int | float]) -> dict[str, object]:
    array = np.asarray(list(values), dtype=np.float64)
    bins = np.asarray(list(edges), dtype=np.float64)
    if bins.size < 2 or np.any(np.diff(bins) <= 0):
        raise ValueError("histogram edges must be strictly increasing")
    counts, _ = np.histogram(array, bins=bins)
    return {
        "edges": bins.tolist(),
        "counts": counts.astype(np.int64).tolist(),
        "underflow": int(np.count_nonzero(array < bins[0])),
        "overflow": int(np.count_nonzero(array > bins[-1])),
    }

