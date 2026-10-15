# Small auxiliary view attribution

Independent run for the approved 2026-10-10 plan. Historical CT/JA/TI contracts,
models, predictions and confidence intervals are read-only. Three new controls
replace exactly 10% of the CORAL auxiliary loss mass, not 10% of total CE.

Run once from the repository root, using Pytorch312:

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' 'eval/small_view_attribution/run.py'
```

The fixed 36-model pilot counts within 180 new CUDA float64 classifiers.
Promotion depends only on original-coordinate numerical gates, never target F1.
All 360 new/reused classifier endpoints precede prediction sealing and scoring.
Target-U training traffic, test pre and PCAP are forbidden. Anonymous marginal
workers receive only two independently permuted numeric/weight arrays.

Stages are also individually executable with the arguments in `run.py`.
Completed stages and accepted artifacts cannot be overwritten. A failed stage
preserves its logs and stops the runner; do not retry or extend its budget.

Outputs: `outputs/small-view-attribution-20261010/run-02/`. The registration-only
run-01 failed before tests/fits on an external installed-library path formatting
bug. Its contract is preserved; scientific settings and numerical gates did not
change. Do not run old run-01 with the now revised source.
Reports and Python-generated figures: `docs/small-view-attribution/`.
Historical-batch and physical-input qualification are reported separately;
successful attribution does not mark either as externally validated.
