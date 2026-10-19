# SD1 frozen map subblock diagnostics

SD1 replays existing C-OOF affine maps; it does not fit models or evaluate business classifiers. Numerical map operations, projections and summary estimation require CUDA float64 in the Pytorch312 environment.

## Run

From the repository root:

```powershell
& 'D:/Tools/Anaconda/envs/Pytorch312/python.exe' -m eval.subblock_drift_diagnostics.run --stage all --resume
```

The current independent engineering version defaults to `run-03`. Existing completed stages are not overwritten. `--verify-only` checks the final lineage and output hashes without scoring again.

The previous `run-01` deterministic-CUDA-prefix stop and `run-02` nominal-label parsing stop remain immutable, with source snapshots. Neither reached query-post numerical scoring. The current version preserves nominal business labels and uses a fixed triangular CUDA matrix for the same prefix-sum definition. It charges the earlier activity segments to the cumulative 1800-second budget.

## Boundaries

- P and G receive the same pre-only query array; only the scorer holds exact target correspondence.
- Query-post is unavailable before all forecasts and all four counterfactual views have been sealed.
- Group summaries use independent anonymous pre/post marginals; no matched visit identity is supplied to G.
- Basis geometry uses raw frequencies. The original fold-specific scale is only reused for mapping and standardized-error reporting.
- All ten blocks, four deployments and five outer folds remain in the output. No H/U, native full cache or PCAP is decoded.
- New M/L/R statistics do not replace historical Guard quantiles or qualification rules. SD1 descriptive point quantiles use fixed linear interpolation.
- A discussion candidate never authorizes new training or deployment.

## Accounting

The final version has 240 distinct role-fold summary sets, 480 frozen map bindings, 7680 common-query map rows, 192000 predictor-block score rows and 307200 counterfactual-block score rows. Engineering replays in stopped versions are additional computation on the same sets, not new data, models or independent observations. The budget ledger preserves that overhead.

The independent verifier uses 12000 predictor-fold-block batches, each containing 16 query rows, covering all 192000 predictor-block rows. It additionally checks the counterfactual vectors and their raw/standardized errors. These batch counts must not be interpreted as distinct visits.

Outputs are under `outputs/subblock-drift-diagnostics-20261015/run-03`; the report is under `docs/subblock-drift-diagnostics-20261015/complete-report.md`.
