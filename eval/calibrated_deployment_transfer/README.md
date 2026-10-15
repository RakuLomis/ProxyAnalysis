# Calibrated deployment business transfer

Implementation of `plan/calibrated-deployment-business-transfer-plan-20261006.md`.
Four exclusive TCP deployments, globally grouped content folds, six labels, ten
flow statistics, and 96-bin visit histograms. Target uncovered training pre AND
post are forbidden. Main inference accepts only post histograms plus opaque IDs.

Use `D:/Tools/Anaconda/envs/Pytorch312/python.exe`; Arrow initializes before torch.
CUDA float64 is required for kernels, representations, fits, prediction and replay.
There is no CPU training fallback and no new raw-capture extraction in this runner.

Initial preparation commands, run exactly once before registration:

```
python eval/calibrated_deployment_transfer/setup.py prepare
python eval/calibrated_deployment_transfer/tests.py
python eval/calibrated_deployment_transfer/setup.py register
python eval/calibrated_deployment_transfer/runner.py
```

The runner completes diagnostics first, seals their class predictions before
offline kernel scoring, then builds C-only kernels and main slots. All 14,400
main inner models are fitted before source pseudo-target selection; all 300 outer
models and all target class predictions are sealed before outer scoring/test-pre
diagnostics. StrongPost selects CT0 or CT2 solely in source pseudo-target tasks.
CT5 opens extra target resources only as a labeled reference, never for main fits.

Every model has its own optimizer log and SHA-256 sidecar. A failure stops rather
than increases budgets or switches device. The exclusive PID lock prevents two
runners. Completed stage markers and sealed model sidecars permit reviewed resume;
check failures and artifact integrity before restarting an interrupted run.

Expected formal new LR fits: 680 diagnostic + 14,400 main inner + 300 main outer
= 15,380. Synthetic unit test fits are separately labeled and not formal models.
Output: `outputs/calibrated-deployment-business-transfer-20261006/run-01/`.
Reports: `docs/calibrated-deployment-business-transfer/`.

The post-observation inventory is NOT physical-only extraction or an attack
window proof. Its independent window and complete physical cache contract remains
a separate gate. No claim of complete TCP epoch reconstruction, new protocols,
external blind validation, or statistical auxiliary noninferiority is made.
