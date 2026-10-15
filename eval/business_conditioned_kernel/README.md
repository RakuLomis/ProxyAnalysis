# Business-conditioned kernel qualification — Q00–Q21

This stage is diagnostic, not a new business classifier or GE training run.
Run with `D:/Tools/Anaconda/envs/Pytorch312/python.exe` from the repository root:

```powershell
python eval/business_conditioned_kernel/run.py prepare
python eval/business_conditioned_kernel/run.py inner
python eval/business_conditioned_kernel/run.py inner-score
python eval/business_conditioned_kernel/run.py outer
python eval/business_conditioned_kernel/run.py qualify
python eval/business_conditioned_kernel/run.py activity
python eval/business_conditioned_kernel/run.py predict
python eval/business_conditioned_kernel/run.py score
python eval/business_conditioned_kernel/run.py bootstrap
python eval/business_conditioned_kernel/report.py plots
python eval/business_conditioned_kernel/run.py verify
python eval/business_conditioned_kernel/report.py report
```

All fitting, kernel queries, moment generation, covariance and frozen-model
gradients require deterministic CUDA float64. Arrow initializes before torch.
CPU is used for IO, audits, fixed-prediction statistics and scientific figures.
Source and data packages are SHA-sealed before fitting. The prepare command is
not rerunnable after registration; it never silently overwrites a contract.
No old files are modified and no PCAP is scanned. The new pipeline has no
classifier fitting function.

The data preparer is trusted and can see both sides to construct role packages;
subsequent stages use checked role-specific readers. Group inputs have only
anonymous content identity, mass and one-side features. Conditional prediction
uses test pre and true Y as an explicitly offline oracle, not an attack interface.
Outer actual post is read only after qualification and predictions are sealed.
Whitelists and actual-read ledgers are not an OS security sandbox.

Main kappa is 1; .25/4/16/infinity are descriptive only. Twelve fixed comparisons
use a shared, six-business-stratified 10,000-content bootstrap, conditional on
fixed kernels. All 60 moments per role remain in the qualification ledger,
including failures. Zero selected relations is an admissible stopping result.
The report must stop at Q21 and request separate approval before stage two.
