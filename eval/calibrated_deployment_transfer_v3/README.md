# Calibrated deployment transfer v3

Approved plan: `plan/calibrated-deployment-gradient-aware-solver-plan-20261006.md`.
Use Pytorch312; CUDA float64 is mandatory. Run `prepare.py`, then `runner.py`.

Old runs and sources are read-only. The original CE, L2, post scaler, labels,
mass, roles, missing-business masks, kernels and content splits are unchanged.
The v2 reversible Cholesky parameterization is retained. A locally derived
LBFGS step replaces transformed-gradient and lack-of-progress convergence with
independent original-coordinate gradient verification. The installed optimizer
is not patched. Two-loop and line-search arithmetic are retained and audited.

No 500-iteration or 625-evaluation budget increase. Three exactly unchanged
updates fail. Nonfinite or non-descent directions fail. Final original gates
remain unchanged. Failed states never become accepted models.

Exactly four complete synthetic fits precede registration. Fifteen fixed
inner roles give 300 pilot candidates, included in the 14,400 inner-fit budget.
Two historical failure roles each get one extra deterministic diagnostic fit.
All 104 accepted v2 main candidates are preserved but not reused as v3 models.
680 old diagnostic models and 20 historical post references are reused only
after checks. All main predictions must be sealed before scoring or test-pre
analysis. No PCAP rescanning or new traffic capture.
