"""Deterministic, leakage-aware baselines for Track B protocol classification."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow.parquet as pq
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


MODEL_METADATA = {
    "session_id",
    "protocol_dataset",
    "group_site",
    "split_by_site",
    "split_by_session",
    "feature_set",
    # These are index-derived entity annotations and would directly reveal H2.
    "post_outer_connection_count",
    "post_carrier_count",
}


def _metrics(y_true: np.ndarray, y_pred: np.ndarray, labels: list[str]) -> dict[str, Any]:
    return {
        "row_count": int(y_true.size),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(
            f1_score(y_true, y_pred, average="macro", labels=labels, zero_division=0)
        ),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    }


def _cluster_bootstrap_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    groups: np.ndarray,
    labels: list[str],
    *,
    seed: int,
    repetitions: int = 2000,
) -> dict[str, list[float]]:
    unique = np.unique(groups)
    rng = np.random.default_rng(seed)
    sampled_metrics = {"accuracy": [], "balanced_accuracy": [], "macro_f1": []}
    group_indices = {group: np.flatnonzero(groups == group) for group in unique}
    for _ in range(repetitions):
        sampled_groups = rng.choice(unique, size=unique.size, replace=True)
        indices = np.concatenate([group_indices[group] for group in sampled_groups])
        sampled_metrics["accuracy"].append(accuracy_score(y_true[indices], y_pred[indices]))
        matrix = confusion_matrix(y_true[indices], y_pred[indices], labels=labels)
        denominators = matrix.sum(axis=1)
        recalls = np.divide(
            np.diag(matrix),
            denominators,
            out=np.zeros(len(labels), dtype=np.float64),
            where=denominators != 0,
        )
        sampled_metrics["balanced_accuracy"].append(float(recalls.mean()))
        sampled_metrics["macro_f1"].append(
            f1_score(
                y_true[indices],
                y_pred[indices],
                average="macro",
                labels=labels,
                zero_division=0,
            )
        )
    return {
        name: [float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))]
        for name, values in sampled_metrics.items()
    }


def _validate_group_split(
    rows: list[dict[str, Any]], *, group_column: str, split_column: str
) -> dict[str, Any]:
    groups: dict[str, set[str]] = {}
    for row in rows:
        groups.setdefault(str(row[group_column]), set()).add(str(row[split_column]))
    crossing = {group: sorted(values) for group, values in groups.items() if len(values) > 1}
    class_by_split = {
        split: sorted(
            {row["protocol_dataset"] for row in rows if row[split_column] == split}
        )
        for split in ("train", "validation", "test")
    }
    if crossing:
        raise ValueError(f"{group_column} leakage detected for {len(crossing)} groups")
    if any(len(classes) < 3 for classes in class_by_split.values()):
        raise ValueError(f"not all protocol classes occur in every split: {class_by_split}")
    return {
        "group_column": group_column,
        "split_column": split_column,
        "group_count": len(groups),
        "cross_split_group_count": 0,
        "classes_by_split": class_by_split,
    }


def run_protocol_baselines(
    dataset_path: Path | str,
    output: Path | str,
    *,
    seed: int = 20260901,
    split_column: str = "split_by_site",
) -> dict[str, Any]:
    rows = pq.read_table(dataset_path).to_pylist()
    group_column = "group_site" if split_column == "split_by_site" else "session_id"
    validation = _validate_group_split(
        rows, group_column=group_column, split_column=split_column
    )
    labels = sorted({str(row["protocol_dataset"]) for row in rows})
    candidates = sorted(set().union(*(row.keys() for row in rows)) - MODEL_METADATA)
    # Fit-time selection must never inspect validation/test missingness.
    train_rows = [row for row in rows if row[split_column] == "train"]
    feature_names = [
        name
        for name in candidates
        if any(row.get(name) is not None for row in train_rows)
        and len({row.get(name) for row in train_rows if row.get(name) is not None}) > 1
    ]

    def matrix(selected_rows: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
        x = np.asarray(
            [
                [float(row[name]) if row.get(name) is not None else np.nan for name in feature_names]
                for row in selected_rows
            ],
            dtype=np.float64,
        )
        y = np.asarray([row["protocol_dataset"] for row in selected_rows])
        return x, y

    subsets = {
        split: [row for row in rows if row[split_column] == split]
        for split in ("train", "validation", "test")
    }
    x_train, y_train = matrix(subsets["train"])
    k = min(64, len(feature_names))
    models = {
        "multinomial_logistic": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
                ("select", SelectKBest(f_classif, k=k)),
                (
                    "model",
                    LogisticRegression(
                        max_iter=5000,
                        class_weight="balanced",
                        random_state=seed,
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("select", SelectKBest(f_classif, k=k)),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=500,
                        min_samples_leaf=2,
                        class_weight="balanced",
                        random_state=seed,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }
    results: dict[str, Any] = {}
    predictions = []
    for model_index, (model_name, model) in enumerate(models.items()):
        model.fit(x_train, y_train)
        model_result: dict[str, Any] = {}
        selector = model.named_steps["select"]
        selected_names = [
            name for name, keep in zip(feature_names, selector.get_support()) if keep
        ]
        scores = selector.scores_
        ranked = sorted(
            (
                {"feature": name, "f_score_train_only": float(score)}
                for name, score in zip(feature_names, scores)
                if np.isfinite(score)
            ),
            key=lambda item: item["f_score_train_only"],
            reverse=True,
        )
        model_result["selected_feature_count"] = len(selected_names)
        model_result["top_train_only_features"] = ranked[:20]
        for split, split_rows in subsets.items():
            x, y = matrix(split_rows)
            predicted = model.predict(x)
            model_result[split] = _metrics(y, predicted, labels)
            if split in {"validation", "test"}:
                model_result[split]["cluster_bootstrap_ci95"] = _cluster_bootstrap_ci(
                    y,
                    predicted,
                    np.asarray([row[group_column] for row in split_rows]),
                    labels,
                    seed=seed + model_index * 10 + (1 if split == "validation" else 2),
                )
            for row, truth, prediction in zip(split_rows, y, predicted):
                predictions.append(
                    {
                        "model": model_name,
                        "split": split,
                        "session_id": row["session_id"],
                        "group_site": row["group_site"],
                        "truth": str(truth),
                        "prediction": str(prediction),
                    }
                )
        results[model_name] = model_result
    report = {
        "dataset": str(dataset_path),
        "seed": seed,
        "split_column": split_column,
        "labels": labels,
        "input_feature_count_after_train_filter": len(feature_names),
        "split_validation": validation,
        "models": results,
        "predictions": predictions,
    }
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, destination)
    return report


def run_all_protocol_baselines(
    dataset_root: Path | str, output_root: Path | str, *, seed: int = 20260901
) -> dict[str, Any]:
    root = Path(dataset_root)
    destination = Path(output_root)
    summary = {}
    for feature_set in ("a_core", "a_plus_b"):
        summary[feature_set] = {}
        for split_name, split_column in (
            ("site_primary", "split_by_site"),
            ("session_sensitivity", "split_by_session"),
        ):
            report = run_protocol_baselines(
                root / f"protocol-classification-{feature_set}.parquet",
                destination / f"protocol-baseline-{feature_set}-{split_name}.json",
                seed=seed,
                split_column=split_column,
            )
            summary[feature_set][split_name] = {
                model: {
                    split: values[split]["macro_f1"]
                    for split in ("validation", "test")
                }
                for model, values in report["models"].items()
            }
    return summary
