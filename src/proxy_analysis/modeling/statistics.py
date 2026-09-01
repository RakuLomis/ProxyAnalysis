"""Session-weighted inferential summaries for Track A transformation metrics."""

from __future__ import annotations

from itertools import combinations
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pyarrow.parquet as pq
from scipy.stats import kruskal, mannwhitneyu

from .datasets import TRANSFORMATION_METRICS


TRACK_A_METRICS = (
    *TRANSFORMATION_METRICS,
    "flow_reversal__log_ratio",
    "flow_reversal__normalized_difference",
)


def cliffs_delta(left: Iterable[float], right: Iterable[float]) -> float | None:
    a = np.asarray(list(left), dtype=np.float64)
    b = np.asarray(list(right), dtype=np.float64)
    if not a.size or not b.size:
        return None
    differences = a[:, None] - b[None, :]
    return float((np.count_nonzero(differences > 0) - np.count_nonzero(differences < 0)) / differences.size)


def benjamini_hochberg(pvalues: Iterable[float]) -> list[float]:
    values = np.asarray(list(pvalues), dtype=np.float64)
    if not values.size:
        return []
    order = np.argsort(values)
    adjusted = np.empty_like(values)
    running = 1.0
    total = values.size
    for reverse_rank in range(total - 1, -1, -1):
        index = order[reverse_rank]
        rank = reverse_rank + 1
        running = min(running, float(values[index]) * total / rank)
        adjusted[index] = min(running, 1.0)
    return adjusted.tolist()


def _bootstrap_ci(
    values: np.ndarray, *, rng: np.random.Generator, repetitions: int
) -> tuple[float | None, float | None]:
    if not values.size:
        return None, None
    samples = rng.choice(values, size=(repetitions, values.size), replace=True)
    medians = np.median(samples, axis=1)
    return float(np.quantile(medians, 0.025)), float(np.quantile(medians, 0.975))


def _session_values(rows: list[dict[str, Any]], metric: str) -> dict[str, np.ndarray]:
    nested: dict[str, dict[str, list[float]]] = {}
    for row in rows:
        value = row.get(metric)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
            nested.setdefault(row["protocol_dataset"], {}).setdefault(
                row["session_id"], []
            ).append(float(value))
    return {
        protocol: np.asarray(
            [np.mean(values) for values in sessions.values()], dtype=np.float64
        )
        for protocol, sessions in nested.items()
    }


def analyze_transformation_track(
    dataset_path: Path | str,
    output: Path | str,
    *,
    seed: int = 20260901,
    bootstrap_repetitions: int = 2000,
) -> dict[str, Any]:
    rows = pq.read_table(dataset_path).to_pylist()
    rng = np.random.default_rng(seed)
    metric_reports: dict[str, Any] = {}
    omnibus_refs: list[dict[str, Any]] = []
    pairwise_refs: list[dict[str, Any]] = []
    for metric in TRACK_A_METRICS:
        groups = _session_values(rows, metric)
        descriptive: dict[str, Any] = {}
        for protocol, values in sorted(groups.items()):
            low, high = _bootstrap_ci(values, rng=rng, repetitions=bootstrap_repetitions)
            descriptive[protocol] = {
                "session_count": int(values.size),
                "mean": float(values.mean()),
                "median": float(np.median(values)),
                "q25": float(np.quantile(values, 0.25)),
                "q75": float(np.quantile(values, 0.75)),
                "bootstrap_median_ci95": [low, high],
            }
        usable = {key: value for key, value in groups.items() if value.size >= 2}
        omnibus = None
        if len(usable) >= 2:
            test = kruskal(*usable.values())
            omnibus = {
                "protocols": sorted(usable),
                "statistic": float(test.statistic),
                "pvalue_raw": float(test.pvalue),
            }
            omnibus_refs.append(omnibus)
        pairwise = []
        for left, right in combinations(sorted(usable), 2):
            test = mannwhitneyu(usable[left], usable[right], alternative="two-sided")
            result = {
                "left": left,
                "right": right,
                "pvalue_raw": float(test.pvalue),
                "cliffs_delta_left_minus_right": cliffs_delta(usable[left], usable[right]),
            }
            pairwise.append(result)
            pairwise_refs.append(result)
        metric_reports[metric] = {
            "descriptive_session_weighted": descriptive,
            "omnibus_kruskal_wallis": omnibus,
            "pairwise_mann_whitney": pairwise,
        }
    for item, adjusted in zip(
        omnibus_refs,
        benjamini_hochberg(item["pvalue_raw"] for item in omnibus_refs),
    ):
        item["qvalue_bh_across_metrics"] = adjusted
    for item, adjusted in zip(
        pairwise_refs,
        benjamini_hochberg(item["pvalue_raw"] for item in pairwise_refs),
    ):
        item["qvalue_bh_across_all_pairwise_tests"] = adjusted
    report = {
        "unit_of_inference": "session",
        "within_session_aggregation": "mean",
        "bootstrap_repetitions": bootstrap_repetitions,
        "seed": seed,
        "fr_note": "Hysteria2 excluded from TCP FR preservation comparisons by design",
        "metrics": metric_reports,
    }
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, destination)
    return report
