# Feasible-summary calibration, 0916

Run with Pytorch312 from the repository root. CUDA is mandatory for generator fitting/encoding/decoding and classifier training/inference. Metadata and statistics run on CPU. The old cross-business experiment stays read-only.

```text
python eval/feasible_summary_calibration/run.py --stage prepare
python eval/feasible_summary_calibration/run.py --stage engineering
python eval/feasible_summary_calibration/run.py --stage paired
python eval/feasible_summary_calibration/run.py --stage group
python eval/feasible_summary_calibration/run.py --stage gate
python eval/feasible_summary_calibration/audit.py
python eval/feasible_summary_calibration/classify.py --stage engineering
python eval/feasible_summary_calibration/classify.py --stage restricted
python eval/feasible_summary_calibration/classify.py --stage infer
python eval/feasible_summary_calibration/classify.py --stage reference
python eval/feasible_summary_calibration/classify.py --stage infer-reference
python eval/feasible_summary_calibration/score.py
python eval/feasible_summary_calibration/finalize.py
```

Paired and group generation are separate processes reading different allowlisted source bundles. No new source cohort is selected. The group encoder never receives post F or a calibration pair identifier. All five generators share the same feasible decoder, with one candidate draw, no rejection sampling, and no fallback. Overflow/invalid numeric states stop the run.

Generation and classifier contracts are frozen separately. Classifier engineering refuses to start unless both the independent generation gate and lineage/replay audit pass. The reference stage refuses to read U_post until restricted predictions have been sealed. Scoring reads held-out labels only after both regimes seal their predictions.

Stage outputs are in `outputs/feasible-summary-calibration-0916/run-01/`; the final report and figures are in `docs/feasible-summary-calibration-0916/`. Resume only unchanged contracts. Do not replace an old experiment's inputs or thresholds to make its checks pass.
