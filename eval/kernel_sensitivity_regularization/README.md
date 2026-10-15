# Kernel conditioned sensitivity regularization

Fixed 96-coordinate post LR, four observed TCP deployments, nested global content folds.
All matrix construction, model fitting and inference require CUDA float64 in Pytorch312.
CPU is used only for IO, audits, fixed-prediction statistics and plots.
No new PCAP reads, collection, model capacity, seeds or test-selected weights.

From the repository root, use `D:/Tools/Anaconda/envs/Pytorch312/python.exe`:

```powershell
python -u eval/kernel_sensitivity_regularization/setup.py inventory
python -u eval/kernel_sensitivity_regularization/setup.py prepare
python -u eval/kernel_sensitivity_regularization/setup.py tests
python -u eval/kernel_sensitivity_regularization/setup.py zero
python -u eval/kernel_sensitivity_regularization/setup.py register
python -u eval/kernel_sensitivity_regularization/train.py inner-matrix
python -u eval/kernel_sensitivity_regularization/train.py inner-fit
python -u eval/kernel_sensitivity_regularization/train.py inner-predict
python -u eval/kernel_sensitivity_regularization/train.py select
python -u eval/kernel_sensitivity_regularization/train.py outer-matrix
python -u eval/kernel_sensitivity_regularization/train.py outer-fit
python -u eval/kernel_sensitivity_regularization/train.py predict
python -u eval/kernel_sensitivity_regularization/results.py evaluate
python -u eval/kernel_sensitivity_regularization/results.py bootstrap
python -u eval/kernel_sensitivity_regularization/results.py explain
python -u eval/kernel_sensitivity_regularization/results.py plot
python -u eval/kernel_sensitivity_regularization/results.py verify
python -u eval/kernel_sensitivity_regularization/results.py report
```

Stages have separate processes and checked package read permissions. This is an
audited workflow, not an operating-system sandbox. Queries contain only opaque
visit IDs and fixed post histogram coordinates; model inference does not load
kernels, Gamma, pre or labels. Zero replay alone reads old frozen G1 probabilities
without labels. Inner fitting cannot reuse outer kernels. All inner candidates
are predicted before labels select pooled six-class F1, ties selecting smaller t.
Outer prediction evaluates only the sealed choice, plus the fixed zero reference.

`complete.json` enables model/matrix resume after hash validation. Registration
seals all scientific Python sources and role packages before positive fits.
Do not change them or repackage after registration. Original G/Q outputs remain
frozen. The final report and verification describe retrospective and offline
qualification boundaries and the 12-comparison conditional bootstrap family.
