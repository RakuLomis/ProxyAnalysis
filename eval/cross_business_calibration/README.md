# Cross-business calibration (0916)

Run from repository root using Pytorch312. CUDA is mandatory for fitting. Historical CB outputs remain read-only.

```text
python eval/cross_business_calibration/run.py --stage export
python eval/cross_business_calibration/engineering.py
python eval/cross_business_calibration/run.py --stage paired
python eval/cross_business_calibration/run.py --stage group
python eval/cross_business_calibration/run.py --stage gate
python eval/cross_business_calibration/audit.py
python eval/cross_business_calibration/report_gate.py
```

Paired and group generation run in separate processes. Each receives its own role-limited bundle. A failed gate exits with status 2: continue only read-only auditing/report delivery, not classification. Do not raise thresholds or omit failed cells automatically.

The group generator receives anonymous calibration pre/post sets linked only by content. Group post data omit session, repetition, time and F; their numeric order is canonical and independent of true matching. U pre retains its query identity for output bookkeeping. The group objective and Cartesian LOCO residuals are separately implemented, not borrowed from true-pair residuals.

Engineering freezes a source/manifest contract before generation. Checkpoints resume only when bundle/file hashes match. Scripts added later for auditing do not alter the frozen generator. To change a method or threshold, register a new experiment/version rather than silently replacing frozen artifacts.

No classification runner is authorized past a failed generation gate. See `docs/cross-business-calibration-0916/summary.md` and output `status.json` for the current stopping point.
