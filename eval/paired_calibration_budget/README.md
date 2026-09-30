# Paired calibration budget (0916)

The frozen experiment is complete. Outputs: `outputs/paired-calibration-budget-0916/run-01/`.
Main report: `docs/paired-calibration-budget-0916/summary.md`.

Use the Pytorch312 Python executable from the repository root. CUDA is mandatory for fitting and inference. No PCAP extraction is required.

Execution order (do not rerun export over a frozen run after changing its code):

```text
python eval/paired_calibration_budget/run.py --stage export
python eval/paired_calibration_budget/lock_worker.py
python eval/paired_calibration_budget/run.py --stage generate
python eval/paired_calibration_budget/audit_generation.py
python -W ignore eval/paired_calibration_budget/train.py --stage engineering
python -W ignore eval/paired_calibration_budget/train.py --stage train
python eval/paired_calibration_budget/evaluate.py --stage infer
python eval/paired_calibration_budget/evaluate.py --stage label
python eval/paired_calibration_budget/summarize.py
python eval/paired_calibration_budget/finalize.py
```

The warning suppression avoids pandas unsorted-MultiIndex performance warnings in the frozen training implementation; it does not suppress exceptions or change sample/view order. Training resumes complete scenario folders only after checking their hashes. Evaluation never imports the trusted exporter. Labels are read in a separate scoring command after predictions are sealed.

`summarize.py` computes metrics separately for every rotation/seed, then averages metrics; it does not ensemble predictions. Its stratified content bootstrap shares draws across deployments, budgets and arms. `finalize.py` reads identity-only historical tables for connection/capture overlap and imports historical T6 only after new predictions/statistics are sealed.

Each stage records provenance and checks prior contracts. For a changed experiment, create a new run/config contract instead of overwriting this run's inputs. Training bundles are an application-level allowlist, not an OS sandbox.
