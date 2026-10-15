# Drift kernel business classification

Fixed four-deployment, six-business, content-held-out evaluation. All fitting and inference require CUDA in Pytorch312. No PCAP scan, new SSL, protocol identity classifier or hyperparameter search.

Run from repository root with `D:/Tools/Anaconda/envs/Pytorch312/python.exe -u eval/drift_kernel_business/<script>.py` in this order:

1. `inventory.py`: validate original source hashes, configuration identity, entities and 200 kernels.
2. `prepare.py`: trusted packaging of training sides, opaque post queries and separate score labels.
3. `tests.py`: artificial CUDA tests; no real classification results.
4. `register.py`: seal methods, code, data packages, model references and statistical families.
5. `fit_distributions.py`: fit labeled pre S/direct post T and compose true/group kernels on CUDA.
6. `fit_baselines.py`: fixed CUDA LR and three-seed MLP per deployment/fold; resumes completed models by SHA.
7. `predict.py`: isolated frozen inference, only post histogram queries and model weights.
8. `evaluate.py`: join score labels after prediction sealing.
9. `uncertainty.py`: shared content-cluster bootstrap, two separate eight-comparison families.
10. `explain.py`: distribution mapping, error flips and exact score contributions; no refitting.
11. `plot.py`: eight PNG/PDF scientific plots.
12. `verify.py`: original source/package integrity and full post-only prediction replay.
13. `report.py`: detailed Chinese report, contract and model card.

Outputs: `outputs/drift-kernel-business-20261005/run-01`. Report: `docs/drift-kernel-business/formal-report.md`.

On this Windows environment, launching `fit_baselines.py` directly caused a native PyArrow access violation before any baseline model was fitted. Preloading the data dependencies avoids the DLL import-order issue without changing sealed model code or dependency versions. Use this equivalent launch command for step 6:

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' -u -c "import sys; sys.path.insert(0,'eval/drift_kernel_business'); import common; import fit_baselines; fit_baselines.run()"
```

The observed failure and workaround are recorded in `manifests/runtime-launch-note.json`. All scientific Python sources remain unchanged from the sealed contract.

Five deterministic arms G0/G1/G3/G4/G5 plus three G2 seeds yield 3840 probability rows for 480 unique visits. The MLP mean is a mean of metrics, not an ensemble or three independent test sets. Bootstrap confidence intervals condition on fixed trained models.

Model fitting roles cannot open query or score packages through the role-limited loader. Prediction cannot open fit or score packages; it accepts only 96 post histogram columns and opaque visit IDs. Known deployment routes every method equally. The role ledger is an engineering audit, not an OS sandbox.

Qualification and visit grouping remain inherited from dual-side offline evidence; this is not an unindexed online attack. Registered carrier/logical isolation is audited, but incomplete historical TCP epoch evidence remains a limit.

Do not change sealed sources or overwrite the existing run to search for a favorable result. Use `verify.py` for integrity checks. Any scientific redesign needs a separately approved plan and new run identity.
