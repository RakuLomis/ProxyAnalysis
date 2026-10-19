# RA1 AD1 minimal 2×2

Authorized on 2026-10-18. Independent run, no overwrite of full NR2.

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/role_asymmetric_transfer_ad1/run.py
```

Two new policies `(rho_C,rho_U)=(0,.25),(.25,.5)`, 120 zero-start fits. Reuse 180 endpoints for `(0,.5),(.25,.25),(.1,.1)` after independent original-coordinate audits. Fixed eight engineering fits are part of the 120.

Wrappers compile sealed full-NR2 common/solver function bodies into a new IO namespace. Only the policy registry adds the two new rho pairs; the original slot function is unchanged. Bootstrap has the same source function, with policy-array size changed from 39 to 5. Hashes are sealed before fitting.

All models seal before H-post query; all predictions seal before labels. Four predeclared contrasts get a new four-comparison family; interaction and comparisons to P-small remain descriptive. No tuning, mappings, new seeds, GAN or temperature fitting.

Original 8-hour cumulative cap and numerical gates retained. Terminal failures do not auto-retry; terminal successful runs cannot be silently rerun.
