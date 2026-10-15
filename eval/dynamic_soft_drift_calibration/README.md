# Dynamic soft drift calibration

This independent run implements only the registered source-only numeric pilot.
Training, finite-unroll gradients and frozen-model inference require CUDA float64.
Historical experiment directories are read-only. The formal target matrix remains
unauthorized until the pilot report and explicit continuation decision.

Run from the repository root with Pytorch312:

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_calibration/inventory.py
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_calibration/prepare.py
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_calibration/tests.py
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_calibration/pilot.py gradients
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' eval/dynamic_soft_drift_calibration/pilot.py reference
```

The 64-step objective is the actual differentiated surrogate, not a converged
classifier risk. Relationship fixtures in this pilot use only pseudo-target C;
they are in-sample arithmetic fixtures, not the formal target C OOF constraints.
No actual target numeric query, labels or pre data are permitted.
