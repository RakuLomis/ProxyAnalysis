"""Publication-oriented tables, figures, quality gates, and lineage manifest."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

_matplotlib_cache = Path(tempfile.gettempdir()) / "proxy-analysis-matplotlib"
_matplotlib_cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_matplotlib_cache))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyarrow.parquet as pq

from .config import StatisticalConfig
from .inference import finite


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def _atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = sorted(set().union(*(row.keys() for row in rows))) if rows else []
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def _save_figure(fig: plt.Figure, root: Path, stem: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg"):
        temporary = root / f"{stem}.{suffix}.tmp"
        final = root / f"{stem}.{suffix}"
        fig.savefig(temporary, format=suffix, dpi=180, bbox_inches="tight")
        os.replace(temporary, final)
    plt.close(fig)


def _q1_forest(rows: list[dict[str, Any]], figures: Path) -> None:
    selected = [row for row in rows if finite(row.get("median"))]
    selected.sort(key=lambda row: (row["metric_id"], row["protocol_dataset"]))
    colors = {"HYSTERIA2": "#d95f02", "SHADOWSOCKS": "#1b9e77", "VLESS": "#7570b3"}
    fig, axis = plt.subplots(figsize=(10, max(7, len(selected) * 0.27)))
    positions = np.arange(len(selected))
    medians = np.asarray([float(row["median"]) for row in selected])
    lows = np.asarray(
        [float(row["cluster_bootstrap_median_ci95_low"]) for row in selected]
    )
    highs = np.asarray(
        [float(row["cluster_bootstrap_median_ci95_high"]) for row in selected]
    )
    for protocol in colors:
        indexes = [i for i, row in enumerate(selected) if row["protocol_dataset"] == protocol]
        if not indexes:
            continue
        axis.errorbar(
            medians[indexes],
            positions[indexes],
            xerr=np.vstack((medians[indexes] - lows[indexes], highs[indexes] - medians[indexes])),
            fmt="o",
            color=colors[protocol],
            capsize=2,
            label=protocol,
        )
    axis.axvline(0, color="black", linewidth=0.8, linestyle="--")
    axis.set_yticks(positions)
    axis.set_yticklabels(
        [f"{row['metric_id']} · {row['protocol_dataset']}" for row in selected], fontsize=7
    )
    axis.set_xlabel("Median proxy transformation with site-cluster bootstrap 95% CI")
    axis.set_title("Q1: within-protocol pre/post transformation")
    axis.invert_yaxis()
    axis.legend(loc="best", fontsize=8)
    axis.grid(axis="x", alpha=0.2)
    _save_figure(fig, figures, "q1-within-protocol-forest")


def _q2_heatmap(rows: list[dict[str, Any]], figures: Path) -> None:
    metrics = sorted({str(row["metric_id"]) for row in rows})
    stages = ("pre", "post", "delta")
    lookup = {(row["metric_id"], row["stage"]): row.get("kendalls_w") for row in rows}
    matrix = np.asarray(
        [
            [float(lookup[(metric, stage)]) if finite(lookup.get((metric, stage))) else np.nan for stage in stages]
            for metric in metrics
        ]
    )
    fig, axis = plt.subplots(figsize=(6, max(5, len(metrics) * 0.45)))
    image = axis.imshow(matrix, aspect="auto", vmin=0, vmax=1, cmap="viridis")
    axis.set_xticks(range(len(stages)), stages)
    axis.set_yticks(range(len(metrics)), metrics, fontsize=8)
    axis.set_title("Q2: matched three-protocol effect size (Kendall's W)")
    for row_index in range(matrix.shape[0]):
        for column_index in range(matrix.shape[1]):
            if np.isfinite(matrix[row_index, column_index]):
                axis.text(
                    column_index,
                    row_index,
                    f"{matrix[row_index, column_index]:.2f}",
                    ha="center",
                    va="center",
                    color="white" if matrix[row_index, column_index] > 0.5 else "black",
                    fontsize=7,
                )
    fig.colorbar(image, ax=axis, label="Kendall's W")
    _save_figure(fig, figures, "q2-cross-protocol-kendalls-w")


def _coverage_figure(audit: Mapping[str, Any], figures: Path) -> None:
    protocols = ["HYSTERIA2", "SHADOWSOCKS", "VLESS"]
    available = audit["page"]["available_target_count_by_protocol"]
    strict = audit["url_strict"]["target_cluster_count_by_protocol"]
    x = np.arange(len(protocols))
    width = 0.35
    fig, axis = plt.subplots(figsize=(7, 4))
    axis.bar(x - width / 2, [available[p] for p in protocols], width, label="Page proxy coverage")
    axis.bar(x + width / 2, [strict[p] for p in protocols], width, label="URL-strict target coverage")
    axis.axhline(20, color="black", linestyle="--", linewidth=0.8, label="Minimum cluster gate")
    axis.set_xticks(x, protocols)
    axis.set_ylabel("Target URL clusters")
    axis.set_title("Coverage by protocol and attribution cohort")
    axis.legend(fontsize=8)
    _save_figure(fig, figures, "coverage-by-protocol")


def finalize_statistical_analysis(
    output_root: Path | str, config_path: Path | str
) -> dict[str, Any]:
    root = Path(output_root)
    config = StatisticalConfig.load(config_path)
    required = {
        "coverage": root / "coverage-audit.json",
        "frozen_spec": root / "frozen-analysis-spec.json",
        "page_summary": root / "page-statistics-summary.json",
        "resource_summary": root / "q3-resource-host-results.json",
        "sensitivity_summary": root / "sensitivity-summary.json",
        "q1": root / "q1-within-protocol-results.parquet",
        "q2_omnibus": root / "q2-cross-protocol-omnibus.parquet",
        "q2_pairwise": root / "q2-cross-protocol-pairwise.parquet",
        "q3_within": root / "q3-within-protocol-results.parquet",
        "sensitivity": root / "sensitivity-matrix.parquet",
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        raise ValueError(f"missing statistical outputs: {missing}")
    audit = json.loads(required["coverage"].read_text(encoding="utf-8"))
    page_summary = json.loads(required["page_summary"].read_text(encoding="utf-8"))
    resource_report = json.loads(required["resource_summary"].read_text(encoding="utf-8"))
    sensitivity_summary = json.loads(
        required["sensitivity_summary"].read_text(encoding="utf-8")
    )
    q1 = pq.read_table(required["q1"]).to_pylist()
    q2_omnibus = pq.read_table(required["q2_omnibus"]).to_pylist()
    q2_pairwise = pq.read_table(required["q2_pairwise"]).to_pylist()
    q3_within = pq.read_table(required["q3_within"]).to_pylist()
    sensitivity = pq.read_table(required["sensitivity"]).to_pylist()

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for name, summary in (
        ("coverage", audit),
        ("page", page_summary),
        ("resource", resource_report["summary"]),
        ("sensitivity", sensitivity_summary),
    ):
        if summary.get("statistical_config_sha256") != config.sha256:
            errors.append({"code": "config_hash_mismatch", "output": name})
    if audit["page"]["complete_triplet_row_count"] != 120:
        errors.append({"code": "page_complete_triplet_row_count"})
    if audit["page"]["complete_triplet_target_count"] != 40:
        errors.append({"code": "page_complete_triplet_target_count"})
    for table_name, rows in (
        ("q1", q1),
        ("q2_omnibus", q2_omnibus),
        ("q2_pairwise", q2_pairwise),
        ("q3_within", q3_within),
    ):
        for row in rows:
            for name in ("pvalue_raw", "qvalue_bh", "blocked_permutation_pvalue"):
                value = row.get(name)
                if value is not None and (not finite(value) or not 0 <= float(value) <= 1):
                    errors.append(
                        {"code": "invalid_probability", "table": table_name, "column": name}
                    )
                    break
    if any(
        row["protocol_dataset"] == "HYSTERIA2" and row["metric_id"] == "flow_reversals"
        for row in q1
    ):
        errors.append({"code": "hysteria2_tcp_flow_reversal_present"})
    vless_transition = [
        row
        for row in q1
        if row["protocol_dataset"] == "VLESS" and row["metric_id"] == "transition_p_pm"
    ]
    if len(vless_transition) != 1 or vless_transition[0].get("interpretation_flag") != config.interpretation_policy["transition_p_pm"]["within_vless"]:
        errors.append({"code": "vless_transition_interpretation_not_frozen"})
    transition_omnibus = [row for row in q2_omnibus if row["metric_id"] == "transition_p_pm"]
    if not transition_omnibus or any(
        row.get("interpretation_flag")
        != config.interpretation_policy["transition_p_pm"]["cross_protocol"]
        for row in transition_omnibus
    ):
        errors.append({"code": "transition_pre_imbalance_interpretation_not_frozen"})
    acknowledged_conflicts = [
        row
        for row in sensitivity
        if row.get("direction_stable") is False
        and row.get("protocol_dataset") == "VLESS"
        and row.get("metric_id") == "transition_p_pm"
    ]
    unacknowledged = [
        row
        for row in sensitivity
        if row.get("direction_stable") is False and row not in acknowledged_conflicts
    ]
    if unacknowledged:
        errors.append(
            {"code": "unacknowledged_direction_conflict", "count": len(unacknowledged)}
        )
    if acknowledged_conflicts:
        warnings.append(
            {
                "code": "acknowledged_vless_transition_direction_instability",
                "count": len(acknowledged_conflicts),
                "explanation": (
                    "The median is below the practical threshold, non-significant, and its "
                    "site-cluster CI crosses zero; no stable within-VLESS directional claim is made."
                ),
            }
        )
    warnings.append(
        {
            "code": "hysteria2_url_weighted_descriptive_only",
            "explanation": "Hysteria2 has only two URL-strict target clusters because carrier sharing is intrinsic.",
        }
    )
    warnings.append(
        {
            "code": "cdn_endpoint_unobservable",
            "explanation": "Host/SNI and proxy endpoints do not identify an origin CDN IP, provider, or PoP.",
        }
    )

    tables = root / "tables"
    _write_csv(tables / "q1-within-protocol-results.csv", q1)
    _write_csv(tables / "q2-cross-protocol-omnibus.csv", q2_omnibus)
    _write_csv(tables / "q2-cross-protocol-pairwise.csv", q2_pairwise)
    _write_csv(tables / "q3-within-protocol-results.csv", q3_within)
    _write_csv(tables / "sensitivity-matrix.csv", sensitivity)
    figures = root / "figures"
    _q1_forest(q1, figures)
    _q2_heatmap(q2_omnibus, figures)
    _coverage_figure(audit, figures)

    quality = {
        "state": "passed" if not errors else "failed",
        "statistical_config_sha256": config.sha256,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "result_counts": {
            "q1": len(q1),
            "q2_omnibus": len(q2_omnibus),
            "q2_pairwise": len(q2_pairwise),
            "q3_within": len(q3_within),
            "sensitivity": len(sensitivity),
        },
    }
    _atomic_json(root / "statistical-quality-report.json", quality)

    readme = f"""# URL-aligned statistical analysis

Quality state: **{quality['state']}** ({quality['error_count']} errors, {quality['warning_count']} explained warnings).

- Confirmatory unit: page/session with site-clustered uncertainty.
- Complete three-protocol cohort: 40 target URLs × 3 protocols.
- URL-strict confirmatory scope: Shadowsocks and VLESS.
- Hysteria2 URL scope: weighted descriptive carrier context only.
- Cross-protocol URL/host scope: exploratory weighted carrier context.
- TCP Flow Reversal preservation excludes Hysteria2.
- `transition_p_pm` is retained with a frozen caveat: the within-VLESS direction is unstable and not practically meaningful; cross-protocol results are pre-imbalanced joint associations.
- CDN endpoint/provider/PoP analysis is unsupported by the current capture points.

Main machine-readable results are the Q1/Q2/Q3 Parquet and JSON files. CSV tables are in `tables/`; figures are in `figures/`; exact lineage and hashes are in `statistical-analysis-manifest.json`.
"""
    _atomic_text(root / "README.md", readme)

    artifact_paths = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.name != "statistical-analysis-manifest.json"
    )
    manifest = {
        "statistical_config_sha256": config.sha256,
        "quality_state": quality["state"],
        "artifacts": {
            str(path.relative_to(root)): {
                "sha256": _sha256(path),
                "byte_size": path.stat().st_size,
                **(
                    {
                        "row_count": pq.read_metadata(path).num_rows,
                        "column_count": len(pq.read_schema(path).names),
                    }
                    if path.suffix == ".parquet"
                    else {}
                ),
            }
            for path in artifact_paths
        },
        "inference_policy": {
            "page": "confirmatory",
            "url_strict": "confirmatory for SHADOWSOCKS/VLESS",
            "hysteria2_url": "weighted descriptive carrier context",
            "cross_protocol_url_host": "exploratory",
        },
        "cdn_endpoint_analysis_supported": False,
    }
    _atomic_json(root / "statistical-analysis-manifest.json", manifest)
    return quality
