# Inner v2 numeric qualification

Use Pytorch312 and CUDA float64. Old source and reference runs are read-only.
Original classifier CE and W regularization remain unchanged; the finite
surrogate trajectory is new. References at q=1 are reused, never refitted.

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_inner_v2/runner.py register
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_inner_v2/runner.py prepare
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_inner_v2/runner.py quality
```

Only when selection.json has passed=true:

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_inner_v2/runner.py gradients
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_inner_v2/runner.py perturbation
```

Finish with report.py, including skipped conditional stages. No full target
matrix or scientific hyperparameter changes are authorized by numeric passing.
