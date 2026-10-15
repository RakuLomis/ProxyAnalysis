"""Post-hoc summary of sealed diagnostics; never fit, select, or read main test data.

This analysis is deliberately outside the sealed experiment module directory.
CPU is used for saved-table arithmetic and plotting, not for model inference.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "outputs/calibrated-deployment-business-transfer-20261006/run-01"
DEST = ROOT / "outputs/calibrated-deployment-business-transfer-analysis-20261006/run-01"
FIG = ROOT / "docs/calibrated-deployment-business-transfer/figures"
PROTOCOLS = ["shadowsocks", "vless", "trojan", "vmess"]
NAMES = ["SS", "VLESS", "Trojan", "VMess"]
LABELS = ["bing.com::search_results_view", "developer.mozilla.org::document_view",
          "github.com::repository_view", "wikipedia.org::article_view",
          "youtube.com::search_results_view", "youtube.com::video_playback"]
FEATURES = ["W_up", "W_down", "U_up", "U_down", "P_up", "P_down", "E_up", "E_down",
            "FR_packet_runs", "R_unique_zero_runs"]
WEIGHTS = np.array([1 / 12] * 8 + [1 / 6] * 2)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    assert (RUN / "failure.json").exists(), "This script summarizes an interrupted run only"
    assert not (RUN / "completion.json").exists(), "Use the formal report for a completed run"
    assert not (RUN / "predictions/visits.parquet").exists(), "Main predictions now exist; do not overwrite a partial-run summary"
    DEST.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    contract = read(RUN / "manifests/experiment-contract-amended-io-v1.json")
    seal = read(RUN / "manifests/engineering-io-cache-v1/amendment-seal.json")
    checks = {
        "baseline_953_files_match": all(sha(ROOT / p) == h for p, h in contract["baseline_sha256"].items()),
        "sealed_source_13_files_match": all(sha(ROOT / p) == h for p, h in contract["source_sha256"].items()),
        "approved_plan_matches": sha(ROOT / "plan/calibrated-deployment-business-transfer-plan-20261006.md") == contract["plan_sha256"],
        "original_contract_matches": sha(RUN / "manifests/experiment-contract.json") == seal["original_contract_sha256"],
        "io_amended_contract_matches": sha(RUN / "manifests/experiment-contract-amended-io-v1.json") == seal["amended_contract_sha256"],
        "diagnostic_predictions_match": sha(RUN / "diagnostics/predictions/visits.parquet") == read(RUN / "diagnostics/predictions/complete.json")["sha256"],
    }
    assert all(checks.values()), checks
    summary = pd.read_parquet(RUN / "diagnostics/classification-summary.parquet")
    pred = pd.read_parquet(RUN / "diagnostics/predictions/visits.parquet")
    labels = []
    for outer in range(5):
        for protocol in PROTOCOLS:
            part = pd.read_parquet(RUN / f"packages/diagnostics/post/f{outer}/{protocol}/labels.parquet").drop(columns="protocol")
            part["outer"], part["target"] = outer, protocol
            labels.append(part)
    scored = pred.merge(pd.concat(labels), on=["outer", "target", "visit_id"], validate="many_to_one")
    classes, matrices, maximum_error = [], [], 0.0
    for (kind, source, target), part in scored.groupby(["kind", "source", "target"]):
        assert len(part) == 120 and part.content_id.nunique() == 30
        y = part.label_id.map(dict(zip(LABELS, range(6)))).to_numpy(int)
        prob = part[[f"p{i}" for i in range(6)]].to_numpy()
        z = prob.argmax(1)
        assert np.array_equal(z, part.prediction.to_numpy())
        cm = np.bincount(6 * y + z, minlength=36).reshape(6, 6)
        denom = cm.sum(0) + cm.sum(1)
        f1 = np.divide(2 * cm.diagonal(), denom, out=np.zeros(6), where=denom > 0)
        values = dict(F1_all=float(f1.mean()), accuracy=float((z == y).mean()),
                      CE_nats=float(-np.log(prob[np.arange(len(y)), y]).mean()),
                      Brier=float(((prob - np.eye(6)[y]) ** 2).sum(1).mean()))
        old = summary[(summary.kind == kind) & (summary.source == source) & (summary.target == target)].iloc[0]
        maximum_error = max(maximum_error, max(abs(values[k] - old[k]) for k in values))
        for j, label in enumerate(LABELS):
            classes.append(dict(kind=kind, source=source, target=target, label=label,
                                F1=float(f1[j]), support=int(cm[j].sum()), correct=int(cm[j, j])))
        matrices.append(dict(kind=kind, source=source, target=target, matrix=cm.tolist()))
    assert maximum_error < 1e-12
    pd.DataFrame(classes).to_parquet(DEST / "diagnostic-class-results.parquet", index=False)
    (DEST / "diagnostic-confusion-matrices.json").write_text(json.dumps(matrices, indent=2) + "\n", encoding="utf-8")

    raw = pd.read_parquet(RUN / "diagnostics/kernel-feature-summary.parquet")
    kernels = []
    for (source, target), part in raw.groupby(["source", "target"]):
        part = part.set_index("feature").loc[FEATURES]
        conditional = float(part.loss_bits @ WEIGHTS)
        marginal = float(part.marginal_bits @ WEIGHTS)
        kernels.append(dict(source=source, target=target, conditional_loss_bits=conditional,
                            marginal_loss_bits=marginal, gain_bits=marginal - conditional,
                            weighted_zero_support_fraction=float(part.zero_support_fraction @ WEIGHTS)))
    kernels = pd.DataFrame(kernels)
    kernels.to_parquet(DEST / "diagnostic-kernel-composites.parquet", index=False)
    raw["gain_bits"] = raw.marginal_bits - raw.loss_bits
    raw[raw.source != raw.target].groupby("feature")[["loss_bits", "marginal_bits", "gain_bits"]].mean().to_parquet(DEST / "cross-deployment-feature-losses.parquet")

    aggregations = []
    for kind in ["pre", "post"]:
        part = summary[summary.kind == kind]
        for scope, flag in [("same_deployment", part.source == part.target), ("different_deployment", part.source != part.target)]:
            selected = part[flag]
            aggregations.append(dict(kind=kind, scope=scope, cells=len(selected), **selected[["F1_all", "accuracy", "CE_nats", "Brier"]].mean().to_dict()))
    part = summary[summary.kind == "postmix"]
    aggregations.append(dict(kind="postmix", scope="different_deployment", cells=4, **part[["F1_all", "accuracy", "CE_nats", "Brier"]].mean().to_dict()))
    pd.DataFrame(aggregations).to_parquet(DEST / "diagnostic-equal-cell-summary.parquet", index=False)

    first_missing = None
    for role in contract["main"]:
        if role["inner"] is None:
            continue
        for arm in ["CT0", "CT1", "CT2", "CT3", "CT4"]:
            for t in [0, .25, 1, 4]:
                if not (RUN / "models" / role["id"] / f"{arm}-t{t:g}.json").exists():
                    first_missing = {k: role[k] for k in ["id", "outer", "inner", "target", "calibration", "sources", "group"]}
                    first_missing.update(arm=arm, t=t, identified_from_execution_order=True,
                                         exact_failed_gate_not_logged=True)
                    break
            if first_missing:
                break
        if first_missing:
            break
    model_logs = []
    for directory in ["diagnostics", "main"]:
        for path in (RUN / "models" / directory).rglob("*.json"):
            meta = read(path)
            assert sha(path.with_suffix(".pt")) == meta["sha256"]
            model_logs.append(dict(kind=directory, path=path.relative_to(ROOT).as_posix(), **meta["optimizer"]))
    pd.DataFrame(model_logs).to_parquet(DEST / "saved-model-optimization-records.parquet", index=False)

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    for ax, kind in zip(axes.flat[:2], ["pre", "post"]):
        matrix = summary[summary.kind == kind].pivot(index="source", columns="target", values="F1_all").loc[PROTOCOLS, PROTOCOLS].to_numpy()
        im = ax.imshow(matrix, vmin=0, vmax=1, cmap="viridis")
        ax.set(title=f"{kind.upper()} macro F1", xlabel="Test deployment", ylabel="Training deployment")
        ax.set_xticks(range(4), NAMES); ax.set_yticks(range(4), NAMES)
        for (i, j), value in np.ndenumerate(matrix):
            ax.text(j, i, f"{value:.3f}", ha="center", va="center", color="white" if value < .5 else "black")
        fig.colorbar(im, ax=ax, shrink=.8)
    ax = axes[1, 0]
    mix = summary[summary.kind == "postmix"].set_index("target").loc[PROTOCOLS]
    ax.bar(NAMES, mix.F1_all, color="#3274a1")
    ax.set(title="Three-source post mix to held deployment", ylabel="Macro F1", ylim=(0, 1))
    for i, value in enumerate(mix.F1_all):
        ax.text(i, value + .02, f"{value:.3f}", ha="center")
    ax = axes[1, 1]
    matrix = kernels.pivot(index="source", columns="target", values="gain_bits").loc[PROTOCOLS, PROTOCOLS].to_numpy()
    maximum = np.abs(matrix).max()
    im = ax.imshow(matrix, vmin=-maximum, vmax=maximum, cmap="RdBu")
    ax.set(title="Conditional kernel gain over source marginal (bits)", xlabel="Scored deployment", ylabel="Kernel deployment")
    ax.set_xticks(range(4), NAMES); ax.set_yticks(range(4), NAMES)
    for (i, j), value in np.ndenumerate(matrix):
        ax.text(j, i, f"{value:+.3f}", ha="center", va="center", color="white" if abs(value) > maximum * .6 else "black")
    fig.colorbar(im, ax=ax, shrink=.8)
    fig.savefig(FIG / "partial-transfer-diagnostics.png", dpi=180)
    plt.close(fig)

    model_table = pd.DataFrame(model_logs)
    main_table = model_table[model_table.kind == "main"]
    main_outer_count = int(main_table.path.str.contains("/outer/").sum())
    result = dict(status="partial_results_engineering_stop_not_completed", source_run=str(RUN),
                  checks=checks, diagnostic_metric_replay_max_error=maximum_error,
                  diagnostic_new_fits=int((model_table.kind == "diagnostics").sum()),
                  saved_main_inner_fits=len(main_table) - main_outer_count, main_outer_fits=main_outer_count,
                  first_unsaved_main_candidate=first_missing, main_primary_comparisons="not_evaluated",
                  new_model_fits=0, model_inference_performed=False, main_test_data_read=False,
                  cpu_saved_table_analysis_only=True,
                  diagnostic_prediction_rows=len(pred), diagnostic_summary_cells=len(summary),
                  kernel_composite_cells=len(kernels), final_experiment_verification_performed=False)
    (DEST / "analysis-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
