# Full RA1 NR2 continuation

Authorized full run, with unchanged scientific task and precision gates. Reuses 1044 audited endpoints (624 scientific + 420 historical) and fits 1296 missing cases with the sealed NR2 1024-LBFGS / 32-Newton policy. Cumulative activity cap is inherited, not reset.

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/role_asymmetric_transfer_nr2_full/run.py
```

Source runs and old failure/completion records remain read-only. Numerical, permission, checksum or budget failure creates a terminal stop with no automatic retry or baseline fallback. All models precede H prediction; all predictions precede labels.

Outputs: `outputs/role-asymmetric-transfer-v1-20261017/full-nr2-01/`.
Reports: `docs/role-asymmetric-transfer-v1-20261017/full-nr2/`.
