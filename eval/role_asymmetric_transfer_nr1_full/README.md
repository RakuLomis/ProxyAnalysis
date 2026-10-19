# RA1 full NR1 resume

Authorized 2026-10-18: complete the fixed RA1 matrix using NR1's 4000/20000
budget, all other scientific settings and precision gates unchanged. The
original stopped run and passed pilot are immutable dependencies.

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/role_asymmetric_transfer_nr1_full/run.py
```

42 NR1 pilot models take precedence on their fixed keys, plus 124 compatible
old scientific models and 420 historical references: 586 adopted endpoints.
Each is independently audited before the remaining 1754 zero-initialized LR
fits. Complete 2340-model seal precedes H queries; complete 56160-row prediction
seal precedes labels. Original scoring/inference ASTs are preserved.

No new mapping, scaler, neural training, scientific hyperparameter selection,
test-side routing or hidden fallback. CUDA float64 and original v4 arithmetic;
global activity checks wrap the objective but do not change its value.

The 8-hour cap includes the original run, NR1 and recorded analyses. An explicit
60-second conservative prior overhead charge is not presented as a measurement.
New-process import/configuration time is included. Stop compute at 28680 total
seconds, reserving the final 120 seconds for closeout. Any unqualified solve,
integrity problem or safety budget stops this run without automatic retry.

Output: `outputs/role-asymmetric-transfer-v1-20261017/full-nr1-01`.
Report: `docs/role-asymmetric-transfer-v1-20261017/full-nr1/complete-report.md`.
