# Hy2 carrier qualification audit

Run from the repository root with Pytorch312:

```powershell
python eval/hy2_carrier_calibration/prepare.py
python eval/hy2_carrier_calibration/refine.py
```

These are metadata/trace audits, not feature extraction or classifier runs. They read
the 0916 historical registry and bounded traces from all 538 attempts. No raw packet
contents, proxy credentials or trained classifiers are exported. Endpoint path keys
are hashed audit identifiers, never model features.

Outputs: `outputs/hy2-carrier-calibration-0916/run-02/`.
Report: `docs/hy2-carrier-calibration-0916/summary.md`.

`run-01` preserves the initial contract from an engineering content-key assertion
failure. Canonical video IDs, not their URLs, are used to inherit FSC folds in run-02.
No data split was regenerated and no model was trained in either version.

`qualification-gate.json` preserves preliminary conservative warnings. Read
`qualification-review.json` and `cross-attempt-references.parquet` for their refined
interpretation: lifecycle references are not equivalent to new logical bindings;
request-index incompleteness is not equivalent to missing flow-index members.

The training gate remains closed. The approved strict scope has not been established.
Do not continue by silently accepting a weaker lifecycle/window condition, replacing
a repetition, or dropping a business. No CUDA model work has been started; CPU is used
for the current metadata and trace checks only.

Tests: `tests/unit/test_hy2_carrier_calibration_audit.py` and
`tests/unit/test_carrier_paths.py`. Seven tests pass; JUnit output is at
`outputs/hy2-carrier-audit-tests.xml`. Use a fresh workspace `--basetemp` directory
and `-p no:cacheprovider` if system temp/cache permissions prevent pytest setup.
