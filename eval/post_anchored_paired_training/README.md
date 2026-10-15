# Post anchored paired training

Fixed task-aware J0–J7 experiment. New joint supervision, not another E1 probe.
All fit/inference paths require CUDA in Pytorch312. The E1 source tree stays read-only.

Run from repository root, in this order:

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/test_core.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/prepare.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/engineering.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/train.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/predict.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/score.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/verify.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/report.py
```

`train.py --fold N` supports independent fold jobs. Completed sealed stages are preserved.
Source seals require the recorded plan, E1 cache, source code and manifests; partial
jobs are never silently overwritten. Model artifacts accept only six ordered post
numeric columns. Group packages contain no common side identity. Software capabilities
are not a claim of OS isolation. Fit-sealed files must not be edited to recover a failed gate.

Outputs remain in ignored `outputs/post-anchored-paired-training-extend/run-01`.
Experiment contract and final documentation are under `docs/post-anchored-paired-training-extend`.

## Approved numerical repair

Attempt1 stopped before scoring because its mathematically equivalent duplicated
J0 CE did not numerically reproduce frozen E1 B0L. The user authorized fifteen
J0 refits only. The original fit code and artifacts remain unchanged; use:

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/repair_train.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/repair_view.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/repair_score.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/repair_verify.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_anchored_paired_training/report.py
```

Final results and deployment artifacts are in `run-01/repair-v1`, not attempt1.
135 full-length fits were actually executed; the fixed comparisons use 120
models: 105 untouched models and fifteen repaired J0 models. Inactive first-stage
layout padding in repair_train is frozen and contributes no fitted models.
J0 duplicate CE is algebraically collapsed to one post forward per update; resource
tables disclose this rather than claiming identical forward counts across arms.
All fifteen repaired E/H hashes and their first1000 losses exactly reproduce B0L.
No tolerance, task definition, objective coefficient, checkpoint selection or
primary family was changed. `score.py` alone intentionally retains the failed
attempt1 gate; it is not an alternative final score entry point.
