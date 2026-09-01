"""Repeated nested site-group CV and train-only feature-family ablations."""

from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pyarrow.parquet as pq
from joblib import parallel_backend
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectPercentile, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold

from .baselines import MODEL_METADATA


EVALUATION_IMPLEMENTATION_VERSION = 1


def feature_family(name: str) -> str | None:
    if name == "post_entity_count" or "volume__" in name:
        return "workload_volume"
    if "histograms__" in name:
        return "packetization_timing"
    if any(token in name for token in ("transition_nonempty__", "direction_run_burst__", "proxy_reversal__")):
        return "interaction"
    if "normalized_cumulative_shape__" in name:
        return "cumulative_shape"
    if any(token in name for token in ("tcp_state__", "tcp_transport__", "active_idle__")):
        return "transport_b"
    return None


ABLATION_RULES: dict[str, Callable[[str], bool]] = {
    "workload_volume": lambda name: feature_family(name) == "workload_volume",
    "packetization_timing": lambda name: feature_family(name) == "packetization_timing",
    "packet_length": lambda name: "histograms__transport_payload_len__" in name
    or "histograms__ip_total_len__" in name,
    "iat_timing": lambda name: "histograms__iat_us__" in name,
    "interaction": lambda name: feature_family(name) == "interaction",
    "reversal_only": lambda name: "proxy_reversal__" in name,
    "transition_burst": lambda name: feature_family(name) == "interaction"
    and "proxy_reversal__" not in name,
    "cumulative_shape": lambda name: feature_family(name) == "cumulative_shape",
    "a_core_all": lambda name: feature_family(name) in {
        "workload_volume", "packetization_timing", "interaction", "cumulative_shape"
    },
    "a_core_minus_reversal": lambda name: feature_family(name) in {
        "workload_volume", "packetization_timing", "interaction", "cumulative_shape"
    }
    and "proxy_reversal__" not in name,
    "a_core_minus_cumulative": lambda name: feature_family(name) in {
        "workload_volume", "packetization_timing", "interaction"
    },
    "a_core_minus_packetization_timing": lambda name: feature_family(name) in {
        "workload_volume", "interaction", "cumulative_shape"
    },
    "a_plus_b_all": lambda name: feature_family(name) is not None,
    "transport_b_only": lambda name: feature_family(name) == "transport_b",
}


def _load_dataset(path: Path | str) -> tuple[list[dict[str, Any]], list[str]]:
    rows = pq.read_table(path).to_pylist()
    columns = sorted(set().union(*(row.keys() for row in rows)) - MODEL_METADATA)
    # Index-derived protocol entity labels remain prohibited even if an older table
    # exposes them as numeric counts.
    prohibited = {"post_outer_connection_count", "post_carrier_count"}
    return rows, [name for name in columns if name not in prohibited]


def _matrix(
    rows: list[dict[str, Any]], feature_names: list[str]
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x = np.asarray(
        [
            [float(row[name]) if row.get(name) is not None else np.nan for name in feature_names]
            for row in rows
        ],
        dtype=np.float64,
    )
    y = np.asarray([row["protocol_dataset"] for row in rows])
    groups = np.asarray([row["group_site"] for row in rows])
    sessions = np.asarray([row["session_id"] for row in rows])
    return x, y, groups, sessions


def _pipeline(model_name: str, seed: int) -> tuple[Pipeline, dict[str, list[Any]]]:
    common = [
        ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("variance", VarianceThreshold()),
        ("select", SelectPercentile(f_classif)),
    ]
    if model_name == "multinomial_logistic":
        pipeline = Pipeline(
            [
                common[0],
                common[1],
                ("scale", StandardScaler()),
                common[2],
                (
                    "model",
                    LogisticRegression(
                        max_iter=5000,
                        class_weight="balanced",
                        random_state=seed,
                    ),
                ),
            ]
        )
        grid = {
            "select__percentile": [25, 50, 100],
            "model__C": [0.1, 1.0, 10.0],
        }
    elif model_name == "random_forest":
        pipeline = Pipeline(
            [
                *common,
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=200,
                        class_weight="balanced",
                        random_state=seed,
                        n_jobs=1,
                    ),
                ),
            ]
        )
        grid = {
            "select__percentile": [25, 50],
            "model__max_depth": [None, 12],
            "model__min_samples_leaf": [1, 3],
            "model__max_features": ["sqrt"],
        }
    else:
        raise ValueError(f"unsupported model: {model_name}")
    return pipeline, grid


def _fold_metrics(y_true: np.ndarray, y_pred: np.ndarray, labels: list[str]) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(
            f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
        ),
    }


def _summarize_folds(folds: list[dict[str, Any]], labels: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {"fold_count": len(folds)}
    for metric in ("accuracy", "balanced_accuracy", "macro_f1"):
        values = np.asarray([fold[metric] for fold in folds], dtype=np.float64)
        result[metric] = {
            "mean": float(values.mean()),
            "std": float(values.std(ddof=1)) if values.size > 1 else 0.0,
            "q025": float(np.quantile(values, 0.025)),
            "q975": float(np.quantile(values, 0.975)),
        }
    total_confusion = np.sum(
        np.asarray([fold["confusion_matrix"] for fold in folds], dtype=np.int64), axis=0
    )
    result["labels"] = labels
    result["summed_confusion_matrix"] = total_confusion.tolist()
    result["per_class_from_summed_confusion"] = _per_class_metrics(
        total_confusion, labels
    )
    return result


def _per_class_metrics(matrix: np.ndarray, labels: list[str]) -> dict[str, Any]:
    result = {}
    for index, label in enumerate(labels):
        true_positive = float(matrix[index, index])
        actual = float(matrix[index, :].sum())
        predicted = float(matrix[:, index].sum())
        recall = true_positive / actual if actual else 0.0
        precision = true_positive / predicted if predicted else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        result[label] = {"precision": precision, "recall": recall, "f1": f1}
    return result


def _paired_fold_comparison(
    candidate: dict[str, Any], reference: dict[str, Any]
) -> dict[str, Any]:
    reference_folds = {
        (fold["repeat"], fold["fold"]): fold["macro_f1"]
        for fold in reference["folds"]
    }
    differences = np.asarray(
        [
            fold["macro_f1"] - reference_folds[(fold["repeat"], fold["fold"])]
            for fold in candidate["folds"]
        ],
        dtype=np.float64,
    )
    return {
        "difference": "candidate_macro_f1_minus_a_core_logistic_macro_f1",
        "paired_fold_count": int(differences.size),
        "mean": float(differences.mean()),
        "std": float(differences.std(ddof=1)) if differences.size > 1 else 0.0,
        "q025": float(np.quantile(differences, 0.025)),
        "q975": float(np.quantile(differences, 0.975)),
        "candidate_win_fraction": float(np.mean(differences > 0)),
        "tie_fraction": float(np.mean(differences == 0)),
        "inference_note": "descriptive paired outer-fold differences; repeated folds are correlated",
    }


def nested_site_group_cv(
    dataset_path: Path | str,
    *,
    model_name: str,
    ablation: str,
    seed: int = 20260901,
    outer_splits: int = 5,
    outer_repeats: int = 5,
    inner_splits: int = 4,
) -> dict[str, Any]:
    if ablation not in ABLATION_RULES:
        raise ValueError(f"unknown ablation: {ablation}")
    rows, candidates = _load_dataset(dataset_path)
    feature_names = [name for name in candidates if ABLATION_RULES[ablation](name)]
    if not feature_names:
        raise ValueError(f"ablation {ablation} selected no features")
    x, y, groups, sessions = _matrix(rows, feature_names)
    labels = sorted(np.unique(y).tolist())
    folds: list[dict[str, Any]] = []
    best_parameters: list[dict[str, Any]] = []
    for repeat in range(outer_repeats):
        outer = StratifiedGroupKFold(
            n_splits=outer_splits, shuffle=True, random_state=seed + repeat
        )
        for fold_index, (train_index, test_index) in enumerate(
            outer.split(x, y, groups), start=1
        ):
            train_groups = groups[train_index]
            test_groups = groups[test_index]
            overlap = set(train_groups) & set(test_groups)
            if overlap:
                raise AssertionError(f"outer group leakage: {sorted(overlap)}")
            pipeline, parameter_grid = _pipeline(model_name, seed + repeat * 100 + fold_index)
            inner = StratifiedGroupKFold(
                n_splits=inner_splits,
                shuffle=True,
                random_state=seed + 10_000 + repeat * 100 + fold_index,
            )
            search = GridSearchCV(
                pipeline,
                parameter_grid,
                scoring="f1_macro",
                cv=inner,
                refit=True,
                n_jobs=-1,
                error_score="raise",
            )
            # Threading avoids Windows loky resource-tracker residue while retaining
            # parallelism for these small in-memory folds.
            with parallel_backend("threading"):
                search.fit(x[train_index], y[train_index], groups=train_groups)
            prediction = search.predict(x[test_index])
            metric = _fold_metrics(y[test_index], prediction, labels)
            folds.append(
                {
                    "repeat": repeat + 1,
                    "fold": fold_index,
                    "train_session_count": int(train_index.size),
                    "test_session_count": int(test_index.size),
                    "train_site_count": int(np.unique(train_groups).size),
                    "test_site_count": int(np.unique(test_groups).size),
                    "site_overlap_count": 0,
                    "inner_best_macro_f1": float(search.best_score_),
                    **metric,
                    "confusion_matrix": confusion_matrix(
                        y[test_index], prediction, labels=labels
                    ).tolist(),
                }
            )
            best_parameters.append(search.best_params_)
    parameter_modes = {
        name: Counter(str(item[name]) for item in best_parameters).most_common()
        for name in sorted(best_parameters[0])
    }
    return {
        "dataset": str(dataset_path),
        "model": model_name,
        "ablation": ablation,
        "seed": seed,
        "evaluation_implementation_version": EVALUATION_IMPLEMENTATION_VERSION,
        "outer_splits": outer_splits,
        "outer_repeats": outer_repeats,
        "inner_splits": inner_splits,
        "session_count": int(sessions.size),
        "site_count": int(np.unique(groups).size),
        "feature_count": len(feature_names),
        "feature_family_counts": dict(Counter(feature_family(name) for name in feature_names)),
        "parameter_selection_frequencies": parameter_modes,
        "summary": _summarize_folds(folds, labels),
        "folds": folds,
    }


def run_formal_tabular_evaluation(
    dataset_root: Path | str,
    output_root: Path | str,
    *,
    seed: int = 20260901,
    outer_splits: int = 5,
    outer_repeats: int = 5,
    inner_splits: int = 4,
) -> dict[str, Any]:
    root = Path(dataset_root)
    destination = Path(output_root)
    destination.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("a_core", "multinomial_logistic", "a_core_all"),
        ("a_core", "random_forest", "a_core_all"),
        ("a_plus_b", "multinomial_logistic", "a_plus_b_all"),
        ("a_plus_b", "random_forest", "a_plus_b_all"),
    ]
    # Systematic family/leave-one-family-out ablations use the interpretable
    # logistic model, while both model families receive nested tuning on full sets.
    jobs.extend(
        ("a_core", "multinomial_logistic", ablation)
        for ablation in (
            "workload_volume",
            "packetization_timing",
            "packet_length",
            "iat_timing",
            "interaction",
            "reversal_only",
            "transition_burst",
            "cumulative_shape",
            "a_core_minus_reversal",
            "a_core_minus_cumulative",
            "a_core_minus_packetization_timing",
        )
    )
    jobs.append(("a_plus_b", "multinomial_logistic", "transport_b_only"))
    results = []
    detailed_reports: dict[tuple[str, str, str], dict[str, Any]] = {}
    for feature_set, model_name, ablation in jobs:
        filename = f"nested-{feature_set}-{model_name}-{ablation}.json"
        report_path = destination / filename
        report = None
        if report_path.is_file():
            existing = json.loads(report_path.read_text(encoding="utf-8"))
            if (
                existing.get("seed") == seed
                and existing.get("outer_splits") == outer_splits
                and existing.get("outer_repeats") == outer_repeats
                and existing.get("inner_splits") == inner_splits
                and existing.get("evaluation_implementation_version", 1)
                == EVALUATION_IMPLEMENTATION_VERSION
            ):
                report = existing
        if report is None:
            report = nested_site_group_cv(
                root / f"protocol-classification-{feature_set}.parquet",
                model_name=model_name,
                ablation=ablation,
                seed=seed,
                outer_splits=outer_splits,
                outer_repeats=outer_repeats,
                inner_splits=inner_splits,
            )
            temporary = destination / (filename + ".tmp")
            temporary.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            os.replace(temporary, report_path)
        if "per_class_from_summed_confusion" not in report["summary"]:
            report["summary"]["per_class_from_summed_confusion"] = _per_class_metrics(
                np.asarray(report["summary"]["summed_confusion_matrix"], dtype=np.int64),
                report["summary"]["labels"],
            )
            report["evaluation_implementation_version"] = EVALUATION_IMPLEMENTATION_VERSION
            temporary = destination / (filename + ".tmp")
            temporary.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            os.replace(temporary, report_path)
        detailed_reports[(feature_set, model_name, ablation)] = report
        results.append(
            {
                "feature_set": feature_set,
                "model": model_name,
                "ablation": ablation,
                "feature_count": report["feature_count"],
                "macro_f1": report["summary"]["macro_f1"],
            }
        )
    manifest = {
        "evaluation": "repeated_nested_site_group_cv",
        "outer_splits": outer_splits,
        "outer_repeats": outer_repeats,
        "inner_splits": inner_splits,
        "seed": seed,
        "exploratory_holdout_used_for_tuning": False,
        "results": results,
    }
    reference = detailed_reports[("a_core", "multinomial_logistic", "a_core_all")]
    for result in manifest["results"]:
        key = (result["feature_set"], result["model"], result["ablation"])
        result["paired_against_a_core_logistic"] = _paired_fold_comparison(
            detailed_reports[key], reference
        )
    temporary = destination / "formal-evaluation-manifest.json.tmp"
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, destination / "formal-evaluation-manifest.json")
    return manifest
