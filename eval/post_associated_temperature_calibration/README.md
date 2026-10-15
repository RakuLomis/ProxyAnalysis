# Frozen source temperature calibration pilot

The completed run is `outputs/post-associated-temperature-calibration-20261015/run-02`.
Run 01 stopped during a synthetic unit test before any real-data fit. Its stop,
registration and archived code remain available. The sole correction was testing
probability equality instead of equality of a non-identifiable temperature for a
flat synthetic objective. No objective, tolerance, data scope or budget changed.

Use the Pytorch312 environment. Fit and prediction require CUDA float64 and disable
TF32. Source model checkpoints are never loaded or updated. Temperatures act on
the full final logit vector, with T in [1, 5]. There are 648 independent fits:
12 roles x 9 frozen pipelines x 6 content folds. Seeds share a temperature within
each role/pipeline/fold. A batch is only an execution optimization; its objectives,
brackets and qualification decisions remain independent.

The staged entry points, in order, are:

```powershell
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_associated_temperature_calibration/run.py register
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_associated_temperature_calibration/run.py test
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_associated_temperature_calibration/run.py fit
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_associated_temperature_calibration/run.py predict
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_associated_temperature_calibration/run.py score
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_associated_temperature_calibration/audit.py
& D:/Tools/Anaconda/envs/Pytorch312/python.exe eval/post_associated_temperature_calibration/review.py
```

These commands deliberately refuse to overwrite existing records. They are not a
resume instruction for the completed run. A new replay must use a new output path,
then register its code hashes before running any fitting stages.

Registration separates five-content calibration packages, label-free evaluation
packages and scoring labels. No role reads another role's examples for fitting.
All temperatures are sealed before held-content probabilities, and probabilities
are sealed before scoring. All H/actual-target-U data remain out of scope.

Scoring uses stitched six-content predictions and full six-class confusion
matrices. It reports original and calibrated controls, all/C/U probability losses,
per-content/deployment/seed diagnostics and exact preservation of the old error
flip identities. The six source contents have already been analyzed previously;
this is retrospective calibration feasibility, not untouched external validation.
