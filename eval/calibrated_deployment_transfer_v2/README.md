# Calibrated deployment transfer v2

Approved repair: `plan/calibrated-deployment-optimizer-repair-plan-20261006.md`.
The original run and source are read-only. V2 uses exactly the original CE,
weight decay, post scaler, samples, masks and content splits. A reversible
97-dimensional curvature parameterization improves numerical optimization;
models are decoded to the original 96D weight and bias before acceptance.

Use Pytorch312. Run `python prepare.py`, then `python runner.py` from this folder
or use repository-relative script paths. CUDA float64 is mandatory. No gate or
500-iteration budget is relaxed. A failed pilot stops before any main selection
or target scoring. Failed numerical states are saved outside accepted models.

The 60 accepted pilot candidates are part of the 14,400 inner-fit budget.
Determinism checks and synthetic tests are separately labeled diagnostic fits.
The four accepted main models of run-01 are deliberately refitted so all five
main methods use the same v2 solver. Old 680 diagnostic models are reused only
after independent original-objective gradient checks.

Frozen downstream functions execute against the v2 IO adapter without modifying
their source. Only input slots/kernels and role packages route to run-01; models,
selection, predictions, logs and reports route to run-02 and the v2 report folder.
Predictions must be sealed before main labels or offline test-pre are readable.
Observation inventory is not proof of physical-only extraction.
