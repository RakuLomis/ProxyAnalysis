# DA-FGAN1 source-only pilot

Active implementation: `eval/decision_aware_forward_drift_r3`.
Active run: `outputs/decision-aware-forward-drift-20261017/pilot-03`.
Use `D:/Tools/Anaconda/envs/Pytorch312/python.exe`.

The user authorized 48 fixed ST1 source tasks, a three-hour cumulative limit,
a 2.4-hour conservative forecast gate, and source query-pre **only after all
models and classification post predictions are sealed**. Actual H/U remain
forbidden. The program does not launch a full outer experiment.

The first two runs stopped during trusted packaging, before any generator or
classifier training. Their source directories, contracts and stop records are
retained. Revision 2 corrected an inappropriate bit-equality test between
integer-derived histograms and a legacy floating-point table, retaining the
original `1e-14` replay policy and adding exact trusted identity checks. Revision
3 avoids a CUDA boolean-index assignment broadcast failure using explicit
one-hot group means. Model, objective, permissions, fixed hyperparameters,
classification gates, and exact ZERO materials are unchanged. Cumulative wall
time starts with pilot-01, including repair time; it is not reset on revision.

`model.py`, `engine.py`, the convex classifier and its certified LBFGS remain
unchanged across these three versions. The classifier/LBFGS are copied from
the accepted NER1 implementation without changing their numerical AST.

## Schedule

`driver.py` performs registration, 48 train-only packages, mathematical and
32-model/eight-stream CUDA Graph checks, two-role fixed engineering training,
eight engineering heads, a conservative forecast, the remaining 138 generator
paths and 184 heads, global model sealing, post-only inference, prediction
sealing, offline query-pre diagnostics, source-only scoring and reporting.

There are 144 generator paths and 192 new convex heads in total. B0 and ZERO
reuse the original frozen model. All models/linear algebra and inference use
CUDA float64. Metadata and reporting may use CPU. No GAN discriminator is
trained. The first round uses exactly one generator configuration; query
labels are not used to select hyperparameters or checkpoints.

Run once only:

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe -u eval/decision_aware_forward_drift_r3/driver.py
```

Existing output roots are never restarted implicitly. Numerical, permission,
identity, hash or budget failures stop with pending work rather than replacing
unrun candidates with B0. Inspect `progress.json`, `active-child.json`, logs,
the immutable stage manifests and `completion.json`/`stop-record.json`.

The detailed completed report is written to
`docs/decision-aware-forward-drift-20261017/pilot-results.md`.
