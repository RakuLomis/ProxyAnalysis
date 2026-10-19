# OR1 output-orthogonal frozen readout

Source-only experiment registered by the local plan
`plan/output-orthogonal-readout-round1-plan-20261015.md`.
The implementation follows the user-pasted specification; no implementation ZIP
was available or executed. Original G/base/scalers and previous results are immutable.

CUDA float64 is required for projection, head fitting, inference and calibration.
Frozen G remains float32. Base logits use the actual double input view. The direct
head input follows the original float32-to-double path. Eta is fixed to 0.01,
tau to 1e-12, and bias is unpenalized. No encoder, base or drift-map fitting occurs.

132 physical heads (including the fixed five-head pilot) create 180 seed endpoints.
X and BIAS are exact aliases across three logical seeds. The existing 480 weighted
rows are never regenerated. Metadata-only row provenance keeps 144 anonymous pre
parents per role anonymous, rather than inferring forbidden visit correspondence.

Stages, with Pytorch312:

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/output_orthogonal_readout_round1/run.py register
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/output_orthogonal_readout_round1/run.py tests
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/output_orthogonal_readout_round1/run.py pilot
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/output_orthogonal_readout_round1/run.py train
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/output_orthogonal_readout_round1/run.py predict
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/output_orthogonal_readout_round1/run.py calibrate
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/output_orthogonal_readout_round1/run.py score
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/output_orthogonal_readout_round1/run.py audit
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/output_orthogonal_readout_round1/run.py finish
```

Stages refuse completed-stage replay or overwriting accepted artifacts. Numerical
or permission failures stop the run, not trigger automatic model fallback/retry.
The first five accepted pilot heads are reused within the 132-fit cap. Source
query data cannot be decoded before all heads seal. Scoring occurs only after
all raw predictions, all new temperatures and all calibrated predictions seal.

Calibration reuses the previous verified scalar backend: T in [1,5], six global
leave-one-content-out folds, independent data per role, one T shared across seeds,
full six-class CE and at most 64 objective evaluations. Five new OR pipelines need
360 new temperatures; five ordinary controls reuse 360 compatible old temperatures.
Orthogonality is audited before temperature scaling. Positive temperature preserves
each OR head's classes, not necessarily the old ordinary readout's classes.

Actual H/U are forbidden. These twelve source roles cover six previously analyzed
query contents and 96 distinct visits, not an external validation cohort. Report
all arms, source content/deployment/seed results and original repair retention.
