# RA1 NR1 finite numerical pilot

Authorized on 2026-10-18: 4000 iterations, 20000 function evaluations,
30-minute activity cap. Original model/objective/weights/precision gates
unchanged. No full-matrix restart, query/H/U reads, or parameter warm start.

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/role_asymmetric_transfer_numeric_pilot_v1/run.py
```

Registration binds the fixed 42 cases and at most 45 physical attempts.
First reproduce the original 2000/10000 rejection from zero, then solve the
same case under NR1 and compare the accepted-point prefix at iteration 2000.
Only if it qualifies, proceed to fixed controls and two exact repeats.
Stop on any unqualified NR1 case; no automatic budget extension or backend
switch. Successful N4 still requires user review before any full experiment.

The backend loader compiles the historical function bodies unchanged into
isolated namespaces. Runtime wrappers inject scoped policy/IO, check activity
limits and clone a read-only prefix; they never modify installed PyTorch or
old modules. Last 60 seconds of the 1800-second cap are reserved for closeout.

Outputs:
`outputs/role-asymmetric-transfer-v1-20261017/numeric-pilot-nr1`.
Report:
`docs/role-asymmetric-transfer-v1-20261017/numeric-pilot-report-20261018.md`.
The original run-01 stop and cost ledger are read-only.
