# HFC-W observed-window experiment

Use Pytorch312 from the repository root. All model fitting, encoding/decoding and
classifier inference require CUDA. Packet parsing, bookkeeping and statistics use CPU.
Do not run the stages out of order or delete a contract to bypass a failure.

```text
python eval/hy2_carrier_calibration/window_extract.py
python eval/hy2_carrier_calibration/window_review.py
# The following prepare stage implements the explicitly approved window/tail exceptions.
python eval/hy2_carrier_calibration/window_prepare.py
python eval/hy2_carrier_calibration/window_generate.py engineering
python eval/hy2_carrier_calibration/window_generate.py paired
python eval/hy2_carrier_calibration/window_generate.py group
python eval/hy2_carrier_calibration/window_generate.py gate
python eval/hy2_carrier_calibration/generation_replay.py
python eval/hy2_carrier_calibration/window_classify.py --stage engineering
python eval/hy2_carrier_calibration/window_classify.py --stage restricted
python eval/hy2_carrier_calibration/window_classify.py --stage infer
python eval/hy2_carrier_calibration/window_classify.py --stage reference
python eval/hy2_carrier_calibration/window_classify.py --stage infer-reference
python eval/hy2_carrier_calibration/window_score.py
python eval/hy2_carrier_calibration/finalize_window.py
```

The paired and group generation workers use separate packages. Group C_post has no
session, repetition, timestamp, carrier identity or original row order. The group
worker never reads the paired package. U_post is not available through either bundle
loader; only the separate reference stage can read it after restricted predictions seal.
H_pre is not exported. H_labels are separate from inference and read only by scoring.

The accepted missing member is not fabricated as an event and is not an extra input
feature. Preserve the original failed audit and its refinement; user approval is
recorded in accepted-window-gate.json and docs/hy2-window-calibration-0916/decisions.md.

Outputs: outputs/hy2-window-calibration-0916/run-01/.
Final report: docs/hy2-window-calibration-0916/summary.md.

Learning contracts hash the fitting, classification and scoring source before training.
Resume unchanged stages only. Neither the old SS/VLESS experiment nor the strict Hy2
qualification audit is overwritten.
