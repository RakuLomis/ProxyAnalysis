# Joint affine transfer

Approved plan: `plan/mechanism-observability-joint-affine-transfer-plan-20261007.md`.
This is a new finite experiment. Historical CT and protocol source evidence are read-only.

Preparation order in Pytorch312:

```powershell
python eval/joint_affine_transfer/prepare.py prepare
python eval/joint_affine_transfer/tests.py
python eval/joint_affine_transfer/observability.py
python eval/joint_affine_transfer/prepare.py diagnostics
python eval/joint_affine_transfer/report.py status
python eval/joint_affine_transfer/prepare.py seal
python eval/joint_affine_transfer/runner.py
```

Each entry accepts `--run ABSOLUTE_PATH` under the designated JA output root.
Run registration must not overwrite an existing seal. Preparation is trusted packing,
not model fitting. Package whitelists are audited application boundaries, not an OS sandbox.

JA0 is paired block affine, JA1 paired joint affine, JA2 anonymous same-content joint affine.
All share the 96-dimensional post coordinate, identity prior, unpenalized intercept,
eta grid 0.1/1/10/100 and fixed CT v4 classifier policy. Group loss retains all input
covariance and the output variance constant; neither anonymous file contains visit,
repetition, pair or carrier identity. Adapted vectors are not probability histograms.

CUDA float64 is mandatory for every fit, inference and numerical replay. No clipping,
CPU fit fallback, added jitter, enlarged budgets or warm-start continuation is allowed.
The four primary comparisons and family size are fixed before pilot training.

The 15-role pilot includes 720 classifiers and 180 mappings in the formal budget.
Two deterministic fits are separate diagnostics. The pilot contract is sealed first;
passing pilot and replay registers promotion without changing the contract. The full
budget is 34,740 new classifiers and 8,820 logical mappings. Progress, stdout, stderr,
failure and completion are local artifacts, not scientific success substitutes.

All post predictions are sealed before test labels or held-out pre become readable.
Source-inner recovery diagnostics run after this same seal and never enter selection.
Reference predictions are re-inferred on CUDA but never retrained or reselected.
The final runner writes metrics, content bootstrap, flips, recovery, plots, independent
verification and Markdown. A terminal numerical failure blocks any restart pending
an explicit revision. Half-mechanistic modeling is not part of this run.
