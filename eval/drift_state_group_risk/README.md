# Drift-state risk DSR0–DSR4

Run from the repository root with `D:/Tools/Anaconda/envs/Pytorch312/python.exe`.
All classifier fitting and inference are deterministic CUDA float64, no CPU fallback.
The trusted setup uses frozen caches, never PCAP. Sources and packages seal before
any real state models/groups. Existing KSR artifacts remain read-only.

```powershell
python eval/drift_state_group_risk/setup.py
python eval/drift_state_group_risk/grouping.py sources
python eval/drift_state_group_risk/grouping.py inner-score
python eval/drift_state_group_risk/grouping.py inner-states
python eval/drift_state_group_risk/train.py inner
python eval/drift_state_group_risk/predict.py inner
python eval/drift_state_group_risk/predict.py select
python eval/drift_state_group_risk/grouping.py outer-score
python eval/drift_state_group_risk/grouping.py outer-states
python eval/drift_state_group_risk/train.py outer
python eval/drift_state_group_risk/predict.py outer
python eval/drift_state_group_risk/score.py evaluate
python eval/drift_state_group_risk/score.py bootstrap
python eval/drift_state_group_risk/score.py test-states
python eval/drift_state_group_risk/plots.py
python eval/drift_state_group_risk/verify.py
python eval/drift_state_group_risk/report.py
```

There are 240 logical CF12 queries, but 40 identical source-training memberships.
Cache keys use protocol and source-fold set only; queries never decide model fits.
Class predictions accept exactly 96 post histogram columns and opaque visit_id.
Group score functions reject individual pre or cross-side identity fields.
All-zero alpha candidates directly alias original baseline parameters.
Tests and group-state scores are offline, not attack inputs.
The three main F1 contrasts use a shared stratified 10,000-content bootstrap,
conditional on selected models, not an external validation or retraining interval.
Any failure of source/member/quality gates must stop, not silently expand budget.

The diagnostic-only engineering repair was approved on 2026-10-06. The original
source/contract snapshot and existing-artifact hashes are preserved under
`manifests/engineering-repair-v1/`. The original contract is never overwritten;
`experiment-contract-amended-v1.json` seals the explicitly zero L2 bias derivative
and traceability code, with unchanged mathematical objective and training matrix.
After `repair.py seal`, resume at `train.py inner`, not at setup. Final report,
contract summary and model card use the completion date 20261006.
