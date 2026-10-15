# Calibrated deployment business transfer v4

Approved plan: `plan/calibrated-deployment-unified-budget-repair-plan-20261006.md`.
Pytorch312 and CUDA float64 are mandatory. Run `prepare.py`, then `runner.py`.

Only the v3 uniform optimization limits and iteration-budget eligibility change:
2000 iterations, 10000 function evaluations, accepted iterations strictly below
2000. Original CE, W L2, unpenalized bias, preconditioning, original-coordinate
gradient (1e-5), and independent replay precision (1e-10) are unchanged.
Evaluation checks remain at iteration boundaries after line search; actual
overshoot is logged. No extra step, warm start, clipping, CPU or Newton fallback.

Four complete synthetic fits precede sealing. All 15 frozen pilot roles (300
candidates) must pass, followed by two exact deterministic replays and compatibility
checks for 680 old diagnostic models and 20 post references. Pilot promotion is
included in 14400 inner fits, followed by 300 outer fits. Main models from old
runs, including the 24 unpromoted v3 pilot models, are never adopted as v4 models.
Old diagnostics retain their historical iteration gate (<500).

All choices and predictions are sealed before test labels or test pre are read.
A numerical failure stops the runner and cannot be silently retried or bypassed.
Old runs, source, reports and installed PyTorch are read-only. No new capture.
