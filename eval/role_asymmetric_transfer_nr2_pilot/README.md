# RA1-NR2 bounded numerical pilot

Only the authorized 30-minute same-objective second-order pilot. Does not restart the full matrix or read H/U.

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/role_asymmetric_transfer_nr2_pilot/run.py
```

Uses original v4 arithmetic for the initial phase, then exact-Hessian Newton in a 581-coordinate mean-bias gauge. All W and its original L2 remain intact. Final acceptance uses the original 582-coordinate objective and gradient. See the frozen plan and design under `plan/RA1-NR2-*`.

Output: `outputs/role-asymmetric-transfer-v1-20261017/numeric-pilot-nr2-02/`.
Report: `docs/role-asymmetric-transfer-v1-20261017/nr2-run02/complete-report-20261018.md`.

The first pre-fit registration stop is retained in `numeric-pilot-nr2/`; its measured activity is charged to the same 1800-second allowance. The repair resolves the NR1 per-attempt policy path, with source SHA verification; it changes no scientific or numerical acceptance settings.

An existing terminal record prevents retry. All source runs remain read-only. Snapshot refinements are diagnostic and cannot be adopted as formal endpoints.
