# Mechanism conditioned paired SSL

Independent CUDA-only Extend E1 experiment. Frozen P3 remains read-only. See
`docs/mechanism-conditioned-ssl-extend/experiment-contract.md` for scope and permissions.

Use `Pytorch312`, then run:

```powershell
python eval/mechanism_conditioned_ssl/prepare.py --suite E1
python -m unittest discover -s eval/mechanism_conditioned_ssl -p "test_*.py"
python eval/mechanism_conditioned_ssl/engineering.py --suite E1
python eval/mechanism_conditioned_ssl/run.py --suite E1 --stage all
python eval/mechanism_conditioned_ssl/diagnose.py --suite E1
python eval/mechanism_conditioned_ssl/score.py --suite E1
python eval/mechanism_conditioned_ssl/verify.py --suite E1
python eval/mechanism_conditioned_ssl/report.py --suite E1
python eval/mechanism_conditioned_ssl/supplement.py --suite E1
```

`prepare` seals code, packages and source centers before training. No overwrite of
valid completed tasks. Engineering must pass before production. E2 is deliberately
not an accepted CLI option. Data/checkpoints remain local and ignored by Git.

The descriptive supplement uses the original saved draws and performs an
independent sklearn score check. It never changes the fit seal, predictions,
main contrast family, or checkpoints; its source is sealed separately. Run it
after report generation so its interpretation section is retained.
