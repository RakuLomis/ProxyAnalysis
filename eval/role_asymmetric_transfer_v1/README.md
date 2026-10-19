# RA1 v1: role-asymmetric forward-drift view allocation

Approved implementation plan:
`plan/RA1-role-asymmetric-forward-drift-implementation-plan-20261017.md`.
User authorized implementation on 2026-10-18.

Run from the repository root:

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/role_asymmetric_transfer_v1/run.py
```

Independent output root:
`outputs/role-asymmetric-transfer-v1-20261017/run-01`.
Historical contracts, code, views, models and results are read-only.

The only scientific change is auxiliary CE-mass allocation by training C/U
role. 39 fixed policies, 60 outer roles; 1920 new v4 LR fits and 420 audited
historical aliases. No new mapping, scaler, CORAL, neural model, temperature,
hyperparameter selection or test-side routing. The main candidate is
`P__m025__UPR`, i.e. `(rho_C,rho_U)=(0,.5)`.

CUDA float64 is mandatory. `solver_v4.py` has the same AST as the historical
v4 solver; the local common module redirects IO only, not solver arithmetic.
All scalar replacement weights are explicitly float64.

P0/P1 never open H. P2 is a 48-fit engineering pilot using legal target C,
not a source-only scientific screening experiment. P4 seals every model;
P5 seals every H-post prediction before P6 can open labels. Historical H
has been studied before; this is an internal fixed-policy evaluation.

The 8-hour active budget includes failed attempts and verification. Completed
stages can be skipped only with the unchanged contract. A failure is terminal
for this run, preserved without automatic retry, hidden fallback or changed
precision. Accepted partial endpoints are retained, but resuming a failed
stage requires an independently registered repair policy.
