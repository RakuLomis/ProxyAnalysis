# Activation-aware check repair and source LR references

The parent failed pilot stays read-only. This independent run keeps its loss,
64-step trajectory and scope unchanged. All model arithmetic requires CUDA
float64 in Pytorch312. The independent oracle does not call the production
recovery functions. The full target matrix and extra perturbation fits remain
unauthorized.

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_calibration_repair/runner.py register
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_calibration_repair/runner.py gradients
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_calibration_repair/runner.py references
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_calibration_repair/report.py
```

Each stage has a distinct completion and read ledger. Reference models only
start after the revised gradient gate passes; all 24 use the sealed v4 solver
policy and original-coordinate acceptance. No scientific promotion is automatic.
